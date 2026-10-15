import 'dart:async';

import 'package:flutter/material.dart';
import 'package:level_schema/level_schema.dart';

import '../../core/pixel_art_preview.dart';
import '../../l10n/strings.dart';
import 'artwork_render_style.dart';
import 'diamond_gem_painter.dart';

/// Shown only after a level is completed. Animation playback does not alter
/// painting state and is disabled for pictures without a sidecar.
class CompletedArtworkPreview extends StatefulWidget {
  const CompletedArtworkPreview({
    required this.level,
    this.animation,
    this.renderStyle = ArtworkRenderStyle.pixel,
    super.key,
  });

  final LevelDefinition level;
  final PixelAnimation? animation;
  final ArtworkRenderStyle renderStyle;

  @override
  State<CompletedArtworkPreview> createState() =>
      _CompletedArtworkPreviewState();
}

class _CompletedArtworkPreviewState extends State<CompletedArtworkPreview> {
  Timer? _timer;
  bool _animated = true;
  int _frame = 0;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _syncTimer();
  }

  @override
  void didUpdateWidget(covariant CompletedArtworkPreview oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.animation != widget.animation ||
        oldWidget.level != widget.level) {
      _frame = 0;
      _animated = true;
      _syncTimer();
    }
  }

  void _syncTimer() {
    _timer?.cancel();
    _timer = null;
    final animation = widget.animation;
    if (!_animated ||
        animation == null ||
        animation.frameCount < 2 ||
        MediaQuery.disableAnimationsOf(context) ||
        !TickerMode.of(context)) {
      return;
    }
    _timer = Timer.periodic(Duration(milliseconds: animation.frameDurationMs), (
      _,
    ) {
      if (mounted) {
        setState(() => _frame = (_frame + 1) % animation.frameCount);
      }
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _switchMode(bool animate) {
    setState(() {
      _animated = animate;
      _frame = 0;
    });
    _syncTimer();
  }

  @override
  Widget build(BuildContext context) {
    final animation = widget.animation;
    final dynamicFrame = animation != null && _animated;
    final persian = context.isPersian;
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (dynamicFrame)
          AspectRatio(
            aspectRatio: widget.level.width / widget.level.height,
            child: CustomPaint(
              key: const ValueKey('animation-frame'),
              painter: _AnimationPainter(
                widget.level,
                animation,
                _frame,
                widget.renderStyle,
              ),
            ),
          )
        else
          PixelArtPreview(level: widget.level, renderStyle: widget.renderStyle),
        if (animation != null) ...[
          const SizedBox(height: 12),
          Wrap(
            alignment: WrapAlignment.center,
            spacing: 8,
            runSpacing: 6,
            children: [
              ChoiceChip(
                key: const ValueKey('still-artwork'),
                label: Text(persian ? 'تصویر ثابت' : 'Still image'),
                selected: !_animated,
                onSelected: (_) => _switchMode(false),
              ),
              ChoiceChip(
                key: const ValueKey('animated-artwork'),
                label: Text(
                  persian
                      ? 'تصویر متحرک (${context.digits(animation.frameCount)} فریم)'
                      : 'Animated (${context.digits(animation.frameCount)} frames)',
                ),
                avatar: const Icon(Icons.play_circle_outline, size: 20),
                selected: _animated,
                onSelected: (_) => _switchMode(true),
              ),
            ],
          ),
        ],
      ],
    );
  }
}

class _AnimationPainter extends CustomPainter {
  _AnimationPainter(this.level, this.animation, this.frame, this.renderStyle);

  final LevelDefinition level;
  final PixelAnimation animation;
  final int frame;
  final ArtworkRenderStyle renderStyle;

  @override
  void paint(Canvas canvas, Size size) {
    final cells = animation.pixelsFor(level, frame);
    final paint = Paint()..isAntiAlias = false;
    final w = size.width / level.width;
    final h = size.height / level.height;
    if (renderStyle == ArtworkRenderStyle.diamond) {
      canvas.drawRect(Offset.zero & size, Paint()..color = const Color(0xffe9edf4));
      for (var y = 0; y < level.height; y++) {
        for (var x = 0; x < level.width; x++) {
          final color = Color(level.palette[cells[y * level.width + x]]);
          paintDiamondGem(
            canvas,
            Rect.fromLTWH(x * w, y * h, w, h),
            color,
            column: x,
            row: y,
          );
        }
      }
      return;
    }
    // Coalesce adjacent same-color pixels to reduce drawing operations.
    for (var y = 0; y < level.height; y++) {
      var x = 0;
      while (x < level.width) {
        final color = cells[y * level.width + x];
        final left = x;
        while (x < level.width && cells[y * level.width + x] == color) {
          x++;
        }
        paint.color = Color(level.palette[color]);
        canvas.drawRect(
          Rect.fromLTRB(left * w, y * h, x * w, (y + 1) * h),
          paint,
        );
        if (renderStyle == ArtworkRenderStyle.canvas && w >= 9 && h >= 9) {
          for (var column = left; column < x; column++) {
            paintCanvasPigment(
              canvas,
              Rect.fromLTWH(column * w, y * h, w, h),
              column: column,
              row: y,
            );
          }
        }
      }
    }
    artworkStylePainters[renderStyle]?.call(
      canvas,
      Offset.zero & size,
      cellWidth: w,
      cellHeight: h,
    );
  }

  @override
  bool shouldRepaint(covariant _AnimationPainter old) =>
      old.frame != frame ||
      old.level != level ||
      old.animation != animation ||
      old.renderStyle != renderStyle;
}
