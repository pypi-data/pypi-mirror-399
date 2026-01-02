from botframework.market_mgr import MarketMgr
from botframework import botframework_utils
from tksessentials import utils
from datetime import datetime, timedelta
import pandas as pd
import logging
import pytz

logger = logging.getLogger('app')


class IndicatorAggregatorBotframework:

    def __init__(self):    
        self.timeframe_configs = []

    async def update_time_variables(self):
        utc_now = datetime.now(pytz.UTC)
        self.utc_without_seconds = utc_now.replace(second=0, microsecond=0)
        self.end_date_MIN_1 = self.utc_without_seconds
        self.minute_adjustement_MIN_5 = utc_now.minute % 5
        self.end_date_MIN_5 = self.utc_without_seconds - timedelta(minutes=self.minute_adjustement_MIN_5)
        self.minute_adjustement_MIN_15 = utc_now.minute % 15
        self.end_date_MIN_15 = self.utc_without_seconds - timedelta(minutes=self.minute_adjustement_MIN_15)
        self.utc_without_minutes = utc_now.replace(minute=0, second=0, microsecond=0)
        self.end_date_HOUR = self.utc_without_minutes
        self.hour_adjustement_HOUR_4 = utc_now.hour % 4
        self.end_date_HOUR_4 = self.utc_without_minutes - timedelta(hours=self.hour_adjustement_HOUR_4)
        self.hour_adjustement_HOUR_6 = utc_now.hour % 6
        self.end_date_HOUR_6 = self.utc_without_minutes - timedelta(hours=self.hour_adjustement_HOUR_6)
        self.utc_without_hours = utc_now.replace(hour=0, minute=0, second=0, microsecond=0)
        self.end_date_DAY = self.utc_without_hours

    async def get_data_frame(self, exchange, market_symbol, timeframe, limit, status):
        market_mgr = MarketMgr()
        df = await market_mgr.get_historical_data(exchange=exchange, market_symbol=market_symbol, timeframe=timeframe, limit=limit)
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        df = pd.DataFrame(df)
        df.columns = ["timestamp", "open", "high", "low", "close", "volume"]
        df["timestamp"] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize('UTC')
        print(df.tail())
        if status=="closed_bar":
            df = await self.process_closed_bar_data_frame(df, timeframe)
        elif status=="intra_bar":
            await self.check_intra_bar_data_frame(df, timeframe)
        print(df.tail())
        df = await self.check_for_inconsistencies(df, timeframe)

        return df

    async def process_closed_bar_data_frame(self, df, timeframe):
        await self.update_time_variables()
        # Drop the last row of the data frame if incomplete. 
        # Check if the timestamp of the last row is as expected.
        last_row_timestamp = df.iloc[-1]['timestamp']
        if timeframe=='1m':
            if last_row_timestamp == self.end_date_MIN_1:
                df = df[:-1]
            else:
                pass
            delta = self.end_date_MIN_1 - timedelta(minutes=1)
            last_row_timestamp = df.iloc[-1]['timestamp']
            if last_row_timestamp==delta:
                pass
            else:
                logger.fatal(f"Could not create data frame.")
        elif timeframe=='5m':
            if last_row_timestamp == self.end_date_MIN_5:
                df = df[:-1]
            else:
                pass
            delta = self.end_date_MIN_5 - timedelta(minutes=5)
            last_row_timestamp = df.iloc[-1]['timestamp']
            if last_row_timestamp==delta:
                    pass
            else:
                logger.fatal(f"Could not create data frame.")
        elif timeframe=='15m':
            if last_row_timestamp == self.end_date_MIN_15:
                df = df[:-1]
            else:
                pass
            delta = self.end_date_MIN_15 - timedelta(minutes=15)
            last_row_timestamp = df.iloc[-1]['timestamp']
            if last_row_timestamp==delta:
                    pass
            else:
                logger.fatal(f"Could not create data frame.")
        elif timeframe=='1h':
            if last_row_timestamp == self.end_date_HOUR:
                df = df[:-1]
            else:
                pass
            delta = self.end_date_HOUR - timedelta(hours=1)
            last_row_timestamp = df.iloc[-1]['timestamp']
            if last_row_timestamp==delta:
                    pass
            else:
                logger.fatal(f"Could not create data frame.")            
        elif timeframe=='4h':
            if last_row_timestamp == self.end_date_HOUR_4:
                df = df[:-1]
            else:
                pass
            delta = self.end_date_HOUR_4 - timedelta(hours=4)
            last_row_timestamp = df.iloc[-1]['timestamp']
            if last_row_timestamp==delta:
                    pass
            else:
                logger.fatal(f"Could not create data frame.")
        elif timeframe=='6h':
            if last_row_timestamp == self.end_date_HOUR_6:
                df = df[:-1]
            else:
                pass
            delta = self.end_date_HOUR_6 - timedelta(hours=6)
            last_row_timestamp = df.iloc[-1]['timestamp']
            if last_row_timestamp==delta:
                    pass
            else:
                logger.fatal(f"Could not create data frame.")
        elif timeframe=='1d':
            if last_row_timestamp == self.end_date_DAY:
                df = df[:-1]
            else:
                pass
            delta = self.end_date_DAY - timedelta(days=1)
            last_row_timestamp = df.iloc[-1]['timestamp']
            if last_row_timestamp==delta:
                    pass
            else:
                logger.fatal(f"Could not create data frame.")

        return df
    
    async def check_intra_bar_data_frame(self, df, timeframe):
        await self.update_time_variables()
        #Check if the timestamp of the last row is as expected.
        last_row_timestamp = df.iloc[-1]['timestamp']
        if timeframe=='1m':
            if last_row_timestamp==self.end_date_MIN_1:
                pass
            else:
                logger.fatal(f"Could not create data frame.")
        elif timeframe=='5m':
            if last_row_timestamp==self.end_date_MIN_5:
                pass
            else:
                logger.fatal(f"Could not create data frame.")
        elif timeframe=='15m':
            if last_row_timestamp==self.end_date_MIN_15:
                pass
            else:
                logger.fatal(f"Could not create data frame.")
        elif timeframe=='1h':
            if last_row_timestamp==self.end_date_HOUR:
                    pass
            else:
                logger.fatal(f"Could not create data frame.")     
        elif timeframe=='4h':
            if last_row_timestamp ==self.end_date_HOUR_4:
                    pass
            else:
                logger.fatal(f"Could not create data frame.")
        elif timeframe=='6h':
            if last_row_timestamp ==self.end_date_HOUR_6:
                    pass
            else:
                logger.fatal(f"Could not create data frame.")
        elif timeframe=='1d':
            if last_row_timestamp ==self.end_date_DAY:
                    pass
            else:
                logger.fatal(f"Could not create data frame.")

    async def check_for_inconsistencies(self, df, timeframe):
        # Check if there are more inconsistencies than accepted.
        app_cfg = utils.get_app_config()
        inconsistency_tolerance = app_cfg['inconsistency_tolerance']
        df_inconsistencies = df.copy()
        df_inconsistencies['diff'] = df_inconsistencies['timestamp'].diff()
        expected_diff = botframework_utils.get_timedelta(timeframe)
        inconsistencies = df_inconsistencies[df_inconsistencies['diff'] != expected_diff]
        if len(inconsistencies) > inconsistency_tolerance:
            logger.critical(f"More than accepted inconsistencies in the time frame. Investigate!")
        else:
            pass
        # There will be at least 1 inconsistency, since the first row of the data frame does not have a previous row to compare to.
        if len(inconsistencies) > 1:
            df.set_index('timestamp', inplace=True)
            resample_freq = botframework_utils.resample(timeframe)
            df = df.resample(resample_freq).ffill()
            df.reset_index(inplace=True)
            len_inconsistencies = len(inconsistencies) - 1
            logger.info(f"{len_inconsistencies} inconsistencies forward filled in the time frame.")
        else:
            logger.info(f"No inconsistencies in the time frame.")
        logger.info(f"Time frame created.")

        return df