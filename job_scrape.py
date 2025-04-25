import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import os

target_team = "G大阪"
url = "https://soccer.yahoo.co.jp/jleague/category/j1/teams/128/schedule?gk=2"

async def scrape_gamba_schedule(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("🌐 アクセス開始...")
        await page.goto(url, wait_until='networkidle')
        await page.wait_for_selector("section#scheduleTable table.sc-tableGame")

        os.makedirs("cache", exist_ok=True)
        await page.screenshot(path="cache/screenshot.png", full_page=True)
        html = await page.content()
        await browser.close()

        with open("cache/debug_team_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ HTML保存済み")

        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.select("table.sc-tableGame tbody tr")
        print(f"✅ 試合行数: {len(rows)}")

        match_info = []
        for i, row in enumerate(rows):
            try:
                date_elem = row.select_one("td.sc-tableGame__data--date")
                teams_elem = row.select("td.sc-tableGame__data--team")
                stadium_elem = row.select_one("td.sc-tableGame__data--venue")

                # ログ出力（デバッグ）
                print(f"\n[DEBUG] Match Row {i+1}")
                print(f"  date_elem: {date_elem}")
                print(f"  teams_elem: {teams_elem}")
                print(f"  stadium_elem: {stadium_elem}")

                if not date_elem or len(teams_elem) < 2:
                    print("  ⛔ データ不足でスキップ")
                    continue

                date_text = date_elem.get_text(strip=True).split()[0]
                try:
                    match_date = datetime.strptime(date_text, "%m/%d")
                    match_date = match_date.replace(year=datetime.now().year)
                except:
                    print("  ⛔ 日付パース失敗")
                    continue

                if match_date.date() < datetime.today().date():
                    print("  ⏭ 過去の試合なのでスキップ")
                    continue

                home_team = teams_elem[0].get_text(strip=True)
                away_team = teams_elem[1].get_text(strip=True)

                print(f"  チーム: {home_team} vs {away_team}")
                if target_team not in [home_team, away_team]:
                    print("  ⏭ G大阪ではないためスキップ")
                    continue

                opponent = away_team if home_team == target_team else home_team
                stadium = stadium_elem.get_text(strip=True) if stadium_elem else "スタジアム不明"

                match_info.append({
                    "date": match_date.strftime("%Y/%m/%d"),
                    "teams": f"{target_team} vs {opponent}",
                    "stadium": stadium
                })
                print("  ✅ 試合情報追加済み")

            except Exception as e:
                print(f"  ❌ 例外発生: {e}")

        return match_info

def save_to_cache(info):
    os.makedirs("cache", exist_ok=True)
    with open("cache/match_info.txt", "w", encoding="utf-8") as f:
        if info:
            next_match = info[0]
            f.write(f"{target_team}の次の試合: {next_match['date']} {next_match['teams']} @ {next_match['stadium']}")
        else:
            f.write("試合情報が見つかりませんでした…")
    print("✅ match_info.txt に保存完了")

if __name__ == "__main__":
    match_info = asyncio.run(scrape_gamba_schedule(url))
    save_to_cache(match_info)
    print("🎉 完了！")
