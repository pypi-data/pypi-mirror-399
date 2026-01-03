from typing import List
import pandas as pd
from collections import deque
from hypella_indicators.core import Indicator, CandleData

class SMA(Indicator):
    """
    Simple Moving Average (SMA).
    
    Arguments:
        period (int): Lookback period. Default: 9.
    """
    
    def __init__(self, period: int = 9):
        self.period = period
        self._history = deque(maxlen=period)
        super().__init__(period=period)

    def reset(self):
        super().reset()
        self._history = deque(maxlen=self.period)

    def calculate_series(self, candles: List[CandleData]) -> pd.Series:
        if len(candles) < self.period:
            return pd.Series([0.0] * len(candles))
            
        df = self.candles_to_df(candles)
        return df['close'].rolling(window=self.period, min_periods=self.period).mean()

    def calculate(self, candles: List[CandleData]) -> float:
        series = self.calculate_series(candles)
        if len(series) == 0:
            return 0.0
        val = series.iloc[-1]
        return 0.0 if pd.isna(val) else float(val)

    def update(self, candle: CandleData) -> float:
        self._history.append(candle.close)
        
        if len(self._history) < self.period:
            self._value = 0.0
        else:
            self._value = sum(self._history) / self.period
            self._initialized = True
            
        return self._value
