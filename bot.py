import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot

BOT_TOKEN = "8642772204:AAHzXM8h8i4vJdLZIx7j6wMLgV80AGwCN14"
CHAT_ID = "527677115"

sent = set()
HEADERS = {"User-Agent": "Mozilla/5.0"}


def scrape_reddit():
    url = "https://www.reddit.com/r/UFOs/top/?t=day"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    posts = []

    for post in soup.select("div[data-testid=post-container]"):
        try:
            title = post.select_one("h3").text
            link = "https://reddit.com" + post.select_one("a")["href"]

            text = post.text

            if "k" in text:  # viral filter
                if link not in sent:
                    posts.append((title, link))
                    sent.add(link)

        except:
            continue

    return posts


def scrape_twitter():
    url = "https://nitter.net/search?f=tweets&q=ufo+OR+uap+OR+alien"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    posts = []

    for tweet in soup.select(".timeline-item")[:5]:
        try:
            content = tweet.select_one(".tweet-content").text.strip()
            link = "https://nitter.net" + tweet.select_one("a")["href"]

            if link not in sent:
                posts.append((content, link))
                sent.add(link)

        except:
            continue

    return posts


def scrape_sites():
    url = "https://www.ufosightingsdaily.com/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    posts = []

    for item in soup.select("h2 a")[:5]:
        title = item.text
        link = item["href"]

        if link not in sent:
            posts.append((title, link))
            sent.add(link)

    return posts


async def main():
    bot = Bot(token=BOT_TOKEN)

    while True:
        try:
            for title, link in scrape_reddit():
                await bot.send_message(chat_id=CHAT_ID, text=f"🚨 VIRAL UFO\n\n{title}\n{link}")

            for content, link in scrape_twitter():
                await bot.send_message(chat_id=CHAT_ID, text=f"🐦 UFO TWITTER\n\n{content}\n{link}")

            for title, link in scrape_sites():
                await bot.send_message(chat_id=CHAT_ID, text=f"🛸 UFO REPORT\n\n{title}\n{link}")

            await asyncio.sleep(300)

        except Exception as e:
            print(e)
            await asyncio.sleep(60)


asyncio.run(main())
