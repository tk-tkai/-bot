import unittest
from typing import Dict, Any, List
from src.modules.market_data.indicator_engine import IndicatorEngine
from src.modules.market_data.indicators.trend import TrendIndicator
from src.modules.market_data.indicators.momentum import MomentumIndicator

class TestIndicatorEngine(unittest.TestCase):
    
    def setUp(self):
        """
        สร้างข้อมูลแท่งเทียนจำลองจำนวน 40 แท่ง (เพียงพอสำหรับทดสอบ Lookback 14 และ 26 แท่ง)
        เก็บไว้ในรูปแบบ Instance Variable (self.mock_candle_history) เพื่อให้ฟังก์ชันเทสเรียกใช้ได้ทันที
        """
        self.mock_candle_history = []
        base_price = 65000.0
        for i in range(40):
            price = base_price + (i * 100)
            self.mock_candle_history.append({
                "symbol": "BTCUSDT",
                "timeframe": "1h",
                "timestamp": 1700000000 + (i * 3600),
                "open": price - 50,
                "high": price + 150,
                "low": price - 100,
                "close": price,
                "volume": 1000.0
            })

    def test_momentum_indicator_rsi(self):
        """
        ทดสอบระบบโมเมนตัม (RSI Test)
        """
        rsi_calc = MomentumIndicator()
        result = rsi_calc.calculate(self.mock_candle_history, period=14)
        
        # เปลี่ยนมาใช้ Assertion Clauses ของ unittest มาตรฐาน
        self.assertIn("rsi", result)
        self.assertIn("status", result)
        self.assertIsInstance(result["rsi"], float)
        # เนื่องจากราคาจำลองขยับขึ้นต่อเนื่อง ค่า RSI ควรจะอยู่ในโซนสูง (Overbought > 50)
        self.assertGreater(result["rsi"], 50)

    def test_indicator_engine_deterministic_replay(self):
        """
        กฎเหล็ก: ป้อนข้อมูลดิบชุดเดิมเข้าเอนจิน ผลลัพธ์อินดิเคเตอร์ต้องเหมือนเดิม 100%
        ไม่มีการเปลี่ยนแปลงจากผลกระทบข้างเคียง (No Hidden Side Effects)
        """
        engine = IndicatorEngine()
        
        # รันคำนวณครั้งที่ 1
        snapshot_1 = engine.calculate_indicators_snapshot(self.mock_candle_history, fib_lookback=20)
        
        # รันคำนวณครั้งที่ 2 (จำลองสถานการณ์ระบบรีสตาร์ทแล้วดึงข้อมูลก้อนเดิมมาคำนวณใหม่)
        snapshot_2 = engine.calculate_indicators_snapshot(self.mock_candle_history, fib_lookback=20)
        
        # ตรวจสอบโครงสร้างและความถูกต้องของข้อมูลผ่านคำสั่งเสถียรของ unittest
        self.assertEqual(snapshot_1["current_price"], snapshot_2["current_price"])
        self.assertEqual(snapshot_1["fibonacci_retracement"]["swing_high"], snapshot_2["fibonacci_retracement"]["swing_high"])
        self.assertEqual(snapshot_1["support_resistance"]["pivot_point"], snapshot_2["support_resistance"]["pivot_point"])
        
        # เปรียบเทียบผลลัพธ์ทั้งหมดดิบๆ ต้องเท่ากันทุกทศนิยม 100%
        self.assertEqual(snapshot_1, snapshot_2)

if __name__ == '__main__':
    unittest.main()