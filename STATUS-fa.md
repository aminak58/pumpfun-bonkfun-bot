# سند وضعیت (Checkpoint CP-1) — اسکنر شکار میم‌کوین

> **تاریخ:** 2026-09-14 | **وضعیت:** ✅ فاز ۱ کامل و فعال — دوره پایش آغاز شده
> **ریپو:** [aminak58/pumpfun-bonkfun-bot](https://github.com/aminak58/pumpfun-bonkfun-bot) (فورک از chainstacklabs/pumpfun-bonkfun-bot)
> **سند مکمل:** [RESEARCH-fa.md](RESEARCH-fa.md) (تحقیق و استدلال انتخاب‌ها)

---

## ۱. خلاصه وضعیت در یک نگاه

| مؤلفه | وضعیت |
|---|---|
| اسکنر paper-mode روی VM | ✅ فعال ۲۴/۷ به‌صورت سرویس `pumpfun-scanner` (systemd، auto-restart) |
| فید کشف | ✅ PumpPortal WS (رایگان، بدون کلید) |
| فید دوم | ✅ Helius logsSubscribe (کلید رایگان کاربر، در `.env` — در لاگ ماسک می‌شود) |
| فیلتر ریسک | ✅ RugCheck + حلقه recheck برای توکن‌های بدون report |
| ذخیره‌سازی | ✅ SQLite در `data/scanner.sqlite3` روی VM (جدول‌های `tokens` و `detections`) |
| پروژه موازی کاربر | ✅ دست‌نخورده (`memehunter_gate0.repeated_probe`, PID 7088) |
| تراکنش واقعی | ❌ هیچ — فقط کشف/ثبت (paper-mode طبق طراحی) |

## ۲. کارهای انجام‌شده (به ترتیب زمانی)

### ۲.۱ تحقیق و انتخاب (2026-09-14)
- بررسی سیستماتیک ریپوهای GitHub در حوزه اسنیپر/اسکنر/کپی‌تریدینگ (۱۱ کوئری، مرتب‌شده بر ستاره) + راستی‌آزمایی قیمت سرویس‌ها.
- نتیجه: اکثریت ریپوهای پرستاره تبلیغاتی/اسکم؛ **دو مخزن تایید شد:** همین ریپو (اسنیپ/اسکن سولانا) و `ChainBuff/open-sol-bot` (کپی‌تریدینگ). جزئیات کامل و فهرست ردشده‌ها → RESEARCH-fa.md.
- **فورک** ساخته شد و **سند تحقیقاتی** (`RESEARCH-fa.md`) کامیت شد (کامیت `eddf88d`).

### ۲.۲ تست عملی روی سیستم محلی (ویندوز ۱۰)
- کلون + venv با Python 3.13.5 → نصب بی‌خطا.
- تست زنده listener ها: **PumpPortal رایگان ✅** (استریم توکن‌های جدید بدون هیچ کلید)، RPC عمومی سولانا برای logsSubscribe **❌** (تأیید هشدار README) → تیر رایگان Helius لازم شد.

### ۲.۳ توسعه اسکنر (کامیت `7bd0cc7`)
پکیج `scanner/` ساخته شد — کاملاً paper-mode، بدون ارسال تراکنش:
- **`config.py`** — پیکربندی از `.env` (فیلترها، مسیرها، فواصل recheck).
- **`main.py`** — دو listener همزمان با reconnect خودکار و backoff:
  - PumpPortal (`subscribeNewToken`) → ثبت توکن جدید
  - Helius `logsSubscribe` (اختیاری، فقط با کلید) → ثبت رویدادهای Create؛ join روی `signature` = مقایسه تاخیر دو فید
  - ایزوله‌سازی خطای تک‌رویداد (یک event خراب هرگز اتصال را نمی‌کشد)
- **`rugcheck.py`** — کلاینت ناهمگام RugCheck با محدودسازی هم‌زمانی و dedup درخواست‌ها؛ فلگ = `score_normalised ≥ آستانه` یا ریسک `danger`.
- **`db.py`** — SQLite: جدول `tokens` (متادیتا + امتیاز/ریسک + فلگ) و `detections` (هر رویداد به تفکیک فید با timestamp محلی).
- **`report.py`** — گزارش آماری: شمارش روزانه، نسبت فلگ، مقایسه تاخیر دو فید (avg/median/min/max)، پرتکرارترین ریسک‌ها.
- **باگ واقعی رفع شد:** `zoneinfo` روی ویندوز بدون پکیج `tzdata` استثنا می‌داد و اتصال را می‌بُرید → حذف وابستگی به IANA tz (ساعت محلی سیستم) + ایزوله‌سازی خطا. (تست اول تصادفاً اثبات کرد reconnect خودکار سالم است.)

### ۲.۴ استقرار روی VM (freestyle)
- **VM:** `vm-fbe34fae6e3344c7b464dfbbc1d4f619` (slug: `memehunter-e2-smoke`) — Ubuntu 24.04، 4 vCPU / 8GB RAM / 32GB دیسک. پیش از استقرار preflight (git/venv/sudo) و ثبت PID پایل پروژه موازی (7088).
- **نصب:** کلون فورک در `/home/ubuntu/meme-scanner`، venv با Python 3.12.3 سیستم، `pip install -e .` — موفق.
- **پیکربندی:** `.env` (شامل کلید Helius) از سیستم محلی به VM منتقل شد؛ فایل gitignore است و کامیت نمی‌شود.
- **سرویس:** `/etc/systemd/system/pumpfun-scanner.service` — User=ubuntu، `Restart=always`، اجرای `python -u -m scanner`. حالت `enabled` (با بوت بالا می‌آید).
- **تأیید پس از استقرار:** سرویس active، هر دو فید متصل، رویدادها جاری؛ مصرف رم اضافه ~۵۰-۱۰۰MB از 7.9GB؛ **PID 7088 دست‌نخورده**.
- نکته عیب‌یابی: ابزار `freestyle vm fs/scp` در Git Bash به‌خاطر MSYS path mangling مسیرهای پوزیکسی را خراب می‌کند → راه‌حل `MSYS_NO_PATHCONV=1`. و CLI از داخل ویندوز بدون VPN به `api.freestyle.sh` نمی‌رسید (curl می‌رسید؛ fetch نود نمی‌رسید) → با روشن‌کردن VPN حل شد.

### ۲.۵ سخت‌سازی و پایش (کامیت `3b2c3f2`)
- **فیکس امنیتی:** لاگ `connected` کلید Helius را کامل چاپ می‌کرد → `feed_label()` فقط `scheme://host/path` لاگ می‌کند. (یک ورود قدیمی journal قبل از این فیکس کلید را دارد — ریسک پایین چون فقط روی VM خود کاربر است؛ چرخش کلید رایگان در پنل Helius در صورت تمایل.)
- **حلقه recheck:** RugCheck توکن‌های چندثانیه‌ای را با تاخیر ایندکس می‌کند → توکن‌های بدون report هر `RECHECK_INTERVAL_S=600` ثانیه دوباره چک می‌شوند (حداقل سن `RECHECK_MIN_AGE_S=300`، حداکثر `RECHECK_MAX_ATTEMPTS=5` بار برای هر mint).
- تست محلی با فواصل کوتاه: ماسک صفر نشتی، recheck فعال، صفر خطا. سپس `git pull` روی VM + ری‌استارت سرویس + تأیید مجدد سلامت و دست‌نخوردگی probe.

### ۲.۶ تاریخ‌چه کامیت‌های فورک

| کامیت | محتوا |
|---|---|
| `a0540fd` | نقطه شروع (فورک از upstream) |
| `eddf88d` | `docs:` سند تحقیقاتی RESEARCH-fa.md |
| `7bd0cc7` | `feat(scanner):` پکیج اسکنر paper-mode |
| `3b2c3f2` | `fix(scanner):` ماسک کلید در لاگ + حلقه recheck RugCheck |

## ۳. نقشه استقرار فعلی

| محل | مسیر / نام | توضیح |
|---|---|---|
| GitHub | `aminak58/pumpfun-bonkfun-bot` (origin) | فورک؛ `upstream` = chainstacklabs برای همگام‌سازی |
| لوکال (ویندوز) | `C:\Users\Kiyan-System\.zcode\workspace\default\pumpfun-bonkfun-bot` | کلون کاری + `.venv` (Python 3.13) + `.env` محلی |
| VM | `/home/ubuntu/meme-scanner` | کلون استقرار + `.venv` (Python 3.12) + `.env` با کلید Helius |
| VM | `/etc/systemd/system/pumpfun-scanner.service` | سرویس ۲۴/۷ (`enabled` + `Restart=always`) |
| VM | `/home/ubuntu/meme-scanner/data/scanner.sqlite3` | دیتای در حال انباشت |
| VM (دست‌نخورده) | `/home/ubuntu/memehunter/MemeHunter-E2-VM` | پروژه خود کاربر — probe gate0 (PID 7088) |

متغیرهای پیکربندی (در `.env`): `HELIUS_API_KEY`، `RUGCHECK_MAX_SCORE_NORM=60`، `RECHECK_INTERVAL_S=600`، `RECHECK_MIN_AGE_S=300`، `RECHECK_MAX_ATTEMPTS=5`، `SCANNER_DB_PATH`، `PUMPPORTAL_WS_URL` — مستندات کامل: [scanner/README.md](scanner/README.md).

## ۴. یافته‌های عملیاتی تا این چک‌پوینت

1. **تاخیر فیدها (n=20، تست محلی):** PumpPortal به‌طور سیستماتیک ~۱۰ ثانیه زودتر از فید رایگان Helius توکن را نشان می‌داد (median 9.98s، دامنه باریک 9.4–10.2s). علت دقیق نیاز به دیتای بیشتر دارد (احتمال push زودهنگام PumpPortal یا صف‌بندی تیر رایگان Helius)؛ از نظر عملیاتی: **فید اصلی همان PumpPortal است و Helius برای تحلیل آنچین/پشتیبان.**
2. **نرخ تولید توکن pump.fun:** حدود ۲۰-۲۵ توکن در دقیقه در ساعات پیک تست (~۲۸ تا ۳۵ هزار در روز) → حجم SQLite قابل‌مدیریت، ولی برای گزارش‌های بلندمدت باید ایندکس/آرشیو ببینید.
3. **رفتار RugCheck:** گزارش توکن تازه بلافاصله موجود نیست (404 تا ایندکس شدن) → recheck این شکاف را پر می‌کند؛ نرخ موفقیت recheck باید در دوره پایش اندازه‌گیری شود.
4. **سیگنال‌های اولیه ریسک:** پرتکرارترین ریسک‌های فلگ‌شده: «سابقه راگ بودن سازنده»، «Mint Authority روشن»، «Freeze Authority»، «توکن کپی».
5. **شبکه:** VM مستقیم (بدون VPN) به همه سرویس‌ها (pumpportal، helius، rugcheck، jup، RPC عمومی) دسترسی دارد؛ مشکل اتصال فقط سمت کلاینت ویندوز/VPN بود.

## ۵. کارهای بعدی (به ترتیب اولویت)

### فاز ۴ — دوره پایش (۱-۲ هفته، از 2026-09-14؛ کار اصلی: «صبر + گزارش‌گیری»)
- [ ] **ردیابی عملکرد ۲۴ ساعته (مهم‌ترین شکاف فعلی):** برای هر توکن ثبت‌شده، قیمت در +1h/+24h از DexScreener/Jupiter گرفته شود و «سود/زیان کاغذی سیگنال‌ها» (به‌ویژه فلگ‌شده‌ها) محاسب گردد → جدول `price_check` یا ستون‌های `price_1h/price_24h`. بدون این، سنجه «PnL کاغذی» نقشه راه قابل محاسبه نیست.
- [ ] مرور گزارش روزانه (`python -m scanner.report`): نسبت فلگ، نرخ موفقیت recheck، پوشش join دو فید (هماکنون helius_creates > pumpportal_creates؛ دلیل اختلاف باید مشخص شود).
- [ ] آستانه‌های فیلتر (`RUGCHECK_MAX_SCORE_NORM` و امضاهای ریسک) بعد از هفته اول با دیتای واقعی تنظیم شود.

### میان‌مدت — بهبودهای شناسایی‌شده
- [ ] **هشدار تلگرام:** توکن BotFather (ورودی کاربر، هنوز گرفته نشده) → ارسال سیگنال فلگ‌شده/فیلترشده به تلگرام. (تلگرام از روی VM خارجی بدون مشکل وصل می‌شود.)
- [ ] **غنی‌سازی متادیتا:** رویدادهای PumpPortal گاهی بدون name/symbol می‌آیند → تکمیل با RPC/DexScreener.
- [ ] **نگهداری دیتابیس:** با ~۳۰k توکن/روز، آرشیو ماهانه یا خانه‌آمدنی‌سازی جدول `detections`.
- [ ] همگام‌سازی دوره‌ای با upstream: `git fetch upstream && git merge upstream/main` (تا امروز upstream تغییر معناداری نداشته).
- [ ] (اختیاری) چرخش کلید Helius به‌خاطر ورود قدیمی journal.

### فاز ۵ — کپی‌تریدینگ با open-sol-bot (فقط پس از صلاحیت اعداد فاز ۴)
- [ ] استقرار `ChainBuff/open-sol-bot` با docker compose روی همان VM (MySQL + Redis + اپ).
- [ ] ساخت والت دورریز و شارژ **۰.۱-۰.۲ SOL** (هیچ‌وقت والت اصلی).
- [ ] اتصال توکن تلگرام؛ انتخاب والت‌های هدف کپی از برترین عملکردهای دیتای فاز ۴.
- [ ] خطوط قرمز: سقف مبلغ هر پوزیشن، سقف ضرر روزانه، تست با کمترین مبلغ حداقل یک هفته.

## ۶. راهنمای عملیات (Runbook)

```bash
VM=vm-fbe34fae6e3344c7b464dfbbc1d4f619

# وضعیت سرویس
freestyle vm exec $VM -- systemctl is-active pumpfun-scanner

# لاگ زنده
freestyle vm exec $VM -- journalctl -u pumpfun-scanner -f -o cat

# گزارش آماری
freestyle vm exec $VM -- bash -c "cd /home/ubuntu/meme-scanner && .venv/bin/python -m scanner.report"

# توقف / شروع / ری‌استارت
freestyle vm exec $VM -- sudo systemctl stop pumpfun-scanner
freestyle vm exec $VM -- sudo systemctl start pumpfun-scanner
freestyle vm exec $VM -- sudo systemctl restart pumpfun-scanner

# به‌روزرسانی اسکنر روی VM (پس از پوش جدید از لوکال)
freestyle vm exec $VM -- bash -c "cd /home/ubuntu/meme-scanner && git pull --ff-only && sudo systemctl restart pumpfun-scanner"
```

## ۷. ریسک‌ها و قواعد امنیتی

- کد بالا «NOT FOR PRODUCTION» upstream است — با همین فرض استفاده می‌شود (paper-mode، بدون تراکنش).
- کلید Helius فقط در `.env` (روی لوکال و VM) — هرگز کامیت/لاگ نمی‌شود (ماسک فعال).
- ورود قدیمی journal (قبل از کامیت `3b2c3f2`) حاوی کلید است — فقط روی VM کاربر؛ چرخش کلید در پنل Helius اختیاری.
- در فاز ۵ (پول واقعی): فقط والت دورریز، مبلغ ناچیز، و بررسی چشمی کد پیش از شارژ — بخش Issues این حوزه پر از بات دزد کلید است.
