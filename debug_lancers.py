#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import aiohttp
import json
import re
import os
import sys
import traceback
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

# デバッグモード
DEBUG = True

def debug_print(message):
    """デバッグ出力"""
    if DEBUG:
        print(f"[DEBUG] {message}")

# 設定
LANCERS_SEARCH_URL = "https://www.lancers.jp/work/search/system?budget_from=&budget_to=&work_rank%5B%5D=&work_rank%5B%5D=&work_rank%5B%5D=&keyword=&sort=work_post_date"
MAX_JOBS_TO_FETCH = 20  # デバッグ用に少なくする
HEADLESS_MODE = False  # デバッグ用にブラウザを表示

# 弊社スキルセット（検索ワード優先版）
COMPANY_SKILLS = {
    "超高優先度": ["AI", "GPT", "ChatGPT", "Python", "API", "Django", "Next.js","React","TypeScript", "機械学習"],
    "高優先度": ["bot", "Talend", "Java", "スマホアプリ", "モバイル開発", "人工知能"],
    "中優先度": ["効率化", "ツール", "開発", "システム開発", "React", "Node.js", "自動化", "スクレイピング"],
    "低優先度": ["PostgreSQL", "MySQL", "社内ツール", "業務改善", "アプリ", "サイト", "管理"],
    "最低優先度": ["Render", "ロリッポップ", "WordPress", "PHP"]
}

# 除外キーワード
EXCLUDE_KEYWORDS = [
    "求人", "採用", "転職", "正社員", "アルバイト", "派遣",
    "コンペ", "コンペティション", "コンテスト",
    "募集終了", "終了", "締切", "CAD",
]

