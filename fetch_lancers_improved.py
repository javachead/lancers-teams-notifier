#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import aiohttp
import json
import re
import os
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

# 設定
LANCERS_SEARCH_URL = "https://www.lancers.jp/work/search/system?budget_from=&budget_to=&work_rank%5B%5D=&work_rank%5B%5D=&work_rank%5B%5D=&keyword=&sort=work_post_date"
MAX_JOBS_TO_FETCH = 100
HEADLESS_MODE = True

# 弊社スキルセット（検索ワード優先版）
COMPANY_SKILLS = {
    "超高優先度": ["AI", "GPT", "ChatGPT", "Python", "API", "Django", "Next.js", "TypeScript", "機械学習"],
    "高優先度": ["bot", "Talend", "Java", "スマホアプリ", "モバイル開発", "人工知能"],
    "中優先度": ["効率化", "ツール", "開発", "システム開発", "React", "Node.js", "自動化", "スクレイピング"],
    "低優先度": ["PostgreSQL", "MySQL", "社内ツール", "業務改善", "アプリ", "サイト", "管理"],
    "最低優先度": ["Render", "ロリッポップ", "WordPress", "PHP"]
}

# 除外キーワード
EXCLUDE_KEYWORDS = [
    "求人", "採用", "転職", "正社員", "アルバイト", "派遣",
    "コンペ", "コンペティション", "コンテスト",
    "募集終了", "締切", "CAD",
]

