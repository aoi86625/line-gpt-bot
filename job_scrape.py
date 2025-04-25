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
        await page.goto(url, wait_until='networkidle')
        await page.wait_for_selector("section#scheduleTable table.sc-tableGame")

        # ページのスクショとHTMLを保存（デバッグ用）
        os.makedirs("cache", exist_ok=True)
        await page.screenshot(path="cache/screenshot.png", full_page=True)
        html = await page.content()
        await browser.close()

        with open("cache/debug_team_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        soup = BeautifulSoup(html, 'html.parser')
        schedule_section = soup.select_one("section#scheduleTable")
        matches = schedule_section.select("table.sc-tableGame tbody tr")

        match_info = []
        for match in matches:
            date_elem = match.select_one("td.sc-tableGame__data--date")
            teams_elem = match.select("td.sc-tableGame__data--team")
            stadium_elem = match.select_one("td.sc-tableGame__data--venue")

            if date_elem and len(teams_elem) == 2:
                date_text = date_elem.get_text(strip=True).split()[0]
                try:
                    match_date = datetime.strptime(date_text, "%m/%d（%a）")
                    match_date = match_date.replace(year=datetime.now().year)
                except:
                    continue

                if match_date.date() < datetime.today().date():
                    continue

                home_team = teams_elem[0].get_text(strip=True)
                away_team = teams_elem[1].get_text(strip=True)
                stadium = stadium_elem.get_text(strip=True) if stadium_elem else "スタジアム不明"

                if target_team in [home_team, away_team]:
                    opponent = away_team if home_team == target_team else home_team
                    match_info.append({
                        "date": match_date.strftime("%Y/%m/%d"),
                        "teams": f"{target_team} vs {opponent}",
                        "stadium": stadium
                    })

        return match_info

def save_to_cache(info):
    os.makedirs("cache", exist_ok=True)
    with open("cache/match_info.txt", "w", encoding="utf-8") as f:
        if info:
            next_match = info[0]
            f.write(f"{target_team}の次の試合: {next_match['date']} {next_match['teams']} @ {next_match['stadium']}")
        else:
            f.write("試合情報が見つかりませんでした…")

if __name__ == "__main__":
    match_info = asyncio.run(scrape_gamba_schedule(url))
    save_to_cache(match_info)
    print("🎉 完了！")
