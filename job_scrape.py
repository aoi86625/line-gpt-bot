from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os

def get_match_info():
    try:
        print("🟡 処理開始：ガンバ大阪の試合情報を取得します")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://soccer.yahoo.co.jp/jleague/category/j1/teams/128/schedule?gk=2", timeout=20000)

            print("✅ ページアクセス成功")

            html = page.content()
            os.makedirs("cache", exist_ok=True)
            with open("cache/debug_team_page.html", "w", encoding="utf-8") as f:
                f.write(html)
                print("📄 HTMLを cache/debug_team_page.html に保存完了")

            soup = BeautifulSoup(html, "html.parser")
            browser.close()

            # 最初の試合行を抽出
            first_row = soup.select_one("section#scheduleTable tbody tr")
            if not first_row:
                print("⚠️ 試合行が見つかりませんでした")
                return "試合情報が見つかりませんでした…"

            cells = first_row.find_all("td")
            if len(cells) < 7:
                print("⚠️ 試合情報の列が不足しています")
                return "試合情報が不完全です…"

            # 日時, 種別, ホーム, スコア, アウェイ, 会場 を取得
            date = cells[0].get_text(strip=True)
            category = cells[1].get_text(strip=True)
            home = cells[3].get_text(strip=True)
            score = cells[4].get_text(strip=True)
            away = cells[5].get_text(strip=True)
            venue = cells[6].get_text(strip=True)

            match_info = f"{date}｜{category}｜{home} {score} {away}｜{venue}"
            print("🟢 抽出成功:", match_info)
            return f"【自動取得】次の試合：{match_info}"

    except Exception as e:
        print("❌ エラー発生:", e)
        return f"試合情報の取得に失敗しました…（{e}）"

def save_to_cache(info):
    os.makedirs("cache", exist_ok=True)
    with open("cache/match_info.txt", "w", encoding="utf-8") as f:
        f.write(info)
    print("✅ キャッシュに保存しました")

if __name__ == "__main__":
    info = get_match_info()
    save_to_cache(info)
    print("🎉 完了！")
