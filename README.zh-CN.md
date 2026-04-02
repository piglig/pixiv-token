# Pixiv OAuth Token Fetcher

🌍 [English](README.md) | [简体中文](README.zh-CN.md)

使用 Python + Playwright 自动模拟 Pixiv OAuth 登录流程，提取授权码，并换取 access_token。

---

## 📦 功能亮点

- ✅ 自动化模拟 Pixiv 登录流程（用户名密码）
- ✅ 支持无头模式（Chrome `--headless=new`，可绕过 reCAPTCHA 检测）
- ✅ 支持窗口模式（非无头）
- ✅ 通过 CDP 在控制台捕获授权码
- ✅ 获取 access_token 与 refresh_token
- ✅ 缓慢输入模拟真人操作，绕过机器人检测
- ✅ 自动跳过安全设置提示页面（Passkeys / 2FA 提醒）
- ✅ 多选择器兼容 Pixiv 登录表单变化

---

## 🚀 安装方式

### 1. 克隆项目

```bash
git clone https://github.com/piglig/pixiv-token.git
cd pixiv-token
```

### 2. 安装依赖

推荐 Python 版本：`>=3.8`

```bash
pip install -r requirements.txt
playwright install chromium
```

依赖示例：

```txt
requests==2.32.2
playwright>=1.51.0
```

---

## ⚙️ 使用方法

### 命令行方式

```bash
# 无头模式（默认）
python pixiv_token_fetcher.py -u "你的邮箱" -p "你的密码"

# 显示浏览器窗口
python pixiv_token_fetcher.py -u "你的邮箱" -p "你的密码" --no-headless
```

### 作为模块调用

```python
from pixiv_token_fetcher import PixivTokenFetcher

fetcher = PixivTokenFetcher(
    username="你的Pixiv账号",
    password="你的Pixiv密码",
    headless=True,  # 设为 False 显示浏览器窗口
)
code = fetcher.fetch_code()
if code:
    token_info = fetcher.exchange_token(code)
    print("Access Token:", token_info.get("access_token"))
    print("Refresh Token:", token_info.get("refresh_token"))
```

---

## 🔧 工作原理

1. **PKCE 生成** — 生成 `code_verifier` 和 `code_challenge` 用于 OAuth PKCE 流程
2. **浏览器启动** — 使用 Chrome 原生 `--headless=new` 模式（完整浏览器引擎，无可见窗口，reCAPTCHA 无法检测）
3. **自动登录** — 以缓慢输入方式填写邮箱和密码，模拟真人操作
4. **授权码捕获** — 通过 CDP（`Network.requestWillBeSent`）拦截 `pixiv://account/login?code=...` 重定向
5. **安全提示处理** — 若 Pixiv 弹出 Passkeys/2FA 设置页面，自动点击"稍后提醒"/"跳过"
6. **Token 交换** — 通过 Pixiv OAuth API 将授权码换取 access token 和 refresh token

---

## 📌 注意事项

- ⚠️ 请勿在生产环境中硬编码账号密码，建议使用环境变量或密钥管理工具。
- ❌ 本项目非 Pixiv 官方 SDK，Pixiv 页面结构变化可能影响运行。
- 🛡 使用时请遵守 Pixiv 的服务条款。
- 🔁 Refresh token 有效期很长，通常只需运行一次即可。

---

## 🧪 示例输出

```
🚀 Opening Pixiv login page...
📧 Username input completed
🔒 Password input completed
🔑 Login submitted
  Clicking 'Remind me later' to skip security prompt
✅ Code captured: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
🎟️ Access Token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
🔁 Refresh Token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 📝 授权协议

MIT License

---

## 🙋‍♀️ 贡献与反馈

欢迎提交 Pull Request 和 Issue！

---

## 📫 联系方式

- GitHub: [piglig](https://github.com/piglig)
- Email: zhu1197437384@gmail.com
