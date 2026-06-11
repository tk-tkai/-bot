import logging
from src.modules.ai_orchestrator.clients.groq_client import GroqClient
from src.modules.ai_orchestrator.clients.gemini_client import GeminiClient
from src.modules.ai_orchestrator.prompts.base_prompt import BasePrompt

logger = logging.getLogger("AIRouterService")

class AIRouterService:
    """
    เอนจินหลักในการบริหารจัดการคำขอวิเคราะห์จากระบบเทรดไปยัง AI Providers
    รองรับระบบ Multi-Provider และ Automatic Failover เพื่อป้องกันการชน Limit
    """
    def __init__(self):
        # เริ่มต้นโหลด Client ของทั้งค่ายหลักและค่ายสำรอง
        try:
            self.main_client = GroqClient()
        except Exception as e:
            logger.warning(f"Unable to initialize Groq Client: {e}. Will rely on fallback.")
            self.main_client = None

        try:
            self.fallback_client = GeminiClient()
        except Exception as e:
            logger.warning(f"Unable to initialize Gemini Client: {e}")
            self.fallback_client = None

        self.prompt_manager = BasePrompt()

    def get_market_analysis(self, market_context: dict) -> dict:
        """
        รับ Market Context (JSON จากโมดูล 1) เข้ามาประกอบ Prompt 
        และส่งให้ AI ที่พร้อมทำงานที่สุดวิเคราะห์ผลลัพธ์กลับมา
        """
        # 1. ดึงข้อความระเบียบปฏิบัติ (System Prompt) และเตรียมข้อมูลตลาด (User Context)
        system_prompt = self.prompt_manager.get_system_prompt()
        user_context_str = self.prompt_manager.format_user_context(market_context)

        # 2. ทำงานผ่านค่ายหลัก (Groq Client) เป็นอันดับแรก
        if self.main_client:
            try:
                logger.info("Sending market context to Primary AI Provider (Groq)...")
                analysis_result = self.main_client.generate_analysis(system_prompt, user_context_str)
                return self._validate_response_structure(analysis_result)
            except Exception as e:
                logger.error(f"Primary AI Provider failed due to Limit/Error: {str(e)}. Activating Failover...")

        # 3. กลไกสลับค่ายอัตโนมัติ (Automatic Failover) ไปยังค่ายสำรอง (Gemini Client)
        if self.fallback_client:
            try:
                logger.info("Sending market context to Secondary AI Provider (Gemini)...")
                analysis_result = self.fallback_client.generate_analysis(system_prompt, user_context_str)
                return self._validate_response_structure(analysis_result)
            except Exception as e:
                logger.critical(f"Secondary AI Provider also failed: {str(e)}")
        
        # 4. หาก AI ทุกค่ายล่มพร้อมกัน จะส่งสัญญาณแจ้งเตือนให้เข้าสู่โหมด Fallback to Pure Technical
        logger.critical("All AI Providers are unavailable or hit rate limit! Shifting to Fallback Mode.")
        return self._generate_emergency_fallback_response()

    def _validate_response_structure(self, response: dict) -> dict:
        """
        ตรวจสอบความถูกต้องของโครงสร้าง JSON เพื่อให้เป็นไปตาม Executable Specification Contract
        """
        required_keys = ["regime", "confidence_score", "reasoning"]
        for key in required_keys:
            if key not in response:
                raise ValueError(f"Invalid AI Response Structure. Missing key: {key}")
        return response

    def _generate_emergency_fallback_response(self) -> dict:
        return {
            "regime": "UNKNOWN_LIMIT_REACHED",
            "confidence_score": 0.0,
            "reasoning": "Emergency Fallback: All AI provider connections lost or limit reached. Bypass to Technical Rules.",
            "emergency_bypass": True
        }

    def analyze_market(self, market_context: dict) -> dict:
        """
        สร้าง Alias ฟังก์ชันเพื่อรองรับท่อส่งข้อมูล (Pipeline) ในไฟล์ main.py
        """
        return self.get_market_analysis(market_context)
        
        return {
            "regime": "UNKNOWN_LIMIT_REACHED",
            "confidence_score": 0.0,
            "reasoning": "Emergency Fallback: All AI provider connections lost or limit reached. Bypass to Technical Rules.",
            "emergency_bypass": True
        }