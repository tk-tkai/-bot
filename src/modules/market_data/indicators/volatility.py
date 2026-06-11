from typing import Dict, Any, List
from src.modules.market_data.indicators.base_indicator import BaseIndicator

class VolatilityIndicator(BaseIndicator):
    """
    ระบบคำนวณอินดิเคเตอร์กลุ่มความผันผวน (Volatility) เช่น ATR (Average True Range)
    """
    def __init__(self):
        super().__init__(name="VolatilityIndicators")

    def calculate(self, data: List[Dict[str, Any]], period: int = 14) -> Dict[str, Any]:
        if not data or len(data) < period + 1:
            raise ValueError(f"ข้อมูลแท่งเทียนไม่เพียงพอสำหรับการคำนวณ ATR-{period}")

        # คำนวณหาค่า True Range (TR) ของแต่ละแท่งเทียน
        tr_values = []
        for i in range(1, len(data)):
            current_high = float(data[i]["high"])
            current_low = float(data[i]["low"])
            previous_close = float(data[i-1]["close"])
            
            #สูตรหาค่า True Range สากล
            tr1 = current_high - current_low
            tr2 = abs(current_high - previous_close)
            tr3 = abs(current_low - previous_close)
            
            tr_values.append(max(tr1, tr2, tr3))

        # คำนวณค่าเฉลี่ย ATR แบบ Wilder's Smoothing
        atr = sum(tr_values[:period]) / period
        for i in range(period, len(tr_values)):
            atr = ((atr * (period - 1)) + tr_values[i]) / period

        return {
            "indicator": self.name,
            "atr": round(atr, 4),
            "market_volatility_ratio_percent": round((atr / float(data[-1]["close"])) * 100, 2)
        }