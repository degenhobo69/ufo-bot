import asyncio
import requests
import json
import time
from telegram import Bot

BOT_TOKEN = "8642772204:AAHzXM8h8i4vJdLZIx7j6wMLgV80AGwCN14"
CHAT_ID = "527677115"

HEADERS = {"User-Agent": "Mozilla/5.0"}
DATA_FILE = "data.json"


# ✅ LOAD / SAVE
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"sent": []}


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
    keywords = ["breaking", "leak", "confirmed", "pentagon", "urgent"]
    return any(word in title.lower() for word in keywords)


# 🧠 SMART SUMMARY
def summarize(text):
    words = text.split()
    short = " ".join(words[:10])

    return f"{short}..."


# 🔥 VIRAL SCORE (KEY FEATURE)
def get_score(upvotes, created):
    age_minutes = max((time.time() - created) / 60, 1)
    return upvotes / age_minutes


# 🔴 REDDIT ELITE SCRAPER
def scrape_reddit():
    url = "https://www.reddit.com/r/UFOs/new.json?limit=25"
    r = safe_get(url)
    if not r:
        return []

    posts = []
    now = time.time()

    for post in r.json()["data"]["children"]:
        try:
            p = post["data"]

            title = p["title"]
            link = "https://reddit.com" + p["permalink"]
            upvotes = p["ups"]
            created = p["created_utc"]

            # ⏱ ONLY LAST 3 HOURS
            if now - created > 10800:
                continue

            # 📈 VIRAL SCORE
            score = get_score(upvotes, created)

            # 🔥 ELITE FILTER (early + strong growth)
            if score < 5:
                continue

            if link not in sent:
                posts.append((title, link, upvotes, score))
                sent.add(link)

        except:
            continue

    # sort by score (best first)
    posts.sort(key=lambda x: x[3], reverse=True)

    return posts[:5]


# 🛸 NEWS
def scrape_news():
    url = "https://news.google.com/rss/search?q=UFO+OR+UAP+OR+aliens"
    r = safe_get(url)
    if not r:
        return []

    import xml.etree.ElementTree as ET
    root = ET.fromstring(r.content)

    posts = []

    for item in root.findall(".//item")[:3]:
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
        print("Running ELITE scraper...")

        # 🔴 REDDIT
        try:
            for title, link, upvotes, score in scrape_reddit():

                if is_breaking(title):
                    prefix = "🚨 BREAKING UFO INTEL"
                else:
                    prefix = "🛸 EARLY UFO SIGNAL"

                msg = (
                    f"{prefix}\n\n"
                    f"📈 Momentum: {round(score,1)}\n"
                    f"🔥 {upvotes} upvotes\n\n"
                    f"{title}\n\n"
                    f"🧠 {summarize(title)}\n\n"
                    f"🔗 {link}\n\n"
                    f"⚡ Join for real-time UFO alerts"
                )

                await bot.send_message(chat_id=CHAT_ID, text=msg)

        except Exception as e:
            print("Reddit error:", e)

        # 🛸 NEWS
        try:
            for title, link in scrape_news():

                if is_breaking(title):
                    prefix = "🚨 BREAKING NEWS"
                else:
                    prefix = "🛸 UFO NEWS"

                msg = (
                    f"{prefix}\n\n"
                    f"{title}\n\n"
                    f"🧠 {summarize(title)}\n\n"
                    f"🔗 {link}\n\n"
                    f"⚡ Stay updated with real-time alerts"
                )

                await bot.send_message(chat_id=CHAT_ID, text=msg)

        except Exception as e:
            print("News error:", e)

        # 💾 SAVE
        data["sent"] = list(sent)
        save_data(data)

        await asyncio.sleep(180)


asyncio.run(main())
