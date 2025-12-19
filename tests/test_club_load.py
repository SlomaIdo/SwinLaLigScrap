import sys
sys.path.insert(0, 'ui')
from data_loader import DataLoader

# Test the data loader
loader = DataLoader()
df = loader.load_data()

print("Columns in loaded data:")
print(df.columns.tolist())

if 'Club' in df.columns:
    print("\n✓ Club column found!")
    print(f"Total records: {len(df)}")
    print(f"Records with Club: {df['Club'].notna().sum()}")
    print(f"Unique clubs: {df['Club'].nunique()}")
    print(f"\nSample clubs:")
    print(df['Club'].dropna().value_counts().head(10))
else:
    print("\n✗ Club column not found!")
    print("Available columns:", df.columns.tolist())
