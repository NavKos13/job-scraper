import requests
import os

from dotenv import load_dotenv
load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_alert(post_url: str, evaluation, original_text: str):
    message = (
        f"🎯 *New Relevant Tech Job Found!*\n\n"
        f"📌 *Role:* {evaluation.job_title}\n"
        f"🏢 *Company:* {evaluation.company_name}\n"
        f"💡 *Match Reason:* {evaluation.reason}\n\n"
        f"🔗 [View Post]({post_url})\n\n"
        f"📝 *Snippet:*\n_{original_text[:250]}..._"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)