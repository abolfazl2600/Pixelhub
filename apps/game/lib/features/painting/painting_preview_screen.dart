import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../core/local_diagnostics.dart';
import '../../core/pixel_art_preview.dart';
import '../../l10n/strings.dart';
import '../gallery/export_button.dart';
import 'painting_board.dart';
import 'painting_controller.dart';

class PaintingPreviewScreen extends StatefulWidget {
  const PaintingPreviewScreen({
    required this.controller,
    required this.diagnostics,
    this.onOpened,
    super.key,
  });
  static const route = '/painting';
  final PaintingController controller;
  final LocalDiagnostics diagnostics;
  final VoidCallback? onOpened;
  @override
  State<PaintingPreviewScreen> createState() => _PaintingPreviewScreenState();
}

class _PaintingPreviewScreenState extends State<PaintingPreviewScreen> {
  bool _moveMode = false;
  bool _viewResult = false;

  @override
  void initState() {
    super.initState();
    _recordOpen();
  }

  void _recordOpen() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) widget.onOpened?.call();
    });
  }

  void _bomb() {
    final count = widget.controller.useBomb();
    if (count == 0 || !mounted) return;
    widget.diagnostics.recordBomb();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(context.strings.bombFilled(context.digits(count))),
      ),
    );
  }

  @override
  void didUpdateWidget(PaintingPreviewScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.controller != widget.controller) {
      _recordOpen();
      _viewResult = false;
      _moveMode = false;
    }
  }

  void _hint() {
    if (widget.controller.showHint() != null) widget.diagnostics.recordHint();
  }

  Future<void> _reset() async {
    final s = context.strings;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(s.resetTitle),
        content: Text(s.resetMessage),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(s.cancel),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text(s.reset),
          ),
        ],
      ),
    );
    if (confirmed == true && mounted) {
      setState(() => _viewResult = false);
      widget.controller.reset();
    }
  }

  void _back() {
    if (context.canPop()) {
      context.pop();
    } else {
      context.go('/');
    }
  }

  Widget _saveState() {
    final s = context.strings;
    final controller = widget.controller;
    if (controller.saveStatus == SaveStatus.error) {
      return TextButton.icon(
        onPressed: controller.flush,
        icon: const Icon(Icons.sync_problem),
        label: Text(s.saveError),
      );
    }
    return Semantics(
      liveRegion: true,
      child: Text(
        controller.saveStatus == SaveStatus.saving ? s.saving : s.saved,
        key: const ValueKey('save-status'),
        style: const TextStyle(color: PixelTokens.muted, fontSize: 12),
      ),
    );
  }

  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: widget.controller,
    builder: (context, _) {
      final s = context.strings;
      final controller = widget.controller;
      final session = controller.session;
      final title = controller.level.titleFor(context.isPersian ? 'fa' : 'en');
      final appBar = AppBar(
        leading: IconButton(
          tooltip: s.backHome,
          icon: const Icon(Icons.arrow_back_rounded),
          onPressed: _back,
        ),
        title: Text(
          title,
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
        ),
      );
      if (controller.status == PaintingStatus.loading) {
        return Scaffold(
          appBar: appBar,
          body: Center(
            child: CircularProgressIndicator(semanticsLabel: s.loading),
          ),
        );
      }
      if (controller.status == PaintingStatus.error) {
        return Scaffold(
          appBar: appBar,
          body: SafeArea(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(s.progressLoadError),
                    const SizedBox(height: 16),
                    FilledButton(
                      onPressed: controller.load,
                      child: Text(s.retry),
                    ),
                    TextButton(onPressed: _reset, child: Text(s.reset)),
                  ],
                ),
              ),
            ),
          ),
        );
      }
      if (session!.isComplete && !_viewResult) {
        return CompletionScreen(
          controller: controller,
          appBar: appBar,
          saveState: _saveState(),
          onView: () => setState(() => _viewResult = true),
          onNext: () => context.go('/'),
        );
      }
      return Scaffold(
        appBar: appBar,
        body: SafeArea(
          top: false,
          child: SingleChildScrollView(
            key: const ValueKey('painting-scroll'),
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  '${s.progressSummary(context.digits(session.completedCount), context.digits(controller.level.cells.length))} · ${s.progressPercent(context.digits((session.fraction * 100).floor()))}',
                  key: const ValueKey('progress-summary'),
                  style: const TextStyle(fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 8),
                LinearProgressIndicator(
                  value: session.fraction,
                  minHeight: 6,
                  semanticsLabel: s.colors,
                ),
                const SizedBox(height: 8),
                _saveState(),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  alignment: WrapAlignment.center,
                  children: [
                    ChoiceChip(
                      label: Text(s.paintMode),
                      selected: !_moveMode,
                      onSelected: (_) {
                        controller.endStroke();
                        setState(() => _moveMode = false);
                      },
                    ),
                    ChoiceChip(
                      label: Text(s.panMode),
                      selected: _moveMode,
                      onSelected: (_) {
                        controller.endStroke();
                        setState(() => _moveMode = true);
                      },
                    ),
                    IconButton(
                      tooltip: s.reset,
                      onPressed: _reset,
                      icon: const Icon(Icons.restart_alt_rounded),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        key: const ValueKey('hint-tool'),
                        onPressed: session.isComplete ? null : _hint,
                        icon: const Icon(Icons.lightbulb_outline_rounded),
                        label: Text(s.hintTool),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: OutlinedButton.icon(
                        key: const ValueKey('bomb-tool'),
                        onPressed: session.remaining[session.selectedColor] == 0
                            ? null
                            : _bomb,
                        icon: const Icon(Icons.auto_awesome_rounded),
                        label: Text(s.bombTool),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  s.freeToolsNote,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 12,
                    color: PixelTokens.muted,
                  ),
                ),
                if (controller.hintIndex != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    s.hintLocation(
                      context.digits(
                        controller.hintIndex! ~/ controller.level.width + 1,
                      ),
                      context.digits(
                        controller.hintIndex! % controller.level.width + 1,
                      ),
                    ),
                    key: const ValueKey('hint-location'),
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                ],
                const SizedBox(height: 12),
                PaintingBoard(
                  key: ValueKey(controller.level.id),
                  controller: controller,
                  moveMode: _moveMode,
                ),
                const SizedBox(height: 8),
                Text(
                  s.colors,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    for (var i = 0; i < controller.level.palette.length; i++)
                      Semantics(
                        label: s.colorLabel(
                          context.digits(i + 1),
                          context.digits(session.remaining[i]),
                        ),
                        button: true,
                        onTap: () => controller.selectColor(i),
                        selected: session.selectedColor == i,
                        child: ExcludeSemantics(
                          child: Material(
                            color: Colors.transparent,
                            child: InkWell(
                              key: ValueKey('color-$i'),
                              borderRadius: BorderRadius.circular(16),
                              onTap: () => controller.selectColor(i),
                              child: Container(
                                width: 56,
                                constraints: const BoxConstraints(
                                  minHeight: 72,
                                ),
                                padding: const EdgeInsets.symmetric(
                                  vertical: 8,
                                ),
                                decoration: BoxDecoration(
                                  borderRadius: BorderRadius.circular(16),
                                  border: Border.all(
                                    color: session.selectedColor == i
                                        ? PixelTokens.green
                                        : PixelTokens.backdrop,
                                    width: session.selectedColor == i ? 2 : 1,
                                  ),
                                ),
                                child: Column(
                                  children: [
                                    CircleAvatar(
                                      radius: 16,
                                      backgroundColor: Color(
                                        controller.level.palette[i],
                                      ),
                                      child: Text(
                                        context.digits(i + 1),
                                        style: TextStyle(
                                          fontWeight: FontWeight.w700,
                                          color:
                                              ThemeData.estimateBrightnessForColor(
                                                    Color(
                                                      controller
                                                          .level
                                                          .palette[i],
                                                    ),
                                                  ) ==
                                                  Brightness.dark
                                              ? Colors.white
                                              : PixelTokens.ink,
                                        ),
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      context.digits(session.remaining[i]),
                                      style: const TextStyle(fontSize: 11),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 16),
                Text(
                  s.gestureHelp,
                  style: const TextStyle(
                    color: PixelTokens.muted,
                    fontSize: 12,
                    height: 1.8,
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    },
  );
}

class CompletionScreen extends StatelessWidget {
  const CompletionScreen({
    required this.controller,
    required this.appBar,
    required this.saveState,
    required this.onView,
    required this.onNext,
    super.key,
  });
  final PaintingController controller;
  final PreferredSizeWidget appBar;
  final Widget saveState;
  final VoidCallback onView;
  final VoidCallback onNext;
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: appBar,
    body: SafeArea(
      top: false,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Icon(
              Icons.celebration_rounded,
              size: 48,
              color: PixelTokens.green,
            ),
            const SizedBox(height: 16),
            Text(
              context.strings.completedTitle,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 12),
            Text(context.strings.completedMessage, textAlign: TextAlign.center),
            const SizedBox(height: 24),
            ClipRRect(
              borderRadius: BorderRadius.circular(24),
              child: PixelArtPreview(level: controller.level),
            ),
            const SizedBox(height: 16),
            saveState,
            const SizedBox(height: 16),
            ExportButton(level: controller.level),
            const SizedBox(height: 8),
            FilledButton(
              onPressed: onNext,
              child: Text(context.strings.nextPicture),
            ),
            TextButton(
              onPressed: onView,
              child: Text(context.strings.viewResult),
            ),
          ],
        ),
      ),
    ),
  );
}
