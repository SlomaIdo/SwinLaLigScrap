import requests
from bs4 import BeautifulSoup
import csv

def main():
    url = "https://loglig.com:2053/Players/Details/134429?seasonId=1715"
    print(f"Fetching: {url}")
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    tables = soup.find_all("table")
    if not tables:
        print("No tables found on the page.")
        return

    # Extract swimmer name from the <h2> tag with the specific class and style
    swimmer_name = None
    h2 = soup.find("h2", class_="d-block", style="font-size: 2.7rem; font-weight: bold; text-align:center; margin-top:10px;")
    if h2:
        swimmer_name = h2.get_text(strip=True)
    else:
        swimmer_name = ""

    # Write only the first table to temp2.csv, adding swimmer name as a column
    with open("temp2.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        first_table = tables[0]
        rows = first_table.find_all("tr")
        for i, row in enumerate(rows):
            cells = row.find_all(["td", "th"])
            row_data = [cell.get_text(strip=True) for cell in cells]
            if i == 0:
                # Header row: add swimmer name column
                row_data.append("swimmer_name")
            else:
                row_data.append(swimmer_name)
            writer.writerow(row_data)
    print("Wrote table 1 to temp2.csv with swimmer name column")

if __name__ == "__main__":
    main()