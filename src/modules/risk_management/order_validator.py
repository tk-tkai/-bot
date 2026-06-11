import logging

logger = logging.getLogger(__name__)

class OrderValidator:
    def __init__(self, min_notional: float = 10.0, max_notional: float = 5000.0):
        """
        ระบบตรวจสอบความถูกต้องและป้องกันข้อผิดพลาดของคำสั่งซื้อขาย (Order Validator)
        :param min_notional: มูลค่าออเดอร์ขั้นต่ำ (เช่น $10 ตามกฎ Exchange)
        :param max_notional: มูลค่าออเดอร์สูงสุดต่อไม้เพื่อป้องกัน Fat Finger ($5000)
        """
        self.min_notional = min_notional
        self.max_notional = max_notional
        self.active_order_hashes = set()  # เก็บ Hash ของออเดอร์ที่กำลังทำงานเพื่อป้องกันยิงซ้ำ

    def validate_order_spec(self, order_proposal: dict) -> bool:
        """
        ตรวจโครงสร้างและความปลอดภัยของออเดอร์ก่อนส่งเข้า Exchange
        order_proposal = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "quantity": 0.01,
            "price": 65000.0,
            "stop_loss": 64000.0
        }
        """
        symbol = order_proposal.get("symbol")
        side = order_proposal.get("side")
        qty = order_proposal.get("quantity", 0.0)
        price = order_proposal.get("price", 0.0)
        sl = order_proposal.get("stop_loss")

        # 1. ตรวจสอบข้อมูลพื้นฐาน (Sanity Check)
        if not symbol or side not in ["BUY", "SELL"]:
            logger.error("Order Validation Failed: Missing symbol or invalid side.")
            return False

        if qty <= 0 or price <= 0:
            logger.error("Order Validation Failed: Quantity and Price must be greater than zero.")
            return False

        # 2. ตรวจสอบมูลค่าขั้นต่ำและสูงสุด (Notional Value Limits)
        notional_value = qty * price
        if notional_value < self.min_notional:
            logger.warning(f"Order Rejected: Notional value ${notional_value:.2f} is below minimum ${self.min_notional}.")
            return False
        if notional_value > self.max_notional:
            logger.warning(f"Order Rejected: Notional value ${notional_value:.2f} exceeds fat-finger limit ${self.max_notional}.")
            return False

        # 3. กฎเหล็ก: ต้องมี Stop Loss เสมอ (No Naked Positions)
        if not sl or sl <= 0:
            logger.error(f"Order Rejected: Safe Execution Policy requires a valid Stop Loss.")
            return False

        # 4. ป้องกันออเดอร์ซ้ำซ้อน (Anti-Idempotency Check)
        order_id_string = f"{symbol}_{side}_{qty}_{price}"
        if order_id_string in self.active_order_hashes:
            logger.warning(f"Order Rejected: Duplicate execution blocked for {order_id_string}.")
            return False

        # ถ้ารอดทุกด่าน ให้บันทึกสถานะกำลังทำงานไว้
        self.active_order_hashes.add(order_id_string)
        logger.info(f"Order Validator Status: APPROVED for {symbol} {side} (Value: ${notional_value:.2f}).")
        return True

    def clear_order_fingerprint(self, order_proposal: dict):
        """
        ล้างลายนิ้วมือออเดอร์เมื่อทำงานเสร็จสิ้น เพื่อให้ออเดอร์ใหม่ในอนาคตทำงานได้
        """
        order_id_string = f"{order_proposal.get('symbol')}_{order_proposal.get('side')}_{order_proposal.get('quantity')}_{order_proposal.get('price')}"
        self.active_order_hashes.discard(order_id_string)