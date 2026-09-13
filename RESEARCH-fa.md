# سند تحقیقاتی: پروژه‌های اوپن‌سورس شکار میم‌کوین و ارزش استفاده برای تریدر ریتیل ایرانی

> **تاریخ تحقیق:** 2026-09-14
> **دامنه بررسی:** GitHub + وب (ریپوهای اسنیپر/اسکنر/کپی‌تریدینگ سولانا و BSC)
> **قیدهای پروژه:** نت ایران (فیلترینگ/تحریم)، بدون API پولی، بودجه نزدیک به صفر
> **نتیجه نهایی:** این ریپو (`chainstacklabs/pumpfun-bonkfun-bot`) + `ChainBuff/open-sol-bot` انتخاب و در دو فاز استقرار شدند.

---

## ۱. خلاصه اجرایی

- اکثریت قاطع مخزن‌های «پرستاره» این حوزه در GitHub یا **قیف تبلیغاتی** هستند یا **اسکم**؛ پرستاره‌ترین نتیجه (4,462★) نشانه‌های واضح ستاره‌خرید دارد.
- فقط **دو مخزن** ارزش واقعی و قابل اتکا پیدا شد: این ریپو و `ChainBuff/open-sol-bot`.
- اسنیپ خودکارِ رقابتی با قید «بدون API پولی» عملاً غیرممکن است (Geyser/gRPC فقط پولی است). ارزش واقعی برای تریدر ریتیل در **کشف سریع + فیلتر راگ + کپی‌تریدینگ** است که تماماً با API های رایگان شدنی است.
- تست عملی روی سیستم واقعی (ویندوز ۱۰) انجام شد: نصب بی‌خطا و استریم زنده توکن‌های جدید pump.fun با صفر هزینه تأیید شد (بخش ۵).

## ۲. روش تحقیق

- جستجوی GitHub API روی کوئری‌های `pumpfun sniper`، `meme coin sniper`، `sniper bot solana`، `four.meme sniper`، `raydium sniper bot`، `dexscreener telegram bot`، `memecoin scanner`، `honeypot detector`، `rugcheck`، `copy trading bot solana`، `pumpportal` (مرتب‌شده بر اساس ستاره).
- بررسی README، لایسنس، تاریخ آخرین push، تعداد commit/watcher/fork برای کاندیداهای برتر.
- راستی‌آزمایی قیمت/تیر رایگان سرویس‌ها (PumpPortal، Helius، Shyft) از مستندات رسمی.
- **تست میدانی:** کلون، نصب venv و اجرای ۳۰ ثانیه‌ای دو listener روی سیستم واقعی.

## ۳. مخزن‌های تاییدشده

