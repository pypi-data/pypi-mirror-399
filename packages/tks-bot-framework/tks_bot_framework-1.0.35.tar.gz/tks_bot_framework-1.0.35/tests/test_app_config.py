import pytest
from botframework.portfolio_mgr import PortfolioMgr
from pytest import approx
import yaml
from pathlib import Path
from famodels.direction import Direction
from unittest.mock import patch, AsyncMock
from botframework.models.position_capacity import PositionCapacity


@pytest.fixture(autouse=True)
def app_config(mocker):
    path = Path(__file__).parent.parent.absolute().joinpath("tests/app_config.yaml")
    with open(path, 'r') as stream:
        try:
            algo_config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            algo_config = {}
    mocker.patch("tksessentials.utils.get_app_config", return_value=algo_config)
    return algo_config

def test_get_total_position_count(app_config):
    # Act.
    # Initialize PortfolioMgr and load position capacities for "BTC".
    position_capacities = PortfolioMgr().get_position_capacities(market="BTC")
    # Expected count: 13 from repeated and 1 individual position for BTC.
    expected_count = 13 + 1
    # Assert.
    assert len(position_capacities) == expected_count

def test_get_specific_position_attributes(app_config):
    # Act.
    # Initialize PortfolioMgr and load position capacities for "BTC".
    position_capacities = PortfolioMgr().get_position_capacities(market="BTC")
    # Pick pos_idx=14 and check its attributes.
    specific_position = next((pc for pc in position_capacities if pc.id == 14), None)
    # Assert.
    assert specific_position is not None, "Position with pos_idx=14 not found."
    # Verify attributes of pos_idx=14
    assert specific_position.take_profit == 20
    assert specific_position.stop_loss == 6
    assert specific_position.direction == "short"
    assert specific_position.position_size_in_percentage == approx(1 / 14)
    assert specific_position.market == "BTC-USDT"
    assert specific_position.market_symbol == "BTC/USDT"

def test_get_position_capacity_btc_asset(app_config):
    # Act.
    portfolio_mgr = PortfolioMgr()
    position_capacity = portfolio_mgr.get_position_capacity(market="BTC", pos_idx=8)
    assert position_capacity is not None, "Position with pos_idx=8 for BTC not found."
    # Assert.
    assert position_capacity.direction == "long"
    assert position_capacity.take_profit == 10
    assert position_capacity.stop_loss is None
    assert position_capacity.position_size_in_percentage == approx(1 / 14)
    assert position_capacity.market == "BTC-USDT"
    assert position_capacity.market_symbol == "BTC/USDT"

def test_get_position_capacity_btc_individual(app_config):
    # Act.
    portfolio_mgr = PortfolioMgr()
    position_capacity = portfolio_mgr.get_position_capacity(market="BTC", pos_idx=14)
    assert position_capacity is not None, "Individual position with pos_idx=14 for BTC not found."
    # Assert.
    assert position_capacity.direction == "short"
    assert position_capacity.take_profit == 20
    assert position_capacity.stop_loss == 6
    assert position_capacity.position_size_in_percentage == approx(1 / 14)
    assert position_capacity.market == "BTC-USDT"
    assert position_capacity.market_symbol == "BTC/USDT"

def test_get_position_capacity_sol_individual(app_config):
    # Act.
    portfolio_mgr = PortfolioMgr()
    position_capacity = portfolio_mgr.get_position_capacity(market="SOL", pos_idx=14)
    # Assert.
    assert position_capacity is not None, "Individual position with pos_idx=14 for SOL not found."
    assert position_capacity.direction == "short"
    assert position_capacity.take_profit == 20
    assert position_capacity.stop_loss == 8
    assert position_capacity.position_size_in_percentage == approx(1 / 14)
    assert position_capacity.market == "SOL-USDT"
    assert position_capacity.market_symbol == "SOL/USDT"

def test_get_directional_position_capacities_sol_long(app_config):
    # Act.
    portfolio_mgr = PortfolioMgr()
    sol_long_positions = portfolio_mgr.get_directional_position_capacities(market="SOL", direction=Direction.LONG)
    # Assert.
    assert len(sol_long_positions) == 13, "Expected 13 long positions for SOL"
    # Check attributes of a sample position (e.g., pos_idx=0).
    specific_position = sol_long_positions[0]
    assert specific_position.direction == "long"
    assert specific_position.take_profit == 8
    assert specific_position.stop_loss == 5
    assert specific_position.alternative_take_profit == 12
    assert specific_position.alternative_stop_loss == 7
    assert specific_position.position_size_in_percentage == approx(1 / 14)
    assert specific_position.market == "SOL-USDT"
    assert specific_position.market_symbol == "SOL/USDT"

