import 'dart:math';

import 'package:file_selector/file_selector.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:game_domain/game_domain.dart';
import 'package:go_router/go_router.dart';
import 'package:level_schema/level_schema.dart';

import '../../app/language_button.dart';
import '../../core/pixel_art_preview.dart';
import '../../l10n/strings.dart';
import '../gallery/library_controller.dart';
import 'photo_converter.dart';

class ImportScreen extends StatefulWidget {
  const ImportScreen({
    required this.library,
    required this.onLanguageToggle,
    super.key,
  });
  final LibraryController library;
  final VoidCallback onLanguageToggle;
  @override
  State<ImportScreen> createState() => _ImportScreenState();
}

class _ImportScreenState extends State<ImportScreen> {
  final _title = TextEditingController();
  NormalizedPhoto? _photo;
  LevelDefinition? _preview;
  String? _id;
  String? _error;
  bool _busy = false;
  String _difficulty = 'easy';
  int _colors = 8;
  int _turns = 0;
  double _cropX = .5, _cropY = .5;
  int get _size => switch (_difficulty) {
    'easy' => 32,
    'normal' => 64,
    _ => 128,
  };

  String _newId() {
    final random = Random.secure();
    final bytes = List.generate(16, (_) => random.nextInt(256));
    bytes[6] = (bytes[6] & 15) | 64;
    bytes[8] = (bytes[8] & 63) | 128;
    final hex = bytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join();
    return 'private-${hex.substring(0, 8)}-${hex.substring(8, 12)}-${hex.substring(12, 16)}-${hex.substring(16, 20)}-${hex.substring(20)}';
  }

