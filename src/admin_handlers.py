"""
معالجات الأوامر الإدارية المتقدمة
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from .keyboards import *
from .database import db_manager
from .signal_parser import signal_parser
from .monitoring import bot_monitor
from config.config import ADMIN_USER_ID, SYSTEM_MESSAGES

logger = logging.getLogger(__name__)

# حالات الإدارة المتقدمة
class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_user_id_add = State()
    waiting_for_user_id_remove = State()
    waiting_for_user_search = State()
    waiting_for_signal_edit = State()

# إنشاء راوتر الإدارة
admin_router = Router()

@admin_router.callback_query(F.data == "admin_panel")
async def show_admin_panel(callback: CallbackQuery):
    """عرض لوحة تحكم المسؤول"""
    try:
        user_id = callback.from_user.id
        
        if user_id != ADMIN_USER_ID:
            await callback.answer(SYSTEM_MESSAGES["admin_only"], show_alert=True)
            return
        
        await callback.answer()
        
        stats = await db_manager.get_stats()
        admin_message = f"""🔧 **لوحة تحكم المسؤول**

📊 **الإحصائيات:**
• المستخدمون الإجمالي: {stats.get('total_users', 0)}
• المستخدمون المصرح لهم: {stats.get('allowed_users', 0)}
• الإشارات الإجمالية: {stats.get('total_signals', 0)}
• الإشارات النشطة: {stats.get('active_signals', 0)}

اختر العملية المطلوبة من الأزرار أدناه:"""
        
        await callback.message.edit_text(
            admin_message,
            reply_markup=get_admin_keyboard(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في عرض لوحة تحكم المسؤول: {e}")
        await callback.answer("حدث خطأ", show_alert=True)

@admin_router.callback_query(F.data == "admin_stats")
async def show_detailed_stats(callback: CallbackQuery):
    """عرض الإحصائيات المفصلة"""
    try:
        user_id = callback.from_user.id
        
        if user_id != ADMIN_USER_ID:
            await callback.answer(SYSTEM_MESSAGES["admin_only"], show_alert=True)
            return
        
        await callback.answer("جاري جلب الإحصائيات...")
        
        stats = await db_manager.get_stats()
        
        # إحصائيات إضافية
        # يمكن إضافة المزيد من الاستعلامات هنا
        
        stats_message = f"""📊 **الإحصائيات التفصيلية**

👥 **المستخدمون:**
• العدد الإجمالي: {stats.get('total_users', 0)}
• المصرح لهم: {stats.get('allowed_users', 0)}
• النشطون اليوم: قيد التطوير

📈 **الإشارات:**
• العدد الإجمالي: {stats.get('total_signals', 0)}
• النشطة: {stats.get('active_signals', 0)}
• المكتملة: {stats.get('total_signals', 0) - stats.get('active_signals', 0)}

📤 **الرسائل:**
• المرسلة اليوم: قيد التطوير
• معدل النجاح: قيد التطوير

