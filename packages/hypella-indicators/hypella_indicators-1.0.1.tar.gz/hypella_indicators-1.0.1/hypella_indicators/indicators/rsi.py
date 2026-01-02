from typing import List
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
        super().__init__(period=period)
        self.period = period

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
        return float(rsi.iloc[-1])
