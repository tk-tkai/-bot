from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseIndicator(ABC):
    """
    Abstract Base Class สำหรับควบคุมมาตรฐานของ Indicator ทุกตัวในระบบ
    ตามหลักการ Read-Only และ Deterministic Replay
    """
    
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def calculate(self, data: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        ฟังก์ชันหลักในการคำนวณอินดิเคเตอร์
        :param data: รายการแท่งเทียนย้อนหลัง (List of Candle Dictsที่มีโครงสร้าง open, high, low, close, volume)
        :return: ผลลัพธ์การคำนวณในรูปแบบ Structured Dict ที่พร้อมแปลงเป็น JSON
        """
        pass