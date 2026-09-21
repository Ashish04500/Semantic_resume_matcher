from dotenv import load_dotenv
from src.parser import extract_text
from src.resume_extractor import ResumeExtractor

load_dotenv()

file_path = input("Enter the full path of your resume: ")

try:
    resume_text = extract_text(file_path)

    print("\nExtracting resume information...\n")

    extractor = ResumeExtractor()
    result = extractor.extract(resume_text)

    print("===== STRUCTURED RESUME =====")
    print(result)

except Exception as e:
    print(f"\nError: {e}")