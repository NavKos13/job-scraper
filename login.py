from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir="./fb_session",
        headless=False  # Opens actual browser window
    )
    page = browser.new_page()
    page.goto("https://www.facebook.com")
    print("Log into Facebook in the opened browser window...")
    page.wait_for_timeout(60000)  # 60 seconds to log in manually and solve 2FA
    browser.close()