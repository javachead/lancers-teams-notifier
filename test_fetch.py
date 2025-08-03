import requests
from bs4 import BeautifulSoup

# すべての新着案件を取得
URL = "https://www.lancers.jp/work/rss"
HEADERS = {"User-Agent": "Mozilla/5.0"}

res = requests.get(URL, headers=HEADERS)
soup = BeautifulSoup(res.content, "xml")

items = soup.find_all("item")
print(f"✅ RSSからの取得件数: {len(items)} 件")

for item in items:
    title = item.title.get_text()
    link = item.link.get_text()
    print(f"- {title}")
    print(f"  🔗 {link}\n")
