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


@pytest.fixture
def app_config_position_capacities_by_asset(mocker):
    path = Path(__file__).parent.parent.absolute().joinpath("tests/app_config_position_capacities_by_asset.yaml")
    with open(path, 'r') as stream:
        try:
            algo_config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            algo_config = {}
    mocker.patch("tksessentials.utils.get_app_config", return_value=algo_config)
    return algo_config

def test_get_position_capacities_position_capacities_by_asset(app_config_position_capacities_by_asset):
    # Act.
    # Initialize PortfolioMgr and load position capacities for "BTC".
    position_capacities = PortfolioMgr().get_position_capacities(market="BTC")
    # Calculate expected count based on the provided configuration.
    asset_count = sum(
        asset["count"] for asset in app_config_position_capacities_by_asset.get("position_capacities_by_asset", [])
        if asset["market"].startswith("BTC")
    )
    expected_count = asset_count  # No individual positions in this case.
    # Assert.
    # Verify the count of returned position capacities.
    assert len(position_capacities) == expected_count
    assert len(position_capacities) == 14
    # Check that the ids range from 0 to 13.
    expected_ids = set(range(14))
    actual_ids = {pc.id for pc in position_capacities}
    assert actual_ids == expected_ids

def test_get_position_capacity_specific_index(app_config_position_capacities_by_asset):
    # Initialize PortfolioMgr and load position capacities for "BTC".
    position_capacities = PortfolioMgr().get_position_capacities(market="BTC")
    # Pick pos_idx=4 and check its attributes.
    specific_position = next((pc for pc in position_capacities if pc.id == 4), None)
    assert specific_position is not None, "Position with pos_idx=4 not found."
    # Assert the specific attributes for pos_idx=4.
    assert specific_position.take_profit == 10  
    # assert specific_position.stop_loss is None
    assert specific_position.direction == "long"
    assert specific_position.position_size_in_percentage == approx(1 / 14) 
    assert specific_position.market == "BTC-USDT"
    assert specific_position.market_symbol == "BTC/USDT"

# Test for retrieving a specific position for BTC
def test_get_position_capacity_btc(app_config_position_capacities_by_asset):
    portfolio_mgr = PortfolioMgr()
    # Retrieve position for BTC with pos_idx=4.
    position_capacity = portfolio_mgr.get_position_capacity(market="BTC", pos_idx=4)
    # Assert the expected attributes
    assert position_capacity is not None, "Position with pos_idx=4 for BTC not found."
    assert position_capacity.direction == "long"
    assert position_capacity.take_profit == 10
    assert position_capacity.stop_loss is None
    assert position_capacity.position_size_in_percentage == approx(1 / 14)
    assert position_capacity.market == "BTC-USDT"
    assert position_capacity.market_symbol == "BTC/USDT"

def test_get_position_capacity_sol(app_config_position_capacities_by_asset):
    portfolio_mgr = PortfolioMgr()
    # Retrieve position for SOL with pos_idx=10.
    position_capacity = portfolio_mgr.get_position_capacity(market="SOL", pos_idx=10)
    # Assert the expected attributes.
    assert position_capacity is not None, "Position with pos_idx=10 for SOL not found."
    assert position_capacity.direction == "long"
    assert position_capacity.take_profit == 8
    assert position_capacity.alternative_take_profit == 12
    assert position_capacity.stop_loss == 5
    assert position_capacity.alternative_stop_loss == 7
    assert position_capacity.position_size_in_percentage == approx(1 / 14)
    assert position_capacity.market == "SOL-USDT"
    assert position_capacity.market_symbol == "SOL/USDT"

def test_get_directional_position_capacities_btc_long(app_config_position_capacities_by_asset):
    # Act.
    portfolio_mgr = PortfolioMgr()
    btc_long_positions = portfolio_mgr.get_directional_position_capacities(market="BTC", direction=Direction.LONG)
    # Assert.
    # Expecting 14 positions for BTC in long direction.
    assert len(btc_long_positions) == 14, "Expected 14 long positions for BTC"
    # Check attributes of a sample position (e.g., pos_idx=0).
    specific_position = btc_long_positions[0]
    assert specific_position.direction == "long"
    assert specific_position.take_profit == 10
    assert specific_position.stop_loss is None
    assert specific_position.alternative_take_profit is None
    assert specific_position.alternative_stop_loss is None
    assert specific_position.position_size_in_percentage == approx(1 / 14)
    assert specific_position.market == "BTC-USDT"
    assert specific_position.market_symbol == "BTC/USDT"

def test_get_directional_position_capacities_btc_short(app_config_position_capacities_by_asset):
    # Act.
    portfolio_mgr = PortfolioMgr()
    btc_short_positions = portfolio_mgr.get_directional_position_capacities(market="BTC", direction=Direction.SHORT)
    # Assert.
    assert len(btc_short_positions) == 0, "Expected no short positions for BTC"

