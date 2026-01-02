import yaml
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from pytest_mock import MockerFixture
from botframework.trade_mgr import TradeMgr  
from botframework.market_mgr import MarketMgr
from botframework.portfolio_mgr import PortfolioMgr
from botframework import botframework_utils
from famodels.direction import Direction
from famodels.trade import StatusOfTrade
from fasignalprovider.side import Side
from tksessentials import utils
import json
import time
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, AsyncMock, ANY


@pytest.fixture(autouse=True)
def insert_test_data(mocker):
    print("Test Fixture up")
    # Patch the entire algo_config.yaml
    path = Path(__file__).parent.parent.absolute().joinpath("tests/app_config.yaml")
    with open(path, 'r') as stream:
        try:
            algo_config=yaml.safe_load(stream)
            print(algo_config)
        except yaml.YAMLError as exc:
            print(exc)
    mocker.patch("tksessentials.utils.get_app_config", return_value=algo_config)

@pytest.fixture
def fixed_datetime():
    """A fixture that returns a fixed datetime object and formatted strings."""
    fixed_dt = datetime(2023, 3, 15, 12, 0, tzinfo=timezone.utc)
    formatted_timestamp = fixed_dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    timestamp_for_data_entry_key = fixed_dt.timestamp()
    return fixed_dt, formatted_timestamp, timestamp_for_data_entry_key

@pytest.mark.asyncio
@patch('botframework.kafka_producer.KafkaProducerManager', autospec=True)  # Mock KafkaProducerManager
async def test_create_first_entry_for_pos_idx(mock_kafka_producer_manager, fixed_datetime):
    # Arrange.
    fixed_dt, formatted_timestamp, timestamp_for_data_entry_key = fixed_datetime
    trade_mgr = TradeMgr()
    topic_name_trade = "trade_topic"
    pos_idx = 1
    provider_trade_id = "test_trade_id"
    provider_signal_id = "test_signal_id"
    status_of_position = StatusOfTrade.NEW
    price = 100.0
    is_hot_signal = True
    market = "test_market"
    data_source = "test_data_source"
    direction = Direction.LONG
    tp = 110.0
    sl = 90.0
    position_size_in_percentage = 10.0
    percentage_of_position = 50.0

    # Set up the mock Kafka producer
    mock_kafka_producer_instance = mock_kafka_producer_manager.return_value
    mock_kafka_producer_instance.produce_message = AsyncMock()

    # Act.
    await trade_mgr.create_first_entry_for_pos_idx(
        kafka_producer_manager=mock_kafka_producer_instance,
        topic_name_trade=topic_name_trade,
        pos_idx=pos_idx,
        provider_trade_id=provider_trade_id,
        provider_signal_id=provider_signal_id,
        status_of_position=status_of_position,
        price=price,
        is_hot_signal=is_hot_signal,
        market=market,
        data_source=data_source,
        direction=direction,
        tp=tp,
        sl=sl,
        position_size_in_percentage=position_size_in_percentage,
        percentage_of_position=percentage_of_position,
        timestamp=timestamp_for_data_entry_key
    )
    
    # Assert.
    trade_data = {
        "pos_idx_str": str(pos_idx),
        "time_of_data_entry": str(timestamp_for_data_entry_key),
        "pos_idx": pos_idx,  # Ensure pos_idx is an integer
        "provider_trade_id": provider_trade_id,
        "status_of_position": status_of_position,
        "is_hot_signal": is_hot_signal,
        "market": market,
        "data_source": data_source,
        "direction": direction,
        "tp": tp,
        "sl": sl,
        "tp_sl_reached": False,
        "position_size_in_percentage": position_size_in_percentage,
        "time_of_position_opening": str(timestamp_for_data_entry_key),
        "time_of_position_closing": None,
        "buy_orders": json.dumps({
            "buy_order_1": {
                "timestamp": timestamp_for_data_entry_key,
                "provider_signal_id": provider_signal_id,
                "percentage_of_position": percentage_of_position,
                "buy_price": price
            }
        }),
        "sell_orders": json.dumps({})
    }

    key = str(pos_idx)  # Ensure key is a string

    mock_kafka_producer_instance.produce_message.assert_called_once_with(
        topic_name=topic_name_trade,
        key=key,
        value=trade_data
    )

