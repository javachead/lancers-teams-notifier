#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import aiohttp
import json
import os

async def test_teams_webhook():
    """Teams Webhookの動作テスト"""
    
    print("🧪 Teams Webhook テスト開始")
    
    # .env ファイルから読み込み
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .env ファイルを読み込みました")
    except ImportError:
        print("⚠️ python-dotenvがインストールされていません")
        print("💡 pip install python-dotenv を実行してください")
        return
    except Exception as e:
        print(f"⚠️ .env ファイルの読み込みエラー: {e}")
    
    # Webhook URLを取得
    webhook_url = os.getenv("TEAMS_WEBHOOK_URL")
    
    if not webhook_url:
        print("❌ TEAMS_WEBHOOK_URLが設定されていません")
        print("💡 .env ファイルに以下を追加してください:")
        print("TEAMS_WEBHOOK_URL=https://your-teams-webhook-url")
        return
    
    print(f"📡 Webhook URL: {webhook_url[:50]}...")
    
    # テストメッセージを作成
    test_message = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": "Lancers通知システム テスト",
        "themeColor": "0078D4",
        "title": "🧪 Lancers通知システム テスト",
        "text": "Teams通知機能が正常に動作しています！\n\n✅ システムの接続確認が完了しました。",
        "potentialAction": [
            {
                "@type": "OpenUri",
                "name": "🔍 Lancersサイトを開く",
                "targets": [
                    {
                        "os": "default",
                        "uri": "https://www.lancers.jp/work/search/system"
                    }
                ]
            }
        ]
    }
    
    try:
        print("📤 Teamsにテストメッセージを送信中...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                webhook_url,
                json=test_message,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    print("✅ Teams送信成功！")
                    print("💬 Teamsチャンネルでメッセージを確認してください")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ 送信失敗 (ステータス: {response.status})")
                    print(f"エラー詳細: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ 送信中にエラーが発生: {e}")
        return False

async def main():
    print("=" * 50)
    print("🚀 Teams Webhook テストツール")
    print("=" * 50)
    
    success = await test_teams_webhook()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 テスト完了！Teams通知システムの準備ができました")
        print("💡 次は fetch_lancers_jobs_with_teams.py を実行してください")
    else:
        print("❌ テスト失敗")
        print("💡 Webhook URLと設定を確認してください")

if __name__ == "__main__":
    asyncio.run(main())