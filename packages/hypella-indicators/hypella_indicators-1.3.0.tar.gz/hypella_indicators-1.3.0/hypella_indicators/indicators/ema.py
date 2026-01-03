from typing import List
import pandas as pd
from hypella_indicators.core import Indicator, CandleData

class EMA(Indicator):
    """
    Exponential Moving Average (EMA).
    
    Arguments:
        period (int): Lookback period. Default: 9.
    """
    
    def __init__(self, period: int = 9):
        self.period = period
        self.alpha = 2.0 / (period + 1.0)
        self._count = 0
        super().__init__(period=period)

    def reset(self):
        super().reset()
        self._count = 0

    def calculate_series(self, candles: List[CandleData]) -> pd.Series:
        if len(candles) < self.period:
            return pd.Series([0.0] * len(candles))
            
        df = self.candles_to_df(candles)
        return df['close'].ewm(span=self.period, adjust=False, min_periods=self.period).mean()

    def calculate(self, candles: List[CandleData]) -> float:
        series = self.calculate_series(candles)
        if len(series) == 0:
            return 0.0
        val = series.iloc[-1]
        return 0.0 if pd.isna(val) else float(val)

    def update(self, candle: CandleData) -> float:
        self._count += 1
        
        if self._value is None:
            self._value = candle.close
        else:
            self._value = (candle.close * self.alpha) + (self._value * (1.0 - self.alpha))
            
        if self._count >= self.period:
            self._initialized = True
            
        # Return 0.0 if not initialized to match current calculate() behavior
        return float(self._value) if self._initialized else 0.0
