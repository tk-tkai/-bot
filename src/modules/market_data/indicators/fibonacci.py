from typing import Dict, Any, List
from src.modules.market_data.indicators.base_indicator import BaseIndicator

class FibonacciIndicator(BaseIndicator):
    """
    ระบบคำนวณ Fibonacci Retracement ระดับสากลแบบ Deterministic
    """
    
    def __init__(self):
        super().__init__(name="FibonacciRetracement")
        # สัดส่วนฟิโบนาชิมาตรฐานที่ระบบเลือกใช้
        self.ratios = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]

    def calculate(self, data: List[Dict[str, Any]], lookback: int = 100) -> Dict[str, Any]:
        """
        คำนวณหาเส้น Fibonacci จากแท่งเทียนย้อนหลังตามจำนวนช่วงเวลาที่กำหนด
        """
        if not data or len(data) < lookback:
            raise ValueError(f"ข้อมูลแท่งเทียนไม่เพียงพอสำหรับการคำนวณฟิโบนาชิ (ต้องการอย่างน้อย {lookback} แท่ง)")
            
        # ดึงเฉพาะข้อมูลในช่วง Lookback ล่าสุด
        target_data = data[-lookback:]
        
        # หาจุด Swing High และ Swing Low ในรอบ Lookback
        swing_high = max(candle["high"] for candle in target_data)
        swing_low = min(candle["low"] for candle in target_data)
        diff = swing_high - swing_low
        
        # ตรวจสอบทิศทางแนวโน้มเพื่อระบุระดับราคา (อ้างอิงจากแท่งแรกเทียบแท่งล่าสุดในช่วง Lookback)
        is_uptrend = target_data[-1]["close"] >= target_data[0]["close"]
        
        levels = {}
        for ratio in self.ratios:
            if is_uptrend:
                # ขาขึ้น: พักฐานลงมาจากบน (0.0 อยู่บนสุด, 1.0 อยู่ล่างสุด)
                price_level = swing_high - (diff * ratio)
            else:
                # ขาลง: ดีดตัวขึ้นมาจากล่าง (0.0 อยู่ล่างสุด, 1.0 อยู่บนสุด)
                price_level = swing_low + (diff * ratio)
                
            levels[str(ratio)] = round(float(price_level), 4)

        return {
            "indicator": self.name,
            "lookback_period": lookback,
            "swing_high": float(swing_high),
            "swing_low": float(swing_low),
            "trend_direction": "UPTREND" if is_uptrend else "DOWNTREND",
            "levels": levels
        }