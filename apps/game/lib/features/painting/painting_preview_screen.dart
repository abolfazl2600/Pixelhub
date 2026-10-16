import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:painting_engine/painting_engine.dart';

import '../../core/local_diagnostics.dart';
import '../../l10n/strings.dart';
import '../gallery/artwork_economy.dart';
import '../gallery/library_controller.dart';
import '../gallery/export_button.dart';
import 'painting_board.dart';
import 'artwork_render_style.dart';
import 'painting_controller.dart';
import 'completed_artwork_preview.dart';
import 'package:level_schema/level_schema.dart';

/// Keep vertical painting strokes from scrolling the surrounding controls.
/// Read pointer state synchronously so pinch/drag recognizers are not rebuilt.
class _CanvasInteractionScrollPhysics extends ScrollPhysics {
  const _CanvasInteractionScrollPhysics({
    required this.isCanvasActive,
    super.parent,
  });

  final bool Function() isCanvasActive;

  @override
  _CanvasInteractionScrollPhysics applyTo(ScrollPhysics? ancestor) {
    return _CanvasInteractionScrollPhysics(
      isCanvasActive: isCanvasActive,
      parent: buildParent(ancestor),
    );
  }

  @override
  double applyPhysicsToUserOffset(ScrollMetrics position, double offset) {
    return isCanvasActive()
        ? 0
        : super.applyPhysicsToUserOffset(position, offset);
  }
}

class PaintingPreviewScreen extends StatefulWidget {
  const PaintingPreviewScreen({
    required this.controller,
    required this.library,
    required this.diagnostics,
    this.animation,
    this.onOpened,
    this.renderStyle = ArtworkRenderStyle.pixel,
    this.onRenderStyleChanged,
    super.key,
  });
  static const route = '/painting';
  final PaintingController controller;
  final LibraryController library;
  final LocalDiagnostics diagnostics;
  final PixelAnimation? animation;
  final VoidCallback? onOpened;
  final ArtworkRenderStyle renderStyle;
  final ValueChanged<ArtworkRenderStyle>? onRenderStyleChanged;
  @override
  State<PaintingPreviewScreen> createState() => _PaintingPreviewScreenState();
}

