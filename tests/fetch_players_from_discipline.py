import requests
from bs4 import BeautifulSoup
import csv
import re

def main():
    url = "https://loglig.com:2053/LeagueTable/AthleticsDisciplines/9453"
    print(f"Fetching: {url}")
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all links to player details
    player_links = soup.find_all("a", href=True)
    player_ids = set()
    player_rows = []
    for a in player_links:
        href = a['href']
        match = re.search(r"/Players/Details/(\d+)", href)
        if match:
            player_id = match.group(1)
            player_name = a.get_text(strip=True)
            player_ids.add(player_id)
            player_rows.append({"player_id": player_id, "player_name": player_name, "player_url": href})

    # Write to CSV
    with open("players_from_discipline.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["player_id", "player_name", "player_url"])
        writer.writeheader()
        for row in player_rows:
            writer.writerow(row)
    print(f"Found {len(player_ids)} unique player IDs. Wrote to players_from_discipline.csv.")

if __name__ == "__main__":
    main()
