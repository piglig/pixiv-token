# Pixiv OAuth Token Fetcher

🌍 [English](README.md) | [简体中文](README.zh-CN.md)

使用 Python + Playwright 自动模拟 Pixiv OAuth 登录流程，提取授权码，并换取 access_token。

---

## 📦 功能亮点

- ✅ 自动化模拟 Pixiv 登录流程（用户名密码）
- ✅ 控制台提取授权 code
- ✅ 获取 access_token 与 refresh_token
- ✅ 缓慢输入绕过机器人检测
- ⬜ 支持~~无头模式~~与窗口模式

---

## 🚀 安装方式

### 1. 克隆项目

```bash
git clone https://github.com/yourname/pixiv-token.git
cd pixiv-token
```

### 2. 安装依赖

推荐 Python 版本：`>=3.8`

```bash
pip install -r requirements.txt
playwright install
```

依赖示例：

```txt
requests==2.32.2
playwright>=1.51.0
```

---

## ⚙️ 使用方法

编辑并运行 `pixiv_token_fetcher.py`：

```python
if __name__ == "__main__":
    fetcher = PixivTokenFetcher(
        username="你的Pixiv账号",
        password="你的Pixiv密码",
        headless=False
    )
    code = fetcher.fetch_code()
    if code:
        token_info = fetcher.exchange_token(code)
        print("Access Token:", token_info.get("access_token"))
        print("Refresh Token:", token_info.get("refresh_token"))
```

---

## 📌 注意事项

- ⚠️ 请勿在生产环境中硬编码账号密码。
- ❌ 本项目非 Pixiv 官方 SDK，Pixiv 页面结构变化可能影响运行。
- 🛡 使用时请遵守 Pixiv 的服务条款。

---

## 🧪 示例输出

![example](./docs/example.png)

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
