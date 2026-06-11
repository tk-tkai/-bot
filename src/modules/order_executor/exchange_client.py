import logging
import time

logger = logging.getLogger(__name__)

class ExchangeClient:
    def __init__(self, api_key: str = None, secret_key: str = None):
        self.api_key = api_key
        self.secret_key = secret_key
        self.order_book_status = {}  # จำลองสถานะออเดอร์ที่จดไว้ในระบบ (Local)

    def execute_market_order(self, symbol: str, side: str, quantity: float) -> dict:
        """
        ยิงคำสั่งซื้อขายราคาตลาด (Market Order) แบบ Atomic Execution
        """
        logger.info(f"Sending Market Order to Exchange: {side} {quantity} {symbol}")
        
        # จำลองสถานการณ์การส่งออเดอร์ (Network Roundtrip)
        time.sleep(0.05) 
        
        order_id = f"cl_id_{int(time.time() * 1000)}"
        order_receipt = {
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "status": "FILLED",
            "timestamp": time.time()
        }
        
        # บันทึกประวัติไว้ตรวจสอบ
        self.order_book_status[order_id] = order_receipt
        logger.info(f"Order Executed Successfully. Exchange Order ID: {order_id}")
        return order_receipt

    def gap_recovery_check(self, client_order_id: str) -> str:
        """
        ระบบ Gap Recovery: ตรวจสอบสถานะออเดอร์กรณีเน็ตหลุดระหว่างส่งคำสั่ง
        ป้องกันการส่งออเดอร์ซ้ำซ้อน (Double Ordering)
        """
        logger.info(f"Gap Recovery initiated for Order ID: {client_order_id}")
        # ถ้าระบบหาเจอบน Exchange แปลว่าคำสั่งสำเร็จไปแล้วก่อนเน็ตหลุด
        if client_order_id in self.order_book_status:
            return self.order_book_status[client_order_id]["status"]
        
        # ถ้าหาไม่เจอ แปลว่าคำสั่งยังไม่ถึง Exchange ให้ตีเป็นร่วง
        return "NOT_FOUND"