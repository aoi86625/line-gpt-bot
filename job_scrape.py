import requests

# 🔑 ここにあなたのTheSportsDBのAPIキーを入れてね
API_KEY = "3"
TEAM_ID = "133604"  # ガンバ大阪のID（TheSportsDB内）

def get_next_match(api_key, team_id):
    url = f"https://www.thesportsdb.com/api/v1/json/{api_key}/eventsnext.php?id={team_id}"
    response = requests.get(url)
    data = response.json()

    events = data.get("events")
    if not events:
        return "⚠️ 次の試合が見つかりませんでした。"

    next_game = events[0]  # 次の試合（最新）を取得
    date = next_game.get("dateEvent")
    time = next_game.get("strTime")
    home_team = next_game.get("strHomeTeam")
    away_team = next_game.get("strAwayTeam")
    venue = next_game.get("strVenue")

    match_info = f"🗓️ {date} {time}\n⚽ {home_team} vs {away_team}\n🏟️ {venue}"
    return match_info

# 実行して表示
info = get_next_match(API_KEY, TEAM_ID)
print(info)
