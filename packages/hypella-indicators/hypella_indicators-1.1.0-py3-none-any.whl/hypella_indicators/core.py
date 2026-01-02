from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Union, Dict, Any
import pandas as pd

@dataclass
class Candle:
    """Represents a standardized OHLCV candle."""
    timestamp: int  # Unix timestamp in milliseconds
    open: float
    high: float
    low: float
    close: float
    volume: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume
        }

class Indicator(ABC):
    """Abstract base class for all Hypella indicators."""

    def __init__(self, **kwargs):
        """Initialize indicator with configuration arguments."""
        self.config = kwargs

    def candles_to_df(self, candles: List[Candle]) -> pd.DataFrame:
        """Helper to convert list of Candles to DataFrame."""
        return pd.DataFrame([c.to_dict() for c in candles])

    @abstractmethod
    def calculate(self, candles: List[Candle]) -> Union[float, Dict[str, float]]:
        """
        Calculate the latest indicator value based on historical candles.
        
        Args:
            candles: List of historical candles, ending with the most recent closed candle.
            
        Returns:
            The calculated indicator value as a float, or a dictionary for multi-value indicators.
        """
        pass
