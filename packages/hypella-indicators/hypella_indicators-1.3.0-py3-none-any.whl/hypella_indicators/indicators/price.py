from typing import List
from hypella_indicators.core import Indicator, CandleData

class Price(Indicator):
    """
    Live price indicator. Represents the latest price of the current (open) candle.
    """
    
    def __init__(self):
        super().__init__()

    def calculate(self, candles: List[CandleData]) -> float:
        """
        You should pass the latest open candle only to make sure you get the live price.
        """
        if not candles:
            return 0.0
        return float(candles[-1].close)

    def update(self, candle: CandleData) -> float:
        """
        You should pass the latest open candle only to make sure you get the live price.
        """
        self._value = float(candle.close)
        self._initialized = True
        return self._value
