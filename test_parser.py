from src.parser import extract_text

file_path = input("Enter the full path of a PDF/DOCX/TXT file: ")

try:
    text = extract_text(file_path)

    print("\n--- EXTRACTED TEXT ---\n")
    print(text[:3000])

    print("\n--- PARSER TEST PASSED ---")

except Exception as e:
    print(f"\nParser error: {e}")