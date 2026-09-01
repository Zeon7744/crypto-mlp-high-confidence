# 三平台同步配置指南

## ✅ 已完成

### GitHub
- **仓库**: https://github.com/Zeon7744/crypto-mlp-high-confidence
- **状态**: ✅ 已推送 (master分支)
- **Commit**: 44dff0d

### 本地配置
- GitHub remote: https://github.com/Zeon7744/crypto-mlp-high-confidence.git
- Gitee remote: https://gitee.com/Zeon7744/crypto-mlp-high-confidence.git (待创建后使用)

---

## ⏳ 待完成

### Gitee - 手动创建仓库

**步骤：**
1. 访问 https://gitee.com/repos/new
2. 填写以下信息：
   - 仓库名称: `crypto-mlp-high-confidence`
   - 项目描述: `Cryptocurrency MLP High Confidence Analysis System - 92.94% CV accuracy`
   - 可见性: ☑️ 公开
   - 初始化: ☑️ 使用 README 初始化
   - .gitignore: Python
   - 许可证: MIT License
3. 点击"创建仓库"
4. 创建完成后执行同步：

```bash
cd /Coze/Drive/红剑/dev-artifacts/crypto-mlp
git remote add gitee https://gitee.com/Zeon7744/crypto-mlp-high-confidence.git
git push -u gitee master
```

### 爱发电 - 手动创建赞助页面

**步骤：**
1. 访问 https://afdian.com/ 并登录
2. 点击"创建创作者"
3. 使用 `platforms/aifadian_guide.md` 中的文案：
   - 标题: 加密货币MLP高精度分析系统 - 技术开源项目赞助
   - 简介: 使用指南中的项目介绍
   - 赞助档位: ¥10/¥50/¥200 三档
4. 完善项目资料后发布

---

## 🔄 后续同步命令

### 同步到 GitHub
```bash
git push github master
```

### 同步到 Gitee（仓库创建后）
```bash
git push gitee master
```

### GitHub Actions 自动同步（可选）
在 GitHub 仓库设置中添加 Secret:
- 名称: `GITEE_TOKEN`
- 值: `1f1e543fdb73b47c4f85ffa65b1ac41d`

创建 `.github/workflows/sync-gitee.yml`:
```yaml
name: Sync to Gitee
on:
  push:
    branches: [master]
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          git remote add gitee https://gitee.com/Zeon7744/crypto-mlp-high-confidence.git
          git push -f gitee master
        env:
          GITEE_TOKEN: ${{ secrets.GITEE_TOKEN }}
```

---

## 📊 当前状态汇总

| 平台 | 状态 | URL |
|------|------|-----|
| GitHub | ✅ 已完成 | https://github.com/Zeon7744/crypto-mlp-high-confidence |
| Gitee | ⏳ 待创建 | https://gitee.com/Zeon7744/crypto-mlp-high-confidence |
| 爱发电 | ⏳ 待创建 | https://afdian.com/@Zeon7744 |

---

## 🔧 技术说明

### 为什么需要手动创建？
- Gitee API 返回 404，可能是权限或限流问题
- 爱发电 API 端点需要验证，暂不支持自动化创建

### Token 配置
- Gitee PAT: `1f1e543fdb73b47c4f85ffa65b1ac41d` (已提供)
- 爱发电 Token: `WTcfMbUpkvFdACswPruY3ySxG87KJ45e` (用户ID: `0c59dda8a1bb11f19b9552540025c377`)

### 权限范围
- GitHub OAuth: repo, gist, read:org (无 workflow 权限)
- Gitee PAT: 需要 repository 权限
