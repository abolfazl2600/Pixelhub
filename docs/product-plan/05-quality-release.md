# 05 | تضمین کیفیت، Release Gates و Definition of Done

## سیاست کلی
هیچ نسخه‌ای فقط با «کد تولیدشده توسط هوش مصنوعی» تأیید نمی‌شود. لازم است Build موفق، تست خودکار، بررسی دستی و ثبت محدودیت‌های واقعی داشته باشد.

## انواع تست
| تست | زمان شروع | هدف |
|---|---|---|
| Format/Lint/Static analysis | V1 | جلوگیری از مشکلات ساده ساخت |
| Unit test Domain | V2 | tap/stroke/count/finish/undo |
| Golden/Widget test | V2 | یکنواختی UI و ابعاد ثابت |
| Property/Parser test | V2 | درست بودن schema و فایل‌ها |
| Integration test local store | V2 | حفظ پیشرفت پس از Restart |
| Converter test با عکس‌های متنوع | V3 | عملکرد رنگ‌آمیزی از عکس |
| Cross-browser UI | V3 | Chrome و مرورگرهای هدف |
| Auth/Sync conflict test | V4 | Guest merge، Retry، Reset |
| API contract/security test | V4 | احراز هویت و مجوز دسترسی |
| Content pipeline e2e | V5 | Draft -> Publish -> CDN |
| Billing test | V6 | renew، cancel، refund، restore |
| UGC abuse/moderation test | V7 | report، block، takedown |
| Load/Resilience | V5 به بعد | بار API، queue، storage، disaster recovery |

## ماتریس پشتیبانی
- Android: گوشی واقعی پایین‌رده/میان‌رده/بالارده در چند نسخه Android فعال بازار هدف.
- Web desktop: Chrome و Edge/Firefox یا Safari بر اساس بازار هدف، با قاب موبایل وسط‌چین.
- Web mobile: حداقل Chrome Android، تست Touch/Zoom/Import و رفتار Storage.
- RTL و LTR پس از انتخاب زبان‌های هدف؛ اگر فارسی در V1 باشد کنترل Overflow لازم است.
- صفحه‌هایی با عرض 360، 390 و 430 واحد منطقی و ارتفاع کوتاه تست شوند.

## اهداف اولیه مهندسی (SLO فرضی و قابل بازنگری)
- نبود نقص Critical در انتشار هر نسخه.
- حفظ پیشرفت در خروج ناگهانی، بدون از دست‌رفتن نقاشی تکمیل‌شده.
- تجربه هدف نزدیک به 60fps برای سناریوهای عمومی روی گوشی میان‌رده؛ با benchmark تأیید شود.
- UI قابل استفاده بدون شبکه برای Level cached.
- نرخ موفقیت Sync و crash-free در V4+ اندازه‌گیری شوند و سپس اهداف عددی تعیین شوند.

## نمونه معیار پذیرش
- اگر تصویر 64x64 باز است و کاربر 50 خانه را رنگ کرده، پس از قتل پردازش برنامه و بازکردن مجدد، 50 خانه بازیابی شوند.
- اگر شبکه قطع شد، Paint فعلی از کار نیفتد؛ Sync به صف اضافه شود.
- اگر level فایل اشتباه دارد، پیام Error امن نشان دهد و برنامه crash نکند.
- اگر Web در دسکتاپ باز شد، UI به چند ستون دسکتاپ تبدیل نشود.
- اگر 2 دستگاه رنگ خانه‌های متفاوت را ثبت کردند، بعد از Sync مجموع رنگ‌های معتبر حفظ شود.
- اگر purchase fail شد، entitlement اعطا نشود و کاربر خطای واضح ببیند.
- اگر اثر عمومی report شد، عملیات Moderation قابل پیگیری باشد.

## Release Gate و شواهد لازم
برای هر V1..V7 در پرونده همان نسخه:
- [ ] همه Taskهای Required انجام شد.
- [ ] Explicit Out-of-scope وارد این نسخه نشد.
- [ ] تست مرتبط موفق شد.
- [ ] Android Build و Web Build از یک SHA ثبت شد.
- [ ] Web URL و Artifact قابل دستیابی بودند (در صورت فعال بودن Pages).
- [ ] روی حداقل یک گوشی واقعی و یک مرورگر آزموده شد.
- [ ] Known Issues و Release Notes ثبت شد.
- [ ] داده کاربر از نسخه قبلی بدون مشکل مهاجرت کرد.
- [ ] صاحب محصول ویژگی‌ها و گیت را تأیید کرد.

## نسخه‌گذاری و Rollback
- قبل از هر Release رسمی Tag ساخته شود.
- schema migration باید Forward/Backward compatibility یا مهاجرت بررسی‌شده داشته باشد.
- Static Web roll back با deploy commit سالم ممکن است.
- تغییر level منتشرشده از طریق نسخه جدید؛ فایل قبلی پاک نشود تا پیشرفت قبلی از دست نرود.
- Backend rollback و data restore نیازمند runbook است، نه صرفاً بازگرداندن کد.

## مواردی که QA نمی‌تواند اثبات کند
- تنها Build Success معادل عملکرد بی‌نقص روی همه گوشی‌ها نیست.
- Google Play approval به کیفیت CI وابسته نیست و باید واقعی بررسی شود.
- عددهای Retention، درآمد و ترافیک تنها پس از انتشار و اندازه‌گیری واقعی معتبرند.
