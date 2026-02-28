import requests
from bs4 import BeautifulSoup
import time
import csv

BASE_URL = "https://isr.org.il/comp.asp?compID={}"  # Competition page URL
START_ID = 16700
END_ID = 16800  # inclusive


def fetch_competition_name(comp_id):
    url = BASE_URL.format(comp_id)
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
        # Try to find the competition name in a <title> or a main header
        title = soup.find('title')
        if title and 'ISR' not in title.text:
            return title.text.strip()
        # Try h1 or h2
        for tag in ['h1', 'h2']:
            header = soup.find(tag)
            if header:
                return header.text.strip()
        # Try a specific div or span if known
        return None
    except Exception as e:
        return None

def main():
    print(f"Fetching competition names for compID {START_ID} to {END_ID}...")
    with open("competition_names.csv", "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["compID", "competition_name"])
        for comp_id in range(START_ID, END_ID + 1):
            name = fetch_competition_name(comp_id)
            writer.writerow([comp_id, name if name else 'Not found'])
            print(f"compID={comp_id}: {name if name else 'Not found'}")
            time.sleep(0.5)  # Be polite to the server

if __name__ == "__main__":
    main()
