import base64
import hashlib
import secrets
import requests
import time
import re
from playwright.sync_api import sync_playwright, TimeoutError

PIXIV_CLIENT_ID = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
PIXIV_CLIENT_SECRET = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"
PIXIV_TOKEN_URL = "https://oauth.secure.pixiv.net/auth/token"
REDIRECT_URI = "https://app-api.pixiv.net/web/v1/users/auth/pixiv/callback"
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)
API_UA = "PixivAndroidApp/5.0.234 (Android 11; Pixel 5)"

EMAIL_SELECTORS = [
    "input[autocomplete^='username']",
    "input[placeholder*='メールアドレス']",
    "input[type='email']",
]
PASSWORD_SELECTORS = [
    "input[autocomplete^='current-password']",
    "input[placeholder*='パスワード']",
    "input[type='password']",
]
SKIP_BUTTON_TEXTS = ["Remind me later", "Skip", "あとで", "スキップ"]


class PixivTokenFetcher:
    def __init__(self, username: str, password: str, headless=True):
        self.headless = headless
        self.username = username
        self.password = password
        self.code_verifier = secrets.token_urlsafe(64)
        self.code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(self.code_verifier.encode()).digest()
        ).rstrip(b'=').decode('ascii')

    def _launch_args(self):
        base_args = ["--disable-blink-features=AutomationControlled"]
        if self.headless:
            base_args.append("--headless=new")
        return base_args

    def _get_login_url(self):
        return (
            "https://app-api.pixiv.net/web/v1/login?"
            f"code_challenge={self.code_challenge}&"
            "code_challenge_method=S256&client=pixiv-android"
        )

    def _slow_type(self, page, selector: str, text: str, delay: float = 0.08):
        page.focus(selector)
        for char in text:
            page.keyboard.insert_text(char)
            time.sleep(delay)

    def _find_input(self, page, selectors: list, timeout=3000):
        for selector in selectors:
            try:
                el = page.wait_for_selector(selector, timeout=timeout)
                if el and el.is_visible():
                    return selector
            except TimeoutError:
                continue
        return None

    def _perform_login(self, page):
        email_selector = self._find_input(page, EMAIL_SELECTORS)
        if not email_selector:
            print("⚠️ Username input not found")
            return

        self._slow_type(page, email_selector, self.username)
        print("📧 Username input completed")

        pwd_selector = self._find_input(page, PASSWORD_SELECTORS)
        if not pwd_selector:
            page.keyboard.press("Enter")
            time.sleep(2)
            pwd_selector = self._find_input(page, PASSWORD_SELECTORS)

        if not pwd_selector:
            print("⚠️ Password input not found")
            return

        self._slow_type(page, pwd_selector, self.password)
        print("🔒 Password input completed")

        login_btn = page.locator("button:has-text('ログイン')")
        if login_btn.count() > 0:
            login_btn.first.click()
        else:
            page.keyboard.press("Enter")
        print("🔑 Login submitted")

    def _skip_security_prompts(self, page):
        for btn_text in SKIP_BUTTON_TEXTS:
            btn = page.locator(f"button:has-text('{btn_text}')")
            if btn.count() > 0 and btn.first.is_visible():
                print(f"  Clicking '{btn_text}' to skip security prompt")
                btn.first.click()
                time.sleep(1)
                return True
        return False

    def fetch_code(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=self._launch_args())
            context = browser.new_context(
                user_agent=BROWSER_UA,
                viewport={"width": 1280, "height": 720},
                locale="ja-JP",
            )
            page = context.new_page()
            cdp_session = context.new_cdp_session(page)
            cdp_session.send("Network.enable")

            captured_code = {"value": None}

            def on_request_will_be_sent(event):
                url = event.get("request", {}).get("url", "")
                check_url = url or event.get("documentURL", "")
                if check_url.startswith("pixiv://account/login"):
                    match = re.search(r"code=([\w-]+)", check_url)
                    if match:
                        captured_code["value"] = match.group(1)
                        print("✅ Code captured:", captured_code["value"], flush=True)
                        page.close()

            cdp_session.on("Network.requestWillBeSent", on_request_will_be_sent)

            print("🚀 Opening Pixiv login page...")
            page.goto(self._get_login_url())
            self._perform_login(page)

            for _ in range(30):
                if captured_code["value"] or page.is_closed():
                    break
                try:
                    self._skip_security_prompts(page)
                except Exception:
                    pass
                time.sleep(1)

            if not captured_code["value"]:
                print("⌛ Timeout: Code not captured.")

            browser.close()
            return captured_code["value"]

    def exchange_token(self, code):
        resp = requests.post(PIXIV_TOKEN_URL, data={
            "client_id": PIXIV_CLIENT_ID,
            "client_secret": PIXIV_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": self.code_verifier,
            "redirect_uri": REDIRECT_URI,
            "include_policy": "true",
        }, headers={"User-Agent": API_UA})
        return resp.json()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch Pixiv OAuth refresh token")
    parser.add_argument("--username", "-u", required=True)
    parser.add_argument("--password", "-p", required=True)
    parser.add_argument("--no-headless", action="store_true", help="Show browser window")
    args = parser.parse_args()

    fetcher = PixivTokenFetcher(args.username, args.password, headless=not args.no_headless)
    code = fetcher.fetch_code()
    if code:
        token_info = fetcher.exchange_token(code)
        print(f"🎟️ Access Token: {token_info.get('access_token')}")
        print(f"🔁 Refresh Token: {token_info.get('refresh_token')}")
    else:
        print("❌ Failed to retrieve authorization code.")
