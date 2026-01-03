from abc import ABC, abstractmethod
import polars as pl
from datetime import datetime
from src.models.enums import Columns

class BaseAdapter(ABC):
    """Abstract base class for all data source adapters."""
    
    @abstractmethod
    def get_kline(
        self, 
        ticker: str, 
        period: str, 
        start_date: datetime | None = None, 
        end_date: datetime | None = None, 
        limit: int = 100
    ) -> pl.DataFrame:
        """
        Fetch kline data and return a standardized Polars DataFrame.
        
        Must return DataFrame with columns strictly matching enum.Columns.
        """
        pass

    def standardize_columns(self, df: pl.DataFrame) -> pl.DataFrame:
        """Helper to ensure columns match the standard."""
        # This is a placeholder; implementations might enforce this 
        # or we check it in the main entry.
        required = [c.value for c in Columns]
        # Basic check logic can go here
        return df
