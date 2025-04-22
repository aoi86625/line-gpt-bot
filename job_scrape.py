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

        if target_team not in raw:
            continue

        # 日付
        time_tag = card.select_one("time")
        if not time_tag or not time_tag.has_attr("datetime"):
            continue
        date_text = time_tag["datetime"][:10]
        match_date = datetime.strptime(date_text, "%Y-%m-%d")
        if match_date.date() < datetime.today().date():
            continue

        # 対戦カード、スタジアム抽出
        lines = raw.split("|")
        teams = next((l for l in lines if "vs" in l), "不明 vs 不明")
        stadium = next((l for l in lines if "＠" in l or "スタジアム" in l), "スタジアム不明")

        future_matches.append({
            "date": match_date.strftime("%Y/%m/%d"),
            "teams": teams,
            "stadium": stadium
        })

    if future_matches:
        next_match = future_matches[0]
        info = f"{target_team}の次の試合: {next_match['date']} {next_match['teams']} @ {next_match['stadium']}"
        print("✅ 試合情報抽出成功:", info)
        return info
    else:
        print("⚠️ G大阪の未来の試合が見つかりませんでした")
        return "試合情報が見つかりませんでした…"

def save_to_cache(info):
    os.makedirs("cache", exist_ok=True)
    with open("cache/match_info.txt", "w", encoding="utf-8") as f:
        f.write(info)
    print("✅ match_info.txt に保存完了")

if __name__ == "__main__":
    info = get_match_info()
    save_to_cache(info)
    print("🎉 完了！")
