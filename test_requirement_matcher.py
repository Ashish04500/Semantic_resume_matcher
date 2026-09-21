from src.parser import extract_text
from src.jd_extractor import JDExtractor
from src.matching.requirement_matcher import RequirementMatcher


jd_path = r"C:\Users\pranj\Downloads\test_job_description.pdf"

resume_path = r"C:\Users\pranj\Downloads\resume.pdf"


print("Reading Job Description...\n")

jd_text = extract_text(jd_path)

jd_extractor = JDExtractor()

jd_data = jd_extractor.extract(jd_text)


print("Reading resume...\n")

resume_text = extract_text(resume_path)


print("Creating requirement matcher...\n")

matcher = RequirementMatcher()


print("\nMatching requirements...\n")

requirement_result = matcher.match_requirements(
    jd_data["requirements"],
    resume_text
)


print("===== REQUIREMENT MATCHING =====")

print(
    f"\nCoverage: "
    f"{requirement_result['coverage'] * 100:.2f}%"
)


print("\nMATCHED REQUIREMENTS:")

for item in requirement_result["matched_requirements"]:

    print(
        f"\n✓ {item['requirement']}"
    )

    print(
        f"  Similarity: "
        f"{item['similarity']:.4f}"
    )

    print(
        f"  Evidence: "
        f"{item['evidence']}"
    )


print("\nUNMATCHED REQUIREMENTS:")

for item in requirement_result["unmatched_requirements"]:

    print(
        f"\n✗ {item['requirement']}"
    )

    print(
        f"  Best similarity: "
        f"{item['similarity']:.4f}"
    )


print("\n===== SKILL MATCHING =====")


skill_result = matcher.match_skills(
    jd_data["required_skills"],
    resume_text
)


print(
    f"\nSkill Coverage: "
    f"{skill_result['coverage'] * 100:.2f}%"
)


print("\nMATCHED SKILLS:")

for item in skill_result["matched_skills"]:

    print(
        f"✓ {item['skill']} "
        f"({item['similarity']:.4f})"
    )


print("\nUNMATCHED SKILLS:")

for item in skill_result["unmatched_skills"]:

    print(
        f"✗ {item['skill']} "
        f"({item['similarity']:.4f})"
    )


print("\n===== TEST PASSED =====")