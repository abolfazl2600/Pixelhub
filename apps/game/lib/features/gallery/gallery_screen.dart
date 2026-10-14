import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:level_schema/level_schema.dart';

import '../../core/pixel_art_preview.dart';
import '../../l10n/strings.dart';
import 'artwork_categories.dart';
import 'gallery_filters.dart';
import 'library_controller.dart';
import 'online_catalog_controller.dart';

String categoryLabel(BuildContext context, String category) =>
    switch (category) {
      'nature' => context.strings.categoryNature,
      'animals' => context.strings.categoryAnimals,
      'objects' => context.strings.categoryObjects,
      'masterpieces' => context.strings.categoryMasterpieces,
      'persian_architecture' => context.strings.categoryPersianArchitecture,
      'space' => context.strings.categorySpace,
      'personal' => context.strings.categoryPersonal,
      _ => context.strings.categoryPatterns,
    };

class GalleryScreen extends StatefulWidget {
  const GalleryScreen({
    required this.library,
    required this.online,
    this.personal = false,
    super.key,
  });
  final LibraryController library;
  final OnlineCatalogController online;
  final bool personal;

  @override
  State<GalleryScreen> createState() => _GalleryScreenState();
}

class _GalleryScreenState extends State<GalleryScreen> {
  String _category = 'all', _filter = 'all', _search = '';
  int _onlineVisibleCount = 6;

