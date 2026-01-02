"""
Enhanced statistics and performance analysis module for backtesting framework.
"""
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
import empyrical as ep
from addict import Dict

# Drawdown threshold constant
DRAWDOWN_THRESHOLD = 0.02  # 2% default threshold for drawdown reporting

class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass


class DrawdownAnalyzer:
    """Specialized class for drawdown analysis."""

    @staticmethod
    def calculate_max_drawdown_dates(cumulative_returns: pd.Series) -> str:
        """
        Calculate maximum drawdown start and end dates.

        Args:
            cumulative_returns: Cumulative returns series

        Returns:
            String representation of begin and end dates (YYYYMMDDYYYYMMDD)
        """
        if cumulative_returns.empty:
            return ""

        running_max = cumulative_returns.cummax()
        drawdown = cumulative_returns / running_max - 1.0

        end_date = drawdown.idxmin()
        begin_idx = cumulative_returns.tolist().index(running_max[end_date])
        begin_date = cumulative_returns.index[begin_idx]

        return f"{begin_date.strftime('%Y%m%d')}{end_date.strftime('%Y%m%d')}"

    @classmethod
    def get_drawdown_periods(cls, cumulative_returns: pd.Series,
                           threshold: float = DRAWDOWN_THRESHOLD) -> pd.DataFrame:
        """
        Get all drawdown periods exceeding threshold.

        Args:
            cumulative_returns: Cumulative returns series
            threshold: Minimum drawdown threshold (default 2%)

        Returns:
            DataFrame with drawdown periods
        """
        if cumulative_returns.empty:
            return pd.DataFrame(columns=['begin_dt', 'end_dt', 'ratio', 'datelen'])

        # Calculate drawdown identifiers over time
        drawdown_ids = pd.Series(index=cumulative_returns.index)
        for date in drawdown_ids.index:
            drawdown_ids.loc[date] = cls.calculate_max_drawdown_dates(
                cumulative_returns.loc[:date]
            )

        # Find points where drawdown period changes
        change_dates = drawdown_ids[drawdown_ids.diff().shift(-1) >= 100000000].index

        # Collect all drawdown periods
        period_ids = [int(drawdown_ids.loc[date]) for date in change_dates]
        period_ids.append(int(drawdown_ids.iloc[-1]))

        # Convert to detailed format
        drawdown_periods = []
        for period_id in period_ids:
            if len(str(period_id)) >= 16:
                begin_str = str(period_id)[:8]
                end_str = str(period_id)[8:16]

                begin_date = pd.to_datetime(begin_str)
                end_date = pd.to_datetime(end_str)

                if begin_date in cumulative_returns.index and end_date in cumulative_returns.index:
                    ratio = cumulative_returns.loc[end_date] / cumulative_returns.loc[begin_date] - 1

                    if ratio < -threshold:
                        drawdown_periods.append({
                            'begin_dt': begin_str,
                            'end_dt': end_str,
                            'ratio': ratio,
                            'datelen': (end_date - begin_date).days
                        })

        if not drawdown_periods:
            return pd.DataFrame(columns=['begin_dt', 'end_dt', 'ratio', 'datelen'])

        result_df = pd.DataFrame(drawdown_periods)
        result_df = result_df.sort_values('ratio', ascending=True)  # Worst drawdowns first

        return result_df


