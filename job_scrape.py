from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os

def get_match_info():
    try:
        print("🟡 処理開始：ガンバ大阪の試合を探します")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://soccer.yahoo.co.jp/jleague/", timeout=15000)

            print("✅ ページアクセス成功")

            # 「Ｇ大阪」が出るまで待つ（最大10秒）
            page.wait_for_selector("a:has-text('Ｇ大阪')", timeout=10000)
            print("✅ 'Ｇ大阪' 表示まで待機完了")

            html = page.content()
            with open("cache/debug_page.html", "w", encoding="utf-8") as f:
                f.write(html)
                print("📄 HTMLを debug_page.html に保存完了")

            soup = BeautifulSoup(html, "html.parser")

            browser.close()

            # 「Ｇ大阪」のリンクを探す
            gamba_link = soup.find("a", string=lambda t: "Ｇ大阪" in t if t else False)
            print("🔍 gamba_link =", gamba_link)

            if gamba_link:
                match_text = gamba_link.get_text(strip=True)
                print("🟢 抽出成功:", match_text)
                return f"【自動取得】次の試合：{match_text}"
            else:
                print("⚠️ ガンバ大阪の試合リンクが見つかりませんでした")
                return "ガンバ大阪の試合が見つからなかったで…"

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
