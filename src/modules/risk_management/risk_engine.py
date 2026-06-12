import logging
from src.core.config import settings

logger = logging.getLogger("RiskEngine")

class RiskEngine:
    """
    Risk Engine: ผู้มีอำนาจสิทธิ์ขาดสูงสุด (Final Authority) ในการควบคุมความเสี่ยงของพอร์ต
    ทำหน้าที่คำนวณขนาดไม้ (Position Sizing) และตรวจสอบกฎเหล็ก Safeguards ก่อนส่งคำสั่งเทรด
    """
    def __init__(self):
        # โหลดค่า Guardrails จาก Settings Source แกนหลัก
        self.max_loss_usd = settings.MAX_LOSS_PER_TRADE_USD  # $1.0 USD
        self.total_capital = settings.TOTAL_PORTFOLIO_CAPITAL # $60.0 USD
        self.min_lot_size = settings.min_lot_size            # 0.001 BTC
        self.price_precision = settings.price_precision        # 2 ตำแหน่ง

    def validate_portfolio_health(self, current_balance: float, total_drawdown: float) -> bool:
        """
        ตรวจสอบสุขภาพโดยรวมของพอร์ต (Portfolio Safeguard)
        หาก Drawdown รวมของพอร์ตเกินเกณฑ์ที่กำหนด จะสั่งล็อกไม่ให้เปิดเพิ่มเด็ดขาด
        """
        max_allowed_drawdown = self.total_capital * 0.20 # ยอมรับ Drawdown สูงสุดได้ 20% ของพอร์ต ($12)
        
        if total_drawdown >= max_allowed_drawdown:
            logger.warning(f"❌ [Risk Blocked] พอร์ตมี Drawdown สูงเกินเกณฑ์ (${total_drawdown:.2f} >= ${max_allowed_drawdown:.2f}) ไม่อนุญาตให้เปิดเพิ่ม")
            return False
            
        if current_balance <= self.max_loss_usd:
            logger.warning(f"❌ [Risk Blocked] เงินทุนในพอร์ตเหลือน้อยเกินไป (${current_balance:.2f} <= ${self.max_loss_usd:.2f})")
            return False
            
        return True

    def calculate_position_size(self, current_price: float, stop_loss_price: float) -> float:
        """
        คำนวณขนาดของออเดอร์ (Position Sizing Formula) ล็อกความเสี่ยงไม่เกิน $1 ตามกฎเหล็ก
        Formula: Position Size = Max Loss USD / (Price Distance to Stop Loss)
        """
        if current_price <= 0 or stop_loss_price <= 0:
            logger.error("❌ ราคาที่นำมาคำนวณขนาด Position ต้องมากกว่า 0")
            return 0.0

        price_distance = abs(current_price - stop_loss_price)
        if price_distance == 0:
            logger.warning("⚠️ ราคาปัจจุบันและราคา Stop Loss อยู่ที่เดียวกัน ไม่สามารถคำนวณขนาดไม้ได้")
            return 0.0

        # คำนวณขนาดไม้ดิบ (Raw Size) ตามระยะห่างของ Stop Loss
        raw_position_size = self.max_loss_usd / price_distance
        
        # ปรับความละเอียดทศนิยม (Rounding) ให้ตรงตามกฎของ Exchange ที่โหลดมาจาก trading_rules.json
        # ตัวอย่างเช่น BTC บังคับขั้นต่ำ 0.001 สัญญา
        step = self.min_lot_size
        final_position_size = round(raw_position_size / step) * step
        
        # ป้องกันไม่ให้ขนาดไม้เล็กเกินกว่าที่ตลาดอนุญาต
        if final_position_size < self.min_lot_size:
            logger.warning(f"⚠️ ขนาดไม้ที่คำนวณได้ ({final_position_size}) ต่ำกว่าขั้นต่ำของตลาด ({self.min_lot_size}) บังคับใช้ขนาดขั้นต่ำแทน")
            final_position_size = self.min_lot_size

        # ด่านตรวจความคุ้มค่าและความปลอดภัย (Safety Cap) ป้องกันความผิดพลาดทางลอจิก
        max_leverage_cap = (self.total_capital * 3) / current_price # คุม Leverage รวมไม่ให้เกิน 3 เท่าของทุน
        if final_position_size > max_leverage_cap:
            logger.warning(f"⚠️ [Risk Cap] ขนาดไม้ใหญ่เกินขีดจำกัด ปรับลดลงมาเป็น {max_leverage_cap:.4f} เพื่อความปลอดภัย")
            final_position_size = round(max_leverage_cap / step) * step

        logger.info(f"📐 [Risk Size Calculated] Price: {current_price} | SL: {stop_loss_price} | ได้ขนาดไม้: {final_position_size:.4f} สัญญา (ความเสี่ยงจำกัดที่ ${self.max_loss_usd})")
        return final_position_size

# สร้างอินสแตนซ์พร้อมใช้งานแบบ Singleton
risk_engine = RiskEngine()