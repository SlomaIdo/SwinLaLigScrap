import requests
from bs4 import BeautifulSoup
import csv
import re

def main():
    url = "https://isr.org.il/comp.asp?compID=14679"
    print(f"Fetching: {url}")
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the main results table
    table = soup.find("table", class_="res-table")
    if not table:
        print("No table found on the page.")
        return

    rows = table.find_all("tr")
    player_rows = []
    for row in rows:
        cells = row.find_all(["td", "th"])
        row_data = [cell.get_text(strip=True) for cell in cells]
        # Try to find player link in each cell
        player_id = None
        player_name = None
        player_url = None
        for cell in cells:
            a = cell.find("a", href=True)
            if a:
                href = a['href']
                match = re.search(r"/Players/Details/(\d+)", href)
                if match:
                    player_id = match.group(1)
                    player_name = a.get_text(strip=True)
                    player_url = href
        # Only add rows with a player ID
        if player_id:
            player_rows.append({"player_id": player_id, "player_name": player_name, "player_url": player_url, "row_data": row_data})

    # Write to CSV
    with open("players_from_isr_comp14679.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["player_id", "player_name", "player_url", "row_data"])
        for row in player_rows:
            writer.writerow([row["player_id"], row["player_name"], row["player_url"], "|".join(row["row_data"])])
    print(f"Found {len(player_rows)} player IDs. Wrote to players_from_isr_comp14679.csv.")

if __name__ == "__main__":
    main()