def test_get_directional_position_capacities_sol_short(app_config):
    # Act.
    portfolio_mgr = PortfolioMgr()
    sol_short_positions = portfolio_mgr.get_directional_position_capacities(market="SOL", direction=Direction.SHORT)
    # Assert.
    assert len(sol_short_positions) == 1, "Expected 1 short position for SOL"
    # Check attributes of the specific short position (pos_idx=14).
    specific_position = sol_short_positions[0]
    assert specific_position.direction == "short"
    assert specific_position.take_profit == 20
    assert specific_position.stop_loss == 8
    assert specific_position.alternative_take_profit is None
    assert specific_position.alternative_stop_loss is None
    assert specific_position.position_size_in_percentage == approx(1 / 14)
    assert specific_position.market == "SOL-USDT"
    assert specific_position.market_symbol == "SOL/USDT"

@pytest.mark.asyncio
async def test_get_free_position_capacities_for_buys_mixed_btc_long(app_config):
    # Act.
    portfolio_mgr = PortfolioMgr()
    ksqldb_query_url = "http://localhost:8088/query-stream"
    view_name = "queryable_pull_tks_gatherer_trades_btc"  # Extracts "BTC" as the market
    direction = Direction.LONG
    # Mock the active positions to simulate currently occupied pos_idx.
    mock_active_positions = [0, 1]  # Simulate pos_idx 0 and 1 are occupied for BTC LONG
    # Patch TradeMgr.get_active_positions to return the mocked active positions.
    with patch('botframework.trade_mgr.TradeMgr.get_active_positions', new=AsyncMock(return_value=mock_active_positions)):
        # Run the method to get free position capacities
        free_positions = await portfolio_mgr.get_free_position_capacities_for_buys(
            ksqldb_query_url=ksqldb_query_url,
            view_name=view_name,
            direction=direction
        )
        # Check that the returned free positions exclude the mocked active positions.
        free_pos_ids = [pos.id for pos in free_positions]
        assert all(pos_id not in mock_active_positions for pos_id in free_pos_ids), "Active positions should not be in free positions"
        # Check the expected count of free positions.
        expected_free_positions = 13 - len(mock_active_positions)
        assert len(free_positions) == expected_free_positions, f"Expected {expected_free_positions} free positions but got {len(free_positions)}"

@pytest.mark.asyncio
async def test_get_free_position_capacities_for_buys_mixed_sol_short(app_config):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    ksqldb_query_url = "http://localhost:8088/query-stream"
    view_name = "queryable_pull_tks_gatherer_trades_sol"  # Extracts "SOL" as the market
    direction = Direction.SHORT
    # Mock the active positions to simulate currently occupied pos_idx.
    mock_active_positions = [14]  # Simulate pos_idx 14 is occupied for SOL SHORT
    # Act.
    # Patch TradeMgr.get_active_positions to return the mocked active positions.
    with patch('botframework.trade_mgr.TradeMgr.get_active_positions', new=AsyncMock(return_value=mock_active_positions)):
        # Run the method to get free position capacities
        free_positions = await portfolio_mgr.get_free_position_capacities_for_buys(
            ksqldb_query_url=ksqldb_query_url,
            view_name=view_name,
            direction=direction
        )
        # Check that the returned free positions exclude the mocked active positions.
        free_pos_ids = [pos.id for pos in free_positions]
        assert all(pos_id not in mock_active_positions for pos_id in free_pos_ids), "Active positions should not be in free positions"
        # Check the expected count of free positions.
        expected_free_positions = 1 - len(mock_active_positions)  # Only one SOL SHORT position exists
        assert len(free_positions) == expected_free_positions, f"Expected {expected_free_positions} free positions but got {len(free_positions)}"

