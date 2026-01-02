"""
Vector backtesting framework for quantitative strategies.
"""

# Core functionality
from .strategy.strategy import Strategy
from .datafeed.datafeed import DataPandas, DataBase
from .stats.stats import Stats

__version__ = "0.0.34"

__all__ = [
    'Strategy', 'DataPandas', 'DataBase', 'Stats',
]
