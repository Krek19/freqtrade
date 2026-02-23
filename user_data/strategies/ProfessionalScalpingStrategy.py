# --- Do not remove these libs ---
from functools import reduce

import talib.abstract as ta
from pandas import DataFrame

import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.strategy import BooleanParameter, DecimalParameter, IStrategy, IntParameter


# --------------------------------


class ProfessionalScalpingStrategy(IStrategy):
    """
    Professional Scalping Strategy
    """

    INTERFACE_VERSION = 2

    # Stoploss:
    stoploss = -0.10

    # Trailing stop:
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = False

    timeframe = "5m"

    # Hyperparameters
    buy_rsi_trigger = IntParameter(20, 40, default=30, space="buy")
    buy_rsi_cross = IntParameter(20, 40, default=35, space="buy")

    sell_rsi_trigger = IntParameter(65, 80, default=70, space="sell")
    use_rsi_exit = BooleanParameter(default=True, space="sell")

    # Add a DecimalParameter for ROI
    sell_roi = DecimalParameter(0.008, 0.012, default=0.01, decimals=3, space="sell")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = [
            (dataframe["rsi"] < self.buy_rsi_trigger.value),
            qtpylib.crossed_above(dataframe["rsi"], self.buy_rsi_cross.value),
        ]

        dataframe.loc[
            (reduce(lambda x, y: x | y, conditions)) & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []

        if self.use_rsi_exit.value:
            conditions.append(dataframe["rsi"] > self.sell_rsi_trigger.value)

        if conditions:
            dataframe.loc[
                (reduce(lambda x, y: x | y, conditions)) & (dataframe["volume"] > 0),
                "exit_long",
            ] = 1
        return dataframe

    @property
    def minimal_roi(self):
        return {"0": self.sell_roi.value}

    plot_config = {
        "main_plot": {
            "tema": {},
            "sar": {"color": "white"},
        },
        "subplots": {
            "RSI": {
                "rsi": {"color": "red"},
            },
        },
    }
