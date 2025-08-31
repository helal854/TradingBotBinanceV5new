# TradingBotBinanceV5new

## 🤖 بوت تليجرام للتداول مع إشارات Binance

بوت تليجرام متطور ومتكامل يوفر إشارات التداول الاحترافية وتحليلات السوق المباشرة مع ميزات إدارية متقدمة.

## ✨ الميزات الرئيسية

### 🎯 للمستخدمين
- **إشارات تداول احترافية**: إشارات دقيقة مع نقاط الدخول والأهداف ووقف الخسارة
- **تحليل السوق المباشر**: بيانات السوق اللحظية ومؤشر الخوف والطمع
- **أفضل المتداولين**: قائمة بأفضل المتداولين على Binance مع إحصائياتهم
- **الأجندة الاقتصادية**: أحداث اقتصادية مهمة تؤثر على السوق
- **واجهة سهلة الاستخدام**: أزرار تفاعلية وتنقل سلس

### 🔧 للمسؤولين
- **لوحة إدارة متقدمة**: إدارة شاملة للمستخدمين والإشارات
- **نظام مراقبة النظام**: مراقبة الأداء والموارد في الوقت الفعلي
- **إحصائيات مفصلة**: تقارير شاملة عن استخدام البوت
- **نظام البث العام**: إرسال رسائل للمستخدمين
- **إدارة الإشارات**: إضافة وتعديل الإشارات

## 🏗️ البنية التقنية

```
TradingBotBinanceV5new/
├── src/                    # الكود المصدري
│   ├── database.py         # إدارة قاعدة البيانات
│   ├── api_clients.py      # عملاء APIs الخارجية
│   ├── handlers.py         # معالجات أوامر البوت
│   ├── admin_handlers.py   # معالجات الإدارة
│   ├── keyboards.py        # لوحات المفاتيح التفاعلية
│   ├── signal_parser.py    # محلل الإشارات
│   ├── top_traders_api.py  # API أفضل المتداولين
│   └── monitoring.py       # نظام المراقبة
├── config/                 # ملفات التكوين
│   └── config.py          # إعدادات البوت
├── data/                   # قاعدة البيانات والتقارير
├── logs/                   # ملفات السجلات
├── main.py                 # الملف الرئيسي
├── test_bot.py            # اختبارات البوت
└── requirements.txt        # المتطلبات
```

## 🚀 التثبيت والتشغيل

### المتطلبات
- Python 3.8+
- pip
- Git

### خطوات التثبيت

1. **استنساخ المستودع**
```bash
git clone https://github.com/yourusername/TradingBotBinanceV5new.git
cd TradingBotBinanceV5new
```

2. **تثبيت المتطلبات**
```bash
pip install -r requirements.txt
```

3. **إعداد متغيرات البيئة**
```bash
cp .env.example .env
# قم بتعديل ملف .env وإضافة مفاتيح APIs الخاصة بك
```

4. **تشغيل البوت**
```bash
python main.py
```

## ⚙️ التكوين

### متغيرات البيئة المطلوبة

```env
# Telegram Bot
BOT_TOKEN=your_telegram_bot_token

# Binance API
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key

# TRON API (اختياري)
TRON_API_KEY=your_tron_api_key

# GitHub API (اختياري)
GITHUB_API_TOKEN=your_github_token

# Admin Settings
ADMIN_USER_ID=your_telegram_user_id
```

### الحصول على مفاتيح APIs

#### 1. Telegram Bot Token
1. ابحث عن `@BotFather` في تليجرام
2. أرسل `/newbot` واتبع التعليمات
3. احفظ التوكن المُعطى

#### 2. Binance API Key
1. سجل دخولك إلى Binance
2. اذهب إلى "API Management"
3. أنشئ مفتاح API جديد
4. فعّل صلاحيات القراءة فقط للأمان

## 🧪 الاختبار

```bash
# تشغيل الاختبارات الشاملة
python test_bot.py

# فحص حالة البوت
python -c "from src.database import db_manager; import asyncio; asyncio.run(db_manager.init_database())"
```

## 📊 الميزات المتقدمة

