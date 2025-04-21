from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os

def get_match_info():
    try:
        print("🟡 処理開始：ガンバ大阪のチームページにアクセスします")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://soccer.yahoo.co.jp/jleague/category/j1/teams/128/schedule?gk=2", timeout=20000)
            print("✅ チームページアクセス成功")

            # HTML取得＆保存（デバッグ用）
            html = page.content()
            os.makedirs("cache", exist_ok=True)
            with open("cache/debug_team_page.html", "w", encoding="utf-8") as f:
                f.write(html)
                print("📄 HTMLを cache/debug_team_page.html に保存完了")

            soup = BeautifulSoup(html, "html.parser")
            browser.close()

            # スケジュールテーブルから未決着（スコアが"-"）の最初の試合を探す
            table = soup.select_one("table.sc-tableGame")
            if not table:
                return "試合情報テーブルが見つかりませんでした…"

            rows = table.find_all("tr")
            for row in rows:
                score = row.select_one(".sc-tableGame__scoreDetail")
                if score and score.text.strip() == "-":
                    date = row.select_one(".sc-tableGame__data--date")
                    category = row.select_one(".sc-tableGame__data--category")
                    teams = row.select_all(".sc-tableGame__data--team span")
                    venue = row.select_one(".sc-tableGame__data--venue")

                    if date and category and len(teams) == 2:
                        match_info = f"{date.get_text(strip=True)} | {category.get_text(strip=True)} | {teams[0].text.strip()} vs {teams[1].text.strip()} @ {venue.get_text(strip=True) if venue else '会場未定'}"
                        print("🟢 抽出成功:", match_info)
                        return f"【自動取得】次の試合：{match_info}"

            return "⚠️ 次の試合情報が見つかりませんでした"

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
