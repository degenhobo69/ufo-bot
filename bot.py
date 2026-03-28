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


# 🔥 MOMENTUM SCORE
def get_score(upvotes, created):
    age_minutes = max((time.time() - created) / 60, 1)
    return upvotes / age_minutes


# 🔴 AGGRESSIVE REDDIT SCRAPER
def scrape_reddit():
    url = "https://www.reddit.com/r/UFOs/new.json?limit=30"
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

            # ⏱ LAST 6 HOURS
            if now - created > 21600:
                continue

            score = get_score(upvotes, created)

            # 🔥 VERY LOW THRESHOLD (AGGRESSIVE)
            if score > 0.3:
                if link not in sent:
                    posts.append((title, link, upvotes, score))
                    sent.add(link)

        except:
            continue

    # 🚨 FORCE CONTENT IF EMPTY
    if not posts:
        for post in r.json()["data"]["children"][:3]:
            try:
                p = post["data"]
                title = p["title"]
                link = "https://reddit.com" + p["permalink"]
                upvotes = p["ups"]
                score = get_score(upvotes, p["created_utc"])

                if link not in sent:
                    posts.append((title, link, upvotes, score))
                    sent.add(link)
            except:
                continue

    return posts[:5]


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
        print("Running AGGRESSIVE scraper...")

        # 🔴 REDDIT
        try:
            for title, link, upvotes, score in scrape_reddit():

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

        # 🛸 NEWS
        try:
            for title, link in scrape_news():

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

        await asyncio.sleep(120)  # ⏱ every 2 minutes


asyncio.run(main())
