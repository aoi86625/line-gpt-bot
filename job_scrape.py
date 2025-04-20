from playwright.sync_api import sync_playwright
import os

def get_match_info():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://soccer.yahoo.co.jp/jleague/schedule")
            page.wait_for_timeout(3000)
            content = page.content()
            browser.close()

            # 本番ではここでBeautifulSoupで抽出して整形
            return "【自動取得】次のガンバ大阪の試合は近日中に開催予定やで！"
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

