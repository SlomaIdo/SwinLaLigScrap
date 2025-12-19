import sys
sys.path.insert(0, 'ui')
from data_loader import DataLoader

# Load data
loader = DataLoader()
df = loader.load_data()

# Count relay teams (names with commas)
relay_teams = df[df['Full name'].str.contains(',', na=False)]
individual_swimmers = df[~df['Full name'].str.contains(',', na=False)]

print("Data Filtering Results:")
print(f"Total records: {len(df):,}")
print(f"Relay team records (with comma): {len(relay_teams):,}")
print(f"Individual swimmer records: {len(individual_swimmers):,}")

print(f"\nTotal unique names: {df['Full name'].nunique():,}")
print(f"Relay team names: {relay_teams['Full name'].nunique():,}")
print(f"Individual swimmer names: {individual_swimmers['Full name'].nunique():,}")

print("\nSample relay team names:")
for name in relay_teams['Full name'].unique()[:5]:
    print(f"  - {name}")
