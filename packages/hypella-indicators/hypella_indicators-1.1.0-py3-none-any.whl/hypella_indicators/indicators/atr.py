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
        super().__init__(period=period)
        self.period = period

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
