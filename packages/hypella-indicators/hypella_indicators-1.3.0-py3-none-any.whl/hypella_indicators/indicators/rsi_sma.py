from typing import List
import pandas as pd
from hypella_indicators.core import Indicator, CandleData
from hypella_indicators.indicators.rsi import RSI
from hypella_indicators.indicators.sma import SMA

class RSISMA(Indicator):
    """
    Simple Moving Average of the Relative Strength Index (RSI).
    
    Arguments:
        rsi_period (int): RSI Lookback period. Default: 14.
        sma_period (int): Simple Moving Average period. Default: 14.
    """
    
    def __init__(self, rsi_period: int = 14, sma_period: int = 14):
        self.rsi_period = rsi_period
        self.sma_period = sma_period
        self.rsi_indicator = RSI(period=rsi_period)
        self.sma_indicator = SMA(period=sma_period)
        super().__init__(rsi_period=rsi_period, sma_period=sma_period)

    def reset(self):
        super().reset()
        self.rsi_indicator.reset()
        self.sma_indicator.reset()

    def calculate(self, candles: List[CandleData]) -> float:
        # Get RSI series
        rsi_series = self.rsi_indicator.calculate_series(candles)
        
        if len(rsi_series) < self.sma_period:
            return 0.0
            
        # Calculate SMA of RSI
        sma_series = rsi_series.rolling(window=self.sma_period, min_periods=self.sma_period).mean()
        
        # Return the latest value
        last_val = sma_series.iloc[-1]
        if pd.isna(last_val):
            return 0.0
            
        return float(last_val)

    def update(self, candle: CandleData) -> float:
        rsi_val = self.rsi_indicator.update(candle)
        
        # We need to wrap the RSI value in a CandleData for the SMA indicator
        # since SMA.update expects a CandleData object.
        fake_candle = CandleData(
            timestamp=candle.timestamp,
            open=rsi_val,
            high=rsi_val,
            low=rsi_val,
            close=rsi_val,
            volume=0.0
        )
        
        self._value = self.sma_indicator.update(fake_candle)
        self._initialized = self.rsi_indicator._initialized and self.sma_indicator._initialized
        return float(self._value)
