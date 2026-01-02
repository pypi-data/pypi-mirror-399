from typing import List
import pandas as pd
from hypella_indicators.core import Indicator, Candle
from hypella_indicators.indicators.rsi import RSI

class RSISMA(Indicator):
    """
    Simple Moving Average of the Relative Strength Index (RSI).
    
    Arguments:
        rsi_period (int): RSI Lookback period. Default: 14.
        sma_period (int): Simple Moving Average period. Default: 14.
    """
    
    def __init__(self, rsi_period: int = 14, sma_period: int = 14):
        super().__init__(rsi_period=rsi_period, sma_period=sma_period)
        self.rsi_period = rsi_period
        self.sma_period = sma_period
        self.rsi_indicator = RSI(period=rsi_period)

    def calculate(self, candles: List[Candle]) -> float:
        # Get RSI series
        rsi_series = self.rsi_indicator.calculate_series(candles)
        
        if len(rsi_series) < self.sma_period:
            return 0.0
            
        # Calculate SMA of RSI
        sma_series = rsi_series.rolling(window=self.sma_period, min_periods=self.sma_period).mean()
        
        # Return the latest value
        # Handle NaN if series is too short even if len check passed (due to NaNs in RSI start)
        last_val = sma_series.iloc[-1]
        if pd.isna(last_val):
            return 0.0
            
        return float(last_val)
