from botframework import botframework_utils
from tksessentials import utils


class Strategy:
    def __init__(self):
        """Represents the strategy of trading bot, thus the Algorithm."""
        pass

    def get_name(self) -> str:
        """Returns the name of the strategy, consumed from the config file."""
        name = utils.get_application_name()

        return name

    def get_default_timeframe(self) -> str:
        """Returns the main timeframe this strategy employs to invoke trading signals. Caution: the algorithm could still be invoke trades within the timeframe."""
        timeframe_configs = botframework_utils.extract_timeframe_config()
        main_timeframe_enum = timeframe_configs[0][2]
        main_interval = int(main_timeframe_enum.value)

        return main_interval

    # async def invoke_signal(self, trading_signal: TradingSignal):
    #     raise NotImplementedError("Every Strategy must have this method.")        
    
    def is_hot(self) -> bool:
        raise NotImplementedError("Indicate if this strategy is currently hot. (All Signals are marked arccordingly.)")

    # def get_trading_markets(self) -> set(str):
    #     raise NotImplementedError("Return the set of markets this strategy is trading. Return in .")
    