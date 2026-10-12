# 12 | عملیات، پایش، اقتصاد و آینده محصول

## رویدادهای تحلیلی پیشنهادی
- app_open, home_view, artwork_open, coloring_start, coloring_progress_sampled, coloring_complete.
- import_started, import_completed, import_failed.
- sync_started, sync_succeeded, sync_failed, sync_conflict.
- reward_offered, reward_claimed, ad_reward_earned.
- purchase_started, purchase_verified, subscription_cancelled.
- post_submitted, post_approved, report_submitted, moderation_action.
هیچ رویدادی نباید عکس، متن خصوصی یا توکن احراز هویت را ارسال کند.

## KPIهای اصلی
- D1/D7/D30 retention؛ درصد بازگشت کاربران.
- Completion rate تصویر و اولین تصویر.
- Average session time و تعداد مراحل تکمیل‌شده به ازای کاربر.
- Photo import/conversion success و usage.
- Crash-free sessions/users و frame timing.
- Sync success، latency و conflict rate.
- Inventory consumption و reward grant errors.
- Purchase conversion، ARPDAU و churn اشتراک (V6).
- UGC report rate، moderator response time و removal rate (V7).

## هزینه‌ها
- V1–V3: GitHub Actions minutes/artifact retention و Pages static hosting؛ حد مجاز plan بررسی شود.
- V4: Host API، Managed PostgreSQL، Auth provider، Log/Monitoring.
- V5: Storage GB، CDN egress، Worker CPU/queue، backup retention.
- V6: Billing/payment fees، Ad platform، support، legal/compliance، content creation.
- V7: Moderation labor، UGC storage/traffic و anti-abuse tooling.
اعداد هزینه بدون DAU، حجم دانلود و فرض استفاده واقعی قابل اتکا نیستند.

## ظرفیت‌سنجی
- Content egress = active users * downloaded levels * mean bytes per level.
- API RPS = sessions * calls/session / active seconds (با Burst و p95).
- Storage growth = artwork count * file size + user assets + backups.
- Budget alert برای egress، request volume، DB storage و queue time.
- benchmark را پیش از خرید زیرساخت گران انجام دهید.

## چرخه انتشار
- هفت نسخه برنامه‌ریزی‌شده نقشه قابلیت‌اند، نه تاریخ اجباری.
- پس از هر نسخه، Bugs/Feedback/KPIها برنامه نسخه بعد را اصلاح کنند.
- به‌روزرسانی فایل مرحله منتشرشده درجا ممنوع.
- Rollout gradual برای Billing/UGC و قابلیت Kill Switch.
- SLA هدف، RTO/RPO و زمان‌بندی backup بعد از تعیین کاربران پرداخت‌کننده/حجم واقعی تصویب شود.

## معیار رفتن از فاز نمونه به محصول
V3 -> V4: هسته بازی پایدار و Storage محلی مطمئن.
V4 -> V5: Sync و Auth امن روی دو پلتفرم.
V5 -> V6: خط تولید محتوا قابل اتکا، SLA عملیاتی و License.
V6 -> V7: ظرفیت Moderation، پایش خطا، تیم پشتیبانی و سیاست عمومی.

## فرصت‌های توسعه بعد از V7 (نیاز به تصمیم مستقل)
- زبان‌های بیشتر و RTL کامل.
- نسخه iOS با همان Flutter codebase و تست مستقل.
- الگوریتم بهبود تبدیل عکس با segmentation و گزینه‌های حرفه‌ای.
- سیستم پیشنهادی محتوا با رعایت حریم خصوصی.
- Marketplace آثار با بررسی حقوق نشر، پرداخت و سن مخاطب.
- همکاری با هنرمندان و بسته‌های ویژه.
- قابلیت‌های Accessibility و ابزار طراحی آزاد.
