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
    swimmer_rows = []
    for row in rows:
        cells = row.find_all(["td", "th"])
        row_data = [cell.get_text(strip=True) for cell in cells]
        swimmer_id = None
        swimmer_name = None
        swimmer_url = None
        for cell in cells:
            a = cell.find("a", href=True)
            if a and "/Players/Details/" in a['href']:
                href = a['href']
                match = re.search(r"/Players/Details/(\d+)", href)
                if match:
                    swimmer_id = match.group(1)
                    swimmer_name = a.get_text(strip=True)
                    swimmer_url = href
        if swimmer_id:
            swimmer_rows.append({
                "swimmer_id": swimmer_id,
                "swimmer_name": swimmer_name,
                "swimmer_url": swimmer_url,
                "row_data": row_data
            })

    # Write to CSV
    with open("swimmers_from_isr_comp14679.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["swimmer_id", "swimmer_name", "swimmer_url", "row_data"])
        for row in swimmer_rows:
            writer.writerow([row["swimmer_id"], row["swimmer_name"], row["swimmer_url"], "|".join(row["row_data"])])
    print(f"Found {len(swimmer_rows)} swimmer IDs. Wrote to swimmers_from_isr_comp14679.csv.")

if __name__ == "__main__":
    main()