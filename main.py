import asyncio
from playwright.async_api import async_playwright
import time

async def fetch_jobs():
    async with async_playwright() as p:
        # Launch browser with more options for debugging
        browser = await p.chromium.launch(
            headless=False,  # Set to True in production
            slow_mo=1000     # Slow down operations for debugging
        )
        
        try:
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()
            
            # Navigate to the page
            url = "https://www.lancers.jp/work/search/system?budget_from=&budget_to=&work_rank%5B%5D=&work_rank%5B%5D=&work_rank%5B%5D=&keyword=&sort=work_post_date"
            print(f"📡 アクセス中: {url}")
            
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait a bit more for dynamic content
            await page.wait_for_timeout(3000)
            
            # Take a screenshot for debugging
            await page.screenshot(path="debug_page.png")
            print("🖼️ デバッグ用スクリーンショット保存: debug_page.png")
            
            # Try multiple possible selectors
            selectors_to_try = [
                ".c-media__heading a",
                ".c-jobListItem__title a",
                ".p-jobList__item a",
                "[data-testid='job-title'] a",
                ".job-title a",
                "a[href*='/work/detail/']"
            ]
            
            jobs = []
            found_selector = None
            
            for selector in selectors_to_try:
                try:
                    print(f"🔍 セレクタを試行中: {selector}")
                    await page.wait_for_selector(selector, timeout=5000)
                    found_selector = selector
                    print(f"✅ セレクタが見つかりました: {selector}")
                    break
                except Exception as e:
                    print(f"❌ セレクタが見つかりませんでした: {selector}")
                    continue
            
            if not found_selector:
                # Get page content for debugging
                content = await page.content()
                with open("debug_page.html", "w", encoding="utf-8") as f:
                    f.write(content)
                print("🐛 ページコンテンツを保存: debug_page.html")
                
                # Try to find any links that might be job links
                all_links = await page.query_selector_all("a")
                print(f"📋 ページ内の全リンク数: {len(all_links)}")
                
                for i, link in enumerate(all_links[:10]):  # First 10 links for debugging
                    href = await link.get_attribute("href")
                    text = await link.text_content()
                    print(f"  {i+1}. {text[:50]}... -> {href}")
                
                return []
            
            # Get job elements
            job_elements = await page.query_selector_all(found_selector)
            print(f"📊 見つかった案件数: {len(job_elements)}")
            
            for i, job_element in enumerate(job_elements[:5]):  # Limit to first 5 for testing
                try:
                    # Get title and link
                    title = await job_element.text_content()
                    link = await job_element.get_attribute("href")
                    
                    # Ensure absolute URL
                    if link and not link.startswith("http"):
                        link = "https://www.lancers.jp" + link
                    
                    # Try to get price - this might need adjustment based on actual HTML structure
                    price = "価格情報なし"
                    try:
                        # Navigate up to parent to find price element
                        parent = await job_element.evaluate_handle("element => element.closest('.c-media, .c-jobListItem, .p-jobList__item')")
                        if parent:
                            price_element = await parent.query_selector(".c-media__price, .price, .budget")
                            if price_element:
                                price = await price_element.text_content()
                    except:
                        pass
                    
                    job_info = {
                        "title": title.strip() if title else "[タイトルなし]",
                        "link": link or "[リンクなし]",
                        "price": price.strip() if price else "価格情報なし"
                    }
                    
                    jobs.append(job_info)
                    print(f"📝 案件 {i+1}: {job_info['title'][:50]}...")
                    
                except Exception as e:
                    print(f"⚠️ 案件 {i+1} の処理でエラー: {e}")
                    continue
            
            return jobs
            
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
            # Take screenshot on error
            try:
                await page.screenshot(path="error_screenshot.png")
                print("📸 エラー時のスクリーンショット保存: error_screenshot.png")
            except:
                pass
            return []
            
        finally:
            await browser.close()

def format_jobs_for_teams(jobs):
    if not jobs:
        return "📭 新しい案件は見つかりませんでした。"
    
    message = f"🚀 **新着案件情報** ({len(jobs)}件)\n\n"
    
    for i, job in enumerate(jobs, 1):
        message += f"**{i}. {job['title']}**\n"
        message += f"💰 {job['price']}\n"
        message += f"🔗 {job['link']}\n\n"
    
    return message

async def main():
    print("🤖 Lancers案件取得を開始します...")
    jobs = await fetch_jobs()
    
    if jobs:
        message = format_jobs_for_teams(jobs)
        print("\n" + "="*50)
        print("TEAMS送信用メッセージ:")
        print("="*50)
        print(message)
        
        # Here you would typically send to Teams webhook
        # For now, just save to file
        with open("latest_jobs.txt", "w", encoding="utf-8") as f:
            f.write(message)
        print("📁 メッセージをファイルに保存しました: latest_jobs.txt")
    else:
        print("❌ 案件の取得に失敗しました。")

if __name__ == "__main__":
    asyncio.run(main())