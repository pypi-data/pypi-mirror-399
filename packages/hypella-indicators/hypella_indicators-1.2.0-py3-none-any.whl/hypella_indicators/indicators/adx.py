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
        self.period = period
        self.alpha = 1.0 / period
        self._prev_high = None
        self._prev_low = None
        self._prev_close = None
        self._tr_smooth = 0.0
        self._plus_dm_smooth = 0.0
        self._minus_dm_smooth = 0.0
        self._adx_smooth = 0.0
        self._count = 0
        super().__init__(period=period)

    def reset(self):
        super().reset()
        self._prev_high = None
        self._prev_low = None
        self._prev_close = None
        self._tr_smooth = 0.0
        self._plus_dm_smooth = 0.0
        self._minus_dm_smooth = 0.0
        self._adx_smooth = 0.0
        self._count = 0

    def calculate(self, candles: List[Candle]) -> Dict[str, float]:
        if len(candles) < self.period:
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

    def update(self, candle: Candle) -> Dict[str, float]:
        if self._prev_high is None:
            self._prev_high = candle.high
            self._prev_low = candle.low
            self._prev_close = candle.close
            self._count = 1
            self._value = {"adx": 0.0, "plus_di": 0.0, "minus_di": 0.0}
            return self._value

        self._count += 1
        
        # True Range
        tr1 = candle.high - candle.low
        tr2 = abs(candle.high - self._prev_close)
        tr3 = abs(candle.low - self._prev_close)
        tr = max(tr1, tr2, tr3)
        
        # Directional Movement
        up_move = candle.high - self._prev_high
        down_move = self._prev_low - candle.low
        
        plus_dm = up_move if up_move > down_move and up_move > 0 else 0.0
        minus_dm = down_move if down_move > up_move and down_move > 0 else 0.0

        if self._count == 2:
            self._tr_smooth = tr
            self._plus_dm_smooth = plus_dm
            self._minus_dm_smooth = minus_dm
        else:
            self._tr_smooth = (tr * self.alpha) + (self._tr_smooth * (1.0 - self.alpha))
            self._plus_dm_smooth = (plus_dm * self.alpha) + (self._plus_dm_smooth * (1.0 - self.alpha))
            self._minus_dm_smooth = (minus_dm * self.alpha) + (self._minus_dm_smooth * (1.0 - self.alpha))

        self._prev_high = candle.high
        self._prev_low = candle.low
        self._prev_close = candle.close

        plus_di = 0.0
        minus_di = 0.0
        dx = 0.0
        
        if self._tr_smooth != 0:
            plus_di = 100 * (self._plus_dm_smooth / self._tr_smooth)
            minus_di = 100 * (self._minus_dm_smooth / self._tr_smooth)
            
        sum_di = plus_di + minus_di
        if sum_di != 0:
            dx = 100 * abs(plus_di - minus_di) / sum_di

        if self._count == 2:
            self._adx_smooth = dx
        else:
            self._adx_smooth = (dx * self.alpha) + (self._adx_smooth * (1.0 - self.alpha))

        if self._count > self.period:
            # We need one more period for DX to start and another period for ADX smoothing
            # But to match pandas min_periods=period exactly, we check _count > period
            self._initialized = True
            self._value = {
                "adx": float(self._adx_smooth),
                "plus_di": float(plus_di),
                "minus_di": float(minus_di)
            }
        else:
            self._value = {"adx": 0.0, "plus_di": 0.0, "minus_di": 0.0}

        return self._value
