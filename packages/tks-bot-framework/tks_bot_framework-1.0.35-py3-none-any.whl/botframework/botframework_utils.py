import logging
from pathlib import Path
import yaml
import sys
import pandas as pd
import json
import time
import httpx
from aiokafka import AIOKafkaProducer
from datetime import datetime, timezone
import asyncio
from fasignalprovider.trading_signal import TradingSignal
from pydantic import BaseModel, Field
from typing import Optional
from tksessentials import database


logger = logging.getLogger('app')

def get_project_root() -> str:    
    str_path = str(Path(__file__).parent.parent)
    return str_path

def get_project_root_path() -> Path:    
    abs_path = Path(__file__).parent.parent.absolute()
    return abs_path

def get_log_path() -> Path:
    log_path = Path.cwd().absolute()
    return log_path

def get_app_config() -> dict:
    algo_cfg = {}
    with open(Path.cwd().absolute().joinpath("config/app_config.yaml"), "r") as ymlfile:
        try:
            algo_cfg = yaml.safe_load(ymlfile)
        except yaml.YAMLError as ex:
            logger.critical(f"Failed to load the app_config.yaml file. Aborting the application. Error: {ex}")
            sys.exit(1)  
    return algo_cfg

YAML_TO_CCXT_TIMEFRAME_MAPPING = {
    "TICK": "1m",
    "MIN_1": "1m",
    "MIN_5": "5m",
    "MIN_15": "15m",
    "HOUR": "1h",
    "HOUR_4": "4h",
    "HOUR_6": "6h",
    "DAY": "1d",
    "WEEK": "1w",
    "MONTH": "1M",
}

def get_ccxt_timeframe(yaml_timeframe):
    try:
        return YAML_TO_CCXT_TIMEFRAME_MAPPING[yaml_timeframe]
    except KeyError:
        raise ValueError(f"'{yaml_timeframe}' is not a recognized timeframe in the configuration.")
    
YAML_TO_TRADING_TIMEFRAME_MAPPING = {
    "TICK": "1", 
    "MIN_1": "1",
    "MIN_5": "5",
    "MIN_15": "15",
    "HOUR": "60",
    "HOUR_4": "240",
    "HOUR_6": "360",
    "DAY": "1440",
    "WEEK": "10080",
    "MONTH": "43800",
}

def get_trading_timeframe(yaml_timeframe):
    try:
        return YAML_TO_TRADING_TIMEFRAME_MAPPING[yaml_timeframe]
    except KeyError:
        raise ValueError(f"'{yaml_timeframe}' is not a recognized timeframe in the configuration.")

STRING_TO_TIMDELTA_MAPPING = {
    "1m": pd.Timedelta(minutes=1),
    "5m": pd.Timedelta(minutes=5),
    "15m": pd.Timedelta(minutes=15),
    "1h": pd.Timedelta(hours=1),
    "4h": pd.Timedelta(hours=4),
    "6h": pd.Timedelta(hours=6),
    "1d": pd.Timedelta(days=1),
}

def get_timedelta(time_string):
    try:
        return STRING_TO_TIMDELTA_MAPPING[time_string]
    except KeyError:
        raise ValueError(f"'{time_string}' is not a recognized timeframe in the configuration.")
    
STRING_TO_RESAMPLE_MAPPING = {
    "1m": '1T',
    "5m": '5T',
    "15m": '15T',
    "1h": '1H',
    "4h": '4H',
    "6h": '6H',
    "1d": '1D',
}

def resample(time_string):
    try:
        return STRING_TO_RESAMPLE_MAPPING[time_string]
    except KeyError:
        raise ValueError(f"'{time_string}' is not a recognized timeframe in the configuration.")

def get_rnn_config() -> dict:
    rnn_cfg = {}
    with open(Path.cwd().absolute().joinpath("config/rnn_config.yaml"), "r") as ymlfile:
        try:
            rnn_cfg = yaml.safe_load(ymlfile)
        except yaml.YAMLError as ex:
            logger.critical(f"Failed to load the algo_config.yaml file. Aborting the application. Error: {ex}")
            sys.exit(1)  
    return rnn_cfg

def get_mean() -> pd.Series:
    with open('storage/train_mean.json', 'r') as file:
        loaded_mean = json.load(file)
        train_mean = pd.Series(loaded_mean)
    
    return train_mean
    
def get_std() -> pd.Series:
    with open('storage/train_std.json', 'r') as file:
        loaded_std = json.load(file)
        train_std = pd.Series(loaded_std)

    return train_std

