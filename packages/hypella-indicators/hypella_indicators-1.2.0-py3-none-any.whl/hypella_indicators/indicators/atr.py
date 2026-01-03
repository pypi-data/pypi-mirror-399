from typing import List
import pandas as pd
import numpy as np
from hypella_indicators.core import Indicator, Candle

class ATR(Indicator):
    """
    Average True Range (ATR).
    
    Arguments:
        period (int): Lookback period. Default: 14.
    """
    
    def __init__(self, period: int = 14):
        self.period = period
        self.alpha = 1.0 / period
        self._prev_close = None
        self._count = 0
        super().__init__(period=period)

    def reset(self):
        super().reset()
        self._prev_close = None
        self._count = 0

    def calculate_series(self, candles: List[Candle]) -> pd.Series:
        if len(candles) < 2:
            return pd.Series([0.0] * len(candles))
            
        df = self.candles_to_df(candles)
        
        high = df['high']
        low = df['low']
        close_prev = df['close'].shift(1)
        
        tr1 = high - low
        tr2 = (high - close_prev).abs()
        tr3 = (low - close_prev).abs()
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Wilder's Smoothing
        atr = tr.ewm(com=self.period-1, min_periods=self.period, adjust=False).mean()
        
        return atr

    def calculate(self, candles: List[Candle]) -> float:
        series = self.calculate_series(candles)
        if len(series) == 0:
            return 0.0
        val = series.iloc[-1]
        return 0.0 if pd.isna(val) else float(val)

    def update(self, candle: Candle) -> float:
        if self._prev_close is None:
            self._prev_close = candle.close
            self._count = 1
            self._value = 0.0
            return 0.0

        self._count += 1
        
        # True Range
        tr1 = candle.high - candle.low
        tr2 = abs(candle.high - self._prev_close)
        tr3 = abs(candle.low - self._prev_close)
        tr = max(tr1, tr2, tr3)

        if self._count == 2:
            # First TR, seed the average
            self._value = tr
        else:
            # Wilder's Smoothing
            self._value = (tr * self.alpha) + (self._value * (1.0 - self.alpha))

        self._prev_close = candle.close

        if self._count > self.period:
            self._initialized = True
        else:
            # Return 0.0 if not enough data to match pandas min_periods behavior
            return 0.0

        return float(self._value)
