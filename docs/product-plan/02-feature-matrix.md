# 02 | ماتریس امکانات و زمان ورود

راهنما: هر قابلیت «اولین نسخه‌ای» دارد که باید در آن کامل و تست شود؛ نسخه‌های بعد آن را حفظ و توسعه می‌دهند. علامت — یعنی عمداً در آن نسخه ارائه نمی‌شود.

| حوزه | قابلیت | اولین نسخه | توضیح / شرط |
|---|---|---|---|
| زیرساخت | پروژه Flutter با خروجی Android + Web | V1 | یک Codebase |
| زیرساخت | GitHub Actions ساخت Web و APK | V1 | بدون IDE محلی |
| زیرساخت | نشر Web روی GitHub Pages | V1 | Static hosting |
| UI | قاب واحد موبایل در مرورگر دسکتاپ | V1 | بدون طراحی دو حالته |
| UI | Design system و Splash/Home mock | V1 | قاب و مسیر اصلی |
| کیفیت | Lint، Unit smoke و Build gate | V1 | شرط Merge |
| Paint | خواندن Level schema نسخه‌دار | V2 | immutable levels |
| Paint | شماره‌ خانه‌ها و انتخاب پالت | V2 | واضح و خوانا |
| Paint | Tap و Drag رنگ‌آمیزی | V2 | جلوگیری از خانه غلط |
| Paint | Zoom و Pan | V2 | Pointer/Touch |
| Paint | Highlight رنگ، پیشرفت، Finish | V2 | deterministic |
| Paint | Undo، Reset و Resume | V2 | Local storage |
| Offline | نقاشی آفلاین مراحل نصب‌شده | V2 | بدون شبکه |
| Gallery | کاتالوگ دسته‌بندی‌شده محلی | V3 | حداکثر حجم قابل کنترل |
| Gallery | Completed/In-progress/Favorites | V3 | local |
| Photo | واردکردن فایل و Crop | V3 | Android & Web |
| Photo | کاهش رنگ و ساخت Level شماره‌دار | V3 | client-side |
| Photo | انتخاب درجه سختی و Preview | V3 | همان Level schema |
| Sharing | Export PNG/Share | V3 | بسته به پلتفرم |
| Account | Guest -> Account migration | V4 | بی‌اتلاف داده |
| Account | Email/Google login | V4 | provider قابل تعویض |
| Sync | Cloud progress و تداخل دو دستگاه | V4 | conflict policy |
| Backend | REST v1، Postgres، Auth و Monitoring | V4 | با Staging |
| Catalog | کاتالوگ پویا از API + CDN | V5 | cached offline |
| Admin | آپلود/تبدیل/تأیید/انتشار اثر | V5 | Draft/Published |
| Ops | scheduled publish و rollback | V5 | version immutable |
| Content | 200–300 محتوای مجاز پیش از انتشار عمومی | V6 | هدف محصولی |
| Engagement | Streak / daily challenge / Hint / Bomb | V6 | inventory ledger |
| Payments | Android Billing + سرور verify | V6 | فقط مطابق policy |
| Payments | Web checkout + entitlement مشترک | V6 | طبق قوانین بازار |
| Ads | rewarded ads اختیاری اندروید | V6 | بدون قطع Paint |
| Compliance | privacy, delete, rating, store listing | V6 | قبل از عمومی |
| Telemetry | crash, retention, conversion, sync success | V4–V6 | بدون اطلاعات حساس |
| Social | انتشار آثار عمومی با رضایت | V7 | privacy default |
| Social | follow/like/public profiles | V7 | moderation ready |
| Social | report/block/takedown/moderator UI | V7 | قبل از UGC عمومی |
| Growth | A/B test, ranking, feature flags | V7 | با guardrails |
| Scale | queueing, CDN optimization, load test | V5–V7 | براساس داده |

## امکاناتی که فعلاً تعهد نسخه ندارند
- هوش مصنوعی مولد اختصاصی عکس، Marketplace آثار، پیام خصوصی، رقابت زنده، NFT، سیستم پیچیده اقتصاد، نسخه iOS.
- آنالیز شخصی‌سازی بسیار پیشرفته، رقابت چندنفره بلادرنگ، اشتراک‌گذاری داده به‌صورت عمومی.
برای اضافه‌کردن این‌ها پس از V7، سند Change Request و اثر روی حریم خصوصی/سرور الزامی است.

## مرزهای مهم
- V1 فقط اسکلت build است، نباید آن را «بازی کامل» معرفی کرد.
- V2 موتور Paint قابل بازی دارد، نه تبدیل عکس و نه حساب آنلاین.
- V3 یک اپ آفلاین نسبتاً کامل است، اما Cloud Sync و Admin آنلاین ندارد.
- V4 همگام‌سازی دارد، اما موتور انتشار محتوا و فروشگاه ندارد.
- V5 پنل و محتوای آنلاین دارد، اما پرداخت و جامعه کاربران عمومی ندارد.
- V6 انتشار عمومی امن با درآمدزایی است، اما Feed/Follow/Comments ندارد.
- V7 تنها زمانی UGC را فعال می‌کند که Moderation واقعاً آماده باشد.

## سیاست نگهداری قابلیت‌ها
- هر قابلیت جدید با Feature Flag و Migration Plan ارائه شود.
- در تغییر schema، خواندن نسخه‌های قدیمی تا حد نیاز داده موجود حمایت شود.
- قابلیت‌هایی که به سرور نیاز دارند، در حالت Offline پیام مناسب نشان دهند؛ رنگ‌آمیزی محلی متوقف نشود.
- Entitlement حساب نباید صرفاً در حافظه دستگاه منبع حقیقت باشد.
