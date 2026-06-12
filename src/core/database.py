import logging
from typing import Optional, Dict, Any
from supabase import create_client, Client

logger = logging.getLogger("DatabaseManager")

class SupabaseDatabaseManager:
    """
    ระบบจัดการฐานข้อมูลบนคลาวด์ (Supabase Cloud Persistence Layer)
    ทำหน้าที่บันทึกประวัติออเดอร์ และซิงค์สถานะ Active Position ป้องกันบ็อทความจำเสื่อม
    """
    def __init__(self):
        from src.core.config import settings
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_KEY
        
        if not self.url or not self.key:
            logger.error("❌ ไม่พบ SUPABASE_URL หรือ SUPABASE_KEY ในระบบ Environment!")
            self.client: Optional[Client] = None
        else:
            try:
                # เริ่มต้นการเชื่อมต่อเข้าคลาวด์ Supabase
                self.client = create_client(self.url, self.key)
                logger.info("📡 Connected to Supabase Cloud Database successfully.")
            except Exception as e:
                logger.error(f"❌ ไม่สามารถเชื่อมต่อ Supabase ได้: {e}")
                self.client = None

    # =====================================================================
    # ส่วนจัดการคำสั่งซื้อขาย (Order History - Table Name: 'order_history')
    # =====================================================================
    def save_order(self, order_id: str, symbol: str, side: str, quantity: float, price: float, stop_loss: float, take_profit: float, status: str):
        """บันทึกตั๋วออเดอร์ใหม่ยิงขึ้นคลาวด์ประวัติการเทรด"""
        if not self.client: return
        
        data = {
            "order_id": order_id,
            "symbol": symbol,
            "side": side.upper(),
            "quantity": float(quantity),
            "price": float(price),
            "stop_loss": float(stop_loss),
            "take_profit": float(take_profit),
            "status": status
        }
        try:
            # ใช้คำสั่ง upsert เพื่อบันทึกข้อมูลใหม่ หรืออัปเดตหากซ้ำเดิม
            self.client.table("order_history").upsert(data).execute()
            logger.info(f"☁️ [Cloud Saved] บันทึกออเดอร์ {order_id} ขึ้นสถิติ Supabase เรียบร้อย")
        except Exception as e:
            logger.error(f"❌ ไม่สามารถเซฟออเดอร์ขึ้น Supabase ได้: {e}")

    # =====================================================================
    # ส่วนจัดการสถานะพอร์ตหน้างาน (Active Position - Table Name: 'active_position')
    # =====================================================================
    def save_active_position(self, symbol: str, side: str, entry_price: float, size: float, stop_loss: float, take_profit: float, order_id: str):
        """ฝังสถานะโพสิชั่นที่เปิดค้างอยู่ขึ้นคลาวด์"""
        if not self.client: return
        
        data = {
            "symbol": symbol,
            "side": side.upper(),
            "entry_price": float(entry_price),
            "size": float(size),
            "stop_loss": float(stop_loss),
            "take_profit": float(take_profit),
            "order_id": order_id
        }
        try:
            self.client.table("active_position").upsert(data).execute()
            logger.info(f"☁️ [Cloud Saved] ฝังสถานะโพสิชั่น {symbol} ไว้บนระบบคลาวด์เรียบร้อย")
        except Exception as e:
            logger.error(f"❌ ไม่สามารถเซฟ Active Position ขึ้น Supabase ได้: {e}")

    def load_active_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """ดึงสถานะโพสิชั่นที่เปิดค้างไว้ล่าสุดจากคลาวด์กลับมาใช้งานในเครื่องตอนเปิดบ็อท"""
        if not self.client: return None
        
        try:
            response = self.client.table("active_position").select("*").eq("symbol", symbol).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"❌ ไม่สามารถโหลด Active Position จาก Supabase ได้: {e}")
            return None

    def clear_active_position(self, symbol: str):
        """ลบโพสิชั่นออกจากตารางบนคลาวด์เมื่อทำกำไรหรือคัตขาดทุนสำเร็จแล้ว"""
        if not self.client: return
        
        try:
            self.client.table("active_position").delete().eq("symbol", symbol).execute()
            logger.info(f"☁️ [Cloud Cleared] เคลียร์โพสิชั่น {symbol} ออกจากตารางหน้างานคลาวด์เรียบร้อย")
        except Exception as e:
            logger.error(f"❌ ไม่สามารถเคลียร์ Active Position บน Supabase ได้: {e}")

# ประกาศอินสแตนซ์ DB เป็น Singleton พร้อมใช้งานทั้งระบบ
db_manager = SupabaseDatabaseManager()