import requests
from bs4 import BeautifulSoup
from datetime import datetime

target_team = "G大阪"
url = "https://soccer.yahoo.co.jp/jleague/category/j1/teams/128/schedule?gk=2"

print("✅ スクレイピング開始")

res = requests.get(url)
print(f"✅ ステータスコード: {res.status_code}")
res.encoding = res.apparent_encoding

with open("cache/team_page.html", "w", encoding="utf-8") as f:
    f.write(res.text)
print("✅ HTML保存完了")

soup = BeautifulSoup(res.text, "html.parser")

matches = soup.select("div.sc-hKFxyN")  # Yahooページで試合カードが並んでるブロック
print(f"✅ 試合件数: {len(matches)} 件")

future_matches = []

for match in matches:
    try:
        raw_text = match.get_text(separator="|", strip=True)

        # 日付、対戦チーム、スタジアムを抽出（必要に応じて正規表現でもOK）
        date_tag = match.select_one("time")
        if not date_tag:
            continue
        date_text = date_tag.get("datetime", "")[:10]  # 例: 2024-05-12
        match_date = datetime.strptime(date_text, "%Y-%m-%d")

        if match_date.date() < datetime.today().date():
            continue

        if target_team not in raw_text:
            continue

        # 対戦カードと会場を含むテキスト全体から抽出
        lines = raw_text.split("|")
        teams = next((l for l in lines if "vs" in l), "不明 vs 不明")
        stadium = next((l for l in lines if "@" in l or "スタジアム" in l), "スタジアム不明")

        future_matches.append({
            "date": match_date.strftime("%Y/%m/%d"),
            "teams": teams,
            "stadium": stadium
        })

    except Exception as e:
        print(f"⚠️ パース失敗: {e}")
        continue

if future_matches:
    print("✅ 試合が見つかりました！")
    next_match = future_matches[0]

    with open("cache/match_info.txt", "w", encoding="utf-8") as f:
        f.write(f"{target_team}の次の試合: {next_match['date']} {next_match['teams']} @ {next_match['stadium']}")
    print("✅ match_info.txt に書き込み完了！")
else:
    print(f"⚠️ {target_team}の未来の試合が見つかりませんでした。")
