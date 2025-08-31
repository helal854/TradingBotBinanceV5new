"""
معالجات أوامر البوت
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
from .api_clients import APIManager
from .signal_parser import signal_parser
from .admin_handlers import admin_router
from .top_traders_api import top_traders_api
from config.config import *

logger = logging.getLogger(__name__)

# حالات البوت
class BotStates(StatesGroup):
    waiting_for_signal = State()
    waiting_for_broadcast = State()
    waiting_for_user_id = State()
    waiting_for_admin_command = State()

# إنشاء الراوتر
router = Router()

# تهيئة مدير APIs
api_manager = APIManager(BINANCE_API_KEY, BINANCE_SECRET_KEY)

@router.message(Command("start"))
async def cmd_start(message: Message):
    """معالج أمر البدء"""
    try:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        username = message.from_user.username
        
        # إضافة المستخدم إلى قاعدة البيانات
        await db_manager.add_user(user_id, first_name, username)
        
        # في الإصدار المجاني، جميع المستخدمين مصرح لهم
        await db_manager.add_allowed_user(user_id)
        
        # تحديث آخر نشاط
        await db_manager.update_user_activity(user_id)
        
        # إرسال رسالة الترحيب
        await message.answer(
            SYSTEM_MESSAGES["welcome"],
            reply_markup=get_main_keyboard()
        )
        
        logger.info(f"مستخدم جديد بدأ البوت: {user_id}")
        
    except Exception as e:
        logger.error(f"خطأ في معالج البدء: {e}")
        await message.answer("حدث خطأ. يرجى المحاولة مرة أخرى.")

@router.callback_query(F.data == "signals")
async def show_signals(callback: CallbackQuery):
    """عرض آخر إشارة"""
    try:
        await callback.answer()
        
        # الحصول على آخر إشارة
        latest_signal = await db_manager.get_latest_signal()
        
        if latest_signal:
            # تنسيق الإشارة
            formatted_signal = signal_parser.format_signal_message(latest_signal)
            await callback.message.edit_text(
                formatted_signal,
                reply_markup=get_signal_actions_keyboard(latest_signal.get('id')),
                parse_mode="Markdown"
            )
        else:
            await callback.message.edit_text(
                SYSTEM_MESSAGES["no_signals"],
                reply_markup=get_back_keyboard()
            )
            
    except Exception as e:
        logger.error(f"خطأ في عرض الإشارات: {e}")
        await callback.answer("حدث خطأ في جلب الإشارات", show_alert=True)

@router.callback_query(F.data == "news")
async def show_market_news(callback: CallbackQuery):
    """عرض حالة السوق"""
    try:
        await callback.answer("جاري جلب بيانات السوق...")
        
        # الحصول على بيانات السوق الشاملة
        market_data = await api_manager.get_comprehensive_market_data()
        
        if market_data.get('market_data'):
            message = await format_market_message(market_data)
            await callback.message.edit_text(
                message,
                reply_markup=get_market_refresh_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await callback.message.edit_text(
                SYSTEM_MESSAGES["market_data_error"],
                reply_markup=get_back_keyboard()
            )
            
    except Exception as e:
        logger.error(f"خطأ في عرض أخبار السوق: {e}")
        await callback.answer("حدث خطأ في جلب بيانات السوق", show_alert=True)

@router.callback_query(F.data == "schedule")
async def show_economic_schedule(callback: CallbackQuery):
    """عرض الأجندة الاقتصادية"""
    try:
        await callback.answer("جاري جلب الأجندة الاقتصادية...")
        
        # الحصول على الأحداث الاقتصادية
        market_data = await api_manager.get_comprehensive_market_data()
        economic_events = market_data.get('economic_events')
        
        if economic_events:
            message = await format_economic_schedule_message(economic_events)
            await callback.message.edit_text(
                message,
                reply_markup=get_schedule_filter_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await callback.message.edit_text(
                SYSTEM_MESSAGES["schedule_data_error"],
                reply_markup=get_back_keyboard()
            )
            
    except Exception as e:
        logger.error(f"خطأ في عرض الأجندة الاقتصادية: {e}")
        await callback.answer("حدث خطأ في جلب الأجندة", show_alert=True)

@router.callback_query(F.data == "account")
async def show_account_info(callback: CallbackQuery):
    """عرض معلومات الحساب"""
    try:
        await callback.answer()
        
        user_id = callback.from_user.id
        user_info = await db_manager.get_user_info(user_id)
        
        if user_info:
            message = f"""👤 **حسابك الشخصي**

