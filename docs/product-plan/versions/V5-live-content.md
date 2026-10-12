# V5 — مدیریت محتوای آنلاین و زیرساخت عملیاتی

نسخه پیشنهادی: v0.5.0 | وضعیت هدف: Operational Beta | وابستگی: V4.

## هدف نسخه
تیم بدون انتشار APK جدید، تصویر بسازد، بررسی کند، منتشر کند و در گالری کاربران نمایش دهد. این نسخه نقطه تبدیل MVP به محصول محتوایی قابل اداره است.

## داخل محدوده (Must Have)
- [ ] Catalog API شامل دسته‌ها، Level metadata، visibility و pagination.
- [ ] Object Storage برای original/level/thumbnail با مسیر نسخه‌دار.
- [ ] CDN و caching صحیح؛ checksum/etag و immutable level files.
- [ ] Admin Panel با MFA و نقش‌های Owner/Admin/Editor/Reviewer.
- [ ] ایجاد/ویرایش draft، tag، category، pack و license metadata.
- [ ] Content Worker برای resize/quantize/thumbnail/validation.
- [ ] Preview در موتور بازی قبل از انتشار.
- [ ] گردش تأیید Draft -> Review -> Published.
- [ ] Scheduled Publish و Unpublish/Archive.
- [ ] امکان rollback محتوای معیوب بدون تخریب progress سابق.
- [ ] cache و download برای Offline stages.
- [ ] Search/filter ساده در Gallery با API.
- [ ] Admin audit log و alerts.
- [ ] بکاپ منظم DB/Storage و تمرین restore.
- [ ] analytics اولیه: open/start/complete/error بدون اطلاعات حساس.
- [ ] load test برای catalog/CDN و گزارش هزینه.
- [ ] هدف 150+ تصویر قابل بازی برای آزمون سامانه محتوا.

## خارج از محدوده
- پرداخت اشتراک و Ads اجباری یا اختیاری.
- Follow، Public User Upload و Feed.
- Chat و Realtime Multiplayer.
- پیشنهادگر سنگین و ML pipeline.
- مهاجرت به Microservice بدون دلیل اندازه‌گیری‌شده.

## پیش‌نیازهای امنیتی
- RBAC سمت سرور و هیچ کلید Admin در کلاینت عمومی.
- upload validation، quarantine و محدودیت ابعاد/فایل.
- URL امضاشده برای تصویر خصوصی.
- ثبت license و منبع اثر قبل از Publish.
- مدیریت محتوا versioned؛ حذف ناگهانی Levelهای استفاده‌شده مجاز نیست.
- محافظت API با rate limiting، logging و monitoring.

## ترتیب کار
1. طراحی schema کاتالوگ/نسخه محتوا.
2. Storage + CDN و URL/version policy.
3. Worker و job queue.
4. Backend catalog endpoints.
5. پنل Admin + Auth/roles.
6. Content preview/approval/publish.
7. Flutter remote Catalog repository و offline cache.
8. Analytics/monitoring، load test و backup restore.
9. تولید و انتشار گروه اولیه تصاویر.

## معیار پذیرش
- [ ] مدیر مرحله جدید را آپلود، Preview و Publish کند.
- [ ] Android و Web بدون آپدیت اپ مرحله منتشرشده را نشان دهند.
- [ ] سطح downloaded بدون اینترنت قابل رنگ‌آمیزی باشد.
- [ ] خطای فایل یا publish قابل Rollback باشد و پیشرفت قدیمی محفوظ بماند.
- [ ] Editor نتواند عملیات Admin/Owner انجام دهد.
- [ ] هیچ فایل عکس خصوصی در URL عمومی منتشر نشود.
- [ ] لاگ عملیات و گزارش خطای پردازش قابل مشاهده باشد.

## انتقال به V6
پس از تثبیت محتوا، مخاطب، الزامات حقوقی و billing/ads/consent برای انتشار عمومی و درآمدزایی آماده می‌شود.
