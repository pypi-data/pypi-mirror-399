from botframework import botframework_utils
from botframework.botframework_utils import execute_pull_query
from botframework.botframework_utils import execute_push_query
import unittest
from unittest.mock import MagicMock, AsyncMock, patch, ANY
import pytest
from pathlib import Path
import yaml
import pandas as pd
import asyncio
import httpx
import json

class TestExecutePullQuery(unittest.IsolatedAsyncioTestCase):

    @patch('botframework_utils.database.table_or_view_exists')
    @patch('botframework_utils.httpx.AsyncClient.post')
    async def test_execute_pull_query_success(self, mock_post, mock_table_or_view_exists):
        # Set up the mocks
        mock_table_or_view_exists.return_value = True

        # Mock the response object and its aiter_text method
        mock_response = AsyncMock()
        mock_response.status_code = 200
        
        async def mock_aiter_text():
            messages = [
                '{"queryId": "test-query-id"}\n',
                '{"columnNames":["col1", "col2"],"row":{"columns":["val1","val2"]}}\n'
            ]
            for msg in messages:
                yield msg
        
        mock_response.aiter_text = mock_aiter_text
        mock_post.return_value = mock_response

        # Define the input parameters
        ksqldb_query_url = 'http://mock-ksqldb-url'
        view_name = 'mock_view'
        select_columns = ['col1', 'col2']
        where_clause = 'col1 = \'value\''
        offset_reset = 'earliest'

        # Call the function
        results = await execute_pull_query(
            ksqldb_query_url, view_name, select_columns, where_clause, offset_reset
        )

        # Verify the results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], {"columnNames":["col1", "col2"], "row":{"columns":["val1","val2"]}})

    @patch('tksessentials.database.table_or_view_exists')
    @patch('botframework_utils.httpx.AsyncClient.post')
    async def test_execute_pull_query_no_table(self, mock_post, mock_table_or_view_exists):
        # Set up the mocks
        mock_table_or_view_exists.return_value = False

        # Define the input parameters
        ksqldb_query_url = 'http://mock-ksqldb-url'
        view_name = 'non_existent_view'
        select_columns = '*'
        where_clause = ''
        offset_reset = 'earliest'

        # Call the function
        results = await botframework_utils.execute_pull_query(
            ksqldb_query_url, view_name, select_columns, where_clause, offset_reset
        )

        # Verify the results
        self.assertIsNone(results)
        mock_post.assert_not_called()

    @patch('tksessentials.database.table_or_view_exists')
    @patch('botframework_utils.httpx.AsyncClient.post')
    async def test_execute_pull_query_error_response(self, mock_post, mock_table_or_view_exists):
        # Set up the mocks
        mock_table_or_view_exists.return_value = True
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.json = AsyncMock(return_value={"error_code": 500, "message": "Internal server error"})
        mock_post.return_value = mock_response

        # Define the input parameters
        ksqldb_query_url = 'http://mock-ksqldb-url'
        view_name = 'mock_view'
        select_columns = '*'
        where_clause = ''
        offset_reset = 'earliest'

        # Call the function
        results = await botframework_utils.execute_pull_query(
            ksqldb_query_url, view_name, select_columns, where_clause, offset_reset
        )

        # Verify the results
        self.assertEqual(results, [])
        mock_post.assert_called_once()

@pytest.mark.parametrize("input_timeframe, expected_output", [
    ("TICK", "1m"),
    ("MIN_1", "1m"),
    ("MIN_5", "5m"),
    ("MIN_15", "15m"),
    ("HOUR", "1h"),
    ("HOUR_4", "4h"),
    ("HOUR_6", "6h"),
    ("DAY", "1d"),
    ("WEEK", "1w"),
    ("MONTH", "1M"),
])
def test_get_ccxt_timeframe_valid(input_timeframe, expected_output):
    # Arrange, act and assert.
    assert botframework_utils.get_ccxt_timeframe(input_timeframe) == expected_output, f"CCXT timeframe for '{input_timeframe}' should be '{expected_output}'"

