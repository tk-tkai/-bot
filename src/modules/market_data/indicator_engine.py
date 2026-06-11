import logging
from typing import Dict, Any, List
from src.modules.market_data.indicators.fibonacci import FibonacciIndicator
from src.modules.market_data.indicators.resistance import SupportResistanceIndicator

logger = logging.getLogger(__name__)

class IndicatorEngine:
    """
    Indicator & Multi-TF Engine (Runtime Pipeline Step 2)
    ทำหน้าที่คำนวณอินดิเคเตอร์ทั้งหมดและรวมข้อมูลจากหลาย Timeframe
    เข้าด้วยกันแบบ Read-Only และรองรับ Deterministic Replay 100%
    """
    
    def __init__(self):
        # โหลดคลาสคำนวณอินดิเคเตอร์ที่เราเตรียมไว้ เข้ามาใช้งานเป็นคอมโพเนนต์หลัก
        self.fibonacci_calc = FibonacciIndicator()
        self.support_resistance_calc = SupportResistanceIndicator()
        
    def calculate_indicators_snapshot(self, candle_history: List[Dict[str, Any]], fib_lookback: int = 100) -> Dict[str, Any]:
        """
        คำนวณอินดิเคเตอร์เชิงคณิตศาสตร์ทั้งหมดจากข้อมูลชุดแท่งเทียนที่ส่งเข้ามา
        :param candle_history: ชุดข้อมูลดิบของแท่งเทียน (List of Dicts: open, high, low, close, volume)
        :param fib_lookback: จำนวนแท่งเทียนย้อนหลังที่ใช้หาจุด Swing High/Low สำหรับ Fibonacci
        :return: Dict ที่รวมผลลัพธ์อินดิเคเตอร์ทุกตัวที่ปิดแท่งสมบูรณ์แล้ว
        """
        if not candle_history:
            return {}
            
        try:
            # 1. ดึงข้อมูลราคาปัจจุบัน (แท่งล่าสุดที่กำลังขยับอยู่ หรือแท่งสุดท้ายใน Replay Feed)
            latest_candle = candle_history[-1]
            current_price = float(latest_candle["close"])
            
            # 2. คำนวณระดับ Fibonacci Levels
            fib_results = self.fibonacci_calc.calculate(candle_history, lookback=fib_lookback)
            
            # 3. คำนวณแนวรับ-แนวต้าน (Support & Resistance จาก Standard Pivot Points)
            sr_results = self.support_resistance_calc.calculate(candle_history)
            
            # 4. แพ็ครวมข้อมูลทั้งหมดเป็นผลลัพธ์ Snapshot เดียว
            indicator_snapshot = {
                "symbol": latest_candle.get("symbol", "UNKNOWN"),
                "timeframe": latest_candle.get("timeframe", "UNKNOWN"),
                "timestamp": latest_candle.get("timestamp"),
                "current_price": current_price,
                "fibonacci_retracement": fib_results,
                "support_resistance": sr_results
            }
            
            return indicator_snapshot
            
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาดในการคำนวณ Indicator Snapshot: {str(e)}")
            raise e

    def build_multi_tf_market_context(self, multi_tf_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        รวบรวมและสร้างบริบทตลาดแบบ Multi-Timeframe (เช่น ผสมข้อมูล 5m, 15m, 1h ร่วมกัน)
        เพื่อจัดเตรียมโครงสร้างข้อมูลส่งต่อให้ AI Orchestrator นำไปใช้ให้เหตุผลวิเคราะห์กราฟ
        
        :param multi_tf_data: Dict ที่มี Key เป็นชื่อ Timeframe และ Value เป็น List ของแท่งเทียนย้อนหลัง
        เช่น: {
            "5m": [...รายชื่อแท่งเวลา 5 นาที...],
            "1h": [...รายชื่อแท่งเวลา 1 ชั่วโมง...]
        }
        """
        market_context = {
            "status": "SUCCESS",
            "timeframes_included": list(multi_tf_data.keys()),
            "data": {}
        }
        
        for tf, candles in multi_tf_data.items():
            if not candles:
                continue
                
            # ปรับแต่งค่า Lookback ตามความเหมาะสมของแต่ละ Timeframe ในระบบเทรด
            lookback = 50 if tf == "1h" else 100
            
            # สั่งให้ Engine คำนวณอินดิเคเตอร์ของ Timeframe นั้นๆ ออกมา
            tf_snapshot = self.calculate_indicators_snapshot(candles, fib_lookback=lookback)
            market_context["data"][tf] = tf_snapshot
            
        return market_context