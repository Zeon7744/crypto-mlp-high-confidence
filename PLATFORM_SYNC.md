# 三平台联动同步配置

## 当前状态

| 平台 | 状态 | URL |
|------|------|-----|
| **GitHub** | ✅ 已完成 | https://github.com/Zeon7744/crypto-mlp-high-confidence |
| **Gitee** | ⏳ 待创建 | https://gitee.com/Zeon7744/crypto-mlp-high-confidence |
| **爱发电** | ⏳ 待创建 | https://afdian.com/@Zeon7744 |

---

## GitHub 配置

### 仓库信息
- **URL**: https://github.com/Zeon7744/crypto-mlp-high-confidence
- **分支**: master
- **最后提交**: 7013036

### 本地 Remote
```bash
github  https://github.com/Zeon7744/crypto-mlp-high-confidence.git
```

### 推送命令
```bash
git push github master
```

---

## Gitee 配置

### 准备工作
1. 手动访问 https://gitee.com/repos/new 创建仓库
2. 使用以下设置:
   - 仓库名称: `crypto-mlp-high-confidence`
   - 描述: `Cryptocurrency MLP High Confidence Analysis System`
   - 可见性: 公开
   - 初始化: README + Python .gitignore + MIT License

### 同步命令（仓库创建后）
```bash
cd /Coze/Drive/红剑/dev-artifacts/crypto-mlp
git remote add gitee https://gitee.com/Zeon7744/crypto-mlp-high-confidence.git
git push -u gitee master
```

### Token
- **Gitee PAT**: `1f1e543fdb73b47c4f85ffa65b1ac41d`
- **注意**: API调用返回404，需手动创建仓库

---

## 爱发电配置

### 准备工作
1. 访问 https://afdian.com/ 登录账号
2. 点击"创建创作者"
3. 使用 `platforms/aifadian_guide.md` 中的文案

### Token 信息
- **Token**: `WTcfMbUpkvFdACswPruY3ySxG87KJ45e`
- **用户ID**: `0c59dda8a1bb11f19b9552540025c377`
- **注意**: API端点均返回404，需手动创建页面

---

## GitHub Actions 自动同步

### 添加 Secret
在 GitHub 仓库设置中添加:
- 名称: `GITEE_TOKEN`
- 值: `1f1e543fdb73b47c4f85ffa65b1ac41d`

### 创建工作流文件
创建 `.github/workflows/sync-gitee.yml`:
```yaml
name: Sync to Gitee

on:
  push:
    branches: [master]
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Push to Gitee
        run: |
          git config --global user.name "Zeon7744"
          git config --global user.email "zeon7744@gmail.com"
          git remote add gitee https://gitee.com/Zeon7744/crypto-mlp-high-confidence.git
          git push -f gitee master
        env:
          GITEE_TOKEN: ${{ secrets.GITEE_TOKEN }}
```

---

## 同步脚本

### 一键同步
```bash
#!/bin/bash
# sync_all.sh

REPO_DIR="/Coze/Drive/红剑/dev-artifacts/crypto-mlp"

echo "=== 三平台同步 ==="

# GitHub
echo "1. 推送 GitHub..."
cd "$REPO_DIR"
git push github master

# Gitee
echo "2. 推送 Gitee..."
git remote add gitee https://gitee.com/Zeon7744/crypto-mlp-high-confidence.git 2>/dev/null || true
git push gitee master

echo "✅ 同步完成"
```

---

## 技术限制

1. **GitHub OAuth**: 缺少 workflow 作用域，无法推送包含 .github 目录的代码
2. **Gitee API**: 返回404，可能需更新 Token 权限或检查 API 版本
3. **爱发电 API**: 所有尝试的端点均返回404/NOT FOUND

---

## 相关文件

- `platforms/three_platform_sync.md` - 详细同步指南
- `platforms/final_status.md` - 最终状态总结
- `sync_platforms.sh` - 同步脚本模板
