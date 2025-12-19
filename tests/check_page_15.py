import pdfplumber
import re

pdf_path = r'src/analysis/data/Rudolph_Punkttabelle_2025.pdf'

print("Checking Page 15...")
print("=" * 60)

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[14]  # Page 15 is index 14 (0-indexed)
    text = page.extract_text()
    
    print(f"\nPage 15 Text (first 500 chars):")
    print(repr(text[:500]))
    print("\n" + "=" * 60)
    
    # Check for gender
    gender = "Unknown"
    if "männlich" in text.lower():
        gender = "Male"
    elif "weiblich" in text.lower():
        gender = "Female"
    print(f"Gender: {gender}")
    
    # Check for age
    age_match = re.search(r'Altersklasse\s+(\d+)', text, re.IGNORECASE)
    if age_match:
        age = age_match.group(1)
        print(f"Age extracted: {repr(age)}")
    else:
        print("No age pattern found")
    
    # Look for the exact pattern
    if "Altersklasse" in text:
        idx = text.find("Altersklasse")
        snippet = text[idx:idx+30]
        print(f"Altersklasse context: {repr(snippet)}")
