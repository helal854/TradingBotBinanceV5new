#!/usr/bin/env python3
"""
اختبار بسيط للبوت
"""
import asyncio
import logging
import sys
from pathlib import Path

# إضافة مسار المشروع
sys.path.append(str(Path(__file__).parent.parent))

from src.database import db_manager
from src.keyboards import get_main_keyboard
from config.config import MESSAGES

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_basic_functions():
    """اختبار الوظائف الأساسية"""
    print("🔄 اختبار الوظائف الأساسية...")
    
    try:
        # اختبار قاعدة البيانات
        print("📊 اختبار قاعدة البيانات...")
        await db_manager.init_database()
        
        # اختبار إضافة مستخدم
        test_user_id = 123456789
        await db_manager.add_user(test_user_id, "TestUser", "test_user")
        print(f"✅ تم إضافة المستخدم {test_user_id}")
        
        # اختبار الحصول على معلومات المستخدم
        user_info = await db_manager.get_user_info(test_user_id)
        if user_info:
            print(f"✅ تم الحصول على معلومات المستخدم: {user_info['username']}")
        
        # اختبار لوحات المفاتيح
        print("⌨️ اختبار لوحات المفاتيح...")
        main_keyboard = get_main_keyboard()
        print("✅ تم إنشاء لوحة المفاتيح الرئيسية بنجاح")
        
        # اختبار الرسائل
        print("💬 اختبار الرسائل...")
        welcome_msg = MESSAGES.get("welcome", "رسالة الترحيب غير متوفرة")
        print(f"✅ رسالة الترحيب: {welcome_msg[:50]}...")
        
        # اختبار الإحصائيات
        print("📈 اختبار الإحصائيات...")
        stats = await db_manager.get_stats()
        print(f"✅ إحصائيات النظام: {stats}")
        
        print("🎉 جميع الاختبارات الأساسية نجحت!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        return False

async def main():
    """الدالة الرئيسية"""
    print("🚀 بدء الاختبار البسيط للبوت...")
    
    success = await test_basic_functions()
    
    if success:
        print("✅ البوت جاهز للعمل!")
    else:
        print("❌ البوت يحتاج إصلاحات")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)

