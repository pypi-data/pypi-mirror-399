from abc import abstractmethod

import pandas as pd

from ..core import Strategy


class BaseMLStrategy(Strategy):
    """
    Base class for Machine Learning based strategies.

    Provides a structured way to separate data preparation,
    model training, and signal generation.
    """

    def __init__(self, model=None):
        super().__init__()
        self.model = model
        self.is_trained = False

    @abstractmethod
    def train(self, data: pd.DataFrame):
        """
        User-defined training logic.

        Args:
            data: Historical data for training.
        """
        pass

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Standard signal generation using the trained model.

        Args:
            data: Market data for prediction/trading.
        """
        pass
