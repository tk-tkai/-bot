import os
import logging
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')

if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                # ดึงค่าฝังเข้า Environment Variables ของ Windows ชั่วคราวในระดับ Memory
                os.environ[key.strip()] = value.strip()
else:
    logging.warning("⚠️ ไม่พบไฟล์ .env ระบบจะใช้ค่า Default ในเครื่อง")
import time
from src.modules.market_data.indicator_engine import IndicatorEngine
from src.modules.ai_orchestrator.router_service import AIRouterService
from src.modules.risk_management.risk_engine import RiskEngine
from src.modules.risk_management.order_validator import OrderValidator
from src.modules.order_executor.exchange_client import ExchangeClient
from src.modules.order_executor.position_tracker import PositionTracker

# ตั้งค่าระบบ Log ให้เห็นการทำงานของบ็อทในแต่ละสเต็ปอย่างละเอียด
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'
)
logger = logging.getLogger("TradingBotMain")

class TradingBotCore:
    def __init__(self):
        logger.info("Initializing Institutional Trading Bot Core...")
        
        # ประกอบร่างโมดูลทั้ง 5 ส่วนตามพิมพ์เขียว
        self.indicator_engine = IndicatorEngine()
        self.ai_orchestrator = AIRouterService()
        self.risk_engine = RiskEngine(max_daily_loss_pct=16.67, max_drawdown_pct=20.0)
        self.order_validator = OrderValidator(min_notional=10.0, max_notional=500.0)
        self.exchange_client = ExchangeClient()
        self.position_tracker = PositionTracker(risk_per_trade_pct=1.67) # ความเสี่ยง 1% ต่อไม้

    def run_pipeline_cycle(self, symbol: str, timeframe: str, mock_market_data: dict, account_metrics: dict):
        """
        ท่อส่งข้อมูลการทำงานจริง (Runtime Pipeline Step 6 - 9)
        """
        logger.info(f"=== Starting New Trading Cycle for {symbol} ({timeframe}) ===")

        # STAGE 1: ตรวจสอบสุขภาพพอร์ตรวมก่อน (Risk Engine Check)
        if not self.risk_engine.check_portfolio_health(account_metrics):
            logger.warning("Cycle Aborted: Portfolio health check failed. Lockout active.")
            return

        # STAGE 2: คำนวณอินดิเคเตอร์ทางเทคนิคัล (Deterministic Calculation)
        logger.info("Stage 2: Calculating technical indicators...")
        # ดึงข้อมูลแท่งเทียนจำลองจากประวัติ
        candles = mock_market_data.get(symbol, {}).get(timeframe, [])
        if not candles:
            logger.error("Cycle Aborted: No historical candle data found.")
            return
            
        market_context = self.indicator_engine.calculate_indicators_snapshot(candles, fib_lookback=20)
        current_price = market_context["current_price"]

        # STAGE 3: ส่งข้อมูลให้ AI Orchestrator วิเคราะห์สภาวะตลาด
        logger.info("Stage 3: Fetching AI Orchestrator analysis...")
        ai_analysis = self.ai_orchestrator.analyze_market(market_context)
        
        if not ai_analysis or "regime" not in ai_analysis:
            logger.error("Cycle Aborted: AI Analysis returned invalid or empty data.")
            return

        regime = ai_analysis.get("regime")
        confidence = ai_analysis.get("confidence_score", 0.0)
        reasoning = ai_analysis.get("reasoning", "")
        logger.info(f"AI Decision: [{regime}] (Confidence: {confidence:.2f}) - {reasoning}")

        # STAGE 4: แปลงบทวิเคราะห์เป็นแผนการเทรด (Trade Proposal Formulation)
        if regime == "BULLISH" and confidence >= 0.70:
            side = "BUY"
            # ตั้ง Stop Loss ไว้ที่แนวรับสำคัญ Fibonacci Level ด้านล่าง (สมมติลบออก $1,000 จากราคาปัจจุบัน)
            stop_loss = current_price - 1000.0
        elif regime == "BEARISH" and confidence >= 0.70:
            side = "SELL"
            # ตั้ง Stop Loss ไว้ที่แนวต้านสำคัญด้านบน
            stop_loss = current_price + 1000.0
        else:
            logger.info("Decision: STAY FLAT (Signal strength or confidence insufficient).")
            return

        # STAGE 5: คำนวณขนาดไม้ตามความเสี่ยง (Dynamic Position Sizing)
        quantity = self.position_tracker.calculate_dynamic_size(
            balance=account_metrics["current_equity"],
            entry_price=current_price,
            stop_loss=stop_loss
        )

        order_proposal = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": current_price,
            "stop_loss": stop_loss
        }

        # STAGE 6: ส่งให้ Order Validator ตรวจกฎเหล็กความปลอดภัยสุดท้ายก่อนยิงออก
        if not self.order_validator.validate_order_spec(order_proposal):
            logger.warning("Order Rejected: Blocked by Order Validator Rules.")
            return

        # STAGE 7: ยิงคำสั่งเข้า Exchange จริง (Atomic Execution)
        order_receipt = self.exchange_client.execute_market_order(symbol, side, quantity)
        
        if order_receipt.get("status") == "FILLED":
            self.position_tracker.update_position_status(symbol, quantity, side)
            logger.info(f"🏆 Successfully executed trade! Position tracked for {symbol}.")
        
        # ล้างรอยนิ้วมือป้องกันการบล็อกออเดอร์ในลูปถัดไป
        self.order_validator.clear_order_fingerprint(order_proposal)


if __name__ == "__main__":
    # จำลองข้อมูลที่ได้มาจากระบบดึงราคา (Market Data) จังหวะราคาขาขึ้นชัดเจน
    mock_candles = []
    base_price = 65000.0
    for i in range(40):
        price = base_price + (i * 100)
        mock_candles.append({
            "symbol": "BTCUSDT", "timeframe": "1h", "timestamp": 1700000000 + (i * 3600),
            "open": price - 50, "high": price + 150, "low": price - 100, "close": price, "volume": 1000.0
        })
    
    mock_market_data = {"BTCUSDT": {"1h": mock_candles}}

    # จำลองสถานะบัญชีเงินทุนปัจจุบัน (Account Metrics)
    mock_account_metrics = {
        "initial_balance": 60.0,
        "current_equity": 60.0,
        "daily_realized_pnl": 0.0,
        "peak_equity": 60.0
    }

    # สั่งเปิดบ็อททำงานรันลูปจำลอง
    bot = TradingBotCore()
    bot.run_pipeline_cycle(
        symbol="BTCUSDT",
        timeframe="1h",
        mock_market_data=mock_market_data,
        account_metrics=mock_account_metrics
    )