@pytest.mark.parametrize("invalid_timeframe", [
    "SECOND",
    "YEAR",
    "MIN_30",
])
def test_get_ccxt_timeframe_invalid(invalid_timeframe):
    # Arrange, act and assert.
    with pytest.raises(ValueError) as excinfo:
        botframework_utils.get_ccxt_timeframe(invalid_timeframe)
    assert f"'{invalid_timeframe}' is not a recognized timeframe in the configuration." in str(excinfo.value), f"Invalid timeframe '{invalid_timeframe}' should raise a ValueError"

@pytest.mark.parametrize("time_string, expected_timedelta", [
    ("1m", pd.Timedelta(minutes=1)),
    ("5m", pd.Timedelta(minutes=5)),
    ("15m", pd.Timedelta(minutes=15)),
    ("1h", pd.Timedelta(hours=1)),
    ("4h", pd.Timedelta(hours=4)),
    ("6h", pd.Timedelta(hours=6)),
    ("1d", pd.Timedelta(days=1)),
])
def test_get_timedelta_valid(time_string, expected_timedelta):
    # Arrange, act and assert.
    assert botframework_utils.get_timedelta(time_string) == expected_timedelta, f"Timedelta for '{time_string}' should be '{expected_timedelta}'"

@pytest.mark.parametrize("invalid_time_string", [
    "30s",
    "2d",
    "10y",
])
def test_get_timedelta_invalid(invalid_time_string):
    # Arrange, act and assert.
    with pytest.raises(ValueError) as excinfo:
        botframework_utils.get_timedelta(invalid_time_string)
    assert f"'{invalid_time_string}' is not a recognized timeframe in the configuration." in str(excinfo.value), f"Invalid time string '{invalid_time_string}' should raise a ValueError"

@pytest.mark.parametrize("time_string, expected_frequency", [
    ("1m", '1T'),
    ("5m", '5T'),
    ("15m", '15T'),
    ("1h", '1H'),
    ("4h", '4H'),
    ("6h", '6H'),
    ("1d", '1D'),
])
def test_resample_valid(time_string, expected_frequency):
    # Arrange, act and assert.
    assert botframework_utils.resample(time_string) == expected_frequency, f"Resample frequency for '{time_string}' should be '{expected_frequency}'"

@pytest.mark.parametrize("invalid_time_string", [
    "2m",
    "3h",
    "2d",
])
def test_resample_invalid(invalid_time_string):
    # Arrange, act and assert.
    with pytest.raises(ValueError) as excinfo:
        botframework_utils.resample(invalid_time_string)
    assert f"'{invalid_time_string}' is not a recognized timeframe in the configuration." in str(excinfo.value), f"Invalid time string '{invalid_time_string}' should raise a ValueError"

def test_parse_quote():
    assert botframework_utils.parse_quote('ETH-USD') == 'USD'
    assert botframework_utils.parse_quote('ETH/USD') == 'USD'

def test_parse_base():
    assert botframework_utils.parse_base('ETH-USD') == 'ETH'
    assert botframework_utils.parse_base('ETH/USD') == 'ETH'

def test_format_symbol_w_hyphen():
    assert botframework_utils.format_symbol_w_hyphen('ETH/USD') == 'ETH-USD'
    with pytest.raises(AssertionError):
        assert botframework_utils.format_symbol_w_hyphen('ETH/USD') == 'ETH/USD'

def test_format_symbol_w_slash():
    assert botframework_utils.format_symbol_w_slash('ETH-USD') == 'ETH/USD'
    with pytest.raises(AssertionError):
        assert botframework_utils.format_symbol_w_slash('ETH-USD') == 'ETH/USDT'

