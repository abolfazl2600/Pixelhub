# 08 | فرایند توسعه با هوش مصنوعی روی GitHub

## مدل انجام کار
مالک محصول نیازی به آشنایی اولیه با Flutter ندارد؛ AI کمک می‌کند فایل‌ها را بسازد و خطاهای CI را رفع کند. بااین‌حال AI نمی‌تواند با ادعای «کد آماده است» جای تست واقعی را بگیرد. هر قابلیت باید یک Issue کوچک، PR/Commit، تست و معیار پذیرش داشته باشد.

## قواعد اجرای یک Task
1. از پرونده نسخه، یک قابلیت محدود و مشخص انتخاب شود.
2. معیار پذیرش، تست‌های لازم و فایل‌های درگیر پیش از کدنویسی تعیین شوند.
3. فقط حداقل کد برای قابلیت اضافه شود؛ refactor بزرگ هم‌زمان ممنوع.
4. Code Review از منظر security، performance، offline و web/android parity.
5. GitHub Actions: format / analyze / test / build.
6. بررسی خروجی وب و نصب APK در صورت تغییر UI/Android.
7. Merge به main فقط پس از عبور آزمون‌ها.
8. Update سند همان نسخه، Known Issues و Changelog.

## قالب دستور برای AI Coder
~~~
Project: Pixelhub
Version: [V1..V7]
Task: [عنوان واضح]
Scope: [رفتار دقیق داخل محدوده]
Not in scope: [چیزهایی که نباید تغییر کنند]
Files/Modules: [مسیرهای مجاز]
Acceptance criteria: [سناریوهای قابل آزمون]
Tests required: [unit/widget/integration/manual]
Android-Web parity: [رفتار یکسان یا adapter تفاوت‌دار]
Security and privacy: [داده کاربر/دسترسی]
Deliverable: PR + explanation + CI result + screenshots/logs if possible.
~~~

## قواعد ضد خطا
- AI نباید فایل secrets، کلید امضا یا credential را تولید/commit کند.
- قابلیت آینده را به بهانه «آماده‌سازی زیرساخت» فعال نکند؛ Interface و migration کافی است.
- هنگام خطای CI به جای خاموش‌کردن تست، علت را اصلاح کند.
- در تغییر Level schema، Migration test بنویسد.
- وابستگی‌های جدید باید علت، نسخه سازگار و License داشته باشند.
- بدون اجازه، Force Push یا حذف داده واقعی کاربران انجام ندهد.
- تغییر Design System باید Golden Test یا مرور بصری داشته باشد.
- از انتشار عمومی اطلاعات خصوصی در Logs خودداری کند.
- Commitهای کوچک و معنادار، نه یک PR ده‌هاهزار خطی.

## فرم Issue برای هر قابلیت
- Goal / User story
- Why now (نسخه)
- Preconditions
- Functional requirements
- Non-functional requirements
- Explicit exclusions
- Acceptance tests
- Dependencies
- Risk + rollback
- Definition of Done

## مدیریت تصمیم‌های معماری
برای هر تصمیم حساس، یک ADR اضافه شود:
- Context: چه مسئله‌ای وجود دارد.
- Options: گزینه‌ها و tradeoff.
- Decision: انتخاب و دلیل.
- Consequences: هزینه، ریسک و شرایط بازنگری.
- تاریخ و نسخه نخستین استفاده.

## روش توسعه با کمترین نصب محلی
- GitHub Codespaces یا ویرایشگر ابری و اتصال Agent در صورت دسترس بودن.
- GitHub Actions روی runner ابزار Flutter/Android را نصب می‌کند.
- وب روی Pages اجرا می‌شود.
- APK از Artifact/Release گرفته می‌شود و روی Android تست دستی می‌گیرد.
- برای تست پیچیده Emulator لازم است runner/خدمت تست یا فردی که به دستگاه دسترسی دارد سناریو را اجرا کند.

## وضعیت‌گذاری کارها
Backlog -> Ready -> In progress -> In review -> CI passed -> Manually verified -> Done.
«CI passed» معادل «Manually verified» نیست.

## ممنوعیت عبور زودهنگام
تا وقتی Release Gate نسخه فعلی انجام نشده، ورژن بعدی شروع نشود؛ تنها تحقیق فنی موازی که وابستگی مستقیم ندارد مجاز است.
