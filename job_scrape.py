from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import os

target_team = "G大阪"
url = "https://soccer.yahoo.co.jp/jleague/category/j1/teams/128/schedule?gk=2"

def get_match_info():
    print("🟡 試合情報取得開始")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("🌐 ページアクセス中...")
        page.goto(url, timeout=20000)
        page.wait_for_selector(".sc-tableGame__data", timeout=10000)
        html = page.content()
        browser.close()

    # 保存（デバッグ用）
    os.makedirs("cache", exist_ok=True)
    with open("cache/debug_team_page.html", "w", encoding="utf-8") as f:
        f.write(html)
        print("📄 HTMLを保存しました")

    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("tr")

    future_matches = []
    for row in rows:
        teams = row.select(".sc-tableGame__team")
        if len(teams) < 2:
            continue

        team_names = [team.get_text(strip=True) for team in teams]
        if target_team not in team_names:
            continue

        date_cell = row.select_one(".sc-tableGame__data--date")
        if date_cell:
            match_date_text = date_cell.get_text(strip=True).split()[0]
            try:
                match_date = datetime.strptime(match_date_text, "%m/%d（%a）")
                match_date = match_date.replace(year=datetime.now().year)
            except:
                continue

            if match_date.date() < datetime.today().date():
                continue

            opponent = team_names[1] if team_names[0] == target_team else team_names[0]
            stadium = row.select_one(".sc-tableGame__data--venue").get_text(strip=True) if row.select_one(".sc-tableGame__data--venue") else "スタジアム不明"

            future_matches.append({
                "date": match_date.strftime("%Y/%m/%d"),
                "teams": f"{target_team} vs {opponent}",
                "stadium": stadium
            })

    if future_matches:
        next_match = future_matches[0]
        info = f"{target_team}の次の試合: {next_match['date']} {next_match['teams']} @ {next_match['stadium']}"
        print("✅ 試合情報抽出成功:", info)
        return info
    else:
        print("⚠️ G大阪の未来の試合が見つかりませんでした")
        return "試合情報が見つかりませんでした…"

def save_to_cache(info):
    os.makedirs("cache", exist_ok=True)
    with open("cache/match_info.txt", "w", encoding="utf-8") as f:
        f.write(info)
    print("✅ match_info.txt に保存完了")

if __name__ == "__main__":
    info = get_match_info()
    save_to_cache(info)
    print("🎉 完了！")
