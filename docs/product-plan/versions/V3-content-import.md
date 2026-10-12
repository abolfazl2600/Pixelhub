# V3 — گالری، عکس شخصی و آلفای آفلاین

نسخه پیشنهادی: v0.3.0 | وضعیت هدف: Offline Alpha | وابستگی: V2 و schema ثابت Level.

## هدف نسخه
اولین محصول کاربردی بدون سرور: انتخاب مرحله از گالری، واردکردن عکس شخصی، تبدیل به پیکسل‌های شماره‌دار، رنگ‌آمیزی و نگهداری آثار.

## داخل محدوده (Must Have)
- [ ] Home/Category/Gallery با دسته‌ها و تصاویر preview.
- [ ] In Progress، Completed و Favorites در My Gallery.
- [ ] حداقل چند ده تصویر قانونی و کنترل کیفی؛ هدف 80–120 برای آلفا.
- [ ] import عکس از File Picker اندروید و وب.
- [ ] در Android دسترسی گالری با روش مجاز و حداقل permission؛ در Web فایل محلی.
- [ ] crop، orientation، size validation، error states.
- [ ] pixelation و color quantization با پالت کنترل‌شده.
- [ ] difficulty preset (easy/normal/hard) و قبل از شروع preview.
- [ ] خروجی converter دقیقاً LevelDefinition نسخه V2 باشد.
- [ ] ذخیره آثار ساخته‌شده کاربر به‌صورت محلی و خصوصی.
- [ ] انتخاب و Resume آثار شخصی از My Gallery.
- [ ] Export تصویر تکمیل‌شده PNG و اشتراک‌گذاری با API مناسب پلتفرم.
- [ ] تنظیمات ابتدایی: صدا/لرزش در صورت استفاده، پاک‌کردن داده محلی، درباره.
- [ ] تست پردازش عکس سنگین و کنترل مصرف حافظه.

## خارج از محدوده
- آپلود اتوماتیک عکس به سرور یا انتشار عمومی عکس.
- Cloud Sync، ورود با Google و حساب مشترک.
- پنل محتوا و کاتالوگ آنلاین.
- پرداخت و تبلیغات، Daily Streak، Leaderboard.
- حذف پس‌زمینه مبتنی بر AI، تولید تصویر با Prompt.
- ابزارهای پردازش عکس نیازمند اشتراک به خدمات ابری.

## زیرساخت برای آینده
- user artwork دارای UUID، createdAt، original source local ref، converter params، level schema version.
- جداسازی public catalog artwork از private user artwork.
- عملیات private photo نباید بدون رضایت به network برود.
- با قابلیت Sync در V4، فقط Metadata و Progress تعیین‌شده همگام شود؛ آپلود عکس اصلی opt-in باشد.
- CatalogRepository طوری طراحی شود که بعدها API جای asset ثابت را بگیرد.

## ترتیب کار
1. ساخت catalog metadata و UI گالری.
2. Favorite/Completed/My Gallery با local storage.
3. Image input و crop.
4. Converter + preview + level validation.
5. بازی Level ساخته‌شده و ذخیره آن.
6. PNG export و platform sharing.
7. تست با نمونه عکس‌های متنوع و کنترل حجم/دقت/زمان.
8. تست آفلاین کامل.

## معیار پذیرش
- [ ] روی Android و Web عکس انتخاب شود و به مرحله قابل بازی تبدیل گردد.
- [ ] ورودی خیلی بزرگ یا نامعتبر crash نکند.
- [ ] عکس خصوصی بدون تعامل آگاهانه به سرور ارسال نشود.
- [ ] آثار بعد از restart محفوظ باشند.
- [ ] Gallery/Paint روی Web همان ساختار Android را داشته باشد.
- [ ] حالت Offline با تصاویر نصب‌شده فعال باشد.
- [ ] Assetهای منتشرشده سند منشأ/مجوز داشته باشند.

## انتقال به V4
بازی محلی و محتوای خصوصی باید قابلیت مهاجرت امن مهمان به حساب آنلاین داشته باشند؛ نباید داده‌های کاربر قدیمی در ورود از بین برود.
