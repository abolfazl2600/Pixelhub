# V4 — کاربران، Backend و همگام‌سازی

نسخه پیشنهادی: v0.4.0 | وضعیت هدف: Private Beta | وابستگی: V3 و قرارداد Progress.

## پیشرفت پیاده‌سازی

- [x] هسته مستقل همگرایی progress مبتنی بر Bitset، server revision و نسل Reset، با کد و تست‌های منبع. قرارداد: [ADR 0004](../../adr/0004-v4-progress-sync.md).
- [ ] قرارداد پایدار idempotency و تراکنش پایگاه داده، پس از انتخاب Auth/Hosting.
- [ ] Auth، API، صف آفلاین، مهاجرت مهمان، UI وضعیت Sync و پذیرش بین‌دستگاهی.

این یک گام آماده‌سازی V4 است و به معنی فعال‌بودن حساب کاربری یا Sync در محصول نیست. بنا بر دستور مالک، تست یا Build محلی این تغییر اجرا نشده است.


## هدف نسخه
کاربر با یک حساب وارد Android و Web شود و نقاشی نیمه‌کاره‌اش را بین دو دستگاه ادامه دهد. آفلاین باقی بماند و با وصل‌شدن اینترنت Sync انجام شود.

## داخل محدوده (Must Have)
- [ ] Backend اولیه NestJS یا انتخاب ثبت‌شده در ADR.
- [ ] PostgreSQL با migration، constraints و بکاپ.
- [ ] environmentهای Staging/Production جدا و HTTPS.
- [ ] Auth امن (ایمیل و/یا Google) با provider قابل تعویض.
- [ ] Guest -> Registered migration بدون حذف local progress.
- [ ] پروفایل پایه و تنظیمات حساب.
- [ ] API نسخه‌دار و authorization row-level/service-level.
- [ ] GET/PUT/Sync progress با rev/generation/operationId.
- [ ] conflict handling برای دو دستگاه با Reset policy.
- [ ] local queue, retry/backoff و connection-state UX.
- [ ] ادامه بازی روی Android و Web با همان حساب.
- [ ] نمایش وضعیت همگام‌سازی و آخرین Sync.
- [ ] endpoint حذف حساب و داده شخصی؛ صفحه وب درخواست حذف.
- [ ] error reporting، backend metrics و log redaction.
- [ ] تست Integration امنیتی و conflict.

## خارج از محدوده
- پنل انتشار آثار توسط مدیر و Content Worker کامل.
- فروشگاه و تبلیغات یا حساب Premium.
- Community/Follow/Chat/Public Artwork.
- Upload اتوماتیک اصل تصاویر شخصی.
- معماری Microservices و Kubernetes.
- امکانات پیچیده رتبه‌بندی و توصیه‌گر.

## معماری و جداول حداقلی
- users / identities / profiles / progress / sync_operations / device_sessions.
- User-scope access؛ پارامتر userId ارسالی از کلاینت به تنهایی ملاک نیست.
- server revision و idempotency.
- guest local key باید قابل merge باشد.
- session revocation و log محدود و بدون اطلاعات حساس.
- progress file levelVersion گره بخورد.

## ترتیب کار
1. انتخاب Auth و Hosting با ADR و Data Privacy review.
2. نوشتن OpenAPI و schema دیتابیس.
3. راه‌اندازی Auth و API staging.
4. Progress service و conflict tests.
5. Flutter adapters برای login و sync queue.
6. Guest migration و delete account.
7. تست Android -> Web و Web -> Android.
8. استقرار production محدود برای بتای دعوتی.

## معیار پذیرش
- [ ] ورود با یک حساب در دو نسخه و ادامه وضعیت نقاشی انجام شود.
- [ ] دو دستگاه همزمان خانه‌های متفاوت را تکمیل کنند؛ merge درست باشد.
- [ ] Reset یک دستگاه پس از Sync سلول‌های قدیمی را احیا نکند.
- [ ] در حالت بدون اینترنت Paint و Local Save ادامه پیدا کند.
- [ ] حساب A نتواند progress حساب B را بخواند/بنویسد.
- [ ] حذف حساب و جلسات طبق policy انجام شود.
- [ ] بکاپ و restore staging آزمایش شود.

## انتقال به V5
Backend آماده اتصال Content Catalog و پنل مدیریت است؛ بستر احراز هویت مدیران و آپلود امن در V5 ساخته خواهد شد.
