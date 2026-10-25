import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import '../../l10n/strings.dart';
import '../../platform_adapters/timelapse_export.dart';
import 'painting_controller.dart';
import 'timelapse_gif_encoder.dart';

/// Loads genuine, unexpired checkpoints and creates a bounded local GIF.
/// Closing the dialog cancels use of any in-flight isolate result.
class PaintingTimelapseButton extends StatefulWidget {
  const PaintingTimelapseButton({required this.controller, super.key});
  final PaintingController controller;

  @override
  State<PaintingTimelapseButton> createState() =>
      _PaintingTimelapseButtonState();
}

class _PaintingTimelapseButtonState extends State<PaintingTimelapseButton> {
  bool _busy = false;
  bool _cancelled = false;
  Uint8List? _gif;
  String? _error;
  StateSetter? _dialogRefresh;

  void _updateDialog() => _dialogRefresh?.call(() {});

  Future<void> _generate() async {
    if (_busy) return;
    setState(() {
      _busy = true;
      _cancelled = false;
      _gif = null;
      _error = null;
    });
    _updateDialog();
    try {
      final session = widget.controller.session!;
      final generation = session.generation;
      // Use the controller's store to ensure queued checkpoint writes are read.
      final records = await widget.controller.readReplayCheckpoints();
      if (_cancelled || !mounted) return;
      final filtered = records
          .where((record) => record['generation'] == generation)
          .toList();
      final payload = <String, Object?>{
        'level': widget.controller.level.toJson(),
        'generation': generation,
        'checkpoints': filtered,
      };
      final bytes = await compute(encodePaintingTimelapse, payload);
      if (_cancelled || !mounted) return;
      setState(() => _gif = bytes);
      _updateDialog();
    } on Object {
      if (mounted && !_cancelled) {
        setState(
          () => _error = context.isPersian
              ? 'مراحل ضبط‌شده کافی نیستند یا منقضی شده‌اند.'
              : 'Replay steps are missing, incomplete or expired.',
        );
        _updateDialog();
      }
    } finally {
      if (mounted) {
        setState(() => _busy = false);
        _updateDialog();
      }
    }
  }

  void _open() {
    showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: Text(
          context.isPersian ? 'تایم‌لپس نقاشی' : 'Painting timelapse',
        ),
        content: StatefulBuilder(
          builder: (dialogContext, refresh) {
            _dialogRefresh = refresh;
            return SizedBox(
              width: 330,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (_busy) ...[
                    const CircularProgressIndicator(),
                    const SizedBox(height: 12),
                    Text(
                      context.isPersian ? 'در حال ساخت GIF…' : 'Creating GIF…',
                    ),
                  ] else if (_error != null)
                    Text(_error!)
                  else if (_gif != null)
                    Image.memory(
                      _gif!,
                      key: const ValueKey('timelapse-gif-preview'),
                      gaplessPlayback: false,
                      fit: BoxFit.contain,
                      width: 300,
                      height: 300,
                    )
                  else
                    Text(
                      context.isPersian
                          ? 'GIF آماده نشده است.'
                          : 'GIF is not ready.',
                    ),
                  const SizedBox(height: 12),
                  if (_gif != null)
                    FilledButton.icon(
                      onPressed: () async {
                        final origin =
                            (context.findRenderObject()! as RenderBox);
                        await exportTimelapse(
                          _gif!,
                          'pixelhub-${widget.controller.level.id}.gif',
                          origin.localToGlobal(Offset.zero) & origin.size,
                        );
                      },
                      icon: const Icon(Icons.ios_share),
                      label: Text(
                        context.isPersian
                            ? 'ذخیره / اشتراک‌گذاری GIF'
                            : 'Save / Share GIF',
                      ),
                    ),
                  TextButton(
                    onPressed: () {
                      _cancelled = true;
                      Navigator.pop(dialogContext);
                    },
                    child: Text(context.isPersian ? 'بستن' : 'Close'),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    ).then((_) {
      _cancelled = true;
      _dialogRefresh = null;
    });
    _generate();
  }

  @override
  Widget build(BuildContext context) => OutlinedButton.icon(
    key: const ValueKey('create-timelapse-gif'),
    onPressed: _busy ? null : _open,
    icon: const Icon(Icons.movie_creation_outlined),
    label: Text(
      context.isPersian ? 'ساخت GIF از مراحل نقاشی' : 'Create timelapse GIF',
    ),
  );
}
