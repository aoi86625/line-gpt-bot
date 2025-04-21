import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ==== ✅ チーム指定（Bot対話で動的に変えたい場合は変数化可能） ====
target_team = "G大阪"

# ==== ✅ 本番URL（ガンバ大阪の試合スケジュール） ====
url = "https://soccer.yahoo.co.jp/jleague/category/j1/teams/128/schedule?gk=2"

# ==== ✅ ページ取得（HTML保存は任意、デバッグ用） ====
res = requests.get(url)
res.encoding = res.apparent_encoding

with open("cache/team_page.html", "w", encoding="utf-8") as f:
    f.write(res.text)

soup = BeautifulSoup(res.text, "html.parser")

# ==== ✅ 試合情報の取得 ====
matches = soup.select("table tbody tr")
future_matches = []

for match in matches:
    try:
        # 日付取得
        date_text = match.select_one("th").get_text(strip=True)
        match_date = datetime.strptime(date_text, "%m/%d（%a）")
        match_date = match_date.replace(year=datetime.today().year)

        if match_date.date() < datetime.today().date():
            continue  # 過去の試合はスキップ

        # チーム情報取得（例：G大阪 vs 川崎F）
        teams = match.select("td")[2].get_text(strip=True).split("vs.")
        teams = [team.strip() for team in teams]

        if target_team not in teams:
            continue

        # スタジアム情報
        stadium = match.select("td")[3].get_text(strip=True)

        future_matches.append({
            "date": match_date.strftime("%Y/%m/%d"),
            "teams": teams,
            "stadium": stadium
        })

    except Exception:
        continue  # パース失敗時はスキップ

# ==== ✅ 最も近い試合を出力 ====
if future_matches:
    next_match = future_matches[0]
    team_vs = " vs ".join(next_match["teams"])

    with open("cache/match_info.txt", "w", encoding="utf-8") as f:
        f.write(f"{target_team}の次の試合: {next_match['date']} {team_vs} @ {next_match['stadium']}")
    print("✅ match_info.txt に書き込み完了！")
else:
    print(f"⚠️ {target_team}の未来の試合が見つかりませんでした。")
