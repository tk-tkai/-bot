from typing import Dict, Any, List
from src.modules.market_data.indicators.base_indicator import BaseIndicator

class MomentumIndicator(BaseIndicator):
    """
    ระบบคำนวณอินดิเคเตอร์กลุ่มแรงส่ง (Momentum) เช่น RSI (Relative Strength Index)
    """
    def __init__(self):
        super().__init__(name="MomentumIndicators")

    def calculate(self, data: List[Dict[str, Any]], period: int = 14) -> Dict[str, Any]:
        if not data or len(data) < period + 1:
            raise ValueError(f"ข้อมูลแท่งเทียนไม่เพียงพอสำหรับการคำนวณ RSI-{period}")

        close_prices = [float(candle["close"]) for candle in data]
        
        # คำนวณผลต่างราคา (Gains / Losses)
        gains = []
        losses = []
        for i in range(1, len(close_prices)):
            diff = close_prices[i] - close_prices[i-1]
            if diff > 0:
                gains.append(diff)
                losses.append(0.0)
            else:
                gains.append(0.0)
                losses.append(abs(diff))

        # ค่าเฉลี่ยเริ่มต้น (First Average Gain/Loss)
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        # คำนวณแบบ Smoothed (Wilder's Smoothing) ไล่มาจนถึงแท่งปัจจุบัน
        for i in range(period, len(gains)):
            avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period
            avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period

        if avg_loss == 0:
            rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100.0 - (100.0 / (1.0 + rs))

        return {
            "indicator": self.name,
            "rsi": round(rsi, 2),
            "status": "OVERBOUGHT" if rsi >= 70 else "OVERSOLD" if rsi <= 30 else "NEUTRAL"
        }