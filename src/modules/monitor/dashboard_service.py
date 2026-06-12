import logging
from datetime import datetime
from typing import Dict, Any

# กำหนดรูปแบบ Logging ให้เป็นมาตรฐานเดียวกันทั้งระบบ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class DashboardService:
    """
    DashboardService: รับผิดชอบการแสดงผลสถานะระบบ (Monitoring)
    ยึดหลักการ 'Passive Observer' เพื่อไม่ให้ขัดขวางการทำงานของ Order Execution Pipeline
    """
    def __init__(self):
        self.logger = logging.getLogger("SystemDashboard")

    def log_trade_execution(self, order_details: Dict[str, Any]):
        """บันทึกสถานะการส่งคำสั่งซื้อขาย"""
        self.logger.info(f"--- [ORDER EXECUTED] ---")
        self.logger.info(f"Time: {datetime.now().isoformat()}")
        self.logger.info(f"Symbol: {order_details.get('symbol')}")
        self.logger.info(f"Side: {order_details.get('side')}")
        self.logger.info(f"Amount: {order_details.get('amount')}")
        self.logger.info(f"Status: {order_details.get('status')}")

    def log_portfolio_status(self, position_tracker_data: Dict[str, Any]):
        """บันทึกสถานะพอร์ตจาก position_tracker.py"""
        self.logger.info(f"--- [PORTFOLIO STATUS] ---")
        self.logger.info(f"Total Balance: {position_tracker_data.get('balance')}")
        self.logger.info(f"Active Positions: {len(position_tracker_data.get('positions', []))}")
        self.logger.info(f"Unrealized PnL: {position_tracker_data.get('unrealized_pnl')}")

    def alert_critical_issue(self, error_message: str):
        """ช่องทางแจ้งเตือนกรณีระบบผิดปกติ (System Safeguard)"""
        self.logger.error(f"!!! [SYSTEM CRITICAL ALERT] !!!")
        self.logger.error(f"Message: {error_message}")