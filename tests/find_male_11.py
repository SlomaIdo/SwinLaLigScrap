import pdfplumber
import re

pdf_path = r'src/analysis/data/Rudolph_Punkttabelle_2025.pdf'

print("Searching for Male Age 11...")
print("=" * 60)

with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages[:20], 1):
        text = page.extract_text()
        if text:
            # Check if this is a male page
            is_male = "männlich" in text.lower()
            
            # Look for patterns that might indicate age 11
            if is_male and ("11" in text[:200] or "116" in text[:200]):
                print(f"\n=== Page {page_num} ===")
                print(f"First 300 chars:\n{repr(text[:300])}")
                
                # Try the updated regex
                age_match = re.search(r'A?\s*ltersklasse\s+(\d+|Offene)', text, re.IGNORECASE)
                if age_match:
                    age = age_match.group(1)
                    print(f"\nExtracted age: {repr(age)}")
                    if age == '116':
                        print("  -> Would be mapped to '11'")
                else:
                    print("\nNo age pattern matched")
