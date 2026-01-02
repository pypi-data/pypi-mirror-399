import asyncio
import logging
from datetime import datetime

logger = logging.getLogger('app')


class Scheduler:

    def __init__(self):
        pass

    async def start_task(self, delay, bot_callback):
        while True:
            utc_now = datetime.utcnow()
            if utc_now.minute==0 and utc_now.second==0:
                if delay == None:
                    pass
                else:
                    await asyncio.sleep(delay*60)
                await bot_callback()                
                break

    async def start_interval(self, interval, delay, bot_callback):
        while True:
            utc_now = datetime.utcnow()
            if utc_now.minute==0 and utc_now.second==0:
                await self.time_decision_making_interval(interval, delay, bot_callback)
                break

    async def time_decision_making_interval(self, interval, delay, bot_callback):
        # If delay is specified, sleep for the delay duration once before starting the loop
        if delay is not None:
            await asyncio.sleep(delay * 60)
        while True:
            await bot_callback()
            utc_now = datetime.utcnow()
            # Calculate the sleep time based on the interval with millisecond precision
            if interval == 1:
                # Calculate remaining time to the next full minute
                sleep_time = interval * 60 - (utc_now.second + utc_now.microsecond / 1_000_000)
            elif interval in [5, 15]:
                # Calculate time since the last interval and sleep until the next one
                current_minute = utc_now.minute
                time_since_last_interval = current_minute % interval
                sleep_time = (interval - time_since_last_interval) * 60 - (utc_now.second + utc_now.microsecond / 1_000_000)
            else:
                # Default sleep calculation for other intervals
                total_seconds = utc_now.minute * 60 + utc_now.second + utc_now.microsecond / 1_000_000
                sleep_time = interval * 60 - total_seconds
            # Avoid sleeping a negative duration
            if sleep_time > 0:
                # Calculate days, hours, minutes, seconds, milliseconds
                days, rem = divmod(sleep_time, 86400)  # 86400 seconds in a day
                hours, rem = divmod(rem, 3600)  # 3600 seconds in an hour
                minutes, rem = divmod(rem, 60)  # 60 seconds in a minute
                seconds = int(rem)
                milliseconds = int((rem - seconds) * 1000)
                # Construct the log message based on the duration
                if days > 0:
                    logger.info(f"Waiting for {days} days, {hours} hours, {minutes} minutes, {seconds} seconds, {milliseconds} milliseconds until next calculations in interval...")
                elif hours > 0:
                    logger.info(f"Waiting for {hours} hours, {minutes} minutes, {seconds} seconds, {milliseconds} milliseconds until next calculations in interval...")
                elif minutes > 0:
                    logger.info(f"Waiting for {minutes} minutes, {seconds} seconds, {milliseconds} milliseconds until next calculations in interval...")
                else:
                    logger.info(f"Waiting for {seconds} seconds, {milliseconds} milliseconds until next calculations in interval...")
                await asyncio.sleep(sleep_time)