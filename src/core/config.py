from fileinput import filename
import os
import json
import logging

logger = logging.getLogger("ConfigManager")

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
        self.GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
# ระบบเครือข่ายและการรอคอย (Network Resilience)
        self.API_TIMEOUT_SEC = int(os.getenv("API_TIMEOUT_SEC", 10))
        self.MAX_AI_RETRIES = int(os.getenv("MAX_AI_RETRIES", 3))

        # 3. คอนฟิก Supabase สำหรับระบบคลาวด์ (พร้อมสับไกเชื่อมต่อ)
        self.SUPABASE_URL = os.getenv("SUPABASE_URL", "")
        self.SUPABASE_KEY = os.getenv("SUPABASE_KEY", "") 
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///trading_system.db")

        # 3. Exchange API Credentials (อ่านตรงจาก Env ปลอดภัยสูงสุด)
        self.EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY", "mock_key")
        self.EXCHANGE_SECRET_KEY = os.getenv("EXCHANGE_SECRET_KEY", "mock_secret")

        # 4. Risk Engine Guardrails (กฎเหล็กคุมเงินไม้ละ $1)
        self.TOTAL_PORTFOLIO_CAPITAL = float(os.getenv("TOTAL_PORTFOLIO_CAPITAL", 60.0))
        self.MAX_LOSS_PER_TRADE_USD = float(os.getenv("MAX_LOSS_PER_TRADE_USD", 1.0))
        self.RISK_PER_TRADE_PCT = float(os.getenv("RISK_PER_TRADE_PCT", 1.67))
        self.TRADING_ENV = os.getenv("TRADING_ENV", "PAPER").upper()

        # 5. โดเมนกฎการเทรด (เฉพาะข้อมูลเชิงสถิติที่ไม่ใช่ความลับ)
        self.TRADING_RULES = self._load_json_file("trading_rules.json", {"MIN_LOT_SIZE": 0.001, "PRICE_PRECISION": 2})

        # 4. คอนฟิกการเชื่อมต่อระบบฐานข้อมูลภายใน (Core Infrastructure Caches)
        self.REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///trading_system.db")

    def _load_json_file(self, filename: str, default_val: dict) -> dict:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        file_path = os.path.join(base_dir, filename)
        
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"❌ เกิดข้อผิดพลาดในการอ่านไฟล์คอนฟิก {filename}: {e}")
                return default_val
        else:
            return default_val

    @property
    def min_lot_size(self) -> float:
        return float(self.TRADING_RULES.get("MIN_LOT_SIZE", 0.001))

    @property
    def price_precision(self) -> int:
        return int(self.TRADING_RULES.get("PRICE_PRECISION", 2))

# ประกาศตัวแปร Singleton เพื่อความมั่นใจทั้งระบบ
settings = Settings()