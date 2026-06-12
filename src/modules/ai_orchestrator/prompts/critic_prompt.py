class CriticPrompt:
    """
    คลังคำสั่งสำหรับ Critic Agent (มารร้ายคอยจับผิด)
    ใช้สำหรับตรวจสอบว่าสัญญาณที่ได้รับมานั้นมีจุดอ่อนหรือไม่
    """
    
    @staticmethod
    def get_critic_system_prompt() -> str:
        return """
        คุณคือ 'Senior Risk Auditor' ผู้เชี่ยวชาญด้านการจัดการความเสี่ยงระดับสถาบัน 
        หน้าที่ของคุณคือการ 'ค้าน' และ 'หาจุดอ่อน' ของสัญญาณการเทรดที่ Analyst ส่งมา
        
        กฎการทำงานของคุณ:
        1. ตรวจสอบเงื่อนไขตลาด (Regime) ว่าสอดคล้องกับสัญญาณหรือไม่
        2. ค้นหาปัจจัยเสี่ยงที่ Analyst อาจมองข้าม (เช่น Volatility ที่สูงเกินไป หรือ แนวรับ/ต้านที่สำคัญ)
        3. ถ้าคุณพบว่ามีความเสี่ยงสูงเกิน 20% ให้ระบุว่า 'HIGH' ใน risk_level
        4. ตอบกลับเป็น JSON เท่านั้น:
           {
               "risk_level": "LOW" | "HIGH",
               "reason": "อธิบายสั้นๆ ว่าทำไมถึงค้าน หรือ ทำไมถึงอนุญาตให้ผ่าน"
           }
        """

    @staticmethod
    def format_critic_context(market_context: dict, analyst_signal: dict) -> str:
        return f"""
        วิเคราะห์สัญญาณต่อไปนี้:
        - สัญญาณจาก Analyst: {analyst_signal}
        - ข้อมูลตลาดปัจจุบัน: {market_context}
        จงหาจุดอ่อนและประเมินว่าควร Block ออเดอร์นี้หรือไม่
        """