### نظام الإشارات
- تحليل تلقائي لنصوص الإشارات
- استخراج العملة والاتجاه والأهداف
- التحقق من صحة البيانات
- تنسيق احترافي للرسائل

### أفضل المتداولين
- جلب بيانات أفضل المتداولين من Binance
- فلترة حسب الفترة الزمنية ونوع الإحصائية
- عرض الأرباح والخسائر والمتابعين

### نظام المراقبة
- مراقبة موارد النظام (CPU, RAM, Disk)
- إحصائيات البوت والمستخدمين
- تقارير شاملة وتنبيهات تلقائية
- حفظ التقارير التاريخية

## 🔐 الأمان

- تشفير مفاتيح APIs
- التحقق من صلاحيات المستخدمين
- تسجيل جميع العمليات
- حماية من الاستخدام المفرط

## 📈 الأداء

- استجابة سريعة (< 500ms)
- دعم آلاف المستخدمين المتزامنين
- تحسين استهلاك الذاكرة
- تخزين مؤقت ذكي

## 🛠️ التطوير

### إضافة ميزات جديدة

1. أنشئ فرع جديد
```bash
git checkout -b feature/new-feature
```

2. اكتب الكود والاختبارات
3. قم بالاختبار الشامل
```bash
python test_bot.py
```

4. ارفع التغييرات
```bash
git commit -m "Add new feature"
git push origin feature/new-feature
```

### هيكل قاعدة البيانات

```sql
-- المستخدمون
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- المستخدمون المصرح لهم
CREATE TABLE allowed_users (
    user_id INTEGER PRIMARY KEY,
    is_premium BOOLEAN DEFAULT 0,
    premium_expires TIMESTAMP,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    added_by INTEGER
);

-- الإشارات
CREATE TABLE signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    direction TEXT NOT NULL,
    entry_prices TEXT NOT NULL,
    targets TEXT,
    stop_loss REAL,
    leverage INTEGER,
    signal_text TEXT NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

## 🚀 النشر

### على خادم Linux

1. **تحديث النظام**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **تثبيت Python والمتطلبات**
```bash
sudo apt install python3 python3-pip git -y
```

3. **استنساخ المشروع**
```bash
git clone https://github.com/yourusername/TradingBotBinanceV5new.git
cd TradingBotBinanceV5new
```

4. **تثبيت المتطلبات**
```bash
pip3 install -r requirements.txt
```

5. **إعداد خدمة systemd**
```bash
sudo nano /etc/systemd/system/tradingbot.service
```

```ini
[Unit]
Description=Trading Bot Binance V5
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/TradingBotBinanceV5new
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

6. **تفعيل الخدمة**
```bash
sudo systemctl enable tradingbot
sudo systemctl start tradingbot
sudo systemctl status tradingbot
```

## 📞 الدعم والمساهمة

### الإبلاغ عن المشاكل
- استخدم [GitHub Issues](https://github.com/yourusername/TradingBotBinanceV5new/issues)
- قدم وصفاً مفصلاً للمشكلة
- أرفق ملفات السجلات إن أمكن

### المساهمة
1. Fork المستودع
2. أنشئ فرع للميزة الجديدة
3. اكتب اختبارات للكود الجديد
4. أرسل Pull Request

## 📄 الترخيص

هذا المشروع مرخص تحت رخصة MIT - انظر ملف [LICENSE](LICENSE) للتفاصيل.

## 🙏 شكر وتقدير

- [aiogram](https://github.com/aiogram/aiogram) - مكتبة Telegram Bot
- [python-binance](https://github.com/sammchardy/python-binance) - مكتبة Binance API
- [ccxt](https://github.com/ccxt/ccxt) - مكتبة تبادل العملات المشفرة

## 📊 الإحصائيات

![GitHub stars](https://img.shields.io/github/stars/yourusername/TradingBotBinanceV5new)
![GitHub forks](https://img.shields.io/github/forks/yourusername/TradingBotBinanceV5new)
![GitHub issues](https://img.shields.io/github/issues/yourusername/TradingBotBinanceV5new)
![GitHub license](https://img.shields.io/github/license/yourusername/TradingBotBinanceV5new)

---

**تم التطوير بـ ❤️ لمجتمع المتداولين العرب**

