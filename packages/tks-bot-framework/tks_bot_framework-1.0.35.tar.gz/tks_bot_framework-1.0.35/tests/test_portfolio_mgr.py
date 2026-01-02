from datetime import datetime
from botframework.portfolio_mgr import PortfolioMgr
from botframework.trade_mgr import TradeMgr
from famodels.direction import Direction
from botframework.models.position_capacity import PositionCapacity
from botframework import botframework_utils
from tksessentials import utils
from unittest.mock import patch, AsyncMock, MagicMock
from pathlib import Path
import pytest
from pytest import approx
import yaml
from typing import List


@pytest.fixture(autouse=True)
def app_config(mocker):
    print("Test Fixture up")
    # Patch the entire app_config.yaml
    path = Path(__file__).parent.parent.absolute().joinpath("tests/app_config.yaml")
    with open(path, 'r') as stream:
        try:
            algo_config=yaml.safe_load(stream)
            print(algo_config)
        except yaml.YAMLError as exc:
            print(exc)
    mocker.patch("tksessentials.utils.get_app_config", return_value=algo_config)
    yield # this is where the testing happens¨
    return algo_config

@pytest.mark.asyncio
@patch('botframework.trade_mgr.TradeMgr.get_latest_trade_data_by_pos_idx', new_callable=AsyncMock)
@patch('botframework.trade_mgr.TradeMgr.create_additional_entry_for_pos_idx', new_callable=AsyncMock)
async def test_check_for_position_closing_tp_long(mock_create_entry, mock_get_latest_trade_data):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    mock_get_latest_trade_data.return_value = [
        None, None, None, None, None, None, None, None, Direction.LONG, 110, 95, None, None
    ]
    ksqldb_query_url = "http://localhost:8088/query"
    topic_name = "mock_topic"
    view_name = "mock_view"
    pos_idx = 0
    close = 100
    high = 111 # TP reached
    low = 99
    # Act.
    await portfolio_mgr.check_for_position_closing(ksqldb_query_url, topic_name, view_name, pos_idx, close, high, low)
    # Assert.
    mock_create_entry.assert_called_once_with(
        ksqldb_query_url=ksqldb_query_url,
        topic_name_trade=topic_name,
        view_name_trade=view_name,
        pos_idx=pos_idx,
        new_status_of_position='closed',
        tp_sl_reached=True
    )
    
@pytest.mark.asyncio
@patch('botframework.trade_mgr.TradeMgr.get_latest_trade_data_by_pos_idx', new_callable=AsyncMock)
@patch('botframework.trade_mgr.TradeMgr.create_additional_entry_for_pos_idx', new_callable=AsyncMock)
async def test_check_for_position_closing_tp_long(mock_create_entry, mock_get_latest_trade_data):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    mock_get_latest_trade_data.return_value = [
        None, None, None, None, None, None, None, None, Direction.LONG, 110, 95, None, None
    ]
    ksqldb_query_url = "http://localhost:8088/query"
    topic_name = "mock_topic"
    view_name = "mock_view"
    pos_idx = 0
    close = 100
    high = 103 # TP not reached in this case
    low = 99 # SL not reached either
       # Act.
    await portfolio_mgr.check_for_position_closing(ksqldb_query_url, topic_name, view_name, pos_idx, close, high, low)
    # Assert.
    mock_create_entry.assert_not_called()

@pytest.mark.asyncio
@patch('botframework.trade_mgr.TradeMgr.get_latest_trade_data_by_pos_idx', new_callable=AsyncMock)
@patch('botframework.trade_mgr.TradeMgr.create_additional_entry_for_pos_idx', new_callable=AsyncMock)
async def test_check_for_position_closing_sl_long(mock_create_entry, mock_get_latest_trade_data):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    mock_get_latest_trade_data.return_value = [
    None, None, None, None, None, None, None, None, Direction.LONG, 110, 95, None, None
    ]
    ksqldb_query_url = "http://localhost:8088/query"
    topic_name = "mock_topic"
    view_name = "mock_view"
    pos_idx = 0
    close = 100
    high = 105
    low = 94 # SL reached
    # Act.
    await portfolio_mgr.check_for_position_closing(ksqldb_query_url, topic_name, view_name, pos_idx, close, high, low)
    # Assert.
    mock_create_entry.assert_called_once_with(
        ksqldb_query_url=ksqldb_query_url,
        topic_name_trade=topic_name,
        view_name_trade=view_name,
        pos_idx=pos_idx,
        new_status_of_position='closed',
        tp_sl_reached=True
    )

@pytest.mark.asyncio
@patch('botframework.trade_mgr.TradeMgr.get_latest_trade_data_by_pos_idx', new_callable=AsyncMock)
@patch('botframework.trade_mgr.TradeMgr.create_additional_entry_for_pos_idx', new_callable=AsyncMock)
async def test_check_for_position_closing_tp_short(mock_create_entry, mock_get_latest_trade_data):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    mock_get_latest_trade_data.return_value = [
        None, None, None, None, None, None, None, None, Direction.SHORT, 88, 120, None, None
    ]
    ksqldb_query_url = "http://localhost:8088/query"
    topic_name = "mock_topic"
    view_name = "mock_view"
    pos_idx = 0
    close = 100
    high = 109  # TP for short not reached in this case
    low = 89  # SL for short not reached either
    # Act.
    await portfolio_mgr.check_for_position_closing(ksqldb_query_url, topic_name, view_name, pos_idx, close, high, low)
    # Assert.
    mock_create_entry.assert_not_called()

@pytest.mark.asyncio
@patch('botframework.trade_mgr.TradeMgr.get_latest_trade_data_by_pos_idx', new_callable=AsyncMock)
@patch('botframework.trade_mgr.TradeMgr.create_additional_entry_for_pos_idx', new_callable=AsyncMock)
async def test_check_for_position_closing_sl_short(mock_create_entry, mock_get_latest_trade_data):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    mock_get_latest_trade_data.return_value = [
        None, None, None, None, None, None, None, None, Direction.SHORT, 92, 120, None, None
    ]
    ksqldb_query_url = "http://localhost:8088/query"
    topic_name = "mock_topic"
    view_name = "mock_view"
    pos_idx = 0
    close = 100
    high = 106
    low = 90 # TP reached
    # Act.
    await portfolio_mgr.check_for_position_closing(ksqldb_query_url, topic_name, view_name, pos_idx, close, high, low)
    # Assert.
    mock_create_entry.assert_called_once_with(
        ksqldb_query_url=ksqldb_query_url,
        topic_name_trade=topic_name,
        view_name_trade=view_name,
        pos_idx=pos_idx,
        new_status_of_position='closed',
        tp_sl_reached=True
    )

def test_get_exchange():
    algo_cft = utils.get_app_config()
    assert algo_cft['exchange'] == 'BINANCE'

def test_get_market():
    algo_cft = utils.get_app_config()
    assert algo_cft['market'] == 'ETH-USDT'