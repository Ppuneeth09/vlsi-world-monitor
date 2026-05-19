import requests
from bs4 import BeautifulSoup
import feedparser
import json
import os
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
DATA_FILE = "data.json"
VLSI_KEYWORDS = ["vlsi", "semiconductor", "chip", "fab", "foundry", "eda", "tapeout", "asic", "soc", "tsmc", "intel", "samsung", "lithography", "tata", "micron"]

def scrape_feeds():
    print("🕵️ Scanning Global Engineering Feeds...")
    urls = {
        "SIA Market Intelligence": "https://semiconductors.org",
        "EE Times Semiconductor": "https://eetimes.com",
        "AnySilicon": "https://anysilicon.com"
    }
    updates = []
    for source, url in urls.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            if any(k in f"{title} {summary}".lower() for k in VLSI_KEYWORDS):
                updates.append({
                    "title": title,
                    "link": entry.get("link", ""),
                    "source": source,
                    "date": entry.get("published", datetime.now().strftime("%Y-%m-%d"))
                })
    return updates

def scrape_pib():
    print("🕵️ Scanning PIB India for Government updates...")
    query = "site%3Apib.gov.in%20semiconductor%20OR%20%22India%20Semiconductor%20Mission%22"
    url = f"https://google.com{query}&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    return [{"title": f"[Gov Update] {e.title}", "link": e.link, "source": "🏛️ PIB India", "date": e.published} for e in feed.entries[:5]]

def save_data(new_data):
    history = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try: history = json.load(f)
            except: pass
    existing_links = {item["link"] for item in history}
    for item in new_data:
        if item["link"] not in existing_links:
            history.insert(0, item)
    with open(DATA_FILE, "w") as f:
        json.dump(history[:500], f, indent=2)
    print(f"✅ Added {len(new_data)} items to data.json")

if __name__ == "__main__":
    all_data = scrape_feeds() + scrape_pib()
    save_data(all_data)
