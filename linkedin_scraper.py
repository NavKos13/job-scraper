import time
import re
import requests
from bs4 import BeautifulSoup
from evaluator import evaluate_job_post
from notifier import send_alert
from db import is_seen, mark_seen

SLEEP_TIME = 1
EVALUATION_CONFIDENCE = 0.7

# ANSI formatting codes
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,he;q=0.8",
}

def extract_linkedin_id(card, job_url: str) -> str:
    data_id = card.get("data-entity-urn") or card.get("data-id")
    if data_id:
        return f"li_{data_id}"
    
    match = re.search(r'(?:view|jobs)/(\d+)', job_url)
    if match:
        return f"li_{match.group(1)}"
    
    return f"li_{job_url.split('?')[0].rstrip('/')}"


def scan_linkedin_jobs(keywords: str, location: str = "Beer Sheva, South District, Israel"):
    """
    Scrapes LinkedIn public guest endpoint for jobs matching keywords in the specified location.
    """
    base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    params = {
        "keywords": keywords,
        "location": location,
        "start": 0
    }

    try:
        response = requests.get(base_url, params=params, headers=HEADERS, timeout=15)
        if response.status_code!= 200:
            print(f"{RED}[-] LinkedIn request failed [{response.status_code}]{RESET}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        job_cards = soup.find_all("li")

        for card in job_cards:
            title_elem = card.find("h3", class_="base-search-card__title")
            company_elem = card.find("h4", class_="base-search-card__subtitle")
            link_elem = card.find("a", class_="base-card__full-link")
            loc_elem = card.find("span", class_="job-search-card__location")

            if not (title_elem and link_elem):
                continue

            job_title = title_elem.get_text(strip=True)
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            job_url = link_elem.get("href", "").split("?")[0]
            job_loc = loc_elem.get_text(strip=True) if loc_elem else location

            post_id = extract_linkedin_id(card, job_url=job_url)

            if not is_seen(post_id):
                job_summary = f"Job Title: {job_title}\nCompany: {company}\nLocation: {job_loc}\nURL: {job_url}"
                print(f"{CYAN}🔍 Evaluating:{RESET} {BOLD}{job_title}{RESET} at {BOLD}{company}{RESET}...")

                evaluation = evaluate_job_post(job_summary)
                print(f"-> Match: {evaluation.is_relevant} (Score: {evaluation.confidence} | Reason: {evaluation.reason}")

                if evaluation.is_relevant and evaluation.confidence >= EVALUATION_CONFIDENCE:
                    status_tag = f"{GREEN}{BOLD}MATCH [Score: {evaluation.confidence:.2f}]{RESET}"
                    print(f"    -> {status_tag}")
                    print(f"    -> {DIM}Reason:{RESET} {evaluation.reason}")
                    print(f"    {YELLOW}⚡ Telegram notification dispatched!{RESET}")
                    send_alert(job_url, evaluation, job_summary)
                else: 
                    status_tag = f"{RED}NO MATCH [Score: {evaluation.confidence:.2f}]{RESET}"
                    print(f"    -> {status_tag}")
                    print(f"    ->{DIM}Reason:{RESET} {evaluation.reason}\n")

                print("\n")

                mark_seen(post_id)
                time.sleep(SLEEP_TIME)

    except Exception as e:
        print(f"{RED}[!] Error scanning LinkedIn: {e}{RESET}")