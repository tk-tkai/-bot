import pytest
from typing import Dict, Any, List
from src.modules.market_data.indicator_engine import IndicatorEngine
from src.modules.market_data.indicators.trend import TrendIndicator
from src.modules.market_data.indicators.momentum import MomentumIndicator

# 1. สร้าง Fixture จำลองข้อมูลแท่งเทียนดิบ (Mock Candle Data) สำหรับใช้ทดสอบ
@pytest.fixture
def mock_candle_history() -> List[Dict[str, Any]]:
    """
    สร้างข้อมูลแท่งเทียนจำลองจำนวน 40 แท่ง (เพียงพอสำหรับทดสอบ Lookback 14 และ 26 แท่ง)
    โดยกำหนดราคาให้มีลักษณะเป็นเทรนด์ขาขึ้นชัดเจน เพื่อทดสอบเงื่อนไขอินดิเคเตอร์
    """
    candles = []
    base_price = 65000.0
    for i in range(40):
        # จำลองราคาขยับขึ้นแท่งละ 100 ดอลลาร์
        price = base_price + (i * 100)
        candles.append({
            "symbol": "BTCUSDT",
            "timeframe": "1h",
            "timestamp": 1700000000 + (i * 3600),
            "open": price - 50,
            "high": price + 150,
            "low": price - 100,
            "close": price,
            "volume": 1000.0
        })
    return candles

# 2. ทำการทดสอบระบบโมเมนตัม (RSI Test)
def test_momentum_indicator_rsi(mock_candle_history):
    rsi_calc = MomentumIndicator()
    result = rsi_calc.calculate(mock_candle_history, period=14)
    
    assert "rsi" in result
    assert "status" in result
    assert isinstance(result["rsi"], float)
    # เนื่องจากราคาจำลองขยับขึ้นต่อเนื่อง ค่า RSI ควรจะอยู่ในโซนสูง (Overbought)
    assert result["rsi"] > 50

# 3. ทำการทดสอบกฎเหล็ก Deterministic Replay (สำคัญที่สุดตามพิมพ์เขียว)
def test_indicator_engine_deterministic_replay(mock_candle_history):
    """
    กฎเหล็ก: ป้อนข้อมูลดิบชุดเดิมเข้าเอนจิน ผลลัพธ์อินดิเคเตอร์ต้องเหมือนเดิม 100%
    ไม่มีการเปลี่ยนแปลงจากผลกระทบข้างเคียง (No Hidden Side Effects)
    """
    engine = IndicatorEngine()
    
    # รันครั้งที่ 1
    snapshot_1 = engine.calculate_indicators_snapshot(mock_candle_history, fib_lookback=20)
    
    # รันครั้งที่ 2 (จำลองสถานการณ์ระบบรีสตาร์ทแล้วดึงข้อมูลก้อนเดิมมาคำนวณใหม่)
    snapshot_2 = engine.calculate_indicators_snapshot(mock_candle_history, fib_lookback=20)
    
    # ตรวจสอบโครงสร้างและความถูกต้องของข้อมูล
    assert snapshot_1["current_price"] == snapshot_2["current_price"]
    assert snapshot_1["fibonacci_retracement"]["swing_high"] == snapshot_2["fibonacci_retracement"]["swing_high"]
    assert snapshot_1["support_resistance"]["pivot_point"] == snapshot_2["support_resistance"]["pivot_point"]
    
    # เปรียบเทียบผลลัพธ์ทั้งหมดดิบๆ ต้องเท่ากันทุกทศนิยม 100%
    assert snapshot_1 == snapshot_2