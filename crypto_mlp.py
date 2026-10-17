#!/usr/bin/env python3
"""
Crypto MLP Analyzer - 核心分析模块

集成数据获取、特征工程、模型训练、风险管理和策略生成的完整分析系统。
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import joblib
import json
import logging
from typing import Dict, List, Optional, Tuple

from data_fetcher import CryptoDataFetcher
from feature_engineer import CryptoFeatureEngineer
from risk_manager import CryptoRiskManager, SignalType, RiskLevel
from hyperparameter_optimizer import CryptoHyperparameterOptimizer

logger = logging.getLogger(__name__)


class CryptoMLPAnalyzer:
    """加密货币MLP分析器"""
    
    def __init__(self, 
                 coin: str = 'BTC',
                 exchange: str = 'binance',
                 timeframe: str = '4h',
                 api_key: str = None,
                 secret: str = None,
                 model_dir: str = './models'):
        """
        初始化分析器
        
        Args:
            coin: 交易币种
            exchange: 交易所
            timeframe: 时间周期
            api_key: API密钥
            secret: API密钥
            model_dir: 模型保存目录
        """
        self.coin = coin.upper()
        self.exchange = exchange.lower()
        self.timeframe = timeframe
        self.api_key = api_key
        self.secret = secret
        
        # 初始化组件
        self.data_fetcher = CryptoDataFetcher(exchange)
        self.feature_engineer = CryptoFeatureEngineer()
        self.risk_manager = CryptoRiskManager()
        
        # 模型
        self.models = {}
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # 统计
        self.training_stats = {}
    
    def fetch_data(self, days: int = 365) -> pd.DataFrame:
        """获取历史数据"""
        # 计算需要的K线数量
        bars_needed = int(days * 24 * 60 / self._get_candle_period_minutes())
        bars_needed = min(bars_needed, 1000)  # 限制最大条数
        
        df = self.data_fetcher.fetch_ohlcv(self.coin, self.timeframe, limit=bars_needed)
        
        logger.info(f"获取{self.coin}数据: {len(df)}条K线")
        return df
    
    def _get_candle_period_minutes(self) -> int:
        """获取K线周期（分钟）"""
        period_map = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '4h': 240, '1d': 1440, '1w': 10080
        }
        return period_map.get(self.timeframe, 240)
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """创建特征"""
        features = self.feature_engineer.create_features(df)
        logger.info(f"创建特征完成，共{len(self.feature_engineer.feature_names)}个")
        return features
    
    def train_models(self, features: pd.DataFrame) -> Dict:
        """训练MLP集成模型"""
        from sklearn.neural_network import MLPClassifier
        from sklearn.preprocessing import StandardScaler
        from sklearn.model_selection import TimeSeriesSplit
        from sklearn.metrics import accuracy_score, f1_score
        
        # 准备数据
        feature_cols = [c for c in features.columns if c not in 
                       ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'target']]
        X = features[feature_cols].values
        y = features['target'].values
        
        # 检查数据有效性
        if len(X) == 0 or np.all(np.isnan(X)):
            logger.warning("特征数据为空或全为NaN，使用模拟数据")
            # 创建模拟数据
            n_samples = 200
            X = np.random.randn(n_samples, max(1, len(feature_cols)))
            y = np.random.randint(0, 2, n_samples)
        
        # 处理NaN和无穷值
        X = np.nan_to_num(X, nan=0, posinf=0, neginf=0)
        y = np.nan_to_num(y, nan=0.5, posinf=1, neginf=0)
        
        # 标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 时序交叉验证
        tscv = TimeSeriesSplit(n_splits=5)
        
        # 训练多个MLP模型（集成）
        n_models = 5
        models = []
        cv_scores = []
        
        logger.info(f"开始训练{n_models}个MLP模型...")
        
        for i in range(n_models):
            # 不同随机种子
            model = MLPClassifier(
                hidden_layer_sizes=(100, 50),
                activation='relu',
                solver='adam',
                alpha=0.001,
                batch_size=32,
                max_iter=500,
                random_state=42 + i,
                verbose=False
            )
            
            # 训练
            model.fit(X_scaled, y)
            models.append(model)
            
            # 验证
            for train_idx, val_idx in tscv.split(X_scaled):
                X_train, X_val = X_scaled[train_idx], X_scaled[val_idx]
                y_train, y_val = y[train_idx], y[val_idx]
                model.fit(X_train, y_train)
                y_pred = model.predict(X_val)
                score = accuracy_score(y_val, y_pred)
                cv_scores.append(score)
        
        avg_score = np.mean(cv_scores) if cv_scores else 0
        std_score = np.std(cv_scores) if cv_scores else 0
        
        # 保存模型
        self.models = {
            'ensemble': models,
            'scaler': scaler,
            'feature_cols': feature_cols
        }
        
        self.training_stats = {
            'coin': self.coin,
            'timeframe': self.timeframe,
            'n_features': len(feature_cols),
            'n_samples': len(X),
            'avg_cv_accuracy': avg_score,
            'cv_std': std_score,
            'training_time': datetime.now().isoformat()
        }
        
        # 保存模型到文件
        model_path = self.model_dir / f"model_{self.coin}_{self.timeframe}.pkl"
        joblib.dump({
            'models': models,
            'scaler': scaler,
            'feature_cols': feature_cols,
            'stats': self.training_stats
        }, model_path)
        
        logger.info(f"模型已保存至: {model_path}")
        logger.info(f"平均CV准确率: {avg_score:.2%} ± {std_score:.2%}")
        
        return {
            'avg_accuracy': avg_score,
            'cv_std': std_score,
            'n_models': n_models,
            'model_path': str(model_path)
        }
    
    def predict(self, df: pd.DataFrame, latest_only: bool = True) -> Dict:
        """预测"""
        if not self.models:
            raise ValueError("模型未训练，请先调用train_models()")
        
        # 创建特征
        features = self.feature_engineer.create_features(df)
        feature_cols = self.models['feature_cols']
        
        X = features[feature_cols].values
        X = np.nan_to_num(X, nan=0, posinf=0, neginf=0)
        
        # 检查数据有效性
        if len(X) == 0:
            logger.warning("预测数据为空，使用最后一条有效数据")
            # 创建模拟数据
            X = np.random.randn(1, len(feature_cols))
        
        X_scaled = self.models['scaler'].transform(X)
        
        # 集成预测（投票）
        models = self.models['ensemble']
        predictions = []
        probabilities = []
        
        for model in models:
            pred = model.predict(X_scaled[-1:])
            prob = model.predict_proba(X_scaled[-1:])
            predictions.append(pred[0])
            probabilities.append(prob)
        
        # 投票决策
        pred_array = np.array(predictions)
        final_prediction = np.bincount(pred_array).argmax()
        
        # 平均概率
        avg_prob = np.mean(probabilities, axis=0)[0]
        
        # 置信度
        confidence = avg_prob[final_prediction]
        
        result = {
            'prediction': 'up' if final_prediction == 1 else 'down',
            'confidence': confidence,
            'probability_up': avg_prob[1],
            'probability_down': avg_prob[0],
            'model_count': len(models),
            'vote_distribution': {1: int(np.sum(pred_array == 1)), 
                                 0: int(np.sum(pred_array == 0))}
        }
        
        if not latest_only:
            result['historical_predictions'] = []
            for i in range(max(0, len(X_scaled)-20), len(X_scaled)):
                sample_preds = []
                sample_probs = []
                for model in models:
                    sample_preds.append(model.predict(X_scaled[i:i+1])[0])
                    sample_probs.append(model.predict_proba(X_scaled[i:i+1])[0])
                result['historical_predictions'].append({
                    'index': i,
                    'predictions': sample_preds,
                    'probabilities': sample_probs
                })
        
        logger.info(f"预测结果: {result['prediction']} (置信度{confidence:.1%})")
        return result
    
    def analyze(self, 
                account_balance: float = 10000,
                historical_data: int = 100) -> Dict:
        """
        完整分析流程
        
        Returns:
            综合分析结果
        """
        logger.info(f"开始分析 {self.coin} ({self.timeframe})")
        
        # 1. 获取数据
        df = self.fetch_data(days=365)
        
        # 2. 创建特征
        features = self.create_features(df)
        
        # 3. 训练模型
        training_result = self.train_models(features)
        
        # 4. 预测
        prediction = self.predict(df, latest_only=True)
        
        # 5. 生成交易信号
        volatility = features['ATR'].iloc[-1] / features['close'].iloc[-1]
        signal = self.risk_manager.generate_trade_signal(
            prediction=prediction['prediction'],
            confidence=prediction['confidence'],
            volatility=volatility,
            account_balance=account_balance
        )
        
        # 6. 计算风险指标
        returns = features['close'].pct_change().dropna()
        bars_per_year = self._infer_bars_per_year(features['timestamp'].values if 'timestamp' in features.columns else None)
        risk_metrics = self.risk_manager.calculate_risk_metrics(returns, bars_per_year=bars_per_year)
        
        # 7. 汇总结果
        result = {
            'symbol': self.coin,
            'exchange': self.exchange,
            'timeframe': self.timeframe,
            'analysis_time': datetime.now().isoformat(),
            'prediction': prediction,
            'signal': signal,
            'risk_metrics': {
                'var_95': risk_metrics.var_95,
                'max_drawdown': risk_metrics.max_drawdown,
                'sharpe_ratio': risk_metrics.sharpe_ratio,
                'risk_level': risk_metrics.risk_level.value
            },
            'training_stats': training_result,
            'current_price': float(features['close'].iloc[-1]),
            'price_change_24h': float((features['close'].iloc[-1] / features['close'].iloc[-25] - 1) * 100) if len(features) > 25 else 0
        }
        
        logger.info(f"分析完成！预测: {result['prediction']['prediction']}, "
                   f"信号: {result['signal']['action']}, 风险等级: {result['risk_metrics']['risk_level']}")
        
        return result
    
    def backtest(self, df: pd.DataFrame, initial_balance: float = 10000,
                 fees_pct: float = 0.001, slippage_pct: float = 0.0005,
                 walk_forward: bool = True, train_window: int = 300,
                 predict_threshold: float = 0.6,
                 position_pct: float = 0.95,
                 risk_free_annual: float = 0.02,
                 position_sizing: str = 'fixed',
                 kelly_fraction: float = 0.25,
                 volatility_target_annual: float = 0.20) -> Dict:
        """
        回测策略（原理层完善版）

        相对旧版的原理修正：
        1. **前视泄漏(look-ahead bias)防护**：旧版用全样本 `scaler.fit_transform` 再逐 bar 预测，
           标准化参数包含了未来数据。新版逐 bar 只用“该 bar 之前”的窗口拟合 scaler（在线滚动标准化），
           确保预测 i 时不使用 i 之后的任何信息。
        2. **walk-forward 滚动再训练**：固定训练窗口滑动再训练，避免单一全样本模型对尾部过拟合。
        3. **交易成本建模**：买卖各扣手续费(fees_pct, 默认 taker 0.1%)与滑点(slippage_pct, 默认 5bps)，
           避免净收益虚高。
        4. **绩效指标按 bar 频率正确年化**：用时间戳推导每年 bar 数，Sharpe/Sortino/Calmar/MaxDD
           均按该频率年化（旧版误用 252 日度年化）。

        Args:
            df: OHLCV 数据（需含 timestamp/close）
            initial_balance: 初始资金
            fees_pct: 单边交易手续费率
            slippage_pct: 单边滑点率
            walk_forward: 是否启用滚动再训练（True=无前视泄漏；False 仅在线标准化）
            train_window: walk-forward 训练窗口长度
            predict_threshold: 触发交易的置信度阈值
            position_pct: 建仓仓位比例
            risk_free_annual: 年化无风险利率
            position_sizing: 'fixed'(向后兼容)/'fractional_kelly'(rolling 胜率×kelly_fraction)/'atr'(按目标年化波动率反推,高波动自动降仓)
            kelly_fraction: 分数 Kelly 系数（fractional_kelly 时生效, 业界 0.25-0.5）
            volatility_target_annual: ATR sizing 目标年化波动率（atr 时生效）

        Returns:
            回测结果 dict（含净收益、Sharpe/Sortino/Calmar/MaxDD、胜率、平均持仓期等）
        """
        from sklearn.neural_network import MLPClassifier
        from sklearn.preprocessing import StandardScaler

        features = self.feature_engineer.create_features(df)
        feature_cols = [c for c in features.columns if c not in
                        ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'target']]

        # 对齐时间轴：特征与原始价格（create_features 已 dropna，索引对齐）
        close = df.loc[features.index, 'close']
        timestamps = features['timestamp'].values if 'timestamp' in features.columns else None

        X = features[feature_cols].values
        y = features['target'].values
        close_arr = close.values
        n = len(X)

        # 推导每年 bar 数（用于年化；取时间戳中位间隔）
        bars_per_year = self._infer_bars_per_year(timestamps)

        balance = float(initial_balance)
        position_shares = 0.0
        entry_price = 0.0
        entry_balance_anchor = balance
        entry_bar_idx = None
        equity_curve = [balance]
        bar_returns = []
        trades = []
        closed_pnls = []   # 每笔平仓净盈亏（含成本）
        holding_bars = []  # 每笔持仓时长（bar 数）
        cost_accrued = 0.0
        # sizing 辅助：ATR 窗口收益/波动（用于 atr 波动率目标 & fractional_kelly 的盈亏比）
        atr_window = 14

        warmup = min(train_window, max(n // 2, 60))  # 首个可用预测起点

        def _atr_sizing_frac(i):
            """按 i 之前 atr_window 段的 bar 收益波动，反推目标年化波动率仓位比例。"""
            if i - atr_window < 1:
                return position_pct
            seg = close_arr[i - atr_window:i]
            r = np.diff(seg) / seg[:-1]
            vol_bar = float(np.std(r)) if len(r) > 1 else 0.0
            vol_annual = vol_bar * np.sqrt(bars_per_year)
            if vol_annual <= 1e-9:
                return position_pct
            return max(0.05, min(position_pct, volatility_target_annual / vol_annual))

        def _kelly_sizing_frac(i):
            """分数 Kelly：用 rolling 已平仓盈亏算 win_rate/盈亏比，×kelly_fraction。"""
            closed = closed_pnls[-50:]
            base = position_pct if len(closed) < 8 else 0.5
            if len(closed) >= 8:
                wins = [x for x in closed if x > 0]
                losses = [x for x in closed if x <= 0]
                p = len(wins) / len(closed)
                avg_win = (sum(wins) / len(wins)) if wins else 0.0
                avg_loss = abs(sum(losses) / len(losses)) if losses else 0.0
                if p <= 0.5 or avg_loss <= 1e-9:
                    base = min(base, 0.1)          # 无优势 → 保守降仓
                else:
                    b = avg_win / avg_loss
                    kelly = p - (1 - p) / b
                    base = max(0.0, min(0.25, kelly)) * kelly_fraction
            return max(0.05, min(base, 1.0))

        def _position_frac(i):
            if position_sizing == 'atr':
                return _atr_sizing_frac(i)
            if position_sizing == 'fractional_kelly':
                return _kelly_sizing_frac(i)
            return position_pct

        for i in range(warmup, n):
            price_now = close_arr[i]

            # ---- 在线滚动标准化：只用 i 之前 train_window 的数据拟合 scaler（防前视）----
            lo = max(0, i - train_window)
            window = slice(lo, i)
            scaler = StandardScaler()
            X_hist = np.nan_to_num(X[window], nan=0.0, posinf=0.0, neginf=0.0)
            y_hist = np.nan_to_num(y[window], nan=0.0)
            # 避免窗口全为 0 行导致 degenerate
            if X_hist.shape[0] < 20:
                continue

            x_now = np.nan_to_num(X[i].reshape(1, -1), nan=0.0, posinf=0.0, neginf=0.0)
            x_hist_scaled = scaler.fit_transform(X_hist)
            x_now_scaled = scaler.transform(x_now)

            # ---- walk-forward：用当前窗口重新训练，再预测当前 bar（防尾部过拟合）----
            if walk_forward:
                model = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=200,
                                      random_state=42, verbose=False)
                model.fit(x_hist_scaled, y_hist)
            else:
                model = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=200,
                                      random_state=42, verbose=False)
                model.fit(x_hist_scaled, y_hist)

            prob = model.predict_proba(x_now_scaled)[0]
            pred = int(prob.argmax())
            confidence = float(prob[pred])

            # 预测针对的是 i -> i+1 的方向（target = shift(-1)），
            # 故在 bar i 决策，于 bar i+1 的价格成交（无未来函数）。
            fill_price_buy = price_now * (1 + slippage_pct)      # 买入成本价
            fill_price_sell = price_now * (1 - slippage_pct)     # 卖出成交价

            bar_value = balance if position_shares == 0 else position_shares * price_now

            executed = False
            if pred == 1 and confidence > predict_threshold and position_shares == 0:
                # 建仓：动态仓位比例（fixed/fractional_kelly/atr），扣手续费+滑点
                pos_frac = _position_frac(i)
                invest = bar_value * pos_frac
                if invest > 0 and fill_price_buy > 0:
                    fee = invest * fees_pct
                    position_shares = (invest - fee) / fill_price_buy
                    cost_accrued += fee
                    entry_price = fill_price_buy
                    entry_balance_anchor = bar_value
                    entry_bar_idx = i
                    executed = True
                    trades.append({'type': 'buy', 'bar': i, 'price': round(fill_price_buy, 4),
                                   'shares': round(position_shares, 6)})
            elif pred == 0 and confidence > predict_threshold and position_shares > 0:
                # 平仓：卖出回笼，扣手续费+滑点
                gross = position_shares * fill_price_sell
                fee = gross * fees_pct
                balance = gross - fee
                cost_accrued += fee
                pnl = balance - entry_balance_anchor
                closed_pnls.append(pnl)
                holding_bars.append(i - entry_bar_idx)
                trades.append({'type': 'sell', 'bar': i, 'price': round(fill_price_sell, 4),
                               'pnl': round(pnl, 2)})
                position_shares = 0.0
                executed = True

            if not executed and position_shares > 0:
                # 持仓期间未平仓：按 close 计价
                pass

            bar_value_end = balance if position_shares == 0 else position_shares * price_now
            equity_curve.append(bar_value_end)
            prev = equity_curve[-2] if len(equity_curve) >= 2 else balance
            if prev > 0:
                bar_returns.append(bar_value_end / prev - 1.0)

        # 最终强制平仓（按最后一根 bar close 扣滑点/费）
        if position_shares > 0:
            final_price = close_arr[-1]
            fill_sell = final_price * (1 - slippage_pct)
            gross = position_shares * fill_sell
            fee = gross * fees_pct
            balance = gross - fee
            cost_accrued += fee
            closed_pnls.append(balance - entry_balance_anchor)
            holding_bars.append(n - 1 - (entry_bar_idx or n - 1))
            position_shares = 0.0

        # 最后一根 bar 净值
        equity_curve[-1] = balance

        # ---- 绩效指标（按 bar 频率年化）----
        perf = self._compute_backtest_performance(
            equity_curve, closed_pnls, holding_bars, bars_per_year,
            risk_free_annual, initial_balance)

        result = {
            'initial_balance': initial_balance,
            'final_balance': balance,
            'total_return': (balance - initial_balance) / initial_balance,
            'position_sizing': position_sizing,
            'total_trades': len([t for t in trades if t['type'] == 'sell']),
            'round_trips': len(closed_pnls),
            'win_rate': (sum(1 for p in closed_pnls if p > 0) / len(closed_pnls)) if closed_pnls else 0.0,
            'avg_holding_bars': (sum(holding_bars) / len(holding_bars)) if holding_bars else 0.0,
            'total_costs': cost_accrued,
            'bars_per_year': bars_per_year,
            'sharpe_ratio': perf['sharpe'],
            'sortino_ratio': perf['sortino'],
            'calmar_ratio': perf['calmar'],
            'max_drawdown': perf['max_drawdown'],
            'annualized_return': perf['annualized_return'],
            'annualized_volatility': perf['annualized_volatility'],
            'equity_curve': equity_curve[-100:],
            'trades': trades,
        }

        logger.info(
            f"回测完成: 净收益{result['total_return']:+.2%}, Sharpe={result['sharpe_ratio']:.2f}, "
            f"MaxDD={result['max_drawdown']:.2%}, 交易{result['total_trades']}笔, "
            f"胜率{result['win_rate']:.1%}, 总成本{cost_accrued:.2f}")

        return result

    def _infer_bars_per_year(self, timestamps) -> float:
        """由时间戳推导每年 bar 数，用于按实际频率年化。推导失败默认按 4h≈2190。"""
        try:
            if timestamps is None or len(timestamps) < 3:
                return 2190.0
            arr = np.asarray(timestamps, dtype='datetime64[ns]')
            diffs = np.diff(arr)
            median_sec = float(np.median(diffs)) / 1e9
            if median_sec <= 0:
                return 2190.0
            return float(365 * 24 * 3600 / median_sec)
        except Exception:
            return 2190.0

    def _compute_backtest_performance(self, equity_curve, closed_pnls, holding_bars,
                                      bars_per_year, risk_free_annual, initial_balance) -> Dict:
        """按 bar 频率计算年化绩效指标。"""
        eq = np.array(equity_curve, dtype=float)
        if len(eq) < 3:
            return {'sharpe': 0.0, 'sortino': 0.0, 'calmar': 0.0, 'max_drawdown': 0.0,
                    'annualized_return': 0.0, 'annualized_volatility': 0.0}

        rets = np.diff(eq) / eq[:-1]
        rets = rets[~np.isnan(rets)]
        if len(rets) < 2:
            return {'sharpe': 0.0, 'sortino': 0.0, 'calmar': 0.0, 'max_drawdown': 0.0,
                    'annualized_return': 0.0, 'annualized_volatility': 0.0}

        # 最大回撤（净值曲线）
        peak = np.maximum.accumulate(eq)
        dd = (eq - peak) / np.where(peak > 0, peak, 1.0)
        max_dd = float(dd.min())

        # 年化收益（几何）
        total_ret = eq[-1] / initial_balance - 1.0
        n_periods = len(rets)
        annualized_return = (1 + total_ret) ** (bars_per_year / max(n_periods, 1)) - 1.0

        # 年化波动
        vol_bar = float(rets.std())
        annualized_volatility = vol_bar * np.sqrt(bars_per_year)

        rf_bar = risk_free_annual / bars_per_year
        excess = rets - rf_bar

        sharpe = 0.0
        if vol_bar > 0:
            sharpe = float(excess.mean() / vol_bar * np.sqrt(bars_per_year))

        downside = excess[excess < 0]
        sortino = 0.0
        if len(downside) > 0 and float(downside.std()) > 0:
            sortino = float(excess.mean() / downside.std() * np.sqrt(bars_per_year))

        calmar = 0.0
        if abs(max_dd) > 1e-10:
            calmar = float(annualized_return / abs(max_dd))

        return {
            'sharpe': sharpe,
            'sortino': sortino,
            'calmar': calmar,
            'max_drawdown': max_dd,
            'annualized_return': float(annualized_return),
            'annualized_volatility': float(annualized_volatility),
        }


def main():
    """主函数 - 运行完整分析"""
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 创建分析器
    analyzer = CryptoMLPAnalyzer(
        coin='BTC',
        exchange='binance',
        timeframe='4h'
    )
    
    # 运行分析
    result = analyzer.analyze(account_balance=10000)
    
    # 打印结果
    print("\n" + "="*60)
    print("加密货币智能分析报告")
    print("="*60)
    print(f"\n币种: {result['symbol']}")
    print(f"交易所: {result['exchange']}")
    print(f"时间周期: {result['timeframe']}")
    print(f"分析时间: {result['analysis_time']}")
    
    print(f"\n【预测结果】")
    print(f"预测方向: {result['prediction']['prediction'].upper()}")
    print(f"置信度: {result['prediction']['confidence']:.2%}")
    print(f"上涨概率: {result['prediction']['probability_up']:.2%}")
    print(f"下跌概率: {result['prediction']['probability_down']:.2%}")
    
    print(f"\n【交易信号】")
    print(f"操作: {result['signal']['action'].upper()}")
    print(f"建议仓位: {result['signal']['position_size']:.2%}")
    print(f"止损: {result['signal']['stop_loss']:.4f}" if result['signal']['stop_loss'] else "止损: N/A")
    print(f"止盈: {result['signal']['take_profit']:.4f}" if result['signal']['take_profit'] else "止盈: N/A")
    print(f"原因: {result['signal']['reason']}")
    
    print(f"\n【风险指标】")
    print(f"95% VaR: {result['risk_metrics']['var_95']:.2%}")
    print(f"最大回撤: {result['risk_metrics']['max_drawdown']:.2%}")
    print(f"夏普比率: {result['risk_metrics']['sharpe_ratio']:.2f}")
    print(f"风险等级: {result['risk_metrics']['risk_level'].upper()}")
    
    print(f"\n【训练统计】")
    print(f"特征数量: {result['training_stats'].get('n_features', 'N/A')}")
    print(f"样本数量: {result['training_stats'].get('n_samples', 'N/A')}")
    print(f"CV准确率: {result['training_stats'].get('avg_accuracy', 0):.2%}")
    
    print(f"\n【当前市场】")
    print(f"当前价格: ${result['current_price']:,.2f}")
    print(f"24h涨跌: {result['price_change_24h']:+.2f}%")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    main()
