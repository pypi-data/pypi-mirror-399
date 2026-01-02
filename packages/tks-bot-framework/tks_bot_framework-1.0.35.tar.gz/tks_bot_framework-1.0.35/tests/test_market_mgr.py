import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock
from botframework.market_mgr import MarketMgr 
from botframework.trading_timeframe import TradingTimeFrame
from botframework.cex_proxy import CEXProxy
import asyncio
from datetime import datetime, timedelta

# @pytest.mark.asyncio
# async def test_get_real_time_data():
#     # Arrange.
#     mocked_response_data = {"data": "mocked_value"}
#     mocked_response_json = json.dumps(mocked_response_data)
#     # Create an AsyncMock for the WebSocket's recv method to return response and then raise CancelledError
#     mock_recv = AsyncMock(side_effect=[mocked_response_json, asyncio.CancelledError()])
#     # Mock the WebSocket connection to properly simulate an async context manager
#     mock_ws = MagicMock()
#     mock_ws.__aenter__.return_value.recv = mock_recv
#     # Patch the websockets.connect function to return our mock WebSocket connection
#     with patch('websockets.connect', return_value=mock_ws):
#         # Create an instance of MarketMgr and a mock callback
#         market_mgr = MarketMgr()
#         mock_callback = AsyncMock()
#         # Act.
#         # Run the method under test and expect it to raise CancelledError to exit the loop
#         with pytest.raises(asyncio.CancelledError):
#             await market_mgr.get_real_time_data("mock_market", mock_callback)
#         # Assert.
#         mock_recv.assert_awaited() 
#         mock_callback.assert_awaited_with(mocked_response_data) 

# @pytest.mark.asyncio
# async def test_get_last_price():
#     # Arrange.
#     mocked_response_data = {"price": "1000.00"}
#     market = "BTC/USDT"
#     # Mock the HTTP response.
#     with aioresponses() as m:
#         m.get("http://localhost:8400/price/BTC/USDT", payload=mocked_response_data)
#         market_mgr = MarketMgr()
#         # Act.
#         response = await market_mgr.get_last_price(market)
#         # Assert.
#         assert response == mocked_response_data['price']

# @pytest.mark.asyncio
# async def test_get_last_price_failure():
#     # Arrange.
#     market = "BTC/USDT"
#     # Mock the httpx ClientSession and its get method to simulate a failed response.
#     mock_session = AsyncMock()
#     mock_response = AsyncMock()
#     mock_response.status = 500  # Simulate a failed response
#     mock_session.get = AsyncMock(return_value=mock_response)
#     # Patch httpx's ClientSession to return our mock session
#     with patch('httpx.Asyncclient', return_value=mock_session):
#         market_mgr = MarketMgr()
#         # Act and assert.
#         with pytest.raises(Exception):
#             await market_mgr.get_last_price(market)

test_data = [
    [1700719200000, 37323.11, 37336.65, 37268.25, 37272.68, 626.65148],
    [1700722800000, 37272.68, 37369.22, 37272.68, 37369.21, 800.38751],
]

@pytest.mark.asyncio
async def test_get_historical_data():
    # Arrange.
    exchange = 'BINANCE'
    market_symbol = 'BTC/USDT'
    timeframe = '1h'
    limit = 1000
    # Mock the CEXProxy and its get_exchange_proxy method
    mock_cex_proxy = AsyncMock(CEXProxy)
    mock_cex_proxy.get_exchange_proxy = AsyncMock(return_value=AsyncMock())
    # Mock the fetch_ohlcv method of the exchange to return test data
    mock_cex_proxy.get_exchange_proxy.return_value.fetch_ohlcv = AsyncMock(return_value=test_data)
    with patch('botframework.market_mgr.CEXProxy', return_value=mock_cex_proxy):
        market_mgr = MarketMgr()
        # Act.
        historical_data = await market_mgr.get_historical_data(exchange, market_symbol, timeframe, limit)
        # Assert.
        assert historical_data == test_data
        mock_cex_proxy.get_exchange_proxy.assert_awaited_with(exchange)
        mock_cex_proxy.get_exchange_proxy.return_value.fetch_ohlcv.assert_awaited_with(symbol=market_symbol, timeframe=timeframe, since=None, limit=limit)

base_timestamp = datetime.now().timestamp() * 1000 

def generate_test_data(interval_minutes, base_timestamp):
    timestamp1 = base_timestamp
    timestamp2 = base_timestamp + (interval_minutes * 60 * 1000)
    return [
        [timestamp1, 37323.11, 37336.65, 37268.25, 37272.68, 626.65148],
        [timestamp2, 37272.68, 37369.22, 37272.68, 37369.21, 800.38751],
    ]

test_data_mapping = {
    TradingTimeFrame.MIN_1.value: generate_test_data(1, base_timestamp),
    TradingTimeFrame.MIN_5.value: generate_test_data(5, base_timestamp),
    TradingTimeFrame.MIN_15.value: generate_test_data(15, base_timestamp),
    TradingTimeFrame.HOUR.value: generate_test_data(60, base_timestamp),
    TradingTimeFrame.HOUR_4.value: generate_test_data(240, base_timestamp),
    TradingTimeFrame.HOUR_6.value: generate_test_data(360, base_timestamp),
    TradingTimeFrame.DAY.value: generate_test_data(1440, base_timestamp),
    TradingTimeFrame.WEEK.value: generate_test_data(10080, base_timestamp),
    TradingTimeFrame.MONTH.value: generate_test_data(43800, base_timestamp), 
}

@pytest.mark.asyncio
@pytest.mark.parametrize("timeframe", [
    TradingTimeFrame.TICK.value,
    TradingTimeFrame.MIN_1.value,
    TradingTimeFrame.MIN_5.value,
    TradingTimeFrame.MIN_15.value,
    TradingTimeFrame.HOUR.value,
    TradingTimeFrame.HOUR_4.value,
    TradingTimeFrame.HOUR_6.value,
    TradingTimeFrame.DAY.value,
    TradingTimeFrame.WEEK.value,
    TradingTimeFrame.MONTH.value,
])
async def test_get_historical_data_with_different_timeframes(timeframe):
    # Arrange.
    exchange = 'BINANCE'
    market_symbol = 'BTC/USDT'
    limit = 1000
    test_data = test_data_mapping.get(timeframe)
    mock_cex_proxy = AsyncMock()
    mock_cex_proxy.get_exchange_proxy = AsyncMock(return_value=AsyncMock())
    mock_cex_proxy.get_exchange_proxy.return_value.fetch_ohlcv = AsyncMock(return_value=test_data)
    with patch('botframework.market_mgr.CEXProxy', return_value=mock_cex_proxy):
        market_mgr = MarketMgr()
        # Act.
        historical_data = await market_mgr.get_historical_data(exchange, market_symbol, timeframe, limit)
        # Assert.
        assert historical_data == test_data
        mock_cex_proxy.get_exchange_proxy.assert_awaited_with(exchange)
        mock_cex_proxy.get_exchange_proxy.return_value.fetch_ohlcv.assert_awaited_with(symbol=market_symbol, timeframe=timeframe, since=None, limit=limit)
