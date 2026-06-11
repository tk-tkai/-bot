import unittest
from src.modules.risk_management.risk_engine import RiskEngine
from src.modules.risk_management.order_validator import OrderValidator

class TestRiskManagementModule(unittest.TestCase):
    def setUp(self):
        self.risk_engine = RiskEngine(max_daily_loss_pct=2.0, max_drawdown_pct=5.0)
        self.validator = OrderValidator(min_notional=10.0, max_notional=5000.0)

    def test_risk_engine_blocks_high_drawdown(self):
        """
        ทดสอบว่า Risk Engine ต้องสั่งบล็อกสัญญาณทันทีหากพอร์ตย่อตัวเกินกฎ 5%
        """
        bad_account_metrics = {
            "initial_balance": 10000.0,
            "current_equity": 9400.0,  # ร่วงลงมาเหลือ 9400 จากจุดสูงสุด 10000 (ย่อตัว 6%)
            "daily_realized_pnl": -100.0,
            "peak_equity": 10000.0
        }
        is_safe = self.risk_engine.check_portfolio_health(bad_account_metrics)
        self.assertFalse(is_safe)  # ต้องได้ค่า False (บล็อก)

    def test_order_validator_requires_stop_loss(self):
        """
        ทดสอบกฎเหล็ก: ออเดอร์ที่ไม่มีการตั้งค่า Stop Loss จะต้องถูกปฏิเสธ 100%
        """
        naked_order = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "quantity": 0.05,
            "price": 60000.0,
            "stop_loss": None  # ไม่ใส่ Stop Loss
        }
        is_valid = self.validator.validate_order_spec(naked_order)
        self.assertFalse(is_valid)

if __name__ == '__main__':
    unittest.main()