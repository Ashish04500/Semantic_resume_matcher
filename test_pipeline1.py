from pathlib import Path

from src.jd_processor import JDProcessor
from src.resume_processor import ResumeProcessor
from src.matching.pipeline import MatchingPipeline


# =========================================================
# CONFIGURATION
# =========================================================

JD_PATH = Path(
    r"C:\Users\pranj\Downloads\test_job_description.pdf"
)

# Put your resumes in this folder.
# Change ONLY this folder path if your resumes are somewhere else.
RESUME_FOLDER = Path(
    r"C:\Users\pranj\Downloads\resumes"
)


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt"
}


# =========================================================
# VALIDATE INPUTS
# =========================================================

print("\n==============================")
print("INPUT VALIDATION")
print("==============================")

if not JD_PATH.exists():

    raise FileNotFoundError(
        f"JD not found:\n{JD_PATH}"
    )

if not RESUME_FOLDER.exists():

    raise FileNotFoundError(
        f"Resume folder not found:\n{RESUME_FOLDER}\n\n"
        f"Create this folder and put your resumes inside it."
    )


resume_paths = [
    path
    for path in RESUME_FOLDER.iterdir()
    if path.is_file()
    and path.suffix.lower()
    in SUPPORTED_EXTENSIONS
]


if not resume_paths:

    raise FileNotFoundError(
        f"No PDF/DOCX/TXT resumes found in:\n"
        f"{RESUME_FOLDER}"
    )


print(
    f"JD found: {JD_PATH.name}"
)

print(
    f"Resume folder: {RESUME_FOLDER}"
)

print(
    f"Resumes found: {len(resume_paths)}"
)

for path in resume_paths:

    print(
        f"  - {path.name}"
    )


# =========================================================
# 1. PROCESS JD
# =========================================================

print("\n==============================")
print("1. PROCESSING JD")
print("==============================")


jd_processor = JDProcessor()

jd_result = jd_processor.process_file(
    str(JD_PATH)
)


print(
    "JD:",
    jd_result["filename"]
)


requirements = jd_result.get(
    "requirements",
    []
)


print(
    f"\nExtracted requirements: "
    f"{len(requirements)}"
)


for requirement in requirements:

    print(
        "-",
        requirement
    )


# =========================================================
# 2. PROCESS RESUMES
# =========================================================

print("\n==============================")
print("2. PROCESSING RESUMES")
print("==============================")


resume_processor = ResumeProcessor()

resume_results = (
    resume_processor.process_files(
        [
            str(path)
            for path in resume_paths
        ]
    )
)


valid_resumes = []


for resume in resume_results:

    if resume.get("error"):

        print(
            "ERROR:",
            resume.get("filename"),
            "→",
            resume.get("error")
        )

    else:

        valid_resumes.append(
            resume
        )

        experience = (
            resume
            .get("structured_data", {})
            .get("total_years_experience")
        )

        if experience is None:

            experience_text = "Unknown"

        else:

            experience_text = (
                f"{experience:g} years"
            )

        print(
            "OK:",
            resume["filename"],
            "→",
            experience_text
        )


if not valid_resumes:

    raise RuntimeError(
        "\nNo resumes were successfully processed."
    )


print(
    f"\nSuccessfully processed "
    f"{len(valid_resumes)} resume(s)."
)


# =========================================================
# 3. RUN MATCHING PIPELINE
# =========================================================

print("\n==============================")
print("3. RUNNING MATCHING PIPELINE")
print("==============================")


pipeline = MatchingPipeline()


results = pipeline.match(
    jd_text=jd_result["raw_text"],
    jd_data=jd_result,
    resumes=valid_resumes
)


if not results:

    raise RuntimeError(
        "\nPipeline completed, but produced "
        "zero ranking results."
    )


# =========================================================
# 4. FINAL RANKING
# =========================================================

print("\n==============================")
print("4. FINAL RANKING")
print("==============================")


for result in results:

    print(
        f"\n#{result['rank']} "
        f"{result['filename']}"
    )

    print(
        "Retrieval Score:",
        result["retrieval_score"]
    )

    print(
        "Re-ranking Score:",
        result["cross_encoder_score"]
    )

    print(
        "Filter Score:",
        result["filter_score"]
    )

    print(
        "Requirement Coverage:",
        result["requirement_coverage"]
    )

    print(
        "Final / Fusion Score:",
        result["final_score"]
    )

    print(
        "Matched Requirements:",
        len(
            result[
                "matched_requirements"
            ]
        )
    )

    print(
        "Missing Requirements:",
        len(
            result[
                "unmatched_requirements"
            ]
        )
    )

    print(
        "Explanation:",
        result["explanation"]
    )


# =========================================================
# 5. REQUIREMENT EVIDENCE
# =========================================================

print("\n==============================")
print("5. REQUIREMENT EVIDENCE")
print("==============================")


for result in results:

    print(
        f"\n--- {result['filename']} ---"
    )

    for item in result[
        "matched_requirements"
    ]:

        print(
            "\n✓",
            item["requirement"]
        )

        print(
            "  Evidence:",
            item["evidence"]
        )

        print(
            "  Similarity:",
            item["similarity"]
        )

    for item in result[
        "unmatched_requirements"
    ]:

        print(
            "\n✗",
            item["requirement"]
        )

        print(
            "  No sufficiently similar "
            "resume evidence found."
        )


# =========================================================
# COMPLETE
# =========================================================

print("\n==============================")
print("PIPELINE TEST COMPLETE")
print("==============================")