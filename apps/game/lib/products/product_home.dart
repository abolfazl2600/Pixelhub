import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:level_schema/level_schema.dart';

import '../core/pixel_art_preview.dart';
import '../features/gallery/library_controller.dart';
import '../l10n/strings.dart';
import 'product_configuration.dart';

/// Product-specific composition; every card opens the same painting engine.
class ProductHome extends StatefulWidget {
  const ProductHome({
    required this.product,
    required this.levels,
    required this.library,
    required this.onLanguageToggle,
    super.key,
  });
  final ProductConfiguration product;
  final List<LevelDefinition> levels;
  final LibraryController library;
  final VoidCallback onLanguageToggle;

  @override
  State<ProductHome> createState() => _ProductHomeState();
}

class _ProductHomeState extends State<ProductHome> {
  String _kidsCategory = 'all';

  static String _categoryLabel(String id, bool persian) => switch (id) {
    'all' => persian ? 'همه' : 'All',
    'animals' => persian ? 'جانوران' : 'Animals',
    'nature' => persian ? 'طبیعت' : 'Nature',
    'objects' => persian ? 'اشیا' : 'Objects',
    'space' => persian ? 'فضا' : 'Space',
    'patterns' => persian ? 'الگوها' : 'Patterns',
    _ => id,
  };

  static IconData _categoryIcon(String id) => switch (id) {
    'animals' => Icons.pets_rounded,
    'nature' => Icons.local_florist_rounded,
    'objects' => Icons.toys_rounded,
    'space' => Icons.rocket_launch_rounded,
    'patterns' => Icons.auto_awesome_rounded,
    _ => Icons.apps_rounded,
  };

