"""
Data handling module for backtesting framework.
"""
from abc import ABC, abstractmethod
from typing import Optional, Union, Dict, Any
import pandas as pd
import numpy as np

class DataError(Exception):
    """Exception raised for data-related errors."""
    pass

# Constants for index futures
INDEX_FUTURES = (
    "IH", "IF", "IC", "IM",  # 股指期货
    "TS", "TF", "T", "TL",   # 国债期货
)

# Time shift for next bar matching
MATCHING_TIME_SHIFT = pd.Timedelta(seconds=1)


class IDataProvider(ABC):
    """Abstract interface for data providers."""

    @abstractmethod
    def get_price_data(self, symbols: list, start_date: pd.Timestamp,
                      end_date: pd.Timestamp) -> Dict[str, pd.DataFrame]:
        """Get price data for given symbols and date range."""
        pass


class BaseDataProvider(IDataProvider):
    """Base class for data providers."""

    REQUIRED_COLUMNS = {'date', 'stockid', 'open', 'close'}
    CASH_SYMBOL = 'cash'

    def __init__(self):
        self.open: Optional[pd.DataFrame] = None
        self.close: Optional[pd.DataFrame] = None
        self._validate_data_integrity()

    def _validate_data_integrity(self):
        """Validate data integrity after initialization."""
        if self.open is not None and self.close is not None:
            if not self.open.index.equals(self.close.index):
                raise DataError("Open and close data must have the same index")
            if not self.open.columns.equals(self.close.columns):
                raise DataError("Open and close data must have the same columns")

    @property
    def symbols(self) -> list:
        """Get list of available symbols."""
        return list(self.open.columns) if self.open is not None else []

    @property
    def date_range(self) -> tuple:
        """Get date range of the data."""
        if self.open is None:
            return None, None
        return self.open.index[0], self.open.index[-1]

    def add_cash_asset(self):
        """Add cash asset to price data."""
        if self.open is not None:
            self.open[self.CASH_SYMBOL] = 1.0
            self.close[self.CASH_SYMBOL] = 1.0

    def adjust_for_matching_type(self, matching_type: str):
        """Adjust data based on matching type."""
        if matching_type == "next_bar":
            if self.open is not None:
                self.open = self.open.shift(-1)
                self.open.index = self.open.index + MATCHING_TIME_SHIFT

    def filter_date_range(self, start_date: pd.Timestamp, end_date: pd.Timestamp):
        """Filter data to specified date range."""
        if self.open is not None:
            mask = (self.open.index >= start_date) & (self.open.index <= end_date)
            self.open = self.open.loc[mask]
            self.close = self.close.loc[mask]

    def is_future_symbol(self, symbol: str) -> bool:
        """Check if symbol is a future contract."""
        return symbol in INDEX_FUTURES

    def split_assets_by_type(self) -> Dict[str, list]:
        """Split symbols into asset types."""
        assets = {'asset': [], 'future': []}
        for symbol in self.symbols:
            if symbol == self.CASH_SYMBOL:
                continue
            if self.is_future_symbol(symbol):
                assets['future'].append(symbol)
            else:
                assets['asset'].append(symbol)
        return assets


class PandasDataProvider(BaseDataProvider):
    """Data provider that works with pandas DataFrames."""

    def __init__(self, data: pd.DataFrame):
        """
        Initialize with DataFrame containing price data.

        Args:
            data: DataFrame with columns ['date', 'stockid', 'open', 'close']
        """
        super().__init__()
        self._validate_input_data(data)
        self._process_data(data)

    def _validate_input_data(self, data: pd.DataFrame):
        """Validate input data format."""
        if not isinstance(data, pd.DataFrame):
            raise DataError("Input data must be a pandas DataFrame")

        data_columns = set(data.columns.str.lower())
        required = self.REQUIRED_COLUMNS

        if not required.issubset(data_columns):
            missing = required - data_columns
            raise DataError(f"Data must contain columns: {missing}")

        if data.empty:
            raise DataError("Input data cannot be empty")

    def _process_data(self, data: pd.DataFrame):
        """Process raw data into open/close price matrices."""
        data = data.copy()
        data.columns = [col.lower() for col in data.columns]

        # Standardize column names
        column_mapping = {
            'date': 'trade_dt',
            'stockid': 'sid'
        }
        data.rename(columns=column_mapping, inplace=True)

        # Convert dates
        data['trade_dt'] = pd.to_datetime(data['trade_dt'])

        # Check for duplicate data
        duplicates = data.duplicated(subset=['trade_dt', 'sid'])
        if duplicates.any():
            raise DataError("Duplicate data found. Please remove duplicates.")

        # Pivot to get price matrices
        try:
            self.open = data.pivot(
                values='open',
                index='trade_dt',
                columns='sid'
            )
            self.close = data.pivot(
                values='close',
                index='trade_dt',
                columns='sid'
            )
        except Exception as e:
            raise DataError(f"Failed to pivot data: {str(e)}")

        self._validate_data_integrity()

    def get_price_data(self, symbols: list, start_date: pd.Timestamp,
                      end_date: pd.Timestamp) -> Dict[str, pd.DataFrame]:
        """Get price data for specific symbols and date range."""
        if self.open is None or self.close is None:
            raise DataError("No data available")

        available_symbols = set(self.symbols)
        requested_symbols = set(symbols)
        missing_symbols = requested_symbols - available_symbols

        if missing_symbols:
            raise DataError(f"Symbols not found: {missing_symbols}")

        # Filter date range
        date_mask = (self.open.index >= start_date) & (self.open.index <= end_date)

        return {
            'open': self.open.loc[date_mask, symbols],
            'close': self.close.loc[date_mask, symbols]
        }


# Backward compatibility aliases
DataBase = BaseDataProvider
DataPandas = PandasDataProvider
