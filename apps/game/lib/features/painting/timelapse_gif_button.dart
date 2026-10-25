import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import '../../l10n/strings.dart';
import '../../platform_adapters/timelapse_gif_export.dart';
import 'painting_controller.dart';
import 'timelapse_gif_renderer.dart';

/// Completion-screen entry point for replay GIFs.
class TimelapseGifButton extends StatelessWidget {
  const TimelapseGifButton({required this.controller, super.key});

  final PaintingController controller;

  @override
  Widget build(BuildContext context) => OutlinedButton.icon(
    key: const ValueKey('create-timelapse-gif'),
    onPressed: () => showDialog<void>(
      context: context,
      builder: (context) => TimelapseGifDialog(controller: controller),
    ),
    icon: const Icon(Icons.movie_creation_outlined),
    label: Text(
      context.isPersian ? 'ساخت GIF مراحل نقاشی' : 'Create timelapse GIF',
    ),
  );
}

class TimelapseGifDialog extends StatefulWidget {
  const TimelapseGifDialog({required this.controller, super.key});

  final PaintingController controller;

  @override
  State<TimelapseGifDialog> createState() => _TimelapseGifDialogState();
}

class _TimelapseGifDialogState extends State<TimelapseGifDialog> {
  Uint8List? _gif;
  bool _busy = true;
  bool _exporting = false;
  String? _message;

  @override
  void initState() {
    super.initState();
    _generate();
  }

  Future<void> _generate() async {
    final controller = widget.controller;
    try {
      final complete = controller.session?.snapshot;
      if (complete == null || !controller.session!.isComplete) {
        throw const FormatException('Painting is not complete.');
      }
      final records = await controller.readReplayCheckpoints();
      if (!mounted) return;
      // Validate the current generation before allocating an encoder.
      prepareTimelapseFrames(controller.level, complete, records);
      final gif = await compute(renderTimelapseGif, <String, Object?>{
        'level': controller.level.toJson(),
        'completed': complete.toJson(),
        'checkpoints': records,
      });
      if (mounted) {
        setState(() {
          _gif = gif;
          _busy = false;
        });
      }
    } on Object {
      if (mounted) {
        setState(() {
          _message = context.isPersian
              ? 'تاریخچه کافی و معتبر وجود ندارد؛ ممکن است مراحل نقاشی منقضی شده باشند.'
              : 'Complete, unexpired painting replay data is unavailable.';
          _busy = false;
        });
      }
    }
  }

  Future<void> _export({required bool share}) async {
    final bytes = _gif;
    if (bytes == null || _exporting) return;
    final box = context.findRenderObject();
    final origin = box is RenderBox
        ? box.localToGlobal(Offset.zero) & box.size
        : const Rect.fromLTWH(0, 0, 1, 1);
    setState(() => _exporting = true);
    try {
      final name = 'pixelhub-${widget.controller.level.id}-timelapse.gif';
      final result = share
          ? await shareTimelapseGif(bytes, name, origin)
          : await saveTimelapseGif(bytes, name, origin);
      if (mounted && result) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              context.isPersian
                  ? 'GIF برای ذخیره یا اشتراک‌گذاری آماده شد.'
                  : 'GIF is ready to save or share.',
            ),
          ),
        );
      }
    } on Object {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              context.isPersian
                  ? 'ذخیره GIF ناموفق بود.'
                  : 'GIF export failed.',
            ),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _exporting = false);
    }
  }

  @override
  void dispose() {
    // Dropping the bytes cancels preview and discards any late compute result.
    _gif = null;
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final persian = context.isPersian;
    return AlertDialog(
      title: Text(persian ? 'تایم‌لپس نقاشی' : 'Painting timelapse'),
      content: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 360),
        child: _busy
            ? const SizedBox(
                height: 130,
                child: Center(child: CircularProgressIndicator()),
              )
            : _gif == null
            ? Text(_message ?? '')
            : Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Image.memory(
                    _gif!,
                    key: const ValueKey('timelapse-preview'),
                    width: 256,
                    height: 256,
                    fit: BoxFit.contain,
                    filterQuality: FilterQuality.none,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    persian
                        ? 'بازپخش مراحل واقعی رنگ‌آمیزی شما'
                        : 'Replay of your recorded painting steps',
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
      ),
      actions: [
        TextButton(
          key: const ValueKey('timelapse-close'),
          onPressed: () => Navigator.of(context).pop(),
          child: Text(persian ? 'بستن / لغو' : 'Close / Cancel'),
        ),
        if (_gif != null) ...[
          TextButton.icon(
            key: const ValueKey('timelapse-save'),
            onPressed: _exporting ? null : () => _export(share: false),
            icon: const Icon(Icons.download_outlined),
            label: Text(persian ? 'ذخیره GIF' : 'Save GIF'),
          ),
          TextButton.icon(
            key: const ValueKey('timelapse-share'),
            onPressed: _exporting ? null : () => _export(share: true),
            icon: const Icon(Icons.share_outlined),
            label: Text(persian ? 'اشتراک‌گذاری' : 'Share'),
          ),
        ],
      ],
    );
  }
}
