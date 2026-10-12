import 'dart:async';

import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:game_domain/game_domain.dart';
import 'package:go_router/go_router.dart';
import 'package:level_schema/level_schema.dart';
import 'package:persistence/persistence.dart';

import '../features/home/home_screen.dart';
import '../features/painting/painting_controller.dart';
import '../features/painting/painting_preview_screen.dart';
import '../l10n/generated/app_localizations.dart';
import '../l10n/strings.dart';
import '../platform_adapters/document_language.dart';
import 'bootstrap_controller.dart';

class PixelhubApp extends StatefulWidget {
  const PixelhubApp({
    required this.repository,
    this.progressRepository,
    this.preferences,
    this.initialRoute,
    super.key,
  });
  final LevelRepository repository;
  final ProgressRepository? progressRepository;
  final PreferencesRepository? preferences;
  final String? initialRoute;

  @override
  State<PixelhubApp> createState() => _PixelhubAppState();
}

class _PixelhubAppState extends State<PixelhubApp> with WidgetsBindingObserver {
  late final BootstrapController _bootstrap;
  late final GoRouter _router;
  late final ProgressRepository _progress;
  late final PreferencesRepository _preferences;
  final Map<String, PaintingController> _sessions = {};
  Locale _locale = const Locale('fa');
  int _languageRevision = 0;
  Future<void> _languageWrites = Future.value();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    final local =
        widget.progressRepository == null || widget.preferences == null
        ? LocalPreferences()
        : null;
    _progress = widget.progressRepository ?? local!;
    _preferences = widget.preferences ?? local!;
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
              redirect: (context, state) => '/painting/sunflower',
            ),
            GoRoute(
              path: 'painting/:levelId',
              builder: (context, state) =>
                  _route(id: state.pathParameters['levelId']),
            ),
          ],
        ),
      ],
      errorBuilder: (context, state) => _notFound(context),
    );
    unawaited(_loadLanguage());
    unawaited(_bootstrap.load());
  }

  Future<void> _loadLanguage() async {
    try {
      final language = await _preferences.readLanguage();
      if (mounted &&
          _languageRevision == 0 &&
          (language == 'fa' || language == 'en')) {
        setState(() => _locale = Locale(language!));
        setDocumentLanguage(language!);
      }
    } on Object {
      /* New installations keep Persian; never guess from OS locale. */
    }
  }

  void _toggleLanguage() {
    final language = _locale.languageCode == 'fa' ? 'en' : 'fa';
    _languageRevision++;
    setState(() => _locale = Locale(language));
    setDocumentLanguage(language);
    _languageWrites = _languageWrites
        .then((_) => _preferences.writeLanguage(language))
        .catchError((Object _) {
          if (!mounted) return;
          final context = _router.routerDelegate.navigatorKey.currentContext;
          if (context != null && context.mounted) {
            ScaffoldMessenger.maybeOf(context)?.showSnackBar(
              SnackBar(content: Text(context.strings.languageSaveError)),
            );
          }
        });
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state != AppLifecycleState.resumed) {
      for (final controller in _sessions.values) {
        unawaited(controller.flush());
      }
    }
  }

  PaintingController _controller(LevelDefinition level) =>
      _sessions.putIfAbsent(
        '${level.id}:${level.contentVersion}',
        () => PaintingController(level, _progress)..load(),
      );

  Widget _notFound(BuildContext context) => Scaffold(
    body: SafeArea(
      child: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(context.strings.notFound),
              const SizedBox(height: 16),
              FilledButton(
                onPressed: () => context.go('/'),
                child: Text(context.strings.backHome),
              ),
            ],
          ),
        ),
      ),
    ),
  );

  Widget _route({String? id}) => ListenableBuilder(
    listenable: _bootstrap,
    builder: (context, _) {
      if (_bootstrap.status == BootstrapStatus.loading) {
        return const _SplashScreen();
      }
      if (_bootstrap.status == BootstrapStatus.error) {
        return _LoadError(onRetry: _bootstrap.load);
      }
      if (id == null) {
        return HomeScreen(
          levels: _bootstrap.levels,
          onLanguageToggle: _toggleLanguage,
        );
      }
      final matches = _bootstrap.levels.where((level) => level.id == id);
      if (matches.isEmpty) return _notFound(context);
      return PaintingPreviewScreen(
        controller: _controller(matches.first),
        onLanguageToggle: _toggleLanguage,
      );
    },
  );

  @override
  Widget build(BuildContext context) => MaterialApp.router(
    title: 'Pixelhub',
    debugShowCheckedModeBanner: false,
    theme: PixelTokens.theme,
    locale: _locale,
    supportedLocales: AppLocalizations.supportedLocales,
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    routerConfig: _router,
    builder: (context, child) => MobileFrame(child: child!),
  );

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _router.dispose();
    _bootstrap.dispose();
    for (final controller in _sessions.values) {
      controller.dispose();
    }
    super.dispose();
  }
}

class _SplashScreen extends StatelessWidget {
  const _SplashScreen();
  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(
      child: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(
                Icons.grid_view_rounded,
                size: 56,
                color: PixelTokens.green,
              ),
              const SizedBox(height: 16),
              const Text(
                'Pixelhub',
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 24),
              CircularProgressIndicator(
                semanticsLabel: context.strings.loading,
              ),
            ],
          ),
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
              Text(context.strings.loadError),
              const SizedBox(height: 24),
              FilledButton(
                onPressed: onRetry,
                child: Text(context.strings.retry),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}
