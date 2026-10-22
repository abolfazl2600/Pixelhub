import 'dart:async';
import 'dart:convert';

import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:game_domain/game_domain.dart';
import 'package:go_router/go_router.dart';
import 'package:level_schema/level_schema.dart';
import 'package:persistence/persistence.dart';

import '../features/home/home_screen.dart';
import '../features/museum/museum_controller.dart';
import '../features/badges/badge_controller.dart';
import '../features/badges/badges_screen.dart';
import '../features/museum/museum_screen.dart';
import '../core/local_diagnostics.dart';
import '../core/game_sounds.dart';
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
import '../features/painting/artwork_render_style.dart';
import '../l10n/generated/app_localizations.dart';
import '../l10n/strings.dart';
import '../platform_adapters/document_language.dart';
import '../platform_adapters/offline_support.dart';
import 'bootstrap_controller.dart';
import '../products/product_configuration.dart';
import '../products/product_home.dart';

class _StyleChanges extends ChangeNotifier {
  void notify() => notifyListeners();
}

class PixelhubApp extends StatefulWidget {
  const PixelhubApp({
    required this.repository,
    this.progressRepository,
    this.preferences,
    this.artworkRepository,
    this.initialRoute,
    this.diagnostics,
    this.product,
    super.key,
  });
  final ProductConfiguration? product;
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
  ProductConfiguration get product => widget.product ?? selectedProduct;
  late final BootstrapController _bootstrap;
  late final GoRouter _router;
  late final ProgressRepository _progress;
  late final PreferencesRepository _preferences;
  late final LibraryController _library;
  late final MuseumController _museum;
  late final BadgeController _badges;
  late final GameSounds _sounds;
  late final OnlineCatalogController _online;
  final ValueNotifier<Map<String, PixelAnimation>> _bundledAnimations =
      ValueNotifier({});
  final _StyleChanges _styleChanges = _StyleChanges();
  final Map<String, String> _bundledAnimationFiles = {};
  final Set<String> _requestedAnimations = {};
  bool _animationCatalogRequested = false;
  late final LocalDiagnostics _diagnostics;
  late final Listenable _routeChanges;
  final Map<String, PaintingController> _sessions = {};
  Locale _locale = const Locale('fa');
  ArtworkRenderStyle _renderStyle = ArtworkRenderStyle.pixel;
  int _languageRevision = 0;
  Future<void> _languageWrites = Future.value();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _diagnostics = widget.diagnostics ?? LocalDiagnostics();
    final local =
        widget.progressRepository == null || widget.preferences == null
        ? LocalPreferences(scope: product.storageScope)
        : null;
    _progress = widget.progressRepository ?? local!;
    _preferences = widget.preferences ?? local!;
    final preferences = _preferences;
    _renderStyle = ArtworkRenderStyle.fromStorage(product.defaultStyle);
    _sounds = GameSounds(
      available: product.features.soundEffects,
      preferences: preferences is SoundEffectsPreferences
          ? preferences as SoundEffectsPreferences
          : null,
    );
    unawaited(_sounds.initialize());
    _library = LibraryController(
      widget.artworkRepository ??
          (preferences is ArtworkRepository
              ? preferences as ArtworkRepository
              : MemoryPreferences()),
      _progress,
      sounds: _sounds,
      coinsEnabled: product.features.coins,
      recentArtworkRepository: preferences is RecentArtworkRepository
          ? preferences as RecentArtworkRepository
          : null,
    );
    _museum = MuseumController(
      preferences is MuseumRepository
          ? preferences as MuseumRepository
          : MemoryPreferences(),
      _library,
    );
    _badges = BadgeController(
      _library,
      preferences is BadgeStorage
          ? preferences as BadgeStorage
          : MemoryPreferences(),
    );
    if (product.features.achievements) unawaited(_badges.initialize());
    _online = OnlineCatalogController(
      preferences is OnlineLevelStorage
          ? preferences as OnlineLevelStorage
          : MemoryPreferences(),
      enabled: product.features.onlineCatalog,
      animationsEnabled: product.features.animations,
      allowedCategories: product.categories,
      maxDimension: product.maxDimension,
      baseUrl: Uri.parse(product.onlineRoot),
      catalogPath: product.onlineManifest,
      productId: product.id,
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
        if (product.features.animations && !_animationCatalogRequested) {
          _animationCatalogRequested = true;
          unawaited(_loadAnimationCatalog());
        }
      }
    });
    _routeChanges = Listenable.merge([
      _bootstrap,
      _library,
      _museum,
      _badges,
      _online,
      _bundledAnimations,
      _styleChanges,
    ]);
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
              path: 'museum',
              builder: (context, state) => _route(
                page: 'museum',
                museumArtworkId: state.uri.queryParameters['artwork'],
              ),
            ),
            GoRoute(
              path: 'profile',
              builder: (context, state) => _route(page: 'profile'),
            ),
            GoRoute(
              path: 'badges',
              builder: (context, state) => _route(page: 'badges'),
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
    unawaited(_loadArtworkStyle());
    unawaited(_library.loadRecentArtwork());
    unawaited(_library.load());
    unawaited(_museum.load());
    unawaited(_bootstrap.load());
    unawaited(prepareOfflineApp());
  }

  Future<void> _loadAnimationCatalog() async {
    try {
      final raw = await rootBundle.loadString('assets/animations/catalog.json');
      final catalog = jsonDecode(raw) as Map<String, dynamic>;
      for (final entry in catalog.entries) {
        final file = entry.value;
        if (file is String && RegExp(r'^[a-z0-9-]+\.json$').hasMatch(file)) {
          _bundledAnimationFiles[entry.key] = file;
        }
      }
      if (mounted) _bundledAnimations.value = {};
    } on Object {
      // Optional effects never prevent the still catalog from loading.
    }
  }

  Future<void> _loadBundledAnimation(LevelDefinition level, String file) async {
    try {
      final raw = await rootBundle.loadString('assets/animations/$file');
      final animation = PixelAnimation.fromJson(
        jsonDecode(raw) as Map<String, Object?>,
        level,
      );
      if (mounted) {
        _bundledAnimations.value = {
          ..._bundledAnimations.value,
          level.id: animation,
        };
      }
    } on Object {
      // Missing or incompatible frames leave the painting playable.
    }
  }

  PixelAnimation? _animationFor(LevelDefinition level) {
    if (!product.features.animations) return null;
    final online = _online.animations[level.id];
    if (online != null) return online;
    final bundled = _bundledAnimations.value[level.id];
    if (bundled != null) return bundled;
    final file = _bundledAnimationFiles[level.id];
    if (file != null && _requestedAnimations.add(level.id)) {
      unawaited(_loadBundledAnimation(level, file));
    }
    return null;
  }

  Future<void> _loadArtworkStyle() async {
    final preferences = _preferences;
    if (preferences is! ArtworkStylePreferences) return;
    final stylePreferences = preferences as ArtworkStylePreferences;
    try {
      final saved = await stylePreferences.readArtworkStyle();
      if (mounted && saved != null) {
        final style = ArtworkRenderStyle.fromStorage(saved);
        if (product.allowsStyle(style.storageId) && _renderStyle != style) {
          setState(() => _renderStyle = style);
          _styleChanges.notify();
        }
      }
    } on Object {
      // Missing/corrupt optional preferences safely keep the Pixel default.
    }
  }

  Future<void> _setArtworkStyle(ArtworkRenderStyle style) async {
    if (!product.allowsStyle(style.storageId) || _renderStyle == style) return;
    setState(() => _renderStyle = style);
    // The active route is rebuilt by _routeChanges, not by this State's
    // setState alone. Notify it so PaintingPreviewScreen and PaintingBoard
    // receive the new render style immediately.
    _styleChanges.notify();
    final preferences = _preferences;
    if (preferences is! ArtworkStylePreferences) return;
    final stylePreferences = preferences as ArtworkStylePreferences;
    try {
      await stylePreferences.writeArtworkStyle(style.storageId);
    } on Object {
      if (!mounted) return;
      final routeContext = _router.routerDelegate.navigatorKey.currentContext;
      if (routeContext != null && routeContext.mounted) {
        ScaffoldMessenger.maybeOf(routeContext)?.showSnackBar(
          SnackBar(
            content: Text(
              _locale.languageCode == 'fa'
                  ? 'ذخیرهٔ سبک نمایش انجام نشد؛ انتخاب فعلی تا بسته‌شدن برنامه فعال می‌ماند.'
                  : 'Could not save the style; the current choice lasts until the app closes.',
            ),
          ),
        );
      }
    }
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
          onCompleted: () {
            _diagnostics.recordCompletion();
            unawaited(_sounds.play(SoundCue.paintingCompleted));
          },
        );
        controller.addListener(() {
          if (controller.status == PaintingStatus.ready) {
            _library.updateProgress(controller.session!.snapshot);
            // Grant only after the final painting snapshot was persisted.
            // Wallet ledger is durable and idempotent across resets/restarts.
            if (controller.session!.isComplete &&
                controller.saveStatus == SaveStatus.saved) {
              unawaited(
                _library.rewardCompletion(level).catchError((Object _) {}),
              );
            }
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
    await _museum.settle();
    await _badges.settle();
    await Future.wait(_sessions.values.map((controller) => controller.flush()));
    for (final controller in _sessions.values) {
      controller.dispose();
    }
    _sessions.clear();
    try {
      await _library.clear();
      _museum.resetAfterClear();
      _badges.resetAfterClear();
      unawaited(_badges.refresh());
      await _sounds.setEnabled(true);
      _online.clearDownloaded();
    } on Object {
      await _library.load();
      rethrow;
    }
    _languageRevision++;
    final preferences = _preferences;
    if (preferences is ArtworkStylePreferences) {
      final stylePreferences = preferences as ArtworkStylePreferences;
      try {
        await stylePreferences.writeArtworkStyle(product.defaultStyle);
      } on Object {
        // Clear still succeeds if this optional preference cannot be reset.
      }
    }
    if (mounted) {
      setState(() {
        _locale = const Locale('fa');
        _renderStyle = ArtworkRenderStyle.fromStorage(product.defaultStyle);
      });
      _styleChanges.notify();
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

  Widget _route({String? id, String? museumArtworkId, String page = 'home'}) =>
      ListenableBuilder(
        listenable: _routeChanges,
        builder: (context, _) {
          if (!product.allowsPage(page) ||
              (!product.features.imageImport &&
                  (id?.startsWith('private-') ?? false))) {
            return _notFound(context);
          }
          // Privacy is reachable even when the picture catalog fails to load.
          if (page == 'privacy') return const PrivacyScreen();
          if (_bootstrap.status == BootstrapStatus.loading) {
            return _SplashScreen(product: product);
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
          if (page == 'museum') {
            return MuseumScreen(
              museum: _museum,
              library: _library,
              animationFor: _animationFor,
              addArtworkId: museumArtworkId,
            );
          }
          if (page == 'badges') {
            return BadgesScreen(badges: _badges);
          }
          if (page == 'profile') {
            return ProfileScreen(
              library: _library,
              diagnostics: _diagnostics,
              badges: _badges,
              onLanguageToggle: _toggleLanguage,
            );
          }
          if (page == 'settings') {
            return SettingsScreen(
              library: _library,
              sounds: product.features.soundEffects ? _sounds : null,
              onClear: _clearLocalData,
            );
          }
          if (page == 'import' || (id?.startsWith('private-') ?? false)) {
            if (_library.status == LibraryStatus.loading) {
              return _SplashScreen(product: product);
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
            if (product.homeLayout != 'classic') {
              return ProductHome(
                product: product,
                levels: _bootstrap.levels,
                library: _library,
                onLanguageToggle: _toggleLanguage,
              );
            }
            return HomeScreen(levels: _bootstrap.levels, library: _library);
          }
          final matches = _library.levels.where((level) => level.id == id);
          if (matches.isEmpty) {
            return _notFound(context);
          }
          if (page == 'artwork' ||
              (page == 'painting' && !_library.canPaint(matches.first))) {
            return ArtworkScreen(
              level: matches.first,
              library: _library,
              animation: _animationFor(matches.first),
              renderStyle: _renderStyle,
              onDelete: _deleteArtwork,
            );
          }
          return PaintingPreviewScreen(
            controller: _controller(matches.first),
            library: _library,
            animation: _animationFor(matches.first),
            diagnostics: _diagnostics,
            renderStyle: _renderStyle,
            onRenderStyleChanged: (style) => unawaited(_setArtworkStyle(style)),
            onOpened: () => unawaited(_library.markOpened(matches.first)),
          );
        },
      );

  @override
  Widget build(BuildContext context) => MaterialApp.router(
    title: product.name,
    debugShowCheckedModeBanner: false,
    theme: _productTheme(Brightness.light),
    darkTheme: _productTheme(Brightness.dark),
    themeMode: product.themeMode,
    locale: _locale,
    supportedLocales: AppLocalizations.supportedLocales,
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    routerConfig: _router,
    builder: (context, child) => ProductScope(
      product: product,
      child: MobileFrame(child: child!),
    ),
  );

  ThemeData _productTheme(Brightness brightness) {
    if (product.id == 'kids') {
      return _kidsTheme(brightness);
    }
    if (product.id == 'pixelhub' && brightness == Brightness.light) {
      return PixelTokens.theme;
    }
    final colors = ColorScheme.fromSeed(
      seedColor: product.primary,
      secondary: product.secondary,
      surface: brightness == Brightness.light ? product.background : null,
      brightness: brightness,
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: colors,
      fontFamily: product.fontFamily,
      scaffoldBackgroundColor: colors.surface,
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: Size(64, product.largeControls ? 68 : 56),
          textStyle: TextStyle(
            fontFamily: product.fontFamily,
            fontSize: product.largeControls ? 20 : 16,
          ),
        ),
      ),
      iconButtonTheme: IconButtonThemeData(
        style: IconButton.styleFrom(
          minimumSize: Size.square(product.largeControls ? 60 : 48),
        ),
      ),
    );
  }

  /// Kids has its own playful surfaces and touch targets, without changing
  /// the existing PixelHub or Art themes.
  ThemeData _kidsTheme(Brightness brightness) {
    final colors = ColorScheme.fromSeed(
      seedColor: product.primary,
      primary: product.primary,
      secondary: product.secondary,
      tertiary: const Color(0xff35bba5),
      surface: brightness == Brightness.light ? product.background : null,
      brightness: brightness,
    );
    const largeRadius = 24.0;
    return ThemeData(
      useMaterial3: true,
      colorScheme: colors,
      fontFamily: product.fontFamily,
      scaffoldBackgroundColor: colors.surface,
      appBarTheme: AppBarTheme(
        backgroundColor: colors.surface,
        foregroundColor: colors.onSurface,
        centerTitle: true,
        elevation: 0,
        scrolledUnderElevation: 0,
      ),
      cardTheme: CardThemeData(
        color: colors.surfaceContainerLowest,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(largeRadius),
          side: BorderSide(color: colors.outlineVariant),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: colors.primary,
          foregroundColor: colors.onPrimary,
          minimumSize: const Size(64, 68),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          textStyle: TextStyle(
            fontFamily: product.fontFamily,
            fontSize: 19,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: colors.primary,
          minimumSize: const Size(60, 56),
          side: BorderSide(color: colors.outlineVariant),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(18),
          ),
          textStyle: TextStyle(
            fontFamily: product.fontFamily,
            fontSize: 16,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
      iconButtonTheme: IconButtonThemeData(
        style: IconButton.styleFrom(
          foregroundColor: colors.primary,
          minimumSize: const Size.square(60),
        ),
      ),
      progressIndicatorTheme: ProgressIndicatorThemeData(
        color: colors.tertiary,
        linearTrackColor: colors.tertiaryContainer,
      ),
    );
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _router.dispose();
    _styleChanges.dispose();
    _bootstrap.dispose();
    _library.dispose();
    _museum.dispose();
    _badges.dispose();
    _sounds.dispose();
    _online.dispose();
    _bundledAnimations.dispose();
    if (widget.diagnostics == null) _diagnostics.dispose();
    for (final controller in _sessions.values) {
      controller.dispose();
    }
    super.dispose();
  }
}

class _SplashScreen extends StatelessWidget {
  const _SplashScreen({required this.product});
  final ProductConfiguration product;
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
                product.icon,
                width: 88,
                height: 88,
                filterQuality: FilterQuality.none,
                semanticLabel: product.name,
              ),
              const SizedBox(height: 16),
              Text(
                product.name,
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