  Widget _kidsCategoryChips(BuildContext context) {
    final persian = context.isPersian;
    final categories = ['all', ...widget.product.defaultCategories];
    return Semantics(
      label: persian ? 'دسته‌بندی نقاشی‌ها' : 'Painting categories',
      child: Wrap(
        key: const ValueKey('kids-category-filters'),
        spacing: 8,
        runSpacing: 8,
        children: [
          for (final category in categories)
            ChoiceChip(
              key: ValueKey('kids-category-$category'),
              avatar: Icon(_categoryIcon(category), size: 18),
              label: Text(_categoryLabel(category, persian)),
              selected: _kidsCategory == category,
              onSelected: (_) => setState(() => _kidsCategory = category),
            ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final product = widget.product;
    final levels = widget.levels;
    final library = widget.library;
    final onLanguageToggle = widget.onLanguageToggle;
    final kids = product.homeLayout == 'kids';
    final visibleLevels = kids && _kidsCategory != 'all'
        ? levels
              .where((level) => library.category(level) == _kidsCategory)
              .toList()
        : levels;
    final fa = context.isPersian;
    final viewportWidth = MediaQuery.sizeOf(context).width;
    final horizontalPadding = kids
        ? math.max(16.0, (viewportWidth - 1000) / 2)
        : 20.0;
    final header = <Widget>[
      Container(
        padding: kids ? const EdgeInsets.all(16) : EdgeInsets.zero,
        decoration: kids
            ? BoxDecoration(
                borderRadius: BorderRadius.circular(28),
                gradient: LinearGradient(
                  colors: [
                    Theme.of(context).colorScheme.primaryContainer,
                    Theme.of(context).colorScheme.tertiaryContainer,
                  ],
                ),
              )
            : null,
        child: Row(
          children: [
            Image.asset(product.icon, width: 64, height: 64),
            const SizedBox(width: 16),
            Expanded(
              child: Text(
                kids
                    ? (fa ? 'با رنگ‌ها بازی کن!' : 'Play with colors!')
                    : (fa ? 'کارگاه آثار کلاسیک' : 'The classic art studio'),
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  color: kids
                      ? Theme.of(context).colorScheme.onPrimaryContainer
                      : null,
                  fontWeight: kids ? FontWeight.w800 : null,
                ),
              ),
            ),
          ],
        ),
      ),
      const SizedBox(height: 20),
      if (kids)
        Card(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              children: [
                _guide(
                  Icons.palette_outlined,
                  fa ? '۱. یک رنگ انتخاب کن' : '1. Choose a color',
                ),
                const SizedBox(height: 12),
                _guide(
                  Icons.touch_app_outlined,
                  fa
                      ? '۲. خانه‌های همان شماره را لمس کن'
                      : '2. Tap cells with the matching number',
                ),
                const SizedBox(height: 12),
                _guide(
                  Icons.celebration_outlined,
                  fa ? '۳. نقاشی‌ات را کامل کن!' : '3. Complete your picture!',
                ),
              ],
            ),
          ),
        )
      else
        Text(
          fa
              ? 'بازآفرینی‌های پیکسلی از نقاشی‌های مشهور. اثر را بشناس، بافت دلخواهت را انتخاب کن و گالری خودت را بچین.'
              : 'Pixel interpretations of famous paintings. Discover each work, choose a texture and arrange your own gallery.',
          style: const TextStyle(height: 1.8),
        ),
      const SizedBox(height: 16),
      if (kids)
        _kidsNavigation(context)
      else
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final page in product.navigation)
              if (product.allowsPage(page) && page != 'settings')
                OutlinedButton.icon(
                  onPressed: () => context.push('/$page'),
                  icon: Icon(_icon(page)),
                  label: Text(_label(context, page)),
                ),
          ],
        ),
      if (kids) ...[
        const SizedBox(height: 16),
        _kidsCategoryChips(context),
        const SizedBox(height: 8),
        Text(
          _kidsCategory == 'all'
              ? (fa ? 'نقاشی‌های من' : 'My paintings')
              : _categoryLabel(_kidsCategory, fa),
          style: Theme.of(context).textTheme.titleLarge,
        ),
      ],
      const SizedBox(height: 20),
    ];
    return Scaffold(
      appBar: AppBar(
        title: Text(fa ? product.displayNameFa : product.name),
        actions: [
          IconButton(
            onPressed: onLanguageToggle,
            tooltip: fa ? 'English' : 'فارسی',
            style: kids
                ? IconButton.styleFrom(
                    minimumSize: const Size.square(48),
                    padding: EdgeInsets.zero,
                  )
                : null,
            icon: const Icon(Icons.language),
          ),
          IconButton(
            onPressed: () => context.push('/settings'),
            tooltip: context.strings.settings,
            style: kids
                ? IconButton.styleFrom(
                    minimumSize: const Size.square(48),
                    padding: EdgeInsets.zero,
                  )
                : null,
            icon: const Icon(Icons.settings_outlined),
          ),
        ],
      ),
      body: SafeArea(
        child: kids
            ? CustomScrollView(
                slivers: [
                  SliverPadding(
                    padding: EdgeInsets.fromLTRB(
                      horizontalPadding,
                      20,
                      horizontalPadding,
                      0,
                    ),
                    sliver: SliverList(
                      delegate: SliverChildListDelegate(header),
                    ),
                  ),
                  SliverPadding(
                    padding: EdgeInsets.fromLTRB(
                      horizontalPadding,
                      0,
                      horizontalPadding,
                      20,
                    ),
                    sliver: SliverLayoutBuilder(
                      builder: (context, constraints) {
                        final textScale =
                            MediaQuery.textScalerOf(context).scale(18) / 18;
                        final width = constraints.crossAxisExtent;
                        var columns = 4;
                        if (width < 340 || (textScale >= 1.4 && width < 600)) {
                          columns = 1;
                        } else if (width < 680) {
                          columns = 2;
                        } else if (width < 970) {
                          columns = 3;
                        }
                        return SliverGrid.builder(
                          gridDelegate:
                              SliverGridDelegateWithFixedCrossAxisCount(
                                crossAxisCount: columns,
                                mainAxisExtent:
                                    268.0 +
                                    math.max(0.0, textScale - 1.0) * 64.0,
                                crossAxisSpacing: 12,
                                mainAxisSpacing: 12,
                              ),
                          itemCount: visibleLevels.length,
                          itemBuilder: (context, index) =>
                              _card(context, visibleLevels[index], true),
                        );
                      },
                    ),
                  ),
                ],
              )
            : ListView(
                padding: const EdgeInsets.all(20),
                children: [
                  ...header,
                  for (final level in levels) _card(context, level, false),
                ],
              ),
      ),
    );
  }

  /// Compact navigation chips wrap naturally without occupying full-width rows.
  Widget _kidsNavigation(BuildContext context) {
    final product = widget.product;
    final scheme = Theme.of(context).colorScheme;
    return Wrap(
      spacing: 10,
      runSpacing: 8,
      children: [
        for (final page in product.navigation)
          if (product.allowsPage(page) && page != 'settings')
            OutlinedButton.icon(
              onPressed: () => context.push('/$page'),
              style: OutlinedButton.styleFrom(
                backgroundColor: page == 'gallery'
                    ? scheme.primaryContainer
                    : scheme.secondaryContainer,
                foregroundColor: page == 'gallery'
                    ? scheme.onPrimaryContainer
                    : scheme.onSecondaryContainer,
                minimumSize: const Size(0, 48),
                padding: const EdgeInsets.symmetric(horizontal: 12),
              ),
              icon: Icon(_icon(page), size: 20),
              label: Text(_label(context, page)),
            ),
      ],
    );
  }

  Widget _guide(IconData icon, String text) => Builder(
    builder: (context) => Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.tertiaryContainer,
            borderRadius: BorderRadius.circular(14),
          ),
          child: Icon(
            icon,
            size: 30,
            color: Theme.of(context).colorScheme.onTertiaryContainer,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(child: Text(text, style: const TextStyle(fontSize: 18))),
      ],
    ),
  );

  Widget _card(BuildContext context, LevelDefinition level, bool kids) {
    final fa = context.isPersian;
    final actionLabel = widget.library.completed(level) > 0
        ? context.strings.continuePainting
        : context.strings.startPainting;
    return Card(
      color: kids ? Theme.of(context).colorScheme.surfaceContainerLow : null,
      margin: EdgeInsets.only(bottom: kids ? 0 : 20),
      child: Padding(
        padding: EdgeInsets.all(kids ? 12 : 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (kids)
              Expanded(
                child: Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(
                      maxWidth: 176,
                      maxHeight: 176,
                    ),
                    child: AspectRatio(
                      aspectRatio: level.width / level.height,
                      child: PixelArtPreview(level: level),
                    ),
                  ),
                ),
              )
            else
              AspectRatio(
                aspectRatio: 1.4,
                child: PixelArtPreview(level: level),
              ),
            SizedBox(height: kids ? 6 : 8),
            Text(
              level.titleFor(fa ? 'fa' : 'en'),
              maxLines: kids ? 2 : null,
              overflow: kids ? TextOverflow.ellipsis : null,
              style: TextStyle(
                fontSize: kids ? 18 : 22,
                fontWeight: FontWeight.w700,
              ),
            ),
            if (!kids) ...[
              const SizedBox(height: 8),
              Text(
                artworkContext(level.id, fa),
                style: const TextStyle(height: 1.7),
              ),
              Text(
                '${level.width} × ${level.height}',
                textDirection: TextDirection.ltr,
              ),
              const SizedBox(height: 12),
            ],
            if (kids)
              FilledButton(
                key: ValueKey('product-paint-${level.id}'),
                onPressed: () => context.go('/painting/${level.id}'),
                style: FilledButton.styleFrom(
                  minimumSize: const Size(0, 48),
                  padding: const EdgeInsets.symmetric(horizontal: 8),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
                child: Text(
                  fa ? 'نقاشی کن' : 'Paint',
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontSize: 15),
                ),
              )
            else
              FilledButton.icon(
                key: ValueKey('product-paint-${level.id}'),
                onPressed: () => context.go('/painting/${level.id}'),
                icon: const Icon(Icons.brush_rounded),
                label: Text(actionLabel),
              ),
          ],
        ),
      ),
    );
  }

  static IconData _icon(String page) => switch (page) {
    'museum' => Icons.museum_outlined,
    'profile' => Icons.person_outline,
    'my-gallery' => Icons.collections_outlined,
    'badges' => Icons.workspace_premium_outlined,
    'import' => Icons.add_photo_alternate_outlined,
    _ => Icons.grid_view_rounded,
  };
  static String _label(BuildContext context, String page) => switch (page) {
    'museum' => context.strings.museumTitle,
    'profile' => context.strings.profile,
    'my-gallery' => context.strings.myGallery,
    'badges' => context.isPersian ? 'نشان‌ها' : 'Badges',
    'import' => context.strings.importPhoto,
    _ => context.strings.gallery,
  };
}

