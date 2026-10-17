import 'dart:async';
import 'dart:math' as math;
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../l10n/strings.dart';
import 'badge_controller.dart';

/// The mission description stays visible while an unearned badge's name
/// and artwork remain hidden. All descriptions are supplied by the catalog.
class BadgesScreen extends StatefulWidget {
  const BadgesScreen({required this.badges, super.key});

  final BadgeController badges;

  @override
  State<BadgesScreen> createState() => _BadgesScreenState();
}

abstract final class _BadgePalette {
  static const background = Color(0xfffaf9f5);
  static const ink = Color(0xff234239);
  static const muted = Color(0xff68766d);
  static const green = Color(0xff348560);
  static const border = Color(0xffe3e8df);
  static const mystery = Color(0xffd8dcd8);
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
    return Scaffold(
      backgroundColor: _BadgePalette.background,
      appBar: AppBar(
        backgroundColor: _BadgePalette.background,
        surfaceTintColor: Colors.transparent,
        title: Text(
          persian ? 'نشان‌های افتخار' : 'Achievements',
          style: const TextStyle(
            color: _BadgePalette.ink,
            fontWeight: FontWeight.w800,
          ),
        ),
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
            final controller = widget.badges;
            if (!controller.hasCatalog) {
              return Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (controller.refreshing)
                        const CircularProgressIndicator.adaptive()
                      else
                        const Icon(Icons.wifi_off_outlined, size: 48),
                      const SizedBox(height: 16),
                      Text(
                        controller.refreshing
                            ? (persian
                                  ? 'در حال آماده‌سازی نشان‌ها...'
                                  : 'Loading achievements...')
                            : (persian
                                  ? 'نشان‌ها فعلاً در دسترس نیستند.'
                                  : 'Achievements are temporarily unavailable.'),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 12),
                      if (!controller.refreshing)
                        OutlinedButton(
                          key: const ValueKey('badges-retry'),
                          onPressed: controller.refresh,
                          child: Text(persian ? 'تلاش دوباره' : 'Try again'),
                        ),
                    ],
                  ),
                ),
              );
            }

            return RefreshIndicator(
              onRefresh: controller.refresh,
              child: LayoutBuilder(
                builder: (context, constraints) {
                  // Two legible columns on phones; three on tablets/desktop.
                  final columns = constraints.maxWidth >= 700 ? 3 : 2;
                  final cardHeight = constraints.maxWidth >= 700 ? 266.0 : 282.0;
                  return CustomScrollView(
                    key: const ValueKey('badges-scroll'),
                    physics: const AlwaysScrollableScrollPhysics(),
                    slivers: [
                      SliverPadding(
                        padding: const EdgeInsets.fromLTRB(16, 16, 16, 20),
                        sliver: SliverToBoxAdapter(
                          child: _BadgeProgressHeader(
                            earned: controller.earnedCount,
                            total: controller.badges.length,
                            persian: persian,
                          ),
                        ),
                      ),
                      SliverPadding(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        sliver: SliverGrid(
                          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: columns,
                            mainAxisExtent: cardHeight,
                            mainAxisSpacing: 14,
                            crossAxisSpacing: 14,
                          ),
                          delegate: SliverChildBuilderDelegate(
                            (context, index) {
                              final badge = controller.badges[index];
                              final earned = controller.isEarned(badge);
                              return _AchievementCard(
                                key: ValueKey('badge-' + badge.id),
                                definition: badge,
                                earned: earned,
                                iconBytes: earned ? controller.imageFor(badge) : null,
                                persian: persian,
                              );
                            },
                            childCount: controller.badges.length,
                          ),
                        ),
                      ),
                      const SliverToBoxAdapter(child: SizedBox(height: 30)),
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

class _BadgeProgressHeader extends StatelessWidget {
  const _BadgeProgressHeader({
    required this.earned,
    required this.total,
    required this.persian,
  });

  final int earned;
  final int total;
  final bool persian;

  @override
  Widget build(BuildContext context) {
    final headline = Theme.of(context).textTheme.titleLarge;
    return DecoratedBox(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(25),
        gradient: const LinearGradient(
          begin: AlignmentDirectional.topStart,
          end: AlignmentDirectional.bottomEnd,
          colors: [Color(0xfff6faf4), Color(0xffe9f3e9)],
        ),
        border: Border.all(color: const Color(0xffe1eade)),
        boxShadow: const [
          BoxShadow(
            color: Color(0x110e3f2b),
            blurRadius: 19,
            offset: Offset(0, 7),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(25),
        child: Stack(
          children: [
            const PositionedDirectional(
              end: -15,
              bottom: -20,
              child: IgnorePointer(
                child: SizedBox(
                  width: 140,
                  height: 170,
                  child: CustomPaint(painter: _LeafPainter()),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 22,
                vertical: 25,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(
                        Icons.eco_outlined,
                        color: _BadgePalette.green,
                        size: 23,
                      ),
                      const SizedBox(width: 8),
                      Flexible(
                        child: Text(
                          persian
                              ? 'مجموعه نشان‌های من'
                              : 'My badge collection',
                          style: headline?.copyWith(
                            fontWeight: FontWeight.w800,
                            color: _BadgePalette.ink,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 9),
                  Text(
                    persian
                        ? context.digits(earned) +
                              ' از ' +
                              context.digits(total) +
                              ' نشان دریافت شده'
                        : '$earned of $total earned',
                    style: const TextStyle(
                      color: _BadgePalette.ink,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 17),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(99),
                    child: Directionality(
                      textDirection: persian
                          ? TextDirection.rtl
                          : TextDirection.ltr,
                      child: LinearProgressIndicator(
                        minHeight: 9,
                        value: total == 0 ? 0 : earned / total,
                        backgroundColor: const Color(0xffd3e2d5),
                        valueColor: const AlwaysStoppedAnimation<Color>(
                          _BadgePalette.green,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 13),
                  Text(
                    persian
                        ? 'با تکمیل نقاشی‌ها، نشان‌های بیشتری دریافت کن.'
                        : 'Complete paintings to earn more badges.',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: _BadgePalette.muted,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _AchievementCard extends StatelessWidget {
  const _AchievementCard({
    required this.definition,
    required this.earned,
    required this.iconBytes,
    required this.persian,
    super.key,
  });

  final BadgeDefinition definition;
  final bool earned;
  final Uint8List? iconBytes;
  final bool persian;

  @override
  Widget build(BuildContext context) {
    final title = earned
        ? definition.titleFor(persian)
        : (persian ? 'نشان ناشناخته' : 'Mystery badge');
    final description = definition.descriptionFor(persian);
    return Semantics(
      label: title + '، ' + description,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: earned ? const Color(0xfff0f9f0) : const Color(0xfffffefb),
          borderRadius: BorderRadius.circular(23),
          border: Border.all(
            color: earned ? const Color(0xffd3e7d2) : _BadgePalette.border,
          ),
          boxShadow: const [
            BoxShadow(
              color: Color(0x100d3526),
              blurRadius: 16,
              offset: Offset(0, 5),
            ),
          ],
        ),
        child: Stack(
          clipBehavior: Clip.hardEdge,
          children: [
            if (earned)
              const PositionedDirectional(
                end: -39,
                top: -20,
                child: IgnorePointer(
                  child: Icon(
                    Icons.spa_rounded,
                    size: 115,
                    color: Color(0x1666a877),
                  ),
                ),
              ),
            Padding(
              padding: const EdgeInsets.fromLTRB(11, 18, 11, 15),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Align(
                    child: Container(
                      width: 85,
                      height: 85,
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(20),
                        color: earned
                            ? const Color(0xfffff0b9)
                            : const Color(0xfff3f4f0),
                      ),
                      child: earned
                          ? (iconBytes == null
                                ? const Icon(
                                    Icons.workspace_premium_outlined,
                                    color: _BadgePalette.green,
                                    size: 48,
                                  )
                                : Image.memory(
                                    iconBytes!,
                                    width: 70,
                                    height: 70,
                                    filterQuality: FilterQuality.none,
                                    gaplessPlayback: true,
                                  ))
                          : const _MysteryEmblem(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    title,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      color: _BadgePalette.ink,
                      fontSize: 14,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 7),
                  Expanded(
                    child: Center(
                      child: Text(
                        description,
                        maxLines: 4,
                        overflow: TextOverflow.ellipsis,
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: _BadgePalette.muted,
                          height: 1.45,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 6),
                  Icon(
                    earned ? Icons.verified_rounded : Icons.lock_outline_rounded,
                    color: earned
                        ? _BadgePalette.green
                        : const Color(0xff9fa6a1),
                    size: 23,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _MysteryEmblem extends StatelessWidget {
  const _MysteryEmblem();

  @override
  Widget build(BuildContext context) => const SizedBox(
    width: 72,
    height: 72,
    child: CustomPaint(
      painter: _MysteryPainter(),
      child: Center(
        child: Text(
          '?',
          style: TextStyle(
            color: Color(0xff8d9690),
            fontSize: 37,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
    ),
  );
}

/// Soft pressed rosette, inspired by the first reference (not pixel-framed).
class _MysteryPainter extends CustomPainter {
  const _MysteryPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final outer = Paint()..color = _BadgePalette.mystery;
    for (var i = 0; i < 12; i++) {
      final angle = i * math.pi / 6;
      canvas.drawCircle(
        center + Offset(
          24 * math.cos(angle),
          24 * math.sin(angle),
        ),
        11,
        outer,
      );
    }
    canvas.drawCircle(center, 29, outer);
    canvas.drawCircle(
      center,
      21,
      Paint()..color = const Color(0xffeff1ed),
    );
    canvas.drawCircle(
      center,
      21,
      Paint()
        ..color = const Color(0xffc1c7c0)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.5,
    );
  }

  @override
  bool shouldRepaint(covariant _MysteryPainter oldDelegate) => false;
}

class _LeafPainter extends CustomPainter {
  const _LeafPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final stem = Paint()
      ..color = const Color(0x43649a76)
      ..strokeWidth = 2.3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    final origin = Offset(20, size.height + 10);
    final tip = Offset(110, 9);
    canvas.drawLine(origin, tip, stem);
    final leaves = <(Offset, double, double)>[
      (const Offset(30, 128), -0.9, 29),
      (const Offset(67, 106), 0.8, 31),
      (const Offset(76, 61), -0.9, 26),
      (const Offset(108, 28), 0.7, 25),
    ];
    for (final (center, angle, radius) in leaves) {
      canvas.save();
      canvas.translate(center.dx, center.dy);
      canvas.rotate(angle);
      canvas.drawOval(
        Rect.fromCenter(
          center: Offset.zero,
          width: radius,
          height: radius * 1.65,
        ),
        Paint()..color = const Color(0x24568f67),
      );
      canvas.restore();
    }
  }

  @override
  bool shouldRepaint(covariant _LeafPainter oldDelegate) => false;
}
