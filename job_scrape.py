from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os

def get_match_info():
    try:
        print("🟡 処理開始：ガンバ大阪のチームページにアクセスします")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://soccer.yahoo.co.jp/team/63", timeout=20000)

            print("✅ ページアクセス成功")

            # HTML取得して保存（デバッグ用）
            html = page.content()
            with open("cache/debug_team_page.html", "w", encoding="utf-8") as f:
                f.write(html)
                print("📄 HTMLを debug_team_page.html に保存完了")

            soup = BeautifulSoup(html, "html.parser")

            browser.close()

            # 「次の試合」のブロックを探す（例：.scoreCard__item などのクラス）
            next_match_block = soup.select_one(".scoreCard__item")  # 試合カード1個目を狙う
            print("🔍 next_match_block =", next_match_block)

            if next_match_block:
                match_text = next_match_block.get_text(separator=" ", strip=True)
                print("🟢 抽出成功:", match_text)
                return f"【自動取得】次の試合：{match_text}"
            else:
                print("⚠️ 次の試合情報が見つかりませんでした")
                return "次の試合が見つからなかったで…"

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
