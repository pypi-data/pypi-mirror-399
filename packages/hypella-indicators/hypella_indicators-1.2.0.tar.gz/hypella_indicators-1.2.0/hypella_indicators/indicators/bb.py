from typing import List, Dict, Union
import pandas as pd
import math
from collections import deque
from hypella_indicators.core import Indicator, Candle

class BollingerBands(Indicator):
    """
    Bollinger Bands (BB).
    
    Arguments:
        period (int): Lookback period. Default: 20.
        std_dev (float): Standard deviation multiplier. Default: 2.0.
    """
    
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        self.period = period
        self.std_dev = std_dev
        self._history = deque(maxlen=period)
        super().__init__(period=period, std_dev=std_dev)

    def reset(self):
        super().reset()
        self._history = deque(maxlen=self.period)

    def calculate(self, candles: List[Candle]) -> Dict[str, float]:
        if len(candles) < self.period:
            return {
                "upper": 0.0,
                "middle": 0.0,
                "lower": 0.0,
                "percent_b": 0.0
            }
            
        df = self.candles_to_df(candles)
        
        # Calculate Middle Band (SMA)
        middle = df['close'].rolling(window=self.period, min_periods=self.period).mean()
        
        # Calculate Standard Deviation (Population, ddof=0)
        # Note: pandas uses ddof=1 by default, but typically indicators use population std
        std = df['close'].rolling(window=self.period, min_periods=self.period).std(ddof=0)
        
        # Calculate Bands
        upper = middle + (std * self.std_dev)
        lower = middle - (std * self.std_dev)
        
        # Get latest values
        last_middle = middle.iloc[-1]
        last_upper = upper.iloc[-1]
        last_lower = lower.iloc[-1]
        last_close = df['close'].iloc[-1]
        
        # Handle NaN if series is valid length but started with NaN
        if pd.isna(last_middle):
            return {"upper": 0.0, "middle": 0.0, "lower": 0.0, "percent_b": 0.0}
            
        # Calculate %B
        bandwidth = last_upper - last_lower
        if bandwidth == 0:
            percent_b = 0.5 # Center it if bandwidth is zero
        else:
            percent_b = (last_close - last_lower) / bandwidth

        return {
            "upper": float(last_upper),
            "middle": float(last_middle),
            "lower": float(last_lower),
            "percent_b": float(percent_b)
        }

    def update(self, candle: Candle) -> Dict[str, float]:
        self._history.append(candle.close)
        
        if len(self._history) < self.period:
            self._value = {
                "upper": 0.0,
                "middle": 0.0,
                "lower": 0.0,
                "percent_b": 0.0
            }
            return self._value

        self._initialized = True
        
        # Calculate Mean
        mean = sum(self._history) / self.period
        
        # Calculate Population Standard Deviation
        variance = sum((x - mean) ** 2 for x in self._history) / self.period
        std = math.sqrt(variance)
        
        upper = mean + (std * self.std_dev)
        lower = mean - (std * self.std_dev)
        
        bandwidth = upper - lower
        if bandwidth == 0:
            percent_b = 0.5
        else:
            percent_b = (candle.close - lower) / bandwidth
            
        self._value = {
            "upper": float(upper),
            "middle": float(mean),
            "lower": float(lower),
            "percent_b": float(percent_b)
        }
        
        return self._value