@pytest.mark.asyncio
@patch('botframework.botframework_utils.execute_pull_query', new_callable=AsyncMock)
async def test_get_latest_trade_data_by_pos_idx(mock_execute_pull_query):
    # Arrange.
    trade_mgr = TradeMgr()
    ksqldb_query_url = "http://localhost:8088/query"
    view_name = "mock_view"
    pos_idx = 1
    # Mocking the Kafka pull query results
    mock_execute_pull_query.return_value = [
        [1000, pos_idx, 'some_trade_id', 'NEW'],
        [2000, pos_idx, 'some_trade_id', 'SELLING']
    ]
    # Act.
    latest_trade_data = await trade_mgr.get_latest_trade_data_by_pos_idx(ksqldb_query_url, view_name, pos_idx)
    # Assert.
    assert latest_trade_data == [2000, pos_idx, 'some_trade_id', 'SELLING']
    assert mock_execute_pull_query.call_count == 1

@pytest.mark.asyncio
@patch('botframework.botframework_utils.execute_pull_query', new_callable=AsyncMock)
async def test_get_latest_trade_data_by_provider_trade_id(mock_execute_pull_query):
    # Arrange.
    trade_mgr = TradeMgr()
    ksqldb_query_url = "http://localhost:8088/query"
    view_name = "mock_view"
    provider_trade_id = "some_trade_id"
    # Mocking the Kafka pull query results
    mock_execute_pull_query.return_value = [
        [1000, 0, provider_trade_id, 'NEW'],
        [2000, 0, provider_trade_id, 'SELLING'],
        [1500, 1, provider_trade_id, 'CLOSED']
    ]
    # Act.
    latest_trade_data = await trade_mgr.get_latest_trade_data_by_provider_trade_id(ksqldb_query_url, view_name, provider_trade_id)
    # Assert.
    assert latest_trade_data == [2000, 0, provider_trade_id, 'SELLING']
    assert mock_execute_pull_query.call_count == 1

@pytest.mark.asyncio
@patch('tksessentials.database.produce_message', new_callable=AsyncMock)
@patch('botframework.trade_mgr.TradeMgr.get_latest_trade_data_by_provider_trade_id', new_callable=AsyncMock)
async def test_update_status_of_trade(mock_get_latest_trade_data_by_provider_trade_id, mock_kafka_send_message):
    # Arrange
    trade_mgr = TradeMgr()
    ksqldb_query_url = "http://localhost:8088/query"
    view_name = "mock_view"
    provider_trade_id = "some_trade_id"
    topic_name = "trade_topic"
    status_of_position = StatusOfTrade.SELLING
    timestamp = time.time() * 1000
    new_time_of_data_entry = str(timestamp)
    # Mocking the latest trade data
    active_trade = [
        "0", 1000, 0, provider_trade_id, 'NEW', True, 'test_market', 'test_data_source', 'LONG', 110, 90, False, 10, 1000,
        None, json.dumps({'order1': 'data'}), json.dumps({'order2': 'data'})
    ]
    mock_get_latest_trade_data_by_provider_trade_id.return_value = active_trade
    # Act.
    await trade_mgr.update_status_of_trade(ksqldb_query_url, view_name, provider_trade_id, topic_name, status_of_position)
    # Assert.
    expected_trade_data = {
        "pos_idx_str": active_trade[0],
        "time_of_data_entry": ANY,
        "pos_idx": active_trade[2],
        "provider_trade_id": active_trade[3],
        "status_of_position": status_of_position,
        "is_hot_signal": active_trade[5],
        "market": active_trade[6],
        "data_source": active_trade[7],
        "direction": active_trade[8],
        "tp": active_trade[9],
        "sl": active_trade[10],
        "tp_sl_reached": active_trade[11],
        "position_size_in_percentage": active_trade[12],
        "time_of_position_opening": active_trade[13],
        "time_of_position_closing": active_trade[14],
        "buy_orders": active_trade[15],
        "sell_orders": active_trade[16]
    }
    mock_kafka_send_message.assert_called_once_with(
        topic_name=topic_name,
        key=ANY,
        value=expected_trade_data
    )
    assert mock_get_latest_trade_data_by_provider_trade_id.call_count == 1

@pytest.fixture
def my_class_instance():
    instance = TradeMgr()
    return instance

@pytest.fixture
def ksqldb_query_url():
    return "http://example.com/query"

@pytest.fixture
def view_name():
    return "test_view"

@pytest.mark.asyncio
async def test_get_realized_and_unrealized_profit_and_loss_of_position_no_active_trade(my_class_instance, ksqldb_query_url, view_name):
    # Mock the get_latest_trade_data_by_pos_idx method to return None
    my_class_instance.get_latest_trade_data_by_pos_idx = AsyncMock(return_value=None)
    
    pos_idx = 1
    market = "BTC/USD"
    exchange = "Binance"
    
    result = await my_class_instance.get_realized_and_unrealized_profit_and_loss_of_position(ksqldb_query_url, view_name, pos_idx, market, exchange)
    
    assert result == (0, 0, 0, 0)