**🆔 رقم المستخدم:** {user_id}
**📅 تاريخ الانضمام:** {user_info.get('join_date', 'غير محدد')}

**🟢 حالة الاشتراك:** الإصدار **المجاني** مفعل.
✅ أنت تتلقى حاليًا **جميع إشاراتنا** بشكل كامل.

---
للاستفسارات أو المشاكل التقنية، يمكنك التواصل مع الدعم الفني."""
            
            await callback.message.edit_text(
                message,
                reply_markup=get_back_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await callback.message.edit_text(
                "حدث خطأ في جلب معلومات الحساب",
                reply_markup=get_back_keyboard()
            )
            
    except Exception as e:
        logger.error(f"خطأ في عرض معلومات الحساب: {e}")
        await callback.answer("حدث خطأ", show_alert=True)

@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    """عرض المساعدة"""
    try:
        await callback.answer()
        
        help_message = """❓ **مركز المساعدة**

أهلاً بك في صفحة المساعدة. إليك شرح الأوامر المتاحة:

• **/start** - إعادة عرض شاشة البداية والترحيب.
• **📈 الإشارات** - عرض آخر إشارة تداول تم نشرها.
• **🌡️ حالة السوق** - الاطلاع على تقرير مفصل عن حالة السوق الحالية.
• **📅 الأجندة الاقتصادية** - عرض الأجندة الاقتصادية للأسبوع القادم.
• **🏆 أفضل المتداولين** - عرض قائمة بأفضل المتداولين على Binance.
• **👤 حسابي** - الاطلاع على معلومات حسابك.
• **❓ المساعدة** - عرض هذه الرسالة.

