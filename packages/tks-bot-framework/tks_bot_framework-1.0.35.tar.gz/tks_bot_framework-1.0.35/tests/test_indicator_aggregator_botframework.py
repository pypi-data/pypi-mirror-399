import pytest
import pandas as pd
from pandas import to_datetime
from botframework.indicator_aggregator_botframework import IndicatorAggregatorBotframework
from pathlib import Path
import yaml
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
import pytz
import numpy as np

pd.options.mode.chained_assignment = None  # default='warn'

def load_mock_ohlcv_data():
    # Load test data from the yaml file
    path = Path(__file__).parent.parent.absolute().joinpath("tests/test_data.yaml")
    with open(path, 'r') as stream:
        try:
            test_data_dict = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            raise
    return test_data_dict['test_data_1h']

@pytest.fixture
def mock_data():
    return load_mock_ohlcv_data()

@pytest.mark.asyncio
async def test_get_data_frame(mock_data):
    # Arrange.
    with patch('botframework.market_mgr.MarketMgr.get_historical_data', new_callable=AsyncMock) as mock_get_historical_data, \
         patch('botframework.indicator_aggregator_botframework.IndicatorAggregatorBotframework.process_closed_bar_data_frame', new_callable=AsyncMock) as mock_process_closed_bar, \
         patch('botframework.indicator_aggregator_botframework.IndicatorAggregatorBotframework.check_intra_bar_data_frame', new_callable=AsyncMock) as mock_check_intra_bar, \
         patch('botframework.indicator_aggregator_botframework.IndicatorAggregatorBotframework.check_for_inconsistencies', new_callable=AsyncMock) as mock_check_inconsistencies:
        mock_get_historical_data.return_value = mock_data
        your_class_instance = IndicatorAggregatorBotframework()
        # Act.
        await your_class_instance.get_data_frame("exchange", "market_symbol", "timeframe", 100, "closed_bar")
        await your_class_instance.get_data_frame("exchange", "market_symbol", "timeframe", 100, "intra_bar")
        # Assert.
        mock_get_historical_data.assert_awaited_with(exchange="exchange", market_symbol="market_symbol", timeframe="timeframe", limit=100)
        mock_process_closed_bar.assert_awaited_once()
        mock_check_intra_bar.assert_awaited_once()
        assert mock_check_inconsistencies.await_count == 2

# Fixture to create a mock DataFrame
@pytest.fixture
def mock_df():
    # This function will be overridden in the test function for specific timeframes
    pass

# Fixture to mock datetime.now
@pytest.fixture
def mock_datetime_now():
    fixed_datetime = datetime(2020, 1, 1, 4, 0, 0, tzinfo=pytz.UTC)
    with patch('botframework.indicator_aggregator_botframework.datetime') as mock_datetime:
        mock_datetime.now.return_value = fixed_datetime
        yield

@pytest.mark.asyncio
@pytest.mark.parametrize("timeframe, freq, delta, end_date_attr", [
    ('1m', 'T', timedelta(minutes=1), 'end_date_MIN_1'),
    ('5m', '5T', timedelta(minutes=5), 'end_date_MIN_5'),
    ('15m', '15T', timedelta(minutes=15), 'end_date_MIN_15'),
    ('1h', 'H', timedelta(hours=1), 'end_date_HOUR'),
    ('4h', '4H', timedelta(hours=4), 'end_date_HOUR_4'),
    ('6h', '6H', timedelta(hours=6), 'end_date_HOUR_6'),
    ('1d', 'D', timedelta(days=1), 'end_date_DAY'),
])
async def test_process_closed_bar_data_frame_without_dropping(mock_datetime_now, timeframe, freq, delta, end_date_attr):
    # This test simulates a scenario where the last row does NOT have to be dropped since it is one "delta" behind the current time.
    # Arrange.
    instance = IndicatorAggregatorBotframework()
    await instance.update_time_variables()
    end_date = getattr(instance, end_date_attr)
    timestamps = pd.date_range(start='2020-01-01', periods=4, freq=freq)  # Generate timestamps without including the end_date
    data = {'timestamp': timestamps, 'value': range(4)}
    mock_df = pd.DataFrame(data)
    # Append a row with timestamp one delta behind the end_date
    last_row_timestamp = pd.to_datetime(end_date, utc=True) - delta
    mock_df = pd.concat([mock_df, pd.DataFrame({'timestamp': [last_row_timestamp], 'value': [4]})], ignore_index=True)
    # The expected last row timestamp should be the same as the appended row since it's not equal to end_date
    expected_last_row_timestamp = last_row_timestamp
    # Act
    result_df = await instance.process_closed_bar_data_frame(mock_df, timeframe)
    # Assert
    assert len(result_df) == len(mock_df)  # The last row should not be dropped
    # Assert that the last row's timestamp matches the expected timestamp
    actual_last_row_timestamp = result_df.iloc[-1]['timestamp']
    assert actual_last_row_timestamp == expected_last_row_timestamp
    
