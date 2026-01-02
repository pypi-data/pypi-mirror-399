from typing import List, Dict, Union
import pandas as pd
import numpy as np
from hypella_indicators.core import Indicator, Candle

class ADX(Indicator):
    """
    Average Directional Index (ADX).
    
    Arguments:
        period (int): Lookback period. Default: 14.
    """
    
    def __init__(self, period: int = 14):
        super().__init__(period=period)
        self.period = period

    def calculate(self, candles: List[Candle]) -> Dict[str, float]:
        if len(candles) < self.period * 2: # ADX needs more data for smoothing stabilizes
             return {"adx": 0.0, "plus_di": 0.0, "minus_di": 0.0}
            
        df = self.candles_to_df(candles)
        
        high = df['high']
        low = df['low']
        close_prev = df['close'].shift(1)
        high_prev = high.shift(1)
        low_prev = low.shift(1)
        
        # True Range
        tr = pd.concat([
            high - low,
            (high - close_prev).abs(),
            (low - close_prev).abs()
        ], axis=1).max(axis=1)
        
        # Directional Movement
        up_move = high - high_prev
        down_move = low_prev - low
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
        
        # Smoothed values using Wilder's
        tr_smooth = pd.Series(tr).ewm(com=self.period-1, min_periods=self.period, adjust=False).mean()
        plus_dm_smooth = pd.Series(plus_dm).ewm(com=self.period-1, min_periods=self.period, adjust=False).mean()
        minus_dm_smooth = pd.Series(minus_dm).ewm(com=self.period-1, min_periods=self.period, adjust=False).mean()
        
        # DI+ and DI-
        plus_di = 100 * (plus_dm_smooth / tr_smooth)
        minus_di = 100 * (minus_dm_smooth / tr_smooth)
        
        # DX
        sum_di = plus_di + minus_di
        # Handle division by zero
        dx = 100 * (plus_di - minus_di).abs() / sum_di.replace(0, np.nan)
        dx = dx.fillna(0)
        
        # ADX
        adx = dx.ewm(com=self.period-1, min_periods=self.period, adjust=False).mean()
        
        last_adx = adx.iloc[-1]
        last_plus_di = plus_di.iloc[-1]
        last_minus_di = minus_di.iloc[-1]
        
        return {
            "adx": 0.0 if pd.isna(last_adx) else float(last_adx),
            "plus_di": 0.0 if pd.isna(last_plus_di) else float(last_plus_di),
            "minus_di": 0.0 if pd.isna(last_minus_di) else float(last_minus_di)
        }
