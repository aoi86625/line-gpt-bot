import requests
import os

# 🔑 あなたのTheSportsDBのAPIキーをここに
API_KEY = "3"
TEAM_ID = "134450"  # ガンバ大阪のID

def get_next_match(api_key, team_id):
    url = f"https://www.thesportsdb.com/api/v1/json/{api_key}/eventsnext.php?id={team_id}"
    response = requests.get(url)
    data = response.json()

    events = data.get("events")
    if not events:
        return "⚠️ 次の試合が見つかりませんでした。"

    next_game = events[0]
    date = next_game.get("dateEvent")
    time = next_game.get("strTime")
    home_team = next_game.get("strHomeTeam")
    away_team = next_game.get("strAwayTeam")
    venue = next_game.get("strVenue")

    match_info = f"🗓️ {date} {time}\n⚽ {home_team} vs {away_team}\n🏟️ {venue}"
    return match_info

def save_to_cache(info):
    os.makedirs("cache", exist_ok=True)
    with open("cache/match_info.txt", "w", encoding="utf-8") as f:
        f.write(info)
    print("✅ match_info.txt に保存完了！")

if __name__ == "__main__":
    info = get_next_match(API_KEY, TEAM_ID)
    print(info)
    save_to_cache(info)
