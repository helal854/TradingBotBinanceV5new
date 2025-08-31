import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# إعدادات البوت
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")

# إعدادات Binance API
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "your_binance_api_key_here")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY", "your_binance_secret_key_here")

# إعدادات TRON API
TRON_API_KEY = os.getenv("TRON_API_KEY", "your_tron_api_key_here")

# إعدادات GitHub API
GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN", "your_github_token_here")

# إعدادات قاعدة البيانات
DATABASE_PATH = "data/trading_bot.db"

# إعدادات المسؤول
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "123456789"))

# إعدادات APIs الخارجية
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
FEAR_GREED_API_URL = "https://api.alternative.me/fng/"
TRADING_ECONOMICS_API_URL = "https://api.tradingeconomics.com"

# إعدادات المنطقة الزمنية
TIMEZONE = "Asia/Riyadh"

# إعدادات الأمان
RATE_LIMIT_MESSAGES = 30
RATE_LIMIT_DURATION = 60

# رسائل البوت
MESSAGES = {
    "welcome": """
🤖 مرحباً بك في بوت إشارات التداول الاحترافي!

🎯 الميزات المتاحة:
• إشارات تداول دقيقة ومحدثة
• تحليلات السوق المباشرة
• أفضل المتداولين على Binance
• الأجندة الاقتصادية

استخدم الأزرار أدناه للتنقل:
    """,
    
    "help": """
📚 دليل استخدام البوت:

🔹 /start - بدء البوت والترحيب
🔹 /help - عرض هذه المساعدة
🔹 /signals - عرض آخر الإشارات
🔹 /market - بيانات السوق المباشرة
🔹 /top_traders - أفضل المتداولين

💡 استخدم الأزرار التفاعلية للتنقل السهل!
    """,
    
    "no_signals": "📭 لا توجد إشارات متاحة حالياً",
    "market_error": "❌ خطأ في جلب بيانات السوق",
    "top_traders_error": "❌ خطأ في جلب بيانات أفضل المتداولين",
    "unauthorized": "🚫 غير مصرح لك باستخدام هذا البوت",
    "admin_only": "👨‍💼 هذا الأمر متاح للمسؤولين فقط"
}

