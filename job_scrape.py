import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ==== ✅ チーム指定（将来Bot連携で変数化）====
target_team = "G大阪"

# ==== ✅ 対象URL ====
url = "https://soccer.yahoo.co.jp/jleague/category/j1/teams/128/schedule?gk=2"

# ==== ✅ HTMLを取得してローカルに保存（debug用）====
res = requests.get(url)
res.encoding = res.apparent_encoding

with open("team_page.html", "w", encoding="utf-8") as f:
    f.write(res.text)

# ==== ✅ BeautifulSoupで読み込み ====
soup = BeautifulSoup(res.text, "html.parser")

# ==== ✅ 試合情報の抽出 ====
matches = soup.select("table tbody tr")
future_matches = []

for match in matches:
    try:
        # 日付の取得
        date_text = match.select_one("th").get_text(strip=True)
        # 日付の形式を整形
        match_date = datetime.strptime(date_text, "%m/%d（%a）")
        # 年を補完
        match_date = match_date.replace(year=datetime.today().year)
        if match_date.date() < datetime.today().date():
            continue

        # チーム名の取得
        teams = match.select("td")[2].get_text(strip=True).split("vs.")
        teams = [team.strip() for team in teams]
        if target_team not in teams:
            continue

        # スタジアムの取得
        stadium = match.select("td")[3].get_text(strip=True)

        future_matches.append({
            "date": match_date.strftime("%Y/%m/%d"),
            "teams": teams,
            "stadium": stadium
        })

    except Exception:
        continue

# ==== ✅ 最も近い試合を1件選んで出力 ====
if future_matches:
    next_match = future_matches[0]
    team_vs = " vs ".join(next_match["teams"])

    with open("match_info.txt", "w", encoding="utf-8") as f:
        f.write(f"{target_team}の次の試合: {next_match['date']} {team_vs} @ {next_match['stadium']}")
    print("✅ match_info.txt に書き込み完了！")
else:
    print(f"⚠️ {target_team}の未来の試合が見つかりませんでした。")
