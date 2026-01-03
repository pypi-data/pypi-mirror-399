import akshare as ak
import polars as pl
from datetime import datetime
from src.adapters.base import BaseAdapter
from src.models.enums import Columns
from utils import get_logger

logger = get_logger("akshare_adapter")

class AKShareAdapter(BaseAdapter):
    def get_kline(
        self, 
        ticker: str, 
        period: str, 
        start_date: datetime | None = None, 
        end_date: datetime | None = None, 
        limit: int = 100
    ) -> pl.DataFrame:
        
        # 1. Prepare Dates (AKShare often expects 'YYYYMMDD' strings)
        start_str = start_date.strftime("%Y%m%d") if start_date else "20200101"
        end_str = end_date.strftime("%Y%m%d") if end_date else datetime.now().strftime("%Y%m%d")
        
        # 2. Identify Type (Stock vs Futures)
        # This is tricky with just a ticker. 
        # Requirement says inputs are standardized:
        # Stock: "000001" (assumed A-share)
        # Futures: "AU2412" or similar
        # We might need better heuristics or explicit 'market_type' passed down?
        # The 'get_kline' signature allows additional kwargs if we modified BaseAdapter,
        # but for now we have to infer or assume usage context from 'pull_kline' wrapper logic.
        # Actually, 'pull_kline' has market_type, but it's not passed to 'get_kline' in BaseAdapter.
        # FIX: I should have included market_type in get_kline or passed it in __init__.
        # For now, I'll attempt simple detection: A-shares usually numeric. Futures often alpha-numeric.
        
        logger.info(f"Fetching {ticker} from AKShare ({period})")

        try:
            pdf = None
            
            # Heuristic for A-Share Stock (Numeric ticker)
            if ticker.isdigit():
                # stock_zh_a_hist: daily data
                # period mapping: 'daily' -> default. 
                # If period < 1d, akshare supports stock_zh_a_minute logic but api differs.
                # Assuming Daily for simplicity unless period indicates otherwise.
                
                # Handling 'period'
                adjust = "qfq" # Default forward adjust
                
                pdf = ak.stock_zh_a_hist(symbol=ticker, start_date=start_str, end_date=end_str, adjust=adjust)
                # Columns: 日期, 开盘, 收盘, 最高, 最低, 成交量, ...
                
            else:
                # Heuristic for Futures
                # Generic futures history
                # This often requires specific exchange info or variation
                # Try 'futures_main_sina' for main contracts or similar
                # For specific contracts, maybe 'futures_zh_daily_sina'
                pdf = ak.futures_zh_daily_sina(symbol=ticker)
                # Columns: date, open, high, low, close, volume...

            if pdf is None or pdf.empty:
                logger.warning(f"No data returned for {ticker}")
                return pl.DataFrame()

            # 3. Normalize Columns
            # AKShare returns Chinese column names often
            
            rename_map = {
                "日期": Columns.TIMESTAMP.value,
                "date": Columns.TIMESTAMP.value,
                "开盘": Columns.OPEN.value,
                "open": Columns.OPEN.value,
                "最高": Columns.HIGH.value,
                "high": Columns.HIGH.value,
                "最低": Columns.LOW.value,
                "low": Columns.LOW.value,
                "收盘": Columns.CLOSE.value,
                "close": Columns.CLOSE.value,
                "成交量": Columns.VOLUME.value,
                "volume": Columns.VOLUME.value,
            }
            
            # Convert to Polars
            df = pl.from_pandas(pdf)
            
            # Rename
            existing_cols = df.columns
            final_map = {k: v for k, v in rename_map.items() if k in existing_cols}
            df = df.rename(final_map)
            
            # Date Parsing
            # AKShare often returns 'yyyy-mm-dd' string in 'timestamp' col
            if Columns.TIMESTAMP.value in df.columns:
                # Check formatting
                # It might be pl.Utf8 or pl.Date
                col_type = df.schema[Columns.TIMESTAMP.value]
                if col_type == pl.Utf8 or col_type == pl.String:
                    # Try casting
                     df = df.with_columns(
                        pl.col(Columns.TIMESTAMP.value).str.strptime(pl.Date, "%Y-%m-%d").cast(pl.Datetime).dt.timestamp("ms")
                    )
                elif col_type == pl.Date:
                     df = df.with_columns(
                        pl.col(Columns.TIMESTAMP.value).cast(pl.Datetime).dt.timestamp("ms")
                    )
            
            # Add Symbol
            df = df.with_columns(pl.lit(ticker).alias(Columns.SYMBOL.value))

             # Select strictly
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

            if limit > 0:
                df = df.tail(limit)
                
            return df

        except Exception as e:
            logger.error(f"AKShare Error: {e}")
            raise
