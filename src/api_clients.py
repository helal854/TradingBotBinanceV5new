"""
عملاء APIs الخارجية
"""
import aiohttp
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import ccxt.async_support as ccxt
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pytz

logger = logging.getLogger(__name__)

class BinanceAPIClient:
    """عميل Binance API"""
    
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.client = None
        self.exchange = None
        
    async def init_client(self):
        """تهيئة العميل"""
        try:
            self.client = Client(self.api_key, self.secret_key)
            self.exchange = ccxt.binance({
                'apiKey': self.api_key,
                'secret': self.secret_key,
                'sandbox': False,
                'enableRateLimit': True,
            })
            logger.info("تم تهيئة عميل Binance بنجاح")
        except Exception as e:
            logger.error(f"خطأ في تهيئة عميل Binance: {e}")
    
    async def get_current_price(self, symbol: str) -> Optional[float]:
        """الحصول على السعر الحالي"""
        try:
            if not self.exchange:
                await self.init_client()
            
            ticker = await self.exchange.fetch_ticker(symbol)
            return float(ticker['last'])
        except Exception as e:
            logger.error(f"خطأ في الحصول على السعر الحالي لـ {symbol}: {e}")
            return None
    
    async def get_24h_stats(self, symbol: str) -> Optional[Dict]:
        """إحصائيات 24 ساعة"""
        try:
            if not self.exchange:
                await self.init_client()
            
            ticker = await self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'price': float(ticker['last']),
                'change_24h': float(ticker['change']),
                'change_percent_24h': float(ticker['percentage']),
                'high_24h': float(ticker['high']),
                'low_24h': float(ticker['low']),
                'volume_24h': float(ticker['baseVolume'])
            }
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات 24 ساعة لـ {symbol}: {e}")
            return None
    
    async def get_klines(self, symbol: str, interval: str = '1d', limit: int = 30) -> Optional[List]:
        """الحصول على بيانات الشموع"""
        try:
            if not self.exchange:
                await self.init_client()
            
            ohlcv = await self.exchange.fetch_ohlcv(symbol, interval, limit=limit)
            return ohlcv
        except Exception as e:
            logger.error(f"خطأ في الحصول على بيانات الشموع لـ {symbol}: {e}")
            return None
    
    async def calculate_support_resistance(self, symbol: str, days: int = 7) -> Dict:
        """حساب مستويات الدعم والمقاومة"""
        try:
            klines = await self.get_klines(symbol, '1d', days)
            if not klines:
                return {'support': [], 'resistance': []}
            
            highs = [float(kline[2]) for kline in klines]  # High prices
            lows = [float(kline[3]) for kline in klines]   # Low prices
            
            # حساب مستويات الدعم والمقاومة البسيطة
            resistance_levels = []
            support_levels = []
            
            # أعلى الأسعار كمقاومة
            max_high = max(highs)
            resistance_levels.append(max_high)
            
            # أقل الأسعار كدعم
            min_low = min(lows)
            support_levels.append(min_low)
            
            # مستويات إضافية بناء على المتوسطات
            avg_high = sum(highs) / len(highs)
            avg_low = sum(lows) / len(lows)
            
            resistance_levels.append(avg_high)
            support_levels.append(avg_low)
            
            return {
                'support': sorted(list(set(support_levels))),
                'resistance': sorted(list(set(resistance_levels)), reverse=True)
            }
        except Exception as e:
            logger.error(f"خطأ في حساب مستويات الدعم والمقاومة: {e}")
            return {'support': [], 'resistance': []}
    
    async def validate_symbol(self, symbol: str) -> bool:
        """التحقق من صحة الرمز"""
        try:
            if not self.exchange:
                await self.init_client()
            
            markets = await self.exchange.load_markets()
            return symbol in markets
        except Exception as e:
            logger.error(f"خطأ في التحقق من صحة الرمز {symbol}: {e}")
            return False
    
    async def close(self):
        """إغلاق الاتصال"""
        if self.exchange:
            await self.exchange.close()

