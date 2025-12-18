import sys
sys.path.insert(0, 'ui')
from data_loader import DataLoader
import pandas as pd

# Test the swimmer events summary logic
loader = DataLoader()
df = loader.load_data()

# Test with a sample swimmer
test_swimmer = df['Full name'].iloc[0]
print(f"Testing with swimmer: {test_swimmer}")

swimmer_data = df[df['Full name'].str.upper() == test_swimmer.upper()].copy()
print(f"Total records for swimmer: {len(swimmer_data)}")

# Group by event and calculate statistics
event_stats = []
for event in swimmer_data['Event'].unique():
    event_data = swimmer_data[swimmer_data['Event'] == event].sort_values('Date')
    
    total_races = len(event_data)
    best_time = event_data['result_seconds'].min()
    latest_time = event_data['result_seconds'].iloc[-1]
    first_time = event_data['result_seconds'].iloc[0]
    
    # Calculate improvement (negative means got faster)
    improvement = ((latest_time - first_time) / first_time * 100) if first_time > 0 else 0
    
    event_stats.append({
        'Event': event,
        'Total Races': total_races,
        'Best Time': f"{best_time:.2f}s",
        'Latest Time': f"{latest_time:.2f}s",
        'Improvement': f"{improvement:+.1f}%"
    })

# Create DataFrame
summary_df = pd.DataFrame(event_stats).sort_values('Event')
print("\nEvents Summary:")
print(summary_df.to_string(index=False))
