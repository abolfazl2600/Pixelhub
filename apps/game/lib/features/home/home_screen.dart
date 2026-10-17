import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:level_schema/level_schema.dart';

import '../../core/pixel_art_preview.dart';
import '../../l10n/strings.dart';
import '../gallery/library_controller.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({required this.levels, required this.library, super.key});
  final List<LevelDefinition> levels;
  final LibraryController library;

  @override
  Widget build(BuildContext context) {
    final level =
        library.recentlyOpenedLevel ??
        levels.firstWhere(
          (item) => item.id == 'sunflower',
          orElse: () => levels.first,
        );
    final savedCells = library.completed(level);
    final totalCells = level.cells.length;
    final hasProgress = savedCells > 0;
    final isComplete = savedCells == totalCells;
    final s = context.strings;
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          key: const ValueKey('home-scroll'),
          padding: const EdgeInsets.all(PixelTokens.space),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  const Expanded(
                    child: Text(
                      'PixelHub',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: 25,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ),
                  IconButton(
                    tooltip: s.settings,
                    icon: const Icon(Icons.settings_outlined),
                    onPressed: () => context.push('/settings'),
                  ),
                  IconButton(
                    tooltip: s.profile,
                    icon: const Icon(Icons.person_outline_rounded),
                    onPressed: () => context.push('/profile'),
                  ),
                ],
              ),
              Card(
                color: PixelTokens.lemon,
                child: Padding(
                  padding: const EdgeInsets.all(10),
                  child: Row(
                    children: [
                      const Icon(Icons.monetization_on_outlined),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          '${s.walletCoins}: ${context.digits(library.coins)}',
                          style: const TextStyle(fontWeight: FontWeight.w700),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
              Text(
                s.headline,
                style: const TextStyle(
                  fontSize: 38,
                  height: 1.4,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                s.welcome,
                style: const TextStyle(
                  color: PixelTokens.muted,
                  fontSize: 15,
                  height: 1.8,
                ),
              ),
              const SizedBox(height: 18),
              Card(
                color: PixelTokens.lemon,
                child: Padding(
                  padding: const EdgeInsets.all(14),
                  child: Row(
                    children: [
                      const Icon(
                        Icons.check_circle_outline_rounded,
                        color: PixelTokens.green,
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          s.homeCompleted(
                            context.digits(
                              library.levels.where(library.isComplete).length,
                            ),
                            context.digits(library.levels.length),
                          ),
                        ),
                      ),
                      TextButton(
                        onPressed: () => context.push('/profile'),
                        child: Text(s.profile),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  OutlinedButton.icon(
                    onPressed: () => context.push('/gallery'),
                    icon: const Icon(Icons.grid_view_rounded),
                    label: Text(s.gallery),
                  ),
                  OutlinedButton.icon(
                    onPressed: () => context.push('/my-gallery'),
                    icon: const Icon(Icons.collections_outlined),
                    label: Text(s.myGallery),
                  ),
                  OutlinedButton.icon(
                    key: const ValueKey('open-museum'),
                    onPressed: () => context.push('/museum'),
                    icon: const Icon(Icons.museum_outlined),
                    label: Text(s.museumTitle),
                  ),
                  OutlinedButton.icon(
                    key: const ValueKey('open-badges'),
                    onPressed: () => context.push('/badges'),
                    icon: const Icon(Icons.workspace_premium_outlined),
                    label: Text(
                      context.isPersian ? 'نشان‌ها' : 'Badges',
                    ),
                  ),
                  OutlinedButton.icon(
                    onPressed: () => context.push('/import'),
                    icon: const Icon(Icons.add_photo_alternate_outlined),
                    label: Text(s.importPhoto),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              Container(
                key: const ValueKey('home-featured-artwork'),
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: PixelTokens.peach,
                  borderRadius: BorderRadius.circular(PixelTokens.radius),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(16),
                      child: PixelArtPreview(level: level),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      level.titleFor(context.isPersian ? 'fa' : 'en'),
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    if (hasProgress) ...[
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              isComplete ? s.completedWorks : s.inProgress,
                              style: const TextStyle(
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                          Text(
                            s.progressPercent(
                              context.digits((savedCells * 100) ~/ totalCells),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      LinearProgressIndicator(value: savedCells / totalCells),
                    ],
                    const SizedBox(height: 16),
                    FilledButton.icon(
                      key: const ValueKey('open-preview'),
                      onPressed: () => context.go('/painting/${level.id}'),
                      icon: const Icon(Icons.brush_rounded),
                      label: Text(
                        isComplete
                            ? s.viewResult
                            : hasProgress
                            ? s.continuePainting
                            : s.startPainting,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
