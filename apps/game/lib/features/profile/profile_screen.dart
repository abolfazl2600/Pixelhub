import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../app/language_button.dart';
import '../../core/local_diagnostics.dart';
import '../../l10n/strings.dart';
import '../gallery/library_controller.dart';

/// Local guest profile. Wallet and remote analytics deliberately disabled.
class ProfileScreen extends StatelessWidget {
  const ProfileScreen({
    required this.library,
    required this.diagnostics,
    required this.onLanguageToggle,
    super.key,
  });

  final LibraryController library;
  final LocalDiagnostics diagnostics;
  final VoidCallback onLanguageToggle;

  @override
  Widget build(BuildContext context) {
    final s = context.strings;
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          onPressed: () => context.go('/'),
          tooltip: s.backHome,
          icon: const Icon(Icons.arrow_back_rounded),
        ),
        title: Text(s.profile),
        actions: [LanguageButton(onToggle: onLanguageToggle)],
      ),
      body: SafeArea(
        child: ListenableBuilder(
          listenable: Listenable.merge([library, diagnostics]),
          builder: (context, _) {
            final levels = library.levels;
            final completed = levels.where(library.isComplete).length;
            final favorites = levels.where(library.isFavorite).length;
            return ListView(
              padding: const EdgeInsets.all(PixelTokens.space),
              children: [
                Card(
                  color: PixelTokens.peach,
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const CircleAvatar(
                          radius: 26,
                          backgroundColor: PixelTokens.lemon,
                          child: Icon(Icons.person_outline_rounded),
                        ),
                        const SizedBox(height: 12),
                        Text(
                          s.guestMode,
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const SizedBox(height: 6),
                        Text(s.localStatsCaption),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 18),
                Text(
                  s.localProgressTitle,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 8),
                _MetricTile(
                  icon: Icons.check_circle_outline_rounded,
                  title: s.completedPictures,
                  value: context.digits(completed),
                ),
                _MetricTile(
                  icon: Icons.favorite_outline_rounded,
                  title: s.favorites,
                  value: context.digits(favorites),
                ),
                _MetricTile(
                  icon: Icons.grid_view_rounded,
                  title: s.allPictures,
                  value: context.digits(levels.length),
                ),
                const SizedBox(height: 18),
                Text(
                  s.localToolTitle,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 8),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(s.inventoryComingSoon),
                        const SizedBox(height: 10),
                        OutlinedButton.icon(
                          onPressed: null,
                          icon: const Icon(Icons.wallet_outlined),
                          label: Text(s.coinComingSoon),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          s.freeToolsNote,
                          style: const TextStyle(
                            fontSize: 12,
                            color: PixelTokens.muted,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 18),
                Text(
                  s.analyticsTitle,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 8),
                _MetricTile(
                  icon: Icons.open_in_new_rounded,
                  title: s.sessionViews,
                  value: context.digits(diagnostics.screenOpens),
                ),
                _MetricTile(
                  icon: Icons.lightbulb_outline_rounded,
                  title: s.sessionHints,
                  value: context.digits(diagnostics.hints),
                ),
                _MetricTile(
                  icon: Icons.auto_awesome_rounded,
                  title: s.sessionBombs,
                  value: context.digits(diagnostics.bombs),
                ),
                _MetricTile(
                  icon: Icons.error_outline_rounded,
                  title: s.sessionErrors,
                  value: context.digits(diagnostics.frameworkErrors),
                ),
                const SizedBox(height: 8),
                Text(
                  s.crashReportingDisabled,
                  style: const TextStyle(color: PixelTokens.muted),
                ),
                const SizedBox(height: 4),
                Text(
                  s.retentionComingSoon,
                  style: const TextStyle(color: PixelTokens.muted),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}

class _MetricTile extends StatelessWidget {
  const _MetricTile({
    required this.icon,
    required this.title,
    required this.value,
  });
  final IconData icon;
  final String title;
  final String value;

  @override
  Widget build(BuildContext context) => Card(
    margin: const EdgeInsets.only(bottom: 6),
    child: ListTile(
      leading: Icon(icon, color: PixelTokens.green),
      title: Text(title),
      trailing: Text(
        value,
        style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 17),
      ),
    ),
  );
}
