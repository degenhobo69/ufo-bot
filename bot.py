print("🌍 VERSION 13 LIVE (GLOBAL DOMINATION MODE) 🌍")

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

NITTERS = [
    "https://nitter.net",
    "https://nitter.unixfox.eu",
    "https://nitter.poast.org",
    "https://nitter.privacydev.net"
]

KEYWORDS = [
    "ufo", "aliens", "uap",
    "ovni", "ovnis", "extraterrestre", "alienigena"
]

# 🌎 LANGUAGE DETECTION
def detect_lang(text):
    if any(word in text.lower() for word in ["ovni", "extraterrestre", "avistamiento"]):
        return "ES"
    return "EN"

# 🌐 FAKE TRANSLATION (fast + no API)
def translate(text):
    return "🌐 " + text[:120] + "..."

# 🚨 BREAKING
def is_breaking(text):
    keywords = ["breaking", "leak", "confirmed", "urgent", "última hora"]
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

# 🛸 REDDIT
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

            if any(k in title.lower() for k in KEYWORDS):
                posts.append((title, link))

        return posts
    except:
        return []

# 🐦 TWITTER
def fetch_twitter():
    tweets = []
    base = random.choice(NITTERS)

    for kw in KEYWORDS:
        url = f"{base}/search?f=tweets&q={kw}"

        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                continue

            html = r.text

            if "timeline-item" not in html:
                continue

            blocks = html.split("timeline-item")

            for block in blocks[1:3]:
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
        print("\n🌍 GLOBAL SCAN ACTIVE 🌍")

        signals = []
        now = time.time()

        # 🛸 REDDIT
        for sub in subs:
            posts = fetch_reddit(sub)

            for title, link in posts:

                lang = detect_lang(title)

                if link not in seen:
                    seen[link] = {"time": now, "count": 1}
                    signals.append((title, link, 35, lang))
                    continue

                seen[link]["count"] += 1
                age = now - seen[link]["time"]

                confidence = get_confidence(
                    seen[link]["count"],
                    age,
                    is_breaking(title)
                )

                if confidence >= 30:
                    signals.append((title, link, confidence, lang))

            await asyncio.sleep(1)

        # 🐦 TWITTER
        tweets = fetch_twitter()

        for text, link in tweets:

            lang = detect_lang(text)

            if link not in tweet_seen:
                tweet_seen[link] = {"time": now, "count": 1}
                signals.append((text, link, 30, lang))
                continue

            tweet_seen[link]["count"] += 1
            age = now - tweet_seen[link]["time"]

            confidence = get_confidence(
                tweet_seen[link]["count"],
                age,
                is_breaking(text)
            )

            if confidence >= 25:
                signals.append((text, link, confidence, lang))

        # 🚨 FALLBACK
        if not signals:
            signals.append((
                "No major UFO/OVNI activity detected globally...",
                "https://reddit.com/r/UFOs",
                20,
                "EN"
            ))

        print(f"Signals: {len(signals)}")

        for title, link, confidence, lang in signals[:5]:

            if confidence >= 80:
                tag = "🔥 TOP 1% GLOBAL SIGNAL"
            elif confidence >= 60:
                tag = "🚨 HIGH CONFIDENCE EVENT"
            elif confidence >= 30:
                tag = "⚡ LIVE GLOBAL SIGNAL"
            else:
                tag = "🛸 MONITORING"

            region = "🌎" if lang == "ES" else "🇺🇸"

            translated = translate(title) if lang == "ES" else ""

            msg = (
                f"{tag} {region}\n\n"
                f"📊 Confidence: {confidence}%\n\n"
                f"{title}\n\n"
                f"{translated}\n\n"
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
                    text="🌍 Global UFO/OVNI scanner active — tracking signals worldwide ⚡"
                )
                last_heartbeat = now
            except:
                pass

        await asyncio.sleep(120)

asyncio.run(main())
