import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:level_schema/level_schema.dart';

import '../../app/language_button.dart';
import '../../core/pixel_art_preview.dart';
import '../../l10n/strings.dart';
import '../gallery/library_controller.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({
    required this.levels,
    required this.library,
    required this.onLanguageToggle,
    super.key,
  });
  final List<LevelDefinition> levels;
  final LibraryController library;
  final VoidCallback onLanguageToggle;
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late String _selectedId = widget.levels.first.id;
  @override
  Widget build(BuildContext context) {
    final level = widget.levels.firstWhere((level) => level.id == _selectedId);
    final s = context.strings;
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          key: const ValueKey('home-scroll'),
          padding: const EdgeInsets.all(PixelTokens.space),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  const Expanded(
                    child: Text(
                      'Pixelhub',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: 25,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ),
                  IconButton(
                    tooltip: s.profile,
                    icon: const Icon(Icons.person_outline_rounded),
                    onPressed: () => context.push('/profile'),
                  ),
                  LanguageButton(onToggle: widget.onLanguageToggle),
                ],
              ),
              const SizedBox(height: 24),
              Align(
                alignment: AlignmentDirectional.centerStart,
                child: PreviewBadge(label: s.demoBadge),
              ),
              const SizedBox(height: 16),
              Text(
                s.headline,
                style: const TextStyle(
                  fontSize: 38,
                  height: 1.4,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                s.welcome,
                style: const TextStyle(
                  color: PixelTokens.muted,
                  fontSize: 15,
                  height: 1.8,
                ),
              ),
              const SizedBox(height: 18),
              Card(
                color: PixelTokens.lemon,
                child: Padding(
                  padding: const EdgeInsets.all(14),
                  child: Row(
                    children: [
                      const Icon(
                        Icons.check_circle_outline_rounded,
                        color: PixelTokens.green,
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          s.homeCompleted(
                            context.digits(widget.library.levels.where(widget.library.isComplete).length),
                            context.digits(widget.library.levels.length),
                          ),
                        ),
                      ),
                      TextButton(
                        onPressed: () => context.push('/profile'),
                        child: Text(s.profile),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
              DropdownButtonFormField<String>(
                key: const ValueKey('level-picker'),
                initialValue: _selectedId,
                isExpanded: true,
                decoration: InputDecoration(
                  labelText: s.choosePicture,
                  border: const OutlineInputBorder(),
                ),
                items: [
                  for (final item in widget.levels)
                    DropdownMenuItem(
                      value: item.id,
                      child: Text(
                        '${item.titleFor(context.isPersian ? 'fa' : 'en')} · ${context.digits(item.width)} × ${context.digits(item.height)}',
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                ],
                onChanged: (value) {
                  if (value != null) setState(() => _selectedId = value);
                },
              ),
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: PixelTokens.peach,
                  borderRadius: BorderRadius.circular(PixelTokens.radius),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(16),
                      child: PixelArtPreview(level: level),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      level.titleFor(context.isPersian ? 'fa' : 'en'),
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 16),
                    FilledButton.icon(
                      key: const ValueKey('open-preview'),
                      onPressed: () => context.go('/painting/${level.id}'),
                      icon: const Icon(Icons.brush_rounded),
                      label: Text(s.startPainting),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  OutlinedButton.icon(
                    onPressed: () => context.push('/gallery'),
                    icon: const Icon(Icons.grid_view_rounded),
                    label: Text(s.gallery),
                  ),
                  OutlinedButton.icon(
                    onPressed: () => context.push('/my-gallery'),
                    icon: const Icon(Icons.collections_outlined),
                    label: Text(s.myGallery),
                  ),
                  OutlinedButton.icon(
                    onPressed: () => context.push('/import'),
                    icon: const Icon(Icons.add_photo_alternate_outlined),
                    label: Text(s.importPhoto),
                  ),
                  TextButton.icon(
                    onPressed: () => context.push('/settings'),
                    icon: const Icon(Icons.settings_outlined),
                    label: Text(s.settings),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              Text(
                s.offlineNote,
                style: const TextStyle(color: PixelTokens.muted, height: 1.8),
              ),
              const SizedBox(height: 8),
              Text(
                s.storageNote,
                style: const TextStyle(
                  color: PixelTokens.muted,
                  fontSize: 12,
                  height: 1.8,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