@pytest.mark.asyncio
async def test_get_a_free_position_capacity_for_buys_combined_long_position(app_config):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    # Mock return value for `get_free_position_capacities_for_buys` with one available long position for BTC
    mock_free_positions = [
        PositionCapacity(id=0, market="BTC-USDT", market_symbol="BTC/USDT", direction="long",
                         position_size_in_percentage=1/14, take_profit=10, stop_loss=None)
    ]
    portfolio_mgr.get_free_position_capacities_for_buys = AsyncMock(return_value=mock_free_positions)
    # Act.
    # Run the method to get a free long position for BTC.
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
async def test_get_a_free_position_capacity_for_buys_combined_short_position(app_config):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    # Mock return value for `get_free_position_capacities_for_buys` with one available short position for SOL.
    mock_free_positions = [
        PositionCapacity(id=14, market="SOL-USDT", market_symbol="SOL/USDT", direction="short",
                         position_size_in_percentage=1/14, take_profit=20, stop_loss=8)
    ]
    portfolio_mgr.get_free_position_capacities_for_buys = AsyncMock(return_value=mock_free_positions)
    # Act.
    # Run the method to get a free short position for SOL
    result = await portfolio_mgr.get_a_free_position_capacity_for_buys(
        ksqldb_query_url="http://mock-url",
        view_name="queryable_pull_tks_gatherer_trades_sol",
        direction=Direction.SHORT
    )
    # Assert.
    assert result is not None
    assert result.id == 14
    assert result.market == "SOL-USDT"
    assert result.take_profit == 20
    assert result.stop_loss == 8

@pytest.mark.asyncio
async def test_get_a_free_position_capacity_for_buys_combined_no_available_positions(app_config):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    # Mock return value for `get_free_position_capacities_for_buys` as an empty list.
    portfolio_mgr.get_free_position_capacities_for_buys = AsyncMock(return_value=[])
    # Act.
    # Run the method to get a free position for BTC long
    result = await portfolio_mgr.get_a_free_position_capacity_for_buys(
        ksqldb_query_url="http://mock-url",
        view_name="queryable_pull_tks_gatherer_trades_btc",
        direction=Direction.LONG
    )
    # Assert.
    assert result is None

@pytest.mark.asyncio
async def test_get_position_size_in_percentage_mixed_config(app_config):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    # Act & Assert.
    # Test for BTC long position.
    btc_position_size_long = await portfolio_mgr.get_position_size_in_percentage(market="BTC", direction=Direction.LONG)
    # With 13 long positions for BTC, each should take up approximately 1/13 of the total, or ~7.69%.
    assert btc_position_size_long == approx(100 / 13, rel=1e-3)
    # Act.
    # Test for BTC short position.
    btc_position_size_short = await portfolio_mgr.get_position_size_in_percentage(market="BTC", direction=Direction.SHORT)
    # With 1 short position for BTC, should return 100% since there's only one position.
    assert btc_position_size_short == 100.0
    # Act & Assert.
    # Test for SOL long position.
    sol_position_size_long = await portfolio_mgr.get_position_size_in_percentage(market="SOL", direction=Direction.LONG)
    # With 13 long positions for SOL, each should take up approximately 1/13 of the total, or ~7.69%.
    assert sol_position_size_long == approx(100 / 13, rel=1e-3)
    # Act.
    # Test for SOL short position.
    sol_position_size_short = await portfolio_mgr.get_position_size_in_percentage(market="SOL", direction=Direction.SHORT)
    # With 1 short position for SOL, should return 100% since there's only one position.
    assert sol_position_size_short == 100.0

@pytest.mark.asyncio
async def test_calculate_take_profit_stop_loss_mixed_config(app_config):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    close_price = 10000.0
    atr = 100.0  
    # Act & Assert for SOL, LONG direction with position index 3.
    sol_tp_price, sol_sl_price = await portfolio_mgr.calculate_take_profit_stop_loss(
        close=close_price,
        market="SOL",
        direction=Direction.LONG,
        pos_idx=3,
        atr=atr
    )
    # Expectations: LONG direction with ATR for SOL position with pos_idx=3.
    # Take Profit = close + (take_profit * atr), Stop Loss = close - (stop_loss * atr)
    assert sol_tp_price == approx(close_price + (8 * atr), rel=1e-3)  # Expected 10800.0
    assert sol_sl_price == approx(close_price - (5 * atr), rel=1e-3)  # Expected 9500.0
    # Act & Assert for BTC, SHORT direction with individual position index 14.
    btc_tp_price, btc_sl_price = await portfolio_mgr.calculate_take_profit_stop_loss(
        close=close_price,
        market="BTC",
        direction=Direction.SHORT,
        pos_idx=14,
        atr=atr
    )
    # Expectations: SHORT direction with ATR for BTC individual position with pos_idx=14.
    # Take Profit = close - (take_profit * atr), Stop Loss = close + (stop_loss * atr)
    assert btc_tp_price == approx(close_price - (20 * atr), rel=1e-3)  # Expected 8000.0
    assert btc_sl_price == approx(close_price + (6 * atr), rel=1e-3)  # Expected 10600.0
