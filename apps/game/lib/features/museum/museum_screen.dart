import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:level_schema/level_schema.dart';

import '../../core/pixel_art_preview.dart';
import '../../l10n/strings.dart';
import '../gallery/library_controller.dart';
import '../painting/completed_artwork_preview.dart';
import 'museum_controller.dart';
import 'pixel_sleeping_cat.dart';
import 'museum_room_painter.dart';

/// Offline-first, two-dimensional pixel gallery. The screen never writes a
/// painting or unlock; it only saves which completed artworks hang on a wall.
class MuseumScreen extends StatefulWidget {
  const MuseumScreen({
    required this.museum,
    required this.library,
    this.animationFor,
    this.addArtworkId,
    super.key,
  });

  final MuseumController museum;
  final LibraryController library;
  final PixelAnimation? Function(LevelDefinition)? animationFor;
  final String? addArtworkId;

  @override
  State<MuseumScreen> createState() => _MuseumScreenState();
}

class _MuseumScreenState extends State<MuseumScreen> {
  String? _pendingArtId;

  @override
  void initState() {
    super.initState();
    _pendingArtId = widget.addArtworkId;
  }

  @override
  void didUpdateWidget(covariant MuseumScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.addArtworkId != widget.addArtworkId) {
      _pendingArtId = widget.addArtworkId;
    }
  }

  LevelDefinition? _completedArtwork(String? id) {
    if (id == null) return null;
    for (final level in widget.library.levels) {
      if (level.id == id && widget.library.isComplete(level)) return level;
    }
    return null;
  }

  void _error() {
    if (!mounted) return;
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(context.strings.museumSaveError)));
  }

  Future<bool> _save(Future<void> Function() operation) async {
    try {
      await operation();
      return true;
    } on Object {
      _error();
      return false;
    }
  }

  Future<void> _tapSlot(int index) async {
    if (!widget.museum.ready || widget.museum.busy) return;
    final pending = _pendingArtId;
    if (pending != null && _completedArtwork(pending) != null) {
      final success = await _save(() => widget.museum.place(index, pending));
      if (!mounted || !success) return;
      setState(() => _pendingArtId = null);
      // Clear the deep-link intent after a successful placement.
      context.replace('/museum');
      return;
    }
    await _chooseArtwork(index);
  }

  Future<void> _chooseArtwork(int index) async {
    final completed = widget.library.levels
        .where(widget.library.isComplete)
        .toList(growable: false);
    final selectedId = widget.museum.layout.slots[index];
    final s = context.strings;
    final selection = await showModalBottomSheet<String>(
      context: context,
      isScrollControlled: true,
      builder: (sheetContext) => SafeArea(
        child: SizedBox(
          height: MediaQuery.sizeOf(sheetContext).height * .68,
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(18, 14, 18, 10),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        s.museumSelectArtwork,
                        style: Theme.of(sheetContext).textTheme.titleLarge,
                      ),
                    ),
                    IconButton(
                      onPressed: () => Navigator.pop(sheetContext),
                      icon: const Icon(Icons.close_rounded),
                    ),
                  ],
                ),
              ),
              if (selectedId != null)
                ListTile(
                  key: const ValueKey('museum-remove-artwork'),
                  leading: const Icon(Icons.remove_circle_outline),
                  title: Text(s.museumRemoveArtwork),
                  onTap: () => Navigator.pop(sheetContext, '#remove'),
                ),
              Expanded(
                child: completed.isEmpty
                    ? Center(
                        child: Padding(
                          padding: const EdgeInsets.all(22),
                          child: Text(
                            s.museumNoCompletedArt,
                            textAlign: TextAlign.center,
                          ),
                        ),
                      )
                    : ListView.builder(
                        itemCount: completed.length,
                        itemBuilder: (context, item) {
                          final level = completed[item];
                          return ListTile(
                            key: ValueKey('museum-choice-${level.id}'),
                            leading: SizedBox(
                              width: 54,
                              height: 54,
                              child: PixelArtPreview(level: level),
                            ),
                            title: Text(
                              level.titleFor(
                                sheetContext.isPersian ? 'fa' : 'en',
                              ),
                            ),
                            trailing: selectedId == level.id
                                ? const Icon(Icons.check_rounded)
                                : const Icon(Icons.add_rounded),
                            onTap: () => Navigator.pop(sheetContext, level.id),
                          );
                        },
                      ),
              ),
            ],
          ),
        ),
      ),
    );
    if (!mounted || selection == null) return;
    if (selection == '#remove') {
      await _save(() => widget.museum.remove(index));
    } else {
      await _save(() => widget.museum.place(index, selection));
    }
  }

  void _showArtwork(LevelDefinition level) {
    showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: Text(level.titleFor(context.isPersian ? 'fa' : 'en')),
        content: SizedBox(
          width: 300,
          child: CompletedArtworkPreview(
            level: level,
            animation: widget.animationFor?.call(level),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: Text(context.strings.museumClose),
          ),
        ],
      ),
    );
  }

  Future<void> _chooseStyle({
    required String title,
    required List<(String, String)> options,
    required String selected,
    required Future<void> Function(String) onSelect,
  }) async {
    await showModalBottomSheet<void>(
      context: context,
      builder: (sheetContext) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 18),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(title, style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 10),
              for (final (id, label) in options)
                ListTile(
                  key: ValueKey('museum-option-$id'),
                  title: Text(label),
                  trailing: selected == id
                      ? const Icon(Icons.check_box_rounded)
                      : const Icon(Icons.check_box_outline_blank_rounded),
                  onTap: () {
                    Navigator.pop(sheetContext);
                    _save(() => onSelect(id));
                  },
                ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: Listenable.merge([widget.museum, widget.library]),
    builder: (context, _) {
      final s = context.strings;
      final museum = widget.museum;
      if (!museum.ready) {
        return Scaffold(
          appBar: AppBar(title: Text(s.museumTitle)),
          body: Center(
            child: museum.failedToLoad
                ? Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(s.museumLoadError),
                      FilledButton(
                        onPressed: museum.load,
                        child: Text(s.retry),
                      ),
                    ],
                  )
                : const CircularProgressIndicator(),
          ),
        );
      }
      final shown = museum.visibleSlots;
      final count = shown.whereType<String>().length;
      final layout = museum.layout;
      final pending = _completedArtwork(_pendingArtId);
      return Scaffold(
        appBar: AppBar(
          title: Text(s.museumTitle),
          leading: IconButton(
            tooltip: s.backHome,
            icon: const Icon(Icons.arrow_back_rounded),
            onPressed: () => context.go('/'),
          ),
        ),
        body: SafeArea(
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 680),
              child: ListView(
                padding: const EdgeInsets.fromLTRB(12, 10, 12, 24),
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: _pixelBox(const Color(0xfff6ddbb)),
                    child: Column(
                      children: [
                        Text(
                          s.museumFirstRoom,
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          s.museumProgress(context.digits(count)),
                          style: const TextStyle(fontWeight: FontWeight.w600),
                        ),
                        const SizedBox(height: 6),
                        LinearProgressIndicator(
                          value: count / 6,
                          minHeight: 8,
                          color: const Color(0xff438669),
                          backgroundColor: const Color(0xffd6ab83),
                        ),
                      ],
                    ),
                  ),
                  if (pending != null) ...[
                    const SizedBox(height: 10),
                    Container(
                      key: const ValueKey('museum-pending-artwork'),
                      padding: const EdgeInsets.all(12),
                      decoration: _pixelBox(const Color(0xffffedca)),
                      child: Text(
                        s.museumChooseSlot(
                          pending.titleFor(context.isPersian ? 'fa' : 'en'),
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ],
                  const SizedBox(height: 14),
                  LayoutBuilder(
                    builder: (context, constraints) {
                      final width = math.min(constraints.maxWidth, 640.0);
                      final unit = width / 64;
                      return SizedBox(
                        key: const ValueKey('museum-pixel-room'),
                        width: width,
                        height: 86 * unit,
                        child: Stack(
                          children: [
                            Positioned.fill(
                              child: CustomPaint(
                                painter: MuseumRoomPainter(layout.wall),
                              ),
                            ),
                            for (var i = 0; i < 6; i++)
                              Positioned(
                                left: (4 + (i % 3) * 20) * unit,
                                top:
                                    (i ~/ 3 == 0 ? 13 : 38) * unit +
                                    (layout.arrangement == 'staggered'
                                        ? (i % 3 == 1 ? 3 : 0) * unit
                                        : 0),
                                width: 16 * unit,
                                child: _MuseumSlot(
                                  index: i,
                                  unit: unit,
                                  frame: layout.frame,
                                  level: _completedArtwork(shown[i]),
                                  animation: shown[i] == null
                                      ? null
                                      : widget.animationFor?.call(
                                          _completedArtwork(shown[i])!,
                                        ),
                                  onTap: () => _tapSlot(i),
                                  onLongPress: () {
                                    final level = _completedArtwork(shown[i]);
                                    if (level != null) _showArtwork(level);
                                  },
                                ),
                              ),
                            // Independent overlay: the scene and six framed
                            // artworks never repaint when the sleeping cat
                            // flicks its tail every few seconds.
                            Positioned(
                              left: 20 * unit,
                              top: 58 * unit,
                              width: 26 * unit,
                              height: 14 * unit,
                              child: const IgnorePointer(
                                child: PixelSleepingCat(
                                  key: ValueKey('museum-sleeping-cat'),
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: _PixelMenuButton(
                          key: const ValueKey('museum-frames-button'),
                          icon: Icons.crop_square_rounded,
                          text: s.museumFrames,
                          onTap: museum.busy
                              ? null
                              : () => _chooseStyle(
                                  title: s.museumFrames,
                                  selected: layout.frame,
                                  options: [
                                    ('wood', s.museumFrameWood),
                                    ('gold', s.museumFrameGold),
                                    ('dark', s.museumFrameDark),
                                  ],
                                  onSelect: museum.setFrame,
                                ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _PixelMenuButton(
                          key: const ValueKey('museum-walls-button'),
                          icon: Icons.format_paint_outlined,
                          text: s.museumWalls,
                          onTap: museum.busy
                              ? null
                              : () => _chooseStyle(
                                  title: s.museumWalls,
                                  selected: layout.wall,
                                  options: [
                                    ('cream', s.museumWallCream),
                                    ('blue', s.museumWallBlue),
                                    ('sage', s.museumWallSage),
                                  ],
                                  onSelect: museum.setWall,
                                ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _PixelMenuButton(
                          key: const ValueKey('museum-arrange-button'),
                          icon: Icons.dashboard_customize_rounded,
                          text: s.museumArrange,
                          onTap: museum.busy
                              ? null
                              : () => _chooseStyle(
                                  title: s.museumArrange,
                                  selected: layout.arrangement,
                                  options: [
                                    ('grid', s.museumArrangeGrid),
                                    ('staggered', s.museumArrangeStaggered),
                                  ],
                                  onSelect: museum.setArrangement,
                                ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    s.museumHelp,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
                  ),
                  if (count == 0 && pending == null) ...[
                    const SizedBox(height: 12),
                    OutlinedButton.icon(
                      onPressed: () => context.push('/gallery'),
                      icon: const Icon(Icons.palette_outlined),
                      label: Text(s.museumFindPaintings),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
      );
    },
  );
}

BoxDecoration _pixelBox(Color color) => BoxDecoration(
  color: color,
  border: Border.all(color: const Color(0xff77523d), width: 3),
  boxShadow: const [
    BoxShadow(color: Color(0xffad886b), offset: Offset(3, 3), blurRadius: 0),
  ],
);

class _PixelMenuButton extends StatelessWidget {
  const _PixelMenuButton({
    required this.icon,
    required this.text,
    required this.onTap,
    super.key,
  });

  final IconData icon;
  final String text;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) => Semantics(
    button: true,
    child: InkWell(
      onTap: onTap,
      child: Container(
        constraints: const BoxConstraints(minHeight: 76),
        decoration: _pixelBox(const Color(0xffffedcb)),
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 3),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: const Color(0xff65422f), size: 29),
            const SizedBox(height: 4),
            Text(
              text,
              textAlign: TextAlign.center,
              maxLines: 1,
              style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 12),
            ),
          ],
        ),
      ),
    ),
  );
}

class _MuseumSlot extends StatelessWidget {
  const _MuseumSlot({
    required this.index,
    required this.unit,
    required this.frame,
    required this.level,
    required this.animation,
    required this.onTap,
    required this.onLongPress,
  });

  final int index;
  final double unit;
  final String frame;
  final LevelDefinition? level;
  final PixelAnimation? animation;
  final VoidCallback onTap;
  final VoidCallback onLongPress;

  @override
  Widget build(BuildContext context) {
    final colors = switch (frame) {
      'gold' => (
        const Color(0xffc58a35),
        const Color(0xffffdc79),
        const Color(0xff744929),
      ),
      'dark' => (
        const Color(0xff343d46),
        const Color(0xff69737a),
        const Color(0xff202630),
      ),
      _ => (
        const Color(0xff8a5532),
        const Color(0xffc99258),
        const Color(0xff4d352b),
      ),
    };
    return Semantics(
      label: level == null
          ? context.strings.museumEmptySlot
          : level!.titleFor(context.isPersian ? 'fa' : 'en'),
      button: true,
      child: GestureDetector(
        key: ValueKey('museum-slot-$index'),
        onTap: onTap,
        onLongPress: level == null ? null : onLongPress,
        child: Column(
          children: [
            Container(
              width: 16 * unit,
              height: 17.7 * unit,
              padding: EdgeInsets.all(unit * .5),
              decoration: BoxDecoration(
                color: colors.$1,
                border: Border.all(color: colors.$2, width: unit * .3),
                boxShadow: [
                  BoxShadow(
                    color: colors.$3,
                    blurRadius: 0,
                    offset: Offset(unit * .7, unit * .9),
                  ),
                ],
              ),
              // Thin stepped highlight and dark inner lip match the denser
              // 128 × 172 pixel room, without filtering the painting itself.
              child: DecoratedBox(
                decoration: BoxDecoration(
                  color: colors.$2,
                  border: Border.all(color: colors.$3, width: unit * .25),
                ),
                child: Padding(
                  padding: EdgeInsets.all(unit * .3),
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      color: const Color(0xffbfa687),
                      border: Border.all(
                        color: colors.$1,
                        width: unit * .22,
                      ),
                    ),
                    child: level == null
                        ? Center(
                            child: Icon(
                              Icons.add_rounded,
                              size: 6 * unit,
                              color: const Color(0xff745b48),
                            ),
                          )
                        : PixelArtPreview(level: level!),
                  ),
                ),
              ),
            ),
            SizedBox(height: unit * .65),
            Container(
              color: const Color(0xffe8bc7a),
              constraints: BoxConstraints(minHeight: 2 * unit),
              padding: EdgeInsets.symmetric(horizontal: unit * .4),
              child: Text(
                level?.titleFor(context.isPersian ? 'fa' : 'en') ??
                    context.strings.museumEmptyFrame,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: const Color(0xff4e3323),
                  fontWeight: FontWeight.bold,
                  fontSize: math.max(7.0, unit * 1.25),
                  height: 1.2,
                ),
              ),
            ),
            if (animation != null && level != null)
              Icon(
                Icons.play_circle_fill_rounded,
                size: unit * 2.8,
                color: const Color(0xff62447e),
              ),
          ],
        ),
      ),
    );
  }
}
