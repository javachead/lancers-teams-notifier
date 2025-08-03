import asyncio
from playwright.async_api import async_playwright

async def simple_test():
    """最小限のテスト"""
    print("🚀 簡単なテストを開始...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # ブラウザを表示
        page = await browser.new_page()
        
        try:
            print("📡 Googleにアクセス中...")
            await page.goto("https://www.google.com", timeout=30000)
            
            title = await page.title()
            print(f"✅ ページタイトル: {title}")
            
            print("📸 スクリーンショット保存中...")
            await page.screenshot(path="google_test.png")
            
            print("⏸️ 5秒待機...")
            await page.wait_for_timeout(5000)
            
            print("✅ テスト完了")
            
        except Exception as e:
            print(f"❌ エラー: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(simple_test())