class PerformanceStats:
    """Enhanced performance statistics calculator."""

    def __init__(self, strategy_returns: pd.Series, benchmark_returns: Optional[pd.Series] = None):
        """
        Initialize performance statistics.

        Args:
            strategy_returns: Strategy daily returns (pct_change)
            benchmark_returns: Optional benchmark daily returns
        """
        self.strategy_returns = strategy_returns.copy()
        self.benchmark_returns = benchmark_returns.copy() if benchmark_returns is not None else None

        # Validate and prepare data
        self._validate_and_prepare_data()

        # Initialize stats container
        self.stats = Dict()

    def _validate_and_prepare_data(self):
        """Validate and prepare return data."""
        if self.strategy_returns.empty:
            raise ValidationError("Strategy returns cannot be empty")

        # Ensure datetime index
        self.strategy_returns.index = pd.to_datetime(self.strategy_returns.index)

        if self.benchmark_returns is not None:
            self.benchmark_returns.index = pd.to_datetime(self.benchmark_returns.index)

            # Align strategy and benchmark returns
            aligned_data = pd.concat([self.strategy_returns, self.benchmark_returns], axis=1).dropna()
            if not aligned_data.empty:
                self.strategy_returns = aligned_data.iloc[:, 0]
                self.benchmark_returns = aligned_data.iloc[:, 1]

    def calculate_basic_stats(self):
        """Calculate basic performance statistics."""
        # Return statistics
        self.stats.annual_return = ep.annual_return(self.strategy_returns)
        self.stats.annual_volatility = ep.annual_volatility(self.strategy_returns)
        self.stats.sharpe_ratio = ep.sharpe_ratio(self.strategy_returns)

        # Cumulative returns
        cumulative_returns = (self.strategy_returns.fillna(0) + 1).cumprod()
        self.stats.total_return = cumulative_returns.iloc[-1] - 1
        self.stats.cumulative_returns = cumulative_returns

    def calculate_drawdown_stats(self):
        """Calculate drawdown-related statistics."""
        # Maximum drawdown
        self.stats.max_drawdown = ep.max_drawdown(self.strategy_returns)

        # Detailed drawdown periods
        cumulative_returns = (self.strategy_returns.fillna(0) + 1).cumprod()
        drawdown_analyzer = DrawdownAnalyzer()
        self.stats.max_drawdown_list = drawdown_analyzer.get_drawdown_periods(cumulative_returns)

        # Drawdown duration
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max

        # Current drawdown
        self.stats.current_drawdown = drawdown.iloc[-1] if not drawdown.empty else 0

        # Average drawdown
        drawdown_periods = drawdown[drawdown < 0]
        self.stats.avg_drawdown = drawdown_periods.mean() if not drawdown_periods.empty else 0

    def calculate_benchmark_stats(self):
        """Calculate benchmark-relative statistics."""
        if self.benchmark_returns is None:
            return

        # Relative performance
        self.stats.excess_return = ep.alpha(self.strategy_returns, self.benchmark_returns)
        self.stats.excess_volatility = ep.annual_volatility(
            self.strategy_returns - self.benchmark_returns
        )
        self.stats.information_ratio = ep.excess_sharpe(
            self.strategy_returns, self.benchmark_returns) * np.sqrt(252)

        # Beta and tracking error
        self.stats.beta = ep.beta(self.strategy_returns, self.benchmark_returns)
        self.stats.tracking_error = ep.annual_volatility(
            self.strategy_returns - self.benchmark_returns)

    def calculate_risk_stats(self):
        """Calculate additional risk statistics."""
        # Value at Risk
        self.stats.var_95 = self.strategy_returns.quantile(0.05)
        self.stats.var_99 = self.strategy_returns.quantile(0.01)

        # Conditional Value at Risk (Expected Shortfall)
        self.stats.cvar_95 = self.strategy_returns[
            self.strategy_returns <= self.stats.var_95
        ].mean()
        self.stats.cvar_99 = self.strategy_returns[
            self.strategy_returns <= self.stats.var_99
        ].mean()

        # Skewness and kurtosis
        self.stats.skewness = self.strategy_returns.skew()
        self.stats.kurtosis = self.strategy_returns.kurtosis()

        # Downside deviation
        negative_returns = self.strategy_returns[self.strategy_returns < 0]
        self.stats.downside_deviation = negative_returns.std() * np.sqrt(252) if not negative_returns.empty else 0

        # Calmar ratio (annual return / max drawdown)
        if self.stats.max_drawdown != 0:
            self.stats.calmar_ratio = self.stats.annual_return / abs(self.stats.max_drawdown)
        else:
            self.stats.calmar_ratio = np.inf if self.stats.annual_return > 0 else 0

    def calculate_rolling_stats(self, window: int = 252):
        """Calculate rolling statistics."""
        if len(self.strategy_returns) < window:
            return

        rolling = pd.DataFrame(index=self.strategy_returns.index)

        # Rolling Sharpe ratio
        rolling_sharpe = self.strategy_returns.rolling(window).apply(
            lambda x: ep.sharpe_ratio(x.dropna()), raw=False
        )
        rolling['rolling_sharpe'] = rolling_sharpe

        # Rolling volatility
        rolling['rolling_volatility'] = self.strategy_returns.rolling(window).std() * np.sqrt(252)

        # Rolling maximum drawdown
        rolling_cumulative = (1 + self.strategy_returns).rolling(window).apply(
            lambda x: (1 + x).cumprod().iloc[-1], raw=False
        )
        rolling_max = rolling_cumulative.rolling(window).max()
        rolling_drawdown = (rolling_cumulative - rolling_max) / rolling_max
        rolling['rolling_max_drawdown'] = rolling_drawdown.rolling(window).min()

        self.stats.rolling_stats = rolling.dropna()

    def calculate_all_stats(self, include_rolling: bool = True, rolling_window: int = 252):
        """
        Calculate all performance statistics.

        Args:
            include_rolling: Whether to include rolling statistics
            rolling_window: Window size for rolling statistics
        """
        self.calculate_basic_stats()
        self.calculate_drawdown_stats()
        self.calculate_benchmark_stats()
        self.calculate_risk_stats()

        if include_rolling:
            self.calculate_rolling_stats(rolling_window)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of key statistics.

        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'Total Return': f"{self.stats.total_return:.2%}",
            'Annual Return': f"{self.stats.annual_return:.2%}",
            'Annual Volatility': f"{self.stats.annual_volatility:.2%}",
            'Sharpe Ratio': f"{self.stats.sharpe_ratio:.3f}",
            'Maximum Drawdown': f"{self.stats.max_drawdown:.2%}",
            'Current Drawdown': f"{self.stats.current_drawdown:.2%}",
        }

        if hasattr(self.stats, 'beta'):
            summary['Beta'] = f"{self.stats.beta:.3f}"
            summary['Information Ratio'] = f"{self.stats.information_ratio:.3f}"
            summary['Tracking Error'] = f"{self.stats.tracking_error:.2%}"

        if hasattr(self.stats, 'calmar_ratio'):
            if np.isfinite(self.stats.calmar_ratio):
                summary['Calmar Ratio'] = f"{self.stats.calmar_ratio:.3f}"
            else:
                summary['Calmar Ratio'] = "∞" if self.stats.calmar_ratio > 0 else "-∞"

        return summary


# Backward compatibility
class Stats(PerformanceStats):
    """
    Backward compatible Stats class.

    This class maintains the original interface while providing enhanced functionality.
    """

    def __init__(self, sret, bret):
        """
        Initialize with original interface.

        Args:
            sret: Strategy returns (pct_change format)
            bret: Benchmark returns (pct_change format)
        """
        super().__init__(sret, bret)

    def run(self):
        """Run statistics calculation (original interface)."""
        self.calculate_all_stats(include_rolling=False)
