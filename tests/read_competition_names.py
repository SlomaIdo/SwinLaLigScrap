import csv

def main():
    # Read the CSV and print compID and competition_name, decoding Hebrew
    with open("competition_names.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            comp_id = row["compID"]
            comp_name = row["competition_name"]
            print(f"compID: {comp_id} | competition_name: {comp_name}")

if __name__ == "__main__":
    main()