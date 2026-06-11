import os
import json
from typing import Dict, Any
import requests
from src.core.config import settings

class GroqClient:
    """
    Client เชื่อมต่อ Groq API ความเร็วสูง สำหรับเป็น AI ตัวหลักของระบบ
    """
    def __init__(self):
        # โหลด API Key ตัวจริงตรงจากในเครื่องพี่อรรถพล
        self.api_key = os.getenv("GROQ_API_KEY", "mock_key")
        self.model_name = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def analyze(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        ส่งคำสั่งหา Groq และดึงผลลัพธ์กลับมาล้างค่าให้เป็น Dict
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # กฎเหล็กของ Groq: เมื่อเปิดโหมด json_object ต้องบังคับคำว่า JSON ลงในระบบ Prompt เสมอเพื่อจูนอินเตอร์เฟส
        strict_system_prompt = f"{system_prompt}\n\nYou must output the response as a valid, well-formed JSON object matching the requested schema contract."

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": strict_system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            # เปิดโหมด JSON Object คุมโครงสร้างกุนซือ
            "response_format": {"type": "json_object"},
            "temperature": 0.1 
        }

        response = requests.post(self.url, headers=headers, json=payload, timeout=10)
        
        # ถ้าระบบปลายทางดีดปัญหา (เช่น คีย์หมดอายุ, คีย์ผิด หรือบ่นเรื่องโครงสร้างข้อมูล) 
        # ตัวนี้จะดักกวาดข้อความอธิบายดิบๆ จากเซิร์ฟเวอร์ Groq ออกมาพ่นบน Terminal ทันที ไม่ปล่อยให้ตาบอดครับ
        if response.status_code != 200:
            raise RuntimeError(f"Groq API Error {response.status_code}: {response.text}")
        
        result_json = response.json()
        content_str = result_json["choices"][0]["message"]["content"]
        
        # แปลงข้อความ JSON String จาก AI ให้กลายเป็น Python Dictionary
        return json.loads(content_str)
    
    def generate_analysis(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        สร้าง Alias ฟังก์ชันเพื่อรองรับการเรียกใช้จาก AIRouterService (ระบบสลับสายหลัก)
        """
        return self.analyze(system_prompt, user_prompt)