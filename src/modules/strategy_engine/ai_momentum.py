from src.modules.strategy_engine.base_strategy import BaseStrategy

class AIMomentumStrategy(BaseStrategy):
    """
    กลยุทธ์หลักที่ผสานพลังปัญญาประดิษฐ์ (AI Advisor) ร่วมกับสัญญาณทางเทคนิคัล
    """
    def __init__(self):
        super().__init__(name="AI_MOMENTUM_V1")

    def calculate_signal(self, market_context: dict, ai_analysis: dict) -> dict:
        """
        ประมวลผลสัญญาณเทรดโดยอิงจาก AI Confidence และ Technical Matrix
        """
        # ดึงข้อมูลตลาดล่าสุดจากคู่เหรียญหลัก (ตัวอย่างเช่น BTCUSDT ใน Timeframe 1h)
        # ข้อมูลถูกแปลงมาจากโมดูล Market Data (Step 2)
        tf_data = market_context.get("BTCUSDT", {}).get("1h", {})
        current_price = tf_data.get("current_price", 0.0)
        atr = tf_data.get("atr", 0.0)
        rsi = tf_data.get("rsi", 50.0)
        
        # ดึงผลวิเคราะห์จากสมอง AI (Step 3)
        ai_regime = ai_analysis.get("regime", "UNKNOWN")
        ai_confidence = ai_analysis.get("confidence_score", 0.0)
        ai_reason = ai_analysis.get("reasoning", "No AI analysis provided.")

        # ตรวจสอบเงื่อนไขฉุกเฉิน (Emergency Bypass จากโมดูล AI Router ที่เราเขียนไว้ก่อนหน้า)
        if ai_analysis.get("emergency_bypass", False) or ai_regime == "UNKNOWN_LIMIT_REACHED":
            # หาก AI ล่มหรือติดลิมิต ให้ส่งต่อไปยังกลยุทธ์ Fallback (คณิตศาสตร์เพียว) ทันที
            return self._generate_signal_package(
                action="HOLD",
                target_price=current_price,
                stop_loss=0.0,
                take_profit=0.0,
                reason="AI Limit Detected! Redirecting system traffic to Pure Technical Rules."
            )

        # ---- LOGIC การตัดสินใจร่วมกัน (AI + Technical) ----
        # เงื่อนไขฝั่งขาซื้อ (BUY): AI มองเป็นขาขึ้นสะสม + เทคนิคัลยืนยันว่าราคาไม่แพงเกินไป (RSI < 65)
        if ai_regime in ["BULLISH", "ACCUMULATION"] and ai_confidence >= 0.70:
            if rsi < 65.0:
                # คำนวณจุดตัดขาดทุนอัตโนมัติด้วยค่าความผันผวน ATR ป้องกัน Market Noise [cite: 42]
                stop_loss = current_price - (2 * atr) if atr > 0 else current_price * 0.95
                take_profit = current_price + (4 * atr) if atr > 0 else current_price * 1.10
                
                return self._generate_signal_package(
                    action="BUY",
                    target_price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    reason=f"AI Confirmed {ai_regime} ({ai_confidence*100}%). Technical RSI is healthy at {rsi:.1f}. {ai_reason}"
                )

        # เงื่อนไขฝั่งขาย/ปิดสถานะ (SELL): AI มองเป็นขาลงอันตราย หรือ ราคาเข้าเขตซื้อมากเกินไปเฉียบพลัน
        elif ai_regime in ["BEARISH", "DISTRIBUTION"] and ai_confidence >= 0.75:
            if rsi > 35.0:  # หากยังมี Position อยู่ ให้พิจารณาส่งสัญญาณขายออกเพื่อลดความเสี่ยง
                stop_loss = current_price + (2 * atr) if atr > 0 else current_price * 1.05
                take_profit = current_price - (4 * atr) if atr > 0 else current_price * 0.90
                
                return self._generate_signal_package(
                    action="SELL",
                    target_price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    reason=f"AI Warning {ai_regime} ({ai_confidence*100}%). Technical Alert. {ai_reason}"
                )

        # ไม่มีเงื่อนไขใดเข้าแก๊ป ให้ถือเงินสดนิ่งๆ เพื่อรักษาความปลอดภัยของทุน
        return self._generate_signal_package(
            action="HOLD",
            target_price=current_price,
            stop_loss=0.0,
            take_profit=0.0,
            reason="Market state does not meet high-confidence criteria. Waiting for clarity."
        )