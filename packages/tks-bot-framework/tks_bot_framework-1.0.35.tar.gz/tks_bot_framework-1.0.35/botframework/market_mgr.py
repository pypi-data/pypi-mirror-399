import httpx
from botframework.cex_proxy import CEXProxy
from datetime import datetime, timedelta
import logging
import asyncio
import websockets
import uuid
import json
import os
import sys

# Ensure the correct event loop policy is used on Windows
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


logger = logging.getLogger('app')


class MarketMgr:
    """Price and Candle Manager"""
    
       
    def get_market_data_service_url_ws(self) -> str:
        return os.getenv("TKS_MARKET_DATA_SERVICE_API_WS", "ws://localhost:8400")
        
    def get_market_data_service_url_http(self) -> str:
        return os.getenv("TKS_MARKET_DATA_SERVICE_API_HTTP", "http://localhost:8400")
    
    async def get_real_time_data(self, markets, callback, reconnect_delay=5):
        if isinstance(markets, str):
            markets = [markets]

        logger.info(f"Subscribing to real-time SSE feed for markets: {markets}")
        markets = [market.upper() for market in markets]

        base_url = self.get_market_data_service_url_http()
        params = {
            "action": "request",
            "watch_type": "real_time",
            "markets": markets  # httpx handles repeated params properly
            # no client_id – will be generated server-side
        }

        url = f"{base_url}/assets/stream/price"

        while True:
            try:
                async with httpx.AsyncClient(timeout=None) as client:
                    async with client.stream("GET", url, params=params) as response:
                        logger.info("SSE connection opened.")
                        async for line in response.aiter_lines():
                            logger.debug(f"Received line: {line}")
                            logger.info(response)
                            if line.startswith("data: "):
                                payload = line.removeprefix("data: ").strip()
                                try:
                                    data = json.loads(payload)
                                    logger.info(data)
                                    await callback(data)
                                except Exception as e:
                                    logger.warning(f"Error in SSE callback: {e} — Payload: {payload}")
            except Exception as e:
                logger.error(f"SSE connection error: {e}")
                logger.info(f"Reconnecting in {reconnect_delay} seconds...")
                await asyncio.sleep(reconnect_delay)

    async def get_last_price(self, market, exchange=None):
        """Returns the last close price from the market and the desired exchange (if specified)."""
        url = f"{self.get_market_data_service_url_http()}/price/{market.upper()}"
        if exchange:
            url += f"?exchange={exchange}"  # Use query parameter for optional 'exchange'
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return data.get('price')
                else:
                    logger.error(f"Failed to fetch last price: HTTP {response.status_code} {response.reason_phrase}")
                    return None
        except httpx.RequestError as exc:
            logger.error(f"Request failed: {exc}")
            return None
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP error occurred: {exc.response.status_code} - {exc.response.text}")
            return None
        except Exception as exc:
            logger.error(f"An unexpected error occurred: {exc}")
            return None
    
    async def get_historical_data(self, exchange, market_symbol, timeframe, limit=1000):
        try:
            cex_proxy = CEXProxy()
            ccxt_exchange = await cex_proxy.get_exchange_proxy(exchange)
            if limit <= 1000:
                since = None
                return await ccxt_exchange.fetch_ohlcv(symbol=market_symbol, timeframe=timeframe, since=since, limit=limit)            
            elif limit > 1000:
                if timeframe=="1m":
                    start_date = datetime.now() - timedelta(hours=limit/60)
                elif timeframe=="5m":
                    start_date = datetime.now() - timedelta(hours=limit/12)
                elif timeframe=="15m":
                    start_date = datetime.now() - timedelta(hours=limit/4)
                elif timeframe=="1h":
                    start_date = datetime.now() - timedelta(hours=limit)
                elif timeframe=="4h":
                    start_date = datetime.now() - timedelta(hours=limit*4)
                elif timeframe=="6h":
                    start_date = datetime.now() - timedelta(hours=limit*6)
                elif timeframe=="1d":
                    start_date = datetime.now() - timedelta(hours=limit*24)
                elif timeframe=="1w":
                    start_date = datetime.now() - timedelta(hours=limit*24*7)
                else:
                    raise Exception(f"Unsupported timeframe: {timeframe}")
                start_date = str(start_date.replace(minute=0, second=0, microsecond=0))
                start_date_parsed = ccxt_exchange.parse8601(start_date)
                ohlcv = await ccxt_exchange.fetch_ohlcv(symbol=market_symbol, timeframe=timeframe, since=start_date_parsed, limit=limit)  
                # Adjust start_date if ohlcv is empty and retry.
                while not ohlcv:
                    logger.info(f"No data found for {market_symbol} at timestamp {start_date_parsed}. Adjusting start date...")
                    if timeframe == "1m":
                        step_hours = 500 / 60
                    elif timeframe == "5m":
                        step_hours = 500 / 12
                    elif timeframe == "15m":
                        step_hours = 500 / 4
                    elif timeframe == "1h":
                        step_hours = 500
                    elif timeframe == "4h":
                        step_hours = 500 * 4
                    elif timeframe == "6h":
                        step_hours = 500 * 6
                    elif timeframe == "1d":
                        step_hours = 500 * 24
                    elif timeframe == "1w":
                        step_hours = 500 * 24 * 7
                    else:
                        raise Exception(f"Unsupported timeframe: {timeframe}")
                    start_date_parsed += int(step_hours * 3600000)
                    ohlcv = await ccxt_exchange.fetch_ohlcv(symbol=market_symbol, timeframe=timeframe, since=start_date_parsed, limit=1000)
                while True:
                    start_date_parsed = ohlcv[-1][0]
                    new_ohlcv = await ccxt_exchange.fetch_ohlcv(symbol=market_symbol, timeframe=timeframe, since=start_date_parsed, limit=limit)  
                    new_ohlcv.pop(0)
                    new_ohlcv
                    ohlcv.extend(new_ohlcv)
                    await asyncio.sleep(0.25)
                    if len(new_ohlcv) != (1000 - 1):
                        break
                return ohlcv
        except Exception as ex:
            await ccxt_exchange.close()
            raise Exception(f"Failed to fetch historical OHLCV data. {ex}")
        finally:
            await ccxt_exchange.close()  
    
    async def get_meta_market_indicator_data(self, callback):
        url = f"{self.get_market_data_service_url_ws()}/tv/meta_market_indicator"
        try:
            async with websockets.connect(url) as websocket:
                while True:  # Loop to keep connection open
                    response = await websocket.recv()
                    data = json.loads(response)
                    logger.info(f"Processing incoming Meta Market Indicator data: {data}")
                    await callback(data)
                    # Handle data here rather than returning immediately
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
 
        