String artworkContext(String id, bool fa) => switch (id) {
  'offline-mona-lisa' =>
    fa
        ? 'مونالیزا · لئوناردو داوینچی. به سایه‌ها و حالت آرام چهره دقت کن.'
        : 'Mona Lisa · Leonardo da Vinci. Explore the soft shadows and calm expression.',
  'offline-starry-night' =>
    fa
        ? 'شب پرستاره · ونسان ون گوگ. گردش آسمان و تضاد آبی و زرد را دنبال کن.'
        : 'The Starry Night · Vincent van Gogh. Follow the swirling sky and blue-yellow contrast.',
  'offline-great-wave' =>
    fa
        ? 'موج بزرگ · کاتسوشیکا هوکوسای. ریتم موج و فضای منفی را کشف کن.'
        : 'The Great Wave · Katsushika Hokusai. Discover the rhythm of the wave and negative space.',
  'offline-girl-pearl' =>
    fa
        ? 'دختری با گوشواره مروارید · یوهانس ورمیر. نور روی چهره و مروارید را ببین.'
        : 'Girl with a Pearl Earring · Johannes Vermeer. Notice the light on the face and pearl.',
  _ =>
    fa
        ? 'بازآفرینی پیکسلی؛ رنگ‌ها و جزئیات ممکن است با اثر اصلی متفاوت باشند.'
        : 'A pixel interpretation; colors and details may differ from the original.',
};
