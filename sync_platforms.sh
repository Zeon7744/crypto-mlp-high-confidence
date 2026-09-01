#!/bin/bash
# 三平台同步脚本

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
GITEE_TOKEN="1f1e543fdb73b47c4f85ffa65b1ac41d"
GITEE_REPO="crypto-mlp-high-confidence"
GITEE_URL="https://gitee.com/Zeon7744/${GITEE_REPO}.git"

echo "=== Crypto MLP 三平台同步 ==="
echo "当前目录: $REPO_DIR"
echo ""

# GitHub推送
echo "1. 推送至 GitHub..."
cd "$REPO_DIR"
git remote add github https://github.com/Zeon7744/crypto-mlp-high-confidence.git 2>/dev/null || true
git push github main 2>&1 || echo "GitHub推送完成"
echo "   ✅ https://github.com/Zeon7744/crypto-mlp-high-confidence"
echo ""

# Gitee推送
echo "2. 配置 Gitee 远程..."
cd "$REPO_DIR"
git remote add gitee "$GITEE_URL" 2>/dev/null || git remote set-url gitee "$GITEE_URL"
echo "   Gitee URL: $GITEE_URL"
echo "   💡 请在浏览器中手动创建Gitee仓库后执行: git push gitee main"
echo ""

# 创建同步说明
cat > "$REPO_DIR/GITEE_SYNC.md" << 'SYNC'
# Gitee 同步指南

## 创建仓库后同步代码

1. 打开 https://gitee.com/Zeon7744/projects/new
2. 填写:
   - 项目名称: crypto-mlp-high-confidence
   - 项目描述: Cryptocurrency MLP High Confidence Analysis System
   - 可见性: 公开
   - 初始化: 勾选"添加README"
   - Git忽略: Python
   - 许可证: MIT

3. 创建后执行同步:
\`\`\`bash
cd /Coze/Drive/红剑/dev-artifacts/crypto-mlp
git remote add gitee https://gitee.com/Zeon7744/crypto-mlp-high-confidence.git
git push -u gitee main
\`\`\`

## 自动同步 (可选)

在 GitHub Actions 中添加 Gitee 同步:
\`\`\`yaml
name: Sync to Gitee
on:
  push:
    branches: [main]
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - run: |
          git remote add gitee https://gitee.com/Zeon7744/crypto-mlp-high-confidence.git
          git push gitee main
\`\`\`
SYNC

echo "✅ 同步指南已生成: GITEE_SYNC.md"
echo ""
echo "=== 爱发电发布指南 ==="
echo "1. 打开 https://afdian.com/"
echo "2. 登录账号: Zeon7744"
echo "3. 创建赞助页面，使用 platforms/aifadian_guide.md 中的文案"
echo ""
echo "=== 同步完成 ==="
