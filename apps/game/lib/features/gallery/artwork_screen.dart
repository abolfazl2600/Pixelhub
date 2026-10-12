import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:level_schema/level_schema.dart';

import '../../app/language_button.dart';
import '../../core/pixel_art_preview.dart';
import '../../l10n/strings.dart';
import 'export_button.dart';
import 'gallery_screen.dart';
import 'library_controller.dart';

class ArtworkScreen extends StatelessWidget {
  const ArtworkScreen({
    required this.level,
    required this.library,
    required this.onLanguageToggle,
    required this.onDelete,
    super.key,
  });
  final LevelDefinition level;
  final LibraryController library;
  final VoidCallback onLanguageToggle;
  final Future<void> Function(LevelDefinition) onDelete;

  Future<void> _delete(BuildContext context) async {
    final s = context.strings;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(s.deleteArtwork),
        content: Text(s.deleteArtworkMessage),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(s.cancel),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text(s.delete),
          ),
        ],
      ),
    );
    if (confirmed != true) {
      return;
    }
    try {
      await onDelete(level);
      if (context.mounted) {
        context.go('/my-gallery');
      }
    } on Object {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(context.strings.librarySaveError)),
        );
      }
    }
  }

  Future<void> _favorite(BuildContext context) async {
    try {
      await library.toggleFavorite(level);
    } on Object {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(context.strings.librarySaveError)),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: library,
    builder: (context, _) {
      final s = context.strings;
      return Scaffold(
        appBar: AppBar(
          leading: IconButton(
            tooltip: s.backHome,
            onPressed: () {
              if (context.canPop()) {
                context.pop();
              } else {
                context.go('/gallery');
              }
            },
            icon: const Icon(Icons.arrow_back),
          ),
          title: Text(level.titleFor(context.isPersian ? 'fa' : 'en')),
          actions: [LanguageButton(onToggle: onLanguageToggle)],
        ),
        body: SafeArea(
          child: ListView(
            padding: const EdgeInsets.all(24),
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(24),
                child: PixelArtPreview(level: level),
              ),
              const SizedBox(height: 20),
              Text(
                categoryLabel(context, library.category(level)),
                style: const TextStyle(fontWeight: FontWeight.w700),
              ),
              Text(
                '${context.digits(level.width)} × ${context.digits(level.height)} · ${context.digits(level.palette.length)} ${s.colors}',
              ),
              const SizedBox(height: 12),
              if (library.completed(level) > 0) ...[
                LinearProgressIndicator(
                  value: library.completed(level) / level.cells.length,
                ),
                const SizedBox(height: 8),
                Text(
                  s.progressSummary(
                    context.digits(library.completed(level)),
                    context.digits(level.cells.length),
                  ),
                ),
              ],
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: () => context.push('/painting/${level.id}'),
                icon: const Icon(Icons.brush),
                label: Text(s.startPainting),
              ),
              const SizedBox(height: 8),
              OutlinedButton.icon(
                onPressed: library.busy || library.status != LibraryStatus.ready
                    ? null
                    : () => _favorite(context),
                icon: Icon(
                  library.isFavorite(level)
                      ? Icons.favorite
                      : Icons.favorite_border,
                ),
                label: Text(
                  library.isFavorite(level) ? s.removeFavorite : s.addFavorite,
                ),
              ),
              if (library.isComplete(level)) ExportButton(level: level),
              if (level.id.startsWith('private-')) ...[
                const SizedBox(height: 16),
                Text(s.importPrivacy, style: const TextStyle(height: 1.8)),
                TextButton.icon(
                  onPressed: library.busy ? null : () => _delete(context),
                  icon: const Icon(Icons.delete_outline),
                  label: Text(s.deleteArtwork),
                ),
              ],
            ],
          ),
        ),
      );
    },
  );
}
