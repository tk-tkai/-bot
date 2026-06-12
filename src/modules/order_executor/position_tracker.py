import logging
from src.core.config import settings

logger = logging.getLogger("PositionTracker")

class PositionTracker:
    """
    Position Tracker: เฝ้าระวังและติดตามสถานะออเดอร์ค้างพอร์ตแบบ Real-time
    คำนวณค่า PnL ล็อกเงื่อนไขการตัดขาดทุนและทำกำไร (Stop-Loss / Take-Profit Guardian)
    """
    def __init__(self):
        self.max_loss_usd = settings.MAX_LOSS_PER_TRADE_USD # ดึงค่า $1 มาคุมหน้างาน

    def check_position_status(self, position: dict, current_price: float) -> dict:
        """
        ตรวจสอบสถานะ PnL ของโพสิชั่นปัจจุบัน และส่งสัญญาณ Action ออกมาหากเข้าเงื่อนไขคัตเอาท์
        - position structure: {"symbol": str, "entry_price": float, "size": float, "direction": str}
        """
        symbol = position.get("symbol", "UNKNOWN")
        entry_price = float(position.get("entry_price", 0.0))
        size = float(position.get("size", 0.0))
        direction = position.get("direction", "LONG").upper()

        if size == 0 or entry_price == 0:
            return {"action": "HOLD", "pnl_usd": 0.0, "reason": "ไม่มีโพสิชั่นถือครองค้างอยู่"}

        # 1. คำนวณหา Unrealized PnL ตามฝั่งการเทรด (Long / Short)
        if direction == "LONG":
            pnl_usd = (current_price - entry_price) * size
        else: # SHORT Position
            pnl_usd = (entry_price - current_price) * size

        logger.info(f"🔄 [Monitoring] {symbol} | Side: {direction} | Price: {current_price} | Entry: {entry_price} | PnL: ${pnl_usd:.2f}")

        # 2. ด่านตรวจกฎเหล็กคัตเอาท์ติดลบเกิน $1 USD (Hard Stop Loss)
        if pnl_usd <= -self.max_loss_usd:
            logger.warning(f"🚨 [CRITICAL CUTOUT] ยอดติดลบถึงเกณฑ์จำกัดความเสี่ยง (${pnl_usd:.2f} <= -${self.max_loss_usd}) สั่งปิดสัญญาด่วน!")
            return {"action": "MARKET_CLOSE", "pnl_usd": pnl_usd, "reason": f"ชนเกณฑ์จำกัดความเสี่ยงดักขาดทุน {self.max_loss_usd} USD"}

        # 3. ด่านตรวจเงื่อนไขทำกำไรเป้าหมาย (Take Profit - ตั้งค่าสัดส่วน Risk/Reward ไว้ที่ 1:2 ขยับตามความเหมาะสม)
        target_profit_usd = self.max_loss_usd * 2.0 # เป้าทำกำไรที่ $2 USD
        if pnl_usd >= target_profit_usd:
            logger.info(f"💰 [TAKE PROFIT reached] ยอดกำไรถึงเป้าหมายการันตีรางวัล (${pnl_usd:.2f} >= ${target_profit_usd}) สั่งล็อกกำไรเข้าพอร์ต!")
            return {"action": "MARKET_CLOSE", "pnl_usd": pnl_usd, "reason": f"กำไรถึงเป้าหมาย Risk/Reward Ratio (${target_profit_usd} USD)"}

        # 4. หากราคายังวิ่งสวิงอยู่ในกรอบปลอดภัย ให้ถือประคองสัญญาต่อ
        return {"action": "HOLD", "pnl_usd": pnl_usd, "reason": "ราคายังวิ่งอยู่ในกรอบความเสี่ยงที่ปลอดภัย"}

    
# สร้างอินสแตนซ์พร้อมใช้งานแบบ Singleton
position_tracker = PositionTracker()