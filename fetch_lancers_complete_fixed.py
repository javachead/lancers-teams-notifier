import os, json, datetime, requests

def send_to_teams(webhook_url: str, payload: dict):
    dry = os.getenv("DRY_RUN", "").lower() in ("1","true","yes")
    if dry or not webhook_url:
        print("[DRY-RUN] Would POST to Teams:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    resp = requests.post(webhook_url, json=payload, timeout=10)
    resp.raise_for_status()
    print("[OK] Posted to Teams:", resp.status_code)

def main():
    # ここでは実処理の代わりにダミーの通知を作る
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    payload = {
        "title": "Lancers Notify テスト",
        "text": f"これはDRY-RUNテストです。時刻: {now}",
        # Teams Incoming Webhook は "text" だけでも投稿可
    }
    url = os.getenv("TEAMS_WEBHOOK_URL", "")
    print("ENV:", {"DRY_RUN": os.getenv("DRY_RUN"), "TEAMS_WEBHOOK_URL_set": bool(url)})
    send_to_teams(url, payload)

if __name__ == "__main__":
    main()
