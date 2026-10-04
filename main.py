import os
import re
import hashlib
from playwright.sync_api import sync_playwright
from evaluator import evaluate_job_post
from notifier import send_alert
from linkedin_scraper import scan_linkedin_jobs
from db import init_db, is_seen, mark_seen

# Enable ANSI escape processing in standard Windows terminals
os.system("")

BOLD = "\033[1m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def run_scanner(group_url: str):
    with sync_playwright() as p:
        # Uses your existing browser profile to stay logged in
        browser = p.chromium.launch_persistent_context(
            user_data_dir="./fb_session",
            headless=True
        )
        page = browser.new_page()
        page.goto(group_url)
        page.wait_for_timeout(4000)

        # Scrape recent post containers
        feed_posts = page.locator('div[role="feed"] > div').all()

        for post in feed_posts[:10]:
            text = post.inner_text()
            post_id = generate_fb_post_id(text)

            if not is_seen(post_id) and len(text.strip()) > 30:
                print("Evaluating new post...")
                evaluation = evaluate_job_post(text)

                print(f"-> Relevant: {evaluation.is_relevant} (Score: {evaluation.confidence})")
                print(f"-> Role: {evaluation.job_title} | Reason: {evaluation.reason}\n")
                
                if evaluation.is_relevant and evaluation.confidence >= 0.7:
                    print(f"Match found: {evaluation.job_title}")
                    send_alert(group_url, evaluation, text)
                
                mark_seen(post_id)
        
        browser.close()

def generate_fb_post_id(text: str) -> str:
    cleaned_text = re.sub(r'\b(\d+\s*(?:hrs?|mins?|days?|w|d|h)|just now)\b', '', text.lower())
    return "fb_" + hashlib.sha256(cleaned_text[:150].encode('utf-8')).hexdigest()

if __name__ == "__main__":
    init_db()
    # 1. Scan Facebook group
    # print(f"\n{BOLD}{CYAN}================== Facebook Group Scanner =================={RESET}")
    # GROUP_URL = "https://www.facebook.com/groups/185895661580288"
    # run_scanner(GROUP_URL)

    # 2. Scan LinkedIn Queries
    print(f"\n{BOLD}{CYAN}================== LinkedIn Public Scanner =================={RESET}")
    SEARCH_QUERIES = [
        # 1. Primary Low-Level / Systems Targets
        # "Rust Developer",
        # "C++ Developer",
        # "Embedded Software Engineer",
        # "Firmware Engineer",
        # "Silicon Validation Engineer",

        # 2. Student & Junior Specific (High hit-rate for students)
        "Software Engineering Student",
        "Embedded Student",
        "Junior Software Engineer",
        "סטודנט תוכנה",
        "מפתח C++",

        # # 3. Secondary Tech & Application Roles
        # "Python Developer",
        # "Backend Developer",
        # "Flutter Developer"
    ]
    for query in SEARCH_QUERIES:
        print(f"\n{YELLOW}--- Scanning LinkedIn for: {query} ---{RESET}")
        scan_linkedin_jobs(keywords=query, location="Beer Sheva, South District, Israel")