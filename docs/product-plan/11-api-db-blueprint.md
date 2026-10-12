# 11 | طرح اولیه API، دیتابیس و قراردادهای عمومی

## زمان فعال‌شدن
V1–V3: API اجرا نمی‌شود؛ فقط مدل‌ها و interfaceهای قابل توسعه.
V4: Auth، Users، Progress Sync.
V5: Catalog، Levels، Storage و Admin.
V6: Reward/Entitlements/Billing.
V7: Community/Moderation.

## قرارداد API اولیه (نمونه پیشنهادی، هنوز پیاده‌سازی نشده)
~~~
GET    /api/v1/health
POST   /api/v1/auth/session
GET    /api/v1/me
PATCH  /api/v1/me
DELETE /api/v1/me
GET    /api/v1/me/progress
GET    /api/v1/me/progress/:levelId
POST   /api/v1/me/progress/sync
GET    /api/v1/catalog
GET    /api/v1/catalog/categories
GET    /api/v1/levels/:levelId
GET    /api/v1/me/entitlements
POST   /api/v1/purchases/verify
GET    /api/v1/me/wallet
POST   /api/v1/rewards/claim
POST   /api/v1/community/posts
GET    /api/v1/community/posts
POST   /api/v1/community/reports
POST   /api/v1/community/blocks
~~~

## قواعد API
- JSON برای metadata؛ فایل سطح بزرگ از CDN/Storage دانلود شود.
- نسخه‌دار: /api/v1؛ OpenAPI قرارداد رسمی بین Flutter و NestJS باشد.
- Authorization از JWT/session معتبر استخراج شود، نه userId دلخواه ورودی.
- pagination و rate-limit برای list، create و write.
- idempotency برای sync operations، purchase، rewards.
- Error format ثابت با code/message/trace-id بدون افشای اطلاعات حساس.
- API نباید برای رنگ‌کردن هر خانه فراخوانی شود؛ sync batch/aggregate کافی است.

## طراحی جدول‌ها بر حسب نسخه
V4:
- users(id, status, created_at, deleted_at)
- user_profiles(user_id, nickname, avatar_ref)
- user_identities(user_id, provider, provider_subject)
- user_devices(id, user_id, last_seen)
- user_progress(user_id, level_id, level_version, generation, revision, bitset, updated_at)
- sync_operations(idempotency_key, user_id, received_at, status)

V5:
- categories(id, slug, display_name, sort_order)
- artworks(id, title, source_license, artist, visibility)
- artwork_versions(artwork_id, version, content_hash, asset_key, thumbnail_key)
- levels(id, artwork_version_id, width, height, difficulty, palette_size)
- packs(id, title, visibility), pack_items(pack_id, artwork_id)
- content_jobs(id, status, error_code), admin_audit_logs(id, actor_id, action, resource)
- publish_schedule(id, artwork_version_id, publish_at, status)

V6:
- products(id, store_product_id, platform, type)
- purchases(id, user_id, platform, provider_purchase_id, state)
- subscriptions(id, user_id, product_id, status, expires_at)
- entitlements(id, user_id, entitlement_key, active_until)
- wallet_transactions(id, user_id, event_key, delta, reason)
- inventories(user_id, item_id, quantity)
- challenges(id, active_from, active_until), user_challenges(user_id, challenge_id, status)

V7:
- public_profiles(user_id, display_name, bio, visibility)
- posts(id, author_id, artwork_version_id, status, approved_at)
- follows(follower_id, followee_id)
- likes(user_id, post_id)
- content_reports(id, reporter_id, target_id, reason, state)
- user_blocks(blocker_id, blocked_id)
- moderation_actions(id, actor_id, target_id, decision, timestamp)

## ایندکس‌ها و تغییر schema
- unique بر user progress composite key و social relations لازم.
- foreign key و on-delete مناسب با privacy/deletion policy.
- versioned migrations همراه rollback plan؛ migration خطرناک نیازمند backup.
- شاخص‌گذاری بر categories/filter/sort/updated_at و foreign keys.
- برای billing، provider transaction id باید unique باشد.
- حذف داده شخصی از جداول عملیاتی باید با الزامات مالی/قانونی و retention policy هماهنگ شود.

## فایل‌ها در Object Storage
- public: catalog thumbnails و immutable level payloads.
- private: user photo originals و user artwork قبل از انتشار.
- quarantined: uploads جدید تا زمان validate/moderate.
- هر فایل کلید، checksum، MIME و policy دسترسی داشته باشد.
- آپلودهای خصوصی فقط با مجوز معتبر یا signed URLs محدود انجام شوند.

## قابلیت مهاجرت
قبل از V4: Level schema migration tests و local guest ID.
قبل از V5: content version negotiation و offline cache invalidation.
قبل از V6: Purchase state machine و entitlement engine.
قبل از V7: public/private visibility و lifecycle حذف محتوا.
