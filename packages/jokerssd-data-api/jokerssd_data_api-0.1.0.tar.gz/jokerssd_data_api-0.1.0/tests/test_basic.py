import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.api import pull_kline, MarketType, Exchange
from src.models.enums import Columns

class TestDataAPI(unittest.TestCase):
    
    @patch('src.adapters.ccxt_adapter.ccxt')
    def test_crypto_dispatch(self, mock_ccxt):
        # Setup mock
        mock_exchange = MagicMock()
        mock_ccxt.binance.return_value = mock_exchange
        mock_exchange.fetch_ohlcv.return_value = [
            [1600000000000, 100, 105, 95, 102, 1000] # Timestamp, Open, High, Low, Close, Volume
        ]
        
        df = pull_kline("BTC_USDT", MarketType.CRYPTO, "1d", limit=1)
        
        self.assertFalse(df.is_empty())
        self.assertEqual(df[Columns.SYMBOL.value][0], "BTC_USDT")
        self.assertEqual(df[Columns.CLOSE.value][0], 102.0)

    @patch('src.adapters.yfinance_adapter.yf')
    def test_stock_dispatch(self, mock_yf):
        # Setup mock pandas df
        import pandas as pd
        data = {
            'Open': [150], 'High': [155], 'Low': [149], 'Close': [152], 'Volume': [10000],
            'Date': [pd.Timestamp("2020-01-01")]
        }
        pdf = pd.DataFrame(data)
        mock_yf.download.return_value = pdf
        
        df = pull_kline("AAPL", MarketType.STOCK, "1d", exchange=Exchange.YFINANCE)
        
        self.assertFalse(df.is_empty())
        self.assertEqual(df[Columns.SYMBOL.value][0], "AAPL")
        self.assertEqual(df[Columns.CLOSE.value][0], 152.0)

if __name__ == '__main__':
    unittest.main()
