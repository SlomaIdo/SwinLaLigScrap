import pdfplumber
import os
import re

script_dir = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(script_dir, 'data', 'Rudolph_Punkttabelle_2025.pdf')

print("Analyzing column structure...")
print("=" * 80)

with pdfplumber.open(pdf_path) as pdf:
    # Look at page 2 which has clearer structure
    page = pdf.pages[1]
    table = page.extract_tables()[0]
    
    # Get headers
    stroke_row = table[0]  # Freestyle, Breaststroke, etc.
    distance_row = table[1]  # 50, 100, 200, etc.
    
    print("Analyzing column positions with actual data...")
    print("\nColumn mapping:")
    
    # Get a data row (points 20)
    data_row = table[2]
    
    event_columns = []
    for col_idx in range(len(data_row)):
        cell = data_row[col_idx]
        
        # Check if this column has a time value (format XX:XX,XX or XX,XX)
        if cell and isinstance(cell, str) and re.search(r'\d{1,2}[:,]\d{2}', cell):
            # Find the stroke type
            stroke = None
            distance = None
            
            # Look backwards to find stroke header
            for i in range(col_idx, -1, -1):
                if stroke_row[i] and stroke_row[i] not in ['', 'Strecke\nPunkte', 'Pkt.']:
                    stroke = stroke_row[i]
                    break
            
            # Get distance from distance row
            if distance_row[col_idx]:
                distance = distance_row[col_idx]
            else:
                # Look backwards for distance
                for i in range(col_idx, -1, -1):
                    if distance_row[i] and distance_row[i].isdigit():
                        distance = distance_row[i]
                        break
            
            if stroke and distance:
                stroke_clean = stroke.strip()
                event_name = f"{distance}m {stroke_clean}"
                event_columns.append((col_idx, event_name, cell))
                print(f"  Column {col_idx:2d}: {event_name:30s} -> {cell}")
    
    print(f"\nTotal event columns found: {len(event_columns)}")
    print("\nColumn indices to use:")
    for col_idx, event_name, _ in event_columns:
        print(f"  ({col_idx}, \"{event_name}\"),")
