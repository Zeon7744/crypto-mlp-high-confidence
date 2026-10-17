# Gitee 认证配置

## 问题
Git push 认证失败: `Incorrect username or password (access token)`

## 解决方案

### 方法 1: 使用 Personal Access Token (PAT)

```bash
# 在 Gitee 设置中获取 PAT:
# https://gitee.com/profile/personal_access_tokens

# 设置 Git 凭据
git config --global credential.helper store

# 推送时会自动提示输入用户名和 token
git push gitee master:main
```

### 方法 2: 使用 gh auth

```bash
# 登录 Gitee
gh auth login
# 选择 Gitee.com
# 输入 token: 1f1e543fdb73b47c4f85ffa65b1ac41d

# 推送
git push gitee master:main
```

### 方法 3: 手动推送

在用户本地电脑执行:
```bash
cd /path/to/crypto-mlp
git remote add gitee https://gitee.com/Zeon7744/crypto-mlp-high-confidence.git
git push -u gitee master
```

## Token 验证

使用 curl 验证 token:
```bash
curl -s "https://gitee.com/api/v5/user" \
  -H "Authorization: token YOUR_TOKEN"
```

## 当前状态

- GitHub: ✅ 已完成 (https://github.com/Zeon7744/crypto-mlp-high-confidence)
- Gitee: ⏳ 仓库已创建，需推送代码
- 爱发电: ⏳ 需手动创建赞助页面
