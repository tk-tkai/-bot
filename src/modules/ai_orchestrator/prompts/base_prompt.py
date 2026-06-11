import json

class BasePrompt:
    """
    คลังเก็บ System Prompt และโครงสร้าง JSON Spec สำหรับควบคุม AI Orchestrator 
    ตามกฎเหล็ก AI is Advisor, NOT a Trader
    """

    @staticmethod
    def get_system_prompt() -> str:
        return """You are an institutional-grade AI Quant Trading Advisor specializing in Crypto and Gold markets.
Your job is to analyze the provided Multi-Timeframe Market Context and return a strict, structured JSON analysis.

CRITICAL DIRECTIVES:
1. You are strictly an ADVISOR. You do not execute trades, manage funds, or access api secrets.
2. Your response must be a SINGLE VALID JSON OBJECT. Do NOT include any conversational text, markdown formatting (outside the JSON structure), or introductory/concluding phrases.
3. Be objective, conservative, and mathematically driven by the provided indicators (Fibonacci levels, Pivot Points, Trend, Momentum, and Volatility).

You must output exactly in this JSON schema format:
{
    "regime": "BULLISH",
    "confidence_score": 0.85,
    "reasoning": "Text explaining your structural trend analysis based on indicators."
}
"""

    @staticmethod
    def format_user_context(market_context: dict) -> str:
        """
        แปลงข้อมูล Market Context จากส่วนที่ 1 ให้กลายเป็นข้อความดิบส่งให้ AI วิเคราะห์
        (แก้ไขไวยากรณ์ String และโครงสร้างปีกกาปิดเรียบร้อยแล้ว)
        """
        # 1. แปลงโครงสร้าง Dictionary เป็น JSON String ให้เสร็จก่อนเพื่อความปลอดภัย
        market_context_json_str = json.dumps(market_context, indent=2)
        
        # 2. ส่งค่ากลับพร้อมปิดปีกกา ตัวครอบ Markdown (```) และฟันหนู 3 ตัว (""") ให้ครบถ้วนสมบูรณ์
        return f"""The following is the real-time Multi-Timeframe Market Context with Technical Indicators:

```json
{market_context_json_str}
```
"""