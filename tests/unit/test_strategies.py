import unittest
from src.modules.strategy_engine.ai_momentum import AIMomentumStrategy
from src.modules.strategy_engine.grid_trading import GridTradingFallbackStrategy

class TestStrategyEngine(unittest.TestCase):
    def setUp(self):
        # จำลองข้อมูล Market Context จากโมดูลที่ 1 (เสถียรและ Deterministic)
        self.mock_market_context = {
            "BTCUSDT": {
                "1h": {
                    "current_price": 65000.0,
                    "rsi": 25.0,            # Oversold หนักมาก
                    "atr": 1000.0,
                    "support_1": 65200.0,   # ราคาปัจจุบันหลุดแนวรับลงมาแล้ว
                    "resistance_1": 67000.0
                }
            }
        }

    def test_ai_momentum_buy_signal(self):
        """
        ทดสอบว่าหาก AI มั่นใจสูงและทิศทางเป็นใจ กลยุทธ์ต้องออกสัญญาณ BUY พร้อมตั้ง SL/TP ชัดเจน
        """
        strategy = AIMomentumStrategy()
        mock_ai_analysis = {
            "regime": "ACCUMULATION",
            "confidence_score": 0.85,
            "reasoning": "Strong whale wallet inflows at support."
        }

        signal = strategy.calculate_signal(self.mock_market_context, mock_ai_analysis)
        
        self.assertEqual(signal["action"], "BUY")
        self.assertGreater(signal["take_profit"], signal["target_price"])
        self.assertLess(signal["stop_loss"], signal["target_price"])
        self.assertIn("AI Confirmed", signal["reason"])

    def test_ai_limit_fallback_trigger(self):
        """
        ทดสอบว่าหาก AI Router ส่งสัญญาณแจ้งเตือนว่าชนลิมิต (Bypass) 
        กลยุทธ์หลักต้องส่งสัญญาณให้ระบบสลับไปใช้กฎคณิตศาสตร์ทันที
        """
        strategy = AIMomentumStrategy()
        emergency_ai_analysis = {
            "regime": "UNKNOWN_LIMIT_REACHED",
            "confidence_score": 0.0,
            "reasoning": "Emergency Fallback triggered.",
            "emergency_bypass": True
        }

        signal = strategy.calculate_signal(self.mock_market_context, emergency_ai_analysis)
        
        # กลยุทธ์หลักต้องสั่ง HOLD เพื่อเตรียมตัวสลับโหมดการจราจรข้อมูล
        self.assertEqual(signal["action"], "HOLD")
        self.assertIn("AI Limit Detected", signal["reason"])

    def test_pure_technical_grid_fallback(self):
        """
        ทดสอบการทำงานของเอนจินคณิตศาสตร์ฉุกเฉิน (Grid Fallback) 
        ต้องสามารถคำนวณและสั่ง BUY ได้จากระดับแนวรับและ RSI โดยตรงโดยไม่ต้องพึ่ง AI
        """
        fallback_strategy = GridTradingFallbackStrategy()
        
        # รันโดยส่งค่า AI Analysis เป็น None หรือค่าว่างเปล่า (จำลองกรณี AI ล่มทั้งหมด)
        signal = fallback_strategy.calculate_signal(self.mock_market_context, ai_analysis=None)
        
        self.assertEqual(signal["action"], "BUY")
        self.assertIn("FALLBACK ACTIVE", signal["reason"])

if __name__ == '__main__':
    unittest.main()