import 'dart:async';

import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../l10n/strings.dart';
import 'badge_controller.dart';

/// Mystery cards conceal the icon, name and objective until an award is earned.
class BadgesScreen extends StatefulWidget {
  const BadgesScreen({required this.badges, super.key});

  final BadgeController badges;

  @override
  State<BadgesScreen> createState() => _BadgesScreenState();
}

class _BadgesScreenState extends State<BadgesScreen> {
  @override
  void initState() {
    super.initState();
    if (!widget.badges.refreshing) {
      unawaited(widget.badges.refresh());
    }
  }

  @override
  Widget build(BuildContext context) {
    final persian = context.isPersian;
    final title = persian ? 'نشان‌های افتخار' : 'Achievements';
    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        leading: IconButton(
          tooltip: persian ? 'بازگشت به خانه' : 'Back home',
          icon: const Icon(Icons.arrow_back_rounded),
          onPressed: () => context.go('/'),
        ),
      ),
      body: SafeArea(
        child: ListenableBuilder(
          listenable: widget.badges,
          builder: (context, _) {
            final badges = widget.badges;
            if (!badges.hasCatalog) {
              return Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (badges.refreshing)
                        const CircularProgressIndicator.adaptive()
                      else
                        const Icon(Icons.wifi_off_outlined, size: 48),
                      const SizedBox(height: 16),
                      Text(
                        badges.refreshing
                            ? (persian
                                  ? 'در حال آماده‌سازی نشان‌ها...'
                                  : 'Loading achievements...')
                            : (persian
                                  ? 'نشان‌ها فعلاً در دسترس نیستند.'
                                  : 'Achievements are temporarily unavailable.'),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 12),
                      if (!badges.refreshing)
                        OutlinedButton(
                          key: const ValueKey('badges-retry'),
                          onPressed: badges.refresh,
                          child: Text(persian ? 'تلاش دوباره' : 'Try again'),
                        ),
                    ],
                  ),
                ),
              );
            }
            return RefreshIndicator(
              onRefresh: badges.refresh,
              child: LayoutBuilder(
                builder: (context, constraints) {
                  final columns = constraints.maxWidth >= 650 ? 3 : 2;
                  return CustomScrollView(
                    key: const ValueKey('badges-scroll'),
                    physics: const AlwaysScrollableScrollPhysics(),
                    slivers: [
                      SliverPadding(
                        padding: const EdgeInsets.all(PixelTokens.space),
                        sliver: SliverToBoxAdapter(
                          child: Card(
                            child: Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    persian
                                        ? 'مجموعه نشان‌های من'
                                        : 'My badge collection',
                                    style: Theme.of(
                                      context,
                                    ).textTheme.titleLarge,
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    persian
                                        ? '${context.digits(badges.earnedCount)} از ${context.digits(badges.badges.length)} نشان دریافت شده'
                                        : '${badges.earnedCount} of ${badges.badges.length} earned',
                                  ),
                                  const SizedBox(height: 12),
                                  LinearProgressIndicator(
                                    value:
                                        badges.earnedCount /
                                        badges.badges.length,
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    persian
                                        ? 'با تکمیل نقاشی‌ها، نشان‌های ناشناخته را کشف کن.'
                                        : 'Complete paintings to discover hidden achievements.',
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),
                      SliverPadding(
                        padding: const EdgeInsets.symmetric(
                          horizontal: PixelTokens.space,
                        ),
                        sliver: SliverGrid(
                          gridDelegate:
                              SliverGridDelegateWithFixedCrossAxisCount(
                                crossAxisCount: columns,
                                childAspectRatio: .76,
                                mainAxisSpacing: 12,
                                crossAxisSpacing: 12,
                              ),
                          delegate: SliverChildBuilderDelegate((
                            context,
                            index,
                          ) {
                            final badge = badges.badges[index];
                            final earned = badges.isEarned(badge);
                            final bytes = earned
                                ? badges.imageFor(badge)
                                : null;
                            return Card(
                              key: ValueKey('badge-${badge.id}'),
                              color: earned
                                  ? null
                                  : Theme.of(
                                      context,
                                    ).colorScheme.surfaceContainerHighest,
                              child: Padding(
                                padding: const EdgeInsets.all(10),
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Container(
                                      width: 76,
                                      height: 76,
                                      alignment: Alignment.center,
                                      decoration: BoxDecoration(
                                        color: earned
                                            ? PixelTokens.lemon
                                            : Colors.black12,
                                        borderRadius: BorderRadius.circular(12),
                                      ),
                                      child: bytes != null
                                          ? Image.memory(
                                              bytes,
                                              width: 64,
                                              height: 64,
                                              filterQuality: FilterQuality.none,
                                              gaplessPlayback: true,
                                            )
                                          : Icon(
                                              earned
                                                  ? Icons
                                                        .workspace_premium_outlined
                                                  : Icons.help_outline_rounded,
                                              color: earned
                                                  ? PixelTokens.green
                                                  : Colors.grey.shade600,
                                              size: 46,
                                            ),
                                    ),
                                    const SizedBox(height: 12),
                                    Text(
                                      earned
                                          ? badge.titleFor(persian)
                                          : (persian
                                                ? 'نشان ناشناخته'
                                                : 'Mystery badge'),
                                      style: const TextStyle(
                                        fontWeight: FontWeight.w800,
                                      ),
                                      textAlign: TextAlign.center,
                                      maxLines: 2,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                    const SizedBox(height: 6),
                                    Flexible(
                                      child: Text(
                                        earned
                                            ? badge.descriptionFor(persian)
                                            : (persian
                                                  ? 'هنوز کشف نشده'
                                                  : 'Not discovered yet'),
                                        textAlign: TextAlign.center,
                                        maxLines: 3,
                                        overflow: TextOverflow.ellipsis,
                                        style: Theme.of(
                                          context,
                                        ).textTheme.bodySmall,
                                      ),
                                    ),
                                    const SizedBox(height: 6),
                                    Icon(
                                      earned
                                          ? Icons.verified_rounded
                                          : Icons.lock_outline_rounded,
                                      size: 20,
                                      color: earned
                                          ? PixelTokens.green
                                          : Colors.grey,
                                    ),
                                  ],
                                ),
                              ),
                            );
                          }, childCount: badges.badges.length),
                        ),
                      ),
                      const SliverToBoxAdapter(child: SizedBox(height: 24)),
                    ],
                  );
                },
              ),
            );
          },
        ),
      ),
    );
  }
}
