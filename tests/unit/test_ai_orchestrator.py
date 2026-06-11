import unittest
from unittest.mock import MagicMock, patch
from src.modules.ai_orchestrator.router_service import AIRouterService

class TestAIOrchestrator(unittest.TestCase):
    def setUp(self):
        self.mock_market_context = {
            "BTCUSDT": {
                "1h": {"rsi": 35.5, "trend": "BEARISH"},
                "5m": {"rsi": 28.0, "trend": "SIDEWAYS"}
            }
        }
        
        # จำลองคำตอบมาตรฐานที่ผ่านเกณฑ์ตรวจสอบโครงสร้าง JSON
        self.valid_ai_response = {
            "regime": "ACCUMULATION",
            "confidence_score": 0.75,
            "reasoning": "Price near historical support zone with multi-timeframe RSI oversold indicators."
        }

    @patch('src.modules.ai_orchestrator.router_service.GroqClient')
    @patch('src.modules.ai_orchestrator.router_service.GeminiClient')
    def test_successful_primary_provider(self, mock_gemini_class, mock_groq_class):
        """
        ทดสอบกรณีที่ค่ายหลักทำงานได้ปกติ ระบบต้องรับและส่งค่าคืนกลับมาได้ทันที
        """
        mock_groq = MagicMock()
        mock_groq.generate_analysis.return_value = self.valid_ai_response
        mock_groq_class.return_value = mock_groq

        router = AIRouterService()
        result = router.get_market_analysis(self.mock_market_context)

        self.assertEqual(result["regime"], "ACCUMULATION")
        self.assertEqual(result["confidence_score"], 0.75)
        mock_groq.generate_analysis.assert_called_once()

    @patch('src.modules.ai_orchestrator.router_service.GroqClient')
    @patch('src.modules.ai_orchestrator.router_service.GeminiClient')
    def test_automatic_failover_to_secondary_provider(self, mock_gemini_class, mock_groq_class):
        """
        ทดสอบกรณีค่ายหลักล่มหรือติด Limit ระบบต้องสลับไปเรียกใช้ค่ายสำรอง (Gemini) อัตโนมัติ
        """
        mock_groq = MagicMock()
        mock_groq.generate_analysis.side_effect = RuntimeError("Rate Limit Reached")
        mock_groq_class.return_value = mock_groq

        mock_gemini = MagicMock()
        mock_gemini.generate_analysis.return_value = self.valid_ai_response
        mock_gemini_class.return_value = mock_gemini

        router = AIRouterService()
        result = router.get_market_analysis(self.mock_market_context)

        # ผลลัพธ์ต้องยังใช้งานได้ แต่ถูกประมวลผลผ่านค่ายสำรองแทน
        self.assertEqual(result["regime"], "ACCUMULATION")
        mock_groq.generate_analysis.assert_called_once()
        mock_gemini.generate_analysis.assert_called_once()

    @patch('src.modules.ai_orchestrator.router_service.GroqClient')
    @patch('src.modules.ai_orchestrator.router_service.GeminiClient')
    def test_all_providers_failed_emergency_fallback(self, mock_gemini_class, mock_groq_class):
        """
        ทดสอบกรณีเลวร้ายที่สุด (All AI Providers Failed) 
        ระบบต้องไม่ Crash แต่ต้องคืนค่าโครงสร้างฉุกเฉินเพื่อส่งต่อไปคำนวณต่อด้วย Pure Technical Strategy
        """
        mock_groq = MagicMock()
        mock_groq.generate_analysis.side_effect = RuntimeError("Network Error")
        mock_groq_class.return_value = mock_groq

        mock_gemini = MagicMock()
        mock_gemini.generate_analysis.side_effect = RuntimeError("API Key Expired")
        mock_gemini_class.return_value = mock_gemini

        router = AIRouterService()
        result = router.get_market_analysis(self.mock_market_context)

        self.assertTrue(result["emergency_bypass"])
        self.assertEqual(result["regime"], "UNKNOWN_LIMIT_REACHED")
        self.assertEqual(result["confidence_score"], 0.0)

if __name__ == '__main__':
    unittest.main()