import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:level_schema/level_schema.dart';

import '../../core/pixel_art_preview.dart';
import '../../l10n/strings.dart';
import 'export_button.dart';
import 'artwork_economy.dart';
import 'gallery_screen.dart';
import 'library_controller.dart';
import '../painting/artwork_render_style.dart';
import '../painting/completed_artwork_preview.dart';

class ArtworkScreen extends StatelessWidget {
  const ArtworkScreen({
    required this.level,
    required this.library,
    required this.onDelete,
    this.animation,
    this.renderStyle = ArtworkRenderStyle.pixel,
    super.key,
  });
  final LevelDefinition level;
  final PixelAnimation? animation;
  final ArtworkRenderStyle renderStyle;
  final LibraryController library;
  final Future<void> Function(LevelDefinition) onDelete;

  Future<void> _delete(BuildContext context) async {
    final s = context.strings;
    final isOnline = level.id.startsWith('online-');
    final router = GoRouter.of(context);
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(isOnline ? s.removeDownloadedArtwork : s.deleteArtwork),
        content: Text(
          isOnline ? s.removeDownloadedArtworkMessage : s.deleteArtworkMessage,
        ),
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
      // Removing an online level rebuilds the artwork route immediately;
      // its BuildContext may no longer be mounted after the storage write.
      router.go(isOnline ? '/gallery' : '/my-gallery');
    } on Object {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(context.strings.librarySaveError)),
        );
      }
    }
  }

  Future<void> _unlock(BuildContext context) async {
    final messenger = ScaffoldMessenger.of(context);
    try {
      await library.unlock(level);
      if (!context.mounted) return;
      messenger.showSnackBar(
        SnackBar(content: Text(context.strings.artworkUnlocked)),
      );
      context.go('/painting/${level.id}');
    } on Object {
      if (!context.mounted) return;
      messenger.showSnackBar(
        SnackBar(
          content: Text(
            library.coins < priceForLevel(level)
                ? context.strings.insufficientCoins
                : context.strings.coinSaveFailed,
          ),
        ),
      );
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
        ),
        body: SafeArea(
          child: ListView(
            padding: const EdgeInsets.all(24),
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(24),
                child: library.isComplete(level) && animation != null
                    ? CompletedArtworkPreview(
                        level: level,
                        animation: animation,
                        renderStyle: renderStyle,
                      )
                    : PixelArtPreview(level: level, renderStyle: renderStyle),
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
              const SizedBox(height: 10),
              Row(
                children: [
                  const Icon(Icons.monetization_on_outlined, size: 20),
                  const SizedBox(width: 6),
                  Text(
                    '${s.walletCoins}: ${context.digits(library.coins)}',
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(s.artworkReward(context.digits(rewardForLevel(level)))),
              const SizedBox(height: 8),
              if (!library.canPaint(level))
                Text(s.artworkCost(context.digits(priceForLevel(level)))),
              const SizedBox(height: 12),
              FilledButton.icon(
                key: ValueKey('artwork-access-${level.id}'),
                onPressed: library.busy || library.status != LibraryStatus.ready
                    ? null
                    : library.canPaint(level)
                    ? () => context.go('/painting/${level.id}')
                    : () => _unlock(context),
                icon: Icon(
                  library.canPaint(level) ? Icons.brush : Icons.lock_open,
                ),
                label: Text(
                  library.canPaint(level)
                      ? s.startPainting
                      : s.unlockArtwork(context.digits(priceForLevel(level))),
                ),
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
              if (library.isComplete(level))
                ExportButton(level: level, renderStyle: renderStyle),
              if (level.id.startsWith('private-') ||
                  level.id.startsWith('online-')) ...[
                const SizedBox(height: 16),
                if (level.id.startsWith('private-'))
                  Text(s.importPrivacy, style: const TextStyle(height: 1.8)),
                TextButton.icon(
                  onPressed: library.busy ? null : () => _delete(context),
                  icon: const Icon(Icons.delete_outline),
                  label: Text(
                    level.id.startsWith('online-')
                        ? s.removeDownloadedArtwork
                        : s.deleteArtwork,
                  ),
                ),
              ],
            ],
          ),
        ),
      );
    },
  );
}
