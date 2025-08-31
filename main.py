"""
الملف الرئيسي لبوت التداول
"""
import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# إضافة مسار المشروع
sys.path.append(str(Path(__file__).parent))

from config.config import BOT_TOKEN, LOGGING_CONFIG, ADMIN_USER_ID
from src.database import db_manager
from src.handlers import router
from src.admin_handlers import admin_router
from src.api_clients import APIManager, BINANCE_API_KEY, BINANCE_SECRET_KEY

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# إنشاء البوت والموزع
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)

dp = Dispatcher(storage=MemoryStorage())

# تسجيل الراوترات
dp.include_router(router)
dp.include_router(admin_router)

# مدير APIs العام
api_manager = None

async def on_startup():
    """إعدادات بدء التشغيل"""
    try:
        logger.info("🚀 بدء تشغيل البوت...")
        
        # إنشاء المجلدات المطلوبة
        Path("data").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        # تهيئة قاعدة البيانات
        await db_manager.init_database()
        logger.info("✅ تم تهيئة قاعدة البيانات")
        
        # تهيئة مدير APIs
        global api_manager
        api_manager = APIManager(BINANCE_API_KEY, BINANCE_SECRET_KEY)
        await api_manager.init_all()
        logger.info("✅ تم تهيئة جميع APIs")
        
        # إرسال رسالة للمسؤول
        try:
            await bot.send_message(
                ADMIN_USER_ID,
                "🟢 **البوت يعمل الآن**\n\nتم تشغيل البوت بنجاح وجميع الأنظمة تعمل بشكل طبيعي.",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.warning(f"لم يتم إرسال رسالة البدء للمسؤول: {e}")
        
        logger.info("🎉 تم تشغيل البوت بنجاح!")
        
    except Exception as e:
        logger.error(f"❌ خطأ في بدء التشغيل: {e}")
        raise

async def on_shutdown():
    """إعدادات إيقاف التشغيل"""
    try:
        logger.info("🛑 إيقاف البوت...")
        
        # إغلاق اتصالات APIs
        if api_manager:
            await api_manager.close_all()
        
        # إرسال رسالة للمسؤول
        try:
            await bot.send_message(
                ADMIN_USER_ID,
                "🔴 **تم إيقاف البوت**\n\nتم إيقاف البوت بأمان.",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.warning(f"لم يتم إرسال رسالة الإيقاف للمسؤول: {e}")
        
        logger.info("✅ تم إيقاف البوت بأمان")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إيقاف التشغيل: {e}")

async def main():
    """الدالة الرئيسية"""
    try:
        # تسجيل معالجات بدء وإيقاف التشغيل
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        # بدء البوت
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
        )
        
    except KeyboardInterrupt:
        logger.info("تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        logger.error(f"خطأ في تشغيل البوت: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        # تشغيل البوت
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("تم إنهاء البرنامج")
    except Exception as e:
        logger.error(f"خطأ عام: {e}")
        sys.exit(1)