| مخزن | کارکرد | وضعیت | نیاز API | داوری |
|---|---|---|---|---|
| [chainstacklabs/pumpfun-bonkfun-bot](https://github.com/chainstacklabs/pumpfun-bonkfun-bot) (همین ریپو) | اسنیپ و ترید pump.fun / letsbonk.fun (سولانا) | 985★، Apache-2.0، آپدیت 2026-08 | بدون API ثالث؛ RPC قوی می‌خواهد | **بهترین نقطه شروع** — مرجع کد تمیز؛ حالت listener روی تیر رایگان برای کشف/یادگیری |
| [ChainBuff/open-sol-bot](https://github.com/ChainBuff/open-sol-bot) | کپی‌تریدینگ + مانیترینگ با رابط تلگرام (سولانا) | 406★، Apache-2.0، آپدیت 2025-12 | README خودش: تیر رایگان Helius/Shyft برای استفاده شخصی کافی است | **کاربردی‌ترین برای سناریوی بدون API پولی** — نیاز به Docker + MySQL + Redis |
| PumpPortal Data WebSocket + ریپوهای واسط کوچک (مثل [thetateman/Trading-API](https://github.com/thetateman/Trading-API)) | استریم لحظه‌ای توکن‌های جدید pump.fun/PumpSwap | سرویس زنده | رایگان، بدون کلید | ماده خام هشداردهنده شخصی؛ API ترید محلی‌اش 0.5% کارمزد دارد |
| RugCheck API (`api.rugcheck.xyz`) + wrapper ها مثل [ccan23/rugcheck](https://github.com/ccan23/rugcheck) | فیلتر راگ/ریسک توکن‌های سولانا | API زنده | رایگان، بدون کلید | لایه ایمنی ضروری برای هر خرید |
| [Immutal0/dexscreener-analysis-bot-meme](https://github.com/Immutal0/dexscreener-analysis-bot-meme) | اسکنر تحلیل میم‌کوین روی DexScreener (سولانا + Base) | 19★، کوچک | DexScreener API (رایگان، بی‌کلید) | فقط **بوایلرپلیت**، نه محصول نهایی |

## ۴. مخزن‌های ردشده (با دلیل)

| مخزن | ستاره | دلیل رد |
|---|---|---|
| `mortdeus/solana-copy-sniper-mev-trading-bot` | 4,462 | کیورد-اسپم، 15 کامیت، 0 watcher، تناقض لایسنس (BSD در سایدبار / MIT در README)، قیف فروش خدمات به نویسنده — **الگوی کامل ستاره‌خرید** |
| خانواده `Sniper-Calls-Bot` (6 اکانت با توضیح یکسان: EthanGreen-sol، sol-ethan، Green-EthanSOL و…) | 7–48 | شبکه ریپوی اسپم با الگوی کلاسیک درینر |
| `coffellas-cto/Solana-Copy-Trading-Bot`، `cutupdev/*`، `bigmacman1129/*` | 130–409 | ریپوهای تبلیغاتی با لینک تلگرام در توضیحات؛ قیف فروش محصول |
| همه ریپوهای four.meme/BNB (`HarrierOnChain/Fourmeme-bot` و مشابه‌ها) | ≤31 | ریز و تبلیغاتی («Contact for …»)؛ آپشن اوپن‌سورس جدی برای BSC وجود ندارد |
| `1fge/pump-fun-sniper-bot` | 300 | متروک از 2024-08، بدون لایسنس (از نظر حقوقی هم قابل استفاده تجاری نیست) |
| `TreeCityWes/Pump-Fun-Trading-Bot-Solana` | 216 | متروک از 2024-08؛ فقط ارزش تاریخی/آموزشی |
| `Webeoidentify/Honeypot-Detector` | 2,232 | 0 watcher، بدون توضیح — نشانه ستاره‌خرید؛ نیازمند ممیزی سخت‌گیرانه قبل از هر استفاده |

## ۵. نتایج تست عملی روی سیستم محلی (2026-09-14)

**محیط:** Windows 10 x64، Python 3.13.5، pip 26.2.1، git 2.49، Docker 28.3.3، Node 24.19

| تست | نتیجه |
|---|---|
| `python -m venv .venv` + `pip install -e .` روی این ریپو | ✅ بدون خطا (وابستگی‌ها سبک‌اند؛ حتی `winloop` برای ویندوز دارد) |
| `learning-examples/listen-new-tokens/listen_pumpportal.py` (30 ثانیه، رایگان، بدون کلید) | ✅ **استریم زنده توکن‌های جدید pump.fun** — چند توکن واقعی در ۳۰ ثانیه دریافت شد (نام، mint، مارکت‌کپ، سازنده) |
| `listen_logsubscribe.py` با `wss://api.mainnet-beta.solana.com` (RPC عمومی رایگان) | ❌ هیچ رویدادی در ۳۰ ثانیه نرسید — هشدار README تأیید شد: RPC عمومی برای این workload کافی نیست → برای گوش‌دادن زنده تیر رایگان Helius لازم است |

> جمع‌بندی تست: مسیر «کشف توکن جدید با صفر هزینه» از همین لپ‌تاپ عملی است؛ فقط مرحله بعد (تحلیل آنچین/ارسال تراکنش) به تیر رایگان Helius (1M اعتبار/ماه، 10 rps + WebSocket) نیاز دارد.

## ۶. پشته API رایگان (بدون API پولی)

| سرویس | کاربرد | وضعیت رایگان |
|---|---|---|
| PumpPortal Data WS (`wss://pumpportal.fun/api/data`) | کشف لحظه‌ای توکن جدید pump.fun/PumpSwap | رایگان با rate limit؛ بدون کلید |
| DexScreener API | داده جفت‌ارزها/نقدینگی/حجم | رایگان، بدون کلید (~300 req/min برای pairs) |
| RugCheck API | امتیاز ریسک/راگ توکن سولانا | رایگان، بدون کلید |
| Jupiter Lite API (`lite-api.jup.ag`) | سوآپ روی سولانا | رایگان با rate limit؛ بدون کلید |
| Helius (Free plan) | RPC + WebSocket سولانا | 1M اعتبار/ماه، 10 req/s — نیاز به ثبت‌نام |
| Shyft (Free plan) | RPC سولانا | 10 req/s؛ **gRPC فقط در پلن‌های پولی** |
| RPC عمومی (`api.mainnet-beta.solana.com`) | تست/کوئری سبک | رایگان بدون حساب؛ برای گوش‌دادن زنده نامناسب (تست شد) |

## ۷. ملاحظات نت ایران

1. **اسنیپ رقابتی = مسابقه سرعت در همان اسلات.** رقیب، حرفه‌ای‌هایی هستند با سرور هم‌مکان و Geyser پولی. با VPN + تیر رایگان (10 rps، بدون gRPC) در این مسابقه می‌بازی. **راهبرد درست برای ریتیل: کشف سریع + فیلتر + کپی‌تریدینگ** (کپی‌تریدینگ به میلی‌ثانیه حساس نیست).
2. **تلگرام فیلتر است** و هر دو بات منتخب رابط تلگرامی دارند → یا VPN دائمی، یا اجرا روی VPS خارج (مشکل را یکجا حل می‌کند و تاخیر را هم کم می‌کند).
3. **تحریم IP:** Helius/Shyft/QuickNode و مشابه‌ها معمولاً IP ایران را سرو نمی‌دهند → ثبت‌نام و مصرف فقط با IP خارجی.
4. Cloudflare-front بودن برخی سرویس‌ها (GMGN، DexScreener وب) ممکن است برای IP ایران چالش بیاورد.

## ۸. نقشه راه پیشنهادی (دو فاز)

**فاز ۱ — همین هفته، سیستم محلی، هزینه صفر:**
- این ریپو فقط به‌عنوان موتور کشف+فیلتر در حالت ناظر: `listen-new-tokens/listen_pumpportal.py` یا `listen_logsubscribe.py` با WSS رایگان Helius.
- فیلتر RugCheck روی خروجی + لاگ‌گیری. دو هفته بدون پول واقعی؛ فقط ثبت: تعداد هشدار/روز، عملکرد ۲۴ ساعته بعدی هر توکن.

**فاز ۲ — VPS لینوکسی رایگان یک‌ماهه (اروپای غربی: فرانکفورت/آمستردام/لندن، اوبونتو ۲۴.۰۴، ۲vCPU/4GB):**
- `ChainBuff/open-sol-bot` با `docker-compose` برای کپی‌تریدینگ با مبلغ آزمایشی 0.1–0.2 SOL.
- همان VPS اسکنر فاز ۱ را هم ۲۴/۷ نگه می‌دارد.
- گزینه‌های سرور رایگان (بررسی‌شده 2026-09): [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/) (ARM 2 OCPU/12GB برای اکانت نو) و Google Cloud با 300$ اعتبار/۹۰ روز.

**شاخص موفقیت پیش از تزریق سرمایه:** تاخیر «ساخت توکن تا هشدار»، دقت فیلتر RugCheck، سود/زیان کاغذی هشدارها.

## ۹. هشدارهای امنیتی (جدی بخوان)

- بخش Issues این ریپوها پر از **بات‌های دزد کلید** است — خود تیم Chainstack در README هشدار داده.
- فقط با **والت دورریز** و مبالغ کم؛ هرگز والت اصلی را وصل نکن.
- کلید خصوصی فقط در `.env`/`config.toml` محلی بماند؛ هیچ سرویس یا باتی آن را دریافت نمی‌کند.
- قبل از اجرای هر کد این حوزه، اسکریپت‌های مربوط به والت را خودت بخوان (درینر واقعی در ریپوهای مشابه پیدا شده است).
- همه این کدها «NOT FOR PRODUCTION» اعلام شده‌اند — با همین فرض استفاده کن.

## ۱۰. منابع

- [chainstacklabs/pumpfun-bonkfun-bot](https://github.com/chainstacklabs/pumpfun-bonkfun-bot) — ریپوی انتخابی
- [ChainBuff/open-sol-bot](https://github.com/ChainBuff/open-sol-bot)
- [PumpPortal Fees](https://pumpportal.fun/fees/) / [Data API](https://pumpportal.fun/data-api/real-time/)
- [Helius Pricing](https://www.helius.dev/pricing) / [Shyft Pricing](https://shyft.to/solana-rpc-grpc-pricing)
- [آموزش رسمی Chainstack برای بات pump.fun](https://docs.chainstack.com/docs/solana-creating-a-pumpfun-bot)
- [راهنمای اسکنر GMGN با پایتون](https://blog.poloxue.com/how-i-built-a-real-time-memecoin-sniper-bot-using-python-telegram-387b01cf31b6) / [ساخت اسنیپر سولانا](https://dev.to/vietthanhsai/how-to-build-your-solana-sniper-bot-5-f8k)
- [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/) / [استقرار بات ترید روی GCP](https://algotrading101.com/learn/algo-trading-deployment-google-cloud-platform/)