@pytest.mark.asyncio
async def test_get_free_position_capacities_for_buys(app_config_position_capacities_by_asset):
    # Act.
    portfolio_mgr = PortfolioMgr()
    # Mock the ksqldb_query_url and view_name for this test.
    ksqldb_query_url = "http://localhost:8088/query-stream"
    view_name = "queryable_pull_tks_gatherer_trades_btc"  # Extracts "BTC" as the market
    direction = Direction.LONG
    # Mock the active positions to simulate currently occupied pos_idx.
    mock_active_positions = [0, 1, 3, 7]
    # Patch TradeMgr.get_active_positions to return the mocked active positions.
    with patch('botframework.trade_mgr.TradeMgr.get_active_positions', new=AsyncMock(return_value=mock_active_positions)):
        free_positions = await portfolio_mgr.get_free_position_capacities_for_buys(
            ksqldb_query_url=ksqldb_query_url,
            view_name=view_name,
            direction=direction
        )
        # Assert.
        # Check that the returned free positions exclude the mocked active positions.
        free_pos_ids = [pos.id for pos in free_positions]
        assert all(pos_id not in mock_active_positions for pos_id in free_pos_ids), "Active positions should not be in free positions"
        # Check the expected count of free positions (14 - len(mock_active_positions)).
        expected_free_positions = 14 - len(mock_active_positions)
        assert len(free_positions) == expected_free_positions, f"Expected {expected_free_positions} free positions but got {len(free_positions)}"

@pytest.mark.asyncio
async def test_get_a_free_position_capacity_for_buys_position_capacities_by_asset(app_config_position_capacities_by_asset):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    # Mock return value for `get_free_position_capacities_for_buys`.
    mock_free_positions = [
        PositionCapacity(id=0, market="BTC-USDT", market_symbol="BTC/USDT", direction="long", 
                         position_size_in_percentage=1/14, take_profit=10, stop_loss=None)
    ]
    portfolio_mgr.get_free_position_capacities_for_buys = AsyncMock(return_value=mock_free_positions)
    # Act.
    result = await portfolio_mgr.get_a_free_position_capacity_for_buys(
        ksqldb_query_url="http://mock-url", 
        view_name="queryable_pull_tks_gatherer_trades_btc", 
        direction=Direction.LONG
    )
    # Assert.
    assert result is not None
    assert result.id == 0
    assert result.market == "BTC-USDT"
    assert result.take_profit == 10
    assert result.stop_loss is None

@pytest.mark.asyncio
async def test_get_a_free_position_capacity_for_buys_position_capacities_by_asset_no_available_positions(app_config_position_capacities_by_asset):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    # Mock return value for `get_free_position_capacities_for_buys` as an empty list.
    portfolio_mgr.get_free_position_capacities_for_buys = AsyncMock(return_value=[])
    # Act.
    result = await portfolio_mgr.get_a_free_position_capacity_for_buys(
        ksqldb_query_url="http://mock-url", 
        view_name="queryable_pull_tks_gatherer_trades_btc", 
        direction=Direction.LONG
    )
    # Assert.
    assert result is None

@pytest.mark.asyncio
async def test_get_position_size_in_percentage_position_capacities_by_asset(app_config_position_capacities_by_asset):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    # Act & Assert.
    # Test for BTC long position.
    btc_position_size_long = await portfolio_mgr.get_position_size_in_percentage(market="BTC", direction=Direction.LONG)
    # With 14 long positions for BTC, each position should take up approximately 1/14 of the total, or ~7.14%.
    assert btc_position_size_long == approx(100 / 14, rel=1e-3)
    # Act.
    # Test for BTC short position (not defined in config).
    btc_position_size_short = await portfolio_mgr.get_position_size_in_percentage(market="BTC", direction=Direction.SHORT)
    # Since no short positions exist for BTC, should return 0%.
    assert btc_position_size_short == 0.0
    # Act & Assert.
    # Test for SOL long position.
    sol_position_size_long = await portfolio_mgr.get_position_size_in_percentage(market="SOL", direction=Direction.LONG)
    # With 14 long positions for SOL, each position should take up approximately 1/14 of the total, or ~7.14%.
    assert sol_position_size_long == approx(100 / 14, rel=1e-3)
    # Act.
    # Test for SOL short position (not defined in config).
    sol_position_size_short = await portfolio_mgr.get_position_size_in_percentage(market="SOL", direction=Direction.SHORT)
    # Since no short positions exist for SOL, should return 0%.
    assert sol_position_size_short == 0.0

@pytest.mark.asyncio
async def test_calculate_take_profit_stop_loss_by_asset_atr(app_config_position_capacities_by_asset):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    close_price = 10000.0
    atr = 100.0  # Average True Range value
    # Act & Assert for SOL, LONG direction.
    sol_tp_price, sol_sl_price = await portfolio_mgr.calculate_take_profit_stop_loss(
        close=close_price,
        market="SOL",
        direction=Direction.LONG,
        pos_idx=0,
        atr=atr
    )
    # Expectations: LONG direction with ATR for SOL position.
    # Take Profit = close + (take_profit * atr), Stop Loss = close - (stop_loss * atr)
    assert sol_tp_price == approx(close_price + (8 * atr), rel=1e-3)
    assert sol_sl_price == approx(close_price - (5 * atr), rel=1e-3)
