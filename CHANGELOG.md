# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Five-model ensemble voting system (RF + GradientBoosting + MLP + LR + SVM)
- 64+ engineered features from OHLCV + order book data
- Kelly formula position sizing module
- Volatility regime detection and adaptive weighting
- Interactive visualization demo page (Chart.js)
- GitHub Pages site deployed

### Changed
- README unified with consistent template and accurate model data
- Fixed model accuracy figures to match actual REPORT.md results

### Fixed
- README: corrected model accuracy table (was missing/wrong)
- README: added GitHub Pages link

---

## [v1.0.0] — 2026-09-05

### Added
- Core prediction engine with 5-model ensemble
- Feature engineering pipeline (technical indicators + price features)
- Risk management module (Kelly sizing + circuit breaker)
- Backtesting framework with walk-forward validation
- Comprehensive model report (REPORT.md)
- Hyperparameter optimizer using Optuna
- Release tag: v1.0.0

### Key Results
- Best model: Random Forest — CV accuracy 92.94%, Test accuracy 86.70%
- Ensemble voting: 90.22% accuracy on test set
- Top features: volume_change, volatility, momentum, RSI, price_distance

---

## [v0.1.0] — 2026-08-15

### Added
- Initial project scaffold
- Single model baseline (Logistic Regression)
- Basic feature engineering

---

[v1.0.0]: https://github.com/Zeon7744/crypto-mlp-high-confidence/releases/tag/v1.0.0
