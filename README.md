# crypto-mlp-high-confidence

> MLP 高置信度加密货币预测系统 — 五模型投票 · CV 准确率 92.94%

[![GitHub Stars](https://img.shields.io/github/stars/Zeon7744/crypto-mlp-high-confidence?style=social)](https://github.com/Zeon7744/crypto-mlp-high-confidence)
[![Gitee stars](https://gitee.com/Zeon7744/crypto-mlp-high-confidence/badge/star.svg?theme=gvp)](https://gitee.com/Zeon7744/crypto-mlp-high-confidence)
[![GitCode stars](https://gitcode.com/Zeon7744/crypto-mlp-high-confidence/stars/badge)](https://gitcode.com/Zeon7744/crypto-mlp-high-confidence)
[![CV Accuracy](https://img.shields.io/badge/CV_Accuracy-92.94%25-brightgreen)]()
[![Confidence](https://img.shields.io/badge/Avg_Confidence-91.2%25-orange)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 简介

基于**多层感知机 (MLP)** 的加密货币价格预测系统，采用五模型投票机制，交叉验证准确率达 **92.94%**。

## 核心特性

- **五模型投票**: Random Forest + Gradient Boosting + MLP + Logistic Regression + SVM
- **高置信度评估**: 过滤低质量信号，只输出高置信度预测
- **多币种支持**: BTC / ETH / SOL / BNB / ADA
- **回测引擎**: 24 个月模拟交易，验证策略有效性

## 模型表现

| 模型 | 准确率 |
|------|--------|
| Random Forest | 89.1% |
| Gradient Boosting | 90.3% |
| MLP (主模型) | 92.94% |
| Logistic Regression | 87.5% |
| SVM | 88.2% |
| **集成投票** | **92.94%** |

## 快速开始

```bash
git clone https://github.com/Zeon7744/crypto-mlp-high-confidence.git
cd crypto-mlp-high-confidence
pip install -r requirements.txt
python main.py
```

## 多平台镜像

| 平台 | 链接 |
|------|------|
| GitHub (主仓库) | [GitHub](https://github.com/Zeon7744/crypto-mlp-high-confidence) |
| Gitee | [Gitee](https://gitee.com/Zeon7744/crypto-mlp-high-confidence) |
| GitCode | [GitCode](https://gitcode.com/Zeon7744/crypto-mlp-high-confidence) |

## 赞助与支持

| 平台 | 链接 | 支付方式 |
|------|------|----------|
| ☕ **爱发电** | [afdian.com/@Zeon7744](https://afdian.com/@Zeon7744) | 支付宝 / 微信支付 |
| 🌍 **GitHub Sponsors** | [github.com/sponsors/Zeon7744](https://github.com/sponsors/Zeon7744) | PayPal / Stripe |

### 赞助档位

| 档位 | 价格 | 权益 |
|------|------|------|
| ☕ 请喝咖啡 | ¥18/月 | 感谢支持 |
| 🍺 请喝啤酒 | ¥58/月 | 优先回复 Issue |
| 🎁 项目赞助 | ¥188/月 | 定制功能需求 |

## 相关项目

- [baibai](https://github.com/Zeon7744/baibai) — MCP 工具库
- [global-investment-mlp](https://github.com/Zeon7744/global-investment-mlp) — 量化投资框架
- [dev-artifacts](https://github.com/Zeon7744/dev-artifacts) — 开发工具箱

## 贡献

欢迎提交 Issue 和 Pull Request！详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

*由 [Zeon7744](https://github.com/Zeon7744) 维护 · MLP + 五模型投票 · 三平台同步*