class CompleteJobsNotifier:
    def __init__(self):
        self.jobs_data = []
        self.seen_links = set()
        
    async def fetch_jobs(self):
        """全案件を取得（フィルタリング最小限）"""
        print("🚀 Lancers全案件取得を開始...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=HEADLESS_MODE, slow_mo=300)
            
            try:
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    locale="ja-JP"
                )
                page = await context.new_page()
                
                print(f"📡 アクセス中: {LANCERS_SEARCH_URL}")
                response = await page.goto(LANCERS_SEARCH_URL, wait_until="domcontentloaded", timeout=60000)
                print(f"✅ ページ読み込み完了 (ステータス: {response.status})")
                
                await page.wait_for_timeout(5000)
                
                # より多くのページを読み込み
                await self.scroll_and_load_more(page)
                
                # 案件リンクを取得
                job_elements = await page.query_selector_all("a[href*='/work/detail/']")
                print(f"📊 {len(job_elements)} 個の案件候補を発見")
                
                all_jobs = []
                
                for i, element in enumerate(job_elements):
                    if len(all_jobs) >= MAX_JOBS_TO_FETCH:
                        break
                        
                    job_info = await self.extract_job_info(element, page)
                    if job_info and self.should_include_job_minimal(job_info):
                        all_jobs.append(job_info)
                        
                        # スキル情報を表示
                        skill_info = self.format_skill_matches(job_info["skill_matches"])
                        print(f"📝 案件 {len(all_jobs)}: {job_info['title'][:40]}... | {skill_info}")
                
                # スキルマッチ度で並び替え
                sorted_jobs = self.sort_by_skill_relevance(all_jobs)
                
                print(f"✅ 全 {len(sorted_jobs)} 件の案件を取得しました")
                self.jobs_data = sorted_jobs
                return sorted_jobs
                
            except Exception as e:
                print(f"❌ エラー: {e}")
                return []
            finally:
                await browser.close()
    
    async def scroll_and_load_more(self, page):
        """より多くのページを読み込み"""
        try:
            for _ in range(5):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2000)
            
            more_button = await page.query_selector(".more-button, .load-more, [class*='more']")
            if more_button:
                await more_button.click()
                await page.wait_for_timeout(3000)
            
            for _ in range(3):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2000)
                
        except Exception as e:
            print(f"⚠️ スクロール読み込みエラー: {e}")
    
    async def extract_job_info(self, element, page):
        """案件情報を抽出"""
        try:
            title_text = await element.text_content()
            href = await element.get_attribute("href")
            
            if not title_text or not href:
                return None
            
            title = self.clean_title(title_text)
            if not title or len(title) < 5:
                return None
            
            if href.startswith("/"):
                href = "https://www.lancers.jp" + href
            
            # 重複チェック
            if href in self.seen_links:
                return None
            self.seen_links.add(href)
            
            # 詳細情報を取得
            recruitment_info = await self.extract_recruitment_details(element)
            
            # スキルマッチを詳細に分析
            skill_matches = self.find_all_skill_matches(title)
            
            job_info = {
                "title": title,
                "link": href,
                "price": recruitment_info["price"],
                "deadline": recruitment_info["deadline"],
                "applicant_count": recruitment_info["applicant_count"],
                "recruitment_count": recruitment_info["recruitment_count"],
                "client_name": recruitment_info["client_name"],
                "status": recruitment_info["status"],
                "urgency": recruitment_info["urgency"],
                "category": recruitment_info["category"],
                "skill_matches": skill_matches,
                "skill_count": len(skill_matches),
                "priority_score": self.calculate_comprehensive_score(title, recruitment_info, skill_matches),
                "scraped_at": datetime.now().isoformat()
            }
            
            return job_info
            
        except Exception as e:
            print(f"⚠️ 案件抽出エラー: {e}")
            return None
    
    def find_all_skill_matches(self, title):
        """全スキルからマッチを検出（優先度強化版）"""
        matches = []
        title_lower = title.lower()
        
        # 全カテゴリのスキルをチェック
        for priority, skills in COMPANY_SKILLS.items():
            for skill in skills:
                if skill.lower() in title_lower:
                    matches.append({"skill": skill, "priority": priority})
        
        # 追加のキーワードマッチング（優先度強化）
        additional_keywords = {
            "自動化": "中優先度",
            "スクレイピング": "中優先度", 
            "アプリ": "中優先度",
            "サイト": "低優先度",
            "管理": "低優先度",
            "コンサル": "中優先度",
            "Ai": "超高優先度",  # AIの別表記
            "人工知能": "高優先度"
        }
        
        for keyword, priority in additional_keywords.items():
            if keyword.lower() in title_lower:
                matches.append({"skill": keyword, "priority": priority})
        
        # 重複除去
        seen_skills = set()
        unique_matches = []
        for match in matches:
            if match["skill"] not in seen_skills:
                unique_matches.append(match)
                seen_skills.add(match["skill"])
        
        return unique_matches
    
    def format_skill_matches(self, skill_matches):
        """スキルマッチ情報をフォーマット"""
        if not skill_matches:
            return "🔧 スキルセット: なし"
        
        skills_by_priority = {}
        for match in skill_matches:
            priority = match["priority"]
            if priority not in skills_by_priority:
                skills_by_priority[priority] = []
            skills_by_priority[priority].append(match["skill"])
        
        parts = []
        if "超高優先度" in skills_by_priority:
            parts.append(f"🔥{', '.join(skills_by_priority['超高優先度'])}")
        if "高優先度" in skills_by_priority:
            parts.append(f"★{', '.join(skills_by_priority['高優先度'])}")
        if "中優先度" in skills_by_priority:
            parts.append(f"◆{', '.join(skills_by_priority['中優先度'])}")
        if "低優先度" in skills_by_priority:
            parts.append(f"◇{', '.join(skills_by_priority['低優先度'])}")
        if "最低優先度" in skills_by_priority:
            parts.append(f"○{', '.join(skills_by_priority['最低優先度'])}")
        
        return f"🔧 スキルセット: {' | '.join(parts)}" if parts else "🔧 スキルセット: なし"
    
    def format_skill_matches_compact(self, skill_matches):
        """スキルマッチ情報をコンパクトにフォーマット"""
        if not skill_matches:
            return "🔧 スキルセット: なし"
        
        # 優先度別にグループ化
        ultra_high = [m["skill"] for m in skill_matches if m["priority"] == "超高優先度"]
        high = [m["skill"] for m in skill_matches if m["priority"] == "高優先度"]
        mid = [m["skill"] for m in skill_matches if m["priority"] == "中優先度"] 
        low = [m["skill"] for m in skill_matches if m["priority"] == "低優先度"]
        lowest = [m["skill"] for m in skill_matches if m["priority"] == "最低優先度"]
        
        parts = []
        if ultra_high: parts.append(f"🔥{','.join(ultra_high[:2])}")
        if high: parts.append(f"★{','.join(high[:2])}")
        if mid: parts.append(f"◆{','.join(mid[:2])}")
        if low: parts.append(f"◇{','.join(low[:1])}")
        if lowest: parts.append(f"○{','.join(lowest[:1])}")
        
        result = f"🔧 スキルセット: {' '.join(parts)}" if parts else "🔧 スキルセット: なし"
        
        # 長すぎる場合は切り詰め
        if len(result) > 100:
            result = result[:97] + "..."
        
        return result
    
    async def extract_recruitment_details(self, element):
        """募集詳細情報を抽出"""
        recruitment_info = {
            "price": "価格情報なし",
            "deadline": "期限情報なし", 
            "applicant_count": "0",
            "recruitment_count": "1",
            "client_name": "依頼者情報なし",
            "status": "募集中",
            "urgency": False,
            "category": "システム開発"
        }
        
        try:
            parent = await element.evaluate_handle("el => el.closest('.c-media, .p-jobList__item, article, li')")
            if parent:
                # 価格情報
                price_elem = await parent.query_selector(".c-media__price, .price, .budget, [class*='price']")
                if price_elem:
                    price_text = await price_elem.text_content()
                    if price_text and "円" in price_text:
                        recruitment_info["price"] = self.clean_price_text(price_text)
                
                # 締切情報
                deadline_elem = await parent.query_selector(".c-media__deadline, .deadline, [class*='deadline']")
                if deadline_elem:
                    deadline_text = await deadline_elem.text_content()
                    if deadline_text:
                        recruitment_info["deadline"] = deadline_text.strip()
                        if any(word in deadline_text for word in ["急募", "緊急", "即日", "至急"]):
                            recruitment_info["urgency"] = True
                
                # 応募者数・募集人数
                applicant_elem = await parent.query_selector(".c-media__applicant, .applicant, [class*='applicant']")
                if applicant_elem:
                    applicant_text = await applicant_elem.text_content()
                    if applicant_text:
                        numbers = re.findall(r'(\d+)', applicant_text)
                        if len(numbers) >= 2:
                            recruitment_info["applicant_count"] = numbers[0]
                            recruitment_info["recruitment_count"] = numbers[1]
                
        except:
            pass
        
        return recruitment_info
    
    def clean_title(self, title):
        """タイトルクリーンアップ"""
        if not title:
            return ""
        
        try:
            import unicodedata
            title = unicodedata.normalize('NFKC', title)
        except:
            pass
        
        title = re.sub(r'\s+', ' ', title.strip())
        title = re.sub(r'^(NEW\s*){1,}', '', title, flags=re.IGNORECASE)
        title = re.sub(r'^\d+回目\s*', '', title)
        
        return title.strip()
    
    def clean_price_text(self, raw_price):
        """価格テキストクリーンアップ"""
        if not raw_price:
            return "価格情報なし"
        
        try:
            import unicodedata
            raw_price = unicodedata.normalize('NFKC', raw_price)
        except:
            pass
        
        price = re.sub(r'\s+', ' ', raw_price.strip())
        price = re.sub(r'円\s*/\s*', '円 / ', price)
        
        return price
    
    def calculate_comprehensive_score(self, title, recruitment_info, skill_matches):
        """検索ワード優先のスコア計算（改良版）"""
        score = 0
        title_lower = title.lower()
        
        # スキルマッチによる大幅加点
        for match in skill_matches:
            priority = match["priority"]
            if priority == "超高優先度":
                score += 100  # 大幅加点
            elif priority == "高優先度":
                score += 50
            elif priority == "中優先度":
                score += 20
            elif priority == "低優先度":
                score += 10
            elif priority == "最低優先度":
                score += 5
        
        # 複数スキルマッチ大幅ボーナス
        if len(skill_matches) >= 3:
            score += 50
        elif len(skill_matches) >= 2:
            score += 25
        elif len(skill_matches) >= 1:
            score += 10
        
        # 特定キーワードボーナス
        priority_keywords = {
            "chatgpt": 80,
            "python": 70,
            "api": 60,
            "ai": 60,
            "自動化": 40,
            "bot": 40,
            "効率化": 30,
            "ツール": 25,
            "開発": 20,
            "システム": 15
        }
        
        for keyword, bonus in priority_keywords.items():
            if keyword in title_lower:
                score += bonus
        
        # 急募案件ボーナス
        if recruitment_info["urgency"]:
            score += 15
        
        # 応募者数考慮（競争率低い案件を優遇）
        try:
            applicant_count = int(recruitment_info["applicant_count"])
            if applicant_count == 0:
                score += 10
            elif applicant_count <= 2:
                score += 5
        except:
            pass
        
        # 高額案件ボーナス
        price_text = recruitment_info["price"]
        if "円" in price_text:
            numbers = re.findall(r'(\d+,?\d*)', price_text.replace(',', ''))
            if numbers:
                try:
                    max_price = max([int(num.replace(',', '')) for num in numbers])
                    if max_price >= 500000:
                        score += 15
                    elif max_price >= 100000:
                        score += 8
                    elif max_price >= 50000:
                        score += 3
                except:
                    pass
        
        return score
    
    def should_include_job_minimal(self, job_info):
        """スキルマッチ重視のフィルタリング（改良版）"""
        title = job_info["title"]
        
        # 基本フィルタ
        if not title or len(title.strip()) < 5:
            return False
        
        # 除外キーワードチェック
        title_lower = title.lower()
        for keyword in EXCLUDE_KEYWORDS:
            if keyword.lower() in title_lower:
                return False
        
        # 募集終了チェック
        status = job_info["status"]
        if any(word in status for word in ["募集終了", "締切", "終了", "完了"]):
            return False
        
        # スキルマッチ優先：スコアが一定以上、またはキーワードマッチがある場合のみ通す
        if job_info["priority_score"] >= 10 or job_info["skill_count"] >= 1:
            return True
        
        # 特定のキーワードが含まれている場合は通す
        priority_keywords = ["chatgpt", "python", "api", "ai", "自動化", "bot", "効率化", "ツール", "開発", "システム"]
        if any(keyword in title_lower for keyword in priority_keywords):
            return True
        
        # 上記に該当しない場合は除外
        return False
    
    def sort_by_skill_relevance(self, jobs):
        """検索ワード優先度で並び替え（大幅改良）"""
        def sort_key(job):
            # スキルマッチなしの案件は順位を大幅に下げる
            base_score = job["priority_score"]
            
            # スキルマッチがない場合は大幅減点
            if job["skill_count"] == 0:
                base_score -= 1000
            
            # 応募者数（少ない方が良い）
            applicant_count = int(job["applicant_count"]) if job["applicant_count"].isdigit() else 999
            
            return (
                -base_score,           # 優先度スコア（高い順）
                -job["skill_count"],   # スキルマッチ数（多い順）
                applicant_count,       # 応募者数（少ない順）
                not job["urgency"],    # 急募案件優先
                job["scraped_at"]      # 新しい順
            )
        
        return sorted(jobs, key=sort_key)
    
    def create_teams_payload(self, jobs):
        """Teams文字数制限（28KB）まで最大活用して表示"""
        if not jobs:
            return {
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "summary": "Lancers全案件通知",
                "themeColor": "0078D4",
                "title": "🚀 Lancers全案件リスト",
                "text": "📭 現在条件に合う案件が見つかりませんでした。"
            }
        
        # Teams制限: 28KB = 28,000文字
        MAX_CHARS = 25000  # 安全マージン（3KB）
        
        # 基本テキスト
        header_text = f"現在の全案件リストです（**{len(jobs)}件**を発見）\n\n"
        footer_text = "\n\n📋 詳細情報はJSONファイルでも確認できます。"
        
        # ヘッダー・フッターの文字数を除いた利用可能文字数
        available_chars = MAX_CHARS - len(header_text) - len(footer_text) - 500
        
        main_content = ""
        displayed_count = 0
        skipped_count = 0
        
        print(f"📊 Teams表示制限: {MAX_CHARS:,}文字まで利用可能")
        
        for i, job in enumerate(jobs, 1):
            # 各案件の表示テキストを構築
            skill_info = self.format_skill_matches_compact(job["skill_matches"])
            
            job_text = f"**{i}. {job['title']}**  \n"
            job_text += f"💰 {job['price']}  \n"
            
            # オプション情報（文字数節約のため条件付き）
            if job['deadline'] != "期限情報なし" and len(job['deadline']) < 20:
                job_text += f"⏰ {job['deadline']}  \n"
            
            if job['applicant_count'] != "0":
                job_text += f"👥 応募{job['applicant_count']}人  \n"
            
            job_text += f"{skill_info}  \n"
            
            if job['urgency']:
                job_text += f"🚨 急募  \n"
            
            job_text += f"🔗 [詳細]({job['link']})  \n\n"
            
            # 文字数チェック
            if len(main_content) + len(job_text) > available_chars:
                skipped_count = len(jobs) - displayed_count
                print(f"📝 文字数制限により {displayed_count}件表示、{skipped_count}件スキップ")
                break
            
            main_content += job_text
            displayed_count += 1
        
        # 最終テキスト構築
        if skipped_count > 0:
            final_text = header_text + main_content + f"\n📋 残り{skipped_count}件の案件はJSONファイルで確認できます。"
        else:
            final_text = header_text + main_content + footer_text
        
        # 実際の文字数をログ出力
        actual_chars = len(final_text)
        print(f"📊 実際の文字数: {actual_chars:,}文字 / {MAX_CHARS:,}文字 ({actual_chars/MAX_CHARS*100:.1f}%)")
        print(f"📊 表示案件数: {displayed_count}件 / {len(jobs)}件")
        
        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": f"Lancers全案件 {len(jobs)}件",
            "themeColor": "0078D4",
            "title": f"🚀 Lancers全案件リスト ({len(jobs)}件発見 / {displayed_count}件表示) - {datetime.now().strftime('%Y/%m/%d %H:%M')}",
            "text": final_text,
            "potentialAction": [{
                "@type": "OpenUri",
                "name": "🔍 Lancersで案件を探す",
                "targets": [{"os": "default", "uri": LANCERS_SEARCH_URL}]
            }]
        }
        
        return payload
    
    async def send_to_teams(self, jobs):
        """Teamsに送信"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except:
            pass
        
        webhook_url = os.getenv("TEAMS_WEBHOOK_URL")
        if not webhook_url:
            print("❌ Teams Webhook URLが設定されていません")
            return False
        
        payload = self.create_teams_payload(jobs)
        
        try:
            async with aiohttp.ClientSession() as session:
                print("📤 Teamsに全案件リストを送信中...")
                async with session.post(webhook_url, json=payload, headers={"Content-Type": "application/json"}) as response:
                    if response.status == 200:
                        print("✅ Teams送信成功！")
                        return True
                    else:
                        print(f"❌ Teams送信失敗 (ステータス: {response.status})")
                        return False
        except Exception as e:
            print(f"❌ Teams送信エラー: {e}")
            return False
    
    def save_data(self, jobs):
        """データ保存"""
        timestamp = datetime.now()
        
        data = {
            "timestamp": timestamp.isoformat(),
            "count": len(jobs),
            "type": "全案件リスト",
            "skill_summary": self.create_skill_summary(jobs),
            "skill_distribution": self.create_skill_distribution(jobs),
            "jobs": jobs
        }
        
        filename = f"all_jobs_{timestamp.strftime('%Y%m%d_%H%M')}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 全案件データを保存: {filename}")
    
    def create_skill_summary(self, jobs):
        """スキル集計サマリー"""
        skill_counts = {}
        for job in jobs:
            for match in job["skill_matches"]:
                skill = match["skill"]
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        return dict(sorted(skill_counts.items(), key=lambda x: x[1], reverse=True))
    
    def create_skill_distribution(self, jobs):
        """スキル分布分析"""
        total_jobs = len(jobs)
        no_skill_jobs = len([job for job in jobs if job["skill_count"] == 0])
        multi_skill_jobs = len([job for job in jobs if job["skill_count"] >= 2])
        high_priority_jobs = len([job for job in jobs if job["priority_score"] >= 10])
        
        return {
            "total_jobs": total_jobs,
            "no_skill_match": no_skill_jobs,
            "multi_skill_match": multi_skill_jobs,
            "high_priority": high_priority_jobs,
            "skill_match_rate": round((total_jobs - no_skill_jobs) / total_jobs * 100, 1) if total_jobs > 0 else 0
        }

async def main():
    """メイン実行関数"""
    print("=" * 70)
    print("🤖 Lancers全案件取得システム（Teams28KB最大活用版）")
    print("=" * 70)
    
    notifier = CompleteJobsNotifier()
    
    jobs = await notifier.fetch_jobs()
    
    if jobs:
        notifier.save_data(jobs)
        teams_success = await notifier.send_to_teams(jobs)
        
        print("\n" + "=" * 70)
        print("📊 実行結果:")
        print("=" * 70)
        print(f"✅ 全案件数: {len(jobs)}件")
        print(f"📤 Teams送信: {'成功' if teams_success else '失敗'}")
        print(f"💾 データ保存: 完了")
        
        # 詳細統計
        skill_summary = notifier.create_skill_summary(jobs)
        skill_distribution = notifier.create_skill_distribution(jobs)
        
        print(f"\n🔧 スキル別マッチ件数（上位10位）:")
        for skill, count in list(skill_summary.items())[:10]:
            print(f"   {skill}: {count}件")
        
        print(f"\n📈 スキル分布:")
        print(f"   スキルマッチ率: {skill_distribution['skill_match_rate']}%")
        print(f"   複数スキルマッチ: {skill_distribution['multi_skill_match']}件")
        print(f"   高優先度案件: {skill_distribution['high_priority']}件")
        print(f"   スキルマッチなし: {skill_distribution['no_skill_match']}件")
        
    else:
        print("❌ 案件が見つかりませんでした")

if __name__ == "__main__":
    asyncio.run(main())