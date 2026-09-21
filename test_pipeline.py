from src.parser import extract_text
from src.jd_extractor import JDExtractor
from src.resume_processor import ResumeProcessor
from src.matching.pipeline import MatchingPipeline


jd_path = r"C:\Users\pranj\Downloads\test_job_description.pdf"

resume_paths = [
    r"C:\Users\pranj\Downloads\resume.pdf",
]


print("Processing Job Description...\n")

jd_text = extract_text(jd_path)

jd_extractor = JDExtractor()

jd_data = jd_extractor.extract(
    jd_text
)

print(
    f"Job Title: {jd_data['job_title']}"
)


print("\nProcessing resumes...\n")

processor = ResumeProcessor()

resumes = processor.process_files(
    resume_paths
)

resumes = [
    resume
    for resume in resumes
    if "error" not in resume
]

print(
    f"Successfully processed: "
    f"{len(resumes)} resume(s)"
)


print("\nRunning complete matching pipeline...\n")

pipeline = MatchingPipeline()

results = pipeline.match(
    jd_text=jd_text,
    jd_data=jd_data,
    resumes=resumes,
    retrieval_top_k=len(resumes)
)


print("\n===== FINAL RANKING =====")

for result in results:

    print(
        f"\n#{result['rank']} "
        f"{result['filename']}"
    )

    print(
        f"Final Score: "
        f"{result['final_score']:.2f}%"
    )

    print(
        f"Skill Coverage: "
        f"{result['skill_coverage']:.2f}%"
    )

    print(
        f"Experience: "
        f"{result['experience_match']['status']}"
    )

    print(
        f"Matched Requirements: "
        f"{len(result['matched_requirements'])}"
    )

    print(
        f"Unmatched Requirements: "
        f"{len(result['unmatched_requirements'])}"
    )

    print(
        f"Explanation: "
        f"{result['explanation']}"
    )


print("\n===== PIPELINE TEST PASSED =====")