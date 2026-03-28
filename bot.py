import asyncio
import requests
import time
from telegram import Bot

BOT_TOKEN = "8642772204:AAHzXM8h8i4vJdLZIx7j6wMLgV80AGwCN14"
CHAT_ID = "527677115"

HEADERS = {"User-Agent": "Mozilla/5.0"}

sent = set()


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


# 🧠 SIMPLE SUMMARY
def summarize(text):
    return " ".join(text.split()[:10]) + "..."


# 🔥 VIRAL SCORE (RELAXED)
def get_score(upvotes, created):
    age_minutes = max((time.time() - created) / 60, 1)
    return upvotes / age_minutes


# 🔴 REDDIT (FIXED)
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

            # ⏱ ONLY LAST 90 MINUTES
            if now - created > 5400:
                continue

            # 🔥 RELAXED FILTER (MORE SIGNALS)
            score = get_score(upvotes, created)

            if score < 1.5:   # MUCH LOWER = more alerts
                continue

            # 🚫 prevent duplicates during runtime
            if link in sent:
                continue

            posts.append((title, link, upvotes, score))
            sent.add(link)

        except:
            continue

    return posts[:5]


# 🛸 NEWS (TIME FILTER)
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

        if link in sent:
            continue

        posts.append((title, link))
        sent.add(link)

    return posts


# 🚀 MAIN LOOP
async def main():
    bot = Bot(token=BOT_TOKEN)

    while True:
        print("Running ELITE FIXED scraper...")

        try:
            reddit_posts = scrape_reddit()

            for title, link, upvotes, score in reddit_posts:

                prefix = "🚨 BREAKING UFO INTEL" if is_breaking(title) else "🛸 EARLY UFO SIGNAL"

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

        try:
            news_posts = scrape_news()

            for title, link in news_posts:

                prefix = "🚨 BREAKING NEWS" if is_breaking(title) else "🛸 UFO NEWS"

                msg = (
                    f"{prefix}\n\n"
                    f"{title}\n\n"
                    f"🧠 {summarize(title)}\n\n"
                    f"🔗 {link}\n\n"
                    f"⚡ Stay updated"
                )

                await bot.send_message(chat_id=CHAT_ID, text=msg)

        except Exception as e:
            print("News error:", e)

        await asyncio.sleep(180)  # every 3 minutes


asyncio.run(main())
