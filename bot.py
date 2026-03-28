import asyncio
import requests
from telegram import Bot

BOT_TOKEN = "8642772204:AAHzXM8h8i4vJdLZIx7j6wMLgV80AGwCN14"
CHAT_ID = "527677115"

sent = set()

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# ✅ SAFE REQUEST
def safe_get(url):
    try:
        return requests.get(url, headers=HEADERS, timeout=10)
    except Exception as e:
        print("Request error:", e)
        return None


# 🔴 REDDIT (OFFICIAL JSON = VERY STABLE)
def scrape_reddit():
    url = "https://www.reddit.com/r/UFOs/top.json?t=day&limit=10"
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

            # 🔥 VIRAL FILTER
            if upvotes > 500:
                if link not in sent:
                    posts.append((title, link, upvotes))
                    sent.add(link)

        except:
            continue

    return posts


# 🐦 TWITTER/X WORKAROUND (RSS = STABLE)
def scrape_twitter():
    url = "https://nitter.poast.org/search/rss?f=tweets&q=ufo+OR+uap+OR+alien"
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
            posts.append((title, link))
            sent.add(link)

    return posts


# 🛸 GOOGLE NEWS (VERY RELIABLE)
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
            posts.append((title, link))
            sent.add(link)

    return posts


# 🚀 MAIN LOOP
async def main():
    bot = Bot(token=BOT_TOKEN)

    while True:
        try:
            print("Running scraper...")

            # 🔴 REDDIT
            for title, link, upvotes in scrape_reddit():
                msg = f"🚨 VIRAL UFO POST\n\n🔥 {upvotes} upvotes\n\n{title}\n\n🔗 {link}"
                await bot.send_message(chat_id=CHAT_ID, text=msg)

            # 🐦 TWITTER
            for title, link in scrape_twitter():
                msg = f"🐦 UFO TWITTER SIGNAL\n\n{title}\n\n🔗 {link}"
                await bot.send_message(chat_id=CHAT_ID, text=msg)

            # 🛸 NEWS
            for title, link in scrape_news():
                msg = f"🛸 UFO NEWS\n\n{title}\n\n🔗 {link}"
                await bot.send_message(chat_id=CHAT_ID, text=msg)

            await asyncio.sleep(300)

        except Exception as e:
            print("Main error:", e)
            await asyncio.sleep(60)


asyncio.run(main())
