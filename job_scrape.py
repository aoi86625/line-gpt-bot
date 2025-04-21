from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os

def get_match_info():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://soccer.yahoo.co.jp/jleague/schedule")

            # 「Ｇ大阪」が入ってる試合が出るまで待機
            page.wait_for_selector("a:has-text('Ｇ大阪')", timeout=10000)

            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            browser.close()

            # 「ガンバ大阪」の行を探して次の対戦相手を取得
            gamba_row = soup.find("a", string=lambda t: "Ｇ大阪" in t if t else False)
            if gamba_row:
                match_text = gamba_row.get_text(strip=True)
                return f"【自動取得】次の試合：{match_text}"
            else:
                return "ガンバ大阪の試合が見つからなかったで…"
    except Exception as e:
        return f"試合情報の取得に失敗しました…（{e}）"

def save_to_cache(info):
    os.makedirs("cache", exist_ok=True)
    with open("cache/match_info.txt", "w", encoding="utf-8") as f:
        f.write(info)

if __name__ == "__main__":
    info = get_match_info()
    save_to_cache(info)
    print("✅ 試合情報をキャッシュしました！")
