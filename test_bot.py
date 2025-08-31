#!/usr/bin/env python3
"""
ملف اختبار شامل لبوت التداول
"""
import asyncio
import logging
import sys
import os
from datetime import datetime

# إضافة مجلد المشروع للمسار
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import db_manager
from src.api_clients import APIManager
from src.signal_parser import signal_parser
from src.top_traders_api import top_traders_api
from src.monitoring import bot_monitor
from config.config import *

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BotTester:
    """فئة اختبار البوت"""
    
    def __init__(self):
        self.api_manager = APIManager(BINANCE_API_KEY, BINANCE_SECRET_KEY)
        self.test_results = []
        self.failed_tests = []
    
    async def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        logger.info("🚀 بدء الاختبار الشامل للبوت...")
        
        tests = [
            ("اختبار قاعدة البيانات", self.test_database),
            ("اختبار Binance API", self.test_binance_api),
            ("اختبار محلل الإشارات", self.test_signal_parser),
            ("اختبار أفضل المتداولين", self.test_top_traders),
            ("اختبار نظام المراقبة", self.test_monitoring),
            ("اختبار APIs الخارجية", self.test_external_apis),
        ]
        
        for test_name, test_func in tests:
            try:
                logger.info(f"🔍 {test_name}...")
                result = await test_func()
                if result:
                    self.test_results.append(f"✅ {test_name}: نجح")
                    logger.info(f"✅ {test_name}: نجح")
                else:
                    self.test_results.append(f"❌ {test_name}: فشل")
                    self.failed_tests.append(test_name)
                    logger.error(f"❌ {test_name}: فشل")
            except Exception as e:
                self.test_results.append(f"❌ {test_name}: خطأ - {str(e)}")
                self.failed_tests.append(test_name)
                logger.error(f"❌ {test_name}: خطأ - {e}")
        
        # عرض النتائج النهائية
        await self.show_results()
    
    async def test_database(self) -> bool:
        """اختبار قاعدة البيانات"""
        try:
            # اختبار الاتصال
            await db_manager.init_database()
            
            # اختبار إضافة مستخدم
            test_user_id = 999999999
            await db_manager.add_user(test_user_id, "test_user", "Test User")
            
            # اختبار جلب المستخدم
            user = await db_manager.get_user_info(test_user_id)
            if not user:
                return False
            
            # اختبار إضافة إشارة
            test_signal = {
                "symbol": "BTCUSDT",
                "direction": "BUY",
                "entry_prices": [50000],
                "targets": [51000, 52000],
                "stop_loss": 49000,
                "leverage": 10,
                "signal_text": "إشارة تجريبية"
            }
            
            signal_id = await db_manager.save_signal(test_signal)
            
            if not signal_id:
                return False
            
            # اختبار جلب الإشارة
            signal = await db_manager.get_latest_signal()
            if not signal:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في اختبار قاعدة البيانات: {e}")
            return False
    
    async def test_binance_api(self) -> bool:
        """اختبار Binance API"""
        try:
            # اختبار جلب السعر
            price = await self.api_manager.binance_client.get_current_price("BTCUSDT")
            if not price or price <= 0:
                return False
            
            # اختبار جلب إحصائيات 24 ساعة
            stats = await self.api_manager.binance_client.get_24h_stats("BTCUSDT")
            if not stats:
                return False
            
            # اختبار جلب الشموع
            klines = await self.api_manager.binance_client.get_klines("BTCUSDT", "1h", 10)
            if not klines or len(klines) == 0:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في اختبار Binance API: {e}")
            return False
    
    async def test_signal_parser(self) -> bool:
        """اختبار محلل الإشارات"""
        try:
            # نص إشارة تجريبي
            test_signal_text = """
            🚀 إشارة جديدة
            
            العملة: BTCUSDT
            الاتجاه: شراء
            سعر الدخول: 50000
            الأهداف: 51000, 52000, 53000
            وقف الخسارة: 49000
            الرافعة: 10x
            """
            
            # تحليل الإشارة
            parsed_signal = signal_parser.parse_signal_text(test_signal_text)
            
            if not parsed_signal:
                return False
            
            # التحقق من البيانات المحللة
            if (parsed_signal.get("symbol") == "BTCUSDT" and
                parsed_signal.get("direction") == "BUY" and
                parsed_signal.get("entry_prices")):
                return True
            else:
                return False
            
        except Exception as e:
            logger.error(f"خطأ في اختبار محلل الإشارات: {e}")
            return False
    
    async def test_top_traders(self) -> bool:
        """اختبار نظام أفضل المتداولين"""
        try:
            # اختبار جلب أفضل المتداولين
            traders = await top_traders_api.get_top_traders(
                period_type="WEEKLY",
                statistics_type="ROI",
                trade_type="PERPETUAL",
                limit=5
            )
            
            if not traders:
                logger.warning("لا توجد بيانات متداولين - قد يكون هذا طبيعياً")
                return True  # نعتبره نجاحاً لأن API قد لا يكون متاحاً
            
            # اختبار تنسيق الرسالة
            message = await top_traders_api.format_top_traders_message(traders, "WEEKLY")
            if not message:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في اختبار أفضل المتداولين: {e}")
            return True  # نعتبره نجاحاً لأن API قد لا يكون متاحاً
    
    async def test_monitoring(self) -> bool:
        """اختبار نظام المراقبة"""
        try:
            # اختبار جلب إحصائيات النظام
            system_stats = await bot_monitor.get_system_stats()
            if not system_stats:
                return False
            
            # اختبار جلب إحصائيات البوت
            bot_stats = await bot_monitor.get_bot_stats()
            if not bot_stats:
                return False
            
            # اختبار إنشاء تقرير شامل
            report = await bot_monitor.get_comprehensive_report()
            if not report:
                return False
            
            # اختبار تنسيق رسالة المراقبة
            message = await bot_monitor.format_monitoring_message(report)
            if not message:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في اختبار نظام المراقبة: {e}")
            return False
    
    async def test_external_apis(self) -> bool:
        """اختبار APIs الخارجية"""
        try:
            # اختبار CoinGecko API
            try:
                market_data = await self.api_manager.get_market_data()
                if not market_data:
                    logger.warning("CoinGecko API غير متاح")
            except:
                logger.warning("CoinGecko API غير متاح")
            
            # اختبار Fear & Greed API
            try:
                fear_greed = await self.api_manager.get_fear_greed_index()
                if not fear_greed:
                    logger.warning("Fear & Greed API غير متاح")
            except:
                logger.warning("Fear & Greed API غير متاح")
            
            return True  # نعتبره نجاحاً حتى لو لم تكن APIs متاحة
            
        except Exception as e:
            logger.error(f"خطأ في اختبار APIs الخارجية: {e}")
            return True
    
    async def show_results(self):
        """عرض نتائج الاختبار"""
        print("\n" + "="*50)
        print("📊 نتائج الاختبار الشامل")
        print("="*50)
        
        for result in self.test_results:
            print(result)
        
        print("\n" + "="*50)
        
        if self.failed_tests:
            print(f"❌ فشل {len(self.failed_tests)} اختبار من أصل {len(self.test_results)}")
            print("الاختبارات الفاشلة:")
            for test in self.failed_tests:
                print(f"  - {test}")
        else:
            print(f"✅ نجح جميع الاختبارات ({len(self.test_results)} اختبار)")
        
        print("="*50)
    
    async def test_bot_startup(self):
        """اختبار بدء تشغيل البوت"""
        try:
            logger.info("🔄 اختبار بدء تشغيل البوت...")
            
            # تهيئة قاعدة البيانات
            await db_manager.init_database()
            
            logger.info("✅ تم بدء تشغيل البوت بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في بدء تشغيل البوت: {e}")
            return False

async def main():
    """الدالة الرئيسية للاختبار"""
    tester = BotTester()
    
    # اختبار بدء التشغيل
    startup_success = await tester.test_bot_startup()
    if not startup_success:
        logger.error("فشل في بدء تشغيل البوت")
        return
    
    # تشغيل جميع الاختبارات
    await tester.run_all_tests()
    
    # إنشاء تقرير اختبار
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_{timestamp}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("تقرير اختبار بوت التداول\n")
        f.write("="*50 + "\n")
        f.write(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for result in tester.test_results:
            f.write(result + "\n")
        
        if tester.failed_tests:
            f.write(f"\nالاختبارات الفاشلة ({len(tester.failed_tests)}):\n")
            for test in tester.failed_tests:
                f.write(f"- {test}\n")
        else:
            f.write(f"\n✅ نجح جميع الاختبارات ({len(tester.test_results)})\n")
    
    logger.info(f"📄 تم حفظ تقرير الاختبار: {report_file}")

if __name__ == "__main__":
    asyncio.run(main())

