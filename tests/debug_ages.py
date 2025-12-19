import pdfplumber
import re

pdf_path = r'src/analysis/data/Rudolph_Punkttabelle_2025.pdf'

print("Searching for 'Altersklasse' patterns in PDF...")
print("=" * 60)

with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages[:30], 1):  # Check first 30 pages
        text = page.extract_text()
        if text and 'Altersklasse' in text:
            # Look for Altersklasse patterns
            matches = re.findall(r'Altersklasse\s+\d+', text, re.IGNORECASE)
            if matches:
                print(f"\nPage {page_num}:")
                for match in matches:
                    print(f"  Found: {repr(match)}")
                
                # Show a snippet around each match
                for match in matches:
                    idx = text.find(match)
                    if idx != -1:
                        snippet = text[max(0, idx-30):min(len(text), idx+50)]
                        print(f"  Context: {repr(snippet)}")
                        
print("\n" + "=" * 60)
print("Also checking raw text for age 10 and 11 patterns...")
print("=" * 60)

with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages[:30], 1):
        text = page.extract_text()
        if text:
            # Look specifically for patterns with 10 or 11
            if re.search(r'Altersklasse\s+(10|11|105|116)', text, re.IGNORECASE):
                print(f"\nPage {page_num} contains age 10 or 11 pattern")
                # Extract gender
                gender = "Unknown"
                if "männlich" in text.lower():
                    gender = "Male"
                elif "weiblich" in text.lower():
                    gender = "Female"
                print(f"  Gender: {gender}")
                
                # Show the actual match
                age_match = re.search(r'Altersklasse\s+(\d+)', text, re.IGNORECASE)
                if age_match:
                    print(f"  Extracted age: {repr(age_match.group(1))}")
