from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os

def get_match_info():
    try:
        print("🟡 処理開始：ガンバ大阪のチームページにアクセスします")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://soccer.yahoo.co.jp/team/52", timeout=20000)

            print("✅ チームページアクセス成功")

            # HTML取得＆保存（デバッグ用）
            html = page.content()
            os.makedirs("cache", exist_ok=True)
            with open("cache/debug_team_page.html", "w", encoding="utf-8") as f:
                f.write(html)
                print("📄 HTMLを cache/debug_team_page.html に保存完了")

            soup = BeautifulSoup(html, "html.parser")
            browser.close()

            # 直近の試合情報を抽出（例：試合日・相手など）
            match_section = soup.find("div", class_="sc-ebnZor")
            if not match_section:
                print("⚠️ 試合情報のセクションが見つかりませんでした")
                return "試合情報が見つかりませんでした…"

            match_text = match_section.get_text(strip=True)
            print("🟢 抽出成功:", match_text)
            return f"【自動取得】次の試合：{match_text}"

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
