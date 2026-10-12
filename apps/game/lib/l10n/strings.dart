import 'package:flutter/widgets.dart';

import 'generated/app_localizations.dart';

extension PixelStrings on BuildContext {
  AppLocalizations get strings => AppLocalizations.of(this);
  bool get isPersian => Localizations.localeOf(this).languageCode == 'fa';

  String digits(Object value) {
    final text = value.toString();
    if (!isPersian) return text;
    return text.replaceAllMapped(
      RegExp('[0-9]'),
      (match) => '۰۱۲۳۴۵۶۷۸۹'[int.parse(match[0]!)],
    );
  }
}