  Future<void> _pick() async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final file = await openFile(
        acceptedTypeGroups: [
          const XTypeGroup(
            label: 'JPEG / PNG / WebP',
            extensions: ['jpg', 'jpeg', 'png', 'webp'],
            mimeTypes: ['image/jpeg', 'image/png', 'image/webp'],
          ),
        ],
      );
      if (file == null) {
        return;
      }
      if (await file.length() > maxPhotoBytes) {
        throw const FormatException('photoTooLarge');
      }
      if (!mounted) {
        return;
      }
      await WidgetsBinding.instance.endOfFrame;
      final normalized = await compute(
        normalizePhoto,
        await file.readAsBytes(),
      );
      if (!mounted) {
        return;
      }
      setState(() {
        _photo = normalized;
        _preview = null;
        _id = _newId();
        _turns = 0;
        _cropX = .5;
        _cropY = .5;
      });
    } on FormatException catch (error) {
      if (mounted) {
        setState(() => _error = error.message);
      }
    } on Object {
      if (mounted) {
        setState(() => _error = 'photoUnsupported');
      }
    } finally {
      if (mounted) {
        setState(() => _busy = false);
      }
    }
  }

  void _changed(VoidCallback change) => setState(() {
    change();
    _preview = null;
    _error = null;
  });

  Future<void> _convert() async {
    setState(() {
      _busy = true;
      _error = null;
    });
    // Yield one UI frame before synchronous Web processing.
    await WidgetsBinding.instance.endOfFrame;
    try {
      final title = _title.text.trim();
      final json = await compute(convertPhoto, <String, Object>{
        'bytes': _photo!.bytes,
        'id': _id!,
        'title': title.isEmpty ? 'عکس من' : title,
        'titleEn': title.isEmpty ? 'My photo' : title,
        'size': _size,
        'colorLimit': _colors,
        'quarterTurns': _turns,
        'cropX': _cropX,
        'cropY': _cropY,
      });
      if (mounted) {
        setState(() => _preview = LevelDefinition.fromJson(json));
      }
    } on Object {
      if (mounted) {
        setState(() => _error = 'convertError');
      }
    } finally {
      if (mounted) {
        setState(() => _busy = false);
      }
    }
  }

  Future<void> _save() async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final level = _preview!;
      await widget.library.add(
        PrivateArtwork(
          level: level,
          createdAt: DateTime.now().toUtc(),
          difficulty: _difficulty,
          colorLimit: _colors,
          quarterTurns: _turns,
          cropX: _cropX,
          cropY: _cropY,
        ),
      );
      if (mounted) {
        context.go('/painting/${level.id}');
      }
    } on Object {
      if (mounted) {
        setState(() => _error = 'librarySaveError');
      }
    } finally {
      if (mounted) {
        setState(() => _busy = false);
      }
    }
  }

  String _errorText() => switch (_error) {
    'photoTooLarge' => context.strings.photoTooLarge,
    'photoAnimated' => context.strings.photoAnimated,
    'librarySaveError' => context.strings.librarySaveError,
    'convertError' => context.strings.convertError,
    _ => context.strings.photoUnsupported,
  };

  @override
  Widget build(BuildContext context) {
    final s = context.strings;
    final photo = _photo;
    final horizontal =
        photo != null &&
        (_turns.isEven
            ? photo.width > photo.height
            : photo.height > photo.width);
    return PopScope(
      canPop: !_busy,
      child: Scaffold(
        appBar: AppBar(
          leading: IconButton(
            tooltip: s.backHome,
            onPressed: _busy ? null : () => context.go('/'),
            icon: const Icon(Icons.arrow_back),
          ),
          title: Text(s.importPhoto),
          actions: [LanguageButton(onToggle: widget.onLanguageToggle)],
        ),
        body: SafeArea(
          child: ListView(
            padding: const EdgeInsets.all(24),
            children: [
              Text(s.importPrivacy, style: const TextStyle(height: 1.8)),
              const SizedBox(height: 12),
              Text(s.photoLimits, style: const TextStyle(fontSize: 12)),
              const SizedBox(height: 20),
              OutlinedButton.icon(
                onPressed: _busy ? null : _pick,
                icon: const Icon(Icons.add_photo_alternate_outlined),
                label: Text(photo == null ? s.choosePhoto : s.replacePhoto),
              ),
              if (_busy) ...[
                const SizedBox(height: 16),
                LinearProgressIndicator(semanticsLabel: s.processingPhoto),
              ],
              if (_error != null)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  child: Text(
                    _errorText(),
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                ),
              if (photo != null) ...[
                const SizedBox(height: 20),
                Text(
                  s.cropPhoto,
                  style: const TextStyle(fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 12),
                // Explicit LTR physical crop controls match converter coordinates.
                ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: AspectRatio(
                    aspectRatio: 1,
                    child: LayoutBuilder(
                      builder: (context, bounds) {
                        final width = _turns.isEven
                            ? photo.width
                            : photo.height;
                        final height = _turns.isEven
                            ? photo.height
                            : photo.width;
                        final scale = bounds.maxWidth / min(width, height);
                        return ClipRect(
                          child: OverflowBox(
                            alignment: Alignment(
                              _cropX * 2 - 1,
                              _cropY * 2 - 1,
                            ),
                            minWidth: width * scale,
                            maxWidth: width * scale,
                            minHeight: height * scale,
                            maxHeight: height * scale,
                            child: RotatedBox(
                              quarterTurns: _turns,
                              child: Image.memory(
                                photo.bytes,
                                fit: BoxFit.fill,
                                gaplessPlayback: true,
                              ),
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                ),
                OutlinedButton.icon(
                  onPressed: _busy
                      ? null
                      : () => _changed(() {
                          _turns = (_turns + 1) % 4;
                          _cropX = .5;
                          _cropY = .5;
                        }),
                  icon: const Icon(Icons.rotate_right),
                  label: Text(s.rotatePhoto),
                ),
                Text(horizontal ? s.cropHorizontal : s.cropVertical),
                Directionality(
                  textDirection: TextDirection.ltr,
                  child: Slider(
                    value: horizontal ? _cropX : _cropY,
                    onChanged: _busy
                        ? null
                        : (value) => _changed(() {
                            if (horizontal) {
                              _cropX = value;
                            } else {
                              _cropY = value;
                            }
                          }),
                  ),
                ),
                TextField(
                  controller: _title,
                  enabled: !_busy,
                  maxLength: 60,
                  decoration: InputDecoration(
                    labelText: s.artworkName,
                    border: const OutlineInputBorder(),
                  ),
                  onChanged: (_) => _changed(() {}),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  initialValue: _difficulty,
                  decoration: InputDecoration(
                    labelText: s.difficulty,
                    border: const OutlineInputBorder(),
                  ),
                  items: [
                    DropdownMenuItem(
                      value: 'easy',
                      child: Text(
                        '${s.easy} · ${context.digits(32)} × ${context.digits(32)}',
                      ),
                    ),
                    DropdownMenuItem(
                      value: 'normal',
                      child: Text(
                        '${s.normal} · ${context.digits(64)} × ${context.digits(64)}',
                      ),
                    ),
                    DropdownMenuItem(
                      value: 'hard',
                      child: Text(
                        '${s.hard} · ${context.digits(128)} × ${context.digits(128)}',
                      ),
                    ),
                  ],
                  onChanged: _busy
                      ? null
                      : (value) {
                          if (value != null) {
                            _changed(() {
                              _difficulty = value;
                              _colors = switch (value) {
                                'easy' => 8,
                                'normal' => 16,
                                _ => 24,
                              };
                            });
                          }
                        },
                ),
                const SizedBox(height: 16),
                Text('${s.colorLimit}: ${context.digits(_colors)}'),
                Slider(
                  value: _colors.toDouble(),
                  min: 2,
                  max: 24,
                  divisions: 22,
                  label: context.digits(_colors),
                  onChanged: _busy
                      ? null
                      : (value) => _changed(() => _colors = value.round()),
                ),
                FilledButton.icon(
                  onPressed: _busy ? null : _convert,
                  icon: const Icon(Icons.auto_awesome_mosaic),
                  label: Text(s.convertPreview),
                ),
                if (_preview != null) ...[
                  const SizedBox(height: 24),
                  Text(
                    s.previewTitle,
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                  const SizedBox(height: 12),
                  PixelArtPreview(level: _preview!),
                  const SizedBox(height: 12),
                  Text(
                    '${context.digits(_preview!.width)} × ${context.digits(_preview!.height)} · ${context.digits(_preview!.palette.length)} ${s.colors}',
                  ),
                  const SizedBox(height: 12),
                  Text(
                    s.originalNotStored,
                    style: const TextStyle(fontSize: 12, height: 1.8),
                  ),
                  const SizedBox(height: 16),
                  ListenableBuilder(
                    listenable: widget.library,
                    builder: (context, _) => FilledButton.icon(
                      onPressed:
                          _busy ||
                              widget.library.busy ||
                              widget.library.status != LibraryStatus.ready ||
                              widget.library.library.artworks.length >= 20
                          ? null
                          : _save,
                      icon: const Icon(Icons.brush),
                      label: Text(s.saveAndPaint),
                    ),
                  ),
                  if (widget.library.library.artworks.length >= 20)
                    Text(s.libraryLimit),
                ],
              ],
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _title.dispose();
    super.dispose();
  }
}
