import 'dart:math' as math;

import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../l10n/strings.dart';
import 'artwork_render_style.dart';
import 'diamond_gem_painter.dart';
import 'painting_controller.dart';

class PaintingBoard extends StatefulWidget {
  const PaintingBoard({
    required this.controller,
    required this.moveMode,
    this.onInteractionChanged,
    this.showZoomControls = true,
    this.maxBoardSize,
    this.renderStyle = ArtworkRenderStyle.pixel,
    super.key,
  });
  final PaintingController controller;
  final bool moveMode;

  /// The parent scroll view must not scroll during a canvas interaction.
  final ValueChanged<bool>? onInteractionChanged;

  /// Hide the secondary zoom buttons when the surrounding screen is focused.
  /// Pinch zoom and touch painting remain enabled.
  final bool showZoomControls;

  /// Optional limit for tight focus-mode viewports and landscape screens.
  final double? maxBoardSize;
  final ArtworkRenderStyle renderStyle;
  @override
  State<PaintingBoard> createState() => _PaintingBoardState();
}

class _PaintingBoardState extends State<PaintingBoard> {
  final _transform = TransformationController();
  final _focus = FocusNode();
  final Set<int> _pointers = {};
  Offset? _start;
  (int, int)? _last;
  bool _multiTouch = false;
  bool _moved = false;
  double _size = 0;
  int _cursorX = 0;
  int _cursorY = 0;
  DateTime _lastWarning = DateTime.fromMillisecondsSinceEpoch(0);

  (int, int)? _cell(Offset local) {
    final point = _transform.toScene(local);
    final level = widget.controller.level;
    final x = (point.dx / _size * level.width).floor();
    final y = (point.dy / _size * level.height).floor();
    return x >= 0 && x < level.width && y >= 0 && y < level.height
        ? (x, y)
        : null;
  }

  void _draw((int, int) cell) {
    final previous = _last ?? cell;
    widget.controller.paintLine(previous.$1, previous.$2, cell.$1, cell.$2);
    _last = cell;
  }

  void _down(PointerDownEvent event) {
    _pointers.add(event.pointer);
    if (_pointers.length == 1) widget.onInteractionChanged?.call(true);
    if (_pointers.length > 1) {
      _multiTouch = true;
      widget.controller.cancelStroke();
      _last = null;
      return;
    }
    if (widget.moveMode) return;
    _focus.requestFocus();
    _start = event.localPosition;
    _last = _cell(event.localPosition);
    _moved = false;
    _multiTouch = false;
    widget.controller.beginStroke();
    // Delay initial paint until move/up, so a second finger cannot paint a tap.
  }

  void _move(PointerMoveEvent event) {
    if (widget.moveMode || _multiTouch || _pointers.length != 1) return;
    if (_start == null) return;
    if (!_moved && (_start! - event.localPosition).distance < 4) return;
    _moved = true;
    final cell = _cell(event.localPosition);
    if (cell == null) {
      _last = null;
      return;
    }
    _draw(cell);
  }

