import os
import logging
import time
from src.modules.market_data.indicator_engine import IndicatorEngine
from src.modules.ai_orchestrator.router_service import AIRouterService
from src.modules.risk_management.risk_engine import RiskEngine
from src.modules.risk_management.order_validator import OrderValidator
from src.modules.order_executor.exchange_client import ExchangeClient
from src.modules.order_executor.position_tracker import PositionTracker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')
logger = logging.getLogger("TradingBotMain")

class TradingBotCore:
    def __init__(self):
        self.indicator_engine = IndicatorEngine()
        self.ai_orchestrator = AIRouterService()
        self.risk_engine = RiskEngine()
        self.order_validator = OrderValidator(min_notional=10.0, max_notional=500.0)
        self.exchange_client = ExchangeClient()
        self.position_tracker = PositionTracker()
        # สถานะโพสิชั่นจำลอง (ในระบบจริงต้องดึงจาก Database/API)
        self.active_position = {} 

    def run_pipeline_cycle(self, symbol: str, timeframe: str, mock_market_data: dict, account_metrics: dict, total_drawdown: float):
        logger.info(f"🔄 === Starting New Trading Cycle for {symbol} ({timeframe}) ===")

        # STAGE 1: ตรวจสอบสุขภาพพอร์ต
        current_balance = account_metrics.get("balance", 0.0)
        if not self.risk_engine.validate_portfolio_health(current_balance, total_drawdown):
            logger.warning("Cycle Aborted: Portfolio health check failed.")
            return

        candles = mock_market_data.get(symbol, {}).get(timeframe, [])
        market_context = self.indicator_engine.calculate_indicators_snapshot(candles, fib_lookback=20)
        current_price = market_context["current_price"]

        # ตรวจสอบ Position ค้าง โดยใช้ฟังก์ชัน check_position_status ที่พี่เขียนไว้
        if self.active_position:
            status = self.position_tracker.check_position_status(self.active_position, current_price)
            if status["action"] == "MARKET_CLOSE":
                self.exchange_client.execute_market_order(
                    symbol=self.active_position["symbol"],
                    side="SELL" if self.active_position["direction"] == "LONG" else "BUY",
                    quantity=self.active_position["size"]
                )
                logger.info(f"🛑 [AUTO CLOSE] {status['reason']}")
                self.active_position = {} # ล้างโพสิชั่นเมื่อปิดสัญญา
            else:
                logger.info(f"📋 {status['reason']}")
            return 

        # STAGE 2 & 3: วิเคราะห์ตลาดโดย AI
        ai_analysis = self.ai_orchestrator.analyze_market(market_context)
        
        # ใส่ลอจิกการตัดสินใจเพิ่ม
        if ai_analysis and ai_analysis.get("confidence_score", 0) > 0.8:
            action = "BUY" if ai_analysis["regime"] == "BULLISH" else "SELL"
            
            # 1. เตรียม Order Proposal
            proposal = {
                "symbol": symbol, "side": action, "quantity": 0.001, 
                "price": current_price, "stop_loss": current_price * 0.98
            }
            
            # 2. ตรวจสอบความถูกต้อง (Validator)
            if self.order_validator.validate_order_spec(proposal):
                # 3. ยิงคำสั่ง (Executor)
                order = self.exchange_client.execute_market_order(symbol, action, proposal["quantity"])
                self.active_position = {"symbol": symbol, "entry_price": current_price, "size": proposal["quantity"], "direction": action}
                logger.info(f"✅ [ORDER SUCCESS] {action} {symbol} at {current_price}")

if __name__ == "__main__":
    logger.info("🚀 [SYSTEM START] Initializing...")
    mock_market_data = {"BTCUSDT": {"1h": [{"open": 64000, "high": 64500, "low": 63900, "close": 64200, "volume": 150}] * 30}}
    mock_account_metrics = {"balance": 10000.0}
    
    bot = TradingBotCore()
    # จำลองว่ามีโพสิชั่นค้างอยู่เพื่อให้ระบบทดสอบการเช็ค PnL
    bot.active_position = {"symbol": "BTCUSDT", "entry_price": 64000.0, "size": 0.001, "direction": "LONG"}

    try:
        while True:
            bot.run_pipeline_cycle("BTCUSDT", "1h", mock_market_data, mock_account_metrics, 0.02)
            time.sleep(3)
    except KeyboardInterrupt:
        logger.info("🛑 [SHUTDOWN] Bot stopped safely.")

