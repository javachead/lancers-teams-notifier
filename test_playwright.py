from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.lancers.jp/work/search/system/ai?sort=client&show_description=0")
    page.wait_for_selector("section.c-media", timeout=10000)

    jobs = page.query_selector_all("section.c-media")

    print(f"✅ 案件数: {len(jobs)} 件")
    for job in jobs[:5]:  # 上位5件だけ表示
        title = job.query_selector("h3").inner_text()
        price = job.query_selector(".c-media__price").inner_text()
        link = "https://www.lancers.jp" + job.query_selector("a").get_attribute("href")
        print(f"- {title} / {price}")
        print(f"  🔗 {link}\n")

    browser.close()
