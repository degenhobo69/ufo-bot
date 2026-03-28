import asyncio
import requests
import json
import time
from telegram import Bot

BOT_TOKEN = "8642772204:AAHzXM8h8i4vJdLZIx7j6wMLgV80AGwCN14"

CHAT_ID = "527677115"

HEADERS = {"User-Agent": "Mozilla/5.0"}

DATA_FILE = "data.json"


# ✅ LOAD / SAVE DATA
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"sent": [], "last_run": 0}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


data = load_data()
sent = set(data["sent"])


# ✅ SAFE REQUEST
def safe_get(url):
    try:
        return requests.get(url, headers=HEADERS, timeout=10)
    except:
        return None


# 🚨 BREAKING DETECTION
def is_breaking(title):
    keywords = ["breaking", "just in", "leak", "confirmed", "pentagon", "urgent"]
    return any(word in title.lower() for word in keywords)


# 🧠 SMART SUMMARY
def summarize(text):
    words = text.split()
    short = " ".join(words[:12])

    if "ufo" in text.lower():
        return f"Sighting gaining attention. {short}..."
    elif "pentagon" in text.lower():
        return f"Government UFO activity reported. {short}..."
    elif "alien" in text.lower():
        return f"Possible extraterrestrial discussion trending. {short}..."
    elif "leak" in text.lower():
        return f"Potential leak or insider info. {short}..."
    else:
        return f"Trending UFO report. {short}..."


# 🔴 REDDIT (NEW + VIRAL ONLY)
def scrape_reddit():
    url = "https://www.reddit.com/r/UFOs/new.json?limit=20"
    r = safe_get(url)
    if not r:
        return []

    now = time.time()
    posts = []

    data_json = r.json()

    for post in data_json["data"]["children"]:
        try:
            p = post["data"]
            title = p["title"]
            link = "https://reddit.com" + p["permalink"]
            upvotes = p["ups"]
            created = p["created_utc"]

            # ⏱ ONLY LAST 2 HOURS
            if now - created > 7200:
                continue

            # 🔥 VIRAL FILTER (dynamic)
            if upvotes < 300:
                continue

            if link not in sent:
                posts.append((title, link, upvotes))
                sent.add(link)

        except:
            continue

    return posts


# 🛸 GOOGLE NEWS
def scrape_news():
    url = "https://news.google.com/rss/search?q=UFO+OR+UAP+OR+aliens"
    r = safe_get(url)
    if not r:
        return []

    import xml.etree.ElementTree as ET
    root = ET.fromstring(r.content)

    posts = []

    for item in root.findall(".//item")[:5]:
        title = item.find("title").text
        link = item.find("link").text

        if link not in sent:
            posts.append((title, link))
            sent.add(link)

    return posts


# 🚀 MAIN LOOP
async def main():
    bot = Bot(token=BOT_TOKEN)

    while True:
        print("Running smart scraper...")

        new_posts = []

        # 🔴 REDDIT
        try:
            new_posts += scrape_reddit()
        except Exception as e:
            print("Reddit error:", e)

        # 🛸 NEWS
        try:
            news_posts = scrape_news()
            for title, link in news_posts:
                new_posts.append((title, link, 0))
        except Exception as e:
            print("News error:", e)

        # 🚫 LIMIT (anti-spam)
        new_posts = new_posts[:5]

        # 📤 SEND
        for title, link, upvotes in new_posts:
            summary = summarize(title)

            if is_breaking(title):
                prefix = "🚨 BREAKING UFO ALERT"
            else:
                prefix = "🛸 UFO ALERT"

            if upvotes > 0:
                msg = f"{prefix}\n\n🔥 {upvotes} upvotes\n\n{title}\n\n🧠 {summary}\n\n🔗 {link}"
            else:
                msg = f"{prefix}\n\n{title}\n\n🧠 {summary}\n\n🔗 {link}"

            await bot.send_message(chat_id=CHAT_ID, text=msg)

        # 💾 SAVE STATE
        data["sent"] = list(sent)
        data["last_run"] = time.time()
        save_data(data)

        await asyncio.sleep(180)  # every 3 min


asyncio.run(main())
