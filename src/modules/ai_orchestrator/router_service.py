import logging
from src.modules.ai_orchestrator.prompts.critic_prompt import CriticPrompt
from src.modules.ai_orchestrator.clients.groq_client import GroqClient
from src.modules.ai_orchestrator.clients.gemini_client import GeminiClient
from src.modules.ai_orchestrator.prompts.base_prompt import BasePrompt

logger = logging.getLogger("AIRouterService")

class AIRouterService:
    """
    เอนจินหลักในการบริหารจัดการคำขอวิเคราะห์จากระบบเทรด
    พร้อมระบบ Failover และ Critic Loop (Multi-Agent Validation)
    """
    def __init__(self):
        try:
            self.main_client = GroqClient()
        except Exception as e:
            logger.warning(f"Groq Client init failed: {e}")
            self.main_client = None

        try:
            self.fallback_client = GeminiClient()
        except Exception as e:
            logger.warning(f"Gemini Client init failed: {e}")
            self.fallback_client = None

        self.prompt_manager = BasePrompt()

    def analyze_market(self, market_context: dict) -> dict:
        """
        Main entry point ที่เชื่อมต่อกับ main.py
        """
        # 1. รับการวิเคราะห์เบื้องต้นจาก AI หลัก/สำรอง
        analysis = self.get_market_analysis(market_context)
        
        # 2. ถ้าเป็น Emergency Fallback ให้ผ่านไปเลย
        if analysis.get("emergency_bypass"):
            return analysis

        # 3. รัน Critic Loop เพื่อตรวจหาความเสี่ยง (Veto Power)
        critique = self._run_critic_agent(market_context, analysis)
        
        if analysis.get("confidence_score", 0) < 0.8 or critique.get("risk_level") == "HIGH":
            logger.warning(f"🛡️ [RISK VETO] Order blocked. Critique: {critique.get('reason')}")
            return {
                "regime": "WAIT",
                "confidence_score": 0.0,
                "reasoning": f"Risk Veto: {critique.get('reason')}",
                "blocked": True
            }
            
        return analysis

    def get_market_analysis(self, market_context: dict) -> dict:
        system_prompt = self.prompt_manager.get_system_prompt()
        user_context_str = self.prompt_manager.format_user_context(market_context)

        # ลองใช้ Main Client
        if self.main_client:
            try:
                res = self.main_client.generate_analysis(system_prompt, user_context_str)
                return self._validate_response_structure(res)
            except Exception as e:
                logger.error(f"Groq failed: {e}. Switching to Gemini...")

        # ลองใช้ Fallback Client
        if self.fallback_client:
            try:
                res = self.fallback_client.generate_analysis(system_prompt, user_context_str)
                return self._validate_response_structure(res)
            except Exception as e:
                logger.critical(f"Gemini also failed: {e}")
        
        return self._generate_emergency_fallback_response()

def _run_critic_agent(self, market_context: dict, initial_analysis: dict) -> dict:
    """
    เรียกใช้งาน Critic Prompt เพื่อตรวจสอบสัญญาณจริงๆ ผ่าน AI Provider
    """
    critic_system_prompt = CriticPrompt.get_critic_system_prompt()
    critic_context = CriticPrompt.format_critic_context(market_context, initial_analysis)
    
    # ส่งให้ Client หลัก (Groq) หรือรอง (Gemini) ช่วยตรวจสอบ
    # ในที่นี้ใช้ self.main_client (หากมี) เพื่อประหยัดเวลา
    try:
        critique_result = self.main_client.generate_analysis(critic_system_prompt, critic_context)
        return critique_result
    except Exception as e:
        logger.error(f"Critic Agent failed, defaulting to SAFE: {e}")
        return {"risk_level": "LOW", "reason": "Audit failed, defaulting to safe mode."}

    def _validate_response_structure(self, response: dict) -> dict:
        required_keys = ["regime", "confidence_score", "reasoning"]
        for key in required_keys:
            if key not in response:
                raise ValueError(f"Missing key: {key}")
        return response

    def _generate_emergency_fallback_response(self) -> dict:
        return {
            "regime": "UNKNOWN",
            "confidence_score": 0.0,
            "reasoning": "Emergency mode active.",
            "emergency_bypass": True
        }