import yfinance as yf
import polars as pl
from datetime import datetime
from src.adapters.base import BaseAdapter
from src.models.enums import Columns
from utils import get_logger

logger = get_logger("yfinance_adapter")

class YFinanceAdapter(BaseAdapter):
    def get_kline(
        self, 
        ticker: str, 
        period: str, 
        start_date: datetime | None = None, 
        end_date: datetime | None = None, 
        limit: int = 100
    ) -> pl.DataFrame:
        
        # 1. Ticker is usually consistent (AAPL, GC=F), but ensure safe string
        symbol = ticker
        
        logger.info(f"Fetching {symbol} {period} from YFinance")
        
        try:
            # YF usage: download(tickers, period, interval, start, end)
            # Mapping 'period' (timeframe) to YF interval. 
            # Note: YF 'period' arg is for "how much history", 'interval' is candle size.
            # My api 'period' usually means candle size (1d, 1h).
            
            # Helper to map standard periods to YF intervals if needed
            # For now assume direct pass-through or simple mapping
            interval = period
            
            # If start/end provided, use them. Else YF defaults or use 'limit' approx?
            # YF doesn't strictly support 'limit' rows, it supports date ranges.
            # We might just fetch a default period like "1mo" if no dates given.
            
            kwargs = {"interval": interval, "progress": False}
            if start_date:
                kwargs["start"] = start_date
            if end_date:
                kwargs["end"] = end_date
            
            if not start_date and not end_date:
                # Fallback to fetch enough data for 'limit'
                # logic is imperfect without knowing timeframe size vs limit
                kwargs["period"] = "1mo" 

            pdf = yf.download(symbol, **kwargs)
            
            if pdf.empty:
                logger.warning(f"No data returned for {symbol}")
                return pl.DataFrame()
            
            # Flatten MultiIndex if necessary (yfinance sometimes returns MultiIndex for columns)
            if isinstance(pdf.columns, (list, tuple)) or hasattr(pdf.columns, "levels"):
                 if hasattr(pdf.columns, "get_level_values"):
                    pdf.columns = pdf.columns.get_level_values(0)

            # Reset index to get Date/Datetime as column
            pdf = pdf.reset_index()
            
            # 2. Convert to Polars
            df = pl.from_pandas(pdf)
            
            # 3. Standardize Columns
            # YF cols: Date (or Datetime), Open, High, Low, Close, Adj Close, Volume
            # Standardize names to lowercase first to be safe
            df = df.select(pl.all().name.to_lowercase())
            
            # Rename map
            rename_map = {
                "date": Columns.TIMESTAMP.value,
                "datetime": Columns.TIMESTAMP.value,
                "open": Columns.OPEN.value,
                "high": Columns.HIGH.value,
                "low": Columns.LOW.value,
                "close": Columns.CLOSE.value,
                "volume": Columns.VOLUME.value,
            }
            
            # Filter valid keys that exist in df
            existing_cols = df.columns
            final_map = {k: v for k, v in rename_map.items() if k in existing_cols}
            
            df = df.rename(final_map)
            
            # Ensure TIMESTAMP is proper int (ms) if it's datetime
            # YF usually gives Date or Datetime
            if Columns.TIMESTAMP.value in df.columns:
                df = df.with_columns(
                   pl.col(Columns.TIMESTAMP.value).cast(pl.Datetime).dt.timestamp("ms").alias(Columns.TIMESTAMP.value)
                )

            # Add Symbol
            df = df.with_columns(pl.lit(ticker).alias(Columns.SYMBOL.value))
            
            # Select only required columns (handling missing optional ones gracefully if needed)
            # For now select strictly
            required = [
                Columns.TIMESTAMP.value, 
                Columns.OPEN.value, 
                Columns.HIGH.value, 
                Columns.LOW.value, 
                Columns.CLOSE.value, 
                Columns.VOLUME.value,
                Columns.SYMBOL.value
            ]
            
            df = df.select([c for c in required if c in df.columns])
            
            # Apply limit
            if limit > 0:
                df = df.tail(limit)

            return df

        except Exception as e:
            logger.error(f"YFinance Error: {e}")
            raise
