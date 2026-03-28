import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot

BOT_TOKEN = "8642772204:AAHzXM8h8i4vJdLZIx7j6wMLgV80AGwCN14"
CHAT_ID = "527677115"

sent = set()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Accept-Language": "en-US,en;q=0.9",
}


# ✅ SAFE REQUEST (prevents crashes)
def safe_get(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r
    except Exception as e:
        print("Request failed:", e)
        return None


# 🔥 REDDIT (VIRAL POSTS)
def scrape_reddit():
    url = "https://old.reddit.com/r/UFOs/top/?t=day"
    r = safe_get(url)
    if not r:
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    posts = []

    for post in soup.select("div.thing")[:10]:
        try:
            title = post.select_one("a.title").text
            link = post.select_one("a.title")["href"]

            if not link.startswith("http"):
                link = "https://reddit.com" + link

            score = post.select_one("div.score").text

            # 🔥 VIRAL FILTER
            if "k" in score.lower() or score.isdigit() and int(score) > 500:
                if link not in sent:
                    posts.append((title, link, score))
                    sent.add(link)

        except:
            continue

    return posts


# 🐦 TWITTER/X (NITTER WORKAROUND)
def scrape_twitter():
    url = "https://nitter.poast.org/search?f=tweets&q=ufo+OR+uap+OR+alien"
    r = safe_get(url)
    if not r:
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    posts = []

    for tweet in soup.select(".timeline-item")[:5]:
        try:
            content = tweet.select_one(".tweet-content").text.strip()
            link = "https://nitter.poast.org" + tweet.select_one("a")["href"]

            if link not in sent:
                posts.append((content, link))
                sent.add(link)

        except:
            continue

    return posts


# 🛸 UFO BLOG / LEAK SITE
def scrape_sites():
    url = "https://www.ufosightingsdaily.com/"
    r = safe_get(url)
    if not r:
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    posts = []

    for item in soup.select("h2 a")[:5]:
        try:
            title = item.text.strip()
            link = item["href"]

            if link not in sent:
                posts.append((title, link))
                sent.add(link)

        except:
            continue

    return posts


# 🚀 MAIN LOOP
async def main():
    bot = Bot(token=BOT_TOKEN)

    while True:
        try:
            print("Checking sources...")

            # 🔴 REDDIT
            for title, link, score in scrape_reddit():
                msg = f"🚨 VIRAL UFO POST\n\n🔥 {score} upvotes\n\n{title}\n\n🔗 {link}"
                await bot.send_message(chat_id=CHAT_ID, text=msg)

            # 🐦 TWITTER
            for content, link in scrape_twitter():
                msg = f"🐦 UFO TWITTER SIGNAL\n\n{content}\n\n🔗 {link}"
                await bot.send_message(chat_id=CHAT_ID, text=msg)

            # 🛸 SITES
            for title, link in scrape_sites():
                msg = f"🛸 UFO REPORT\n\n{title}\n\n🔗 {link}"
                await bot.send_message(chat_id=CHAT_ID, text=msg)

            await asyncio.sleep(300)  # every 5 minutes

        except Exception as e:
            print("Main loop error:", e)
            await asyncio.sleep(60)


asyncio.run(main())
