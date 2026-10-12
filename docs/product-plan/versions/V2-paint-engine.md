# V2 — موتور اصلی نقاشی و ذخیره پیشرفت

نسخه پیشنهادی: v0.2.0 | وضعیت هدف: Playable Demo | وابستگی: V1 و قرارداد Level schema.

## هدف نسخه
کاربر از ابتدا تا انتها یک تصویر پیکسلی شماره‌دار را رنگ کند و پیشرفت با بسته‌شدن اپ حفظ شود. همان مکانیک روی Android و Web کار کند.

## داخل محدوده (Must Have)
- [ ] مدل LevelDefinition با schemaVersion، levelVersion، width/height، palette، cells، checksum.
- [ ] Parser، validator و reject کردن فایل Level نامعتبر.
- [ ] renderer grid و شماره‌های قابل خواندن.
- [ ] پالت شماره‌دار + رنگ انتخاب‌شده.
- [ ] tap برای رنگ‌کردن خانه معتبر، جلوگیری از خانه اشتباه.
- [ ] drag stroke برای چند خانه، بدون جاانداختن سلول در حرکت سریع.
- [ ] Pinch zoom در Android و Web touch؛ pan صحیح و bounds.
- [ ] Mouse/pointer support برای Web desktop.
- [ ] highlight شماره‌های هم‌رنگ و شمارنده خانه‌های باقی‌مانده.
- [ ] Progress percentage، completion detector و Completion screen.
- [ ] Undo حداقل چند اقدام اخیر؛ Reset با تأیید.
- [ ] ذخیره محلی با adapter مناسب برای Android و Web، autosave.
- [ ] resume پس از خروج ناگهانی و بازگشت.
- [ ] مجموعه 10–20 نمونه Level مجاز برای تست.
- [ ] تست‌های Unit و Widget برای Paint، Undo، finish و persistence.
- [ ] پروفایل‌کردن عملکرد روی گوشی واقعی و مرورگر.

## خارج از محدوده (Must Not)
- تبدیل تصویر کاربر، Crop یا Pixelation.
- حساب کاربری و Sync بین دو دستگاه.
- گالری آنلاین، دانلود محتوا و Admin.
- پاداش سکه، اشتراک و تبلیغات.
- تولید آثار کاربران در Community.
- الگوریتم AI مولد تصویر.

## زیرساخت برای آینده
- Progress object شامل levelId, levelVersion, generation, revision، bitset.
- Level asset immutable؛ session جدا از فایل level.
- Storage repository interface به‌جای مستقیم‌نویسی در Widget.
- سطح آماده قابل خواندن از asset/file/network future adapter.
- Eventهای محلی مانند painting_started / completed بدون الزام Analytics آنلاین.

## ترتیب کار
1. پیاده‌سازی schema و parser با fixture.
2. ساخت Painting domain و unit tests.
3. Render + gesture mapping + Palette UI.
4. Zoom/pan و تست روی Touch/Mouse.
5. Undo، progress، completion.
6. ذخیره و Resume.
7. benchmark و اصلاح jank.
8. انتشار Web+APK آزمایشی.

## معیار پذیرش
- [ ] نمونه 32x32، 64x64 و 128x128 باز و قابل رنگ‌آمیزی باشد.
- [ ] تعداد رنگ‌شده و پیشرفت بعد از خروج ناگهانی حفظ شود.
- [ ] Undo/Reset وضعیت اشتباه ایجاد نکنند.
- [ ] خانه رنگ اشتباه شمرده نشود و شمارنده منفی نشود.
- [ ] لمس با زوم بالا خانه درست را تشخیص دهد.
- [ ] رابط Android و Web یکسان باشد؛ تفاوت صرفاً کنترل‌های ورودی باشد.
- [ ] Benchmark روی دستگاه و مرورگر ثبت شود؛ نقص بحرانی کیفیت باقی نماند.

## انتقال به V3
موتور باید هر LevelDefinition معتبر را مستقل از منبع تصویر اجرا کند؛ V3 فرایند تبدیل عکس را به همان فرمت خروجی وصل می‌کند.
