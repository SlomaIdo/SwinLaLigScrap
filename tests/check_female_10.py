import pdfplumber
import re

pdf_path = r'src/analysis/data/Rudolph_Punkttabelle_2025.pdf'

print("Checking all pages for Female Age 10...")
print("=" * 60)

with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages, 1):
        text = page.extract_text()
        if text:
            # Check if this is a female page
            is_female = "weiblich" in text.lower()
            
            # Check for age 10 patterns
            has_age_10 = re.search(r'Altersklasse\s+(10|105)', text, re.IGNORECASE)
            
            if is_female and has_age_10:
                print(f"\n✓ FOUND Female Age 10 on Page {page_num}")
                age_match = re.search(r'Altersklasse\s+(\d+)', text, re.IGNORECASE)
                if age_match:
                    print(f"  Extracted age value: {repr(age_match.group(1))}")
                snippet = text[:200]
                print(f"  First 200 chars: {repr(snippet)}")

print("\n" + "=" * 60)
print("Summary of all Female pages:")
print("=" * 60)

with pdfplumber.open(pdf_path) as pdf:
    female_ages = []
    for page_num, page in enumerate(pdf.pages, 1):
        text = page.extract_text()
        if text and "weiblich" in text.lower():
            age_match = re.search(r'Altersklasse\s+(\d+)', text, re.IGNORECASE)
            if age_match:
                age = age_match.group(1)
                female_ages.append((page_num, age))
                
    for page, age in female_ages:
        print(f"  Page {page:2d}: Female Age {age}")

print(f"\nTotal female pages: {len(female_ages)}")
female_age_values = sorted(set([age for _, age in female_ages]))
print(f"Unique female ages: {female_age_values}")
