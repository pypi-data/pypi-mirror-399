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
def app_config_individual_position_capacities(mocker):
    path = Path(__file__).parent.parent.absolute().joinpath("tests/app_config_individual_position_capacities.yaml")
    with open(path, 'r') as stream:
        try:
            algo_config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            algo_config = {}
    mocker.patch("tksessentials.utils.get_app_config", return_value=algo_config)
    return algo_config

def test_get_position_capacities_individual_position_capacities(app_config_individual_position_capacities):
    # Act.
    # Initialize PortfolioMgr and load position capacities for "BTC".
    position_capacities = PortfolioMgr().get_position_capacities(market="BTC")
    # Calculate expected count based on the provided configuration.
    individual_count = len([
        pos for pos in app_config_individual_position_capacities.get("individual_positions", [])
        if pos["position_capacity"]["market"] == "BTC-USDT"
    ])
    expected_count = individual_count  # No repeated capacities in this case
    # Assert.
    assert len(position_capacities) == expected_count
    assert len(position_capacities) == 1

def test_get_position_capacity_specific_index_individual(app_config_individual_position_capacities):
    # Act.
    # Initialize PortfolioMgr and load position capacities for "BTC".
    position_capacities = PortfolioMgr().get_position_capacities(market="BTC")
    # Pick pos_idx=0 and check its attributes.
    specific_position = next((pc for pc in position_capacities if pc.id == 0), None)
    # Assert.
    assert specific_position is not None, "Position with pos_idx=0 not found."
    # Assert the specific attributes for pos_idx=0.
    assert specific_position.take_profit == 12 
    assert specific_position.stop_loss == 6 
    assert specific_position.direction == "short"
    assert specific_position.position_size_in_percentage == approx(1 / 14)
    assert specific_position.market == "BTC-USDT"
    assert specific_position.market_symbol == "BTC/USDT"

def test_get_position_capacity_btc(app_config_individual_position_capacities):
    # Act.
    portfolio_mgr = PortfolioMgr()
    # Retrieve position for BTC with pos_idx=0.
    position_capacity = portfolio_mgr.get_position_capacity(market="BTC", pos_idx=0)
    # Assert.
    assert position_capacity is not None, "Position with pos_idx=0 for BTC not found."
    assert position_capacity.direction == "short"
    assert position_capacity.take_profit == 12
    assert position_capacity.stop_loss == 6
    assert position_capacity.position_size_in_percentage == approx(1 / 14)
    assert position_capacity.market == "BTC-USDT"
    assert position_capacity.market_symbol == "BTC/USDT"

def test_get_position_capacity_sol(app_config_individual_position_capacities):
    # Act.
    portfolio_mgr = PortfolioMgr()
    # Retrieve position for SOL with pos_idx=1.
    position_capacity = portfolio_mgr.get_position_capacity(market="SOL", pos_idx=0)
    # Assert.
    assert position_capacity is not None, "Position with pos_idx=1 for SOL not found."
    assert position_capacity.direction == "short"
    assert position_capacity.take_profit == 15
    assert position_capacity.stop_loss == 8
    assert position_capacity.position_size_in_percentage == approx(1 / 14)
    assert position_capacity.market == "SOL-USDT"
    assert position_capacity.market_symbol == "SOL/USDT"

def test_get_directional_position_capacities_btc_long(app_config_individual_position_capacities):
    # Act.
    portfolio_mgr = PortfolioMgr()
    btc_long_positions = portfolio_mgr.get_directional_position_capacities(market="BTC", direction=Direction.LONG)
    # Assert.
    assert len(btc_long_positions) == 0, "Expected no long positions for BTC"

def test_get_directional_position_capacities_btc_short(app_config_individual_position_capacities):
    # Act.
    portfolio_mgr = PortfolioMgr()
    btc_short_positions = portfolio_mgr.get_directional_position_capacities(market="BTC", direction=Direction.SHORT)
    # Assert.
    assert len(btc_short_positions) == 1, "Expected one short position for BTC"
    specific_position = btc_short_positions[0]
    # Assert the attributes of the BTC short position
    assert specific_position.id == 0
    assert specific_position.direction == "short"
    assert specific_position.take_profit == 12
    assert specific_position.stop_loss == 6
    assert specific_position.position_size_in_percentage == approx(1 / 14)
    assert specific_position.market == "BTC-USDT"
    assert specific_position.market_symbol == "BTC/USDT"

