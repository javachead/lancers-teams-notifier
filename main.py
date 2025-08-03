import os, json
from playwright.sync_api import sync_playwright
import requests

WEBHOOK_URL = os.environ["TEAMS_WEBHOOK_URL"]
DB_FILE = "jobs.json"

def load_posted_links():
    if not os.path.exists(DB_FILE):
        return set()
    with open(DB_FILE, "r") as f:
        return set(json.load(f))

def save_posted_links(links):
    with open(DB_FILE, "w") as f:
        json.dump(list(links), f)

def post_to_teams(title, price, link):
    payload = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": "Lancers新着案件",
        "themeColor": "0076D7",
        "title": title,
        "text": f"💰 {price}\n🔗 [案件を確認]({link})"
    }
    res = requests.post(WEBHOOK_URL, json=payload)
    print(f"📩 Teams通知: {title}")
    res.raise_for_status()

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.lancers.jp/work/search/system/ai?sort=client&show_description=0")
        page.wait_for_selector("section.c-media", timeout=10000)
        jobs = page.query_selector_all("section.c-media")

        print(f"✅ 取得案件数: {len(jobs)}")

        posted = load_posted_links()
        new_posted = set(posted)

        for job in jobs[:5]:  # 上位5件まで通知
            title = job.query_selector("h3").inner_text()
            price = job.query_selector(".c-media__price").inner_text()
            link = "https://www.lancers.jp" + job.query_selector("a").get_attribute("href")

            if link not in posted:
                post_to_teams(title, price, link)
                new_posted.add(link)

        save_posted_links(new_posted)
        browser.close()

if __name__ == "__main__":
    main()
