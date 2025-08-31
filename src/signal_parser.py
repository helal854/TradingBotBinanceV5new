"""
محلل نصوص الإشارات
"""
import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class SignalParser:
    """محلل الإشارات التلقائي"""
    
    def __init__(self):
        # أنماط التعبيرات النمطية لاستخراج البيانات
        self.patterns = {
            'symbol': [
                r'(?:زوج|الزوج|pair):\s*([A-Z]{3,10}/?USDT?)',
                r'([A-Z]{3,10}/?USDT?)',
                r'#([A-Z]{3,10})',
            ],
            'direction': [
                r'(?:اتجاه|direction):\s*(BUY|SELL|شراء|بيع|LONG|SHORT)',
                r'(BUY|SELL|شراء|بيع|LONG|SHORT)',
            ],
            'entry_price': [
                r'(?:نقطة الدخول|entry|دخول):\s*([\d,.\-\s]+)',
                r'(?:entry price|دخول):\s*([\d,.\-\s]+)',
                r'(?:buy|شراء).*?([\d,.\-\s]+)',
            ],
            'stop_loss': [
                r'(?:وقف الخسارة|stop loss|sl):\s*([\d,.]+)',
                r'(?:stop|وقف).*?([\d,.]+)',
            ],
            'targets': [
                r'(?:أهداف|targets?|take profit|tp):\s*(.*?)(?:\n|$)',
                r'(?:T\d+|هدف\s*\d*):\s*([\d,.]+)',
                r'(\d+)\s*[️⃣]\s*T\d+:\s*([\d,.]+)',
            ],
            'support': [
                r'(?:الدعم|support):\s*([\d,.\-\s]+)',
                r'(?:دعم).*?([\d,.\-\s]+)',
            ],
            'resistance': [
                r'(?:المقاومة|resistance):\s*([\d,.\-\s]+)',
                r'(?:مقاومة).*?([\d,.\-\s]+)',
            ]
        }
    
    def parse_signal_text(self, signal_text: str) -> Dict:
        """تحليل نص الإشارة واستخراج البيانات"""
        try:
            result = {
                'symbol': None,
                'direction': None,
                'entry_price_min': None,
                'entry_price_max': None,
                'stop_loss': None,
                'targets': [],
                'support_levels': [],
                'resistance_levels': [],
                'raw_text': signal_text,
                'parsed_successfully': False,
                'errors': []
            }
            
            # استخراج الرمز
            symbol = self._extract_symbol(signal_text)
            if symbol:
                result['symbol'] = symbol
            else:
                result['errors'].append("لم يتم العثور على رمز العملة")
            
            # استخراج الاتجاه
            direction = self._extract_direction(signal_text)
            if direction:
                result['direction'] = direction
            else:
                result['errors'].append("لم يتم العثور على اتجاه التداول")
            
            # استخراج سعر الدخول
            entry_prices = self._extract_entry_price(signal_text)
            if entry_prices:
                result['entry_price_min'] = entry_prices[0]
                result['entry_price_max'] = entry_prices[1] if len(entry_prices) > 1 else entry_prices[0]
            else:
                result['errors'].append("لم يتم العثور على سعر الدخول")
            
            # استخراج وقف الخسارة
            stop_loss = self._extract_stop_loss(signal_text)
            if stop_loss:
                result['stop_loss'] = stop_loss
            else:
                result['errors'].append("لم يتم العثور على وقف الخسارة")
            
            # استخراج الأهداف
            targets = self._extract_targets(signal_text)
            if targets:
                result['targets'] = targets
            else:
                result['errors'].append("لم يتم العثور على أهداف الربح")
            
            # استخراج مستويات الدعم
            support_levels = self._extract_support_levels(signal_text)
            result['support_levels'] = support_levels
            
            # استخراج مستويات المقاومة
            resistance_levels = self._extract_resistance_levels(signal_text)
            result['resistance_levels'] = resistance_levels
            
            # تحديد نجاح التحليل
            required_fields = ['symbol', 'direction', 'entry_price_min', 'stop_loss']
            result['parsed_successfully'] = all(result[field] is not None for field in required_fields)
            
            if result['parsed_successfully']:
                logger.info(f"تم تحليل الإشارة بنجاح: {symbol}")
            else:
                logger.warning(f"فشل في تحليل الإشارة: {result['errors']}")
            
            return result
            
        except Exception as e:
            logger.error(f"خطأ في تحليل الإشارة: {e}")
            return {
                'parsed_successfully': False,
                'errors': [f"خطأ في التحليل: {str(e)}"],
                'raw_text': signal_text
            }
    
    def _extract_symbol(self, text: str) -> Optional[str]:
        """استخراج رمز العملة"""
        for pattern in self.patterns['symbol']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                symbol = match.group(1).upper().replace('/', '')
                # تأكد من أن الرمز ينتهي بـ USDT
                if not symbol.endswith('USDT'):
                    symbol += 'USDT'
                return symbol
        return None
    
    def _extract_direction(self, text: str) -> Optional[str]:
        """استخراج اتجاه التداول"""
        for pattern in self.patterns['direction']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                direction = match.group(1).upper()
                # توحيد الاتجاهات
                if direction in ['BUY', 'شراء', 'LONG']:
                    return 'BUY'
                elif direction in ['SELL', 'بيع', 'SHORT']:
                    return 'SELL'
        return None
    
    def _extract_entry_price(self, text: str) -> List[float]:
        """استخراج أسعار الدخول"""
        prices = []
        for pattern in self.patterns['entry_price']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_text = match.group(1)
                # استخراج الأرقام من النص
                numbers = re.findall(r'[\d,.]+', price_text)
                for num in numbers:
                    try:
                        price = float(num.replace(',', ''))
                        prices.append(price)
                    except ValueError:
                        continue
                if prices:
                    break
        
        return sorted(prices) if prices else []
    
    def _extract_stop_loss(self, text: str) -> Optional[float]:
        """استخراج وقف الخسارة"""
        for pattern in self.patterns['stop_loss']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    continue
        return None
    
    def _extract_targets(self, text: str) -> List[float]:
        """استخراج أهداف الربح"""
        targets = []
        
        # البحث عن الأهداف بأنماط مختلفة
        target_patterns = [
            r'(\d+)[️⃣]\s*T\d+:\s*([\d,.]+)',  # 1️⃣ T1: 62,200
            r'T(\d+):\s*([\d,.]+)',             # T1: 62,200
            r'هدف\s*(\d+):\s*([\d,.]+)',        # هدف 1: 62,200
            r'(\d+)\.\s*([\d,.]+)',             # 1. 62,200
        ]
        
        for pattern in target_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    target_num = int(match[0])
                    target_price = float(match[1].replace(',', ''))
                    targets.append(target_price)
                except (ValueError, IndexError):
                    continue
        
        # إزالة المكررات وترتيب
        targets = sorted(list(set(targets)))
        return targets[:5]  # أقصى 5 أهداف
    
    def _extract_support_levels(self, text: str) -> List[float]:
        """استخراج مستويات الدعم"""
        levels = []
        for pattern in self.patterns['support']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                level_text = match.group(1)
                numbers = re.findall(r'[\d,.]+', level_text)
                for num in numbers:
                    try:
                        level = float(num.replace(',', ''))
                        levels.append(level)
                    except ValueError:
                        continue
        return sorted(list(set(levels)))
    
    def _extract_resistance_levels(self, text: str) -> List[float]:
        """استخراج مستويات المقاومة"""
        levels = []
        for pattern in self.patterns['resistance']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                level_text = match.group(1)
                numbers = re.findall(r'[\d,.]+', level_text)
                for num in numbers:
                    try:
                        level = float(num.replace(',', ''))
                        levels.append(level)
                    except ValueError:
                        continue
        return sorted(list(set(levels)), reverse=True)
    
    def validate_signal_data(self, parsed_data: Dict, current_price: float = None) -> Dict:
        """التحقق من صحة بيانات الإشارة"""
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'risk_reward_ratio': None
        }
        
        try:
            # التحقق من وجود البيانات الأساسية
            required_fields = ['symbol', 'direction', 'entry_price_min', 'stop_loss']
            for field in required_fields:
                if not parsed_data.get(field):
                    validation_result['errors'].append(f"حقل مطلوب مفقود: {field}")
                    validation_result['is_valid'] = False
            
            if not validation_result['is_valid']:
                return validation_result
            
            entry_price = parsed_data['entry_price_min']
            stop_loss = parsed_data['stop_loss']
            direction = parsed_data['direction']
            targets = parsed_data.get('targets', [])
            
            # التحقق من منطقية الأسعار
            if direction == 'BUY':
                if stop_loss >= entry_price:
                    validation_result['errors'].append("وقف الخسارة يجب أن يكون أقل من سعر الدخول في صفقة الشراء")
                    validation_result['is_valid'] = False
                
                # التحقق من الأهداف
                for i, target in enumerate(targets):
                    if target <= entry_price:
                        validation_result['warnings'].append(f"الهدف {i+1} ({target}) أقل من سعر الدخول")
            
            elif direction == 'SELL':
                if stop_loss <= entry_price:
                    validation_result['errors'].append("وقف الخسارة يجب أن يكون أعلى من سعر الدخول في صفقة البيع")
                    validation_result['is_valid'] = False
                
                # التحقق من الأهداف
                for i, target in enumerate(targets):
                    if target >= entry_price:
                        validation_result['warnings'].append(f"الهدف {i+1} ({target}) أعلى من سعر الدخول")
            
            # حساب نسبة المخاطرة إلى العائد
            if targets:
                if direction == 'BUY':
                    risk = entry_price - stop_loss
                    reward = targets[0] - entry_price
                elif direction == 'SELL':
                    risk = stop_loss - entry_price
                    reward = entry_price - targets[0]
                
                if risk > 0:
                    validation_result['risk_reward_ratio'] = reward / risk
                    if validation_result['risk_reward_ratio'] < 1:
                        validation_result['warnings'].append(f"نسبة المخاطرة إلى العائد منخفضة: {validation_result['risk_reward_ratio']:.2f}")
            
            # التحقق من السعر الحالي إذا كان متاحاً
            if current_price:
                if direction == 'BUY':
                    if current_price > parsed_data.get('entry_price_max', entry_price):
                        validation_result['warnings'].append(f"السعر الحالي ({current_price}) أعلى من نطاق الدخول")
                elif direction == 'SELL':
                    if current_price < parsed_data.get('entry_price_max', entry_price):
                        validation_result['warnings'].append(f"السعر الحالي ({current_price}) أقل من نطاق الدخول")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من صحة الإشارة: {e}")
            return {
                'is_valid': False,
                'errors': [f"خطأ في التحقق: {str(e)}"],
                'warnings': []
            }
    
    def format_signal_message(self, parsed_data: Dict, validation_result: Dict = None) -> str:
        """تنسيق رسالة الإشارة"""
        try:
            if not parsed_data.get('parsed_successfully'):
                return "❌ فشل في تحليل الإشارة"
            
            symbol = parsed_data['symbol']
            direction = parsed_data['direction']
            entry_min = parsed_data['entry_price_min']
            entry_max = parsed_data.get('entry_price_max', entry_min)
            stop_loss = parsed_data['stop_loss']
            targets = parsed_data.get('targets', [])
            support_levels = parsed_data.get('support_levels', [])
            resistance_levels = parsed_data.get('resistance_levels', [])
            
            # تحديد اتجاه التداول بالعربية
            direction_ar = "شراء (BUY)" if direction == 'BUY' else "بيع (SELL)"
            
            message = f"""🎯 **إشارة تداول - SPOT**

**⏰ وقت الإشارة:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**🪙 الزوج:** {symbol}
**↗️ الاتجاه:** {direction_ar}

**📍 نقطة الدخول:** {entry_min:,.0f}"""
            
            if entry_max != entry_min:
                message += f" - {entry_max:,.0f}"
            
            message += f"""
**🛑 وقف الخسارة (Stop Loss):** {stop_loss:,.0f}"""
            
            if targets:
                message += "\n\n**🎯 أهداف البيع (Take Profit):**"
                for i, target in enumerate(targets[:5], 1):
                    emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"][i-1]
                    message += f"\n{emoji} T{i}: {target:,.0f}"
            
            if support_levels or resistance_levels:
                message += "\n\n**📊 مستويات رئيسية:**"
                if support_levels:
                    support_str = " - ".join([f"{level:,.0f}" for level in support_levels[:2]])
                    message += f"\n**🧱 الدعم:** {support_str}"
                if resistance_levels:
                    resistance_str = " - ".join([f"{level:,.0f}" for level in resistance_levels[:2]])
                    message += f"\n**🚧 المقاومة:** {resistance_str}"
            
            # إضافة معلومات التحقق إذا كانت متاحة
            if validation_result and validation_result.get('risk_reward_ratio'):
                rr_ratio = validation_result['risk_reward_ratio']
                message += f"\n\n**📈 نسبة المخاطرة/العائد:** 1:{rr_ratio:.2f}"
            
            message += """\n\n---
🛑 **تنبيه هام:** الصفقة ليست نصيحة استثمارية. يرجى التحليل الشخصي وإدارة المخاطر قبل الدخول بأي صفقة."""
            
            return message
            
        except Exception as e:
            logger.error(f"خطأ في تنسيق رسالة الإشارة: {e}")
            return "❌ خطأ في تنسيق الإشارة"

# إنشاء مثيل عام للمحلل
signal_parser = SignalParser()

