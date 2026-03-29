print("🚀 VERSION 4 LIVE (NO BLOCK) 🚀")

import asyncio
import requests
import time
import xml.etree.ElementTree as ET
from telegram import Bot

BOT_TOKEN = "8642772204:AAHzXM8h8i4vJdLZIx7j6wMLgV80AGwCN14"
CHAT_ID = "@ufoalerts"

sent = {}


# 🚨 BREAKING DETECTION
def is_breaking(title):
    keywords = ["breaking", "leak", "confirmed", "pentagon", "urgent"]
    return any(word in title.lower() for word in keywords)


# 🧠 SIMPLE SUMMARY
def summarize(text):
    return " ".join(text.split()[:10]) + "..."


# 🔴 RSS VIA PROXY (NO RATE LIMIT)
def scrape_rss(subreddit):
    url = f"https://r.jina.ai/http://www.reddit.com/r/{subreddit}/new/.rss"

    try:
        r = requests.get(url, timeout=10)
        print(f"Proxy RSS ({subreddit}):", r.status_code)

        if r.status_code != 200:
            return []

        root = ET.fromstring(r.content)
        posts = []

        for item in root.findall(".//item")[:10]:
            title = item.find("title").text
            link = item.find("link").text

            # allow resend after 30 min
            if link in sent and time.time() - sent[link] < 1800:
                continue

            posts.append((title, link))
            sent[link] = time.time()

        return posts

    except Exception as e:
        print("RSS error:", e)
        return []


# 🚀 MAIN LOOP
async def main():
    bot = Bot(token=BOT_TOKEN)

    subs = ["UFOs", "aliens", "HighStrangeness"]

    while True:
        print("Running PROXY scraper (NO BLOCK)...")

        all_posts = []

        try:
            for sub in subs:
                all_posts += scrape_rss(sub)
                await asyncio.sleep(2)
        except Exception as e:
            print("Scraping error:", e)

        # fallback (never silent)
        if not all_posts:
            print("⚠️ No data — fallback triggered")
            all_posts.append((
                "🛸 Monitoring UFO & alien activity… stay tuned for signals",
                "https://reddit.com/r/UFOs"
            ))

        all_posts = all_posts[:5]

        for title, link in all_posts:

            prefix = "🚨 BREAKING UFO INTEL" if is_breaking(title) else "🛸 UFO / ALIEN SIGNAL"

            msg = (
                f"{prefix}\n\n"
                f"{title}\n\n"
                f"🧠 {summarize(title)}\n\n"
                f"🔗 {link}\n\n"
                f"⚡ Join: https://t.me/ufoalerts"
            )

            try:
                await bot.send_message(chat_id=CHAT_ID, text=msg)
            except Exception as e:
                print("Telegram error:", e)

        await asyncio.sleep(180)


asyncio.run(main())