def test_is_same_market():    
    assert botframework_utils.is_same_market("BTC/USD", "BTC-USD") == True
    assert botframework_utils.is_same_market("BTC/USD", "BTC-USDT") == False
    assert botframework_utils.is_same_market("ETH/USD", "BTC-USD") == False

# @pytest.mark.asyncio
# @patch('botframework.botframework_utils.httpx.AsyncClient.post')
# async def test_execute_pull_query(mock_post):
#     # Arrange.
#     mock_response = AsyncMock()
#     mock_response.status_code = 200
#     async def mock_aiter_text():
#         yield '{"queryId":"query_1"}\n'
#         yield '{"row_1":"value_1"}\n'
#         yield '{"row_2":"value_2"}\n'
#     mock_response.aiter_text = mock_aiter_text
#     mock_post.return_value = mock_response
#     mock_ksqldb_query_url = "http://mock-ksqldb-server:8088/query"
#     view_name = "mock_view"
#     select_columns = "*"
#     where_clause = ""
#     offset_reset = "earliest"
#     # Act.
#     results = await execute_pull_query(mock_ksqldb_query_url, view_name, select_columns, where_clause, offset_reset)
#     # Assert.
#     assert mock_post.called
#     assert results == [{"row_1": "value_1"}, {"row_2": "value_2"}]

# @pytest.mark.asyncio
# @patch('botframework.botframework_utils.httpx.AsyncClient.post')
# async def test_execute_pull_query_failure(mock_post):
#     # Arrange.
#     mock_response = AsyncMock()
#     mock_response.status_code = 400
#     mock_response.json.return_value = {"error_message": "some error"}
#     mock_post.return_value = mock_response
#     mock_ksqldb_query_url = "http://mock-ksqldb-server:8088/query"
#     view_name = "mock_view"
#     select_columns = "*"
#     where_clause = ""
#     offset_reset = "earliest"
#     # Act.
#     results = await execute_pull_query(mock_ksqldb_query_url, view_name, select_columns, where_clause, offset_reset)
#     # Assert.
#     assert mock_post.called
#     assert results == []

@pytest.mark.asyncio
@patch('botframework.botframework_utils.httpx.AsyncClient.stream')
async def test_execute_push_query(mock_stream):
    # Arrange.
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.http_version = "2"
    mock_response.headers = {"Content-Type": "application/vnd.ksql.v1+json"}
    async def mock_aiter_text():
        yield '{"row_1":"value_1"}\n'
        yield '{"row_2":"value_2"}\n'
    mock_response.aiter_text = mock_aiter_text
    mock_stream.return_value.__aenter__.return_value = mock_response
    mock_ksqldb_query_url = "http://mock-ksqldb-server:8088/query"
    stream_name = "mock_stream"
    select_columns = "*"
    offset_reset = "earliest"
    async def mock_callback(result):
        results.append(result)
    results = []
    # Act.
    task = asyncio.create_task(execute_push_query(mock_ksqldb_query_url, stream_name, select_columns, offset_reset, mock_callback))
    await asyncio.sleep(0.1)
    task.cancel()
    # Assert.
    assert mock_stream.called
    assert results == [{"row_1": "value_1"}, {"row_2": "value_2"}]

@pytest.mark.asyncio
@patch('botframework.botframework_utils.httpx.AsyncClient.stream')
async def test_execute_push_query_failure(mock_stream):
    # Arrange.
    mock_response = AsyncMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"error_message": "some error"}
    mock_stream.return_value.__aenter__.return_value = mock_response
    mock_ksqldb_query_url = "http://mock-ksqldb-server:8088/query"
    stream_name = "mock_stream"
    select_columns = "*"
    offset_reset = "earliest"
    async def mock_callback(result):
        results.append(result)
    results = []
    # Act.
    task = asyncio.create_task(execute_push_query(mock_ksqldb_query_url, stream_name, select_columns, offset_reset, mock_callback))
    await asyncio.sleep(0.1)
    task.cancel()
    # Assert.
    assert mock_stream.called
    assert results == []