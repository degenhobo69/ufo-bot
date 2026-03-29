print("🚀 VERSION 8 LIVE (CONFIDENCE ENGINE) 🚀")

import asyncio
import requests
import time
from telegram import Bot

BOT_TOKEN = "8642772204:AAHzXM8h8i4vJdLZIx7j6wMLgV80AGwCN14"
CHAT_ID = "@ufoalerts"

seen = {}
last_heartbeat = 0


# 🚨 BREAKING
def is_breaking(title):
    keywords = ["breaking", "leak", "confirmed", "pentagon", "urgent"]
    return any(k in title.lower() for k in keywords)


# 🧠 SUMMARY
def summarize(text):
    return " ".join(text.split()[:10]) + "..."


# 📊 CONFIDENCE SCORE
def get_confidence(count, age, breaking):
    score = 0

    # 🔁 repetition weight
    score += min(count * 25, 60)

    # ⏱ speed boost (faster = higher)
    if age < 300:
        score += 25
    elif age < 600:
        score += 15

    # 🚨 breaking boost
    if breaking:
        score += 15

    return min(score, 100)


# 🔴 FETCH VIA PROXY
def fetch_posts(sub):
    url = f"https://api.allorigins.win/get?url=https://www.reddit.com/r/{sub}/new.json"

    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return []

        data = r.json()["contents"]
        data = eval(data)

        posts = []
        for p in data["data"]["children"][:10]:
            title = p["data"]["title"]
            link = "https://reddit.com" + p["data"]["permalink"]
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
        print("Scanning with confidence engine...")

        signals = []
        now = time.time()

        for sub in subs:
            posts = fetch_posts(sub)

            for title, link in posts:

                if link not in seen:
                    seen[link] = {"time": now, "count": 1}
                    continue

                seen[link]["count"] += 1
                age = now - seen[link]["time"]

                breaking = is_breaking(title)
                confidence = get_confidence(seen[link]["count"], age, breaking)

                # ⚡ SIGNAL THRESHOLD
                if confidence >= 60:
                    signals.append((title, link, confidence))

            await asyncio.sleep(2)

        # 🚨 SEND SIGNALS
        if signals:
            print("🚨 HIGH CONFIDENCE SIGNAL")

            for title, link, confidence in signals[:3]:

                prefix = "🚨 BREAKING UFO INTEL" if is_breaking(title) else "⚡ VIRAL SIGNAL"

                msg = (
                    f"{prefix}\n\n"
                    f"📊 Confidence: {confidence}%\n\n"
                    f"{title}\n\n"
                    f"🧠 {summarize(title)}\n\n"
                    f"🔗 {link}\n\n"
                    f"⚡ Join: https://t.me/yourchannelname"
                )

                try:
                    await bot.send_message(chat_id=CHAT_ID, text=msg)
                except Exception as e:
                    print("Telegram error:", e)

        # 💓 HEARTBEAT
        if now - last_heartbeat > 1200:
            print("💓 Heartbeat")

            msg = (
                "🛸 Monitoring UFO activity...\n\n"
                "AI Confidence Engine Active 📊\n\n"
                "Scanning for high-probability signals ⚡\n\n"
                "⚡ Join: https://t.me/ufoalerts"
            )

            try:
                await bot.send_message(chat_id=CHAT_ID, text=msg)
                last_heartbeat = now
            except:
                pass

        await asyncio.sleep(120)


asyncio.run(main())
