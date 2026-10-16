# 三平台同步配置

## GitHub
- 仓库: https://github.com/Zeon7744/crypto-mlp-high-confidence
- Token: 已配置 (gh auth)
- 推送状态: ✅ 已推送

## Gitee
- 账号: Zeon7744
- Token: 1f1e543fdb73b47c4f85ffa65b1ac41d
- 仓库: 待创建 (browser task pending)
- 同步策略: GitHub → Gitee 手动推送

## 爱发电
- 用户ID: 0c59dda8a1bb11f19b9552540025c377
- Token: WTcfMbUpkvFdACswPruY3ySxG87KJ45e
- 状态: API端点需验证
- 同步策略: 手动创建页面

## 同步脚本

```bash
#!/bin/bash
# sync_platforms.sh - 同步代码到多平台

REPO_DIR="/Coze/Drive/红剑/dev-artifacts/crypto-mlp"
GITEE_TOKEN="1f1e543fdb73b47c4f85ffa65b1ac41d"
GITEE_REPO="crypto-mlp-high-confidence"
GITEE_URL="https://gitee.com/Zeon7744/${GITEE_REPO}.git"

cd "$REPO_DIR"

# 推送至GitHub
echo "Pushing to GitHub..."
git push github main

# 推送至Gitee
echo "Pushing to Gitee..."
git remote add gitee "$GITEE_URL" 2>/dev/null || git remote set-url gitee "$GITEE_URL"
git push gitee main
```