  void _up(PointerUpEvent event) {
    if (!widget.moveMode && !_multiTouch && !_moved) {
      final cell = _cell(event.localPosition);
      if (cell != null) {
        _last = cell;
        final session = widget.controller.session!;
        final index = cell.$2 * session.level.width + cell.$1;
        if (!session.isCompleted(index) &&
            session.level.cells[index] != session.selectedColor &&
            DateTime.now().difference(_lastWarning).inMilliseconds > 1000) {
          _lastWarning = DateTime.now();
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(context.strings.wrongColor),
              duration: const Duration(seconds: 1),
            ),
          );
        }
        _draw(cell);
      }
    }
    _pointers.remove(event.pointer);
    if (_pointers.isEmpty) {
      widget.onInteractionChanged?.call(false);
      widget.controller.endStroke();
      _last = null;
      _start = null;
      _multiTouch = false;
    }
  }

  void _cancel(PointerCancelEvent event) {
    _pointers.remove(event.pointer);
    if (_pointers.isEmpty) widget.onInteractionChanged?.call(false);
    widget.controller.cancelStroke();
    _last = null;
    _start = null;
    _multiTouch = _pointers.isNotEmpty;
  }

  void _zoom(double factor) {
    final scale = (_transform.value.getMaxScaleOnAxis() * factor).clamp(
      1.0,
      32.0,
    );
    final center = Offset(_size / 2, _size / 2);
    final scene = _transform.toScene(center);
    final x = (center.dx - scene.dx * scale).clamp(_size * (1 - scale), 0.0);
    final y = (center.dy - scene.dy * scale).clamp(_size * (1 - scale), 0.0);
    _transform.value = Matrix4.diagonal3Values(scale, scale, 1)
      ..setTranslationRaw(x, y, 0);
  }

  KeyEventResult _key(FocusNode node, KeyEvent event) {
    if (event is! KeyDownEvent && event is! KeyRepeatEvent) {
      return KeyEventResult.ignored;
    }
    final level = widget.controller.level;
    final key = event.logicalKey;
    if (key == LogicalKeyboardKey.arrowLeft) {
      _cursorX = math.max(0, _cursorX - 1);
    } else if (key == LogicalKeyboardKey.arrowRight) {
      _cursorX = math.min(level.width - 1, _cursorX + 1);
    } else if (key == LogicalKeyboardKey.arrowUp) {
      _cursorY = math.max(0, _cursorY - 1);
    } else if (key == LogicalKeyboardKey.arrowDown) {
      _cursorY = math.min(level.height - 1, _cursorY + 1);
    } else if (key == LogicalKeyboardKey.enter ||
        key == LogicalKeyboardKey.space) {
      widget.controller.beginStroke();
      widget.controller.paintLine(_cursorX, _cursorY, _cursorX, _cursorY);
      widget.controller.endStroke();
    } else {
      return KeyEventResult.ignored;
    }
    setState(() {});
    return KeyEventResult.handled;
  }

  @override
  Widget build(BuildContext context) => Column(
    mainAxisSize: MainAxisSize.min,
    children: [
      LayoutBuilder(
        builder: (context, constraints) {
          // Avoid an enormous square board on wide/landscape tablets.
          // The surrounding screen still uses the entire viewport.
          _size = math.min(
            constraints.maxWidth,
            math.min(
              widget.maxBoardSize ?? double.infinity,
              math.max(280.0, MediaQuery.sizeOf(context).height * 0.76),
            ),
          );
          return Semantics(
            label: context.strings.canvasLabel,
            identifier: 'painting-board',
            image: true,
            container: true,
            child: Focus(
              focusNode: _focus,
              onKeyEvent: _key,
              child: SizedBox.square(
                key: const ValueKey('painting-board'),
                dimension: _size,
                child: Directionality(
                  textDirection: TextDirection.ltr,
                  child: Listener(
                    onPointerDown: _down,
                    onPointerMove: _move,
                    onPointerUp: _up,
                    onPointerCancel: _cancel,
                    child: InteractiveViewer(
                      transformationController: _transform,
                      panEnabled: widget.moveMode,
                      scaleEnabled: true,
                      minScale: 1,
                      maxScale: 32,
                      clipBehavior: Clip.hardEdge,
                      child: CustomPaint(
                        size: Size.square(_size),
                        painter: _GridPainter(
                          widget.controller,
                          _transform,
                          context.isPersian,
                          _focus.hasFocus ? (_cursorX, _cursorY) : null,
                          widget.renderStyle,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          );
        },
      ),
      if (widget.showZoomControls)
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            IconButton(
              tooltip: context.strings.zoomOut,
              onPressed: () => _zoom(1 / 1.5),
              icon: const Icon(Icons.remove_rounded),
            ),
            IconButton(
              tooltip: context.strings.fitCanvas,
              onPressed: () => _transform.value = Matrix4.identity(),
              icon: const Icon(Icons.fit_screen_rounded),
            ),
            IconButton(
              tooltip: context.strings.zoomIn,
              onPressed: () => _zoom(1.5),
              icon: const Icon(Icons.add_rounded),
            ),
          ],
        ),
    ],
  );

  @override
  void dispose() {
    if (_pointers.isNotEmpty) widget.onInteractionChanged?.call(false);
    widget.controller.session?.endStroke();
    _transform.dispose();
    _focus.dispose();
    super.dispose();
  }
}

class _GridPainter extends CustomPainter {
  _GridPainter(
    this.controller,
    this.transform,
    this.persian,
    this.cursor,
    this.renderStyle,
  ) : super(repaint: Listenable.merge([controller, transform]));
  final PaintingController controller;
  final TransformationController transform;
  final bool persian;
  final (int, int)? cursor;
  final ArtworkRenderStyle renderStyle;

  @override
  void paint(Canvas canvas, Size size) {
    final session = controller.session!;
    final level = session.level;
    final cw = size.width / level.width;
    final ch = size.height / level.height;
    final scale = transform.value.getMaxScaleOnAxis();
    final a = transform.toScene(Offset.zero);
    final b = transform.toScene(Offset(size.width, size.height));
    final left = (a.dx / cw).floor().clamp(0, level.width - 1);
    final top = (a.dy / ch).floor().clamp(0, level.height - 1);
    final right = (b.dx / cw).ceil().clamp(0, level.width);
    final bottom = (b.dy / ch).ceil().clamp(0, level.height);
    final paint = Paint()..isAntiAlias = false;
    final labels = <int, TextPainter>{};
    final wovenCells = Path();
    canvas.drawRect(
      Offset.zero & size,
      paint
        ..color = switch (renderStyle) {
          ArtworkRenderStyle.canvas => const Color(0xfff6f5f1),
          ArtworkRenderStyle.diamond => const Color(0xffe9edf4),
          ArtworkRenderStyle.pixel => Colors.white,
        },
    );
    for (var y = top; y < bottom; y++) {
      for (var x = left; x < right; x++) {
        final index = y * level.width + x;
        final color = level.cells[index];
        final done = session.isCompleted(index);
        final rect = Rect.fromLTWH(x * cw, y * ch, cw, ch);
        if (done && renderStyle == ArtworkRenderStyle.canvas) {
          wovenCells.addRect(rect);
        }
        if (renderStyle == ArtworkRenderStyle.diamond) {
          if (done) {
            paintDiamondGem(
              canvas,
              rect,
              Color(level.palette[color]),
              column: x,
              row: y,
              zoomScale: scale,
            );
          } else {
            if (color == session.selectedColor) {
              canvas.drawRect(rect, Paint()..color = const Color(0xffdcebdd));
            }
            paintDiamondSocket(canvas, rect);
          }
        } else if (done || color == session.selectedColor) {
          paint.color = done
              ? Color(level.palette[color])
              : const Color(0xffdcebdd);
          canvas.drawRect(rect, paint);
        }
        if (!done && cw * scale >= 14) {
          final label = labels.putIfAbsent(color, () {
            final text = '${color + 1}';
            return TextPainter(
              text: TextSpan(
                text: persian
                    ? text.replaceAllMapped(
                        RegExp('[0-9]'),
                        (m) => '۰۱۲۳۴۵۶۷۸۹'[int.parse(m[0]!)],
                      )
                    : text,
                style: TextStyle(
                  color: PixelTokens.ink,
                  fontFamily: 'Vazirmatn',
                  fontSize: math.min(cw, ch) * 0.5,
                ),
              ),
              textDirection: TextDirection.ltr,
            )..layout();
          });
          label.paint(
            canvas,
            rect.center - Offset(label.width / 2, label.height / 2),
          );
        }
      }
    }
    if (renderStyle == ArtworkRenderStyle.canvas) {
      // Unpainted numbered cells remain readable and untextured.
      canvas.save();
      canvas.clipPath(wovenCells);
      paintCanvasTexture(
        canvas,
        Rect.fromLTRB(left * cw, top * ch, right * cw, bottom * ch),
        cellWidth: cw,
        cellHeight: ch,
      );
      canvas.restore();
    }
    final path = Path();
    for (var x = left; x <= right; x++) {
      path.moveTo(x * cw, top * ch);
      path.lineTo(x * cw, bottom * ch);
    }
    for (var y = top; y <= bottom; y++) {
      path.moveTo(left * cw, y * ch);
      path.lineTo(right * cw, y * ch);
    }
    canvas.drawPath(
      path,
      paint
        ..color = switch (renderStyle) {
          ArtworkRenderStyle.canvas => const Color(0x664f5965),
          ArtworkRenderStyle.diamond => const Color(0x22546276),
          ArtworkRenderStyle.pixel => const Color(0xffa5b0a5),
        }
        ..style = PaintingStyle.stroke
        ..strokeWidth = 0.6 / scale,
    );
    final hint = controller.hintIndex;
    if (hint != null && !session.isCompleted(hint)) {
      final hx = hint % level.width;
      final hy = hint ~/ level.width;
      final hintRect = Rect.fromLTWH(hx * cw, hy * ch, cw, ch);
      canvas.drawRect(hintRect, Paint()..color = const Color(0x66ffac42));
      canvas.drawRect(
        hintRect.deflate(1 / scale),
        Paint()
          ..color = const Color(0xffff8200)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 3 / scale,
      );
    }
    if (cursor != null) {
      canvas.drawRect(
        Rect.fromLTWH(cursor!.$1 * cw, cursor!.$2 * ch, cw, ch),
        paint
          ..color = PixelTokens.green
          ..strokeWidth = 2 / scale,
      );
    }
    for (final label in labels.values) {
      label.dispose();
    }
  }

  @override
  bool shouldRepaint(_GridPainter old) =>
      old.controller != controller ||
      old.persian != persian ||
      old.cursor != cursor ||
      old.renderStyle != renderStyle;
}
