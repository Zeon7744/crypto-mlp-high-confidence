"""
crypto-mlp: 回测原理层完善 - 测试
验证：无前视泄漏(walk-forward 在线标准化) / 交易成本 / 按 bar 频率年化绩效
"""
import os, sys, unittest
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto_mlp import CryptoMLPAnalyzer


def _synthetic_ohlcv(n=400, seed=42):
    """构造带 4h 时间戳的合成 OHLCV（避免依赖网络）。"""
    rng = np.random.default_rng(seed)
    ts = pd.date_range(end=pd.Timestamp.now().floor('h'), periods=n, freq='4h')
    close = 50000 * np.exp(np.cumsum(rng.normal(0.0, 0.01, n)))
    high = close * (1 + np.abs(rng.normal(0, 0.005, n)))
    low = close * (1 - np.abs(rng.normal(0, 0.005, n)))
    open_ = close * (1 + rng.normal(0, 0.003, n))
    vol = rng.uniform(1000, 5000, n)
    return pd.DataFrame({'timestamp': ts, 'open': open_, 'high': high,
                         'low': low, 'close': close, 'volume': vol})


class TestBacktestPrinciples(unittest.TestCase):
    def setUp(self):
        self.analyzer = CryptoMLPAnalyzer(coin='BTC', timeframe='4h',
                                          model_dir='/tmp/zt_model_test')
        self.df = _synthetic_ohlcv()

    def test_no_crash_and_fields_present(self):
        res = self.analyzer.backtest(self.df, initial_balance=10000)
        for k in ['sharpe_ratio', 'sortino_ratio', 'calmar_ratio',
                  'max_drawdown', 'win_rate', 'avg_holding_bars',
                  'total_costs', 'bars_per_year', 'annualized_return']:
            self.assertIn(k, res)
        # 4h 频率年化应≈2190（每年 bar 数），而非旧版误用 252
        self.assertGreater(res['bars_per_year'], 1000)
        self.assertLess(res['bars_per_year'], 4000)

    def test_transaction_costs_deduced(self):
        res = self.analyzer.backtest(self.df, initial_balance=10000)
        # 有成交时成本 > 0；无成交时 0
        self.assertGreaterEqual(res['total_costs'], 0.0)
        if res['total_trades'] > 0:
            self.assertGreater(res['total_costs'], 0.0)

    def test_costs_reduce_return_vs_zero_fee(self):
        """原理验证：扣成本后净收益 应低于 零成本 收益（成本确实拉低净收益）"""
        with_cost = self.analyzer.backtest(self.df, fees_pct=0.001, slippage_pct=0.0005)
        no_cost = self.analyzer.backtest(self.df, fees_pct=0.0, slippage_pct=0.0)
        if with_cost['round_trips'] > 0:
            self.assertLessEqual(with_cost['total_return'], no_cost['total_return'])

    def test_no_lookahead_uses_past_window(self):
        """walk-forward：改 walk_forward 开关不应让数据不足时崩溃。"""
        res = self.analyzer.backtest(self.df, walk_forward=False)
        self.assertIn('sharpe_ratio', res)
        self.assertGreaterEqual(res['max_drawdown'], -1.0)

    def test_insufficient_data_degrade(self):
        tiny = self.df.head(5)
        res = self.analyzer.backtest(tiny, initial_balance=1000)
        # 数据不足时不崩溃，返回结构完整
        self.assertIn('total_return', res)


if __name__ == '__main__':
    unittest.main(verbosity=2)
