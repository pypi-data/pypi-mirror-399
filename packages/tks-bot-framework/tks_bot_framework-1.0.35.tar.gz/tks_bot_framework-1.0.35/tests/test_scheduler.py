from unittest.mock import patch, AsyncMock
import pytest
from botframework.scheduler import Scheduler
from datetime import datetime
import asyncio
from itertools import cycle

@pytest.mark.asyncio
async def test_start_task():
    # Arrange
    with patch('botframework.scheduler.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value = datetime(2022, 9, 26, 0, 0, 0)
        mock_callback = AsyncMock()
        scheduler = Scheduler()
        # Act
        await scheduler.start_task(delay=None, bot_callback=mock_callback)
        # Allow the event loop to run briefly to ensure the callback has time to be invoked
        await asyncio.sleep(0.1)
    # Assert
    mock_callback.assert_awaited_once() 

@pytest.mark.asyncio
async def test_start_interval(mocker):
    # Arrange
    mock_datetime = mocker.patch('botframework.scheduler.datetime')
    mock_datetime.utcnow.return_value = datetime(2022, 9, 26, 0, 0, 0)
    mocked_time_decision_making_interval = mocker.patch(
        "botframework.scheduler.Scheduler.time_decision_making_interval",
        new_callable=AsyncMock
    )
    mock_callback = AsyncMock()
    # Act
    await Scheduler().start_interval(interval=60, delay=None, bot_callback=mock_callback)
    # Assert
    mocked_time_decision_making_interval.assert_awaited_once()

@pytest.mark.asyncio
async def test_time_decision_making_interval(mocker):
    # Arrange
    mock_sleep = mocker.patch('asyncio.sleep', new_callable=AsyncMock)
    mock_callback = AsyncMock()
    # To avoid an infinite loop, make the callback raise an exception after it's called once
    async def callback_side_effect():
        mock_callback.call_count += 1
        if mock_callback.call_count > 1:
            raise Exception("Callback called more than once")
    mock_callback.side_effect = callback_side_effect
    # Act & Assert
    with pytest.raises(Exception, match="Callback called more than once"):
        await Scheduler().time_decision_making_interval(interval=1, delay=0.1, bot_callback=mock_callback)
    # Ensure the sleep and callback were called
    mock_sleep.assert_awaited()
    mock_callback.assert_awaited()