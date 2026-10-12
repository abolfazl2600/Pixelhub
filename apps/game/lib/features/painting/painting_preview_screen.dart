import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:level_schema/level_schema.dart';

import '../../core/pixel_art_preview.dart';

class PaintingPreviewScreen extends StatelessWidget {
  const PaintingPreviewScreen({required this.level, super.key});

  static const route = '/painting';
  final LevelDefinition level;

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      leading: IconButton(
        tooltip: 'بازگشت به خانه',
        icon: const Icon(Icons.arrow_forward_rounded),
        onPressed: () {
          if (context.canPop()) {
            context.pop();
          } else {
            context.go('/');
          }
        },
      ),
      title: Text(
        level.title,
        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
      ),
    ),
    body: SafeArea(
      top: false,
      child: SingleChildScrollView(
        key: const ValueKey('painting-scroll'),
        padding: const EdgeInsets.all(PixelTokens.space),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Align(alignment: Alignment.center, child: PreviewBadge()),
            const SizedBox(height: 24),
            ClipRRect(
              borderRadius: BorderRadius.circular(PixelTokens.radius),
              child: PixelArtPreview(level: level),
            ),
            const SizedBox(height: 24),
            const Text(
              'رنگ‌های این تصویر',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                for (var i = 0; i < level.palette.length; i++)
                  Semantics(
                    label: 'رنگ ${i + 1}، فقط برای نمایش',
                    child: Container(
                      width: 48,
                      height: 48,
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        color: Color(level.palette[i]),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(
                          color: PixelTokens.ink.withValues(alpha: 0.15),
                        ),
                      ),
                      child: Text(
                        '${i + 1}',
                        style: TextStyle(
                          fontWeight: FontWeight.w800,
                          color:
                              ThemeData.estimateBrightnessForColor(
                                    Color(level.palette[i]),
                                  ) ==
                                  Brightness.dark
                              ? Colors.white
                              : PixelTokens.ink,
                        ),
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 28),
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: PixelTokens.lemon,
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'به‌زودی، نوبت رنگ کردن است',
                    style: TextStyle(fontWeight: FontWeight.w800),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'در نسخهٔ ۲ می‌توانید پیکسل‌ها را رنگ کنید. فعلاً این تصویر و پالت فقط برای نمایش هستند.',
                    style: TextStyle(height: 1.8),
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
