import os
import json
from google import genai
from google.genai import types

class GeminiClient:
    """
    Client สำหรับเชื่อมต่อ Gemini API ทำหน้าที่เป็น Backup Provider
    และบังคับให้โมเดลตอบกลับเฉพาะรูปแบบ JSON เท่านั้น
    """
    def __init__(self):
        # โหลด API Key จาก Environment Variables
        self.api_key = os.getenv("GEMINI_API_KEY", "mock_key")
        if not self.api_key:
            raise ValueError("Missing GEMINI_API_KEY in environment variables.")
        
        # เริ่มต้น Client โดยใช้ google-genai SDK มาตรฐานปี 2026
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def generate_analysis(self, system_prompt: str, user_context: str) -> dict:
        """
        ส่งคำสั่งวิเคราะห์ไปยัง Gemini API และบังคับ Output เป็น JSON Object
        """
        try:
            # กำหนด Configuration เพื่อบังคับโครงสร้างข้อมูลเป็น JSON (Structured Output)
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,  # ใช้ค่าต่ำเพื่อให้ผลลัพธ์เป็น Deterministic มากที่สุด
                system_instruction=system_prompt
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_context,
                config=config
            )

            if not response.text:
                raise ValueError("Gemini API returned an empty response.")

            # แปลงข้อความ JSON String ให้เป็น Python Dictionary
            return json.loads(response.text)

        except Exception as e:
            # ส่งต่อ Error เพื่อให้ Router Service นำไปบริหารจัดการระบบ Failover
            raise RuntimeError(f"Gemini Client Error: {str(e)}")