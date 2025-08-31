"""
لوحات المفاتيح للبوت
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard() -> InlineKeyboardMarkup:
    """القائمة الرئيسية للبوت"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📈 الإشارات", callback_data="signals"),
            InlineKeyboardButton(text="🌡️ حالة السوق", callback_data="news")
        ],
        [
            InlineKeyboardButton(text="📅 الأجندة الاقتصادية", callback_data="schedule"),
            InlineKeyboardButton(text="🏆 أفضل المتداولين", callback_data="top_traders")
        ],
        [
            InlineKeyboardButton(text="👤 حسابي", callback_data="account"),
            InlineKeyboardButton(text="❓ المساعدة", callback_data="help")
        ],
        [
            InlineKeyboardButton(text="🔄 تحديث", callback_data="refresh")
        ]
    ])
    return keyboard

def get_back_keyboard() -> InlineKeyboardMarkup:
    """زر العودة للقائمة الرئيسية"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]
    ])
    return keyboard

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """لوحة مفاتيح المسؤول"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 الإحصائيات", callback_data="admin_stats"),
            InlineKeyboardButton(text="👥 إدارة المستخدمين", callback_data="admin_users")
        ],
        [
            InlineKeyboardButton(text="📤 إرسال إشارة", callback_data="admin_send_signal"),
            InlineKeyboardButton(text="📢 رسالة عامة", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton(text="🖥️ مراقبة النظام", callback_data="admin_monitoring"),
            InlineKeyboardButton(text="📋 السجلات", callback_data="admin_logs")
        ],
        [
            InlineKeyboardButton(text="⚙️ الإعدادات", callback_data="admin_settings"),
            InlineKeyboardButton(text="🔙 العودة", callback_data="back_to_main")
        ]
    ])
    return keyboard

def get_user_management_keyboard() -> InlineKeyboardMarkup:
    """لوحة إدارة المستخدمين"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ إضافة مستخدم", callback_data="admin_add_user"),
            InlineKeyboardButton(text="➖ إزالة مستخدم", callback_data="admin_remove_user")
        ],
        [
            InlineKeyboardButton(text="📋 قائمة المستخدمين", callback_data="admin_list_users"),
            InlineKeyboardButton(text="🔍 بحث عن مستخدم", callback_data="admin_search_user")
        ],
        [
            InlineKeyboardButton(text="🔙 العودة", callback_data="admin_panel")
        ]
    ])
    return keyboard

def get_signal_confirmation_keyboard() -> InlineKeyboardMarkup:
    """لوحة تأكيد الإشارة"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ إرسال الإشارة", callback_data="confirm_signal"),
            InlineKeyboardButton(text="❌ إلغاء", callback_data="cancel_signal")
        ],
        [
            InlineKeyboardButton(text="✏️ تعديل", callback_data="edit_signal")
        ]
    ])
    return keyboard

def get_broadcast_confirmation_keyboard() -> InlineKeyboardMarkup:
    """لوحة تأكيد الرسالة العامة"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ إرسال للجميع", callback_data="confirm_broadcast"),
            InlineKeyboardButton(text="❌ إلغاء", callback_data="cancel_broadcast")
        ]
    ])
    return keyboard

def get_market_refresh_keyboard() -> InlineKeyboardMarkup:
    """لوحة تحديث بيانات السوق"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 تحديث البيانات", callback_data="refresh_market"),
            InlineKeyboardButton(text="📊 تفاصيل أكثر", callback_data="detailed_market")
        ],
        [
            InlineKeyboardButton(text="🔙 العودة", callback_data="back_to_main")
        ]
    ])
    return keyboard

def get_signal_actions_keyboard(signal_id: int = None) -> InlineKeyboardMarkup:
    """لوحة إجراءات الإشارة"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 تحليل الإشارة", callback_data=f"analyze_signal_{signal_id}"),
            InlineKeyboardButton(text="📈 السعر الحالي", callback_data=f"current_price_{signal_id}")
        ],
        [
            InlineKeyboardButton(text="🔔 تنبيه عند الهدف", callback_data=f"alert_target_{signal_id}"),
            InlineKeyboardButton(text="📋 نسخ الإشارة", callback_data=f"copy_signal_{signal_id}")
        ],
        [
            InlineKeyboardButton(text="🔙 العودة", callback_data="back_to_main")
        ]
    ])
    return keyboard

def get_schedule_filter_keyboard() -> InlineKeyboardMarkup:
    """لوحة فلترة الأجندة الاقتصادية"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 اليوم", callback_data="schedule_today"),
            InlineKeyboardButton(text="📅 غداً", callback_data="schedule_tomorrow")
        ],
        [
            InlineKeyboardButton(text="📅 هذا الأسبوع", callback_data="schedule_week"),
            InlineKeyboardButton(text="📅 الشهر القادم", callback_data="schedule_month")
        ],
        [
            InlineKeyboardButton(text="🔙 العودة", callback_data="back_to_main")
        ]
    ])
    return keyboard

