import 'dart:async';

import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:game_domain/game_domain.dart';
import 'package:go_router/go_router.dart';
import 'package:level_schema/level_schema.dart';
import 'package:persistence/persistence.dart';

import '../features/home/home_screen.dart';
import '../core/local_diagnostics.dart';
import '../features/profile/profile_screen.dart';
import '../features/gallery/artwork_screen.dart';
import '../features/gallery/gallery_screen.dart';
import '../features/gallery/library_controller.dart';
import '../features/gallery/online_catalog_controller.dart';
import '../features/import/import_screen.dart';
import '../features/settings/settings_screen.dart';
import '../features/settings/privacy_screen.dart';
import '../features/painting/painting_controller.dart';
import '../features/painting/painting_preview_screen.dart';
import '../l10n/generated/app_localizations.dart';
import '../l10n/strings.dart';
import '../platform_adapters/document_language.dart';
import '../platform_adapters/offline_support.dart';
import 'bootstrap_controller.dart';

class PixelhubApp extends StatefulWidget {
  const PixelhubApp({
    required this.repository,
    this.progressRepository,
    this.preferences,
    this.artworkRepository,
    this.initialRoute,
    this.diagnostics,
    super.key,
  });
  final LevelRepository repository;
  final ProgressRepository? progressRepository;
  final PreferencesRepository? preferences;
  final ArtworkRepository? artworkRepository;
  final String? initialRoute;
  final LocalDiagnostics? diagnostics;

  @override
  State<PixelhubApp> createState() => _PixelhubAppState();
}

class _PixelhubAppState extends State<PixelhubApp> with WidgetsBindingObserver {
  late final BootstrapController _bootstrap;
  late final GoRouter _router;
  late final ProgressRepository _progress;
  late final PreferencesRepository _preferences;
  late final LibraryController _library;
  late final OnlineCatalogController _online;
  late final LocalDiagnostics _diagnostics;
  late final Listenable _routeChanges;
  final Map<String, PaintingController> _sessions = {};
  Locale _locale = const Locale('fa');
  int _languageRevision = 0;
  Future<void> _languageWrites = Future.value();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _diagnostics = widget.diagnostics ?? LocalDiagnostics();
    final local =
        widget.progressRepository == null || widget.preferences == null
        ? LocalPreferences()
        : null;
    _progress = widget.progressRepository ?? local!;
    _preferences = widget.preferences ?? local!;
    final preferences = _preferences;
    _library = LibraryController(
      widget.artworkRepository ??
          (preferences is ArtworkRepository
              ? preferences as ArtworkRepository
              : MemoryPreferences()),
      _progress,
      recentArtworkRepository: preferences is RecentArtworkRepository
          ? preferences as RecentArtworkRepository
          : null,
    );
    _online = OnlineCatalogController(
      preferences is OnlineLevelStorage
          ? preferences as OnlineLevelStorage
          : MemoryPreferences(),
    );
    _online.addListener(() {
      if (_online.isLoaded) _library.setDownloadedOnline(_online.downloaded);
      _library.setOnlineCategories(_online.categories);
    });
    unawaited(_online.loadDownloaded());
    _bootstrap = BootstrapController(widget.repository);
    final catalogTimer = Stopwatch()..start();
    _bootstrap.addListener(() {
      if (_bootstrap.status == BootstrapStatus.ready) {
        if (catalogTimer.isRunning) {
          catalogTimer.stop();
          _diagnostics.recordCatalogLoad(catalogTimer.elapsedMilliseconds);
        }
        _library.setCatalog(_bootstrap.levels, _bootstrap.metadata);
      }
    });
    _routeChanges = Listenable.merge([_bootstrap, _library]);
    _router = GoRouter(
      initialLocation: widget.initialRoute,
      observers: [LocalNavigationObserver(_diagnostics)],
      routes: [
        GoRoute(
          path: '/',
          builder: (context, state) => _route(),
          routes: [
            GoRoute(
              path: 'gallery',
              builder: (context, state) => _route(page: 'gallery'),
            ),
            GoRoute(
              path: 'my-gallery',
              builder: (context, state) => _route(page: 'my-gallery'),
            ),
            GoRoute(
              path: 'import',
              builder: (context, state) => _route(page: 'import'),
            ),
            GoRoute(
              path: 'profile',
              builder: (context, state) => _route(page: 'profile'),
            ),
            GoRoute(
              path: 'privacy',
              builder: (context, state) => _route(page: 'privacy'),
            ),
            GoRoute(
              path: 'settings',
              builder: (context, state) => _route(page: 'settings'),
            ),
            GoRoute(
              path: 'artwork/:levelId',
              builder: (context, state) =>
                  _route(page: 'artwork', id: state.pathParameters['levelId']),
            ),
            GoRoute(
              path: 'painting',
              redirect: (context, state) => '/painting/sunflower',
            ),
            GoRoute(
              path: 'painting/:levelId',
              builder: (context, state) =>
                  _route(page: 'painting', id: state.pathParameters['levelId']),
            ),
          ],
        ),
      ],
      errorBuilder: (context, state) => _notFound(context),
    );
    unawaited(_loadLanguage());
    unawaited(_library.loadRecentArtwork());
    unawaited(_library.load());
    unawaited(_bootstrap.load());
    unawaited(prepareOfflineApp());
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
          if (!mounted) {
            return;
          }
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

