import asyncio
import requests
import time
from telegram import Bot

BOT_TOKEN = "8642772204:AAHzXM8h8i4vJdLZIx7j6wMLgV80AGwCN14"
CHAT_ID = "@ufoalerts"

HEADERS = {"User-Agent": "Mozilla/5.0"}

sent = set()


# ✅ SAFE REQUEST
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


# 🔴 GENERIC REDDIT SCRAPER
def scrape_subreddit(subreddit):
    urls = [
        f"https://www.reddit.com/r/{subreddit}/new.json?limit=25",
        f"https://www.reddit.com/r/{subreddit}/hot.json?limit=25"
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
            break

    return posts


# 🚀 MAIN LOOP
async def main():
    bot = Bot(token=BOT_TOKEN)

    while True:
        print("Running REDDIT UFO + ALIENS scraper...")

        all_posts = []

        try:
            # 🛸 UFOs
            all_posts += scrape_subreddit("UFOs")

            # 👽 Aliens
            all_posts += scrape_subreddit("aliens")

        except Exception as e:
            print("Scraping error:", e)

        # 🚨 FORCE CONTENT IF EMPTY
        if not all_posts:
            print("⚠️ No data — fallback triggered")
            all_posts.append((
                "Monitoring UFO & alien activity... no major signals yet.",
                "https://reddit.com/r/UFOs",
                0,
                0
            ))

        # 🔥 LIMIT
        all_posts = all_posts[:6]

        # 📤 SEND
        for title, link, upvotes, score in all_posts:

            prefix = "🚨 BREAKING UFO INTEL" if is_breaking(title) else "🛸 UFO / ALIEN SIGNAL"

            msg = (
                f"{prefix}\n\n"
                f"📈 Momentum: {round(score,1)}\n"
                f"🔥 {upvotes} upvotes\n\n"
                f"{title}\n\n"
                f"🧠 {summarize(title)}\n\n"
                f"🔗 {link}"
            )

            try:
                await bot.send_message(chat_id=CHAT_ID, text=msg)
            except Exception as e:
                print("Telegram error:", e)

        await asyncio.sleep(120)  # every 2 minutes


asyncio.run(main())
