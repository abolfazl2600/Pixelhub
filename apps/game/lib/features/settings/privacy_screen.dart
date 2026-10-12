import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';

import '../../l10n/strings.dart';

/// This page works entirely offline. The same policy is published as a
/// standalone HTML file at the public URL for Google Play store listing.
class PrivacyScreen extends StatelessWidget {
  const PrivacyScreen({super.key});

  static const publicUrl =
      'https://abolfazl2600.github.io/Pixelhub/privacy.html';

  @override
  Widget build(BuildContext context) {
    final strings = context.strings;
    final sections = [
      strings.privacyIntro,
      strings.privacyPhotos,
      strings.privacySaves,
      strings.privacySharing,
      strings.privacyRemote,
      strings.privacyDelete,
      strings.privacyWebsite,
      strings.privacyContact,
    ];

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          tooltip: strings.backHome,
          onPressed: () {
            if (context.canPop()) {
              context.pop();
            } else {
              context.go('/settings');
            }
          },
          icon: const Icon(Icons.arrow_back_rounded),
        ),
        title: Text(strings.privacyPolicyTitle),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(PixelTokens.space),
          children: [
            const Icon(
              Icons.privacy_tip_outlined,
              size: 42,
              color: PixelTokens.green,
            ),
            const SizedBox(height: 12),
            Text(
              strings.privacyPolicyTitle,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              strings.privacyUpdated,
              textAlign: TextAlign.center,
              style: const TextStyle(color: PixelTokens.muted),
            ),
            const SizedBox(height: 24),
            SelectionArea(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  for (final section in sections) ...[
                    Text(section, style: const TextStyle(height: 1.75)),
                    const SizedBox(height: 16),
                  ],
                  Text(
                    strings.privacyOnlineLink,
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    publicUrl,
                    textDirection: TextDirection.ltr,
                    style: TextStyle(
                      color: PixelTokens.green,
                      decoration: TextDecoration.underline,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: () async {
                await Clipboard.setData(const ClipboardData(text: publicUrl));
                if (!context.mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(context.strings.privacyLinkCopied)),
                );
              },
              icon: const Icon(Icons.copy_rounded),
              label: Text(strings.privacyCopyLink),
            ),
          ],
        ),
      ),
    );
  }
}
