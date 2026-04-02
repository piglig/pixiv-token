# Pixiv OAuth Token Fetcher

🌍 [English](README.md) | [简体中文](README.zh-CN.md)

A Python automation tool using Playwright to simulate Pixiv OAuth login, capture authorization code, and exchange it for an access token.

---

## 📦 Features

- ✅ Automated Pixiv login (username/password)
- ✅ Headless mode support (Chrome `--headless=new`, bypasses reCAPTCHA detection)
- ✅ Visible (non-headless) mode support
- ✅ Console-based authorization code capture via CDP
- ✅ Access token & refresh token retrieval
- ✅ Slow typing to bypass bot detection
- ✅ Auto-skip security prompt pages (Passkeys / 2FA reminders)
- ✅ Multi-selector fallback for Pixiv login form compatibility

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/piglig/pixiv-token.git
cd pixiv-token
```

### 2. Install dependencies

Recommended Python version: `>=3.8`

```bash
pip install -r requirements.txt
playwright install chromium
```

Sample requirements.txt:

```txt
requests==2.32.2
playwright>=1.51.0
```

---

## ⚙️ Usage

### Command line

```bash
# Headless mode (default)
python pixiv_token_fetcher.py -u "your_email" -p "your_password"

# Visible browser mode
python pixiv_token_fetcher.py -u "your_email" -p "your_password" --no-headless
```

### As a module

```python
from pixiv_token_fetcher import PixivTokenFetcher

fetcher = PixivTokenFetcher(
    username="your_pixiv_email",
    password="your_pixiv_password",
    headless=True,  # Set to False to show browser window
)
code = fetcher.fetch_code()
if code:
    token_info = fetcher.exchange_token(code)
    print("Access Token:", token_info.get("access_token"))
    print("Refresh Token:", token_info.get("refresh_token"))
```

---

## 🔧 How It Works

1. **PKCE Generation** — Generates `code_verifier` and `code_challenge` for OAuth PKCE flow
2. **Browser Launch** — Uses Chrome's native `--headless=new` mode (full browser engine without a visible window, undetectable by reCAPTCHA)
3. **Auto Login** — Fills in email/password with slow typing to mimic human input
4. **Code Capture** — Intercepts the `pixiv://account/login?code=...` redirect via CDP (`Network.requestWillBeSent`)
5. **Security Prompt Handling** — Automatically clicks "Remind me later" / "Skip" if Pixiv shows a Passkeys/2FA setup page
6. **Token Exchange** — Exchanges the authorization code for access & refresh tokens via Pixiv OAuth API

---

## 📌 Notes

- ⚠️ Do not hardcode credentials in production environments. Use environment variables or a secrets manager.
- ❌ This is not an official Pixiv SDK. Changes to Pixiv's login page may affect functionality.
- 🛡 Please comply with Pixiv's Terms of Service.
- 🔁 The refresh token is long-lived. You typically only need to run this tool once.

---

## 🧪 Example Output

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

## 📝 License

See the [LICENSE](LICENSE) file for license rights and limitations (MIT).

---

## 🙋‍♀️ Contribution & Issues

Pull Requests and Issues are welcome!

---

## 📫 Contact

- GitHub: [piglig](https://github.com/piglig)
- Email: zhu1197437384@gmail.com
