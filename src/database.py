"""
إدارة قاعدة البيانات لبوت التداول
"""
import sqlite3
import aiosqlite
import asyncio
from datetime import datetime
import json
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "data/trading_bot.db"):
        self.db_path = db_path
        
    async def init_database(self):
        """إنشاء الجداول الأساسية"""
        async with aiosqlite.connect(self.db_path) as db:
            # جدول المستخدمين
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    username TEXT,
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول المستخدمين المصرح لهم
            await db.execute("""
                CREATE TABLE IF NOT EXISTS allowed_users (
                    user_id INTEGER PRIMARY KEY,
                    added_by INTEGER,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_premium INTEGER DEFAULT 0,
                    premium_expires TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # جدول الإشارات
            await db.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    signal_text TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    entry_price_min REAL,
                    entry_price_max REAL,
                    stop_loss REAL,
                    targets TEXT,  -- JSON array
                    support_levels TEXT,  -- JSON array
                    resistance_levels TEXT,  -- JSON array
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    is_active INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'active'  -- active, completed, cancelled
                )
            """)
            
            # جدول إحصائيات الإشارات
            await db.execute("""
                CREATE TABLE IF NOT EXISTS signal_stats (
                    signal_id INTEGER PRIMARY KEY,
                    current_price REAL,
                    targets_hit INTEGER DEFAULT 0,
                    max_profit_percent REAL DEFAULT 0,
                    is_stop_loss_hit INTEGER DEFAULT 0,
                    final_result TEXT,  -- profit, loss, pending
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (signal_id) REFERENCES signals (id)
                )
            """)
            
            # جدول الرسائل المرسلة
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sent_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message_type TEXT,  -- signal, broadcast, notification
                    message_text TEXT,
                    sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_successful INTEGER DEFAULT 1
                )
            """)
            
            # جدول إعدادات النظام
            await db.execute("""
                CREATE TABLE IF NOT EXISTS system_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.commit()
            logger.info("تم إنشاء قاعدة البيانات بنجاح")

    async def add_user(self, user_id: int, first_name: str = None, username: str = None) -> bool:
        """إضافة مستخدم جديد"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR IGNORE INTO users (user_id, first_name, username)
                    VALUES (?, ?, ?)
                """, (user_id, first_name, username))
                await db.commit()
                logger.info(f"تم إضافة المستخدم {user_id}")
                return True
        except Exception as e:
            logger.error(f"خطأ في إضافة المستخدم: {e}")
            return False

    async def add_allowed_user(self, user_id: int, added_by: int = None) -> bool:
        """إضافة مستخدم إلى القائمة المصرح لها"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR IGNORE INTO allowed_users (user_id, added_by)
                    VALUES (?, ?)
                """, (user_id, added_by))
                await db.commit()
                logger.info(f"تم إضافة المستخدم {user_id} إلى القائمة المصرح لها")
                return True
        except Exception as e:
            logger.error(f"خطأ في إضافة المستخدم للقائمة المصرح لها: {e}")
            return False

    async def remove_allowed_user(self, user_id: int) -> bool:
        """إزالة مستخدم من القائمة المصرح لها"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("DELETE FROM allowed_users WHERE user_id = ?", (user_id,))
                await db.commit()
                logger.info(f"تم إزالة المستخدم {user_id} من القائمة المصرح لها")
                return True
        except Exception as e:
            logger.error(f"خطأ في إزالة المستخدم من القائمة المصرح لها: {e}")
            return False

    async def is_user_allowed(self, user_id: int) -> bool:
        """التحقق من صلاحية المستخدم"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM allowed_users 
                    WHERE user_id = ?
                """, (user_id,))
                result = await cursor.fetchone()
                return result[0] > 0
        except Exception as e:
            logger.error(f"خطأ في التحقق من صلاحية المستخدم: {e}")
            return False

    async def get_allowed_users(self) -> List[int]:
        """الحصول على قائمة المستخدمين المصرح لهم"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT user_id FROM allowed_users")
                results = await cursor.fetchall()
                return [row[0] for row in results]
        except Exception as e:
            logger.error(f"خطأ في الحصول على قائمة المستخدمين المصرح لهم: {e}")
            return []

    async def save_signal(self, signal_data: Dict) -> int:
        """حفظ إشارة جديدة"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO signals (
                        signal_text, symbol, direction, entry_price_min, entry_price_max,
                        stop_loss, targets, support_levels, resistance_levels, created_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    signal_data.get('signal_text'),
                    signal_data.get('symbol'),
                    signal_data.get('direction'),
                    signal_data.get('entry_price_min'),
                    signal_data.get('entry_price_max'),
                    signal_data.get('stop_loss'),
                    json.dumps(signal_data.get('targets', [])),
                    json.dumps(signal_data.get('support_levels', [])),
                    json.dumps(signal_data.get('resistance_levels', [])),
                    signal_data.get('created_by')
                ))
                signal_id = cursor.lastrowid
                await db.commit()
                logger.info(f"تم حفظ الإشارة {signal_id}")
                return signal_id
        except Exception as e:
            logger.error(f"خطأ في حفظ الإشارة: {e}")
            return 0

    async def get_latest_signal(self) -> Optional[Dict]:
        """الحصول على آخر إشارة"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT * FROM signals 
                    WHERE is_active = 1 
                    ORDER BY created_date DESC 
                    LIMIT 1
                """)
                result = await cursor.fetchone()
                if result:
                    columns = [description[0] for description in cursor.description]
                    signal_dict = dict(zip(columns, result))
                    # تحويل JSON strings إلى lists
                    signal_dict['targets'] = json.loads(signal_dict.get('targets', '[]'))
                    signal_dict['support_levels'] = json.loads(signal_dict.get('support_levels', '[]'))
                    signal_dict['resistance_levels'] = json.loads(signal_dict.get('resistance_levels', '[]'))
                    return signal_dict
                return None
        except Exception as e:
            logger.error(f"خطأ في الحصول على آخر إشارة: {e}")
            return None

    async def update_user_activity(self, user_id: int):
        """تحديث آخر نشاط للمستخدم"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE users SET last_activity = CURRENT_TIMESTAMP 
                    WHERE user_id = ?
                """, (user_id,))
                await db.commit()
        except Exception as e:
            logger.error(f"خطأ في تحديث نشاط المستخدم: {e}")

    async def get_user_info(self, user_id: int) -> Optional[Dict]:
        """الحصول على معلومات المستخدم"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT u.*, au.is_premium, au.premium_expires, au.added_date
                    FROM users u
                    LEFT JOIN allowed_users au ON u.user_id = au.user_id
                    WHERE u.user_id = ?
                """, (user_id,))
                result = await cursor.fetchone()
                if result:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, result))
                return None
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات المستخدم: {e}")
            return None

    async def log_sent_message(self, user_id: int, message_type: str, message_text: str, is_successful: bool = True):
        """تسجيل الرسائل المرسلة"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO sent_messages (user_id, message_type, message_text, is_successful)
                    VALUES (?, ?, ?, ?)
                """, (user_id, message_type, message_text[:500], 1 if is_successful else 0))
                await db.commit()
        except Exception as e:
            logger.error(f"خطأ في تسجيل الرسالة المرسلة: {e}")

    async def get_system_setting(self, key: str) -> Optional[str]:
        """الحصول على إعداد النظام"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT value FROM system_settings WHERE key = ?", (key,))
                result = await cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"خطأ في الحصول على إعداد النظام: {e}")
            return None

    async def set_system_setting(self, key: str, value: str):
        """تعيين إعداد النظام"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO system_settings (key, value, updated_date)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (key, value))
                await db.commit()
        except Exception as e:
            logger.error(f"خطأ في تعيين إعداد النظام: {e}")

    async def get_stats(self) -> Dict:
        """الحصول على إحصائيات عامة"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                stats = {}
                
                # عدد المستخدمين الإجمالي
                cursor = await db.execute("SELECT COUNT(*) FROM users")
                stats['total_users'] = (await cursor.fetchone())[0]
                
                # عدد المستخدمين المصرح لهم
                cursor = await db.execute("SELECT COUNT(*) FROM allowed_users")
                stats['allowed_users'] = (await cursor.fetchone())[0]
                
                # عدد الإشارات الإجمالي
                cursor = await db.execute("SELECT COUNT(*) FROM signals")
                stats['total_signals'] = (await cursor.fetchone())[0]
                
                # عدد الإشارات النشطة
                cursor = await db.execute("SELECT COUNT(*) FROM signals WHERE is_active = 1")
                stats['active_signals'] = (await cursor.fetchone())[0]
                
                return stats
        except Exception as e:
            logger.error(f"خطأ في الحصول على الإحصائيات: {e}")
            return {}

    async def get_detailed_stats(self) -> Dict:
        """الحصول على إحصائيات مفصلة للنظام"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                stats = {}
                
                # إحصائيات المستخدمين
                cursor = await db.execute("SELECT COUNT(*) FROM users")
                stats['total_users'] = (await cursor.fetchone())[0]
                
                cursor = await db.execute("SELECT COUNT(*) FROM allowed_users")
                stats['allowed_users'] = (await cursor.fetchone())[0]
                
                cursor = await db.execute("SELECT COUNT(*) FROM allowed_users WHERE is_premium = 1")
                stats['premium_users'] = (await cursor.fetchone())[0]
                
                # إحصائيات الإشارات
                cursor = await db.execute("SELECT COUNT(*) FROM signals")
                stats['total_signals'] = (await cursor.fetchone())[0]
                
                cursor = await db.execute("SELECT COUNT(*) FROM signals WHERE is_active = 1")
                stats['active_signals'] = (await cursor.fetchone())[0]
                
                cursor = await db.execute("SELECT COUNT(*) FROM signals WHERE created_date >= date('now', '-7 days')")
                stats['signals_last_week'] = (await cursor.fetchone())[0]
                
                cursor = await db.execute("SELECT COUNT(*) FROM signals WHERE created_date >= date('now', '-30 days')")
                stats['signals_last_month'] = (await cursor.fetchone())[0]
                
                # إحصائيات النشاط
                cursor = await db.execute("SELECT COUNT(*) FROM users WHERE last_activity >= datetime('now', '-24 hours')")
                stats['active_users_24h'] = (await cursor.fetchone())[0]
                
                cursor = await db.execute("SELECT COUNT(*) FROM users WHERE last_activity >= datetime('now', '-7 days')")
                stats['active_users_week'] = (await cursor.fetchone())[0]
                
                # أحدث إشارة
                cursor = await db.execute("SELECT symbol, direction, created_date FROM signals ORDER BY created_date DESC LIMIT 1")
                latest_signal = await cursor.fetchone()
                if latest_signal:
                    stats['latest_signal'] = {
                        'symbol': latest_signal[0],
                        'type': latest_signal[1],
                        'date': latest_signal[2]
                    }
                
                return stats
        except Exception as e:
            logger.error(f"خطأ في الحصول على الإحصائيات المفصلة: {e}")
            return {}

# إنشاء مثيل عام لإدارة قاعدة البيانات
db_manager = DatabaseManager()

