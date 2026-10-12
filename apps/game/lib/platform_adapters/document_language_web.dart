import 'package:web/web.dart';

void setDocumentLanguage(String language) {
  // Keep host DOM geometry LTR; Flutter owns the RTL UI and hit testing.
  document.documentElement?.setAttribute('lang', language);
}
