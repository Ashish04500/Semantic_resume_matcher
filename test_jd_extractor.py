from dotenv import load_dotenv

from src.parser import extract_text
from src.jd_extractor import JDExtractor

load_dotenv()

file_path = input("Enter the full path of your Job Description: ")

try:
    jd_text = extract_text(file_path)

    print("\nExtracting job description information...\n")

    extractor = JDExtractor()
    result = extractor.extract(jd_text)

    print("===== STRUCTURED JOB DESCRIPTION =====")
    print(result)

except Exception as e:
    print(f"\nError: {e}")