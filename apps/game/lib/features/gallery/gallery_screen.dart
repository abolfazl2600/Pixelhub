import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:level_schema/level_schema.dart';

import '../../app/language_button.dart';
import '../../core/pixel_art_preview.dart';
import '../../l10n/strings.dart';
import 'library_controller.dart';

String categoryLabel(BuildContext context, String category) =>
    switch (category) {
      'nature' => context.strings.categoryNature,
      'animals' => context.strings.categoryAnimals,
      'objects' => context.strings.categoryObjects,
      'space' => context.strings.categorySpace,
      'personal' => context.strings.categoryPersonal,
      _ => context.strings.categoryPatterns,
    };

class GalleryScreen extends StatefulWidget {
  const GalleryScreen({
    required this.library,
    required this.onLanguageToggle,
    this.personal = false,
    super.key,
  });
  final LibraryController library;
  final VoidCallback onLanguageToggle;
  final bool personal;
  @override
  State<GalleryScreen> createState() => _GalleryScreenState();
}

class _GalleryScreenState extends State<GalleryScreen> {
  String _category = 'all', _filter = 'all', _search = '';

  bool _matches(LevelDefinition level) {
    final library = widget.library;
    if (!widget.personal && level.id.startsWith('private-')) {
      return false;
    }
    if (_category != 'all' && library.category(level) != _category) {
      return false;
    }
    if (_filter == 'personal' && !level.id.startsWith('private-')) {
      return false;
    }
    if (_filter == 'favorites' && !library.isFavorite(level)) {
      return false;
    }
    if (_filter == 'completed' && !library.isComplete(level)) {
      return false;
    }
    if (_filter == 'progress' &&
        (library.completed(level) == 0 || library.isComplete(level))) {
      return false;
    }
    if (widget.personal &&
        _filter == 'all' &&
        !level.id.startsWith('private-') &&
        library.completed(level) == 0 &&
        !library.isFavorite(level)) {
      return false;
    }
    final query = _search.trim().toLowerCase();
    return query.isEmpty ||
        '${level.title} ${level.titleEn} ${library.metadata[level.id]?.tags.join(' ') ?? ''}'
            .toLowerCase()
            .contains(query);
  }

