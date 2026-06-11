import os

class Settings:
    """
    ศูนย์รวมการจัดการ Configuration และ API Keys ทั้งระบบ (Central Settings Source)
    ทำหน้าที่โหลดค่าจาก Environment Variables หรือกำหนดค่าเริ่มต้นให้ระบบเทรด
    """
    def __init__(self):
        # 1. โหลด API Keys ของปัญญาประดิษฐ์ (AI Providers)
        # หากเป็นการทดสอบระบบและยังไม่มีการตั้งค่า Env ค่า Mock String ด้านหลังจะทำงานอัตโนมัติ
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "mock_groq_key_for_testing")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "mock_gemini_key_for_testing")
        
        # 2. กำหนดรุ่นของโมเดล AI (AI Models Specs)
        self.GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        # 3. คอนฟิกการเชื่อมต่อระบบฐานข้อมูลภายใน (Core Infrastructure Caches)
        self.REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///trading_system.db")

# ประกาศตัวแปร settings ในฐานะ Singleton Instance สำหรับให้โมดูลอื่นๆ เรียกใช้ร่วมกันทั้งระบบ
settings = Settings()