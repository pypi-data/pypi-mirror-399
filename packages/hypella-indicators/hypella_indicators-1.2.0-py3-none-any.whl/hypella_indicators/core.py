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
        self.reset()

    def reset(self):
        """Reset the indicator state."""
        self._value: Union[float, Dict[str, float], None] = None
        self._initialized = False

    @property
    def value(self) -> Union[float, Dict[str, float], None]:
        """Return the latest calculated value."""
        return self._value

    def candles_to_df(self, candles: List[Candle]) -> pd.DataFrame:
        """Helper to convert list of Candles to DataFrame."""
        return pd.DataFrame([c.to_dict() for c in candles])

    @abstractmethod
    def calculate(self, candles: List[Candle]) -> Union[float, Dict[str, float]]:
        """
        Calculate the latest indicator value based on historical candles (stateless).
        
        Args:
            candles: List of historical candles, ending with the most recent closed candle.
            
        Returns:
            The calculated indicator value as a float, or a dictionary for multi-value indicators.
        """
        pass

    @abstractmethod
    def update(self, candle: Candle) -> Union[float, Dict[str, float]]:
        """
        Update indicator with a new candle and return the latest value (stateful).
        
        Args:
            candle: The latest closed candle.
            
        Returns:
            The newly calculated indicator value.
        """
        pass

    def seed(self, candles: List[Candle]):
        """
        Warm up the indicator state with historical data.
        
        Args:
            candles: Historical candles for initialization.
        """
        self.reset()
        for candle in candles:
            self.update(candle)
