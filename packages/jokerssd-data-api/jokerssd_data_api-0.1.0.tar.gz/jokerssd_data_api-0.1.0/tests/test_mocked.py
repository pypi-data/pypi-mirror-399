import sys
import unittest
from unittest.mock import MagicMock

# 1. Mock External Dependencies BEFORE importing src.api
# This is necessary because we don't have them installed in this environment
mock_pl = MagicMock()
sys.modules["polars"] = mock_pl
sys.modules["ccxt"] = MagicMock()
sys.modules["yfinance"] = MagicMock()
sys.modules["akshare"] = MagicMock()

# Mock DataFrame behavior to avoid crashes when calling methods on it
mock_df = MagicMock()
mock_pl.DataFrame.return_value = mock_df
mock_pl.from_pandas.return_value = mock_df
mock_df.select.return_value = mock_df
mock_df.rename.return_value = mock_df
mock_df.with_columns.return_value = mock_df
mock_df.tail.return_value = mock_df
mock_df.__getitem__.return_value = [100.0] # Mock returning a list for df['col']
mock_df.columns = ["ts", "open", "high", "low", "close", "vol", "symbol"] # Mock columns existence

import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Now import our modules
# We need to make sure enum_ is importable. It's in root.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.api import pull_kline
from src.models.enums import MarketType, Exchange

class TestMockedAPI(unittest.TestCase):
    def test_pull_kline_crypto_call(self):
        # We just want to ensure it calls the right adapter and returns the mock df
        try:
            df = pull_kline("BTC_USDT", MarketType.CRYPTO, "1d", limit=10)
        except Exception as e:
            self.fail(f"pull_kline raised exception: {e}")
        
        # Verify it returned our mock dict/df
        self.assertTrue(df is not None)

    def test_pull_kline_stock_call(self):
         try:
            df = pull_kline("AAPL", MarketType.STOCK, "1d", exchange=Exchange.YFINANCE)
         except Exception as e:
            self.fail(f"pull_kline raised exception: {e}")
         self.assertTrue(df is not None)

if __name__ == '__main__':
    unittest.main()
