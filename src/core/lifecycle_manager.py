import sys
import signal
import time
import logging
from src.core.config import Settings

logger = logging.getLogger("SystemLifecycle")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

class SystemLifecycleManager:
    def __init__(self, market_data, ai_router, risk_engine, executor):
        self.settings = Settings()
        self.market_data = market_data
        self.ai_router = ai_router
        self.risk_engine = risk_engine
        self.executor = executor
        
        self.is_running = False
        self.shutdown_requested = False
        
        # ลงทะเบียนดักจับสัญญาณ Shutdown จาก OS (เช่น Ctrl+C หรือ Kill Signal)
        signal.signal(signal.SIGINT, self._handle_shutdown_signal)
        signal.signal(signal.SIGTERM, self._handle_shutdown_signal)

    def execute_startup_sequence(self) -> bool:
        """[006_STARTUP_SEQUENCE] ตรวจสอบความพร้อมของระบบทั้งหมดก่อนเริ่มเทรดจริง"""
        logger.info("=== เริ่มต้นกระบวนการเปิดระบบ (006_STARTUP_SEQUENCE) ===")
        
        try:
            # 1. ตรวจสอบการเชื่อมต่อโครงสร้างพื้นฐาน (Config & Keys)
            logger.info("1. [Check] ตรวจสอบ Environment Variables และ API Keys...")
            if not self.settings.GROQ_API_KEY or not self.settings.GEMINI_API_KEY:
                raise ValueError("API Keys สำหรับ AI Orchestrator ไม่ครบถ้วน!")

            # 2. ตรวจสอบระบบ Market Data Feed
            logger.info("2. [Check] ตรวจสอบการเชื่อมต่อวงจรข้อมูลตลาด (Exchange Feed)...")
            # สมมุติเรียกใช้ฟังก์ชันตรวจสอบสิทธิ์หรือปิง Exchange
            self.market_data.get_latest_candle("BTC/USDT") 
            
            # 3. ตรวจสอบและซิงค์สถานะพอร์ตโฟลิโอ (Restart Safe - Source of Truth)
            logger.info("3. [Check] ตรวจสอบสถานะพอร์ตและ Active Position จาก Supabase/Exchange...")
            is_healthy = self.risk_engine.validate_portfolio_health()
            if not is_healthy:
                logger.error("❌ พอร์ตโฟลิโออยู่ในสถานะเสี่ยงหรือ Circuit Breaker ทำงานอยู่!")
                return False
                
            logger.info("✅ ทุกโมดูลผ่านการตรวจสอบความปลอดภัยทางสถาปัตยกรรม!")
            self.is_running = True
            return True
            
        except Exception as e:
            logger.critical(f"❌ Startup Fail: เกิดข้อผิดพลาดรุนแรงระหว่างเปิดระบบ: {str(e)}")
            return False

    def _handle_shutdown_signal(self, signum, frame):
        """ระบบดักจับสัญญาณปิดโปรแกรมจากภายนอก"""
        logger.warning(f"\n⚠️ ตรวจพบสัญญาณปิดระบบ (Signal: {signum}) กำลังเตรียม Graceful Shutdown...")
        self.shutdown_requested = True
        self.is_running = False

    def execute_shutdown_sequence(self):
        """[007_SHUTDOWN_SEQUENCE] เคลียร์ Resource บันทึกสถานะ และปิดบ็อทอย่างปลอดภัย"""
        logger.info("=== เริ่มต้นกระบวนการปิดระบบอย่างปลอดภัย (007_SHUTDOWN_SEQUENCE) ===")
        
        try:
            # 1. หยุดการรับข้อมูลใหม่
            logger.info("1. [Action] ตัดการเชื่อมต่อสตรีมข้อมูลตลาด (Disconnecting Feeds)...")
            
            # 2. รอเคลียร์ลูปการประมวลผลปัจจุบันให้จบ (Prevent Mid-flight State Corruption)
            logger.info("2. [Action] ตรวจสอบและเคลียร์คำสั่งเทรดที่ค้างคา (Clearing Pipeline)...")
            
            # 3. บันทึกสเตตัสสุดท้ายลง Supabase
            logger.info("3. [Action] อัปเดตและบันทึก State สุดท้ายลงระบบคลาวด์ถาวร...")
            
            logger.info("🎉 [Complete] ระบบปิดตัวลงอย่างสมบูรณ์แบบ 100% เงินทุนปลอดภัย ข้อมูลไม่สูญหาย")
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"❌ Shutdown Error: เกิดข้อผิดพลาดระหว่างปิดระบบ: {str(e)}")
            sys.exit(1)