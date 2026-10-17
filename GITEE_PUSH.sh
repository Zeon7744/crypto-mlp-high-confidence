#!/bin/bash
# Gitee 代码推送脚本

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Gitee 代码推送 ==="
echo "仓库: https://gitee.com/Zeon7744/crypto-mlp-high-confidence"
echo ""

cd "$REPO_DIR"

# 设置 Git 凭据
git config credential.helper '!echo username=Zeon7744; echo password=1f1e543fdb73b47c4f85ffa65b1ac41d'

# 推送代码
echo "正在推送代码到 Gitee..."
git push gitee master:main

echo ""
echo "✅ 推送完成！"
echo "访问: https://gitee.com/Zeon7744/crypto-mlp-high-confidence"
