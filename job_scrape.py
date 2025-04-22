from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import os

def get_match_info():
    print("🟡 処理開始：ガンバ大阪の試合情報を取得します")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://soccer.yahoo.co.jp/jleague/category/j1/teams/128/schedule?gk=2", timeout=20000)
        page.wait_for_timeout(5000)  # JS読み込み待ち
        print("✅ ページアクセス成功")

        html = page.content()
        os.makedirs("cache", exist_ok=True)
        with open("cache/debug_team_page.html", "w", encoding="utf-8") as f:
            f.write(html)
            print("📄 HTMLを cache/debug_team_page.html に保存完了")

        soup = BeautifulSoup(html, "html.parser")
        browser.close()

        # 全試合行を取得（2行構成の最初の tr のみ）
        rows = soup.select("section#scheduleTable tbody tr")
        print(f"✅ 試合行検出数: {len(rows)}")

        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 7:
                continue

            date = cells[0].get_text(strip=True)
            category = cells[1].get_text(strip=True)
            home = cells[3].get_text(strip=True)
            score = cells[4].get_text(strip=True)
            away = cells[5].get_text(strip=True)
            venue = cells[6].get_text(strip=True)

            # 今日以降の試合を抽出（未来フィルタは任意）
            if "vs" not in score:
                continue  # スコアが未確定 = 未来の試合

            match_info = f"{date}｜{category}｜{home} {score} {away}｜{venue}"
            print("🟢 抽出成功:", match_info)
            return f"【自動取得】次の試合：{match_info}"

        print("⚠️ 条件に合う試合が見つかりませんでした")
        return "試合情報が見つかりませんでした…"

def save_to_cache(info):
    os.makedirs("cache", exist_ok=True)
    with open("cache/match_info.txt", "w", encoding="utf-8") as f:
        f.write(info)
    print("✅ キャッシュに保存しました")

if __name__ == "__main__":
    info = get_match_info()
    save_to_cache(info)
    print("🎉 完了！")
