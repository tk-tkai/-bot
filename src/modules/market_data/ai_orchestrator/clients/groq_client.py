### 2. `src/modules/ai_orchestrator/clients/groq_client.py`

import os
import json
from typing import Dict, Any
# หมายเหตุ: ในระบบจริงจะใช้ไลบรารีอย่างเช่น `requests` หรือ `groq` SDK 
# ในที่นี้จะเขียนด้วยรูปแบบโครงสร้างมาตรฐานที่ใช้งานได้จริง
import requests
from src.core.config import settings

class GroqClient:
    """
    Client เชื่อมต่อ Groq API ความเร็วสูง สำหรับเป็น AI ตัวหลักของระบบ
    """
    def __init__(self):
        # โหลด API Key และชื่อ Model จากศูนย์กลางระบบ (core/config)
        self.api_key = os.getenv("GROQ_API_KEY", "mock_key")
        self.model_name = os.getenv("GROQ_MODEL_NAME", "llama3-70b-8192")
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def analyze(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        ส่งคำสั่งหา Groq และดึงผลลัพธ์กลับมาล้างค่าให้เป็น Dict
        """
        if self.api_key == "mock_key":
            raise ValueError("กรุณาตั้งค่า GROQ_API_KEY ในระบบก่อนใช้งาน")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            # เปิดโหมด JSON Object ป้องกัน AI ตอบนอกลู่นอกทาง
            "response_format": {"type": "json_object"},
            "temperature": 0.2 # ปรับค่าให้ต่ำเพื่อให้ AI ตอบอย่างมีเสถียรภาพและอิงสถิติคงเดิม
        }

        response = requests.post(self.url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        
        result_json = response.json()
        content_str = result_json["choices"][0]["message"]["content"]
        
        # แปลงข้อความ JSON String จาก AI ให้กลายเป็น Python Dictionary
        return json.loads(content_str)