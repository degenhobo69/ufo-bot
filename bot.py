print("🚀 VERSION 6 LIVE (VIRAL SPIKE DETECTOR) 🚀")

import asyncio
import requests
import time
import xml.etree.ElementTree as ET
from telegram import Bot

BOT_TOKEN = "8642772204:AAHzXM8h8i4vJdLZIx7j6wMLgV80AGwCN14"
CHAT_ID = "@ufoalerts"

seen_posts = {}
last_heartbeat = 0


# 🚨 BREAKING KEYWORDS
def is_breaking(title):
    keywords = ["breaking", "leak", "confirmed", "pentagon", "urgent"]
    return any(k in title.lower() for k in keywords)


# 🧠 SUMMARY
def summarize(text):
    return " ".join(text.split()[:10]) + "..."


# 🔴 RSS SCRAPER
def scrape_rss(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/new/.rss"

    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return []

        root = ET.fromstring(r.content)
        posts = []

        for item in root.findall(".//item")[:10]:
            title = item.find("title").text
            link = item.find("link").text

            posts.append((title, link))

        return posts

    except:
        return []


# 🚀 MAIN LOOP
async def main():
    global last_heartbeat

    bot = Bot(token=BOT_TOKEN)
    subs = ["UFOs", "aliens", "HighStrangeness"]

    while True:
        print("Scanning for viral spikes...")

        detected_signals = []

        for sub in subs:
            posts = scrape_rss(sub)
            now = time.time()

            for title, link in posts:

                # first time seen
                if link not in seen_posts:
                    seen_posts[link] = {
                        "first_seen": now,
                        "count": 1
                    }
                    continue

                # seen again → possible spike
                seen_posts[link]["count"] += 1
                age = now - seen_posts[link]["first_seen"]

                # 🚨 SPIKE CONDITION
                if (
                    seen_posts[link]["count"] >= 2 and
                    age < 600  # within 10 minutes
                ):
                    detected_signals.append((title, link))

            await asyncio.sleep(2)

        # 🚨 SEND SIGNALS
        if detected_signals:
            print("🚨 VIRAL SPIKE DETECTED")

            for title, link in detected_signals[:3]:

                if is_breaking(title):
                    prefix = "🚨 BREAKING UFO INTEL"
                else:
                    prefix = "⚡ VIRAL SPIKE DETECTED"

                msg = (
                    f"{prefix}\n\n"
                    f"{title}\n\n"
                    f"🧠 {summarize(title)}\n\n"
                    f"🔗 {link}\n\n"
                    f"⚡ Join: https://t.me/yourchannelname"
                )

                try:
                    await bot.send_message(chat_id=CHAT_ID, text=msg)
                except Exception as e:
                    print("Telegram error:", e)

        # 💓 HEARTBEAT (20 min)
        if time.time() - last_heartbeat > 1200:
            print("💓 Heartbeat")

            msg = (
                "🛸 Monitoring UFO & alien activity...\n\n"
                "Scanning for viral spikes ⚡\n\n"
                "Standby 🚨\n\n"
                "⚡ Join: https://t.me/ufoalerts"
            )

            try:
                await bot.send_message(chat_id=CHAT_ID, text=msg)
                last_heartbeat = time.time()
            except:
                pass

        await asyncio.sleep(120)


asyncio.run(main())
