from src.resume_processor import ResumeProcessor


resume_paths = [
    r"C:\Users\pranj\Downloads\resume.pdf",
    # Add more resume paths here only for testing
]


print("Starting resume processing...\n")

processor = ResumeProcessor()

results = processor.process_files(resume_paths)

print("===== RESUME PROCESSING RESULTS =====")

for result in results:

    print("\n-----------------------------------")

    print("Resume ID:")
    print(result["resume_id"])

    print("Filename:")
    print(result["filename"])

    if "error" in result:
        print("ERROR:")
        print(result["error"])
    else:
        print("Status: SUCCESS")

print("\n===== TEST COMPLETED =====")