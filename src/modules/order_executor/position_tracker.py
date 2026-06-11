class PositionTracker:
    def __init__(self, risk_per_trade_pct: float = 1.0):
        """
        ระบบจัดการหน้าตักและคำนวณขนาดไม้ (Position Sizing Tracker)
        :param risk_per_trade_pct: เปอร์เซ็นต์ความเสี่ยงของพอร์ตที่ยอมให้เสียได้ต่อไม้ (Default: 1%)
        """
        self.risk_per_trade_pct = risk_per_trade_pct
        self.open_positions = {}

    def calculate_dynamic_size(self, balance: float, entry_price: float, stop_loss: float) -> float:
        """
        คำนวณขนาดไม้ (Quantity) ตามระยะ Stop Loss เพื่อคุมความเสี่ยงให้อยู่ในกฎเหล็กเป๊ะๆ
        สูตร: Quantity = (Balance * Risk%) / (Entry Price - Stop Loss)
        """
        risk_amount = balance * (self.risk_per_trade_pct / 100.0)
        stop_distance = abs(entry_price - stop_loss)
        
        if stop_distance == 0:
            return 0.0
            
        raw_qty = risk_amount / stop_distance
        return round(raw_qty, 4)  # ปัดทศนิยม 4 ตำแหน่งมาตรฐานคริปโต

    def update_position_status(self, symbol: str, qty: float, side: str):
        if qty == 0:
            self.open_positions.pop(symbol, None)
        else:
            self.open_positions[symbol] = {"quantity": qty, "side": side}