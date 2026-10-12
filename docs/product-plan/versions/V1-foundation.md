# V1 — پایه محصول و تولید خروجی ابری

نسخه پیشنهادی: v0.1.0 | وضعیت: پیاده‌سازی Technical Preview؛ گیت انتشار در انتظار GitHub و گوشی واقعی | وابستگی: هیچ نسخه پیشین
تجربه کاربر در این نسخه **بازی کامل نیست**؛ هدف اعتبارسنجی زنجیره توسعه AI -> GitHub -> Web/APK است.

## هدف نسخه
با یک Codebase بتوان اپ Flutter را روی Web در GitHub Pages مشاهده و فایل APK آزمایشی آن را از GitHub Actions دریافت کرد. نسخه وب و اندروید در ظاهر و ساختار صفحه یکسان‌اند.

## داخل محدوده (Must Have)
- [x] scaffold Flutter با پشتیبانی Android و Web.
- [x] پوشه‌ها و package boundaries مطابق سند Architecture.
- [x] Design tokens: palette، فونت، spacing، component states.
- [x] shell اپ: Splash، Home آزمایشی، navigation اولیه.
- [x] نمایش قاب موبایلی واحد در مرورگر دسکتاپ با عرض حداکثر 430 منطقی و وسط‌چین.
- [x] تست landscape/height کم، safe area و حفظ قابلیت اسکرول.
- [x] نمونه Fixture یک تصویر ثابت و placeholder صفحه Painting (نه موتور واقعی).
- [x] Flutter version pin، .gitignore، formatting و lint config.
- [x] workflow CI برای analyze/test/build web/android.
- [x] workflow GitHub Pages با base href /Pixelhub/ و routing سازگار Refresh.
- [x] workflow Artifact APK آزمایشی، build from same commit.
- [x] فایل README ریشه با لینک‌های Web/Artifacts و روش توسعه بدون IDE محلی.
- [x] ثبت ADR انتخاب state manager و local store، حتی اگر هنوز استفاده‌ای نشده.
- [x] template برای Issue/PR و کاتالوگ تست دستی ابتدایی.

## خارج از محدوده (Must Not)
- رنگ‌آمیزی واقعی، Undo، Zoom و ذخیره پیشرفت.
- تبدیل عکس، گالری تصاویر واقعی و سطح‌های متعدد.
- Backend، دیتابیس، حساب کاربری، API، سرور خارجی.
- پرداخت، تبلیغات، اعلان، جامعه، Chat و Admin.
- ادعای Play Store readiness، فایل AAB signed، نیاز به نشر در Google Play.
- چیدمان دسکتاپ جدا، Sidebar مخصوص وب یا تغییر تعداد ستون‌ها بر اساس عرض دسکتاپ.

## زیرساخت برای آینده (بدون فعال‌سازی زودهنگام)
- define interfaces: LevelRepository، ProgressRepository، AuthAdapter، BillingAdapter.
- جداسازی Flutter UI از Painting domain.
- اضافه‌کردن schemaVersion و constants مسیرهای asset.
- environment config برای staging/prod بدون واردکردن secrets.
- تعیین نام package یکتای Android؛ پس از انتشار بهتر است تغییر نکند.

## ترتیب اجرای V1
1. ساخت apps/game و اطمینان از خروجی Web/Android بدون خطا.
2. قاب UI موبایلی ثابت + shell اولیه.
3. تست Widget برای عرض قاب و navigation.
4. تنظیم CI lint و unit smoke.
5. ساخت APK روی Runner و دریافت Artifact.
6. تنظیم Pages و بازکردن لینک سایت.
7. تست دستی ظاهر Web و APK، ثبت issues.

## معیار پذیرش / Release Gate
- [ ] در Branch اصلی، CI سبز باشد و Web+APK با SHA یکسان ساخته شوند.
- [ ] URL سایت GitHub Pages باز شود؛ Refresh باعث خطای مسیر نشود.
- [ ] APK روی حداقل یک Android نصب و وارد Home شود.
- [ ] مرورگر دسکتاپ، UI موبایل را بدون تبدیل به صفحه دسکتاپ نشان دهد.
- [ ] README نصب، مسیر Artifact و خطاهای شناخته‌شده را توضیح دهد.
- [ ] هیچ Secret یا Keystore واقعی Commit نشده باشد.

## شواهد پیاده‌سازی V1
- سورس در `apps/game` و چهار پکیج مشترک ساخته شده است؛ Fixture و فونت‌ها محلی‌اند.
- فایل‌های گردش‌کار CI و Pages ایجاد شده‌اند؛ اجرای واقعی GitHub و انتشار عمومی هنوز تأیید نشده‌اند.
- [گزارش اعتبارسنجی محیط ابری](../../qa/v1-validation.md)، [چک‌لیست گوشی/مرورگر](../../qa/v1-manual-checklist.md) و [تصمیم معماری](../../adr/0001-v1-foundation.md) وضعیت واقعی آزمون‌ها و محدودیت‌ها را ثبت می‌کنند.
- تیک‌های Must Have به پیاده‌سازی فایل‌ها اشاره دارند؛ معیار پذیرش بالا تا ثبت CI، Pages و نصب روی گوشی واقعی باز می‌ماند.

## خروجی و انتقال به V2
Web Demo + APK تستی + Repo ساختارمند. V2 با تکیه به این shell موتور نقاشی را اضافه می‌کند؛ قابلیت‌های backend هنوز تعهد نیستند.
