# Tech Job Scanner & AI Matcher

An automated job hunting bot that aggregates tech listings from **Facebook Groups** and **LinkedIn**, filters them against a custom developer profile using **Google Gemini Structured Outputs**, and sends instant alerts via **Telegram**.

---

## Architecture Overview

```
                                  ┌──────────────────────────┐
                                  │   Facebook Group Feed    │ (Playwright / Chromium)
                                  └─────────────┬────────────┘
                                                │
┌──────────────────────────┐                    │
│   LinkedIn Guest API     │                    │
└─────────────┬────────────┘                    │
              │                                 │
              └───────────────┬─────────────────┘
                              │  Raw Job Text
                              ▼
                ┌───────────────────────────┐
                │       db.py (SQLite)      │ (Skip if already evaluated)
                └─────────────┬─────────────┘
                              │
                              ▼
                ┌───────────────────────────┐
                │   evaluator.py (Gemini)   │ (Strict JSON extraction & scoring)
                └─────────────┬─────────────┘
                              │
                              │ If relevant (confidence >= 0.7)
                              ▼
                ┌───────────────────────────┐
                │     Telegram Alert Bot    │
                └───────────────────────────┘

```

---

## Prerequisites & Installation

### 1. Clone & Set Up Python Environment

Ensure Python 3.10+ is installed. Create an isolated Conda or virtual environment:

```bash
git clone <your-repo-url>
cd job_scraper

# Install dependencies
pip install google-genai playwright pydantic python-dotenv requests beautifulsoup4

# Install Playwright browser binaries
playwright install chromium

```

---

## Configuration & Credentials

Create a `.env` file in the project root directory (Do not give the file a name before the dot, literally just name it `.env`):

```env
GEMINI_API_KEY=your_gemini_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_numeric_chat_id_here

```
> [!WARNING]
> **Do not share this file or its contents! These are your personal API keys and link straigt to your private sensitive data!**

### 1. Google Gemini API Setup

> [!IMPORTANT]
> **Consumer Subscriptions vs. Developer API:**
> A **Gemini Pro Web / Advanced Plan** (the interactive consumer chatbot) **does not cover API access**. The Developer API operates through **Google AI Studio / Google Cloud Platform** and requires its own API key.

1. Go to [Google AI Studio](https://aistudio.google.com/apikey).
2. Sign in with your Google account and click **Create API Key**.
3. Choose your plan:
* **Free Tier:** Free input and output tokens for standard models like `gemini-3.6-flash` or `gemini-3.7-flash` (limited to 15 Requests Per Minute, which is sufficient for daily scans).


* **Paid Tier (Pay-As-You-Go):** Link a Google Cloud Billing account under the project if you need higher burst limits. At Flash model pricing, scanning dozens of jobs costs fractions of a cent per run.




4. Copy the resulting key into `GEMINI_API_KEY` in your `.env` file.

---

### 2. Telegram Alert Bot Setup

1. Open Telegram, search for `@BotFather`, and start a conversation.
2. Send `/newbot` and follow the prompts to choose a display name and username.
3. Copy the HTTP API token provided by BotFather into `TELEGRAM_BOT_TOKEN` in your `.env` file.
4. Open the link to your new bot (e.g., `t.me/your_bot_username`) and click **Start** or send any message.
5. In your web browser, navigate to:
```text
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates

```


6. Locate `"chat":{"id": 123456789}` in the JSON response. Copy this numeric ID into `TELEGRAM_CHAT_ID` in `.env`.

---

### 3. Facebook Session Setup (One-Time Login)

Facebook requires an authenticated session to load group posts. To prevent automated login challenges, persist your cookies using a local browser profile:

1. Open `login.py` and run it:
```bash
python login.py

```


2. A Chromium window will open. Manually log into your Facebook account and complete any two-factor authentication.


3. The script waits 60 seconds before closing. Your login state is saved inside the `./fb_session` directory and reused in headless mode by `main.py`.



---

## Customizing Your Search Profile

### Tailoring Target Criteria (`evaluator.py`)

Open `evaluator.py` and modify `CANDIDATE_PROFILE` to reflect your target roles, accepted experience limits, tech stack, and location constraints:

```python
CANDIDATE_PROFILE = """
Candidate Context:
- Current 3rd-year Software Engineering student.

Acceptance Criteria:
- Experience Level: Student / Intern / Junior (0-1 years required experience).
- Primary Tech: Rust, C++, Python, Low-level/Embedded Systems.
- Locations: Be'er Sheva, Southern District, Remote, or Hybrid.

Strict Rejection Criteria (is_relevant = False):
- Roles requiring 2+ years of professional industry experience.
- Non-developer roles (IT, Sales, Support, HR).
"""

```

### Configuring Search Queries (`main.py`)

In `main.py`, uncomment or modify the Facebook group URL and customize your LinkedIn query list:

```python
# Facebook Group
GROUP_URL = "https://www.facebook.com/groups/YOUR_GROUP_ID"

# LinkedIn Keywords
SEARCH_QUERIES = [
    "Software Engineering Student",
    "Embedded Student",
    "Junior Software Engineer",
    "סטודנט תוכנה",
    "מפתח C++",
]

```

---

## Running the Scraper

### Manual Execution

Run the scanner directly from your terminal:

```bash
python -u main.py

```

* **Duplicate Prevention:** Posts evaluated on previous runs are indexed by hash/Job ID in `seen_posts.db` and skipped automatically.


* **Resetting Cache:** To re-evaluate all current listings from scratch, delete the local cache file:
```bash
rm seen_posts.db
# Or on Windows PowerShell:
Remove-Item seen_posts.db -ErrorAction Ignore

```



---

## Automated Scheduling

### Windows Task Scheduler

To run the scraper automatically once or twice a day:

1. Press `Win + R`, type `taskschd.msc`, and press Enter.
2. Select **Create Basic Task...** in the right-hand panel.
3. Set the trigger to **Daily** (e.g., 09:00 AM).
4. For the Action, select **Start a program**:
* **Program/script:** Full path to your Python interpreter (e.g., `C:\Users\<Username>\anaconda3\python.exe` or virtualenv path).
* **Add arguments:** `-u main.py`
* **Start in:** Full directory path of your `job_scraper` folder.


5. Save the task. Test it by right-clicking it in the **Task Scheduler Library** and clicking **Run**.

---

## File Reference

| File | Purpose |
| --- | --- |
| `main.py` | Orchestrates the Facebook and LinkedIn scraping passes.

 |
| `linkedin_scraper.py` | Fetches listings via LinkedIn's guest endpoint and parses job metadata.

 |
| `evaluator.py` | Calls the Gemini API with structured Pydantic schema validation.

 |
| `notifier.py` | Formats and dispatches markdown alerts to your Telegram chat.

 |
| `db.py` | Lightweight SQLite helper for tracking seen post IDs.

 |
| `login.py` | Headed browser launcher for logging into Facebook once.

 |
