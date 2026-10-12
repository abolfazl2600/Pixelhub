import 'package:flutter/material.dart';

abstract final class PixelTokens {
  static const maxWidth = 430.0;
  static const space = 24.0;
  static const radius = 24.0;
  static const ink = Color(0xff223a31);
  static const muted = Color(0xff58675e);
  static const green = Color(0xff316349);
  static const canvas = Color(0xfff9f7f1);
  static const backdrop = Color(0xffe9e9e1);
  static const peach = Color(0xffffe7d1);
  static const lemon = Color(0xfff8edb7);

  static ThemeData get theme => ThemeData(
    useMaterial3: true,
    fontFamily: 'Vazirmatn',
    colorScheme: ColorScheme.fromSeed(
      seedColor: green,
      surface: canvas,
      onSurface: ink,
    ),
    scaffoldBackgroundColor: canvas,
    appBarTheme: const AppBarTheme(
      backgroundColor: canvas,
      foregroundColor: ink,
      centerTitle: true,
      elevation: 0,
      scrolledUnderElevation: 0,
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        minimumSize: const Size(48, 56),
        backgroundColor: green,
        foregroundColor: Colors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        textStyle: const TextStyle(
          fontFamily: 'Vazirmatn',
          fontSize: 16,
          fontWeight: FontWeight.w700,
        ),
      ),
    ),
    iconButtonTheme: IconButtonThemeData(
      style: IconButton.styleFrom(minimumSize: const Size(48, 48)),
    ),
  );
}

/// Applied outside the navigator so every route uses exactly the same frame.
class MobileFrame extends StatelessWidget {
  const MobileFrame({required this.child, super.key});

  final Widget child;

  @override
  Widget build(BuildContext context) => ColoredBox(
    color: PixelTokens.backdrop,
    child: Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: PixelTokens.maxWidth),
        child: SizedBox(
          key: const ValueKey('mobile-frame'),
          width: double.infinity,
          height: double.infinity,
          child: MediaQuery(
            data: MediaQuery.of(context).copyWith(
              size: Size(
                MediaQuery.sizeOf(context).width.clamp(0, PixelTokens.maxWidth),
                MediaQuery.sizeOf(context).height,
              ),
            ),
            child: child,
          ),
        ),
      ),
    ),
  );
}

class PreviewBadge extends StatelessWidget {
  const PreviewBadge({required this.label, super.key});
  final String label;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
    decoration: BoxDecoration(
      color: PixelTokens.lemon,
      borderRadius: BorderRadius.circular(10),
    ),
    child: Text(
      label,
      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
    ),
  );
}
