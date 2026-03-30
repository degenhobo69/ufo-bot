print("🚀 VERSION 9 LIVE (ELITE MULTI-SOURCE ENGINE) 🚀")

import asyncio
import requests
import time
import random
from telegram import Bot

BOT_TOKEN = "8642772204:AAHzXM8h8i4vJdLZIx7j6wMLgV80AGwCN14"
CHAT_ID = "@ufoalerts"

seen = {}
tweet_seen = {}
last_heartbeat = 0


# 🐦 NITTER MIRRORS (ROTATING)
NITTERS = [
    "https://nitter.net",
    "https://nitter.unixfox.eu",
    "https://nitter.poast.org",
    "https://nitter.privacydev.net"
]


# 🚨 BREAKING
def is_breaking(text):
    keywords = ["breaking", "leak", "confirmed", "pentagon", "urgent"]
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


# 🛸 REDDIT VIA PROXY
def fetch_reddit(sub):
    url = f"https://api.allorigins.win/get?url=https://www.reddit.com/r/{sub}/new.json"

    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return []

        data = eval(r.json()["contents"])

        posts = []
        for p in data["data"]["children"][:10]:
            title = p["data"]["title"]
            link = "https://reddit.com" + p["data"]["permalink"]
            posts.append((title, link))

        return posts
    except:
        return []


# 🐦 TWITTER (ROTATING NITTER + VELOCITY)
def fetch_twitter():
    keywords = ["ufo", "aliens", "uap", "pentagon"]
    tweets = []

    base = random.choice(NITTERS)

    for kw in keywords:
        url = f"{base}/search?f=tweets&q={kw}"

        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                continue

            html = r.text.split("timeline-item")

            for block in html[1:4]:
                try:
                    text = block.split("tweet-content")[1].split(">")[1].split("<")[0]
                    link = base + block.split('href="')[1].split('"')[0]

                    tweets.append((text.strip(), link))
                except:
                    continue

        except:
            continue

    return tweets


# 🚀 MAIN LOOP
async def main():
    global last_heartbeat

    bot = Bot(token=BOT_TOKEN)
    subs = ["UFOs", "aliens", "HighStrangeness"]

    while True:
        print("🔥 Scanning multi-source signals...")

        signals = []
        now = time.time()

        # 🛸 REDDIT SCAN
        for sub in subs:
            posts = fetch_reddit(sub)

            for title, link in posts:

                if link not in seen:
                    seen[link] = {"time": now, "count": 1}
                    continue

                seen[link]["count"] += 1
                age = now - seen[link]["time"]

                breaking = is_breaking(title)
                confidence = get_confidence(seen[link]["count"], age, breaking)

                if confidence >= 40:
                    signals.append((title, link, confidence))

            await asyncio.sleep(1)

        # 🐦 TWITTER SCAN
        tweets = fetch_twitter()

        for text, link in tweets:

            if link not in tweet_seen:
                tweet_seen[link] = {"time": now, "count": 1}
                continue

            tweet_seen[link]["count"] += 1
            age = now - tweet_seen[link]["time"]

            breaking = is_breaking(text)
            confidence = get_confidence(tweet_seen[link]["count"], age, breaking)

            if confidence >= 40:
                signals.append((text, link, confidence))

        # 🚨 SEND SIGNALS
        if signals:
            print("🚨 SIGNAL DETECTED")

            for title, link, confidence in signals[:5]:

                prefix = "🚨 BREAKING ALERT" if is_breaking(title) else "⚡ VIRAL SIGNAL"

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
                "🛸 Multi-source scanner active\n\n"
                "Tracking Reddit + Twitter ⚡\n\n"
                "Detecting viral spikes...\n\n"
                "⚡ Join: https://t.me/ufoalerts"
            )

            try:
                await bot.send_message(chat_id=CHAT_ID, text=msg)
                last_heartbeat = now
            except:
                pass

        await asyncio.sleep(120)


asyncio.run(main())
