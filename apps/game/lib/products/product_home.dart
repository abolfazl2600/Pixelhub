import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:level_schema/level_schema.dart';

import '../core/pixel_art_preview.dart';
import '../features/gallery/library_controller.dart';
import '../l10n/strings.dart';
import 'product_configuration.dart';

/// Product-specific composition; every card opens the same painting engine.
class ProductHome extends StatelessWidget {
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
  Widget build(BuildContext context) {
    final kids = product.homeLayout == 'kids';
    final fa = context.isPersian;
    return Scaffold(
      appBar: AppBar(
        title: Text(fa ? product.displayNameFa : product.name),
        actions: [
          IconButton(
            onPressed: onLanguageToggle,
            tooltip: fa ? 'English' : 'فارسی',
            icon: const Icon(Icons.language),
          ),
          IconButton(
            onPressed: () => context.push('/settings'),
            tooltip: context.strings.settings,
            icon: const Icon(Icons.settings_outlined),
          ),
        ],
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
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
                        : (fa
                              ? 'کارگاه آثار کلاسیک'
                              : 'The classic art studio'),
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      color: kids
                          ? Theme.of(context).colorScheme.onPrimaryContainer
                          : null,
                      fontWeight: kids ? FontWeight.w800 : null,
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
                        fa
                            ? '۳. نقاشی‌ات را کامل کن!'
                            : '3. Complete your picture!',
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
            const SizedBox(height: 20),
            if (kids)
              LayoutBuilder(
                builder: (context, constraints) {
                  final columns = constraints.maxWidth >= 380 ? 2 : 1;
                  return GridView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: columns,
                      mainAxisExtent: 280,
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                    ),
                    itemCount: levels.length,
                    itemBuilder: (context, index) =>
                        _card(context, levels[index], true),
                  );
                },
              )
            else
              for (final level in levels) _card(context, level, false),
          ],
        ),
      ),
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
    return Card(
      color: kids ? Theme.of(context).colorScheme.surfaceContainerLow : null,
      margin: EdgeInsets.only(bottom: kids ? 0 : 20),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (kids)
              Expanded(child: PixelArtPreview(level: level))
            else
              AspectRatio(
                aspectRatio: 1.4,
                child: PixelArtPreview(level: level),
              ),
            const SizedBox(height: 8),
            Text(
              level.titleFor(fa ? 'fa' : 'en'),
              style: TextStyle(
                fontSize: kids ? 20 : 22,
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
            FilledButton.icon(
              key: ValueKey('product-paint-${level.id}'),
              onPressed: () => context.go('/painting/${level.id}'),
              icon: const Icon(Icons.brush_rounded),
              label: Text(
                library.completed(level) > 0
                    ? context.strings.continuePainting
                    : context.strings.startPainting,
              ),
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
