from botframework.botframework import Botframework
import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

@pytest.fixture(autouse=True)
def mock_dependencies(mocker):
    # Mock get_app_config
    path = Path(__file__).parent.parent.absolute().joinpath("tests/app_config.yaml")
    with open(path, 'r') as stream:
        try:
            algo_config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    mocker.patch("tksessentials.utils.get_app_config", return_value=algo_config)
    mocker.patch("tksessentials.utils.get_application_name", return_value="tks-atomic-test")
    mocker.patch("tksessentials.utils.get_environment", return_value="development")
    # Mock dependencies
    mocker.patch('botframework.strategy.Strategy', return_value=MagicMock(get_name=MagicMock(return_value='DummyStrategy')))
    mocker.patch('botframework.portfolio_mgr.PortfolioMgr', return_value=MagicMock(get_market=MagicMock(return_value='DummyMarket'), get_exchange=MagicMock(return_value='DummyExchange'), get_position_capacities=MagicMock(return_value=[]), get_directional_position_capacities=MagicMock(return_value=[])))
    mocker.patch('botframework.trade_mgr.TradeMgr', return_value=MagicMock(get_active_positions=AsyncMock(return_value=[])))
    mocker.patch('asyncio.sleep', return_value=AsyncMock())

@pytest.mark.asyncio
async def test_start_framework_initializes_correctly(mock_dependencies):
    # Arrange.
    botframework_instance = Botframework()
    initial_tasks = [AsyncMock(), AsyncMock()]
    asyncio_tasks = [(None, 10, AsyncMock()), (20, 5, AsyncMock())]
    with patch('botframework.scheduler.Scheduler') as mock_scheduler:
        mock_scheduler_instance = mock_scheduler.return_value
        mock_scheduler_instance.start_task = AsyncMock()
        mock_scheduler_instance.start_interval = AsyncMock()
        with patch.object(Botframework, 'start_framework', new=AsyncMock()) as mock_start_framework:
            # Act.
            await botframework_instance.start_framework(initial_tasks, asyncio_tasks, "http://localhost:8088/query-stream", "mock_view")
            # Assert.
            mock_start_framework.assert_called_once_with(initial_tasks, asyncio_tasks, "http://localhost:8088/query-stream", "mock_view")