  PaintingController _controller(LevelDefinition level) => _sessions
      .putIfAbsent('${level.id}:${level.contentVersion}:${level.checksum}', () {
        final controller = PaintingController(
          level,
          _progress,
          onCompleted: _diagnostics.recordCompletion,
        );
        controller.addListener(() {
          if (controller.status == PaintingStatus.ready) {
            _library.updateProgress(controller.session!.snapshot);
          }
        });
        unawaited(controller.load());
        return controller;
      });

  Future<void> _deleteArtwork(LevelDefinition level) async {
    final key = '${level.id}:${level.contentVersion}:${level.checksum}';
    final controller = _sessions[key];
    if (controller != null) {
      await controller.flush();
    }
    try {
      if (level.id.startsWith('online-')) {
        await _online.removeDownloaded(level.id);
        await _library.forgetDownloadedOnline(level);
      } else {
        await _library.delete(level);
      }
    } finally {
      if (level.id.startsWith('online-') ||
          !_library.library.artworks.any((art) => art.level.id == level.id)) {
        _sessions.remove(key)?.dispose();
      }
    }
  }

  Future<void> _clearLocalData() async {
    await _languageWrites;
    await Future.wait(_sessions.values.map((controller) => controller.flush()));
    for (final controller in _sessions.values) {
      controller.dispose();
    }
    _sessions.clear();
    try {
      await _library.clear();
      _online.clearDownloaded();
    } on Object {
      await _library.load();
      rethrow;
    }
    _languageRevision++;
    if (mounted) {
      setState(() => _locale = const Locale('fa'));
    }
    setDocumentLanguage('fa');
  }

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

  Widget _route({String? id, String page = 'home'}) => ListenableBuilder(
    listenable: _routeChanges,
    builder: (context, _) {
      // Privacy is reachable even when the picture catalog fails to load.
      if (page == 'privacy') return const PrivacyScreen();
      if (_bootstrap.status == BootstrapStatus.loading) {
        return const _SplashScreen();
      }
      if (_bootstrap.status == BootstrapStatus.error) {
        return _LoadError(onRetry: _bootstrap.load);
      }
      if (page == 'gallery' || page == 'my-gallery') {
        return GalleryScreen(
          library: _library,
          online: _online,
          personal: page == 'my-gallery',
        );
      }
      if (page == 'profile') {
        return ProfileScreen(
          library: _library,
          diagnostics: _diagnostics,
          onLanguageToggle: _toggleLanguage,
        );
      }
      if (page == 'settings') {
        return SettingsScreen(library: _library, onClear: _clearLocalData);
      }
      if (page == 'import' || (id?.startsWith('private-') ?? false)) {
        if (_library.status == LibraryStatus.loading) {
          return const _SplashScreen();
        }
        if (_library.status == LibraryStatus.error) {
          return _LoadError(
            onRetry: _library.load,
            message: context.strings.libraryLoadError,
          );
        }
      }
      if (page == 'import') {
        return ImportScreen(library: _library);
      }
      if (id == null) {
        return HomeScreen(levels: _bootstrap.levels, library: _library);
      }
      final matches = _library.levels.where((level) => level.id == id);
      if (matches.isEmpty) {
        return _notFound(context);
      }
      if (page == 'artwork') {
        return ArtworkScreen(
          level: matches.first,
          library: _library,
          onDelete: _deleteArtwork,
        );
      }
      return PaintingPreviewScreen(
        controller: _controller(matches.first),
        diagnostics: _diagnostics,
        onOpened: () => unawaited(_library.markOpened(matches.first)),
      );
    },
  );

  @override
  Widget build(BuildContext context) => MaterialApp.router(
    title: 'PixelHub',
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
    _library.dispose();
    _online.dispose();
    if (widget.diagnostics == null) _diagnostics.dispose();
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
              Image.asset(
                'assets/brand/pixelhub_mark.png',
                width: 88,
                height: 88,
                filterQuality: FilterQuality.none,
                semanticLabel: 'PixelHub',
              ),
              const SizedBox(height: 16),
              const Text(
                'PixelHub',
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
  const _LoadError({required this.onRetry, this.message});
  final VoidCallback onRetry;
  final String? message;
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
              Text(message ?? context.strings.loadError),
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
