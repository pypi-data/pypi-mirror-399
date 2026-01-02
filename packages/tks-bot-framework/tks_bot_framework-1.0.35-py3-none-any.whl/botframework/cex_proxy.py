from logging import Logger
import logging
import sys
import ccxt.async_support as ccxt 
import logging

logger = logging.getLogger('app')
ccxt_logger = logging.getLogger('ccxt')


class CEXProxy:

    def __init__(self):
        pass

    async def get_exchange_proxy(self, exchange: str) -> ccxt.Exchange:
        """Returns the cex exchange proxy."""
        try:
            ccxt_exchange = get_exchange(exchange)
            ccxt_exchange.verbose = False  # or True if you want the HTTP log
            ccxt_exchange.enableRateLimit = True
            ccxt_exchange.logger = ccxt_logger  # Ensure ccxt_logger is defined
        except KeyError as ke:
            error_msg = f"Failed to to open high-liquidity exchange connection with the connection keys: {ke}"
            Logger.critical(error_msg)
            sys.exit()       
        except Exception as ex:
            error_msg = f"Failed to to open high-liquidity exchange connection: {ex}"
            Logger.critical(error_msg)
            sys.exit()
            #raise Exception(error_msg)
        return ccxt_exchange

def get_exchange(exchange: str) -> ccxt.Exchange:
    """Dynamically gets and instantiates an exchange class from ccxt."""
    # Convert the exchange name to lowercase to match ccxt's convention
    exchange_name = exchange.lower()

    # Dynamically get the exchange class from ccxt
    exchange_class = getattr(ccxt, exchange_name, None)

    if exchange_class:
        # Instantiate the exchange
        return exchange_class({'enableRateLimit': True})
    else:
        raise ValueError(f"Exchange {exchange_name} is not supported by ccxt.")
