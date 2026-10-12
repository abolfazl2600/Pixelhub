# 10 | مشخصات صفحات و یکسانی Android / Web

## قرارداد بصری ثابت
- Flutter Widgets و Design System کاملاً مشترک.
- قاب بازی در دسکتاپ وب وسط‌چین، maxLogicalWidth حدود 430 و عرض معمول 390؛ حالت UI دسکتاپ جدا ندارد.
- در گوشی‌های کوچک تا عرض 360، اندازه‌ها باید بدون clipping کار کنند؛ قاب ثابت به معنی overflow عمدی نیست.
- Safe Area، scroll و صفحه‌کلید مجازی نیازمند تطبیق ارتفاع/Insets هستند، نه ساخت layout تازه.
- Input touch/pinch در گوشی و pointer/click/wheel در دسکتاپ با رفتار معادل.
- Loading، Empty، Error، Offline، Permission Denied و Retry برای تمام صفحه‌های داده‌دار طراحی شوند.
- تایپوگرافی، اندازه تاچ تارگت‌ها، contrast و دسترس‌پذیری باید آزموده شوند.

## فهرست صفحه‌ها و نخستین نسخه
| صفحه | نخستین نسخه | رفتار اصلی |
|---|---|---|
| Splash / Bootstrap | V1 | بارگذاری config محلی |
| Home Shell | V1 | شروع/گالری نمونه |
| Painting Canvas | V2 | رنگ، پالت، زوم، ذخیره |
| Completion | V2 | نتیجه و بازگشت |
| Categories / Gallery | V3 | browse/filter محلی |
| Artwork Detail | V3 | preview و شروع |
| My Gallery | V3 | نیمه‌کاره/تکمیل‌شده |
| Photo Picker / Crop | V3 | انتخاب و برش |
| Pixelation Preview | V3 | سختی، رنگ و شروع |
| Settings | V3 | داده محلی و تنظیمات |
| Login / Register | V4 | ایمیل/Google |
| Profile / Sync Status | V4 | حساب و همگام‌سازی |
| Account Deletion | V4 | حذف داده کاربر |
| Search / Online catalog | V5 | جستجوی محتوای پویا |
| Daily Challenge | V6 | مأموریت روزانه |
| Rewards / Inventory | V6 | ابزار و پاداش |
| Shop / Premium | V6 | خرید و اشتراک |
| Privacy / Support | V6 | رضایت، پشتیبانی |
| Community Feed | V7 | محتواهای عمومی |
| Public Profile | V7 | آثار و دنبال‌کردن |
| Publish / Report / Block | V7 | ابزار ایمنی اجتماعی |

## جریان‌های ضروری
1. First-time: Launch -> Home -> Select level -> Tutorial overlay -> Paint -> Complete -> Next suggestion.
2. Returning: Home -> In progress -> Resume painting -> Complete.
3. Custom: Home -> Import -> Crop -> Pick difficulty -> Preview -> Paint -> Save private.
4. Cross-device V4: Guest -> Account -> Confirm merge -> Sync -> Open same account on Web.
5. Commerce V6: Reward choice -> explicit rewarded ad or shop -> verify -> entitlement.
6. UGC V7: Private artwork -> publish choice -> check license/consent -> moderation -> public.

## صفحه Painting — Layout
- Top: بازگشت، عنوان/درصد و دسترسی تنظیمات.
- Main: Canvas قابل بزرگ‌نمایی، بدون عنصر پوشاننده روی خانه‌ها.
- Bottom: پالت افقی شماره‌دار؛ وضعیت رنگ فعلی و شمارنده؛ دسترسی Undo/Hint.
- Zoom/Pan با no accidental paint در mode navigation.
- Completed state و continuation به My Gallery بدون از دست دادن وضعیت.

## Empty/error states
- No pictures: empty state با راه‌حل.
- Missing local asset: retry یا بازگشت به گالری.
- Offline remote catalog: cached items + message.
- Storage full: هشدار و جلوگیری از حذف progress موجود.
- Login failed: error قابل فهم بدون نمایش داده محرمانه.
- Converter failed: عکس ورودی و تغییرات حفظ شود؛ retry.
- Payment fail: توضیح و عدم اعطای خرید.
- Moderation pending: وضعیت انتشار معلوم باشد.

## کیفیت تجربه
- اولین تصویر کوتاه و دارای رنگ‌های محدود باشد.
- هیچ popup تبلیغاتی اجباری وسط Paint نمایش داده نشود.
- برنامه به‌صورت پیش‌فرض بدون Account شروع شود.
- همه Screenها باید Golden/Widget test در حد قابلیت نسخه داشته باشند.
- اگر طراحی صفحه جدید به desktop-specific mode نیاز داشت، با تصمیم محصول تعارض دارد و باید رد یا در ADR بررسی شود.
