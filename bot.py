print("🚀 VERSION 14 LIVE (ALWAYS SIGNALS FIX) 🚀")

import asyncio
import requests
import time
import random
from telegram import Bot

BOT_TOKEN = "8642772204:AAHzXM8h8i4vJdLZIx7j6wMLgV80AGwCN14"
CHAT_ID = "ufoalerta"

seen = {}
tweet_seen = {}
last_heartbeat = 0

NITTERS = [
    "https://nitter.net",
    "https://nitter.unixfox.eu",
    "https://nitter.poast.org"
]

# 🚨 BREAKING
def is_breaking(text):
    keywords = ["breaking", "leak", "confirmed", "urgent"]
    return any(k in text.lower() for k in keywords)

# 🧠 SUMMARY
def summarize(text):
    return " ".join(text.split()[:12]) + "..."

# 📊 CONFIDENCE
def get_confidence(count, age, breaking):
    score = min(count * 25, 60)

    if age < 300:
        score += 25
    elif age < 600:
        score += 15

    if breaking:
        score += 15

    return min(score, 100)

# 🛸 REDDIT (NO FILTER)
def fetch_reddit(sub):
    url = f"https://api.allorigins.win/get?url=https://www.reddit.com/r/{sub}/new.json"

    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            print("Reddit failed")
            return []

        data = eval(r.json()["contents"])

        posts = []
        for p in data["data"]["children"][:10]:
            title = p["data"]["title"]
            link = "https://reddit.com" + p["data"]["permalink"]
            posts.append((title, link))

        print(f"Reddit posts: {len(posts)}")
        return posts

    except Exception as e:
        print("Reddit error:", e)
        return []

# 🐦 TWITTER (OPTIONAL)
def fetch_twitter():
    tweets = []
    base = random.choice(NITTERS)

    try:
        url = f"{base}/search?f=tweets&q=ufo"
        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            return []

        html = r.text

        if "timeline-item" not in html:
            return []

        blocks = html.split("timeline-item")

        for block in blocks[1:3]:
            try:
                text = block.split("tweet-content")[1].split(">")[1].split("<")[0]
                link = base + block.split('href="')[1].split('"')[0]
                tweets.append((text.strip(), link))
            except:
                continue

    except:
        pass

    print(f"Tweets: {len(tweets)}")
    return tweets

# 🚀 MAIN LOOP
async def main():
    global last_heartbeat

    bot = Bot(token=BOT_TOKEN)
    subs = ["UFOs", "aliens", "HighStrangeness"]

    while True:
        print("\n🔥 NEW SCAN 🔥")

        signals = []
        now = time.time()

        # 🛸 REDDIT (PRIMARY SOURCE)
        for sub in subs:
            posts = fetch_reddit(sub)

            for title, link in posts:

                # ✅ ALWAYS SEND FIRST TIME
                if link not in seen:
                    seen[link] = {"time": now, "count": 1}
                    signals.append((title, link, 40))
                    continue

                seen[link]["count"] += 1
                age = now - seen[link]["time"]

                confidence = get_confidence(
                    seen[link]["count"],
                    age,
                    is_breaking(title)
                )

                if confidence >= 30:
                    signals.append((title, link, confidence))

            await asyncio.sleep(1)

        # 🐦 TWITTER (BONUS)
        tweets = fetch_twitter()

        for text, link in tweets:
            if link not in tweet_seen:
                tweet_seen[link] = {"time": now, "count": 1}
                signals.append((text, link, 35))
                continue

        # 🚨 GUARANTEE OUTPUT
        if not signals:
            print("Fallback triggered")

            signals.append((
                "Scanning for UFO activity — no strong signals yet...",
                "https://reddit.com/r/UFOs",
                25
            ))

        print(f"Signals sending: {len(signals)}")

        for title, link, confidence in signals[:5]:

            if confidence >= 80:
                tag = "🔥 TOP 1% SIGNAL"
            elif confidence >= 60:
                tag = "🚨 HIGH CONFIDENCE"
            elif confidence >= 30:
                tag = "⚡ LIVE SIGNAL"
            else:
                tag = "🛸 MONITORING"

            msg = (
                f"{tag}\n\n"
                f"📊 Confidence: {confidence}%\n\n"
                f"{title}\n\n"
                f"🧠 {summarize(title)}\n\n"
                f"🔗 {link}\n\n"
                f"⚡ Join: https://t.me/ufoalerts"
            )

            try:
                await bot.send_message(chat_id=CHAT_ID, text=msg)
            except Exception as e:
                print("Telegram error:", e)

        # 💓 HEARTBEAT
        if now - last_heartbeat > 1200:
            try:
                await bot.send_message(
                    chat_id=CHAT_ID,
                    text="🛸 Scanner active — tracking UFO signals ⚡"
                )
                last_heartbeat = now
            except:
                pass

        await asyncio.sleep(120)

asyncio.run(main())