⏰ **آخر تحديث:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
        await callback.message.edit_text(
            stats_message,
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في عرض الإحصائيات: {e}")
        await callback.answer("حدث خطأ في جلب الإحصائيات", show_alert=True)

@admin_router.callback_query(F.data == "admin_users")
async def show_user_management(callback: CallbackQuery):
    """عرض إدارة المستخدمين"""
    try:
        user_id = callback.from_user.id
        
        if user_id != ADMIN_USER_ID:
            await callback.answer(SYSTEM_MESSAGES["admin_only"], show_alert=True)
            return
        
        await callback.answer()
        
        await callback.message.edit_text(
            """👥 **إدارة المستخدمين**

اختر العملية المطلوبة:

• **إضافة مستخدم** - إضافة مستخدم جديد للقائمة المصرح لها
• **إزالة مستخدم** - إزالة مستخدم من القائمة المصرح لها  
• **قائمة المستخدمين** - عرض جميع المستخدمين المصرح لهم
• **بحث عن مستخدم** - البحث عن مستخدم معين""",
            reply_markup=get_user_management_keyboard(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في عرض إدارة المستخدمين: {e}")
        await callback.answer("حدث خطأ", show_alert=True)

@admin_router.callback_query(F.data == "admin_add_user")
async def add_user_prompt(callback: CallbackQuery, state: FSMContext):
    """طلب إضافة مستخدم"""
    try:
        user_id = callback.from_user.id
        
        if user_id != ADMIN_USER_ID:
            await callback.answer(SYSTEM_MESSAGES["admin_only"], show_alert=True)
            return
        
        await callback.answer()
        await state.set_state(AdminStates.waiting_for_user_id_add)
        
        await callback.message.edit_text(
            """➕ **إضافة مستخدم جديد**

يرجى إرسال رقم المستخدم (User ID) الذي تريد إضافته إلى القائمة المصرح لها.

**مثال:** 123456789

**ملاحظة:** يمكنك الحصول على رقم المستخدم عن طريق:
1. طلب المستخدم إرسال أمر /start
2. استخدام @userinfobot في تليجرام
3. من رسائل المستخدم في السجلات

أرسل رقم المستخدم الآن:""",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في طلب إضافة مستخدم: {e}")
        await callback.answer("حدث خطأ", show_alert=True)

@admin_router.message(StateFilter(AdminStates.waiting_for_user_id_add))
async def process_add_user(message: Message, state: FSMContext):
    """معالجة إضافة مستخدم"""
    try:
        admin_id = message.from_user.id
        
        if admin_id != ADMIN_USER_ID:
            await message.answer(SYSTEM_MESSAGES["admin_only"])
            return
        
        try:
            user_id_to_add = int(message.text.strip())
        except ValueError:
            await message.answer("❌ رقم المستخدم غير صحيح. يرجى إرسال رقم صحيح.")
            return
        
        # التحقق من وجود المستخدم مسبقاً
        is_already_allowed = await db_manager.is_user_allowed(user_id_to_add)
        
        if is_already_allowed:
            await message.answer(f"⚠️ المستخدم {user_id_to_add} موجود بالفعل في القائمة المصرح لها.")
            await state.clear()
            return
        
        # إضافة المستخدم
        success = await db_manager.add_allowed_user(user_id_to_add, admin_id)
        
        if success:
            # محاولة إرسال رسالة ترحيب للمستخدم الجديد
            try:
                await message.bot.send_message(
                    user_id_to_add,
                    """🎉 **مرحباً بك!**

تم منحك الوصول إلى بوت إشارات التداول الاحترافي.

يمكنك الآن استخدام جميع ميزات البوت والحصول على الإشارات المجانية.

اضغط /start للبدء!""",
                    parse_mode="Markdown"
                )
                welcome_status = "✅ تم إرسال رسالة ترحيب"
            except Exception as e:
                welcome_status = "⚠️ لم يتم إرسال رسالة ترحيب (المستخدم قد يكون حظر البوت)"
                logger.warning(f"فشل في إرسال رسالة ترحيب للمستخدم {user_id_to_add}: {e}")
            
            await message.answer(
                f"""✅ **تم إضافة المستخدم بنجاح**

**رقم المستخدم:** {user_id_to_add}
**تاريخ الإضافة:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**أضيف بواسطة:** {admin_id}

{welcome_status}""",
                parse_mode="Markdown"
            )
        else:
            await message.answer("❌ فشل في إضافة المستخدم. يرجى المحاولة مرة أخرى.")
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"خطأ في معالجة إضافة مستخدم: {e}")
        await message.answer("حدث خطأ في إضافة المستخدم")
        await state.clear()

@admin_router.callback_query(F.data == "admin_remove_user")
async def remove_user_prompt(callback: CallbackQuery, state: FSMContext):
    """طلب إزالة مستخدم"""
    try:
        user_id = callback.from_user.id
        
        if user_id != ADMIN_USER_ID:
            await callback.answer(SYSTEM_MESSAGES["admin_only"], show_alert=True)
            return
        
        await callback.answer()
        await state.set_state(AdminStates.waiting_for_user_id_remove)
        
        await callback.message.edit_text(
            """➖ **إزالة مستخدم**

يرجى إرسال رقم المستخدم (User ID) الذي تريد إزالته من القائمة المصرح لها.

**تحذير:** بعد الإزالة، لن يتمكن المستخدم من استقبال الإشارات أو استخدام البوت.

أرسل رقم المستخدم الآن:""",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في طلب إزالة مستخدم: {e}")
        await callback.answer("حدث خطأ", show_alert=True)

@admin_router.message(StateFilter(AdminStates.waiting_for_user_id_remove))
async def process_remove_user(message: Message, state: FSMContext):
    """معالجة إزالة مستخدم"""
    try:
        admin_id = message.from_user.id
        
        if admin_id != ADMIN_USER_ID:
            await message.answer(SYSTEM_MESSAGES["admin_only"])
            return
        
        try:
            user_id_to_remove = int(message.text.strip())
        except ValueError:
            await message.answer("❌ رقم المستخدم غير صحيح. يرجى إرسال رقم صحيح.")
            return
        
        # التحقق من وجود المستخدم
        is_allowed = await db_manager.is_user_allowed(user_id_to_remove)
        
        if not is_allowed:
            await message.answer(f"⚠️ المستخدم {user_id_to_remove} غير موجود في القائمة المصرح لها.")
            await state.clear()
            return
        
        # إزالة المستخدم
        success = await db_manager.remove_allowed_user(user_id_to_remove)
        
        if success:
            # إرسال رسالة إشعار للمستخدم المحذوف
            try:
                await message.bot.send_message(
                    user_id_to_remove,
                    """📢 **إشعار هام**

تم إيقاف وصولك إلى بوت إشارات التداول.

إذا كان هذا خطأ، يرجى التواصل مع الإدارة.

شكراً لاستخدامك البوت.""",
                    parse_mode="Markdown"
                )
                notification_status = "✅ تم إرسال إشعار للمستخدم"
            except Exception as e:
                notification_status = "⚠️ لم يتم إرسال إشعار (المستخدم قد يكون حظر البوت)"
                logger.warning(f"فشل في إرسال إشعار للمستخدم {user_id_to_remove}: {e}")
            
            await message.answer(
                f"""✅ **تم إزالة المستخدم بنجاح**

**رقم المستخدم:** {user_id_to_remove}
**تاريخ الإزالة:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**أزيل بواسطة:** {admin_id}

{notification_status}""",
                parse_mode="Markdown"
            )
        else:
            await message.answer("❌ فشل في إزالة المستخدم. يرجى المحاولة مرة أخرى.")
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"خطأ في معالجة إزالة مستخدم: {e}")
        await message.answer("حدث خطأ في إزالة المستخدم")
        await state.clear()

@admin_router.callback_query(F.data == "admin_list_users")
async def list_allowed_users(callback: CallbackQuery):
    """عرض قائمة المستخدمين المصرح لهم"""
    try:
        user_id = callback.from_user.id
        
        if user_id != ADMIN_USER_ID:
            await callback.answer(SYSTEM_MESSAGES["admin_only"], show_alert=True)
            return
        
        await callback.answer("جاري جلب قائمة المستخدمين...")
        
        allowed_users = await db_manager.get_allowed_users()
        
        if not allowed_users:
            await callback.message.edit_text(
                "📋 **قائمة المستخدمين المصرح لهم**\n\n❌ لا يوجد مستخدمون مصرح لهم حالياً.",
                reply_markup=get_back_keyboard(),
                parse_mode="Markdown"
            )
            return
        
        # تقسيم القائمة إلى صفحات (10 مستخدمين لكل صفحة)
        users_per_page = 10
        total_users = len(allowed_users)
        total_pages = (total_users + users_per_page - 1) // users_per_page
        
        # عرض الصفحة الأولى
        start_idx = 0
        end_idx = min(users_per_page, total_users)
        current_page_users = allowed_users[start_idx:end_idx]
        
        message = f"""📋 **قائمة المستخدمين المصرح لهم**

**العدد الإجمالي:** {total_users} مستخدم
**الصفحة:** 1 من {total_pages}

"""
        
        for i, user_id in enumerate(current_page_users, 1):
            message += f"{start_idx + i}. `{user_id}`\n"
        
        # إضافة أزرار التنقل إذا كان هناك أكثر من صفحة
        if total_pages > 1:
            keyboard = get_pagination_keyboard(1, total_pages, "admin_users")
        else:
            keyboard = get_back_keyboard()
        
        await callback.message.edit_text(
            message,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في عرض قائمة المستخدمين: {e}")
        await callback.answer("حدث خطأ في جلب القائمة", show_alert=True)

@admin_router.callback_query(F.data == "admin_broadcast")
async def broadcast_prompt(callback: CallbackQuery, state: FSMContext):
    """طلب إرسال رسالة عامة"""
    try:
        user_id = callback.from_user.id
        
        if user_id != ADMIN_USER_ID:
            await callback.answer(SYSTEM_MESSAGES["admin_only"], show_alert=True)
            return
        
        await callback.answer()
        await state.set_state(AdminStates.waiting_for_broadcast)
        
        await callback.message.edit_text(
            """📢 **إرسال رسالة عامة**

يرجى كتابة الرسالة التي تريد إرسالها لجميع المستخدمين المصرح لهم.

**ملاحظات:**
• يمكن استخدام تنسيق Markdown
• تجنب الرسائل الطويلة جداً
• تأكد من المحتوى قبل الإرسال

**مثال:**
```
📢 إعلان هام

نحيطكم علماً بأنه سيتم تحديث البوت غداً من الساعة 2:00 إلى 3:00 صباحاً.

شكراً لتفهمكم.
```

اكتب رسالتك الآن:""",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في طلب الرسالة العامة: {e}")
        await callback.answer("حدث خطأ", show_alert=True)

@admin_router.message(StateFilter(AdminStates.waiting_for_broadcast))
async def process_broadcast(message: Message, state: FSMContext):
    """معالجة الرسالة العامة"""
    try:
        admin_id = message.from_user.id
        
        if admin_id != ADMIN_USER_ID:
            await message.answer(SYSTEM_MESSAGES["admin_only"])
            return
        
        broadcast_message = message.text
        
        # حفظ الرسالة في الحالة للمعاينة
        await state.update_data(broadcast_message=broadcast_message)
        
        # عرض معاينة الرسالة
        preview_message = f"""📋 **معاينة الرسالة العامة:**

{broadcast_message}

---
**هل تريد إرسال هذه الرسالة لجميع المستخدمين؟**"""
        
        await message.answer(
            preview_message,
            reply_markup=get_broadcast_confirmation_keyboard(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في معالجة الرسالة العامة: {e}")
        await message.answer("حدث خطأ في معالجة الرسالة")
        await state.clear()

@admin_router.callback_query(F.data == "confirm_broadcast")
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext):
    """تأكيد إرسال الرسالة العامة"""
    try:
        user_id = callback.from_user.id
        
        if user_id != ADMIN_USER_ID:
            await callback.answer(SYSTEM_MESSAGES["admin_only"], show_alert=True)
            return
        
        # الحصول على الرسالة من الحالة
        state_data = await state.get_data()
        broadcast_message = state_data.get('broadcast_message')
        
        if not broadcast_message:
            await callback.answer("لا توجد رسالة للإرسال", show_alert=True)
            return
        
        await callback.answer("جاري إرسال الرسالة...")
        
        # الحصول على قائمة المستخدمين المصرح لهم
        allowed_users = await db_manager.get_allowed_users()
        
        if not allowed_users:
            await callback.message.edit_text(
                "❌ لا يوجد مستخدمون لإرسال الرسالة إليهم",
                reply_markup=get_back_keyboard()
            )
            await state.clear()
            return
        
        # إرسال الرسالة لجميع المستخدمين
        sent_count = 0
        failed_count = 0
        
        for target_user_id in allowed_users:
            try:
                await callback.bot.send_message(
                    target_user_id,
                    broadcast_message,
                    parse_mode="Markdown"
                )
                await db_manager.log_sent_message(target_user_id, "broadcast", broadcast_message, True)
                sent_count += 1
                
                # تأخير قصير لتجنب حد المعدل
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"فشل في إرسال الرسالة للمستخدم {target_user_id}: {e}")
                await db_manager.log_sent_message(target_user_id, "broadcast", broadcast_message, False)
                failed_count += 1
        
        # تقرير النتائج
        result_message = f"""✅ **تم إرسال الرسالة العامة**

📊 **تقرير الإرسال:**
• تم الإرسال بنجاح: {sent_count} مستخدم
• فشل الإرسال: {failed_count} مستخدم
• إجمالي المستهدفين: {len(allowed_users)} مستخدم
• معدل النجاح: {(sent_count / len(allowed_users) * 100):.1f}%

⏰ **وقت الإرسال:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
        await callback.message.edit_text(
            result_message,
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"خطأ في تأكيد الرسالة العامة: {e}")
        await callback.answer("حدث خطأ في إرسال الرسالة", show_alert=True)

@admin_router.callback_query(F.data == "cancel_broadcast")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    """إلغاء الرسالة العامة"""
    try:
        await callback.answer()
        await state.clear()
        await callback.message.edit_text(
            "❌ تم إلغاء إرسال الرسالة العامة",
            reply_markup=get_admin_keyboard()
        )
    except Exception as e:
        logger.error(f"خطأ في إلغاء الرسالة العامة: {e}")

@admin_router.callback_query(F.data == "admin_settings")
async def show_admin_settings(callback: CallbackQuery):
    """عرض إعدادات المسؤول"""
    try:
        user_id = callback.from_user.id
        
        if user_id != ADMIN_USER_ID:
            await callback.answer(SYSTEM_MESSAGES["admin_only"], show_alert=True)
            return
        
        await callback.answer()
        
        settings_message = """⚙️ **إعدادات المسؤول**

**الإعدادات الحالية:**
• وضع البوت: نشط ✅
• الإشارات التلقائية: مفعلة ✅
• التحقق من APIs: مفعل ✅
• حفظ السجلات: مفعل ✅

**إعدادات متقدمة:**
• نسخ احتياطي تلقائي: قيد التطوير
• تنبيهات المسؤول: مفعلة ✅
• وضع الصيانة: غير مفعل ❌

---
*ملاحظة: بعض الإعدادات قيد التطوير وستكون متاحة في التحديثات القادمة.*"""
        
        await callback.message.edit_text(
            settings_message,
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في عرض إعدادات المسؤول: {e}")
        await callback.answer("حدث خطأ", show_alert=True)

@admin_router.callback_query(F.data == "admin_logs")
async def show_admin_logs(callback: CallbackQuery):
    """عرض سجلات النظام"""
    try:
        user_id = callback.from_user.id
        
        if user_id != ADMIN_USER_ID:
            await callback.answer(SYSTEM_MESSAGES["admin_only"], show_alert=True)
            return
        
        await callback.answer("جاري جلب السجلات...")
        
        # قراءة آخر سجلات من ملف السجل
        try:
            with open('logs/bot.log', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                last_lines = lines[-10:]  # آخر 10 أسطر
                
            logs_text = ''.join(last_lines)
            
            logs_message = f"""📋 **سجلات النظام (آخر 10 إدخالات)**

```
{logs_text}
```

⏰ **آخر تحديث:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
        except FileNotFoundError:
            logs_message = """📋 **سجلات النظام**

❌ لم يتم العثور على ملف السجلات.

**الحالة:** البوت يعمل بشكل طبيعي
**آخر فحص:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
        await callback.message.edit_text(
            logs_message,
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في عرض السجلات: {e}")
        await callback.answer("حدث خطأ في جلب السجلات", show_alert=True)

# أوامر سريعة للمسؤول
@admin_router.message(Command("stats"))
async def quick_stats(message: Message):
    """إحصائيات سريعة"""
    try:
        user_id = message.from_user.id
        
        if user_id != ADMIN_USER_ID:
            await message.answer(SYSTEM_MESSAGES["admin_only"])
            return
        
        stats = await db_manager.get_stats()
        
        quick_stats_message = f"""📊 **إحصائيات سريعة**

👥 المستخدمون: {stats.get('allowed_users', 0)}
📈 الإشارات: {stats.get('total_signals', 0)}
🟢 النشطة: {stats.get('active_signals', 0)}

⏰ {datetime.now().strftime('%H:%M:%S')}"""
        
        await message.answer(quick_stats_message, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"خطأ في الإحصائيات السريعة: {e}")
        await message.answer("حدث خطأ في جلب الإحصائيات")

@admin_router.message(Command("users"))
async def quick_users_count(message: Message):
    """عدد المستخدمين السريع"""
    try:
        user_id = message.from_user.id
        
        if user_id != ADMIN_USER_ID:
            await message.answer(SYSTEM_MESSAGES["admin_only"])
            return
        
        allowed_users = await db_manager.get_allowed_users()
        count = len(allowed_users)
        
        await message.answer(f"👥 **عدد المستخدمين المصرح لهم:** {count}")
        
    except Exception as e:
        logger.error(f"خطأ في عدد المستخدمين السريع: {e}")
        await message.answer("حدث خطأ")

@admin_router.callback_query(F.data == "admin_monitoring")
async def show_system_monitoring(callback: CallbackQuery):
    """عرض مراقبة النظام"""
    try:
        user_id = callback.from_user.id
        
        if user_id != ADMIN_USER_ID:
            await callback.answer(SYSTEM_MESSAGES["admin_only"], show_alert=True)
            return
        
        await callback.answer("جاري جلب بيانات المراقبة...")
        
        # الحصول على تقرير شامل
        report = await bot_monitor.get_comprehensive_report()
        
        if report:
            message = await bot_monitor.format_monitoring_message(report)
            await callback.message.edit_text(
                message,
                reply_markup=get_monitoring_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await callback.message.edit_text(
                "❌ خطأ في جلب بيانات المراقبة",
                reply_markup=get_back_keyboard()
            )
            
    except Exception as e:
        logger.error(f"خطأ في عرض مراقبة النظام: {e}")
        await callback.answer("حدث خطأ في جلب البيانات", show_alert=True)

@admin_router.callback_query(F.data == "refresh_monitoring")
async def refresh_monitoring_data(callback: CallbackQuery):
    """تحديث بيانات المراقبة"""
    try:
        user_id = callback.from_user.id
        
        if user_id != ADMIN_USER_ID:
            await callback.answer(SYSTEM_MESSAGES["admin_only"], show_alert=True)
            return
        
        await callback.answer("جاري تحديث البيانات...")
        
        # الحصول على تقرير محدث
        report = await bot_monitor.get_comprehensive_report()
        
        if report:
            message = await bot_monitor.format_monitoring_message(report)
            await callback.message.edit_text(
                message,
                reply_markup=get_monitoring_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await callback.message.edit_text(
                "❌ خطأ في تحديث البيانات",
                reply_markup=get_monitoring_keyboard()
            )
            
    except Exception as e:
        logger.error(f"خطأ في تحديث بيانات المراقبة: {e}")
        await callback.answer("حدث خطأ في التحديث", show_alert=True)

@admin_router.message(Command("monitor"))
async def quick_monitor(message: Message):
    """مراقبة سريعة للنظام"""
    try:
        user_id = message.from_user.id
        
        if user_id != ADMIN_USER_ID:
            await message.answer(SYSTEM_MESSAGES["admin_only"])
            return
        
        # الحصول على إحصائيات سريعة
        system_stats = await bot_monitor.get_system_stats()
        
        if system_stats:
            cpu = system_stats.get("system", {}).get("cpu_usage", 0)
            memory = system_stats.get("system", {}).get("memory", {}).get("percent", 0)
            uptime = bot_monitor._format_uptime(system_stats.get("uptime", 0))
            
            quick_message = f"""🖥️ **مراقبة سريعة**

⚡ المعالج: {cpu:.1f}%
💾 الذاكرة: {memory:.1f}%
⏰ وقت التشغيل: {uptime}

✅ النظام يعمل بشكل طبيعي"""
            
            await message.answer(quick_message, parse_mode="Markdown")
        else:
            await message.answer("❌ خطأ في جلب بيانات المراقبة")
        
    except Exception as e:
        logger.error(f"خطأ في المراقبة السريعة: {e}")
        await message.answer("حدث خطأ في المراقبة")

