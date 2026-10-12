# 03 | قرارداد داده و مشخصات موتور Pixel Coloring

## Level format v1 (قرارداد پیشنهادی)
~~~
{
  "schemaVersion": 1,
  "levelId": "flower-001",
  "levelVersion": 1,
  "title": "Flower",
  "width": 4,
  "height": 4,
  "palette": ["#FFFFFF", "#E45C73", "#3B9D65"],
  "cells": [0,0,1,0,0,1,1,0,2,2,1,0,0,2,0,0],
  "difficulty": "easy",
  "checksum": "sha256-of-canonical-payload"
}
~~~
- یک index برای هر سلول؛ ترتیب row-major.
- width * height باید دقیقاً برابر length(cells) باشد.
- مقدار هر cell باید بین 0 و palette.length-1 باشد.
- تصمیم درباره خانه‌های Background/Transparent قبل از پیاده‌سازی V2 ثبت شود؛ مثال بالا index صفر را رنگ واقعی فرض می‌کند.
- checksum پس از تعریف canonical serialization تولید شود، نه روی JSON با ترتیب دلخواه کلیدها.
- schemaVersion برای فرمت، levelVersion برای محتوای یک سطح ثابت.
- بعد از انتشار، فایل سطح تغییر نکند؛ تغییر محتوا به levelVersion جدید یا levelId جدید نیاز دارد.

## Progress format v1
~~~
{
  "schemaVersion": 1,
  "userKey": "guest-or-user-id",
  "levelId": "flower-001",
  "levelVersion": 1,
  "generation": 0,
  "completedCells": "base64-encoded-bitset",
  "completedCount": 7,
  "updatedAt": "server-or-local-timestamp",
  "deviceId": "local-device-identifier",
  "revision": 12
}
~~~
- Bitset برای وضعیت رنگ‌شده، نه ذخیره تمام grid در هر save.
- برای 128x128 خانه، Bitset خام حدود 2 KiB است (بدون متادیتا).
- داده محلی روی هر تغییر فوری با debounce مناسب ثبت شود.
- Undo یک stack جدا و محدود است؛ الزامی نیست به Cloud Sync منتقل شود.
- مدل رنگ‌آمیزی اولیه monotonic است (خالی -> تکمیل). Reset نسل generation را افزایش می‌دهد.

## Conflict policy برای V4
- هر تغییر محلی Operation ID منحصربه‌فرد داشته باشد.
- Sync همراه levelVersion، generation، revision و deviceId انجام شود.
- اگر دو دستگاه در همان generation بخشی از سلول‌ها را تکمیل کردند، با OR بیت‌های تکمیل‌شده ادغام شود.
- اگر یکی Reset کرده، سرور طبق generation بالاتر عمل کند؛ از احیای داده قدیمی جلوگیری شود.
- تغییر levelVersion به مهاجرت شفاف یا session جدا نیاز دارد.
- با شکست شبکه، صف محلی حفظ شود و retry با backoff انجام شود.
- زمان محلی تنها شاخص حل تعارض نیست.

## Input / Rendering
- Touch: tap, drag stroke, pinch; Desktop web: pointer down/drag, wheel+modifier zoom یا controls.
- مختصات screen -> inverse canvas transform -> cell index.
- تفاوت drag نقاشی و pan به mode/gesture policy وابسته باشد.
- رنگ اشتباه تغییر وضعیت ندهد؛ feedback ملایم داشته باشد.
- حساب percent بر اساس completedCount / targetCellCount.
- پس از تکمیل رنگ، امکان هایلایت رنگ بعدی و انتقال focus.
- Texture/layers و partial repaint در صورت نیاز با benchmark انتخاب شوند.
- سنجش zoom روی دستگاه کم‌قدرت؛ رفع UI jank قبل از V3.

## Photo -> Level pipeline (V3)
1. Validate MIME/size/dimensions.
2. Decode با اصلاح Orientation.
3. Crop و Resize به grid قابل انتخاب.
4. Quantize به K رنگ با الگوریتم آزمایش‌شده.
5. اختیاری: حذف نویزهای تک‌سلولی، یکپارچه‌سازی طیف‌های نزدیک.
6. تخصیص palette index و تولید cells.
7. Validate، Preview و Save به storage خصوصی محلی.
8. اگر کاربر خواست، Export PNG بدون ارسال اجباری به Backend.

مقادیر پیش‌فرض قابل آزمایش: Easy=32x32/8–12 رنگ؛ Normal=64x64/12–20؛ Hard=96x96/20–32؛ Expert=128x128/32–48. این‌ها تنظیمات طراحی هستند و پس از آزمون کاربران اصلاح می‌شوند.

## سیاست امنیتی داده
- حد حجم و ابعاد فایل ورودی، decode ایمن و کنترل خطای حافظه.
- عکس خصوصی وارد Analytics نشود.
- ذخیره/Export و حذف عکس با عمل صریح کاربر.
- نسخه Public برای تصویر کاربر تنها بعد از Consent و Moderation در V7.

## تست‌های قرارداد
- level نامعتبر (ابعاد غلط، palette index بیرون محدوده) reject شود.
- output converter از parser موتور بدون تبدیل ثانویه قابل خواندن باشد.
- یک level نمونه در Android و Web دقیقاً رنگ یکسان داشته باشد.
- پاک‌شدن ناگهانی برنامه در هر نقطه با ذخیره محلی بازیابی شود.
- Sync همزمان دو دستگاه و Reset توسط تست deterministic بررسی شود.