@pytest.mark.asyncio
async def test_get_realized_and_unrealized_profit_and_loss_of_position_buy_orders_only(my_class_instance, ksqldb_query_url, view_name):
    # Mock the get_latest_trade_data_by_pos_idx method to return sample data
    my_class_instance.get_latest_trade_data_by_pos_idx = AsyncMock(return_value=(
        "1", '2023-01-01T00:00:00Z', 1, 'trade_id', 'OPEN', True,
        'BTC/USD', 'Binance', 'LONG', 10000, 8000, False, 100,
        '2023-01-01T00:00:00Z', None, json.dumps({'order1': {'buy_price': 2500, 'percentage_of_position': 50}, 'order2': {'buy_price': 2800, 'percentage_of_position': 50}}), '{}'
    ))

    pos_idx = 1
    market = "BTC/USD"
    exchange = "Binance"

    # Mock the get_last_price method of MarketMgr to return a predefined price
    with patch.object(MarketMgr, 'get_last_price', AsyncMock(return_value=3000)):
        result = await my_class_instance.get_realized_and_unrealized_profit_and_loss_of_position(ksqldb_query_url, view_name, pos_idx, market, exchange)
    
    # Current price set in the function is 3000
    expected_unrealized_pnl = ((3000 - 2500) / 2500 * 50) + ((3000 - 2800) / 2800 * 50)
    expected_realized_pnl = 0
    
    assert result == (expected_realized_pnl, expected_unrealized_pnl, 100, 0)

@pytest.mark.asyncio
async def test_get_realized_and_unrealized_profit_and_loss_of_position_buy_and_sell_orders(my_class_instance, ksqldb_query_url, view_name):
    # Mock the get_latest_trade_data_by_pos_idx method to return sample data
    my_class_instance.get_latest_trade_data_by_pos_idx = AsyncMock(return_value=(
        "1", '2023-01-01T00:00:00Z', 1, 'trade_id', 'OPEN', True,
        'BTC/USD', 'Binance', 'LONG', 10000, 8000, False, 100,
        '2023-01-01T00:00:00Z', None, json.dumps({'order1': {'buy_price': 2500, 'percentage_of_position': 70}, 'order2': {'buy_price': 2800, 'percentage_of_position': 30}}), 
        json.dumps({'order1': {'sell_price': 2900, 'percentage_of_position': 50}})
    ))

    pos_idx = 1
    market = "BTC/USD"
    exchange = "Binance"

    # Mock the get_last_price method of MarketMgr to return a predefined price
    with patch.object(MarketMgr, 'get_last_price', AsyncMock(return_value=3000)):
        result = await my_class_instance.get_realized_and_unrealized_profit_and_loss_of_position(ksqldb_query_url, view_name, pos_idx, market, exchange)
    
    # Current price set in the function is 3000
    hypothetical_unrealized_profit = ((3000 - 2500) / 2500 * 70) + ((3000 - 2800) / 2800 * 30)
    average_entry_price = 3000 / ((100 + hypothetical_unrealized_profit) / 100)
    
    expected_realized_pnl = (2900 - average_entry_price) / average_entry_price * 50
    open_percentage_of_position = (70 + 30) - 50
    expected_unrealized_pnl = (3000 - average_entry_price) / average_entry_price * open_percentage_of_position
    
    # Assert the calculated values with correct expected values
    assert result == (expected_realized_pnl, expected_unrealized_pnl, 100, 50)

@pytest.mark.asyncio
@patch("botframework.botframework_utils.execute_pull_query")
async def test_get_active_positions_short(mock_execute_pull_query):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    ksqldb_query_url = "http://mock_ksqldb_url"
    view_name = "queryable_pull_tks_gatherer_trades_btc"  # Updated to include market symbol 'btc'
    # Mock Kafka query to return a non-closed status for the BTC position only
    mock_execute_pull_query.return_value = [
        [None, None, 0, None, "open", None, None, None, None, None, None],
        [None, None, 1, None, "closed", None, None, None, None, None, None],
    ]
    # Act.
    occupied_positions = await TradeMgr().get_active_positions(
        ksqldb_query_url=ksqldb_query_url,
        view_name=view_name
    )
    # Assert.
    assert occupied_positions == [0]
    mock_execute_pull_query.assert_called_once_with(
        ksqldb_query_url=ksqldb_query_url,
        view_name=view_name,
        select_columns='*',
        where_clause="1=1",
        offset_reset="earliest"
    )
