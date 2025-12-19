import pdfplumber
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(script_dir, 'data', 'Rudolph_Punkttabelle_2025.pdf')

print(f"Inspecting PDF: {pdf_path}")
print("=" * 80)

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}\n")
    
    # Inspect first few pages
    for page_num in range(min(3, len(pdf.pages))):
        page = pdf.pages[page_num]
        print(f"\n{'='*80}")
        print(f"PAGE {page_num + 1}")
        print('='*80)
        
        # Get text
        text = page.extract_text()
        print("\n--- Page Text (first 500 chars) ---")
        print(text[:500] if text else "No text extracted")
        
        # Get tables
        tables = page.extract_tables()
        print(f"\n--- Found {len(tables)} table(s) ---")
        
        for table_idx, table in enumerate(tables):
            print(f"\nTable {table_idx + 1}:")
            print(f"  Rows: {len(table)}")
            print(f"  Columns: {len(table[0]) if table else 0}")
            
            # Show first few rows
            print("\n  First 5 rows:")
            for row_idx, row in enumerate(table[:5]):
                print(f"  Row {row_idx}: {row}")
            
            # Show a data row (skip headers, look for point value 20)
            print("\n  Looking for data row with points=20:")
            for row in table:
                try:
                    if row[0] and int(row[0]) == 20:
                        print(f"  Points 20 row: {row}")
                        print(f"  Number of columns: {len(row)}")
                        break
                except:
                    continue