class CoinGeckoAPIClient:
    """عميل CoinGecko API"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = None
    
    async def init_session(self):
        """تهيئة الجلسة"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def get_market_data(self, coins: List[str] = None) -> Optional[Dict]:
        """الحصول على بيانات السوق"""
        try:
            await self.init_session()
            
            if not coins:
                coins = ['bitcoin', 'ethereum', 'solana', 'ripple']
            
            coins_str = ','.join(coins)
            url = f"{self.base_url}/simple/price"
            params = {
                'ids': coins_str,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"خطأ في API CoinGecko: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"خطأ في الحصول على بيانات السوق من CoinGecko: {e}")
            return None
    
    async def close(self):
        """إغلاق الجلسة"""
        if self.session:
            await self.session.close()

class FearGreedAPIClient:
    """عميل مؤشر الخوف والطمع"""
    
    def __init__(self):
        self.base_url = "https://api.alternative.me/fng/"
        self.session = None
    
    async def init_session(self):
        """تهيئة الجلسة"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def get_fear_greed_index(self) -> Optional[Dict]:
        """الحصول على مؤشر الخوف والطمع"""
        try:
            await self.init_session()
            
            async with self.session.get(self.base_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('data'):
                        fng_data = data['data'][0]
                        return {
                            'value': int(fng_data['value']),
                            'value_classification': fng_data['value_classification'],
                            'timestamp': fng_data['timestamp'],
                            'time_until_update': fng_data.get('time_until_update')
                        }
                return None
        except Exception as e:
            logger.error(f"خطأ في الحصول على مؤشر الخوف والطمع: {e}")
            return None
    
    async def close(self):
        """إغلاق الجلسة"""
        if self.session:
            await self.session.close()

class TradingEconomicsAPIClient:
    """عميل Trading Economics API"""
    
    def __init__(self):
        self.base_url = "https://api.tradingeconomics.com"
        self.session = None
    
    async def init_session(self):
        """تهيئة الجلسة"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def get_economic_calendar(self, days: int = 7) -> Optional[List[Dict]]:
        """الحصول على الأجندة الاقتصادية"""
        try:
            await self.init_session()
            
            # استخدام البيانات العامة المتاحة
            start_date = datetime.now().strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            
            url = f"{self.base_url}/calendar"
            params = {
                'c': 'guest:guest',  # بيانات الضيف
                'f': 'json',
                'd1': start_date,
                'd2': end_date,
                'i': 'high'  # أهمية عالية فقط
            }
            
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    # تنسيق البيانات
                    events = []
                    for event in data[:10]:  # أول 10 أحداث
                        events.append({
                            'date': event.get('Date'),
                            'time': event.get('Time'),
                            'country': event.get('Country'),
                            'event': event.get('Event'),
                            'importance': event.get('Importance'),
                            'actual': event.get('Actual'),
                            'forecast': event.get('Forecast'),
                            'previous': event.get('Previous')
                        })
                    return events
                else:
                    logger.warning(f"Trading Economics API غير متاح: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"خطأ في الحصول على الأجندة الاقتصادية: {e}")
            return None
    
    async def close(self):
        """إغلاق الجلسة"""
        if self.session:
            await self.session.close()

class APIManager:
    """مدير جميع APIs"""
    
    def __init__(self, binance_api_key: str, binance_secret_key: str):
        self.binance = BinanceAPIClient(binance_api_key, binance_secret_key)
        self.binance_client = self.binance  # إضافة مرجع للتوافق
        self.coingecko = CoinGeckoAPIClient()
        self.fear_greed = FearGreedAPIClient()
        self.trading_economics = TradingEconomicsAPIClient()
    
    async def init_all(self):
        """تهيئة جميع العملاء"""
        await self.binance.init_client()
        await self.coingecko.init_session()
        await self.fear_greed.init_session()
        await self.trading_economics.init_session()
        logger.info("تم تهيئة جميع عملاء APIs")
    
    async def get_comprehensive_market_data(self) -> Dict:
        """الحصول على بيانات السوق الشاملة"""
        try:
            # بيانات العملات الرئيسية
            symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT']
            market_data = {}
            
            for symbol in symbols:
                stats = await self.binance.get_24h_stats(symbol)
                if stats:
                    # حساب مستويات الدعم والمقاومة
                    levels = await self.binance.calculate_support_resistance(symbol)
                    stats['support_resistance'] = levels
                    market_data[symbol] = stats
            
            # مؤشر الخوف والطمع
            fng_data = await self.fear_greed.get_fear_greed_index()
            
            # الأجندة الاقتصادية
            economic_events = await self.trading_economics.get_economic_calendar()
            
            return {
                'market_data': market_data,
                'fear_greed_index': fng_data,
                'economic_events': economic_events,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"خطأ في الحصول على بيانات السوق الشاملة: {e}")
            return {}
    
    async def close_all(self):
        """إغلاق جميع الاتصالات"""
        await self.binance.close()
        await self.coingecko.close()
        await self.fear_greed.close()
        await self.trading_economics.close()
        logger.info("تم إغلاق جميع اتصالات APIs")

