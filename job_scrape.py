from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import os

target_team = "G大阪"
url = "https://soccer.yahoo.co.jp/jleague/category/j1/teams/128/schedule?gk=2"

def get_match_info():
    print("🟡 試合情報取得開始")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("🌐 ページアクセス中...")
        page.goto(url, timeout=20000)

        try:
            page.wait_for_selector("div.GameCard", timeout=10000)
            print("✅ GameCard の読み込み確認済み")
        except:
            print("❌ GameCard が表示されませんでした（タイムアウト）")
            return "試合情報が取得できませんでした（カード未表示）"

        html = page.content()
        browser.close()

    # 保存（デバッグ用）
    os.makedirs("cache", exist_ok=True)
    with open("cache/debug_team_page.html", "w", encoding="utf-8") as f:
        f.write(html)
        print("📄 HTMLを保存しました")

    soup = BeautifulSoup(html, "html.parser")
    matches = soup.select("div.GameCard")

    print(f"✅ 試合カード検出数: {len(matches)}")

    future_matches = []
    for card in matches:
        raw = card.get_text(separator="|", strip=True)
        print(f"🔍 RAWテキスト: {raw}")

        if target_team not in raw and "Ｇ大阪" not in raw:
            continue

        time_tag = card.select_one("time")
        if not time_tag or not time_tag.has_attr("datetime"):
