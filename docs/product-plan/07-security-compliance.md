# 07 | امنیت، حریم خصوصی، انطباق و عملیات

## مدل تهدید فازبه‌فاز
- V1–V3: فایل عکس واردشده، داده محلی، خروجی Build و وابستگی‌های ثالث.
- V4: اطلاعات حساب، نشست‌ها، Access Control، Cloud Sync و backup.
- V5: Admin privileged access، upload pipeline، Object Storage و publish.
- V6: پرداخت، تبلیغات، Billing fraud، اشتراک و قوانین فروشگاه.
- V7: UGC عمومی، حقوق نشر، آزار/محتوای نامناسب و abuse.

## حریم خصوصی پیش‌فرض
- بازی مهمان و پردازش عکس بدون ثبت‌نام ممکن باشد.
- اصل کمینه‌سازی اطلاعات جمع‌آوری‌شده.
- عکس شخصی به طور پیش‌فرض روی سرور ارسال نشود.
- Analytics نباید تصویر یا متن خصوصی کاربر را ثبت کند.
- Policy و Consent واضح پیش از جمع‌آوری اختیاری اطلاعات.
- حذف حساب و درخواست حذف داده در فاز ثبت‌نام طراحی شود.
- حق دسترسی کاربر به داده و زمان نگهداری مطابق بازار هدف مشخص شود.

## کنترل‌های فنی
- HTTPS برای همه APIها و فایل خصوصی.
- RBAC/ABAC روی Admin و داده کاربر، MFA اجباری برای مدیران.
- اعتبارسنجی MIME و magic bytes؛ سقف حجم/ابعاد/زمان decode تصویر.
- محدودسازی نرخ API و anti-abuse.
- Sanitization/validation تمامی ورودی‌ها.
- Secret scanning و Dependency scanning در CI.
- نگهداری رمزها/کلیدها در secrets manager و rotation.
- Security headers/CORS محدود، cookie/session strategy مناسب وب.
- Logging بدون توکن، رمز و اطلاعات خصوصی.
- encryption at rest بسته به زیرساخت و طبقه‌بندی داده، و backup encrypted.
- Idempotency در Pay/Reward/Sync، authorization در Server.
- Audit log تغییرات پنل و توان freeze کردن حساب‌های مشکوک.

## مشخصات تأیید پرداخت V6
- کلاینت صرفاً Token/Receipt ارسال می‌کند.
- Backend از کانال معتبر store آن را اعتبارسنجی و وضعیت entitlement را تعیین می‌کند.
- Renew/Cancel/Refund/Restore باید به شکل idempotent پردازش شوند.
- entitlement در API مشترک برای Android و Web قابل دریافت باشد.
- اتصال پرداخت بیرونی از اپ اندروید تنها پس از بررسی دقیق سیاست‌های Google Play و برنامه‌های مجاز منطقه‌ای.
- Marketplace target، taxes/refund/support از پیش تعیین شوند.

## الزامات UGC V7
- قواعد انتشار و مالکیت آثار.
- Report محتوا و کاربر، Block کاربر.
- Queue بازبینی انسانی و امکان Takedown فوری.
- جلوگیری از انتشار عمومی پیش از آماده‌شدن Moderation.
- حفاظت از عکس کودکان و کنترل مخاطب هدف مطابق سیاست فروشگاه.
- مستندسازی مراحل رسیدگی، Appeal در صورت لزوم و retention policy.

## عملیات Production
- Health check، alert و metrics برای API، database، worker و Sync.
- پشتیبان‌گیری روزانه یا مطابق RPO هدف؛ اجرای restore drill.
- RTO/RPO را پیش از ورود کاربران پولی تصویب کنید.
- دکمه خاموشی (kill switch) برای انتشار UGC، فروشگاه و تبلیغات در Remote Config.
- Incident response: ارزیابی، مهار، اعلان مقتضی، بازیابی و postmortem.
- Account deletion حتی بعد از تعلیق حساب قابل بررسی و پیگیری باشد.

## چک‌لیست رسمی انتشار
- Privacy Policy عمومی با دامنه پایدار.
- Data Safety و Content Rating مطابق رفتار واقعی برنامه.
- Target API، App Bundle، Store listing و signing مطابق سیاست زمان ارسال.
- Billing library معتبر و تست sandbox.
- اگر ثبت‌نام وجود دارد، امکان حذف حساب داخل اپ و مسیر وب مربوط.
- اگر کودکان در بازار هدف هستند، Families/Ads/Privacy requirements بررسی شود.
- بررسی دوره‌ای؛ سیاست‌ها ممکن است تغییر کنند.

## مراجع رسمی
- https://support.google.com/googleplay/android-developer/
- https://developer.android.com/google/play/billing
- https://docs.flutter.dev/deployment/android
- https://owasp.org/www-project-mobile-app-security/
