from typing import Dict, Any, List
from src.modules.market_data.indicators.base_indicator import BaseIndicator

class SupportResistanceIndicator(BaseIndicator):
    """
    ระบบคำนวณแนวรับ-แนวต้าน อ้างอิงตามหลัก Standard Pivot Points
    """
    
    def __init__(self):
        super().__init__(name="SupportResistance")

    def calculate(self, data: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        คำนวณระดับแนวรับ (S1-S3) แนวต้าน (R1-R3) และจุด Pivot (P) 
        โดยอ้างอิงข้อมูล High, Low, Close ของแท่งเทียนก่อนหน้า (แท่งที่สมบูรณ์แล้ว)
        """
        if not data or len(data) < 2:
            raise ValueError("ข้อมูลแท่งเทียนไม่เพียงพอสำหรับการคำนวณ Pivot Points")
            
        # ดึงแท่งเทียนก่อนหน้าตัวล่าสุด (แท่งก่อนหน้าดัชนีปัจจุบันที่ปิดสมบูรณ์แล้ว)
        previous_candle = data[-2]
        
        high = previous_candle["high"]
        low = previous_candle["low"]
        close = previous_candle["close"]
        
        # สูตรมาตรฐานคณิตศาสตร์ Pivot Points
        pivot = (high + low + close) / 3.0
        
        # คำนวณแนวต้าน (Resistances)
        r1 = (2 * pivot) - low
        r2 = pivot + (high - low)
        r3 = high + 2 * (pivot - low)
        
        # คำนวณแนวรับ (Supports)
        s1 = (2 * pivot) - high
        s2 = pivot - (high - low)
        s3 = low - 2 * (high - pivot)
        
        return {
            "indicator": self.name,
            "pivot_point": round(float(pivot), 4),
            "resistances": [
                round(float(r1), 4),
                round(float(r2), 4),
                round(float(r3), 4)
            ],
            "supports": [
                round(float(s1), 4),
                round(float(s2), 4),
                round(float(s3), 4)
            ]
        }