class CompleteJobsNotifier:
    def __init__(self):
        self.jobs_data = []
        self.seen_links = set()
        debug_print("CompleteJobsNotifier初期化完了")
        
    async def test_basic_connection(self):
        """基本的な接続テスト"""
        debug_print("基本的な接続テストを開始...")
        
        try:
            async with async_playwright() as p:
                debug_print("Playwright起動中...")
                browser = await p.chromium.launch(headless=HEADLESS_MODE, slow_mo=500)
                debug_print("ブラウザ起動完了")
                
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    locale="ja-JP"
                )
                page = await context.new_page()
                debug_print("新しいページ作成完了")
                
                debug_print(f"アクセス中: {LANCERS_SEARCH_URL}")
                response = await page.goto(LANCERS_SEARCH_URL, wait_until="domcontentloaded", timeout=30000)
                debug_print(f"ページ読み込み完了 (ステータス: {response.status})")
                
                await page.wait_for_timeout(3000)
                
                # ページタイトルを取得
                title = await page.title()
                debug_print(f"ページタイトル: {title}")
                
                # 基本的な要素をチェック
                job_links = await page.query_selector_all("a[href*='/work/detail/']")
                debug_print(f"案件リンク数: {len(job_links)}")
                
                if len(job_links) > 0:
                    debug_print("案件リンクが見つかりました！")
                    for i, link in enumerate(job_links[:3]):  # 最初の3つだけチェック
                        href = await link.get_attribute("href")
                        text = await link.text_content()
                        debug_print(f"リンク {i+1}: {text[:50]}... -> {href}")
                else:
                    debug_print("❌ 案件リンクが見つかりません")
                    
                    # ページの内容を確認
                    content = await page.content()
                    debug_print(f"ページ内容の長さ: {len(content)}")
                    
                    # エラーメッセージがあるかチェック
                    error_elements = await page.query_selector_all(".error, .alert, .warning")
                    for elem in error_elements:
                        error_text = await elem.text_content()
                        debug_print(f"エラー要素: {error_text}")
                
                await browser.close()
                debug_print("ブラウザクローズ完了")
                
        except Exception as e:
            debug_print(f"❌ 接続テストエラー: {e}")
            traceback.print_exc()
        
    async def fetch_jobs(self):
        """全案件を取得（デバッグ版）"""
        debug_print("🚀 Lancers案件取得を開始...")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=HEADLESS_MODE, slow_mo=300)
                debug_print("ブラウザ起動完了")
                
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    locale="ja-JP"
                )
                page = await context.new_page()
                
                debug_print(f"📡 アクセス中: {LANCERS_SEARCH_URL}")
                response = await page.goto(LANCERS_SEARCH_URL, wait_until="domcontentloaded", timeout=60000)
                debug_print(f"✅ ページ読み込み完了 (ステータス: {response.status})")
                
                await page.wait_for_timeout(5000)
                
                # スクロールして読み込み
                debug_print("ページをスクロール中...")
                await self.scroll_and_load_more(page)
                
                # 案件リンクを取得
                job_elements = await page.query_selector_all("a[href*='/work/detail/']")
                debug_print(f"📊 {len(job_elements)} 個の案件候補を発見")
                
                if len(job_elements) == 0:
                    debug_print("❌ 案件が見つかりませんでした。ページ構造を確認します...")
                    
                    # 代替セレクタを試す
                    alternative_selectors = [
                        "a[href*='work']",
                        ".job-item a",
                        ".work-item a",
                        "a[href*='detail']"
                    ]
                    
                    for selector in alternative_selectors:
                        alt_elements = await page.query_selector_all(selector)
                        debug_print(f"代替セレクタ '{selector}': {len(alt_elements)}個")
                
                all_jobs = []
                
                for i, element in enumerate(job_elements):
                    if len(all_jobs) >= MAX_JOBS_TO_FETCH:
                        break
                        
                    debug_print(f"案件 {i+1}/{len(job_elements)} を処理中...")
                    job_info = await self.extract_job_info(element, page)
                    
                    if job_info:
                        debug_print(f"案件情報取得成功: {job_info['title'][:30]}...")
                        if self.should_include_job_minimal(job_info):
                            all_jobs.append(job_info)
                            debug_print(f"✅ 案件追加: {len(all_jobs)}件目")
                        else:
                            debug_print("❌ フィルタリングにより除外")
                    else:
                        debug_print("❌ 案件情報取得失敗")
                
                debug_print(f"✅ 合計 {len(all_jobs)} 件の案件を取得しました")
                
                await browser.close()
                return all_jobs
                
        except Exception as e:
            debug_print(f"❌ エラー: {e}")
            traceback.print_exc()
            return []
    
    async def scroll_and_load_more(self, page):
        """ページスクロール"""
        try:
            debug_print("ページスクロール開始...")
            
            for i in range(3):  # 回数を減らす
                debug_print(f"スクロール {i+1}/3")
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2000)
            
            # もっと見るボタンを探す
            more_button = await page.query_selector(".more-button, .load-more, [class*='more']")
            if more_button:
                debug_print("「もっと見る」ボタンをクリック")
                await more_button.click()
                await page.wait_for_timeout(3000)
            else:
                debug_print("「もっと見る」ボタンが見つかりません")
                
        except Exception as e:
            debug_print(f"⚠️ スクロール読み込みエラー: {e}")
    
    async def extract_job_info(self, element, page):
        """案件情報を抽出（デバッグ版）"""
        try:
            title_text = await element.text_content()
            href = await element.get_attribute("href")
            
            debug_print(f"タイトル: {title_text[:50] if title_text else 'None'}...")
            debug_print(f"リンク: {href}")
            
            if not title_text or not href:
                debug_print("❌ タイトルまたはリンクが空です")
                return None
            
            title = self.clean_title(title_text)
            if not title or len(title) < 5:
                debug_print("❌ タイトルが短すぎます")
                return None
            
            if href.startswith("/"):
                href = "https://www.lancers.jp" + href
            
            # 重複チェック
            if href in self.seen_links:
                debug_print("❌ 重複リンクです")
                return None
            self.seen_links.add(href)
            
            # 基本的な案件情報を作成
            job_info = {
                "title": title,
                "link": href,
                "price": "価格情報なし",
                "deadline": "期限情報なし",
                "start_date": "開始日情報なし",
                "delivery_date": "納期情報なし",
                "applicant_count": "0",
                "recruitment_count": "1",
                "client_name": "依頼者情報なし",
                "status": "募集中",
                "urgency": False,
                "category": "システム開発",
                "corporate_allowed": False,
                "skill_matches": [],
                "skill_count": 0,
                "priority_score": 1,
                "scraped_at": datetime.now().isoformat()
            }
            
            debug_print(f"✅ 基本情報作成完了: {title[:30]}...")
            return job_info
            
        except Exception as e:
            debug_print(f"⚠️ 案件抽出エラー: {e}")
            return None
    
    def clean_title(self, title):
        """タイトルクリーンアップ"""
        if not title:
            return ""
        
        title = re.sub(r'\s+', ' ', title.strip())
        title = re.sub(r'^(NEW\s*){1,}', '', title, flags=re.IGNORECASE)
        
        return title.strip()
    
    def should_include_job_minimal(self, job_info):
        """基本的なフィルタリング"""
        title = job_info["title"]
        
        if not title or len(title.strip()) < 5:
            return False
        
        # 除外キーワードチェック
        title_lower = title.lower()
        for keyword in EXCLUDE_KEYWORDS:
            if keyword.lower() in title_lower:
                debug_print(f"除外キーワードでフィルタ: {keyword}")
                return False
        
        return True
    
    def save_debug_data(self, jobs):
        """デバッグ用データ保存"""
        timestamp = datetime.now()
        
        data = {
            "timestamp": timestamp.isoformat(),
            "count": len(jobs),
            "type": "デバッグ用全案件リスト",
            "jobs": jobs
        }
        
        filename = f"debug_jobs_{timestamp.strftime('%Y%m%d_%H%M')}.json"
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            debug_print(f"💾 デバッグデータを保存: {filename}")
        except Exception as e:
            debug_print(f"❌ ファイル保存エラー: {e}")

async def main():
    """メイン実行関数（デバッグ版）"""
    print("=" * 70)
    print("🤖 Lancers案件取得システム（デバッグモード）")
    print("=" * 70)
    
    try:
        notifier = CompleteJobsNotifier()
        
        # まず基本的な接続テストを実行
        debug_print("=== 基本接続テスト開始 ===")
        await notifier.test_basic_connection()
        
        # 実際の案件取得を実行
        debug_print("=== 案件取得開始 ===")
        jobs = await notifier.fetch_jobs()
        
        if jobs:
            debug_print(f"✅ {len(jobs)}件の案件を取得しました")
            notifier.save_debug_data(jobs)
            
            print("\n" + "=" * 70)
            print("📊 実行結果:")
            print("=" * 70)
            print(f"✅ 取得案件数: {len(jobs)}件")
            
            # 最初の3件を表示
            for i, job in enumerate(jobs[:3], 1):
                print(f"\n{i}. {job['title']}")
                print(f"   リンク: {job['link']}")
                
        else:
            debug_print("❌ 案件が見つかりませんでした")
            print("❌ 案件取得に失敗しました。ログを確認してください。")
            
    except Exception as e:
        debug_print(f"❌ メイン関数エラー: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    # Pythonのバージョンをチェック
    debug_print(f"Python バージョン: {sys.version}")
    debug_print(f"作業ディレクトリ: {os.getcwd()}")
    
    asyncio.run(main())