---
إذا كانت لديك أي استفسارات أخرى أو واجهتك مشكلة تقنية، لا تتردد في التواصل مع فريق الدعم. نحن هنا لمساعدتك!"""
        
        await callback.message.edit_text(
            help_message,
            reply_markup=get_help_categories_keyboard(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في عرض المساعدة: {e}")
        await callback.answer("حدث خطأ", show_alert=True)

@router.callback_query(F.data == "top_traders")
async def show_top_traders(callback: CallbackQuery):
    """عرض أفضل المتداولين"""
    try:
        await callback.answer("جاري جلب بيانات أفضل المتداولين...")
        
        # الحصول على بيانات أفضل المتداولين (أسبوعي ROI افتراضياً)
        traders_data = await top_traders_api.get_top_traders(
            period_type="WEEKLY",
            statistics_type="ROI",
            trade_type="PERPETUAL",
            limit=10
        )
        
        if traders_data:
            message = await top_traders_api.format_top_traders_message(traders_data, "WEEKLY")
            await callback.message.edit_text(
                message,
                reply_markup=get_top_traders_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await callback.message.edit_text(
                SYSTEM_MESSAGES.get("top_traders_error", "❌ خطأ في جلب بيانات المتداولين"),
                reply_markup=get_back_keyboard()
            )
            
    except Exception as e:
        logger.error(f"خطأ في عرض أفضل المتداولين: {e}")
        await callback.answer("حدث خطأ في جلب البيانات", show_alert=True)

@router.callback_query(F.data.startswith("traders_"))
async def handle_traders_filter(callback: CallbackQuery):
    """معالجة فلاتر أفضل المتداولين"""
    try:
        await callback.answer("جاري تحديث البيانات...")
        
        filter_type = callback.data.replace("traders_", "")
        
        # تحديد المعاملات حسب النوع
        if filter_type == "weekly_roi":
            period_type, statistics_type = "WEEKLY", "ROI"
        elif filter_type == "weekly_pnl":
            period_type, statistics_type = "WEEKLY", "PNL"
        elif filter_type == "monthly_roi":
            period_type, statistics_type = "MONTHLY", "ROI"
        elif filter_type == "monthly_pnl":
            period_type, statistics_type = "MONTHLY", "PNL"
        elif filter_type == "most_followed":
            period_type, statistics_type = "WEEKLY", "FOLLOWERS"
        else:
            period_type, statistics_type = "WEEKLY", "ROI"
        
        # جلب البيانات
        traders_data = await top_traders_api.get_top_traders(
            period_type=period_type,
            statistics_type=statistics_type,
            trade_type="PERPETUAL",
            limit=10
        )
        
        if traders_data:
            message = await top_traders_api.format_top_traders_message(traders_data, period_type)
            await callback.message.edit_text(
                message,
                reply_markup=get_top_traders_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await callback.message.edit_text(
                "❌ لا توجد بيانات متاحة لهذا الفلتر",
                reply_markup=get_top_traders_keyboard()
            )
            
    except Exception as e:
        logger.error(f"خطأ في معالجة فلتر المتداولين: {e}")
        await callback.answer("حدث خطأ في تحديث البيانات", show_alert=True)

@router.callback_query(F.data == "refresh_traders")
async def refresh_traders_data(callback: CallbackQuery):
    """تحديث بيانات المتداولين"""
    try:
        await callback.answer("جاري تحديث البيانات...")
        
        # جلب بيانات محدثة
        traders_data = await top_traders_api.get_top_traders(
            period_type="WEEKLY",
            statistics_type="ROI",
            trade_type="PERPETUAL",
            limit=10
        )
        
        if traders_data:
            message = await top_traders_api.format_top_traders_message(traders_data, "WEEKLY")
            await callback.message.edit_text(
                message,
                reply_markup=get_top_traders_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await callback.message.edit_text(
                "❌ خطأ في تحديث البيانات",
                reply_markup=get_top_traders_keyboard()
            )
            
    except Exception as e:
        logger.error(f"خطأ في تحديث بيانات المتداولين: {e}")
        await callback.answer("حدث خطأ في التحديث", show_alert=True)

@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: CallbackQuery):
    """العودة للقائمة الرئيسية"""
    try:
        await callback.answer()
        await callback.message.edit_text(
            SYSTEM_MESSAGES["welcome"],
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"خطأ في العودة للقائمة الرئيسية: {e}")

@router.callback_query(F.data == "refresh")
async def refresh_data(callback: CallbackQuery):
    """تحديث البيانات"""
    try:
        await callback.answer("جاري تحديث البيانات...")
        await callback.message.edit_text(
            SYSTEM_MESSAGES["welcome"],
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"خطأ في تحديث البيانات: {e}")

# معالجات الأوامر الإدارية
@router.message(Command("admin"))
async def admin_panel(message: Message):
    """لوحة تحكم المسؤول"""
    try:
        user_id = message.from_user.id
        
        if user_id != ADMIN_USER_ID:
            await message.answer(SYSTEM_MESSAGES["admin_only"])
            return
        
        stats = await db_manager.get_stats()
        admin_message = f"""🔧 **لوحة تحكم المسؤول**

📊 **الإحصائيات:**
• المستخدمون الإجمالي: {stats.get('total_users', 0)}
• المستخدمون المصرح لهم: {stats.get('allowed_users', 0)}
• الإشارات الإجمالية: {stats.get('total_signals', 0)}
• الإشارات النشطة: {stats.get('active_signals', 0)}

