from enum import Enum


class TradingTimeFrame(Enum):
    TICK = "tick"  # Representing an immediate transaction or a very short time frame
    MIN_1 = "1"
    MIN_5 = "5"
    MIN_15 = "15"
    HOUR = "60"
    HOUR_4 = "240"
    HOUR_6 = "360"
    DAY = "1440"
    WEEK = "10080"
    MONTH = "43800"  # Approx. 30 days = 43800 minutes (Note: This is an approximation, as months vary in length)