class _PaintingPreviewScreenState extends State<PaintingPreviewScreen> {
  bool _moveMode = false;
  bool _focusMode = false;
  bool _viewResult = false;
  bool _pointerOnCanvas = false;
  PrecisionPaintTool? _activeTool;
  bool _toolBusy = false;

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
    if (_toolBusy) return;
    if (_activeTool != null) setState(() => _activeTool = null);
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
      _focusMode = false;
      _pointerOnCanvas = false;
      _activeTool = null;
    }
  }

  void _canvasInteractionChanged(bool active) {
    _pointerOnCanvas = active;
  }

  void _setFocusMode(bool focused) {
    widget.controller.endStroke();
    setState(() {
      _focusMode = focused;
      _pointerOnCanvas = false;
      _activeTool = null;
      if (focused) _moveMode = false;
    });
  }

  void _togglePrecisionTool(PrecisionPaintTool tool) {
    if (_toolBusy || widget.library.busy) return;
    widget.controller.endStroke();
    setState(() {
      _activeTool = _activeTool == tool ? null : tool;
      if (_activeTool != null) _moveMode = false;
    });
  }

  /// Only spend coins for a valid, unfinished target. The serialized wallet
  /// write completes before the progress bitset changes.
  Future<void> _usePrecisionTool((int, int) cell) async {
    final tool = _activeTool;
    if (tool == null || _toolBusy || widget.library.busy) return;
    final controller = widget.controller;
    final targets = controller.previewTool(tool, cell.$1, cell.$2);
    if (targets.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(context.strings.precisionToolNoTargets)),
      );
      return;
    }
    final cost = precisionToolPrice(tool);
    if (widget.library.coins < cost) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(context.strings.precisionToolInsufficient)),
      );
      return;
    }
    setState(() => _toolBusy = true);
    try {
      await widget.library.spendToolCoins(cost);
      // Sessions are cached by the parent, so apply the paid action even if
      // navigation disposed this screen during the wallet write.
      final filled = controller.applyToolTargets(targets);
      if (!mounted) return;
      setState(() => _activeTool = null);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            context.strings.precisionToolFilled(
              context.digits(filled),
              context.digits(cost),
            ),
          ),
        ),
      );
    } on Object {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            widget.library.coins < cost
                ? context.strings.precisionToolInsufficient
                : context.strings.precisionToolSaveFailed,
          ),
        ),
      );
    } finally {
      if (mounted) setState(() => _toolBusy = false);
    }
  }

  void _hint() {
    if (_toolBusy) return;
    if (widget.controller.showHint() != null) widget.diagnostics.recordHint();
  }

  Future<void> _reset() async {
    if (_toolBusy) return;
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
      setState(() {
        _viewResult = false;
        _activeTool = null;
      });
      widget.controller.reset();
    }
  }

  void _back() {
    if (_toolBusy) return;
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

  /// Horizontally scrolling palette remains visible while the canvas/tools
  /// occupy the vertical scroll area. Color selection never moves the canvas.
  Widget _paletteStrip(BuildContext context, PaintingController controller) {
    final session = controller.session!;
    final s = context.strings;
    return Container(
      height: 108,
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        border: const Border(top: BorderSide(color: PixelTokens.backdrop)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsetsDirectional.only(start: 16, top: 6),
            child: Text(
              s.colors,
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700),
            ),
          ),
          Expanded(
            child: SingleChildScrollView(
              key: const ValueKey('color-palette-scroll'),
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              child: Row(
                children: [
                  for (var i = 0; i < controller.level.palette.length; i++)
                    Padding(
                      padding: const EdgeInsetsDirectional.only(end: 8),
                      child: Builder(
                        builder: (context) {
                          final color = Color(controller.level.palette[i]);
                          return Semantics(
                            label: s.colorLabel(
                              context.digits(i + 1),
                              context.digits(session.remaining[i]),
                            ),
                            button: true,
                            selected: session.selectedColor == i,
                            child: ExcludeSemantics(
                              child: Material(
                                color: Colors.transparent,
                                child: InkWell(
                                  key: ValueKey('color-$i'),
                                  borderRadius: BorderRadius.circular(16),
                                  onTap: _toolBusy
                                       ? null
                                       : () => controller.selectColor(i),
                                  child: Container(
                                    width: 56,
                                    decoration: BoxDecoration(
                                      borderRadius: BorderRadius.circular(16),
                                      border: Border.all(
                                        color: session.selectedColor == i
                                            ? PixelTokens.green
                                            : PixelTokens.backdrop,
                                        width: session.selectedColor == i
                                            ? 2
                                            : 1,
                                      ),
                                    ),
                                    child: Column(
                                      mainAxisAlignment:
                                          MainAxisAlignment.center,
                                      children: [
                                        CircleAvatar(
                                          radius: 14,
                                          backgroundColor: color,
                                          child: Text(
                                            context.digits(i + 1),
                                            style: TextStyle(
                                              fontWeight: FontWeight.w700,
                                              color:
                                                  ThemeData.estimateBrightnessForColor(
                                                        color,
                                                      ) ==
                                                      Brightness.dark
                                                  ? Colors.white
                                                  : PixelTokens.ink,
                                            ),
                                          ),
                                        ),
                                        const SizedBox(height: 2),
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
                          );
                        },
                      ),
                    ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: Listenable.merge([widget.controller, widget.library]),
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
        actions: [
          if (controller.status == PaintingStatus.ready)
            IconButton(
              key: const ValueKey('focus-mode-toggle'),
              tooltip: _focusMode ? s.exitFocusMode : s.focusMode,
              icon: Icon(
                _focusMode
                    ? Icons.fullscreen_exit_rounded
                    : Icons.fullscreen_rounded,
              ),
              onPressed: _toolBusy ? null : () => _setFocusMode(!_focusMode),
            ),
        ],
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
          animation: widget.animation,
          renderStyle: widget.renderStyle,
          appBar: appBar,
          saveState: _saveState(),
          rewardCoins: rewardForLevel(controller.level),
          rewardReceived: widget.library.library.rewarded.contains(
            controller.level.id,
          ),
          rewardSaveError: widget.library.storageError,
          onRetryReward: () async {
            try {
              await widget.library.rewardCompletion(controller.level);
            } on Object {
              // Display the persistent wallet error and allow another retry.
            }
          },
          onView: () => setState(() => _viewResult = true),
          onNext: () => context.go('/'),
        );
      }
      if (_focusMode) {
        return Scaffold(
          appBar: AppBar(
            toolbarHeight: 48,
            leading: IconButton(
              tooltip: s.backHome,
              icon: const Icon(Icons.arrow_back_rounded),
              onPressed: _back,
            ),
            title: Text(
              s.progressPercent(
                context.digits((session.fraction * 100).floor()),
              ),
              key: const ValueKey('focus-progress'),
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
            ),
            actions: [
              IconButton(
                key: const ValueKey('focus-mode-toggle'),
                tooltip: s.exitFocusMode,
                icon: const Icon(Icons.fullscreen_exit_rounded),
                onPressed: () => _setFocusMode(false),
              ),
            ],
          ),
          bottomNavigationBar: SafeArea(
            top: false,
            child: _paletteStrip(context, controller),
          ),
          body: SafeArea(
            top: false,
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: LinearProgressIndicator(
                    value: session.fraction,
                    minHeight: 6,
                    semanticsLabel: s.progressPercent(
                      context.digits((session.fraction * 100).floor()),
                    ),
                  ),
                ),
                Expanded(
                  child: LayoutBuilder(
                    builder: (context, constraints) {
                      final availableSize =
                          constraints.maxWidth < constraints.maxHeight
                          ? constraints.maxWidth
                          : constraints.maxHeight;
                      return Center(
                        child: PaintingBoard(
                          key: ValueKey(controller.level.id),
                          controller: controller,
                          moveMode: false,
                          showZoomControls: false,
                          maxBoardSize: availableSize > 16
                              ? availableSize - 16
                              : availableSize,
                          onInteractionChanged: _canvasInteractionChanged,
                          renderStyle: widget.renderStyle,
                          interactionLocked: _toolBusy,
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        );
      }
      return Scaffold(
        appBar: appBar,
        bottomNavigationBar: SafeArea(
          top: false,
          child: _paletteStrip(context, controller),
        ),
        body: SafeArea(
          top: false,
          child: SingleChildScrollView(
            key: const ValueKey('painting-scroll'),
            physics: _CanvasInteractionScrollPhysics(
              isCanvasActive: () => _pointerOnCanvas,
            ),
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
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Icon(Icons.monetization_on_outlined, size: 18),
                    const SizedBox(width: 6),
                    Text(
                      s.artworkCoins(
                        context.digits(rewardForLevel(controller.level)),
                      ),
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  '${s.walletCoins}: ${context.digits(widget.library.coins)}',
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
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
                        setState(() {
                          _moveMode = false;
                          _activeTool = null;
                        });
                      },
                    ),
                    ChoiceChip(
                      label: Text(s.panMode),
                      selected: _moveMode,
                      onSelected: (_) {
                        controller.endStroke();
                        setState(() {
                          _moveMode = true;
                          _activeTool = null;
                        });
                      },
                    ),
                    ChoiceChip(
                      key: const ValueKey('style-pixel'),
                      avatar: const Icon(Icons.grid_4x4_rounded, size: 18),
                      label: Text(s.pixelStyle),
                      selected: widget.renderStyle == ArtworkRenderStyle.pixel,
                      onSelected: (_) => widget.onRenderStyleChanged?.call(
                        ArtworkRenderStyle.pixel,
                      ),
                    ),
                    ChoiceChip(
                      key: const ValueKey('style-canvas'),
                      avatar: const Icon(Icons.texture_rounded, size: 18),
                      label: Text(s.canvasStyle),
                      selected: widget.renderStyle == ArtworkRenderStyle.canvas,
                      onSelected: (_) => widget.onRenderStyleChanged?.call(
                        ArtworkRenderStyle.canvas,
                      ),
                    ),
                    ChoiceChip(
                      key: const ValueKey('style-diamond'),
                      avatar: const Icon(Icons.diamond_outlined, size: 18),
                      label: Text(s.diamondStyle),
                      selected:
                          widget.renderStyle == ArtworkRenderStyle.diamond,
                      onSelected: (_) => widget.onRenderStyleChanged?.call(
                        ArtworkRenderStyle.diamond,
                      ),
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
                const SizedBox(height: 10),
                Text(
                  s.precisionToolTitle,
                  style: const TextStyle(fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton(
                        key: const ValueKey('magic-wand-tool'),
                        onPressed: _toolBusy
                            ? null
                            : () => _togglePrecisionTool(
                                PrecisionPaintTool.magicWand,
                              ),
                        style: OutlinedButton.styleFrom(
                          backgroundColor:
                              _activeTool == PrecisionPaintTool.magicWand
                              ? PixelTokens.lemon
                              : null,
                          padding: const EdgeInsets.symmetric(
                            horizontal: 4,
                            vertical: 8,
                          ),
                        ),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.auto_fix_high_rounded),
                            const SizedBox(height: 3),
                            Text(s.magicWandTool, textAlign: TextAlign.center),
                            Text(
                              s.precisionToolCost(
                                context.digits(
                                  precisionToolPrice(
                                    PrecisionPaintTool.magicWand,
                                  ),
                                ),
                              ),
                              style: const TextStyle(fontSize: 11),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: OutlinedButton(
                        key: const ValueKey('color-splash-tool'),
                        onPressed: _toolBusy
                            ? null
                            : () => _togglePrecisionTool(
                                PrecisionPaintTool.colorSplash,
                              ),
                        style: OutlinedButton.styleFrom(
                          backgroundColor:
                              _activeTool == PrecisionPaintTool.colorSplash
                              ? PixelTokens.lemon
                              : null,
                          padding: const EdgeInsets.symmetric(
                            horizontal: 4,
                            vertical: 8,
                          ),
                        ),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.blur_on_rounded),
                            const SizedBox(height: 3),
                            Text(s.colorSplashTool, textAlign: TextAlign.center),
                            Text(
                              s.precisionToolCost(
                                context.digits(
                                  precisionToolPrice(
                                    PrecisionPaintTool.colorSplash,
                                  ),
                                ),
                              ),
                              style: const TextStyle(fontSize: 11),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
                if (_activeTool != null) ...[
                  const SizedBox(height: 6),
                  Text(
                    s.precisionToolInstructions,
                    key: const ValueKey('precision-tool-instructions'),
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                ],
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
                  onInteractionChanged: _canvasInteractionChanged,
                  renderStyle: widget.renderStyle,
                  toolMode: _activeTool,
                  onToolTap: _usePrecisionTool,
                  interactionLocked: _toolBusy,
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
    this.animation,
    this.renderStyle = ArtworkRenderStyle.pixel,
    required this.appBar,
    required this.saveState,
    required this.rewardCoins,
    required this.rewardReceived,
    required this.rewardSaveError,
    required this.onRetryReward,
    required this.onView,
    required this.onNext,
    super.key,
  });
  final PaintingController controller;
  final PixelAnimation? animation;
  final ArtworkRenderStyle renderStyle;
  final PreferredSizeWidget appBar;
  final Widget saveState;
  final int rewardCoins;
  final bool rewardReceived;
  final bool rewardSaveError;
  final VoidCallback onRetryReward;
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
            const SizedBox(height: 16),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 18),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        Icons.monetization_on_rounded,
                        size: 28,
                        color: PixelTokens.green,
                      ),
                      const SizedBox(width: 8),
                      Flexible(
                        child: Text(
                          rewardReceived
                              ? context.strings.completionCoinsEarned(
                                  context.digits(rewardCoins),
                                )
                              : context.strings.artworkCoins(
                                  context.digits(rewardCoins),
                                ),
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            fontSize: 19,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    rewardReceived
                        ? context.strings.completionCoinsReceived
                        : rewardSaveError
                        ? context.strings.coinSaveFailed
                        : context.strings.completionCoinsPending,
                    textAlign: TextAlign.center,
                  ),
                  if (!rewardReceived && rewardSaveError)
                    TextButton(
                      onPressed: onRetryReward,
                      child: Text(context.strings.retry),
                    ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            ClipRRect(
              borderRadius: BorderRadius.circular(24),
              child: CompletedArtworkPreview(
                level: controller.level,
                animation: animation,
                renderStyle: renderStyle,
              ),
            ),
            const SizedBox(height: 16),
            saveState,
            const SizedBox(height: 16),
            ExportButton(level: controller.level, renderStyle: renderStyle),
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
