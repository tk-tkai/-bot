from typing import Dict, Any, List
from src.modules.market_data.indicators.base_indicator import BaseIndicator

class TrendIndicator(BaseIndicator):
    """
    ระบบคำนวณอินดิเคเตอร์กลุ่มแนวโน้ม (Trend) เช่น SMA, EMA และ MACD
    """
    def __init__(self):
        super().__init__(name="TrendIndicators")

    def _calculate_sma(self, prices: List[float], period: int) -> float:
        if len(prices) < period:
            return prices[-1] if prices else 0.0
        return sum(prices[-period:]) / period

    def _calculate_ema(self, prices: List[float], period: int) -> float:
        if not prices:
            return 0.0
        if len(prices) < period:
            return prices[-1]
            
        k = 2 / (period + 1)
        # ใช้ SMA เป็นค่าเริ่มต้นของ EMA ตัวแรก
        ema = sum(prices[:period]) / period
        
        # คำนวณค่า EMA ไล่มาจนถึงปัจจุบัน
        for price in prices[period:]:
            ema = (price * k) + (ema * (1 - k))
        return ema

    def calculate(self, data: List[Dict[str, Any]], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, Any]:
        if not data or len(data) < slow_period + signal_period:
            raise ValueError("ข้อมูลแท่งเทียนไม่เพียงพอสำหรับการคำนวณ Trend Indicators")

        close_prices = [float(candle["close"]) for candle in data]
        
        # คำนวณ EMA สำหรับเส้น MACD
        # เพื่อหาค่าล่าสุด ระบบต้องคำนวณประวัติย้อนหลังมาเรื่อยๆ เพื่อความแม่นยำ (Deterministic)
        macd_line = []
        for i in range(slow_period, len(close_prices) + 1):
            sub_prices = close_prices[:i]
            fast_ema = self._calculate_ema(sub_prices, fast_period)
            slow_ema = self._calculate_ema(sub_prices, slow_period)
            macd_line.append(fast_ema - slow_ema)
            
        # คำนวณ Signal Line จากประวัติของ MACD Line
        signal_line = self._calculate_ema(macd_line, signal_period)
        latest_macd = macd_line[-1]
        histogram = latest_macd - signal_line

        return {
            "indicator": self.name,
            "ema_fast": round(self._calculate_ema(close_prices, fast_period), 4),
            "ema_slow": round(self._calculate_ema(close_prices, slow_period), 4),
            "macd": {
                "macd_line": round(latest_macd, 4),
                "signal_line": round(signal_line, 4),
                "histogram": round(histogram, 4)
            }
        }