اختر العملية المطلوبة من الأزرار أدناه:"""
        
        await message.answer(
            admin_message,
            reply_markup=get_admin_keyboard(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في لوحة تحكم المسؤول: {e}")
        await message.answer("حدث خطأ في الوصول للوحة التحكم")

@router.callback_query(F.data == "admin_send_signal")
async def admin_send_signal(callback: CallbackQuery, state: FSMContext):
    """إرسال إشارة جديدة"""
    try:
        user_id = callback.from_user.id
        
        if user_id != ADMIN_USER_ID:
            await callback.answer(SYSTEM_MESSAGES["admin_only"], show_alert=True)
            return
        
        await callback.answer()
        await state.set_state(BotStates.waiting_for_signal)
        
        await callback.message.edit_text(
            """📤 **إرسال إشارة جديدة**

يرجى إرسال نص الإشارة بالتنسيق المطلوب:

```
🎯 إشارة تداول - SPOT

الزوج: BTC/USDT
الاتجاه: BUY

نقطة الدخول: 61,500 - 61,800
وقف الخسارة: 60,900

أهداف البيع:
1️⃣ T1: 62,200
2️⃣ T2: 63,000
3️⃣ T3: 64,500

الدعم: 61,200 - 60,900
المقاومة: 63,000 - 64,500
```

أرسل النص الآن:""",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في إرسال إشارة: {e}")
        await callback.answer("حدث خطأ", show_alert=True)

@router.message(StateFilter(BotStates.waiting_for_signal))
async def process_new_signal(message: Message, state: FSMContext):
    """معالجة الإشارة الجديدة"""
    try:
        user_id = message.from_user.id
        
        if user_id != ADMIN_USER_ID:
            await message.answer(SYSTEM_MESSAGES["admin_only"])
            return
        
        signal_text = message.text
        
        # تحليل الإشارة
        parsed_signal = signal_parser.parse_signal_text(signal_text)
        
        if not parsed_signal['parsed_successfully']:
            error_message = "❌ فشل في تحليل الإشارة:\n\n"
            error_message += "\n".join(parsed_signal.get('errors', []))
            await message.answer(error_message)
            return
        
        # التحقق من صحة الإشارة
        current_price = None
        if parsed_signal['symbol']:
            current_price = await api_manager.binance.get_current_price(parsed_signal['symbol'])
        
        validation_result = signal_parser.validate_signal_data(parsed_signal, current_price)
        
        # تنسيق الإشارة للمعاينة
        formatted_signal = signal_parser.format_signal_message(parsed_signal, validation_result)
        
        # عرض المعاينة للمسؤول
        preview_message = f"📋 **معاينة الإشارة:**\n\n{formatted_signal}"
        
        if validation_result.get('warnings'):
            preview_message += "\n\n⚠️ **تحذيرات:**\n"
            preview_message += "\n".join(validation_result['warnings'])
        
        if current_price:
            preview_message += f"\n\n💰 **السعر الحالي:** {current_price:,.2f}"
        
        preview_message += "\n\n**هل تريد إرسال هذه الإشارة؟**"
        
        # حفظ بيانات الإشارة في الحالة
        await state.update_data(
            signal_data=parsed_signal,
            formatted_signal=formatted_signal,
            validation_result=validation_result
        )
        
        await message.answer(
            preview_message,
            reply_markup=get_signal_confirmation_keyboard(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في معالجة الإشارة الجديدة: {e}")
        await message.answer("حدث خطأ في معالجة الإشارة")

@router.callback_query(F.data == "confirm_signal")
async def confirm_send_signal(callback: CallbackQuery, state: FSMContext):
    """تأكيد إرسال الإشارة"""
    try:
        user_id = callback.from_user.id
        
        if user_id != ADMIN_USER_ID:
            await callback.answer(SYSTEM_MESSAGES["admin_only"], show_alert=True)
            return
        
        # الحصول على بيانات الإشارة
        state_data = await state.get_data()
        signal_data = state_data.get('signal_data')
        formatted_signal = state_data.get('formatted_signal')
        
        if not signal_data:
            await callback.answer("لا توجد بيانات إشارة", show_alert=True)
            return
        
        await callback.answer("جاري إرسال الإشارة...")
        
        # حفظ الإشارة في قاعدة البيانات
        signal_data['signal_text'] = formatted_signal
        signal_data['created_by'] = user_id
        signal_id = await db_manager.save_signal(signal_data)
        
        if signal_id:
            # إرسال الإشارة لجميع المستخدمين المصرح لهم
            allowed_users = await db_manager.get_allowed_users()
            sent_count = 0
            failed_count = 0
            
            for target_user_id in allowed_users:
                try:
                    await callback.bot.send_message(
                        target_user_id,
                        formatted_signal,
                        parse_mode="Markdown"
                    )
                    await db_manager.log_sent_message(target_user_id, "signal", formatted_signal, True)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"فشل في إرسال الإشارة للمستخدم {target_user_id}: {e}")
                    await db_manager.log_sent_message(target_user_id, "signal", formatted_signal, False)
                    failed_count += 1
            
            # تقرير النتائج للمسؤول
            result_message = f"""✅ **تم إرسال الإشارة بنجاح**

