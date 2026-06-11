from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """
    Abstract Base Class สำหรับทุกกลยุทธ์ในระบบ
    บังคับให้ส่งออกเฉพาะ Signal Object เพื่อส่งต่อให้ Risk Engine ตรวจสอบ
    """
    def __init__(self, name: str):
        self.strategy_name = name

    @abstractmethod
    def calculate_signal(self, market_context: dict, ai_analysis: dict) -> dict:
        """
        คำนวณหาลอจิกการเทรด 
        Input: ข้อมูลอินดิเคเตอร์ (Market Context) และ ผลวิเคราะห์จาก AI (AI Analysis)
        Output: Dictionary ของ Signal (ห้าม Execute ออเดอร์เองเด็ดขาด)
        """
        pass

    def _generate_signal_package(self, action: str, target_price: float, stop_loss: float, take_profit: float, reason: str) -> dict:
        """
        ฟังก์ชันมาตรฐานในการแพ็คโครงสร้างสัญญาณซื้อขาย (Signal Contract)
        ACTION: "BUY", "SELL", or "HOLD"
        """
        return {
            "strategy_name": self.strategy_name,
            "action": action,              # BUY, SELL, HOLD
            "target_price": float(target_price),
            "stop_loss": float(stop_loss),
            "take_profit": float(take_profit),
            "reason": reason
        }