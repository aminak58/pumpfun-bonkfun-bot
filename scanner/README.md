# Scanner (paper-mode)

اسکنر شکار توکن‌های جدید pump.fun — بدون هیچ تراکنش واقعی. فقط کشف + فیلتر RugCheck + ثبت در SQLite.

## اجرا

```bash
# forever (Ctrl-C برای توقف)
python -u -m scanner

# اجرای محدود برای تست
python -u -m scanner --duration 60

# گزارش آماری
python -m scanner.report
```

## پیکربندی (فایل `.env` در ریشه ریپو — کامیت نمی‌شود)

| متغیر | پیش‌فرض | توضیح |
|---|---|---|
| `HELIUS_API_KEY` | — | کلید رایگان Helius؛ با این کلید، کانال دوم (logsSubscribe) هم فعال می‌شود تا تاخیر دو فید مقایسه شود |
| `PUMPPORTAL_WS_URL` | `wss://pumpportal.fun/api/data` | فید اصلی کشف (رایگان، بدون کلید) |
| `RUGCHECK_MAX_SCORE_NORM` | `60` | بالای این امتیاز (۰-۱۰۰) توکن `flag` می‌شود |
| `RECHECK_INTERVAL_S` | `600` | هر چند ثانیه یک‌بار توکن‌های بدون report دوباره چک شوند |
| `RECHECK_MIN_AGE_S` | `300` | حداقل سن توکن برای recheck (RugCheck توکن‌های تازه را دیر ایندکس می‌کند) |
| `RECHECK_MAX_ATTEMPTS` | `5` | حداکثر دفعات تلاش مجدد برای هر mint |
| `SCANNER_DB_PATH` | `data/scanner.sqlite3` | مسیر دیتابیس |

## ساختار داده

- `tokens` — هر توکن جدید: mint، نام/سمبل، مارکت‌کپ، خرید اولیه، امتیاز و ریسک‌های RugCheck، فلگ
- `detections` — هر رویداد کشف به تفکیک فید (`pumpportal` / `helius-logs`) با timestamp محلی؛ join روی `signature` = مقایسه تاخیر دو فید
- گزارش تاخیر و ریسک‌ها: `python -m scanner.report`
