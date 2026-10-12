import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:level_schema/level_schema.dart';

import '../../core/pixel_art_preview.dart';
import '../painting/painting_preview_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({required this.level, super.key});

  final LevelDefinition level;

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(
      child: SingleChildScrollView(
        key: const ValueKey('home-scroll'),
        padding: const EdgeInsets.all(PixelTokens.space),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    'Pixelhub',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(fontSize: 25, fontWeight: FontWeight.w800),
                  ),
                ),
                Icon(
                  Icons.grid_view_rounded,
                  color: PixelTokens.green,
                  size: 30,
                ),
              ],
            ),
            const SizedBox(height: 32),
            const Align(
              alignment: AlignmentDirectional.centerStart,
              child: PreviewBadge(),
            ),
            const SizedBox(height: 16),
            const Text(
              'کمی مکث،\nکمی رنگ.',
              style: TextStyle(
                fontSize: 38,
                height: 1.4,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'یک دنیای کوچک، پیکسل به پیکسل.\nبه اولین پیش‌نمایش پیکسل‌هاب خوش آمدید.',
              style: TextStyle(
                color: PixelTokens.muted,
                fontSize: 15,
                height: 1.8,
              ),
            ),
            const SizedBox(height: 28),
            Container(
              decoration: BoxDecoration(
                color: PixelTokens.peach,
                borderRadius: BorderRadius.circular(PixelTokens.radius),
              ),
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.local_florist_outlined, size: 20),
                      SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'اولین تصویر ما',
                          style: TextStyle(fontWeight: FontWeight.w700),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: PixelArtPreview(level: level),
                  ),
                  const SizedBox(height: 20),
                  Text(
                    level.title,
                    style: const TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 6),
                  const Text('یک آفتابگردان کوچک برای روزهای روشن'),
                  const SizedBox(height: 20),
                  FilledButton.icon(
                    key: const ValueKey('open-preview'),
                    onPressed: () => context.go(PaintingPreviewScreen.route),
                    icon: const Icon(Icons.arrow_back_rounded),
                    label: const Text('دیدن تصویر نمونه'),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            const Row(
              children: [
                Icon(
                  Icons.wifi_off_rounded,
                  size: 18,
                  color: PixelTokens.muted,
                ),
                SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'تصویر نمونه از داخل برنامه بارگذاری می‌شود.',
                    style: TextStyle(color: PixelTokens.muted, fontSize: 12),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            const Text(
              'این نسخه فقط پیش‌نمایش است؛ رنگ‌آمیزی و ذخیرهٔ پیشرفت در نسخهٔ بعد اضافه می‌شوند.',
              style: TextStyle(
                color: PixelTokens.muted,
                fontSize: 12,
                height: 1.8,
              ),
            ),
          ],
        ),
      ),
    ),
  );
}
