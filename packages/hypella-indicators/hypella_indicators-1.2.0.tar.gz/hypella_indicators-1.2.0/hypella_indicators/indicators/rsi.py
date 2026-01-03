from typing import List, Dict, Union
import pandas as pd
import numpy as np
from hypella_indicators.core import Indicator, Candle

class RSI(Indicator):
    """
    Relative Strength Index (RSI).
    
    Arguments:
        period (int): Lookback period. Default: 14.
    """
    
    def __init__(self, period: int = 14):
        self.period = period
        self.alpha = 1.0 / period
        self._prev_close = None
        self._avg_gain = 0.0
        self._avg_loss = 0.0
        self._count = 0
        super().__init__(period=period)

    def reset(self):
        super().reset()
        self._prev_close = None
        self._avg_gain = 0.0
        self._avg_loss = 0.0
        self._count = 0

    def calculate_series(self, candles: List[Candle]) -> pd.Series:
        if len(candles) < self.period:
            return pd.Series([0.0] * len(candles))
            
        df = self.candles_to_df(candles)
        
        # Calculate price changes
        delta = df['close'].diff()
        
        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        
        # Calculate RS
        # Use Wilder's Smoothing (alpha = 1/N)
        # Note: adjust=False ensures the recursive calculation: 
        # y_t = (y_{t-1} * (N-1) + x_t) / N
        avg_gain = gain.ewm(com=self.period-1, min_periods=self.period, adjust=False).mean()
        avg_loss = loss.ewm(com=self.period-1, min_periods=self.period, adjust=False).mean()
        
        rs = avg_gain / avg_loss
        
        # Calculate RSI
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate(self, candles: List[Candle]) -> float:
        rsi = self.calculate_series(candles)
        if len(rsi) == 0:
            return 0.0
        val = rsi.iloc[-1]
        return 0.0 if pd.isna(val) else float(val)

    def update(self, candle: Candle) -> float:
        if self._prev_close is None:
            self._prev_close = candle.close
            self._count = 1
            self._value = 0.0
            return 0.0

        self._count += 1
        delta = candle.close - self._prev_close
        gain = max(delta, 0.0)
        loss = max(-delta, 0.0)

        if self._count == 2:
            # First delta, seed the averages
            self._avg_gain = gain
            self._avg_loss = loss
        else:
            # Wilder's Smoothing EMA
            self._avg_gain = (gain * self.alpha) + (self._avg_gain * (1.0 - self.alpha))
            self._avg_loss = (loss * self.alpha) + (self._avg_loss * (1.0 - self.alpha))

        self._prev_close = candle.close

        if self._count > self.period:
            if self._avg_loss == 0:
                self._value = 100.0
            else:
                rs = self._avg_gain / self._avg_loss
                self._value = 100.0 - (100.0 / (1.0 + rs))
            self._initialized = True
        else:
            self._value = 0.0

        return float(self._value)
