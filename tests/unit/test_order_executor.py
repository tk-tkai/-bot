import unittest
from src.modules.order_executor.exchange_client import ExchangeClient
from src.modules.order_executor.position_tracker import PositionTracker

class TestOrderExecutorModule(unittest.TestCase):
    def setUp(self):
        self.client = ExchangeClient()
        self.tracker = PositionTracker(risk_per_trade_pct=1.0)  # เสี่ยง 1% ต่อไม้

    def test_dynamic_position_sizing_calculation(self):
        """
        ทดสอบสูตรคำนวณขนาดไม้: ทุน $10,000 เสี่ยง 1% ($100) 
        เข้าซื้อ BTC ที่ราคา 60,000 โดยมี SL ที่ 59,000 (ระยะห่าง $1,000)
        ขนาดไม้ที่ได้ต้องเท่ากับ 100 / 1000 = 0.1 BTC เป๊ะๆ
        """
        calculated_qty = self.tracker.calculate_dynamic_size(
            balance=10000.0,
            entry_price=60000.0,
            stop_loss=59000.0
        )
        self.assertEqual(calculated_qty, 0.1)

    def test_atomic_order_execution_flow(self):
        """
        ทดสอบการยิงออเดอร์เข้า Exchange ว่าสามารถส่งสถานะกลับมาเป็น FILLED ได้ถูกต้อง
        """
        receipt = self.client.execute_market_order(symbol="BTCUSDT", side="BUY", quantity=0.05)
        self.assertEqual(receipt["status"], "FILLED")
        self.assertEqual(receipt["quantity"], 0.05)

if __name__ == '__main__':
    unittest.main()