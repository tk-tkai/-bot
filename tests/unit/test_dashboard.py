import unittest
from unittest.mock import MagicMock, patch
from src.modules.monitor.dashboard_service import DashboardService

class TestDashboardService(unittest.TestCase):
    def setUp(self):
        """ตั้งค่าเริ่มต้นก่อนรัน Test แต่ละเคส"""
        self.dashboard = DashboardService()

    def test_log_trade_execution_success(self):
        """ทดสอบการบันทึกข้อมูลการเทรดปกติ"""
        mock_order = {
            "symbol": "BTC/USDT",
            "side": "buy",
            "amount": 0.1,
            "status": "filled"
        }
        # ตรวจสอบว่าฟังก์ชันทำงานโดยไม่มี Error
        try:
            self.dashboard.log_trade_execution(mock_order)
        except Exception as e:
            self.fail(f"log_trade_execution failed unexpectedly: {e}")

    def test_alert_critical_issue(self):
        """ทดสอบระบบแจ้งเตือนเมื่อเกิดเหตุวิกฤต"""
        with self.assertLogs("SystemDashboard", level="ERROR") as cm:
            self.dashboard.alert_critical_issue("Database Connection Lost")
        
        self.assertTrue(any("Database Connection Lost" in log for log in cm.output))

    def test_portfolio_status_handling(self):
        """ทดสอบว่า Dashboard รองรับโครงสร้างข้อมูลพอร์ตโฟลิโอ"""
        portfolio = {
            "balance": 10000,
            "positions": ["BTC"],
            "unrealized_pnl": 50.5
        }
        try:
            self.dashboard.log_portfolio_status(portfolio)
        except Exception as e:
            self.fail(f"log_portfolio_status failed: {e}")

if __name__ == '__main__':
    unittest.main()