async def execute_pull_query(ksqldb_query_url, view_name, select_columns='*', where_clause='', offset_reset="earliest", callback=None):
    """
    Checks first if the table is available, returns None if not.
    Returns an empty list [] if no message meets the query criteria.
    Otherwise, returns a list with the matching messages.
    
    """
    # Check if the table or view exists.
    if not database.table_or_view_exists(view_name):
        logger.error(f"Table or view {view_name} does not exist.")
        return None
    
    results = []
    if isinstance(select_columns, list):
        select_columns = ', '.join(select_columns)
    
    where_clause = f"WHERE {where_clause}" if where_clause else ""
    
    pull_query = f"""
    SELECT {select_columns} FROM {view_name} {where_clause};
    """
    # logger.info(f"Executing pull query: {pull_query}")
    
    async with httpx.AsyncClient(http2=True) as client:
        response = await client.post(ksqldb_query_url, json={
            "sql": pull_query,
            "streamsProperties": {
                "ksql.streams.auto.offset.reset": offset_reset
            },
            "properties": {}
        }, timeout=60.0)
        
        # logger.info(f"Pull query response status: {response.status_code}")
        
        if response.status_code == 200:
            metadata_received = False
            schema_info = None
            
            async for message in response.aiter_text():
                if not message.strip():
                    continue
                try:
                    for line in message.splitlines():
                        if not metadata_received:
                            result = json.loads(line)
                            if 'queryId' in result:
                                # logger.info("Received query metadata: %s", result)
                                schema_info = result
                                metadata_received = True
                            continue
                        data_row = json.loads(line)
                        results.append(data_row)
                except json.JSONDecodeError:
                    logger.warning("Received non-JSON message: %s", message)
                    if message.startswith('{"queryId":'):
                        error_data = json.loads(message)
                        logger.error("Error data received: %s", error_data)
                        schema_info = error_data
            
            # logger.info("Final schema information: %s", schema_info)
            if callback and results:
                logger.info("Calling callback with results")
                await callback(results)
        else:
            logger.error("Failed to execute query: %s", response.status_code)
            logger.error(response.json())

    return results

async def execute_push_query(ksqldb_query_url, stream_name, select_columns='*', offset_reset="earliest", callback=None):
    """
    Executes a push query on the specified KSQLDB stream.

    Args:
        ksqldb_query_url (str): The URL of the KSQLDB query endpoint.
        stream_name (str): The name of the KSQLDB stream to query.
        offset_reset (str): The offset reset policy ("earliest" or "latest").
        callback (callable): A callback function to process each message.
    """
    push_query = f"SELECT {select_columns} FROM {stream_name} EMIT CHANGES;"
    logger.info(f"Starting to run Continuous/Push Query: {push_query}")

    headers = {
        "Content-Type": "application/vnd.ksql.v1+json"
    }
    body = {
        "sql": push_query,
        "streamsProperties": {
            "ksql.streams.auto.offset.reset": offset_reset
        }
    }
    async with httpx.AsyncClient(http2=True) as client:
        while True:
            try:
                logger.debug("Sending push query request...")
                async with client.stream("POST", ksqldb_query_url, headers=headers, json=body, timeout=None) as response:
                    logger.info(f"HTTP Version: {response.http_version}")
                    logger.info(f"Response Status: {response.status_code}")
                    logger.info(f"Response Headers: {response.headers}")

                    if response.status_code == 200:
                        async for message in response.aiter_text():
                            if message.strip():
                                try:
                                    result = json.loads(message)
                                    logger.info("Query result: %s", result)
                                    if callback:
                                        await callback(result)
                                except json.JSONDecodeError:
                                    logger.warning("Received non-JSON message: %s", message)
                            else:
                                logger.debug("Received empty message")
                    else:
                        logger.error(f"Failed to execute query: {response.status_code}")
                        logger.error(response.json())
            except Exception as e:
                logger.error(f"Exception occurred: {e}")
                logger.info("Retrying push query in 20 seconds...")
                await asyncio.sleep(20)  # Wait for 20 seconds before retrying
            await asyncio.sleep(1)  # Avoid tight loop in case of error


##### TRADING PLATFORM CONNECTION SETTINGS ######


# def get_trading_platform() -> dict:
#     return get_app_config()["services"]["trading-platform"]
# def get_trading_platform_host() -> str:
#     return get_trading_platform()["host"]
# def get_trading_platform_protocol() -> str:
#     return get_trading_platform()["protocol"]
# def get_trading_platform_endpoint() -> str:
#     """Delievrs the full endpoint address for the POST method."""
#     return f"{get_trading_platform_protocol()}://{get_trading_platform_host()}/signal"

###### PARSING ######
def parse_quote(market:str) -> str:
    """Returns the quote of a market: e.g. send BTC-USD and receive USD."""
    seperator = "-" if "-" in market else "/"            
    return market.split(seperator)[1]

def parse_base(market:str) -> str:
    """Returns the quote of a market: e.g. send BTC-USD and receive BTC."""
    seperator = "-" if "-" in market else "/"            
    return market.split(seperator)[0]

def format_symbol_w_hyphen(market:str) -> str:
    """Returns the market with a hyphen in between."""
    return market.replace("/", "-")

def format_symbol_w_slash(market:str) -> str:
    """Returns the market with a slash in between."""
    return market.replace("-", "/")

def is_same_market(market_1:str, market_2:str) -> bool:
    return True if format_symbol_w_hyphen(market_1) == format_symbol_w_hyphen(market_2) else False