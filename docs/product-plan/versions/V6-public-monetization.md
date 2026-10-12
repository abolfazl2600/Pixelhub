# V6 — انتشار عمومی، تعامل و درآمدزایی مسئولانه

نسخه پیشنهادی: v1.0.0 | وضعیت هدف: Public Release | وابستگی: V5 و تصمیم بازار/رده سنی.

## هدف نسخه
Pixelhub به محصول قابل انتشار عمومی Android و Web تبدیل شود؛ ابزارهای کمکی، چالش و درآمدزایی قابل کنترل داشته باشد بدون اینکه نقاشی را با تبلیغات اجباری قطع کند.

## داخل محدوده (Must Have)
- [ ] Polish کامل Home/Gallery/Paint/Profile و Onboarding کاربر تازه.
- [ ] 200–300 سطح دارای مجوز، با دسته‌بندی و درجه سختی متعادل (هدف اولیه).
- [ ] Hint، Bomb، inventory و قوانین استفاده.
- [ ] Daily Challenge و streak/reward mechanics با تنظیمات Server.
- [ ] Wallet ledger تراکنش‌محور در صورت وجود سکه.
- [ ] اشتراک/آیتم دیجیتال در Android با Google Play Billing معتبر.
- [ ] backend purchase verification و entitlement مشترک.
- [ ] فروشگاه وب از درگاه مجاز منطقه هدف و API مشترک entitlement (در صورت وجود پرداخت وب).
- [ ] restore، refund/cancel، expired subscription handling.
- [ ] rewarded ads اختیاری Android و limit/frequency config.
- [ ] عدم نمایش Interstitial اجباری در میانه Paint.
- [ ] Remote feature flags / emergency disable Ads/Shop.
- [ ] Consent flow و Privacy/Data Safety/Content Rating و account deletion.
- [ ] Crash reporting و analytics retention/conversion/privacy-conscious.
- [ ] Store Listing، icon، screenshots، AAB امضاشده و test tracks.
- [ ] Production release runbook و پشتیبانی کاربر.
- [ ] performance/battery/memory baseline و تست بازار هدف.
- [ ] rollout تدریجی، مانیتور خطا و rollback plan.

## خارج از محدوده
- آثار عمومی کاربران، Follow، Like، Comment و Feed.
- پیام‌رسانی، Real-time PvP و Leaderboard جهانی.
- نمایش تبلیغات اجباری هنگام اجرای رنگ‌آمیزی.
- انتشار در iOS یا ساخت UI دسکتاپ.
- ادعای این‌که خرید وب لزوماً از داخل Android قابل لینک‌دهی است؛ policy باید جدا بررسی شود.

## ترتیب کار
1. تعیین سن/کشورهای هدف و فروشگاه‌های موردنظر.
2. مرور جدیدترین قواعد Play و Billing، انتخاب Merchant setup.
3. Reward/Inventory backend و UI.
4. Billing verification و purchase state machine.
5. Ads rewarded و kill switches، با تست بدون مزاحمت.
6. صفحه‌های Terms/Privacy/Delete/Support و Data Safety.
7. QA خرید/Refund/Restore، battery و crash.
8. Play Console internal/closed testing متناسب حساب و شرایط روز.
9. انتشار Web و AAB اندروید با Version/Tag ثبت‌شده.
10. پایش واقعی KPIها و رفع مشکلات.

## معیار پذیرش
- [ ] نقاشی بدون پرداخت یا تبلیغ اجباری وسط session کار کند.
- [ ] خرید ناموفق دسترسی Premium ایجاد نکند.
- [ ] خرید موفق قابل Restore باشد و لغو/Refund به Entitlement صحیح منجر شود.
- [ ] وب و Android وضعیت اشتراک را مطابق سیاست‌های فروشگاه به‌درستی نمایش دهند.
- [ ] حذف حساب، privacy و data disclosure مطابق رفتار واقعی باشند.
- [ ] AAB امضاشده ساخته و Play Console بدون نقص مسدودکننده بررسی شود (تأیید نهایی فروشگاه وابسته به Google است).
- [ ] شاخص‌های Crash، Retention، Completion و Sync واقعاً ثبت و بررسی شوند.
- [ ] طرح پشتیبانی و پاسخ‌گویی به کاربران فعال باشد.

## انتقال به V7
فقط پس از وجود ثبات محصول، ظرفیت Moderation و معیارهای عملکرد، قابلیت انتشار عمومی کاربران را فعال کنیم.
