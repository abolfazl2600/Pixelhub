# 01 | معماری مرجع و ساختار توسعه

## اصول
- Monorepo: کد Flutter، Backend، Admin، اسناد و گردش‌های CI در یک مخزن.
- یک موتور Paint برای هر دو پلتفرم؛ هیچ نسخه دوم مجزا از الگوریتم بازی ساخته نشود.
- Dependency Inversion: Domain منطق بازی به SDK تبلیغ، دیتابیس یا HTTP وابسته نباشد.
- Offline-first: اعمال نقاشی ابتدا محلی و فوری انجام شوند؛ شبکه در مسیر هر لمس نباشد.
- Progressive enhancement: Backend و خدمات آنلاین به‌تدریج در نسخه‌های ۴ به بعد افزوده شوند.
- Versioned data contracts: تمام تصاویر و پیشرفت‌ها Schema Version دارند.

## ساختار هدف مخزن (هنوز پیاده‌سازی نشده)
~~~
Pixelhub/
  docs/product-plan/         # همین نقشه توسعه
  apps/
    game/                    # Flutter Android + Web
      lib/
        app/
        features/
          home/
          painting/
          image_import/
          gallery/
          account/
          shop/
          community/
        core/
        platform_adapters/
      assets/
      android/
      web/
      test/
    admin/                   # Next.js dashboard, V5
    api/                     # NestJS modular monolith, V4
  packages/
    game_domain/             # پاک، بدون UI
    painting_engine/         # painter + input processing
    pixel_converter/         # import -> quantize -> level
    level_schema/            # models and migration
    design_system/           # widgets/theme
    api_client/              # typed contracts
    persistence/             # repositories/interfaces
  services/
    content_worker/          # V5
  infrastructure/
    docker/
    migrations/
    monitoring/
  .github/workflows/
~~~

## معماری منطق بازی
- LevelDefinition: شناسه، نسخه، ابعاد، پالت، cell color index و checksum.
- PaintingSession: خانه‌های تکمیل‌شده، شمارنده‌ها، حرکت‌های Undo و generation.
- PaintingController: تغییر رنگ، اعمال stroke، hint و finish detection.
- PaintRenderer: رندر کم‌هزینه شبکه، شماره‌ها، انتخاب‌ها و Zoom/Pan؛ جدا از Domain.
- LevelRepository: دریافت از asset در V1–V3 یا CDN/Cache در V5 به بعد.
- ProgressRepository: ذخیره محلی، سپس Cloud sync adapter از V4.
- ImageConverter: عکس -> grid -> palette -> level؛ خروجی همان LevelDefinition.

## مدیریت state / navigation
- Riverpod یا یک state manager استاندارد، با Dependency Injection قابل تست.
- go_router یا معادل با مسیریابی ثابت؛ روی GitHub Pages ابتدا Hash URL برای پرهیز از 404 مسیر مستقیم.
- Design tokens، کامپوننت‌های مشترک و یک ResponsivePolicy محدود: هیچ layout دسکتاپ ساخته نشود.
- دسکتاپ وب: محتوای بازی در قاب 390–430 واحد منطقی و وسط‌چین. ارتفاع و safe area adapt شوند. کلیک ماوس و چرخ اسکرول اختیاری معادل Gestures.

## لایه داده نسخه به نسخه
| دوره | منبع سطح‌ها | ذخیره پیشرفت | هویت |
|---|---|---|---|
| V1 | fixture محلی | ندارد | ندارد |
| V2 | asset محلی | محلی | مهمان |
| V3 | asset + عکس خصوصی | محلی | مهمان |
| V4 | asset + cloud catalog اولیه | محلی + cloud | حساب و مهمان |
| V5 | CDN و Admin | محلی + cloud | حساب |
| V6 | مثل V5 + پرداخت | محلی + cloud | Entitlement |
| V7 | مثل V6 + عمومی‌سازی کنترل‌شده | محلی + cloud | Social profile |

## Backend هدف (فقط از V4 به بعد)
- REST API نسخه‌دار: /api/v1.
- Auth و user profile؛ authorization روی هر رکورد.
- Progress Sync با optimistic concurrency، idempotency و conflict policy.
- Catalog metadata در PostgreSQL، فایل سطح در Object Storage/CDN.
- سرویس Content Pipeline غیرهمزمان با Queue/Worker در V5.
- Commerce: اعتبارسنجی خرید در Server، entitlement مستقل از داده کلاینت.
- Community: visibility, report, block, moderation و audit trail از V7.

## دیتابیس و ذخیره فایل
- PostgreSQL source of truth: users, levels, catalog, user_progress, purchases, moderation.
- نگهداری نسخه immutable فایل سطح منتشرشده تا پیشرفت کاربران قدیمی خراب نشود.
- Object storage برای original image، level payload، thumbnail، user shared assets.
- حداقل دسترسی؛ URL امضاشده برای فایل‌های خصوصی.
- بکاپ دیتابیس + Object Storage و آزمایش بازگردانی در V5 به بعد.

## زیرساخت و محیط‌ها
- Dev (لوکال runner یا cloud dev), Staging, Production.
- محیط اصلی Android و Web از یک commit/tag ساخته شود.
- Secrets در GitHub Environments و Secret manager میزبان، نه در سورس.
- DevOps اولیه: Managed DB و container-based API؛ Kubernetes لازم نیست.
- Monitoring: runtime exceptions، latency، error rates، failed jobs و sync errors.

## معماری وب یکسان با موبایل
- Flutter Web همان route، state و widgets را ارائه کند.
- در دسکتاپ حداکثر عرض قاب موبایل، نه افزایش ستون‌ها و نه سایدبار.
- در موبایل عرض متناسب با viewport و safe area.
- فرمت فونت و input کنترل شود؛ اختلاف اجباری در Camera, Billing, Push و File Picker صرفاً در Adapter.
- نه Google AdMob Android را برای نسخه Web فرض می‌کنیم، نه Billing اندروید را در وب.
- مرورگر storage می‌تواند توسط کاربر یا خود مرورگر پاک شود؛ Cloud Sync بعدی محافظت مکمل است.

## تصمیم‌های معماری نیازمند ثبت ADR
- انتخاب قطعی state-management و local DB پس از Spike V1.
- روش Pixel Renderer پس از بنچمارک V2 روی Web و گوشی واقعی.
- روش auth/provider قبل از V4.
- هاست backend و regions قبل از V4.
- روش پرداخت وب و بازارها پیش از V6.

این فایل معماری هدف است؛ سرویس‌های ذکرشده تا نسخه مربوطه الزامی نیستند.
