#!/usr/bin/env python3
"""
verify_no_lookahead.py — point-in-time 前视泄漏校验器（crypto P0）

业界量化回测的金标准之一：每个特征/标签在 bar i 只能用 ≤ i 的数据。
小量前视泄漏也能把回测收益虚高 5-10%。本校验器对 feature_engineer.create_features
产出的特征矩阵做逐 bar 一致性校验，检测以下泄漏源：

1. **全样本统计泄漏**：把完整序列喂给 feature_engineer vs 只喂前 i 段，
   若第 i 行的特征值发生漂移 → 说明特征用到了 i 之后的信息（全窗口 rolling/expanding/fillna）。
2. **滚动窗口预热**：特征含固定窗口 w（rolling(w)/ewm(span=w)）时，i < w 的行应不可用，
   校验器标注预热边界，避免把预热期的"脏值"喂进回测。
3. **目标标签前视提示**：target 用 shift(-1) 是监督学习的正常约定，但成交必须发生在
   预测 bar 之后。本工具提示"target 依赖 i+1 收盘价"，提醒回测侧把成交对齐到 i+1。

用法：
    from verify_no_lookahead import verify_no_lookahead, report_to_string
    df = ... # OHLCV
    res = verify_no_lookahead(df, feature_engineer, n_check=8)
    print(report_to_string(res))
    assert res.lookahead_detected == False
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict, Optional


def _full_at_i_all(full, i):
    """取 full 中 bar i 行；若 i 被 dropna 丢弃返回 None。"""
    return full.at[i] if i in full.index else None


def verify_no_lookahead(df: pd.DataFrame,
                        feature_engineer,
                        n_check: int = 8,
                        tol: float = 1e-8) -> Dict:
    """
    逐 bar 一致性校验：对 n_check 个抽样 bar，比较
      full_i   = create_features(完整 df)[i]      （用完整序列算）
      trunc_i  = create_features(df[:i+1])[i]    （只喂到 i 的截断序列算）
    两者应一致；不一致 → 该特征用了 i 之后的信息 → 前视泄漏。

    Args:
        df: 完整 OHLCV
        feature_engineer: 提供 create_features(df)->DataFrame 的对象（CryptoFeatureEngineer）
        n_check: 抽样的 bar 数（均匀分布在中后段，预热期之后）
        tol: 浮点比较容差

    Returns:
        dict：lookahead_detected(bool) / 泄漏特征列表 / 预热边界估计 / target 前视提示
    """
    df_reset = df.reset_index(drop=True)
    full = feature_engineer.create_features(df_reset.copy())
    n = len(df_reset)
    # full / trunc 的 index 都是原 df 的整数位置（0..n-1）；dropna 后是子集。
    # 用 .index（原位置）对齐 bar i，而不是行号。

    # 抽样 bar：取中后段（跳过预热期），均匀 n_check 个
    start = max(20, n // 2)
    check_idx = np.linspace(start, n - 1, min(n_check, n - start - 1)).astype(int)

    leaked_features = {}
    drift_rows = 0
    for i in check_idx:
        if i not in full.index:
            continue
        trunc = feature_engineer.create_features(df_reset.iloc[: i + 1].copy())
        if i not in trunc.index:
            continue
        feat_cols = [c for c in full.columns
                     if c not in ('timestamp', 'open', 'high', 'low', 'close', 'volume', 'target')]
        for c in feat_cols:
            if c not in trunc.columns:
                continue
            fv = full.at[i, c]
            tv = trunc.at[i, c]
            fv = 0.0 if pd.isna(fv) else float(fv)
            tv = 0.0 if pd.isna(tv) else float(tv)
            if abs(fv - tv) > tol * max(1.0, abs(fv)):
                leaked_features.setdefault(c, []).append(int(i))
                drift_rows += 1

    # 预热边界估计：create_features 末尾 dropna，特征首次非空位置
    warmup_bound = 0
    for c in full.columns:
        if c in ('timestamp', 'open', 'high', 'low', 'close', 'volume', 'target'):
            continue
        nv = full[c].dropna()
        if len(nv) > 0:
            warmup_bound = max(warmup_bound, int(nv.index[0]))

    # target 前视提示（supervision 标签）
    target_uses_future = 'target' in full.columns
    target_future_note = ('target 用 shift(-1) 依赖 i+1 收盘价（监督学习正常约定），'
                          '回测侧须把成交对齐到预测 bar 之后（i+1），否则构成前视。')

    lookahead_detected = len(leaked_features) > 0
    return {
        'lookahead_detected': lookahead_detected,
        'leaked_features': {k: v for k, v in leaked_features.items()},
        'n_leaked_features': len(leaked_features),
        'drift_rows': drift_rows,
        'warmup_bound': warmup_bound,
        'checked_bars': [int(x) for x in check_idx],
        'tol': tol,
        'target_uses_future': target_uses_future,
        'target_future_note': target_future_note if target_uses_future else None,
    }


def report_to_string(res: Dict) -> str:
    lines = ['===== point-in-time 前视泄漏校验报告 =====']
    if res['lookahead_detected']:
        lines.append(f"⚠️  检出前视泄漏：{res['n_leaked_features']} 个特征在 {res['drift_rows']} 处漂移")
        for feat, idxs in res['leaked_features'].items():
            lines.append(f"   - {feat}: bars {idxs[:5]}{'...' if len(idxs) > 5 else ''}")
    else:
        lines.append(f"✅ 未检出前视泄漏（校验 bar={res['checked_bars']}, tol={res['tol']:.1e}）")
    lines.append(f"预热边界: bar > {res['warmup_bound']} 起特征才有效（回测 warmup 应 ≥ 此值）")
    if res['target_future_note']:
        lines.append('ⓘ ' + res['target_future_note'])
    return '\n'.join(lines)


if __name__ == '__main__':
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    np.random.seed(0)
    n = 300
    ts = pd.date_range(end=pd.Timestamp.now().floor('h'), periods=n, freq='4h')
    close = 50000 * np.exp(np.cumsum(np.random.randn(n) * 0.01))
    demo = pd.DataFrame({
        'timestamp': ts,
        'open': close * (1 + np.random.randn(n) * 0.002),
        'high': close * (1 + np.abs(np.random.randn(n) * 0.006)),
        'low': close * (1 - np.abs(np.random.randn(n) * 0.006)),
        'close': close,
        'volume': np.random.uniform(1000, 5000, n),
    })
    from feature_engineer import CryptoFeatureEngineer
    eng = CryptoFeatureEngineer()
    res = verify_no_lookahead(demo, eng, n_check=6)
    print(report_to_string(res))
