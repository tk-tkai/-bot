import unittest
from unittest.mock import MagicMock, patch
from src.core.lifecycle_manager import SystemLifecycleManager

class TestSystemLifecycle(unittest.TestCase):
    def setUp(self):
        self.market_data = MagicMock()
        self.ai_router = MagicMock()
        self.risk_engine = MagicMock()
        self.executor = MagicMock()
        
        # ม็อคค่า config เริ่มต้น
        with patch('src.core.lifecycle_manager.Settings') as mock_settings:
            instance = mock_settings.return_value
            instance.GROQ_API_KEY = "mock-key"
            instance.GEMINI_API_KEY = "mock-key"
            self.lifecycle = SystemLifecycleManager(
                self.market_data, self.ai_router, self.risk_engine, self.executor
            )

    def test_startup_sequence_success(self):
        """เทส Happy Path: ทุกอย่างพร้อม ระบบต้องเปิดผ่าน"""
        self.risk_engine.validate_portfolio_health.return_value = True
        
        startup_result = self.lifecycle.execute_startup_sequence()
        
        self.assertTrue(startup_result)
        self.assertTrue(self.lifecycle.is_running)

    def test_startup_sequence_fail_by_risk(self):
        """เทสกรณี Risk Engine สั่งเบรกตอนเปิดเครื่อง บ็อทต้องไม่ยอมทำงาน"""
        self.risk_engine.validate_portfolio_health.return_value = False
        
        startup_result = self.lifecycle.execute_startup_sequence()
        
        self.assertFalse(startup_result)
        self.assertFalse(self.lifecycle.is_running)

    def test_shutdown_sequence_clean_exit(self):
        """เทสระบบปิดเครื่อง [007] ต้องจบลูปด้วย SystemExit โค้ด 0 เสมอ"""
        with self.assertRaises(SystemExit) as cm:
            self.lifecycle.execute_shutdown_sequence()
            
        self.assertEqual(cm.exception.code, 0)