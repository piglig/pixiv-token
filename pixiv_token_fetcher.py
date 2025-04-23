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
USER_AGENT = "PixivAndroidApp/5.0.234 (Android 11; Pixel 5)"


class PixivTokenFetcher:
    def __init__(self, username: str, password: str, headless=True):
        self.headless = headless
        self.username = username
        self.password = password
        self.code_verifier = secrets.token_urlsafe(64)
        self.code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(self.code_verifier.encode()).digest()
        ).rstrip(b'=').decode('ascii')

    def get_login_url(self):
        return (
            "https://app-api.pixiv.net/web/v1/login?"
            f"code_challenge={self.code_challenge}&"
            "code_challenge_method=S256&client=pixiv-android&"
            f"redirect_uri={REDIRECT_URI}"
        )

    def slow_type(self, page, selector: str, text: str, delay: float = 0.08):
        page.focus(selector)
        for char in text:
            page.keyboard.insert_text(char)
            time.sleep(delay)

    def perform_auto_login(self, page, username: str, password: str):
        try:
            page.wait_for_selector("input[autocomplete^='username']", timeout=15000)
            self.slow_type(page, "input[autocomplete^='username']", username)
            page.keyboard.press("Enter")
            print("📧 Username input completed (slow typing mode)")

            page.wait_for_selector("input[autocomplete^='current-password']", timeout=15000)
            self.slow_type(page, "input[autocomplete^='current-password']", password)
            page.keyboard.press("Enter")
            print("🔒 Password input completed (slow typing mode)")

        except TimeoutError:
            print("⚠️ Login input fields not found. Please check the page structure or network connectivity.")

    def fetch_code(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context()
            page = context.new_page()
            cdp_session = context.new_cdp_session(page)
            cdp_session.send("Network.enable")

            print("🚀 Opening Pixiv login page...")
            page.goto(self.get_login_url())

            captured_code = {"value": None}

            def cleanup_and_return(code):
                try:
                    page.close()
                except:
                    pass
                try:
                    context.close()
                except:
                    pass
                try:
                    browser.close()
                except:
                    pass
                return code

            def on_request_will_be_sent(event):
                url = event.get("request", {}).get("url", "")
                check_url = url or event.get("documentURL", "")
                if check_url.startswith("pixiv://account/login"):
                    match = re.search(r"code=([\w-]+)", check_url)
                    if match:
                        captured_code["value"] = match.group(1)
                        print("✅ Code captured via CDP:", captured_code["value"], flush=True)
                        # Trick: close page to interrupt wait loop
                        page.close()

            cdp_session.on("Network.requestWillBeSent", on_request_will_be_sent)

            self.perform_auto_login(page, self.username, self.password)

            try:
                page.wait_for_event("close", timeout=10000)
            except TimeoutError:
                print("⌛ Timeout: Code not captured.")

            return cleanup_and_return(captured_code["value"])

    def exchange_token(self, code):
        data = {
            "client_id": PIXIV_CLIENT_ID,
            "client_secret": PIXIV_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": self.code_verifier,
            "redirect_uri": REDIRECT_URI,
            "include_policy": "true",
        }
        headers = {"User-Agent": USER_AGENT}
        response = requests.post(PIXIV_TOKEN_URL, data=data, headers=headers)
        return response.json()


if __name__ == "__main__":
    fetcher = PixivTokenFetcher(username="your_username", password="your_password", headless=False)
    code = fetcher.fetch_code()
    if code:
        print("✅ Authorization code successfully obtained:", code)
        token_info = fetcher.exchange_token(code)
        print("🎟️ Access Token:", token_info.get("access_token"))
        print("🔁 Refresh Token:", token_info.get("refresh_token"))
    else:
        print("❌ Failed to retrieve authorization code. Please verify the login process.")