  Future<void> _favorite(LevelDefinition level) async {
    try {
      await widget.library.toggleFavorite(level);
    } on Object {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(context.strings.librarySaveError)),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: widget.library,
    builder: (context, _) {
      final s = context.strings, library = widget.library;
      final levels = library.levels.where(_matches).toList();
      return Scaffold(
        appBar: AppBar(
          leading: IconButton(
            tooltip: s.backHome,
            onPressed: () => context.go('/'),
            icon: const Icon(Icons.arrow_back),
          ),
          title: Text(widget.personal ? s.myGallery : s.gallery),
          actions: [
            IconButton(
              tooltip: s.profile,
              onPressed: () => context.push('/profile'),
              icon: const Icon(Icons.person_outline_rounded),
            ),
            LanguageButton(onToggle: widget.onLanguageToggle),
          ],
        ),
        floatingActionButton: widget.personal
            ? FloatingActionButton(
                onPressed: () => context.push('/import'),
                tooltip: s.importPhoto,
                child: const Icon(Icons.add_photo_alternate_outlined),
              )
            : null,
        body: SafeArea(
          child: CustomScrollView(
            slivers: [
              SliverPadding(
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                sliver: SliverToBoxAdapter(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        s.galleryResults(context.digits(levels.length)),
                        style: const TextStyle(
                          color: PixelTokens.muted,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 10),
                      TextField(
                        decoration: InputDecoration(
                          labelText: s.searchPictures,
                          prefixIcon: const Icon(Icons.search),
                          border: const OutlineInputBorder(),
                        ),
                        onChanged: (value) => setState(() => _search = value),
                      ),
                      const SizedBox(height: 12),
                      Wrap(
                        spacing: 6,
                        runSpacing: 4,
                        children: [
                          ChoiceChip(
                            label: Text(s.allPictures),
                            selected: _category == 'all',
                            onSelected: (_) =>
                                setState(() => _category = 'all'),
                          ),
                          for (final category in [
                            'nature',
                            'animals',
                            'objects',
                            'patterns',
                            'space',
                            if (widget.personal) 'personal',
                          ])
                            ChoiceChip(
                              label: Text(categoryLabel(context, category)),
                              selected: _category == category,
                              onSelected: (_) =>
                                  setState(() => _category = category),
                            ),
                        ],
                      ),
                      if (widget.personal) ...[
                        const SizedBox(height: 12),
                        Wrap(
                          spacing: 6,
                          runSpacing: 4,
                          children: [
                            for (final entry in <String, String>{
                              'all': s.allPictures,
                              'progress': s.inProgress,
                              'completed': s.completedWorks,
                              'favorites': s.favorites,
                              'personal': s.importedWorks,
                            }.entries)
                              ChoiceChip(
                                label: Text(entry.value),
                                selected: _filter == entry.key,
                                onSelected: (_) =>
                                    setState(() => _filter = entry.key),
                              ),
                          ],
                        ),
                      ],
                      if (library.status == LibraryStatus.loading)
                        const Padding(
                          padding: EdgeInsets.all(16),
                          child: LinearProgressIndicator(),
                        ),
                      if (library.status == LibraryStatus.error) ...[
                        Text(s.libraryLoadError),
                        TextButton(
                          onPressed: library.load,
                          child: Text(s.retry),
                        ),
                      ],
                      if (library.storageError)
                        Text(
                          s.librarySaveError,
                          style: TextStyle(
                            color: Theme.of(context).colorScheme.error,
                          ),
                        ),
                      const SizedBox(height: 12),
                    ],
                  ),
                ),
              ),
              if (levels.isEmpty)
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.all(32),
                    child: Column(
                      children: [
                        const Icon(Icons.collections_outlined, size: 48),
                        const SizedBox(height: 16),
                        Text(s.galleryEmpty, textAlign: TextAlign.center),
                        if (widget.personal)
                          TextButton(
                            onPressed: () => context.push('/import'),
                            child: Text(s.importPhoto),
                          ),
                      ],
                    ),
                  ),
                ),
              SliverPadding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 96),
                sliver: SliverGrid.builder(
                  gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
                    maxCrossAxisExtent: 540,
                    mainAxisExtent: 176,
                    mainAxisSpacing: 12,
                    crossAxisSpacing: 12,
                  ),
                  itemCount: levels.length,
                  itemBuilder: (context, index) {
                    final level = levels[index];
                    final count = library.completed(level);
                    return Card(
                      color: PixelTokens.peach,
                      clipBehavior: Clip.antiAlias,
                      child: InkWell(
                        onTap: () => context.push('/artwork/${level.id}'),
                        child: Padding(
                          padding: const EdgeInsets.all(12),
                          child: Row(
                            children: [
                              SizedBox(
                                width: 96,
                                child: ClipRRect(
                                  borderRadius: BorderRadius.circular(12),
                                  child: PixelArtPreview(level: level),
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      level.titleFor(
                                        context.isPersian ? 'fa' : 'en',
                                      ),
                                      maxLines: 2,
                                      overflow: TextOverflow.ellipsis,
                                      style: const TextStyle(
                                        fontWeight: FontWeight.w700,
                                      ),
                                    ),
                                    Text(
                                      categoryLabel(
                                        context,
                                        library.category(level),
                                      ),
                                      style: const TextStyle(fontSize: 12),
                                    ),
                                    Text(
                                      '${context.digits(level.width)} × ${context.digits(level.height)}',
                                      style: const TextStyle(fontSize: 12),
                                    ),
                                    if (count > 0) ...[
                                      const SizedBox(height: 6),
                                      LinearProgressIndicator(
                                        value: count / level.cells.length,
                                      ),
                                      Text(
                                        library.isComplete(level)
                                            ? s.completedWorks
                                            : s.progressPercent(
                                                context.digits(
                                                  (count *
                                                          100 /
                                                          level.cells.length)
                                                      .floor(),
                                                ),
                                              ),
                                        style: const TextStyle(fontSize: 12),
                                      ),
                                    ],
                                    if (library.damagedProgress.contains(
                                      level.id,
                                    ))
                                      Text(
                                        s.progressNeedsAttention,
                                        style: const TextStyle(fontSize: 12),
                                      ),
                                  ],
                                ),
                              ),
                              IconButton(
                                tooltip: library.isFavorite(level)
                                    ? s.removeFavorite
                                    : s.addFavorite,
                                onPressed:
                                    library.busy ||
                                        library.status != LibraryStatus.ready
                                    ? null
                                    : () => _favorite(level),
                                icon: Icon(
                                  library.isFavorite(level)
                                      ? Icons.favorite
                                      : Icons.favorite_border,
                                  color: PixelTokens.green,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      );
    },
  );
}
