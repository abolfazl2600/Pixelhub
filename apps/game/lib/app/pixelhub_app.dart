import 'dart:async';

import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:game_domain/game_domain.dart';
import 'package:go_router/go_router.dart';

import '../features/home/home_screen.dart';
import '../features/painting/painting_preview_screen.dart';
import 'bootstrap_controller.dart';

class PixelhubApp extends StatefulWidget {
  const PixelhubApp({required this.repository, this.initialRoute, super.key});

  final LevelRepository repository;
  final String? initialRoute;

  @override
  State<PixelhubApp> createState() => _PixelhubAppState();
}

class _PixelhubAppState extends State<PixelhubApp> {
  late final BootstrapController _bootstrap;
  late final GoRouter _router;

  @override
  void initState() {
    super.initState();
    _bootstrap = BootstrapController(widget.repository);
    _router = GoRouter(
      initialLocation: widget.initialRoute,
      routes: [
        GoRoute(
          path: '/',
          builder: (context, state) => _route(),
          routes: [
            GoRoute(
              path: 'painting',
              builder: (context, state) => _route(painting: true),
            ),
          ],
        ),
      ],
      errorBuilder: (context, state) => Scaffold(
        body: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('این صفحه پیدا نشد.'),
                  const SizedBox(height: 16),
                  FilledButton(
                    onPressed: () => context.go('/'),
                    child: const Text('بازگشت به خانه'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
    unawaited(_bootstrap.load());
  }

  @override
  void dispose() {
    _router.dispose();
    _bootstrap.dispose();
    super.dispose();
  }

  Widget _route({bool painting = false}) => ListenableBuilder(
    listenable: _bootstrap,
    builder: (context, _) => switch (_bootstrap.status) {
      BootstrapStatus.loading => const _SplashScreen(),
      BootstrapStatus.error => _LoadError(onRetry: _bootstrap.load),
      BootstrapStatus.ready =>
        painting
            ? PaintingPreviewScreen(level: _bootstrap.level!)
            : HomeScreen(level: _bootstrap.level!),
    },
  );

  @override
  Widget build(BuildContext context) => MaterialApp.router(
    title: 'Pixelhub',
    debugShowCheckedModeBanner: false,
    theme: PixelTokens.theme,
    locale: const Locale('fa'),
    supportedLocales: const [Locale('fa')],
    localizationsDelegates: GlobalMaterialLocalizations.delegates,
    routerConfig: _router,
    builder: (context, child) => MobileFrame(child: child!),
  );
}

class _SplashScreen extends StatelessWidget {
  const _SplashScreen();

  @override
  Widget build(BuildContext context) => const Scaffold(
    body: SafeArea(
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.grid_view_rounded, size: 56, color: PixelTokens.green),
            SizedBox(height: 16),
            Text(
              'Pixelhub',
              style: TextStyle(fontSize: 28, fontWeight: FontWeight.w800),
            ),
            SizedBox(height: 24),
            CircularProgressIndicator(semanticsLabel: 'بارگذاری تصویر نمونه'),
          ],
        ),
      ),
    ),
  );
}

class _LoadError extends StatelessWidget {
  const _LoadError({required this.onRetry});

  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(
      child: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.broken_image_outlined, size: 48),
              const SizedBox(height: 20),
              const Text('تصویر نمونه بارگذاری نشد.'),
              const SizedBox(height: 8),
              const Text(
                'دوباره تلاش کنید.',
                style: TextStyle(color: PixelTokens.muted),
              ),
              const SizedBox(height: 24),
              FilledButton(
                onPressed: onRetry,
                child: const Text('تلاش دوباره'),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}