📊 **تقرير الإرسال:**
• تم الإرسال: {sent_count} مستخدم
• فشل الإرسال: {failed_count} مستخدم
• رقم الإشارة: {signal_id}"""
            
            await callback.message.edit_text(
                result_message,
                reply_markup=get_back_keyboard(),
                parse_mode="Markdown"
            )
        else:
            await callback.message.edit_text(
                "❌ فشل في حفظ الإشارة",
                reply_markup=get_back_keyboard()
            )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"خطأ في تأكيد إرسال الإشارة: {e}")
        await callback.answer("حدث خطأ في إرسال الإشارة", show_alert=True)

@router.callback_query(F.data == "cancel_signal")
async def cancel_signal(callback: CallbackQuery, state: FSMContext):
    """إلغاء إرسال الإشارة"""
    try:
        await callback.answer()
        await state.clear()
        await callback.message.edit_text(
            "❌ تم إلغاء إرسال الإشارة",
            reply_markup=get_admin_keyboard()
        )
    except Exception as e:
        logger.error(f"خطأ في إلغاء الإشارة: {e}")

# دوال مساعدة
async def format_market_message(market_data: Dict) -> str:
    """تنسيق رسالة حالة السوق"""
    try:
        message = "🌡️ **تقرير حالة السوق الآن**\n\n"
        
        # مؤشر الخوف والطمع
        fng_data = market_data.get('fear_greed_index')
        if fng_data:
            fng_value = fng_data['value']
            fng_classification = fng_data['value_classification']
            message += f"**📊 مؤشر الطمع والخوف (F&G Index):**\n"
            message += f"• **القيمة:** {fng_value} ({fng_classification})\n"
            
            # تفسير المؤشر
            if fng_value >= 75:
                interpretation = "طمع شديد - حذر من التصحيح"
            elif fng_value >= 55:
                interpretation = "طمع - معنويات إيجابية"
            elif fng_value >= 45:
                interpretation = "محايد - توازن في السوق"
            elif fng_value >= 25:
                interpretation = "خوف - فرصة شراء محتملة"
            else:
                interpretation = "خوف شديد - فرصة شراء قوية"
            
            message += f"• **التفسير:** {interpretation}\n\n"
        
        message += "---\n\n**📋 مستويات الدعم والمقاومة الرئيسية (24 ساعة):**\n\n"
        
        # بيانات العملات
        symbols_info = {
            'BTCUSDT': {'name': '₿ BTC (بيتكوين)', 'emoji': '₿'},
            'ETHUSDT': {'name': 'Ξ ETH (إيثريوم)', 'emoji': 'Ξ'},
            'SOLUSDT': {'name': '◎ SOL (سولانا)', 'emoji': '◎'},
            'XRPUSDT': {'name': '✕ XRP (ريبل)', 'emoji': '✕'}
        }
        
        market_symbols = market_data.get('market_data', {})
        for symbol, info in symbols_info.items():
            if symbol in market_symbols:
                data = market_symbols[symbol]
                price = data['price']
                change_24h = data['change_percent_24h']
                
                # تحديد اتجاه السعر
                trend_emoji = "📈" if change_24h > 0 else "📉" if change_24h < 0 else "➡️"
                
                message += f"**{info['name']}:**\n"
                message += f"• **السعر:** {price:,.2f} USDT {trend_emoji} ({change_24h:+.2f}%)\n"
                
                # مستويات الدعم والمقاومة
                levels = data.get('support_resistance', {})
                support_levels = levels.get('support', [])
                resistance_levels = levels.get('resistance', [])
                
                if support_levels:
                    support_str = " - ".join([f"{level:,.0f}" for level in support_levels[:2]])
                    message += f"• **الدعم:** {support_str}\n"
                
                if resistance_levels:
                    resistance_str = " - ".join([f"{level:,.0f}" for level in resistance_levels[:2]])
                    message += f"• **المقاومة:** {resistance_str}\n"
                
                message += "\n"
        
        message += "---\n*مصدر البيانات: Binance & Alternative.me. يتم التحديث تلقائيًا.*"
        
        return message
        
    except Exception as e:
        logger.error(f"خطأ في تنسيق رسالة السوق: {e}")
        return SYSTEM_MESSAGES["market_data_error"]

async def format_economic_schedule_message(economic_events: List[Dict]) -> str:
    """تنسيق رسالة الأجندة الاقتصادية"""
    try:
        message = "📅 **الأجندة الاقتصادية الأسبوعية**\n\n"
        message += "**الأحداث المؤثرة المحتملة للأيام السبعة القادمة:**\n\n"
        
        if not economic_events:
            message += "**(لا توجد أحداث كبرى متاحة حالياً)**\n\n"
        else:
            # تجميع الأحداث حسب التاريخ
            events_by_date = {}
            for event in economic_events[:7]:  # أول 7 أحداث
                date = event.get('date', 'غير محدد')
                if date not in events_by_date:
                    events_by_date[date] = []
                events_by_date[date].append(event)
            
            for date, events in events_by_date.items():
                # تنسيق التاريخ
                try:
                    date_obj = datetime.strptime(date, '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%A (%d %B)')
                    
                    # ترجمة أيام الأسبوع
                    day_translations = {
                        'Monday': 'الاثنين',
                        'Tuesday': 'الثلاثاء', 
                        'Wednesday': 'الأربعاء',
                        'Thursday': 'الخميس',
                        'Friday': 'الجمعة',
                        'Saturday': 'السبت',
                        'Sunday': 'الأحد'
                    }
                    
                    for en_day, ar_day in day_translations.items():
                        formatted_date = formatted_date.replace(en_day, ar_day)
                        
                except:
                    formatted_date = date
                
                message += f"**{formatted_date}**\n"
                
                for event in events:
                    time = event.get('time', 'غير محدد')
                    event_name = event.get('event', 'حدث اقتصادي')
                    country = event.get('country', '')
                    
                    # تحديد علم الدولة
                    country_flags = {
                        'United States': '🇺🇸',
                        'European Union': '🇪🇺',
                        'United Kingdom': '🇬🇧',
                        'Japan': '🇯🇵',
                        'China': '🇨🇳',
                        'Germany': '🇩🇪',
                        'France': '🇫🇷'
                    }
                    
                    flag = country_flags.get(country, '🌍')
                    
                    message += f"• ⏰ {time} | 📊 {event_name} | {flag}\n"
                
                message += "\n"
        
        message += "---\n*ملاحظة: الأحداث الاقتصادية قد تسبب تقلبات حادة في السوق. يُنصح بالحذر خلال أوقاتها.*"
        
        return message
        
    except Exception as e:
        logger.error(f"خطأ في تنسيق رسالة الأجندة الاقتصادية: {e}")
        return SYSTEM_MESSAGES["schedule_data_error"]

