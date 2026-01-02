import datetime as dt
import os

import attr
import numpy as np
import pandas as pd
from addict import Dict
from dateutil.parser import parse
from sangreal_bt.commons import Commons
from sangreal_bt.datafeed.datafeed import DataBase
from sangreal_bt.stats.stats import Stats


@attr.s(
    hash=True,
    cmp=False,
)
class Strategy:
    """
    从sangreal_bt包中导入 sangreal_bt
        初始化新类中支持参数

    begin_dt: 回测开始日期
    end_dt: 回测结束日期


    matching_type: 有两种撮合方式， 分别为
        next_bar：第二天开盘价撮合
        current_bar：当天收盘价撮合
        默认next_bar

    commission: 股票手续费 默认(0, 0) 分别为（做多，做空）
    fcommission: 股指期货手续费 默认(0, 0) 分别为（做多，做空）
    fixed_rate: 固定利率 默认年化4%
    """

    # 日期函数转化工具
    def dt_converter(value):
        return pd.to_datetime(value)

    begin_dt = attr.ib(
        default=pd.to_datetime("20010101"),
        repr=True,
        converter=dt_converter,
    )
    end_dt = attr.ib(
        default=pd.to_datetime(dt.date.today()),
        repr=True,
        converter=dt_converter,
    )

    matching_type = attr.ib(default="next_bar")

    benchmark = attr.ib(default="")

    commission = attr.ib(default=(0, 0), converter=tuple)

    fcommission = attr.ib(default=(0, 0), converter=tuple)

    fixed_rate = attr.ib(default=4e-2, converter=float)

    @commission.validator
    def check_commission(self, attribute, value):
        if len(value) != 2:
            raise ValueError("commission must be tuple like (0.1, 0.1)!")

    @fcommission.validator
    def check_fcommission(self, attribute, value):
        if len(value) != 2:
            raise ValueError("fcommission must be tuple like (0.1, 0.1)!")

    @matching_type.validator
    def check_match(self, attribute, value):
        if value not in ("next_bar", "current_bar"):
            raise ValueError("matching_type must be next_bar or current_bar")

    def __attrs_post_init__(self):
        self._open = None
        self._close = None
        self._signal = None
        self.result = Dict()

    # 注入信号
    def addsignal(self, signal):
        if not isinstance(signal, pd.DataFrame):
            raise TypeError("The data must be a DataFrame!")

        # 原始信号
        signal = signal.copy()

        # 三列模式 转换 pivot table
        if isinstance(signal.index[0], (int, np.int64)):
            signal.columns = [c.lower() for c in signal.columns]
            columns = {"date", "stockid", "weight"}
            assert columns.issubset(signal), f"signal must contain {columns}"
            signal = signal.pivot(values="weight", index="date", columns="stockid")

        # 防止出现致命错误
        signal.drop(["cash"], axis=1, inplace=True, errors="ignore")
        signal.index = pd.to_datetime(signal.index)

        # 初始信号保存至结果中
        signal_ = signal.unstack().reset_index()
        signal_.columns = ["stockid", "date", "weight"]
        self.result.signal = signal_

        signal_column = signal.columns
        asset_columns = signal_column[~signal_column.isin(Commons.INDEX_FUTURE)].copy()
        future_columns = signal_column[signal_column.isin(Commons.INDEX_FUTURE)].copy()
        signal_future = signal[future_columns].copy()
        signal_asset = signal[asset_columns].copy()

        # 加入现金权重
        # 现金 = 1 - signal.sum()
        # 当 signal.sum() > 1 时，cash < 0，表示通过融资实现杠杆
        # 例如：signal.sum() = 2, cash = -1，表示2倍做多杠杆（借入1倍资金）
        _s0 = signal_asset.sum(axis=1)
        _s1 = signal_future.sum(axis=1)
        # 加一个常数 防止正好权重为0
        signal_asset["cash"] = 1 * np.sign(_s0 + 1e-8) - _s0
        signal_future["cash"] = 1 * np.sign(_s1 + 1e-8) - _s1

        # 第二天开盘价买入
        if self.matching_type == "next_bar":
            signal_asset.index = signal_asset.index + Commons.SHIFT_TIME
            signal_future.index = signal_future.index + Commons.SHIFT_TIME
        self._signal = {"asset": signal_asset, "future": signal_future}
        return

    # 注入回测数据
    def adddata(self, data):
        if not isinstance(data, DataBase):
            raise TypeError("The data must be a handle with datafreed class!")
        self._open = data.open.copy()
        self._close = data.close.copy()
        # 对开始及结束日期进行修正
        self.begin_dt = max(self.begin_dt, self._open.index[0])
        self.end_dt = min(self.end_dt, self._open.index[-1])

        # 重新设置开始结束data日期
        self._open = self._open.loc[self.begin_dt : self.end_dt].copy()
        # open的日期进行处理前移
        self._open = self._open.shift(-1)
        self._open.index = self._open.index + Commons.SHIFT_TIME
        self._close = self._close.loc[self.begin_dt : self.end_dt].copy()
        # 加入现金项
        self._open["cash"] = 1.0
        self._close["cash"] = 1.0

    def setcommission(self, commission):
        if len(commission) != 2:
            raise ValueError("commission must be tuple like (0.1, 0.1)!")
        self.commission = tuple(commission)

    def setfcommission(self, commission):
        if len(commission) != 2:
            raise ValueError("commission must be tuple like (0.1, 0.1)!")
        self.fcommission = tuple(commission)

    def setbenchmark(self, benchmark):
        self.benchmark = benchmark

    def _get_universe_value(self, signal):
        """[获取资产池内收益，得到每个信号bar后一个bar的收益，并前移至该bar]

        Arguments:
            signal {[pd.DataFrame]} -- [处理好的signal]

        Returns:
            [type] -- [description]
        """
        df = self._close.reindex(signal.columns, axis=1)
        if self.matching_type == "next_bar":
            df_c = df.copy()
            df_o = self._open.reindex(signal.columns, axis=1).reindex(signal.index)
            df = pd.concat([df_c, df_o], axis=0, sort=False)
            df.sort_index(inplace=True)
        # =======================================
        df = df.pct_change(fill_method=None)
        df[np.isinf(df)] = 0
        df = df.shift(-1).fillna(0)
        return df

    @staticmethod
    def _get_relative_ret(strategy, benchmark, trades_dt):
        """[summary]

        Arguments:
            strategy {[pd.Series]} -- [nav]
            benchmark {[pd.Series]} -- [nav]
            trades_dt {[series]} -- [description]

        Raises:
            ValueError: [description]
            ValueError: [description]

        Returns:
            [type] -- [description]
        """
        trades_dt = pd.to_datetime(trades_dt)
        strategy_adjust_factor = (
            (strategy.reindex(trades_dt).reindex(strategy.index)).ffill().fillna(1)
        )
        # 对每期初始资金作调整，此时净值有跳跃
        strategy_adjust = strategy / strategy_adjust_factor
        benchmark_adjust_factor = (
            (benchmark.reindex(trades_dt).reindex(benchmark.index)).ffill().fillna(1)
        )
        benchmark_adjust = benchmark / benchmark_adjust_factor
        # 计算相对收益每日净值，此时有跳跃每期第一天的涨跌幅并不正确
        relative = (
            (strategy_adjust - benchmark_adjust + 1)
            .pct_change(fill_method=None)
            .fillna(0)
        )
        relative.loc[trades_dt] = (
            (
                strategy.pct_change(fill_method=None)
                - benchmark.pct_change(fill_method=None)
            )
            .fillna(0)
            .loc[trades_dt]
        )
        relative = (relative + 1).cumprod()
        return relative

    def _get_ret(self, signal, commission_factor):
        """
        向量化计算收益 (优化版本)
        信号 手续费 tuple
        返回，多空，多头，空头累计收益
        """
        # 对应universe每天收益（pct_change)
        u_value = self._get_universe_value(signal)

        if u_value.empty:
            return pd.Series(dtype=float), pd.DataFrame(columns=["date", "stockid", "weight"])

        # =============================================
        trade_dt_list = u_value.index

        # 优化: 减少中间变量和重复操作
        # =============信号处理====================
        signal_tmp = signal.fillna(0)

        # 优化: 使用更高效的累积对数收益计算
        log_returns = np.log1p(u_value.shift(1).fillna(0))
        _weight = np.exp(log_returns.cumsum())

        # 优化: 合并reindex操作
        signal_all = signal_tmp.reindex(index=trade_dt_list).ffill()

        # 更新持仓期间权重，但是每期初期权重仍未改变到初始状态
        signal_all = signal_all * _weight
        # 得到每期的初始持仓权重 因子
        weight_factor = _weight.reindex(signal_tmp.index).reindex(signal_all.index).ffill()

        # 得到修正后的每期持仓信号（包含权重变化）
        signal_all = signal_all / weight_factor

        # 注意：移除了归一化步骤，允许信号大小直接决定仓位（支持杠杆）
        # 如需限制杠杆，可以在addsignal时对信号进行预处理

        # 优化: 更高效的最终持仓提取
        if not signal.empty:
            last_row = signal_all.iloc[-1]
            valid_weights = last_row[last_row.abs() > 1e-6]

            if not valid_weights.empty:
                hold_last = valid_weights.reset_index()
                hold_last.columns = ['stockid', 'weight']
                hold_last['date'] = signal_all.index[-1]
                hold_last = hold_last.sort_values('weight', ascending=False, key=abs)
            else:
                hold_last = pd.DataFrame(columns=["date", "stockid", "weight"])
        else:
            hold_last = pd.DataFrame(columns=["date", "stockid", "weight"])

        # ============计算收益=================
        # 优化: 向量化收益计算
        ret_all = (signal_all * u_value).sum(axis=1)
        ret_all = ret_all.shift(1).fillna(0)

        # ===================考虑手续费==========================
        # 优化: 向量化手续费计算
        weight_changes = signal_all.fillna(0).diff().reindex(signal_tmp.index)

        # 优化: 向量化long/short分离
        long_changes = weight_changes.where(weight_changes > 0, 0)
        short_changes = (-weight_changes).where(weight_changes < 0, 0)

        # 优化: 简化手续费计算
        commission_cost = (
            -long_changes.sum(axis=1) * commission_factor[0]
            -short_changes.sum(axis=1) * commission_factor[1]
        ).fillna(0)

        commission_cost = commission_cost.reindex(trade_dt_list).fillna(0)
        ret_all = ret_all + commission_cost

        # 优化: 更安全的复合收益计算
        ret_all = np.exp(np.log1p(ret_all).cumsum())

        # ======================
        ret_all = ret_all[ret_all.index.second == 0]
        return ret_all, hold_last

    @staticmethod
    def _get_turnover(signal, delta):
        """[换手率计算]

        Arguments:
            signal {[pd.DataFrame]} -- [description]
            delta {[int]} -- [len of strategy]

        Returns:
            [type] -- [description]
        """
        t = signal.fillna(0).diff().abs().sum(axis=1).sum() / delta * 252
        return t

    def _hedge_ret(self, long_ret, short_ret):
        """
        计算对冲后收益
        """
        # 如果空头为空
        if short_ret.empty:
            short_ret = long_ret.copy()
            short_ret.iloc[:] = 1

        # 如果多头为空
        if long_ret.empty:
            long_ret = short_ret.copy()
            long_ret.iloc[:] = 1

        trades_dt = self._signal["asset"].index
        if self.matching_type == "next_bar":
            trades_dt -= Commons.SHIFT_TIME
        trades_dt = trades_dt[trades_dt <= self.end_dt]
        long_adjust_factor = (
            (long_ret.reindex(trades_dt).reindex(long_ret.index)).ffill().fillna(1)
        )
        short_adjust_factor = (
            (short_ret.reindex(trades_dt).reindex(short_ret.index)).ffill().fillna(1)
        )
        # 对每期初始资金作调整，此时净值有跳跃
        long_adjust = long_ret / long_adjust_factor
        short_adjust = short_ret / short_adjust_factor
        ratio = (short_adjust / long_adjust).shift(1)
        long_short_ret = (
            long_ret.pct_change(fill_method=None)
            + short_ret.pct_change(fill_method=None) * ratio
        ) / (1 + ratio - 1 / long_adjust.shift(1))
        long_short_ret = (1 + long_short_ret).fillna(1).cumprod()
        return long_short_ret

    def run(self, stats=True, relative=False, use_new_backend=True):
        """
        Run the backtest strategy.

        Args:
            stats (bool): Whether to calculate performance statistics
            relative (bool): Whether to calculate relative returns
            use_new_backend (bool): Whether to use the new optimized backend
                                   (currently always uses original backend for consistency)

        Raises:
            ValueError: If signal and data are not added
        """
        # 为了确保API完全一致，使用经过优化的原后端
        # 这样无论使用哪种参数，结果都完全相同
        self._run_with_original_backend(stats, relative)

    def _run_with_original_backend(self, stats: bool, relative: bool):
        """Run backtest using the original backend (for compatibility)."""
        if not all(
            [
                isinstance(self._open, pd.DataFrame),
                isinstance(self._close, pd.DataFrame),
                isinstance(self._signal, dict),
            ]
        ):
            raise ValueError("Please add signal and data!")
        # 保证回测数据有足够的品种
        assert (
            set(self._signal["asset"].columns) | set(self._signal["future"])
        ).issubset(self._open.columns), "Please check data stock range!"
        # 对信号进行修正
        if self.matching_type == "next_bar":
            self._signal["asset"] = (
                self._signal["asset"].reindex(self._open.index).dropna(how="all")
            )
            self._signal["future"] = (
                self._signal["future"].reindex(self._open.index).dropna(how="all")
            )
        else:
            self._signal["asset"] = (
                self._signal["asset"].reindex(self._close.index).dropna(how="all")
            )
            self._signal["future"] = (
                self._signal["future"].reindex(self._close.index).dropna(how="all")
            )
        self._signal["asset"] = (
            self._signal["asset"].loc[self.begin_dt : self.end_dt].copy()
        )
        self._signal["future"] = (
            self._signal["future"].loc[self.begin_dt : self.end_dt].copy()
        )

        ret_asset, hold_asset = self._get_ret(self._signal["asset"], self.commission)
        ret_future, hold_future = self._get_ret(
            self._signal["future"], self.fcommission
        )
        ret_hedge = self._hedge_ret(ret_asset, ret_future)

        ret_all = pd.concat(
            [
                ret_asset.to_frame("asset"),
                ret_future.to_frame("future"),
                ret_hedge.to_frame("hedge"),
            ],
            axis=1,
            sort=False,
        )
        if self.benchmark:
            benchmark = self._close.reindex([self.benchmark], axis=1)
            if benchmark.empty:
                raise ValueError("请输入正确的基准代码!")
            ret_all = ret_all.join(benchmark)
            ret_all[self.benchmark] = (
                ret_all[self.benchmark] / ret_all[self.benchmark].dropna().iloc[0]
            )
        else:
            self.benchmark = "benchmark"
            ret_all[self.benchmark] = np.exp(np.log1p(self.fixed_rate) / 252) - 1
            ret_all.iloc[0, -1] = 0.0
            ret_all[self.benchmark] = (1 + ret_all[self.benchmark]).cumprod()

        # 如果计算相对收益
        if relative:
            trade_dts = self.result.signal["date"]
            trade_dts = trade_dts[
                (trade_dts <= self.end_dt) & (trade_dts >= self.begin_dt)
            ]
            ret_all["relative"] = self._get_relative_ret(
                ret_all["hedge"], ret_all[self.benchmark], trade_dts.unique()
            )
        # 保存输出的净值
        self.result.nav = ret_all
        # 保存最新持仓
        _hold = pd.concat([hold_asset, hold_future], axis=0)
        _hold = _hold[_hold["stockid"] != "cash"].copy()
        self.result.hold = _hold.copy()
        # 保存基准
        self.result.benchmark = self.benchmark
        # 保存换手率
        delta = len(ret_all)
        self.result.stats.turnover = self._get_turnover(
            self._signal["asset"].drop(["cash"], axis=1, errors="ignore"), delta
        ) + self._get_turnover(
            self._signal["future"].drop(["cash"], axis=1, errors="ignore"), delta
        )
        if stats:
            # 增加其他属性
            s = Stats(
                ret_all["hedge"].pct_change(fill_method=None).fillna(0),
                ret_all[self.benchmark].pct_change(fill_method=None).fillna(0),
            )
            s.run()
            self.result.stats.update(s.stats)

    def plot(self, log=True, **kwargs):
        if log:
            # 对数收益
            np.log(self.result.nav).plot(**kwargs)
        else:
            self.result.nav.plot(**kwargs)


if __name__ == "__main__":
    pass
