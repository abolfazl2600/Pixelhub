import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:level_schema/level_schema.dart';

import '../../l10n/strings.dart';
import '../painting/artwork_render_style.dart';
import '../../platform_adapters/artwork_export.dart';
import '../import/photo_converter.dart';

class ExportButton extends StatefulWidget {
  const ExportButton({required this.level, super.key});
  final LevelDefinition level;
  @override
  State<ExportButton> createState() => _ExportButtonState();
}

class _ExportButtonState extends State<ExportButton> {
  bool _busy = false;
  Future<void> _export() async {
    final box = context.findRenderObject()! as RenderBox;
    final origin = box.localToGlobal(Offset.zero) & box.size;
    final level = widget.level;
    setState(() => _busy = true);
    try {
      final bytes = await compute(renderLevelPng, level.toJson());
      if (!mounted) {
        return;
      }
      final exported = await exportArtwork(
        bytes,
        'pixelhub-${level.id}.png',
        origin,
      );
      if (mounted && exported) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(context.strings.exportReady)));
      }
    } on Object {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(context.strings.exportError)));
      }
    } finally {
      if (mounted) {
        setState(() => _busy = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) => OutlinedButton.icon(
    onPressed: _busy ? null : _export,
    icon: _busy
        ? const SizedBox.square(
            dimension: 20,
            child: CircularProgressIndicator(strokeWidth: 2),
          )
        : const Icon(Icons.ios_share_rounded),
    label: Text(context.strings.exportPng),
  );
}
