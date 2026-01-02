import asyncio
import sys


if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
else:
    sys.path.append("/Users/kaihock/Desktop/All In/Xecution")
import asyncio
from pathlib import Path
from urllib.parse import parse_qs
import pandas as pd
import logging
from xecution.core.engine import BaseEngine
from xecution.common.enums import DataProvider, Exchange, KlineType, Mode, OrderSide, OrderStatus, OrderType, Symbol, TimeInForce
from xecution.models.config import OrderConfig, RuntimeConfig
from xecution.models.topic import DataTopic, KlineTopic
from xecution.utils.logger import Logger
from xecution.models.order import OrderUpdate
from xecution.utils.utility import (
    to_camel,
    write_csv_overwrite,
    normalize_interval,
    qualifier_suffix,
    _provider_title
)
import numpy as np

# --------------------------------------------------------------------
candle_path1 = Path("data/candle/binance_kline_btc_1h.csv") # candle data file path
# --------------------------------------------------------------------

DATASOURCE_PATH = Path("data/datasource")
CANDLE_PATH = Path("data/candle")
KLINE_FUTURES = KlineTopic(klineType=KlineType.Bybit_Futures, symbol=Symbol.BTCUSDT, timeframe="1m")
KLINE_SPOT = KlineTopic(klineType=KlineType.Binance_Spot, symbol=Symbol.BTCUSDT, timeframe="1h")
BINANCE_FUTURES = KlineTopic(klineType=KlineType.Binance_Futures, symbol=Symbol.BTCUSDT, timeframe="1h")

Data1 = DataTopic(provider=DataProvider.CRYPTOQUANT, url='btc/flow-indicator/exchange-whale-ratio?exchange=binance&window=hour')
Data2 = DataTopic(provider=DataProvider.REXILION, url='btc/market-data/coinbase-premium-gap?window=1h')
Data3 = DataTopic(provider=DataProvider.GLASSNODE, url='blockchain/block_height?a=BTC&i=10m')

# Enable logging to see real-time data
class Engine(BaseEngine):
    """Base engine that initializes BinanceService and processes on_candle_closed and on_datasource_update."""
    def __init__(self, config):
        Logger(log_file="data_retrieval.log", log_level=logging.INFO)
        super().__init__(config)

    async def on_datasource_update(self, datasource_topic):
        """
        Saves datasource to CSV:
        {SYMBOL}_{Provider}-{CategoryCamel}-{EndpointCamel}-{interval}.csv

        Examples:
          BTC_CryptoQuant-MarketData-StablecoinsRatio-1h.csv
          BTC_Rexilion-MarketData-CoinbasePremiumGap-1h.csv
          BTC_Glassnode-Blockchain-BlockHeight-1h.csv
        """
        data = self.data_map.get(datasource_topic, [])
        logging.info(f"Data Incoming: {datasource_topic} (len={len(data)})")

        # split URL into path + query
        raw_url = getattr(datasource_topic, "url", "")
        path, _, query = str(raw_url).lstrip("/").partition("?")
        params = parse_qs(query)

        # resolve provider
        provider = getattr(datasource_topic, "provider", None)
        provider_title = _provider_title(provider)
        provider_name_uc = provider_title.upper()

        # defaults
        symbol = "BTC"
        category_slug = "misc"
        endpoint = "unknown"
        interval = "1h"

        # provider-specific parsing
        parts = [p for p in path.split("/") if p]

        if provider_name_uc == "GLASSNODE":
            # e.g. 'blockchain/block_height?a=BTC&i=1h'
            symbol = (params.get("a") or params.get("asset") or ["BTC"])[0].upper()
            if parts:
                category_slug = parts[0]              # 'blockchain'
                endpoint = parts[-1]                  # 'block_height'
            interval = normalize_interval((params.get("i") or ["1h"])[0])

        else:
            # CryptoQuant or Rexilion style:
            # e.g. 'btc/market-data/coinbase-premium-gap?window=1h'
            if parts:
                symbol = parts[0].upper()             # 'BTC'
                if len(parts) >= 2:
                    category_slug = parts[1]          # 'market-data' / 'network-data' / ...
                endpoint = parts[-1]                  # last segment
            interval = normalize_interval((params.get("window") or ["hour"])[0])

        # camelize for filename
        category_camel = to_camel(category_slug)
        camel_endpoint = to_camel(endpoint)

        # optional qualifiers to avoid collisions across different from/to/miner/exchange combos
        suffix = qualifier_suffix(params)
        camel_endpoint_with_q = camel_endpoint + suffix

        # final filename
        filename = f"{symbol}_{provider_title}-{category_camel}-{camel_endpoint_with_q}-{interval}.csv"
        out_path = DATASOURCE_PATH / filename

        try:
            write_csv_overwrite(out_path, data)
            logging.info(f"Saved {datasource_topic.url} → {out_path}")
        except Exception as e:
            logging.exception(f"Failed to save datasource to {out_path}: {e}")

    async def on_candle_closed(self, kline_topic):
        self.candles = self.data_map[kline_topic]
        candle = np.array(list(map(lambda c: float(c["close"]), self.candles)))        
        logging.info(
            f"Last Kline Closed | {kline_topic.symbol}-{kline_topic.timeframe} | Close: {candle[-1]}"
        )

    async def on_order_update(self, order: OrderUpdate):
        if order.status in (OrderStatus.FILLED, OrderStatus.NEW, OrderStatus.CANCELED):
            logging.error(order.status)


engine = Engine(
    RuntimeConfig(
        mode= Mode.Backtest,
        kline_topic=[
            # KLINE_FUTURES,
            # KLINE_SPOT,
            # BINANCE_FUTURES
        ],
        datasource_topic=[
             Data3
        ],
        data_count=50000,
        exchange=Exchange.Bybit,
        cryptoquant_api_key="iG48lac3kRFcFq0q5WMm0BpnTt1XYMvRB6yz63OP",
        glassnode_api_key="35Ml0UMDbCfF0U7YqYp48GorMN3",
        rexilion_api_key="rexilion-api-key-2025",
    )
)

asyncio.run(engine.start())

