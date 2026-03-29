import asyncio
import requests
import time
from telegram import Bot

BOT_TOKEN = "8642772204:AAHzXM8h8i4vJdLZIx7j6wMLgV80AGwCN14"
CHAT_ID = "@ufoalerts"

sent = set()


# ✅ SAFE REQUEST (NO HEADERS NEEDED NOW)
def safe_get(url):
    try:
        r = requests.get(url, timeout=10)
        print("Status:", r.status_code)
        if r.status_code != 200:
            return None
        return r.json()
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


# 🔥 SCORE
def get_score(upvotes, created):
    age_minutes = max((time.time() - created) / 60, 1)
    return upvotes / age_minutes


# 🔴 REDDIT VIA MIRROR (NO BLOCK)
def scrape_subreddit(subreddit):
    url = f"https://api.pushshift.io/reddit/search/submission/?subreddit={subreddit}&size=20&sort=desc&sort_type=created"

    data = safe_get(url)
    if not data:
        return []

    posts = []
    now = time.time()

    for p in data["data"]:
        try:
            title = p["title"]
            link = "https://reddit.com" + p["permalink"]
            upvotes = p.get("score", 0)
            created = p["created_utc"]

            # ⏱ LAST 12 HOURS
            if now - created > 43200:
                continue

            if link in sent:
                continue

            score = get_score(upvotes, created)

            if score > 0.1:  # VERY AGGRESSIVE
                posts.append((title, link, upvotes, score))
                sent.add(link)

        except:
            continue

    return posts


# 🚀 MAIN LOOP
async def main():
    bot = Bot(token=BOT_TOKEN)

    while True:
        print("Running STABLE scraper...")

        all_posts = []

        try:
            all_posts += scrape_subreddit("UFOs")
            all_posts += scrape_subreddit("aliens")
        except Exception as e:
            print("Scraping error:", e)

        # 🚨 FALLBACK
        if not all_posts:
            print("⚠️ No data — fallback triggered")
            all_posts.append((
                "Monitoring UFO & alien activity... no major signals yet.",
                "https://reddit.com/r/UFOs",
                0,
                0
            ))

        all_posts = all_posts[:5]

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

        await asyncio.sleep(180)  # every 3 minutes


asyncio.run(main())