  @override
  void initState() {
    super.initState();
    if (!widget.personal) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) widget.online.checkForUpdates();
      });
    }
  }

  void _selectCategory(String category) {
    setState(() {
      _category = category;
      _onlineVisibleCount = category == 'all' ? 6 : 12;
    });
  }

  void _updateSearch(String query) {
    setState(() {
      _search = query;
      _onlineVisibleCount = _category == 'all' ? 6 : 12;
    });
  }

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

  Future<void> _downloadAndPaint(
    OnlinePicture picture, {
    BuildContext? previewContext,
  }) async {
    if (widget.online.downloadingId != null) return;
    await widget.online.download(picture);
    if (!mounted) return;
    if (widget.online.downloaded.any((level) => level.id == picture.id)) {
      if (previewContext != null && previewContext.mounted) {
        Navigator.of(previewContext).pop();
      }
      if (mounted) context.go('/painting/${picture.id}');
    } else {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(context.strings.downloadFailed)));
    }
  }

  Widget _previewImage(OnlinePicture picture) => Image.network(
    widget.online.previewUrl(picture).toString(),
    fit: BoxFit.contain,
    filterQuality: FilterQuality.none,
    loadingBuilder: (context, child, progress) => progress == null
        ? child
        : const Center(child: CircularProgressIndicator.adaptive()),
    errorBuilder: (context, error, stackTrace) =>
        const Center(child: Icon(Icons.image_not_supported_outlined, size: 36)),
  );

  void _showOnlinePreview(OnlinePicture picture) {
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      isScrollControlled: true,
      builder: (sheetContext) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
          child: ListenableBuilder(
            listenable: widget.online,
            builder: (context, _) => Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                SizedBox(height: 180, child: _previewImage(picture)),
                const SizedBox(height: 12),
                Text(
                  picture.titleFor(context.isPersian ? 'fa' : 'en'),
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 4),
                Text(
                  '${categoryLabel(context, picture.category)} · '
                  '${context.digits(picture.width)} × '
                  '${context.digits(picture.height)}',
                  textAlign: TextAlign.center,
                ),
                if (picture.animation != null) ...[
                  const SizedBox(height: 6),
                  Text(
                    context.isPersian
                        ? 'نقاشی متحرک · ${context.digits(picture.animation!.frameCount)} فریم پس از تکمیل'
                        : 'Animated after completion · ${context.digits(picture.animation!.frameCount)} frames',
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontWeight: FontWeight.w600),
                  ),
                ],
                const SizedBox(height: 16),
                FilledButton.icon(
                  onPressed: widget.online.downloadingId != null
                      ? null
                      : () => _downloadAndPaint(
                          picture,
                          previewContext: sheetContext,
                        ),
                  icon: const Icon(Icons.download_outlined),
                  label: Text(
                    widget.online.downloadingId == picture.id
                        ? context.strings.downloadingPicture
                        : context.strings.downloadAndPaint,
                  ),
                ),
                if (widget.online.failedDownloadId == picture.id)
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      context.strings.downloadFailed,
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.error,
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _localCard(BuildContext context, LevelDefinition level) {
    final library = widget.library;
    final count = library.completed(level);
    final s = context.strings;
    return Card(
      key: ValueKey('local-picture-${level.id}'),
      color: PixelTokens.peach,
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => context.push('/artwork/${level.id}'),
        child: Padding(
          padding: const EdgeInsets.all(10),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Expanded(
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(10),
                      child: PixelArtPreview(level: level),
                    ),
                    PositionedDirectional(
                      end: 4,
                      top: 4,
                      child: Material(
                        color: Colors.white.withValues(alpha: 0.90),
                        shape: const CircleBorder(),
                        child: IconButton(
                          constraints: const BoxConstraints(
                            minWidth: 40,
                            minHeight: 40,
                          ),
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
                            size: 20,
                            color: PixelTokens.green,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 8),
              Text(
                level.titleFor(context.isPersian ? 'fa' : 'en'),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 2),
              Row(
                children: [
                  Expanded(
                    child: Text(
                      categoryLabel(context, library.category(level)),
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontSize: 12),
                    ),
                  ),
                  Text(
                    '${context.digits(level.width)} × '
                    '${context.digits(level.height)}',
                    style: const TextStyle(fontSize: 12),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              if (count > 0) ...[
                LinearProgressIndicator(
                  value: count / level.cells.length,
                  minHeight: 4,
                ),
                Text(
                  library.isComplete(level)
                      ? s.completedWorks
                      : s.progressPercent(
                          context.digits(
                            (count * 100 / level.cells.length).floor(),
                          ),
                        ),
                  style: const TextStyle(fontSize: 11),
                ),
              ] else
                Text(
                  library.damagedProgress.contains(level.id)
                      ? s.progressNeedsAttention
                      : s.readyToPaint,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontSize: 11),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _onlineCard(BuildContext context, OnlinePicture picture) {
    final s = context.strings;
    final downloading = widget.online.downloadingId == picture.id;
    return Card(
      key: ValueKey('online-picture-${picture.id}'),
      color: PixelTokens.peach,
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => _showOnlinePreview(picture),
        child: Padding(
          padding: const EdgeInsets.all(10),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Expanded(
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(10),
                      child: _previewImage(picture),
                    ),
                    if (picture.animation != null)
                      PositionedDirectional(
                        start: 4,
                        top: 4,
                        child: Tooltip(
                          message: context.isPersian
                              ? 'متحرک پس از تکمیل'
                              : 'Animated after completion',
                          child: DecoratedBox(
                            decoration: BoxDecoration(
                              color: Colors.white.withValues(alpha: 0.9),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Padding(
                              padding: EdgeInsets.all(6),
                              child: Icon(Icons.motion_photos_on, size: 19),
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
              ),
              const SizedBox(height: 8),
              Text(
                picture.titleFor(context.isPersian ? 'fa' : 'en'),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 2),
              Row(
                children: [
                  Expanded(
                    child: Text(
                      categoryLabel(context, picture.category),
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontSize: 12),
                    ),
                  ),
                  Text(
                    '${context.digits(picture.width)} × '
                    '${context.digits(picture.height)}',
                    style: const TextStyle(fontSize: 12),
                  ),
                ],
              ),
              const SizedBox(height: 2),
              Align(
                alignment: AlignmentDirectional.centerEnd,
                child: IconButton(
                  key: ValueKey('online-download-${picture.id}'),
                  tooltip: s.downloadPicture,
                  visualDensity: VisualDensity.compact,
                  constraints: const BoxConstraints(
                    minWidth: 36,
                    minHeight: 36,
                  ),
                  padding: EdgeInsets.zero,
                  icon: downloading
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.cloud_download_outlined, size: 22),
                  onPressed: widget.online.downloadingId != null
                      ? null
                      : () => _downloadAndPaint(picture),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: Listenable.merge([widget.library, widget.online]),
    builder: (context, _) {
      final s = context.strings;
      final library = widget.library;
      final online = widget.online;
      final levels = library.levels.where(_matches).toList();
      final available = widget.personal
          ? <OnlinePicture>[]
          : matchingOnlinePictures(
              online.available,
              category: _category,
              search: _search,
            );
      final visible = available.take(_onlineVisibleCount).toList();
      const grid = SliverGridDelegateWithMaxCrossAxisExtent(
        maxCrossAxisExtent: 240,
        mainAxisExtent: 246,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
      );

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
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 12),
                sliver: SliverToBoxAdapter(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      TextField(
                        decoration: InputDecoration(
                          labelText: s.searchPictures,
                          prefixIcon: const Icon(Icons.search),
                          border: const OutlineInputBorder(),
                        ),
                        onChanged: _updateSearch,
                      ),
                      const SizedBox(height: 12),
                      Wrap(
                        spacing: 6,
                        runSpacing: 4,
                        children: [
                          ChoiceChip(
                            label: Text(s.allPictures),
                            selected: _category == 'all',
                            onSelected: (_) => _selectCategory('all'),
                          ),
                          for (final category in [
                            ...publicArtworkCategories,
                            if (widget.personal) 'personal',
                          ])
                            ChoiceChip(
                              label: Text(categoryLabel(context, category)),
                              selected: _category == category,
                              onSelected: (_) => _selectCategory(category),
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
                    ],
                  ),
                ),
              ),
              SliverPadding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 10),
                sliver: SliverToBoxAdapter(
                  child: Row(
                    children: [
                      Expanded(
                        child: Text(
                          widget.personal ? s.myGallery : s.onDevicePictures,
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                      ),
                      Text(
                        context.digits(levels.length),
                        style: const TextStyle(color: PixelTokens.muted),
                      ),
                    ],
                  ),
                ),
              ),
              if (levels.isEmpty)
                SliverPadding(
                  padding: const EdgeInsets.fromLTRB(16, 4, 16, 20),
                  sliver: SliverToBoxAdapter(
                    child: Text(
                      widget.personal ? s.galleryEmpty : s.noLocalPictures,
                      style: const TextStyle(color: PixelTokens.muted),
                    ),
                  ),
                )
              else
                SliverPadding(
                  padding: const EdgeInsets.fromLTRB(16, 0, 16, 20),
                  sliver: SliverGrid.builder(
                    gridDelegate: grid,
                    itemCount: levels.length,
                    itemBuilder: (context, index) =>
                        _localCard(context, levels[index]),
                  ),
                ),
              if (!widget.personal) ...[
                SliverPadding(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 10),
                  sliver: SliverToBoxAdapter(
                    child: Column(
                      key: const ValueKey('online-gallery-section'),
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.cloud_outlined, size: 22),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                _category == 'all'
                                    ? s.onlinePictures
                                    : s.onlineCategoryTitle(
                                        categoryLabel(context, _category),
                                      ),
                                style: Theme.of(context).textTheme.titleMedium,
                              ),
                            ),
                            if (online.status == OnlineCatalogStatus.ready)
                              Text(
                                context.digits(available.length),
                                style: const TextStyle(
                                  color: PixelTokens.muted,
                                ),
                              ),
                            IconButton(
                              tooltip: s.checkPictures,
                              onPressed:
                                  online.status == OnlineCatalogStatus.checking
                                  ? null
                                  : online.checkForUpdates,
                              icon: const Icon(Icons.refresh),
                            ),
                          ],
                        ),
                        Text(
                          s.onlineExplore,
                          style: const TextStyle(color: PixelTokens.muted),
                        ),
                        if (online.status == OnlineCatalogStatus.checking)
                          Padding(
                            padding: const EdgeInsets.only(top: 8),
                            child: Text(s.checkingPictures),
                          ),
                        if (online.status == OnlineCatalogStatus.error)
                          Padding(
                            padding: const EdgeInsets.only(top: 8),
                            child: Text(s.onlineUnavailable),
                          ),
                      ],
                    ),
                  ),
                ),
                if (visible.isNotEmpty)
                  SliverPadding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    sliver: SliverGrid.builder(
                      gridDelegate: grid,
                      itemCount: visible.length,
                      itemBuilder: (context, index) =>
                          _onlineCard(context, visible[index]),
                    ),
                  ),
                if (online.status == OnlineCatalogStatus.ready &&
                    available.isEmpty)
                  SliverPadding(
                    padding: const EdgeInsets.fromLTRB(16, 4, 16, 16),
                    sliver: SliverToBoxAdapter(
                      child: Text(
                        _category == 'all' && _search.trim().isEmpty
                            ? s.noNewPictures
                            : s.noMatchingOnline,
                        style: const TextStyle(color: PixelTokens.muted),
                      ),
                    ),
                  ),
                if (available.length > visible.length)
                  SliverPadding(
                    padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
                    sliver: SliverToBoxAdapter(
                      child: Center(
                        child: OutlinedButton.icon(
                          key: const ValueKey('online-show-more'),
                          onPressed: () =>
                              setState(() => _onlineVisibleCount += 12),
                          icon: const Icon(Icons.expand_more),
                          label: Text(
                            '${s.showMoreOnline} '
                            '(${context.digits(available.length - visible.length)})',
                          ),
                        ),
                      ),
                    ),
                  ),
              ],
              const SliverToBoxAdapter(child: SizedBox(height: 96)),
            ],
          ),
        ),
      );
    },
  );
}
