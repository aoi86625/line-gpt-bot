from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime

target_team = "G大阪"
url = "https://soccer.yahoo.co.jp/jleague/category/j1/teams/128/schedule?gk=2"

print("✅ Playwrightでページ取得開始")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)
    page.wait_for_timeout(5000)  # ← JS読み込み待ち5秒に延長

    html = page.content()
    browser.close()

# HTML保存（デバッグ用）
with open("cache/team_page.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ レンダリング後のHTML保存完了")

soup = BeautifulSoup(html, "html.parser")
matches = soup.select("section > div > div > div > ul > li")

print(f"✅ 試合ブロック検出数: {len(matches)}")

future_matches = []

for match in matches:
    try:
        raw_text = match.get_text(separator="|", strip=True)
        print("📝 raw_text:", raw_text)

        # G大阪を含む対戦カードのみ対象
        if target_team not in raw_text or "vs" not in raw_text:
            continue

        # 日付
        date_tag = match.select_one("time")
        if not date_tag:
            continue
        date_text = date_tag.get("datetime", "")[:10]
        match_date = datetime.strptime(date_text, "%Y-%m-%d")

        # ※以下、未来試合判定を一時的にOFF（検証目的）
        # if match_date.date() < datetime.today().date():
        #     continue

        # チームとスタジアム
        lines = raw_text.split("|")
        teams = next((l for l in lines if "vs" in l), "不明 vs 不明")
        stadium = next((l for l in lines if "＠" in l or "スタジアム" in l), "スタジアム不明")

        future_matches.append({
            "date": match_date.strftime("%Y/%m/%d"),
            "teams": teams,
            "stadium": stadium
        })

    except Exception as e:
        print(f"⚠️ パース失敗: {e}")
        continue

# 出力
if future_matches:
    print("✅ G大阪の試合が見つかりました")
    next_match = future_matches[0]
    with open("cache/match_info.txt", "w", encoding="utf-8") as f:
        f.write(f"{target_team}の次の試合: {next_match['date']} {next_match['teams']} @ {next_match['stadium']}")
    print("✅ match_info.txt に書き出し完了")
else:
    print(f"⚠️ {target_team}の試合が見つかりませんでした")
