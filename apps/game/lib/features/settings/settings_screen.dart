import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../app/language_button.dart';
import '../../l10n/strings.dart';
import '../../platform_adapters/offline_support.dart';
import '../gallery/library_controller.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({
    required this.library,
    required this.onLanguageToggle,
    required this.onClear,
    super.key,
  });
  final LibraryController library;
  final VoidCallback onLanguageToggle;
  final Future<void> Function() onClear;
  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _busy = false;
  Future<void> _clear() async {
    final s = context.strings;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(s.clearData),
        content: Text(s.clearDataMessage),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(s.cancel),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text(s.delete),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) {
      return;
    }
    setState(() => _busy = true);
    try {
      await widget.onClear();
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(context.strings.dataCleared)));
      }
    } on Object {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(context.strings.clearDataError)));
      }
    } finally {
      if (mounted) {
        setState(() => _busy = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final s = context.strings;
    return PopScope(
      canPop: !_busy,
      child: Scaffold(
        appBar: AppBar(
          leading: IconButton(
            tooltip: s.backHome,
            onPressed: _busy ? null : () => context.go('/'),
            icon: const Icon(Icons.arrow_back),
          ),
          title: Text(s.settings),
          actions: [
            if (!_busy) LanguageButton(onToggle: widget.onLanguageToggle),
          ],
        ),
        body: SafeArea(
          child: ListView(
            padding: const EdgeInsets.all(24),
            children: [
              Text(
                s.about,
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 12),
              const Text('Pixelhub · 0.3.0'),
              const SizedBox(height: 12),
              Text(s.aboutMessage, style: const TextStyle(height: 1.8)),
              const SizedBox(height: 24),
              Text(s.importPrivacy, style: const TextStyle(height: 1.8)),
              const SizedBox(height: 12),
              Text(s.originalNotStored, style: const TextStyle(height: 1.8)),
              const SizedBox(height: 12),
              Text(s.storageNote, style: const TextStyle(height: 1.8)),
              const SizedBox(height: 24),
              ValueListenableBuilder(
                listenable: offlineStatus,
                builder: (context, status, _) => Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(switch (status) {
                      OfflineStatus.preparing => s.offlinePreparing,
                      OfflineStatus.ready => s.offlineReady,
                      OfflineStatus.unavailable => s.offlineUnavailable,
                    }, style: const TextStyle(height: 1.8)),
                    if (status == OfflineStatus.preparing)
                      const LinearProgressIndicator(),
                    if (status == OfflineStatus.unavailable)
                      TextButton(
                        onPressed: prepareOfflineApp,
                        child: Text(s.retry),
                      ),
                    const SizedBox(height: 24),
                  ],
                ),
              ),
              ListenableBuilder(
                listenable: widget.library,
                builder: (context, _) => OutlinedButton.icon(
                  onPressed: _busy || widget.library.busy ? null : _clear,
                  icon: const Icon(Icons.delete_outline),
                  label: Text(s.clearData),
                ),
              ),
              if (_busy) const LinearProgressIndicator(),
            ],
          ),
        ),
      ),
    );
  }
}
