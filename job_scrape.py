import requests
from bs4 import BeautifulSoup
from datetime import datetime

target_team = "G大阪"
url = "https://soccer.yahoo.co.jp/jleague/category/j1/teams/128/schedule?gk=2"

print("✅ スクレイピング開始")

try:
    res = requests.get(url)
    print(f"✅ ステータスコード: {res.status_code}")
except Exception as e:
    print(f"❌ リクエスト失敗: {e}")
    exit()

res.encoding = res.apparent_encoding

with open("cache/team_page.html", "w", encoding="utf-8") as f:
    f.write(res.text)
print("✅ HTML保存完了")

soup = BeautifulSoup(res.text, "html.parser")
matches = soup.select("table tbody tr")
print(f"✅ 試合件数: {len(matches)} 件")

future_matches = []

for match in matches:
    try:
        date_text = match.select_one("th").get_text(strip=True)
        match_date = datetime.strptime(date_text, "%m/%d（%a）")
        match_date = match_date.replace(year=datetime.today().year)

        if match_date.date() < datetime.today().date():
            continue

        teams = match.select("td")[2].get_text(strip=True).split("vs.")
        teams = [team.strip() for team in teams]

        if target_team not in teams:
            continue

        stadium = match.select("td")[3].get_text(strip=True)

        future_matches.append({
            "date": match_date.strftime("%Y/%m/%d"),
            "teams": teams,
            "stadium": stadium
        })

    except Exception as e:
        print(f"⚠️ 1件パース失敗: {e}")
        continue

if future_matches:
    print("✅ 試合が見つかりました！")
    next_match = future_matches[0]
    team_vs = " vs ".join(next_match["teams"])

    try:
        with open("cache/match_info.txt", "w", encoding="utf-8") as f:
            f.write(f"{target_team}の次の試合: {next_match['date']} {team_vs} @ {next_match['stadium']}")
        print("✅ match_info.txt に書き込み完了！")
    except Exception as e:
        print(f"❌ ファイル書き込み失敗: {e}")
else:
    print(f"⚠️ {target_team}の未来の試合が見つかりませんでした。")
