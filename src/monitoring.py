"""
نظام مراقبة وإحصائيات متقدم للبوت
"""
import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import psutil
import aiofiles

from .database import db_manager

logger = logging.getLogger(__name__)

class BotMonitor:
    """مراقب حالة البوت والإحصائيات"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.stats_cache = {}
        self.last_update = None
        self.monitoring_active = True
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات النظام"""
        try:
            # إحصائيات النظام
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # إحصائيات الشبكة
            network = psutil.net_io_counters()
            
            return {
                "system": {
                    "cpu_usage": cpu_percent,
                    "memory": {
                        "total": memory.total,
                        "available": memory.available,
                        "percent": memory.percent,
                        "used": memory.used
                    },
                    "disk": {
                        "total": disk.total,
                        "free": disk.free,
                        "used": disk.used,
                        "percent": (disk.used / disk.total) * 100
                    },
                    "network": {
                        "bytes_sent": network.bytes_sent,
                        "bytes_recv": network.bytes_recv,
                        "packets_sent": network.packets_sent,
                        "packets_recv": network.packets_recv
                    }
                },
                "uptime": (datetime.now() - self.start_time).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"خطأ في جلب إحصائيات النظام: {e}")
            return {}
    
    async def get_bot_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات البوت"""
        try:
            # إحصائيات قاعدة البيانات
            db_stats = await db_manager.get_detailed_stats()
            
            # إحصائيات الرسائل
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # حساب معدلات النجاح
            success_rate = await self._calculate_success_rate()
            
            return {
                "database": db_stats,
                "messages": {
                    "today": await db_manager.get_messages_count_by_date(today),
                    "this_week": await db_manager.get_messages_count_by_date_range(week_ago, today),
                    "this_month": await db_manager.get_messages_count_by_date_range(month_ago, today),
                    "success_rate": success_rate
                },
                "performance": {
                    "avg_response_time": await self._calculate_avg_response_time(),
                    "error_rate": await self._calculate_error_rate(),
                    "active_users_today": await db_manager.get_active_users_count(today)
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في جلب إحصائيات البوت: {e}")
            return {}
    
    async def get_comprehensive_report(self) -> Dict[str, Any]:
        """تقرير شامل عن حالة البوت"""
        try:
            system_stats = await self.get_system_stats()
            bot_stats = await self.get_bot_stats()
            
            # تحليل الاتجاهات
            trends = await self._analyze_trends()
            
            # تحديد المشاكل المحتملة
            issues = await self._detect_issues(system_stats, bot_stats)
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "system": system_stats,
                "bot": bot_stats,
                "trends": trends,
                "issues": issues,
                "recommendations": await self._generate_recommendations(issues)
            }
            
            # حفظ التقرير
            await self._save_report(report)
            
            return report
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء التقرير الشامل: {e}")
            return {}
    
    async def _calculate_success_rate(self) -> float:
        """حساب معدل نجاح الرسائل"""
        try:
            total_messages = await db_manager.get_total_sent_messages()
            successful_messages = await db_manager.get_successful_sent_messages()
            
            if total_messages > 0:
                return (successful_messages / total_messages) * 100
            return 0.0
            
        except Exception as e:
            logger.error(f"خطأ في حساب معدل النجاح: {e}")
            return 0.0
    
    async def _calculate_avg_response_time(self) -> float:
        """حساب متوسط وقت الاستجابة"""
        try:
            # يمكن تطوير هذا لاحقاً لقياس أوقات الاستجابة الفعلية
            return 0.5  # افتراضي 500ms
            
        except Exception as e:
            logger.error(f"خطأ في حساب متوسط وقت الاستجابة: {e}")
            return 0.0
    
    async def _calculate_error_rate(self) -> float:
        """حساب معدل الأخطاء"""
        try:
            # يمكن تطوير هذا لاحقاً لقياس معدل الأخطاء الفعلي
            return 0.1  # افتراضي 0.1%
            
        except Exception as e:
            logger.error(f"خطأ في حساب معدل الأخطاء: {e}")
            return 0.0
    
    async def _analyze_trends(self) -> Dict[str, Any]:
        """تحليل الاتجاهات"""
        try:
            # تحليل نمو المستخدمين
            user_growth = await self._analyze_user_growth()
            
            # تحليل نشاط الإشارات
            signal_activity = await self._analyze_signal_activity()
            
            return {
                "user_growth": user_growth,
                "signal_activity": signal_activity,
                "peak_hours": await self._analyze_peak_hours()
            }
            
        except Exception as e:
            logger.error(f"خطأ في تحليل الاتجاهات: {e}")
            return {}
    
    async def _analyze_user_growth(self) -> Dict[str, Any]:
        """تحليل نمو المستخدمين"""
        try:
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            users_today = await db_manager.get_new_users_count(today)
            users_week = await db_manager.get_new_users_count_range(week_ago, today)
            users_month = await db_manager.get_new_users_count_range(month_ago, today)
            
            return {
                "daily": users_today,
                "weekly": users_week,
                "monthly": users_month,
                "growth_rate": await self._calculate_growth_rate()
            }
            
        except Exception as e:
            logger.error(f"خطأ في تحليل نمو المستخدمين: {e}")
            return {}
    
    async def _analyze_signal_activity(self) -> Dict[str, Any]:
        """تحليل نشاط الإشارات"""
        try:
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            
            signals_today = await db_manager.get_signals_count_by_date(today)
            signals_week = await db_manager.get_signals_count_by_date_range(week_ago, today)
            
            return {
                "signals_today": signals_today,
                "signals_this_week": signals_week,
                "avg_per_day": signals_week / 7 if signals_week > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"خطأ في تحليل نشاط الإشارات: {e}")
            return {}
    
    async def _analyze_peak_hours(self) -> List[int]:
        """تحليل ساعات الذروة"""
        try:
            # تحليل الساعات الأكثر نشاطاً
            peak_hours = await db_manager.get_peak_activity_hours()
            return peak_hours or [9, 10, 11, 14, 15, 16, 20, 21]  # افتراضي
            
        except Exception as e:
            logger.error(f"خطأ في تحليل ساعات الذروة: {e}")
            return []
    
    async def _calculate_growth_rate(self) -> float:
        """حساب معدل النمو"""
        try:
            # حساب معدل النمو الأسبوعي
            this_week = await db_manager.get_new_users_count_range(
                datetime.now().date() - timedelta(days=7),
                datetime.now().date()
            )
            last_week = await db_manager.get_new_users_count_range(
                datetime.now().date() - timedelta(days=14),
                datetime.now().date() - timedelta(days=7)
            )
            
            if last_week > 0:
                return ((this_week - last_week) / last_week) * 100
            return 0.0
            
        except Exception as e:
            logger.error(f"خطأ في حساب معدل النمو: {e}")
            return 0.0
    
    async def _detect_issues(self, system_stats: Dict, bot_stats: Dict) -> List[Dict[str, Any]]:
        """اكتشاف المشاكل المحتملة"""
        issues = []
        
        try:
            # فحص استخدام الذاكرة
            if system_stats.get("system", {}).get("memory", {}).get("percent", 0) > 85:
                issues.append({
                    "type": "high_memory_usage",
                    "severity": "warning",
                    "message": "استخدام الذاكرة مرتفع",
                    "value": system_stats["system"]["memory"]["percent"]
                })
            
            # فحص استخدام المعالج
            if system_stats.get("system", {}).get("cpu_usage", 0) > 80:
                issues.append({
                    "type": "high_cpu_usage",
                    "severity": "warning",
                    "message": "استخدام المعالج مرتفع",
                    "value": system_stats["system"]["cpu_usage"]
                })
            
            # فحص مساحة القرص
            disk_percent = system_stats.get("system", {}).get("disk", {}).get("percent", 0)
            if disk_percent > 90:
                issues.append({
                    "type": "low_disk_space",
                    "severity": "critical",
                    "message": "مساحة القرص منخفضة",
                    "value": disk_percent
                })
            
            # فحص معدل نجاح الرسائل
            success_rate = bot_stats.get("messages", {}).get("success_rate", 100)
            if success_rate < 95:
                issues.append({
                    "type": "low_success_rate",
                    "severity": "warning",
                    "message": "معدل نجاح الرسائل منخفض",
                    "value": success_rate
                })
            
            return issues
            
        except Exception as e:
            logger.error(f"خطأ في اكتشاف المشاكل: {e}")
            return []
    
    async def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """إنشاء توصيات بناءً على المشاكل"""
        recommendations = []
        
        try:
            for issue in issues:
                if issue["type"] == "high_memory_usage":
                    recommendations.append("فكر في زيادة ذاكرة الخادم أو تحسين استخدام الذاكرة")
                elif issue["type"] == "high_cpu_usage":
                    recommendations.append("راقب العمليات المستهلكة للمعالج وفكر في ترقية الخادم")
                elif issue["type"] == "low_disk_space":
                    recommendations.append("احذف الملفات غير الضرورية أو قم بزيادة مساحة التخزين")
                elif issue["type"] == "low_success_rate":
                    recommendations.append("تحقق من اتصال الإنترنت وإعدادات Telegram API")
            
            if not recommendations:
                recommendations.append("النظام يعمل بشكل طبيعي")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء التوصيات: {e}")
            return ["خطأ في إنشاء التوصيات"]
    
    async def _save_report(self, report: Dict[str, Any]):
        """حفظ التقرير في ملف"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/reports/report_{timestamp}.json"
            
            # إنشاء مجلد التقارير إذا لم يكن موجوداً
            import os
            os.makedirs("data/reports", exist_ok=True)
            
            async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(report, ensure_ascii=False, indent=2))
            
            logger.info(f"تم حفظ التقرير: {filename}")
            
        except Exception as e:
            logger.error(f"خطأ في حفظ التقرير: {e}")
    
    async def format_monitoring_message(self, report: Dict[str, Any]) -> str:
        """تنسيق رسالة المراقبة للمسؤول"""
        try:
            system = report.get("system", {}).get("system", {})
            bot = report.get("bot", {})
            issues = report.get("issues", [])
            
            message = f"""🖥️ **تقرير حالة النظام**

**⚡ النظام:**
• المعالج: {system.get('cpu_usage', 0):.1f}%
• الذاكرة: {system.get('memory', {}).get('percent', 0):.1f}%
• القرص: {system.get('disk', {}).get('percent', 0):.1f}%

**🤖 البوت:**
• المستخدمون: {bot.get('database', {}).get('total_users', 0)}
• الإشارات: {bot.get('database', {}).get('total_signals', 0)}
• معدل النجاح: {bot.get('messages', {}).get('success_rate', 0):.1f}%

**📊 الأداء:**
• وقت التشغيل: {self._format_uptime(report.get('system', {}).get('uptime', 0))}
• المستخدمون النشطون اليوم: {bot.get('performance', {}).get('active_users_today', 0)}

"""
            
            if issues:
                message += "⚠️ **تنبيهات:**\n"
                for issue in issues[:3]:  # أول 3 مشاكل
                    severity_emoji = "🔴" if issue["severity"] == "critical" else "🟡"
                    message += f"{severity_emoji} {issue['message']}\n"
                message += "\n"
            else:
                message += "✅ **لا توجد مشاكل**\n\n"
            
            message += f"⏰ **وقت التقرير:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return message
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق رسالة المراقبة: {e}")
            return "❌ خطأ في إنشاء تقرير المراقبة"
    
    def _format_uptime(self, uptime_seconds: float) -> str:
        """تنسيق وقت التشغيل"""
        try:
            uptime = timedelta(seconds=int(uptime_seconds))
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            if days > 0:
                return f"{days} يوم، {hours} ساعة"
            elif hours > 0:
                return f"{hours} ساعة، {minutes} دقيقة"
            else:
                return f"{minutes} دقيقة"
                
        except Exception as e:
            logger.error(f"خطأ في تنسيق وقت التشغيل: {e}")
            return "غير محدد"
    
    async def start_monitoring(self, interval: int = 300):
        """بدء المراقبة التلقائية (كل 5 دقائق افتراضياً)"""
        logger.info("بدء مراقبة النظام...")
        
        while self.monitoring_active:
            try:
                # إنشاء تقرير دوري
                report = await self.get_comprehensive_report()
                
                # حفظ الإحصائيات في الكاش
                self.stats_cache = report
                self.last_update = datetime.now()
                
                # انتظار الفترة المحددة
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"خطأ في المراقبة التلقائية: {e}")
                await asyncio.sleep(60)  # انتظار دقيقة في حالة الخطأ
    
    def stop_monitoring(self):
        """إيقاف المراقبة التلقائية"""
        self.monitoring_active = False
        logger.info("تم إيقاف مراقبة النظام")

# إنشاء مثيل عام
bot_monitor = BotMonitor()