def get_settings_keyboard() -> InlineKeyboardMarkup:
    """لوحة الإعدادات"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔔 إعدادات التنبيهات", callback_data="settings_notifications"),
            InlineKeyboardButton(text="🌐 اللغة", callback_data="settings_language")
        ],
        [
            InlineKeyboardButton(text="⏰ المنطقة الزمنية", callback_data="settings_timezone"),
            InlineKeyboardButton(text="📊 تفضيلات العرض", callback_data="settings_display")
        ],
        [
            InlineKeyboardButton(text="🔙 العودة", callback_data="back_to_main")
        ]
    ])
    return keyboard

def get_help_categories_keyboard() -> InlineKeyboardMarkup:
    """لوحة فئات المساعدة"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚀 البدء السريع", callback_data="help_quick_start"),
            InlineKeyboardButton(text="📈 فهم الإشارات", callback_data="help_signals")
        ],
        [
            InlineKeyboardButton(text="📊 قراءة السوق", callback_data="help_market"),
            InlineKeyboardButton(text="⚠️ إدارة المخاطر", callback_data="help_risk")
        ],
        [
            InlineKeyboardButton(text="❓ أسئلة شائعة", callback_data="help_faq"),
            InlineKeyboardButton(text="📞 التواصل", callback_data="help_contact")
        ],
        [
            InlineKeyboardButton(text="🔙 العودة", callback_data="back_to_main")
        ]
    ])
    return keyboard

def get_confirmation_keyboard(action: str) -> InlineKeyboardMarkup:
    """لوحة تأكيد عامة"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ تأكيد", callback_data=f"confirm_{action}"),
            InlineKeyboardButton(text="❌ إلغاء", callback_data=f"cancel_{action}")
        ]
    ])
    return keyboard

def get_pagination_keyboard(current_page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
    """لوحة التنقل بين الصفحات"""
    buttons = []
    
    # أزرار التنقل
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ السابق", callback_data=f"{prefix}_page_{current_page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="current_page"))
    
    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="➡️ التالي", callback_data=f"{prefix}_page_{current_page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    # زر العودة
    buttons.append([InlineKeyboardButton(text="🔙 العودة", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# لوحة مفاتيح الطوارئ للمسؤول
def get_emergency_keyboard() -> InlineKeyboardMarkup:
    """لوحة الطوارئ للمسؤول"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚨 إيقاف البوت", callback_data="emergency_stop"),
            InlineKeyboardButton(text="🔄 إعادة تشغيل", callback_data="emergency_restart")
        ],
        [
            InlineKeyboardButton(text="📤 نسخ احتياطي", callback_data="emergency_backup"),
            InlineKeyboardButton(text="🗑️ مسح البيانات", callback_data="emergency_clear")
        ],
        [
            InlineKeyboardButton(text="🔙 العودة", callback_data="admin_panel")
        ]
    ])
    return keyboard



def get_top_traders_keyboard() -> InlineKeyboardMarkup:
    """لوحة أفضل المتداولين"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 أسبوعي (ROI)", callback_data="traders_weekly_roi"),
            InlineKeyboardButton(text="💰 أسبوعي (PNL)", callback_data="traders_weekly_pnl")
        ],
        [
            InlineKeyboardButton(text="📈 شهري (ROI)", callback_data="traders_monthly_roi"),
            InlineKeyboardButton(text="💵 شهري (PNL)", callback_data="traders_monthly_pnl")
        ],
        [
            InlineKeyboardButton(text="👥 الأكثر متابعة", callback_data="traders_most_followed"),
            InlineKeyboardButton(text="🔄 تحديث البيانات", callback_data="refresh_traders")
        ],
        [
            InlineKeyboardButton(text="🔙 العودة", callback_data="back_to_main")
        ]
    ])
    return keyboard

def get_trader_details_keyboard(encrypted_uid: str) -> InlineKeyboardMarkup:
    """لوحة تفاصيل متداول محدد"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 تحليل الأداء", callback_data=f"analyze_trader_{encrypted_uid}"),
            InlineKeyboardButton(text="📈 المراكز الحالية", callback_data=f"trader_positions_{encrypted_uid}")
        ],
        [
            InlineKeyboardButton(text="📋 نسخ المعرف", callback_data=f"copy_uid_{encrypted_uid}"),
            InlineKeyboardButton(text="🔔 تنبيه متابعة", callback_data=f"follow_trader_{encrypted_uid}")
        ],
        [
            InlineKeyboardButton(text="🔙 العودة للقائمة", callback_data="top_traders")
        ]
    ])
    return keyboard

def get_traders_filter_keyboard() -> InlineKeyboardMarkup:
    """لوحة فلترة المتداولين"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚡ العقود الدائمة", callback_data="filter_perpetual"),
            InlineKeyboardButton(text="📅 العقود الآجلة", callback_data="filter_delivery")
        ],
        [
            InlineKeyboardButton(text="🎯 الخيارات", callback_data="filter_options"),
            InlineKeyboardButton(text="🌟 جميع الأنواع", callback_data="filter_all")
        ],
        [
            InlineKeyboardButton(text="✅ المشاركون فقط", callback_data="filter_shared_only"),
            InlineKeyboardButton(text="🏅 المعتمدون فقط", callback_data="filter_verified_only")
        ],
        [
            InlineKeyboardButton(text="🔙 العودة", callback_data="top_traders")
        ]
    ])
    return keyboard


def get_monitoring_keyboard() -> InlineKeyboardMarkup:
    """لوحة مراقبة النظام"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 تحديث البيانات", callback_data="refresh_monitoring"),
            InlineKeyboardButton(text="📊 تقرير مفصل", callback_data="detailed_monitoring")
        ],
        [
            InlineKeyboardButton(text="📈 الاتجاهات", callback_data="monitoring_trends"),
            InlineKeyboardButton(text="⚠️ التنبيهات", callback_data="monitoring_alerts")
        ],
        [
            InlineKeyboardButton(text="🔙 العودة للإدارة", callback_data="admin_panel")
        ]
    ])
    return keyboard