@pytest.mark.asyncio
@pytest.mark.parametrize("timeframe, freq, delta, end_date_attr", [
    ('1m', 'T', timedelta(minutes=1), 'end_date_MIN_1'),
    ('5m', '5T', timedelta(minutes=5), 'end_date_MIN_5'),
    ('15m', '15T', timedelta(minutes=15), 'end_date_MIN_15'),
    ('1h', 'H', timedelta(hours=1), 'end_date_HOUR'),
    ('4h', '4H', timedelta(hours=4), 'end_date_HOUR_4'),
    ('6h', '6H', timedelta(hours=6), 'end_date_HOUR_6'),
    ('1d', 'D', timedelta(days=1), 'end_date_DAY'),
])
async def test_process_closed_bar_data_frame_with_dropping(mock_datetime_now, timeframe, freq, delta, end_date_attr):
    # This test simulates a scenario where the last row has to be dropped since it corresponds with the actual time.
    # Arrange
    instance = IndicatorAggregatorBotframework()
    await instance.update_time_variables()
    end_date = getattr(instance, end_date_attr)
    timestamps = pd.date_range(start='2020-01-01', periods=4, freq=freq, tz='UTC')
    data = {'timestamp': timestamps, 'value': range(4)}
    mock_df = pd.DataFrame(data)
    # Append the end_date row
    last_row_df = pd.DataFrame({'timestamp': [pd.to_datetime(end_date, utc=True)], 'value': [4]})
    mock_df = pd.concat([mock_df, last_row_df], ignore_index=True)
    # The expected last row timestamp should be the last timestamp before appending the end_date row
    expected_last_row_timestamp = timestamps[-1]
    # Act
    result_df = await instance.process_closed_bar_data_frame(mock_df, timeframe)
    # Assert that the last row was dropped
    assert len(result_df) == len(mock_df) - 1
    # Assert that the new last row's timestamp matches the expected timestamp
    actual_last_row_timestamp = result_df.iloc[-1]['timestamp']
    assert actual_last_row_timestamp == expected_last_row_timestamp

# Mock botframework_utils functions
@pytest.fixture
def mock_botframework_utils():
    # Patch for tksessentials.utils.get_app_config to control the inconsistency_tolerance
    app_config_patch = patch('tksessentials.utils.get_app_config', return_value={'inconsistency_tolerance': 2})
    # Patch botframework_utils functions as before
    get_timedelta_patch = patch('botframework.botframework_utils.get_timedelta')
    resample_patch = patch('botframework.botframework_utils.resample')
    with app_config_patch, get_timedelta_patch as mock_get_timedelta, resample_patch as mock_resample:
        # Mock get_timedelta to return a timedelta corresponding to each time frame
        def get_timedelta_side_effect(timeframe):
            unit_mapping = {
                '1m': 'T',
                '5m': 'T',
                '15m': 'T',
                '1h': 'H', 
                '4h': 'H',
                '6h': 'H',
                '1d': 'D'  
            }
            unit = unit_mapping.get(timeframe[-1], 'T')  # Default to 'T' if unit not found
            value = int(timeframe[:-1])  # Extracting the numerical part
            return pd.Timedelta(value=value, unit=unit)
        mock_get_timedelta.side_effect = get_timedelta_side_effect
        # Mock resample to return the frequency string corresponding to each time frame
        def resample_side_effect(timeframe):
            return timeframe  # Assuming this function converts timeframe to a pandas frequency string
        mock_resample.side_effect = resample_side_effect
        yield

@pytest.mark.asyncio
@pytest.mark.parametrize("timeframe", ['1m', '5m', '15m', '1h', '4h', '6h', '1d'])
async def test_check_for_inconsistencies(mock_botframework_utils, timeframe):
    # Arrange
    timestamps = pd.date_range(start='2020-01-01', periods=10, freq=timeframe)
    data = {'timestamp': timestamps, 'value': range(10)}
    df = pd.DataFrame(data)
    # Introduce inconsistencies by dropping some rows
    inconsistent_df = df.drop(index=[3, 7])
    instance = IndicatorAggregatorBotframework()
    # Act
    result_df = await instance.check_for_inconsistencies(inconsistent_df, timeframe)
    # Assert
    assert len(result_df) == len(df) 
    assert not result_df['timestamp'].isnull().any()  
    assert not result_df['value'].isnull().any()  