@pytest.mark.asyncio
async def test_get_free_position_capacities_for_buys_individual(app_config_individual_position_capacities):
    # Act.
    portfolio_mgr = PortfolioMgr()
    ksqldb_query_url = "http://localhost:8088/query-stream"
    view_name = "queryable_pull_tks_gatherer_trades_btc"  # Extracts "BTC" as the market
    direction = Direction.SHORT
    # Mock the active positions to simulate currently occupied pos_idx.
    mock_active_positions = [0]  # Simulate pos_idx 0 is occupied for BTC
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
        # Check the expected count of free positions (no position should remain unoccupied)
        expected_free_positions = 1 - len(mock_active_positions)
        assert len(free_positions) == expected_free_positions, f"Expected {expected_free_positions} free positions but got {len(free_positions)}"


@pytest.mark.asyncio
async def test_get_a_free_position_capacity_for_buys(app_config_individual_position_capacities):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    # Mock return value for `get_free_position_capacities_for_buys`.
    mock_free_positions = [
        PositionCapacity(id=0, market="BTC-USDT", market_symbol="BTC/USDT", direction="short", 
                         position_size_in_percentage=1/14, take_profit=12, stop_loss=6)
    ]
    portfolio_mgr.get_free_position_capacities_for_buys = AsyncMock(return_value=mock_free_positions)
    # Act.
    result = await portfolio_mgr.get_a_free_position_capacity_for_buys(
        ksqldb_query_url="http://mock-url", 
        view_name="queryable_pull_tks_gatherer_trades_btc", 
        direction=Direction.SHORT
    )
    # Assert.
    assert result is not None
    assert result.id == 0
    assert result.market == "BTC-USDT"
    assert result.take_profit == 12
    assert result.stop_loss == 6

@pytest.mark.asyncio
async def test_get_a_free_position_capacity_for_buys_no_available_positions(app_config_individual_position_capacities):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    # Mock return value for `get_free_position_capacities_for_buys` as an empty list.
    portfolio_mgr.get_free_position_capacities_for_buys = AsyncMock(return_value=[])
    # Act.
    result = await portfolio_mgr.get_a_free_position_capacity_for_buys(
        ksqldb_query_url="http://mock-url", 
        view_name="queryable_pull_tks_gatherer_trades_btc", 
        direction=Direction.SHORT
    )
    # Assert.
    assert result is None

@pytest.mark.asyncio
async def test_get_position_size_in_percentage_short(app_config_individual_position_capacities):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    # Act.
    # Test for BTC short position.
    btc_position_size = await portfolio_mgr.get_position_size_in_percentage(market="BTC", direction=Direction.SHORT)
    # Assert.
    # With 1 short position for BTC, should return 100% since there's only one position.
    assert btc_position_size == 100.0
    # Act.
    # Test for BTC long position (not defined in config).
    btc_position_size_long = await portfolio_mgr.get_position_size_in_percentage(market="BTC", direction=Direction.LONG)
    # Assert.
    # Since no long positions exist for BTC, should return 0%.
    assert btc_position_size_long == 0.0
    # Act.
    # Test for SOL short position.
    sol_position_size = await portfolio_mgr.get_position_size_in_percentage(market="SOL", direction=Direction.SHORT)
    # Assert.
    # With 1 short position for SOL, should return 100% since there's only one position.
    assert sol_position_size == 100.0
    # Act.
    # Test for SOL long position (not defined in config).
    sol_position_size_long = await portfolio_mgr.get_position_size_in_percentage(market="SOL", direction=Direction.LONG)
    # ASsert.
    # Since no long positions exist for SOL, should return 0%.
    assert sol_position_size_long == 0.0
    
@pytest.mark.asyncio
async def test_calculate_take_profit_stop_loss_atr(app_config_individual_position_capacities):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    close_price = 10000.0
    atr = 100.0  # Average True Range value
    # Act & Assert for BTC, SHORT direction.
    btc_tp_price, btc_sl_price = await portfolio_mgr.calculate_take_profit_stop_loss(
        close=close_price,
        market="BTC",
        direction=Direction.SHORT,
        pos_idx=0,
        atr=atr
    )
    # Expectations: SHORT direction with ATR for BTC position.
    # Take Profit = close - (take_profit * atr), Stop Loss = close + (stop_loss * atr)
    assert btc_tp_price == approx(close_price - (12 * atr), rel=1e-3)
    assert btc_sl_price == approx(close_price + (6 * atr), rel=1e-3)
    # Act & Assert for SOL, SHORT direction.
    sol_tp_price, sol_sl_price = await portfolio_mgr.calculate_take_profit_stop_loss(
        close=close_price,
        market="SOL",
        direction=Direction.SHORT,
        pos_idx=0,
        atr=atr
    )
    # Expectations: SHORT direction with ATR for SOL position.
    # Take Profit = close - (take_profit * atr), Stop Loss = close + (stop_loss * atr)
    assert sol_tp_price == approx(close_price - (15 * atr), rel=1e-3)
    assert sol_sl_price == approx(close_price + (8 * atr), rel=1e-3)
