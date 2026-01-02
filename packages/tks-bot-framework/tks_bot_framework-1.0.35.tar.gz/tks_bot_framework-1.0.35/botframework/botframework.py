import os
from tksessentials import global_logger
from botframework.portfolio_mgr import PortfolioMgr
from botframework.trade_mgr import TradeMgr
from botframework.market_mgr import MarketMgr
from botframework.scheduler import Scheduler
from botframework.strategy import Strategy
from famodels.direction import Direction
from tksessentials import utils, database
from datetime import datetime
import asyncio
import platform
import sys

# CAUTION: Only the main file should create this custom loger. The others should retrieve it. logging.getLogger('root')
logger = global_logger.setup_custom_logger('app')


class Botframework:

    def __init__(self):
        pass
    
    async def start_framework(self, initial_tasks, asyncio_tasks, ksqldb_query_url, view_names_trade):
        """Start all the service tasks, which run in the background."""
        strategy = Strategy()
        strategy_id = strategy.get_name()
        logger.info(f"Starting {strategy_id}.")
        market_mgr = MarketMgr()
        logger.info(f"Using market data service, http: {market_mgr.get_market_data_service_url_http()}")
        logger.info(f"Using market data service, ws: {market_mgr.get_market_data_service_url_ws()}")      
        # # Wait for the entry to start the signal decision making interval.
        # logger.info(f"Waiting for the full hour to start the bot.")
        # now = datetime.now()
        # seconds_to_wait = 60 - now.second - now.microsecond / 1_000_000
        # await asyncio.sleep(seconds_to_wait)
        pfm = PortfolioMgr() 
        trade_mgr = TradeMgr()
        # Load bot configurations.
        algo_id = utils.get_application_name()
        logger.info(f"The {algo_id} bot is loading configurations.")
        # Start bot.
        logger.critical(f"Bot {algo_id} is starting in {utils.get_environment()} mode.")
        # TODO send usage reports to TKS: python, sys version, location?
        #EmailMgr().send_email(EmailContext.TRADING, recipient_email, f"Bot {app_cfg['bot_id']} is starting.", "Nothing more to say :-).")  
        # Report System and Python Version.
        logger.info(f"System: {sys.version}")
        logger.info(f"Python: {platform.python_version()}")
        # Check on the trading platform config.
        #logger.info(f"Any trading activity will be reported to endpoint {utils.get_trading_platform_endpoint()}")  
        # Report position capacities of the bot.
        app_cfg = utils.get_app_config()
        market_list = app_cfg.get("market_list", [])
        for market in market_list:
            exchange = app_cfg.get("exchange")
            base_asset = market.split('/')[0]  # Extracts "BTC" from "BTC/USDT"
            logger.info(f"The {utils.get_application_name()} is configured and is starting for {market} on {exchange}.")
            # Log position capacities for each market.
            logger.info(f"There are {len(pfm.get_position_capacities(base_asset))} positions for {market}.")
            # for pos in pfm.get_directional_position_capacities(base_asset, Direction.LONG):
            #     logger.info(f"{market} LONG position: {pos}")
            # for pos in pfm.get_directional_position_capacities(base_asset, Direction.SHORT):
            #     logger.info(f"{market} SHORT position: {pos}") 
        # Execute the initial tasks sequentially.
        for initial_task in initial_tasks:
            await initial_task()
        logger.info("All initial tasks completed.")
        # Report currently active trades. 
        for market in market_list:
            base_asset = market.split('/')[0].lower()  # Extract BTC or SOL as lowercase
            view_name = view_names_trade.get(base_asset)
            if not view_name:
                logger.warning(f"No view name found for market {market}. Skipping.")
                continue
            active_positions_long = await trade_mgr.get_active_positions(ksqldb_query_url, view_name, Direction.LONG)
            active_positions_short = await trade_mgr.get_active_positions(ksqldb_query_url, view_name, Direction.SHORT)
            logger.info(f"There are currently {len(active_positions_long)} {Direction.LONG} trades for {market}.")
            logger.info(f"There are currently {len(active_positions_short)} {Direction.SHORT} trades for {market}.")
            if active_positions_long:
                logger.info(f"The active long trades for {market} are: {active_positions_long}")
            if active_positions_short:
                logger.info(f"The active short trades for {market} are: {active_positions_short}")
        # Launch all tasks concurrently.
        scheduler = Scheduler()
        tasks = []
        for interval, delay, callback in asyncio_tasks:
            if interval is None:
                tasks.append(scheduler.start_task(delay, callback))
            else:
                tasks.append(scheduler.start_interval(interval, delay, callback))
        # Use asyncio.gather to run all tasks concurrently.
        await asyncio.gather(*tasks)

    async def execute_with_retries(self, sql_task, retries=20, delay=20):
        for attempt in range(retries):
            try:
                await sql_task()  # Execute the task directly
                return
            except Exception as e:
                logger.info(f"Failed to execute SQL statement (attempt {attempt + 1}): {e}")
                if attempt < retries - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
        raise Exception(f"Failed to execute SQL after {retries} attempts: {sql_task}")
