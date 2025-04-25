from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import os

# Yahoo!ガンバ大阪試合日程ページ（2024年〜）
url = "https://soccer.yahoo.co.jp/jleague/category/j1/teams/128/schedule?gk=2"
target_marker = "G"  # G大阪の表記は "G" だけになってることがある

def get_match_info():
    print("🟡 試合情報取得開始")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("🌐 ページアクセス中...")
        page.goto(url, timeout=20000)

        page.wait_for_timeout(3000)  # JS描画待機

        os.makedirs("cache", exist_ok=True)
        page.screenshot(path="cache/screenshot.png", full_page=True)
        print("📸 スクリーンショット保存済み → cache/screenshot.png")

        html = page.content()
        browser.close()

    # HTMLを保存（デバッグ用）
    with open("cache/debug_team_page.html", "w", encoding="utf-8") as f:
        f.write(html)

    # パース開始
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table tbody tr")
    print(f"✅ 試合行数: {len(rows)}")

    future_matches = []

    for row in rows:
        imgs = row.find_all("img")
        alt_texts = [img.get("alt", "") for img in imgs]

        # Gを含むチームロゴが1個以上ある試合を対象とする
        g_count = sum(1 for alt in alt_texts if target_marker in alt)
        if g_count < 1 or len(alt_texts) < 2:
            continue

        cols = row.find_all("td")
        if len(cols) < 2:
            continue

        # 日付取得
        date_raw = cols[0].get_text(strip=True).split()[0]
        try:
            match_date = datetime.strptime(date_raw, "%m/%d")
            match_date = match_date.replace(year=datetime.now().year)
        except:
            continue

        if match_date.date() < datetime.today().date():
            continue

        # チーム名とスタジアム（仮）
        teams = " vs ".join(alt_texts[:2])
        stadium = "スタジアム不明"

        future_matches.append({
            "date": match_date.strftime("%Y/%m/%d"),
            "teams": teams,
            "stadium": stadium
        })

    if future_matches:
        next_match = future_matches[0]
        info = f"G大阪の次の試合: {next_match['date']} {next_match['teams']} @ {next_match['stadium']}"
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
