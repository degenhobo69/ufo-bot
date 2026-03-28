import asyncio
import requests
import time
from telegram import Bot

BOT_TOKEN = "8642772204:AAHzXM8h8i4vJdLZIx7j6wMLgV80AGwCN14"
CHAT_ID = "527677115"

HEADERS = {"User-Agent": "Mozilla/5.0"}

sent = set()


# ✅ SAFE REQUEST (WITH DEBUG)
def safe_get(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        print("Status:", r.status_code)

        if r.status_code != 200:
            return None

        return r

    except Exception as e:
        print("Request failed:", e)
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


# 🔴 REDDIT (MULTI-ENDPOINT + FALLBACK)
def scrape_reddit():
    urls = [
        "https://www.reddit.com/r/UFOs/new.json?limit=25",
        "https://www.reddit.com/r/UFOs/hot.json?limit=25"
    ]

    posts = []
    now = time.time()

    for url in urls:
        r = safe_get(url)
        if not r:
            continue

        try:
            data = r.json()
        except:
            continue

        for post in data["data"]["children"]:
            try:
                p = post["data"]

                title = p["title"]
                link = "https://reddit.com" + p["permalink"]
                upvotes = p["ups"]
                created = p["created_utc"]

                # ⏱ LAST 12 HOURS
                if now - created > 43200:
                    continue

                if link in sent:
                    continue

                score = get_score(upvotes, created)

                posts.append((title, link, upvotes, score))
                sent.add(link)

            except:
                continue

        if posts:
            break  # stop if one endpoint works

    # 🚨 GUARANTEE OUTPUT
    if not posts:
        print("⚠️ No Reddit data — sending fallback")

        posts.append((
            "No fresh UFO posts detected — monitoring continues...",
            "https://reddit.com/r/UFOs",
            0,
            0
        ))

    return posts[:5]


# 🛸 GOOGLE NEWS (ALWAYS RETURNS)
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

        posts.append((title, link))

    return posts


# 🚀 MAIN LOOP
async def main():
    bot = Bot(token=BOT_TOKEN)

    while True:
        print("Running FINAL scraper...")

        # 🔴 REDDIT
        try:
            for title, link, upvotes, score in scrape_reddit():

                prefix = "🚨 BREAKING UFO INTEL" if is_breaking(title) else "🛸 UFO SIGNAL"

                msg = (
                    f"{prefix}\n\n"
                    f"📈 Momentum: {round(score,1)}\n"
                    f"🔥 {upvotes} upvotes\n\n"
                    f"{title}\n\n"
                    f"🧠 {summarize(title)}\n\n"
                    f"🔗 {link}\n\n"
                    f"⚡ Live updates every 2 min"
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
