from bs4 import BeautifulSoup
from datetime import datetime

# ==== ✅ ここを書き換えると他チーム対応可能 ====
# 例: "ガンバ", "G大阪", "アントラーズ", "鹿島", "浦和"など
target_team = "G大阪"

# ==== ✅ HTMLファイルを読み込み ====
with open("debug_team_page (4).html", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# ==== ✅ 全試合を取得して、未来かつ対象チームが含まれるものだけに絞る ====
matches = soup.select(".match-info")
future_matches = []

for match in matches:
    try:
        date_text = match.select_one(".date").get_text(strip=True)
        match_date = datetime.strptime(date_text, "%Y.%m.%d")
        if match_date.date() < datetime.today().date():
            continue  # 過去試合は除外

        match_text = match.get_text()
        if target_team in match_text:
            team_elems = match.select(".team-name")
            teams = [t.get_text(strip=True) for t in team_elems]
            stadium = match.select_one(".stadium").get_text(strip=True)

            future_matches.append({
                "date": date_text,
                "teams": teams,
                "stadium": stadium,
                "raw": match_text
            })

    except Exception:
        continue  # パースエラー等があっても無視

# ==== ✅ 最も近い試合を1件選んで出力 ====
if future_matches:
    future_matches.sort(key=lambda m: datetime.strptime(m["date"], "%Y.%m.%d"))
    next_match = future_matches[0]
    team_vs = " vs ".join(next_match["teams"])

    with open("match_info.txt", "w", encoding="utf-8") as f:
        f.write(f"{target_team}の次の試合: {next_match['date']} {team_vs} @ {next_match['stadium']}")
    print("✅ match_info.txt に書き込み完了！")
else:
    print(f"⚠️ {target_team}の未来の試合が見つかりませんでした。")
