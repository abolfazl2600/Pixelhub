import 'package:flutter/material.dart';

import '../l10n/strings.dart';

class LanguageButton extends StatelessWidget {
  const LanguageButton({required this.onToggle, super.key});
  final VoidCallback onToggle;

  @override
  Widget build(BuildContext context) => TextButton(
    key: const ValueKey('language-toggle'),
    onPressed: onToggle,
    style: TextButton.styleFrom(minimumSize: const Size(48, 48)),
    child: Text(context.isPersian ? 'English' : 'فارسی'),
  );
}
