# V7 — Community، Moderation و رشد مقیاس‌پذیر

نسخه پیشنهادی: v1.1.0 | وضعیت هدف: Social Product Expansion | وابستگی: V6 و تیم عملیاتی محتوا.

## هدف نسخه
کاربران با رضایت خود آثار ساخته‌شده را عمومی کنند و جامعه محتوا شکل بگیرد؛ همراه با محافظت از حریم خصوصی، گزارش تخلف و نظارت واقعی.

## داخل محدوده (Must Have)
- [ ] پروفایل عمومی جدا از اطلاعات حساس حساب.
- [ ] انتشار اختیاری آثار، با visibility خصوصی به‌صورت پیش‌فرض.
- [ ] سازوکار رضایت صریح و اعلام حقوق اثر پیش از Publish.
- [ ] Gallery آثار عمومی با pagination و sorting کنترل‌شده.
- [ ] follow/unfollow، like/unlike، favorites آثار عمومی.
- [ ] امکان رنگ‌آمیزی آثار عمومی مجاز توسط دیگران.
- [ ] Report Artwork / Report User و علت گزارش.
- [ ] Block User و محدودکردن تعامل کاربر مسدودشده.
- [ ] صف Moderator و وضعیت‌های pending/approved/rejected/removed.
- [ ] ابزار Takedown سریع و appeal policy در صورت لزوم.
- [ ] سیستم تشخیص abuse، rate limits و audit logs.
- [ ] Content License/Ownership، deletion policy و پاسخ‌گویی حقوقی.
- [ ] اطلاع‌رسانی رویدادهای اجتماعی بدون افشای داده خصوصی.
- [ ] load test و CDN object lifecycle و کنترل هزینه.
- [ ] پشتیبانی از incident response و rollback/mute Community.
- [ ] داشبورد moderation volume/response time و گزارش رشد.

## خارج از محدوده
- پیام خصوصی آزاد و چت زنده (ریسک ایمنی بالاتر).
- انتشار تصویر خصوصی یا عکس اصلی بدون رضایت کاربر.
- آزادکردن خودکار همه تصاویر بدون بازبینی و ابزار گزارش.
- شبکه اجتماعی عمومی با ویدئو/لایو/موقعیت مکانی.
- سیستم کسب درآمد سازندگان یا Marketplace بدون طرح حقوقی و مالی جداگانه.
- بازطراحی Desktop؛ وب همچنان همان UI موبایل است.

## زیرساخت و مقیاس
- جداول user_public_profiles, posts, follows, likes, reports, blocks, moderation_actions.
- Storage جداگانه assets خصوصی و محتوای عمومی تأییدشده.
- Queue انتشار و job پردازش فایل.
- CDN برای رسانه عمومی و strict access برای اصل خصوصی.
- Spam throttling، quota روزانه و safety review.
- مدیریت lifecycle حذف محتوا از CDN/cache.
- Event analytics تجمیعی و dashboard نرخ گزارش و Abuse.

## ترتیب کار
1. سیاست جامعه، سن مخاطب و منشور Moderation.
2. مدل داده و AuthZ پروفایل عمومی و انتشار.
3. Upload flow امن و preview با privacy default.
4. Report/Block و پنل Moderator **قبل از روشن‌کردن** Community.
5. انتشار محدود invitation-only و رسیدگی عملی گزارش‌ها.
6. Feed عمومی و Follow/Like.
7. سنجش latency، گزارش‌های تخلف و هزینه Storage.
8. rollout تدریجی و تهیه برنامه تکامل V8+.

## معیار پذیرش
- [ ] قابلیت گزارش و مسدودسازی پیش از Public Posts فعال باشد.
- [ ] کاربر نتواند به فایل خصوصی کاربر دیگر دسترسی بگیرد.
- [ ] حذف اثر عمومی از اپ و storage/CDN طبق policy اجرایی شود.
- [ ] Moderator گزارش را مشاهده و اقدام قابل ثبت انجام دهد.
- [ ] کاربر نقض‌کننده محدود شود؛ Abuse API قابل پایش باشد.
- [ ] زمان پاسخ Moderation قابل گزارش باشد.
- [ ] Android/Web UI و عملکرد اصلی رنگ‌آمیزی همچنان یکسان بمانند.
- [ ] در صورت رخداد امنیتی بتوان کل بخش UGC را با kill switch غیرفعال کرد.

## پس از V7، اولویت‌های تحقیق
پیشنهادگر شخصی‌سازی‌شده، Localization گسترده، ویژگی‌های پیشرفته ویرایش عکس، ابزار تولید آثار برای سازندگان، برنامه افزایش محتوا و توسعه iOS فقط با تصویب Scope مستقل.
