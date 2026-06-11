import logging

logger = logging.getLogger(__name__)

class RiskEngine:
    def __init__(self, max_daily_loss_pct: float = 2.0, max_drawdown_pct: float = 5.0):
        """
        ระบบควบคุมความเสี่ยงส่วนกลาง (Risk Engine)
        :param max_daily_loss_pct: เปอร์เซ็นต์ขาดทุนสูงสุดที่ยอมรับได้ต่อวัน (Default: 2%)
        :param max_drawdown_pct: เปอร์เซ็นต์ Drawdown สูงสุดจากจุดสูงสุดของพอร์ต (Default: 5%)
        """
        self.max_daily_loss_pct = max_daily_loss_pct
        self.max_drawdown_pct = max_drawdown_pct

    def check_portfolio_health(self, account_metrics: dict) -> bool:
        """
        ตรวจสอบสุขภาพของพอร์ตปัจจุบันตามกฎเหล็กควบคุมความเสี่ยง
        account_metrics = {
            "initial_balance": 10000.0,
            "current_equity": 9850.0,
            "daily_realized_pnl": -150.0,
            "peak_equity": 10200.0
        }
        """
        initial_balance = account_metrics.get("initial_balance", 0.0)
        current_equity = account_metrics.get("current_equity", 0.0)
        daily_pnl = account_metrics.get("daily_realized_pnl", 0.0)
        peak_equity = account_metrics.get("peak_equity", current_equity)

        if initial_balance <= 0:
            logger.error("Risk Engine Rejected: Invalid initial balance.")
            return False

        # 1. ตรวจสอบกฎ Daily Loss Limit (ขีดจำกัดขาดทุนรายวัน)
        daily_loss_pct = (abs(daily_pnl) / initial_balance) * 100 if daily_pnl < 0 else 0.0
        if daily_loss_pct >= self.max_daily_loss_pct:
            logger.warning(f"Risk Engine Violation: Daily Loss Limit Reached ({daily_loss_pct:.2f}%).")
            return False

        # 2. ตรวจสอบกฎ Maximum Drawdown (ขีดจำกัดการย่อตัวของพอร์ตจากจุดสูงสุด)
        current_dd_pct = ((peak_equity - current_equity) / peak_equity) * 100 if peak_equity > 0 else 0.0
        if current_dd_pct >= self.max_drawdown_pct:
            logger.warning(f"Risk Engine Violation: Max Drawdown Reached ({current_dd_pct:.2f}%).")
            return False

        logger.info("Risk Engine Status: PASSED (Portfolio health is optimal).")
        return True