from typing import List
from hypella_indicators.core import Indicator, CandleData

class Candle(Indicator):
    """
    An indicator to provide raw candle fields (close, open, high, low, volume)
    from closed candles.
    
    Arguments:
        field (str): The candle field to return ('close', 'open', 'high', 'low', 'volume').
    """
    
    def __init__(self, field: str = "close"):
        super().__init__(field=field)
        self.field = field

    def calculate(self, candles: List[CandleData]) -> float:
        if not candles:
            return 0.0
        return float(getattr(candles[-1], self.field))

    def update(self, candle: CandleData) -> float:
        self._value = float(getattr(candle, self.field))
        self._initialized = True
        return self._value
