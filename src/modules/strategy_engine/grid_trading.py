from src.modules.strategy_engine.base_strategy import BaseStrategy

class GridTradingFallbackStrategy(BaseStrategy):
    """
    กลยุทธ์สำรองฉุกเฉิน (Pure Technical Fallback) 
    ทำงานเมื่อ AI ล่ม เพื่อทำหน้าที่เคลียร์ออเดอร์ค้าง หรือแก้พอร์ตตามแนวรับ-แนวต้านหลัก
    """
    def __init__(self):
        super().__init__(name="PURE_TECH_GRID_FALLBACK")

    def calculate_signal(self, market_context: dict, ai_analysis: dict = None) -> dict:
        """
        คำนวณสัญญาณโดยใช้แนวรับ-แนวต้าน (Pivot Points/Fibonacci) จากโมดูลที่ 1 เพียวๆ 
        """
        tf_data = market_context.get("BTCUSDT", {}).get("1h", {})
        current_price = tf_data.get("current_price", 0.0)
        rsi = tf_data.get("rsi", 50.0)
        
        # ดึงราคาแนวรับแนวต้านคงที่จาก Pivot Points & Fibonacci Engine [cite: 17, 29]
        support_level = tf_data.get("support_1", current_price * 0.98)
        resistance_level = tf_data.get("resistance_1", current_price * 1.02)

        # กลไกเอาตัวรอดฉุกเฉินเชิงคณิตศาสตร์ (Hard-coded Safety Rules) 
        # กฎที่ 1: ถ้าราคาดิ่งหลุดแนวรับหลัก + RSI บ่งบอกว่าเทขายหนักเกินไป (Oversold) -> สั่งซื้อตั้งรับสวนกลับ
        if current_price <= support_level and rsi <= 30.0:
            return self._generate_signal_package(
                action="BUY",
                target_price=current_price,
                stop_loss=support_level * 0.95,
                take_profit=resistance_level,
                reason="FALLBACK ACTIVE: Price hit Support Level with Technical Oversold condition. AI Bypassed."
            )

        # กฎที่ 2: ถ้าราคาชนแนวต้านสำคัญเพื่อเคลียร์กำไร หรือ RSI Overbought -> สั่งขายทำกำไร/ตัดลดความเสี่ยงออกทันที 
        elif current_price >= resistance_level or rsi >= 70.0:
            return self._generate_signal_package(
                action="SELL",
                target_price=current_price,
                stop_loss=resistance_level * 1.05,
                take_profit=support_level,
                reason="FALLBACK ACTIVE: Price hit Resistance Level or Technical Overbought. Executing Safety Liquidate."
            )

        # นอกนั้นให้รักษาสภาพคล่อง นั่งนิ่งๆ
        return self._generate_signal_package(
            action="HOLD",
            target_price=current_price,
            stop_loss=0.0,
            take_profit=0.0,
            reason="FALLBACK ACTIVE: Pure Technical monitoring. No actionable grid boundary triggered."
        )