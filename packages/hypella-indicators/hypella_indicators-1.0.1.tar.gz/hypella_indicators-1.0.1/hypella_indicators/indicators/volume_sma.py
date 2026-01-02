from typing import List
import pandas as pd
from hypella_indicators.core import Indicator, Candle

class VolumeSMA(Indicator):
    """
    Simple Moving Average of Volume.
    
    Arguments:
        period (int): Lookback period. Default: 20.
    """
    
    def __init__(self, period: int = 20):
        super().__init__(period=period)
        self.period = period

    def calculate_series(self, candles: List[Candle]) -> pd.Series:
        if len(candles) < self.period:
            return pd.Series([0.0] * len(candles))
            
        df = self.candles_to_df(candles)
        return df['volume'].rolling(window=self.period, min_periods=self.period).mean()

    def calculate(self, candles: List[Candle]) -> float:
        series = self.calculate_series(candles)
        if len(series) == 0:
            return 0.0
        val = series.iloc[-1]
        return 0.0 if pd.isna(val) else float(val)
