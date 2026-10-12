# 04 | CI/CD و Build بدون نصب ابزار توسعه روی رایانه

## هدف عملی
از اولین نسخه فنی، GitHub Actions روی runner ابری Flutter/Android SDK را نصب و Web و APK را تولید کند. این کار نیاز به نصب SDK روی سیستم کاربر را حذف می‌کند؛ ولی نوشتن کد، مرور خطاهای CI و تست روی گوشی واقعی همچنان ضروری است.

## جریان شعبه‌ها و انتشار
- main: نسخه پایدار، هر تغییر با PR و CI پاس‌شده.
- feature/*: هر قابلیت/اصلاح به‌صورت مستقل.
- release/*: فقط در صورت نیاز به تثبیت نسخه عمومی.
- tag: v0.1.0, v0.2.0, v0.3.0, v0.4.0, v0.5.0, v1.0.0, v1.1.0.
- Android APK و Web در یک Workflow با همان commit ساخته شوند.
- فایل APK مستقیماً روی GitHub Pages ساخته نمی‌شود؛ به عنوان Actions Artifact یا GitHub Release عرضه می‌شود.

## Workflowهای هدف
1. ci.yml: format، analyze، unit tests، contract tests، build smoke Android/Web روی Pull Request.
2. web-pages.yml: build Flutter Web با base href مناسب، upload artifact، deploy GitHub Pages پس از merge main.
3. android-build.yml: تولید APK آزمایشی برای هر tag/release یا push منتخب؛ ذخیره Artifact.
4. android-release.yml (V6): امضای Release APK/AAB با Secrets و تأیید دستی/محیط محافظت‌شده.
5. security.yml: بررسی dependency و اسکن secrets؛ اگر ابزار مناسب در دسترس باشد.

## نمونه فرمان‌های Build برای اجرا توسط Runner
~~~
flutter pub get
flutter analyze
flutter test
flutter build web --release --base-href /Pixelhub/
flutter build apk --release
flutter build appbundle --release
~~~
فرمان‌های فوق با ساختار پروژه و signing واقعی سازگار خواهند شد؛ در V1، فقط Web و APK آزمایشی هدف هستند؛ AAB امضاشده در V6.

## GitHub Pages
- نشانی پیش‌بینی‌شده پس از فعال‌سازی: https://abolfazl2600.github.io/Pixelhub/
- Pages با source=GitHub Actions؛ دسترسی pages:write و id-token:write برای job نشر.
- index.html یا Flutter base href باید /Pixelhub/ باشد.
- برای جلوگیری از 404 Refresh مسیرهای SPA، در نسخه استاتیک Hash URLs در نظر گرفته شود.
- فایل‌های وب استاتیک را Pages میزبانی می‌کند؛ Auth/API/پرداخت/DB نه.
- برای دامنه اختصاصی بعداً CNAME و base href و HTTPS بازبینی شوند.
- GitHub Pages فقط پس از ساخت پروژه Flutter و تنظیم Actions واقعاً فعال می‌شود.

## امنیت امضای Android
- ساخت debug/internal APK بدون کلید انتشار ممکن است؛ این خروجی آماده Play Store نیست.
- upload keystore برای V6 در محیط امن ساخته و پشتیبان‌گیری شود.
- فقط secrets رمزگذاری‌شده GitHub و Protected Environment، نه commit فایل JKS.
- مجوز اجرا/انتشار محدود؛ کلیدهای غیرضروری در CI قرار نگیرند.
- نصب روی گوشی واقعی برای سنجش نسخه نهایی ضروری است.
- release AAB برای Play Console؛ APK برای آزمون جانبی/انتشار مستقیم.

## سیاست شکست Build
- هر PR که lint/test/build را fail کند نباید Merge شود.
- Artifactها باید نام شامل version و commit داشته باشند.
- هر Build شکست‌خورده خطای قابل ردیابی دارد و قبل از رفتن نسخه بعد رفع می‌شود.
- نسخه production قبلی در صورت شکست deploy سالم بماند.
- پس از فعال‌سازی Backend، deploy آن مستقل از Pages و با Staging+health check انجام شود.

## چک‌لیست راه‌اندازی به‌ترتیب
- [ ] ساخت apps/game با flutter create و Target Android/Web.
- [ ] ثبت نسخه Flutter در CI (پین نسخه).
- [ ] اجرای format/analyze/test.
- [ ] ایجاد Workflow وب با build و base-href.
- [ ] فعال‌سازی Settings > Pages > Build and deployment > GitHub Actions.
- [ ] فعال‌سازی permissions موردنیاز و Environment.
- [ ] ایجاد Workflow APK آزمایشی و آپلود Artifact.
- [ ] دریافت APK و نصب روی گوشی واقعی.
- [ ] تست لینک وب و بازکردن مجدد صفحه پس از refresh.
- [ ] برای V6: کلید امضا، AAB، Google Play testing و rollout.

## منابع رسمی و مرجع اجرایی
- https://docs.flutter.dev/deployment/web
- https://docs.flutter.dev/deployment/android
- https://docs.flutter.dev/ui/navigation/url-strategies
- https://docs.github.com/en/pages
- https://github.com/actions/deploy-pages
