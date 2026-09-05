# CONTRIBUTING

感谢你对 crypto-mlp-high-confidence 的关注！以下是参与贡献的指南。

## 如何贡献

1. Fork 本仓库
2. 创建特性分支: `git checkout -b feature/your-feature`
3. 提交更改: `git commit -m 'Add your feature'`
4. 推送分支: `git push origin feature/your-feature`
5. 提交 Pull Request

## 模型开发

- 新模型需在 `models/` 目录实现
- 每个模型需包含交叉验证脚本
- 提交前确保 CV 准确率符合基线

## 数据要求

- 使用 `data/` 目录存储原始数据
- 数据预处理脚本放在 `scripts/` 目录
- 所有数据变更需记录在 CHANGELOG.md

## 报告问题

请在 [Issues](https://github.com/Zeon7744/crypto-mlp-high-confidence/issues) 中报告。

## 赞助支持

如果模型对你有帮助：
- [爱发电](https://afdian.com/@Zeon7744)
- [GitHub Sponsors](https://github.com/sponsors/Zeon7744)
