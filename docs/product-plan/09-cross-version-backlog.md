# 09 | Backlog فرابخشی و تصمیم‌های قابل پیگیری

## اولویت بحرانی (ابتدا)
- [ ] انتخاب نام پکیج اندروید و سیاست تغییرناپذیر آن پیش از Release.
- [ ] نسخه Flutter در runner قفل شود.
- [ ] Game schema v1 و پیشرفت Bitset قرارداد مشخص داشته باشند.
- [ ] GitHub Pages و APK خروجی پایدار هر commit داشته باشند.
- [ ] تصاویر نمونه با License ثبت‌شده تهیه شوند.
- [ ] تست دو پلتفرم به معیار تحویل تبدیل شود.
- [ ] حفظ پیشرفت و سازگاری نسخه‌ها از V2 تست شود.

## اولویت بالا (قبل از آنلاین‌شدن)
- [ ] انتخاب Auth provider با ADR.
- [ ] انتخاب local storage compatible Android/Web.
- [ ] مدل API و conflict resolution formalized.
- [ ] سیاست Delete/Export account و backup.
- [ ] انتخاب region سرویس ابری و برآورد هزینه.
- [ ] سازوکار CDN asset versioning و offline cache.
- [ ] قرارداد purchase entitlement و token verification.

## پس از انتشار
- [ ] معماری Event pipeline و privacy-aware analytics.
- [ ] Feature flags + remote kill switches.
- [ ] Content moderation operation handbook.
- [ ] Load/cost dashboards و alerting.
- [ ] A/B testing تنها پس از وجود شاخص معنادار.
- [ ] برنامه انتشار محتوا و نرخ تولید ماهانه.

## تصمیم‌های باز و مالک تصمیم
| موضوع | زمان تعیین | معیار انتخاب |
|---|---|---|
| State management | V1 | تست‌پذیری و سادگی |
| Local DB | V1/V2 | Android/Web persistence |
| Painting renderer | V2 | benchmark روی دستگاه و مرورگر |
| Conversion algorithm | V3 | خروجی زیبا در زمان قابل‌قبول |
| Auth Provider | قبل V4 | امنیت، هزینه، دسترسی بازار |
| Hosting Backend | قبل V4 | Region، cost، backup، SLA |
| Admin framework | V5 | سرعت توسعه + RBAC |
| Payment web | قبل V6 | بازار هدف و compliance |
| Target audience | قبل V6 | content policy + Ads |
| Moderation plan | قبل V7 | ظرفیت عملیاتی و زمان پاسخ |

## Debt policy
فقط بدهی فنی ثبت‌شده پذیرفته شود: توضیح، مالک، شدت، نسخه تسویه و تست جلوگیری از بازگشت. بدهی مربوط به ازبین‌رفتن داده کاربر، کلیدهای امنیتی یا کنترل پرداخت اجازه تعویق ندارد.

## تغییر Scope
افزودن قابلیت جدید به هر نسخه باید این پرسش‌ها را پاسخ دهد:
1. آیا به هدف همان نسخه کمک می‌کند؟
2. چه بخش‌هایی را متاثر می‌کند؟
3. آیا تست، هزینه و ریسک مشخص است؟
4. چه چیزی به نسخه بعد منتقل می‌شود تا زمان‌بندی ثابت بماند؟
5. آیا Android و Web هر دو پشتیبانی می‌شوند؟

تعیین تاریخ، هزینه و تعداد نفرات فقط پس از محاسبه ظرفیت واقعی تیم انجام شود.
