import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:persistence/persistence.dart';
import 'package:pixelhub/features/badges/badge_controller.dart';
import 'package:pixelhub/features/badges/badges_screen.dart';
import 'package:pixelhub/features/gallery/library_controller.dart';

const _catalog = '''
{
  "version": 1,
  "badges": [
    {
      "id": "animal_first",
      "titleFa": "اولین دوست حیوانات",
      "titleEn": "First Animal Friend",
      "descriptionFa": "یک نقاشی حیوان را تکمیل کن.",
      "descriptionEn": "Complete one animal painting.",
      "category": "animals",
      "required": 1,
      "image": "images/animal_first.png",
      "bytes": 100,
      "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    },
    {
      "id": "animal_five",
      "titleFa": "دوستدار حیوانات",
      "titleEn": "Animal Lover",
      "descriptionFa": "پنج نقاشی حیوان را تکمیل کن.",
      "descriptionEn": "Complete five animal paintings.",
      "category": "animals",
      "required": 5,
      "image": "images/animal_five.png",
      "bytes": 100,
      "sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    }
  ]
}
''';

void main() {
  for (final locale in const [Locale('fa'), Locale('en')]) {
    testWidgets(
      'locked badge uses its online mission description in ${locale.languageCode}',
      (tester) async {
        tester.view.devicePixelRatio = 1;
        tester.view.physicalSize = const Size(360, 780);
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);

        final store = MemoryPreferences();
        await store.writeBadgeCatalog(_catalog);
        await store.writeEarnedBadges({'animal_first'});

        final library = LibraryController(store, store);
        final client = MockClient((_) async => http.Response('offline', 503));
        final controller = BadgeController(library, store, client: client);
        addTearDown(() {
          controller.dispose();
          library.dispose();
          client.close();
        });
        await controller.initialize();
        expect(controller.badges.length, 2);

        await tester.pumpWidget(
          MaterialApp(
            locale: locale,
            supportedLocales: const [Locale('fa'), Locale('en')],
            localizationsDelegates: const [
              GlobalMaterialLocalizations.delegate,
              GlobalWidgetsLocalizations.delegate,
              GlobalCupertinoLocalizations.delegate,
            ],
            home: BadgesScreen(badges: controller),
          ),
        );
        await tester.pumpAndSettle();

        expect(
          find.byKey(const ValueKey('badge-animal_first')),
          findsOneWidget,
        );
        expect(find.byKey(const ValueKey('badge-animal_five')), findsOneWidget);
        if (locale.languageCode == 'fa') {
          expect(find.text('اولین دوست حیوانات'), findsOneWidget);
          expect(find.text('دوستدار حیوانات'), findsOneWidget);
          expect(find.text('۰/۵'), findsOneWidget);
          expect(find.text('پنج نقاشی حیوان را تکمیل کن.'), findsOneWidget);
          expect(find.text('هنوز کشف نشده'), findsNothing);
        } else {
          expect(find.text('First Animal Friend'), findsOneWidget);
          expect(find.text('Animal Lover'), findsOneWidget);
          expect(find.text('0/5'), findsOneWidget);
          expect(find.text('Complete five animal paintings.'), findsOneWidget);
          expect(find.text('Not discovered yet'), findsNothing);
        }
        expect(tester.takeException(), isNull);
      },
    );
  }
}
