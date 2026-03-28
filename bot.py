import asyncio
import requests
from telegram import Bot
from openai import OpenAI

BOT_TOKEN = "8642772204:AAHzXM8h8i4vJdLZIx7j6wMLgV80AGwCN14"
CHAT_ID = "527677115"

client = OpenAI()

sent = set()

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# ✅ SAFE REQUEST
def safe_get(url):
    try:
        return requests.get(url, headers=HEADERS, timeout=10)
    except:
        return None


# 🔥 BREAKING DETECTION
def is_breaking(title):
    keywords = ["breaking", "just in", "leak", "confirmed", "pentagon", "urgent"]
    title_lower = title.lower()
    return any(word in title_lower for word in keywords)


# 🔴 REDDIT (TOP 5% FILTER)
def scrape_reddit():
    url = "https://www.reddit.com/r/UFOs/top.json?t=day&limit=20"
    r = safe_get(url)
    if not r:
        return []

    data = r.json()
    posts = []

    for post in data["data"]["children"]:
        try:
            p = post["data"]
            title = p["title"]
            link = "https://reddit.com" + p["permalink"]
            upvotes = p["ups"]

            # 🔥 TOP 5% (strict filter)
            if upvotes > 1500:
                if link not in sent:
                    posts.append((title, link, upvotes))
                    sent.add(link)

        except:
            continue

    return posts


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
            posts.append((title, link, 0))
            sent.add(link)

    return posts


# 🧠 AI SUMMARY
def summarize(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Summarize this UFO news in 1-2 short punchy lines, make it engaging."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("AI error:", e)
        return ""


# 🚀 MAIN LOOP
async def main():
    bot = Bot(token=BOT_TOKEN)

    while True:
        print("Running scraper...")

        # 🔴 REDDIT
        try:
            for title, link, upvotes in scrape_reddit():
                summary = summarize(title)

                if is_breaking(title):
                    prefix = "🚨 BREAKING UFO ALERT"
                else:
                    prefix = "🛸 VIRAL UFO POST"

                msg = f"{prefix}\n\n🔥 {upvotes} upvotes\n\n{title}\n\n🧠 {summary}\n\n🔗 {link}"
                await bot.send_message(chat_id=CHAT_ID, text=msg)

        except Exception as e:
            print("Reddit error:", e)

        # 🛸 NEWS
        try:
            for title, link, _ in scrape_news():
                summary = summarize(title)

                if is_breaking(title):
                    prefix = "🚨 BREAKING NEWS"
                else:
                    prefix = "🛸 UFO NEWS"

                msg = f"{prefix}\n\n{title}\n\n🧠 {summary}\n\n🔗 {link}"
                await bot.send_message(chat_id=CHAT_ID, text=msg)

        except Exception as e:
            print("News error:", e)

        await asyncio.sleep(180)  # ⏱ 3 minutes


asyncio.run(main())
