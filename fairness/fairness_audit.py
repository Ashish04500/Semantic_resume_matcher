import re
import math
from pathlib import Path


# ============================================================
# MASKING
# ============================================================

def mask_resume(text: str) -> str:
    """
    Create a masked version of a resume by removing/generalizing
    demographic-correlated information.
    """

    masked = text

    # --------------------------------------------------------
    # Names
    # --------------------------------------------------------

    masked = re.sub(
        r"(?im)^(name\s*:\s*|candidate\s*:\s*).*$",
        r"\1[MASKED]",
        masked
    )

    # Common resume name/header pattern
    lines = masked.splitlines()

    if lines:
        first_line = lines[0].strip()

        if (
            first_line
            and len(first_line.split()) <= 4
            and not any(
                keyword in first_line.lower()
                for keyword in [
                    "resume",
                    "cv",
                    "software",
                    "engineer",
                    "developer"
                ]
            )
        ):
            lines[0] = "[MASKED NAME]"

    masked = "\n".join(lines)

    # --------------------------------------------------------
    # Gendered pronouns
    # --------------------------------------------------------

    masked = re.sub(
        r"\b(he|him|his|she|her|hers)\b",
        "[MASKED_PRONOUN]",
        masked,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------------
    # Graduation year
    # --------------------------------------------------------

    masked = re.sub(
        r"(?i)"
        r"(graduat(?:ed|ion)|class\s+of|passing\s+year)"
        r"(\s*[:\-]?\s*)"
        r"(19|20)\d{2}",
        r"\1\2[MASKED_YEAR]",
        masked
    )

    # --------------------------------------------------------
    # Address
    # --------------------------------------------------------

    masked = re.sub(
        r"(?im)^(address|residential address|location)"
        r"\s*[:\-]\s*.*$",
        r"\1: [MASKED_LOCATION]",
        masked
    )

    # --------------------------------------------------------
    # ZIP / PIN codes
    # --------------------------------------------------------

    masked = re.sub(
        r"\b\d{6}\b",
        "[MASKED_PIN]",
        masked
    )

    masked = re.sub(
        r"\b\d{5}(?:-\d{4})?\b",
        "[MASKED_ZIP]",
        masked
    )

    # --------------------------------------------------------
    # University / college names
    # --------------------------------------------------------

    masked = re.sub(
        r"(?im)^"
        r"(university|college|institute|school)"
        r"[^:\n]*"
        r"[:\-]?\s*.*$",
        r"[MASKED EDUCATIONAL INSTITUTION]",
        masked
    )

    # Lines containing common education keywords
    education_keywords = [
        "iit ",
        "nit ",
        "university of ",
        "college of ",
        "institute of ",
        "technology"
    ]

    result_lines = []

    for line in masked.splitlines():

        lower = line.lower()

        if any(
            keyword in lower
            for keyword in education_keywords
        ):
            # Preserve degree information where possible
            if any(
                degree in lower
                for degree in [
                    "b.tech",
                    "btech",
                    "m.tech",
                    "mtech",
                    "b.e",
                    "b.e.",
                    "m.e",
                    "m.e.",
                    "b.sc",
                    "m.sc",
                    "bca",
                    "mca",
                    "mba"
                ]
            ):
                result_lines.append(
                    "[MASKED UNIVERSITY/COLLEGE] "
                    + line
                )
            else:
                result_lines.append(
                    "[MASKED UNIVERSITY/COLLEGE]"
                )
        else:
            result_lines.append(line)

    return "\n".join(result_lines)


# ============================================================
# RANK CORRELATION
# ============================================================

def rank_positions(ranking):
    return {
        resume_id: position + 1
        for position, resume_id
        in enumerate(ranking)
    }


def kendall_tau(original, masked):
    """
    Calculate Kendall's tau manually so no additional package
    is required.
    """

    common = [
        resume_id
        for resume_id in original
        if resume_id in masked
    ]

    if len(common) < 2:
        return 1.0

    original_positions = rank_positions(original)
    masked_positions = rank_positions(masked)

    concordant = 0
    discordant = 0

    for i in range(len(common)):
        for j in range(i + 1, len(common)):

            a = common[i]
            b = common[j]

            original_difference = (
                original_positions[a]
                - original_positions[b]
            )

            masked_difference = (
                masked_positions[a]
                - masked_positions[b]
            )

            product = (
                original_difference
                * masked_difference
            )

            if product > 0:
                concordant += 1
            elif product < 0:
                discordant += 1

    total = concordant + discordant

    if total == 0:
        return 1.0

    return (
        (concordant - discordant)
        / total
    )


def spearman_rho(original, masked):
    """
    Calculate Spearman's rank correlation manually.
    """

    common = [
        resume_id
        for resume_id in original
        if resume_id in masked
    ]

    n = len(common)

    if n < 2:
        return 1.0

    original_positions = rank_positions(original)
    masked_positions = rank_positions(masked)

    difference_squared = 0

    for resume_id in common:

        difference = (
            original_positions[resume_id]
            - masked_positions[resume_id]
        )

        difference_squared += difference ** 2

    return 1 - (
        6 * difference_squared
        / (n * (n ** 2 - 1))
    )


# ============================================================
# TOP-K SELECTION AUDIT
# ============================================================

def top_k_selection_difference(
    original,
    masked,
    k=5
):
    original_top_k = set(original[:k])
    masked_top_k = set(masked[:k])

    if not original_top_k:
        return {
            "original_top_k": [],
            "masked_top_k": [],
            "selection_difference": 0.0
        }

    changed = (
        original_top_k.symmetric_difference(
            masked_top_k
        )
    )

    difference = (
        len(changed)
        / (2 * len(original_top_k))
    )

    return {
        "original_top_k": list(original_top_k),
        "masked_top_k": list(masked_top_k),
        "selection_difference": difference
    }


# ============================================================
# FOUR-FIFTHS STYLE AUDIT
# ============================================================

def four_fifths_audit(
    original,
    masked,
    k=5
):
    """
    Audit changes in top-K selection.

    This is an audit indicator only.
    It does NOT modify ranking or scores.
    """

    original_top_k = set(original[:k])
    masked_top_k = set(masked[:k])

    all_candidates = set(original)

    if not all_candidates:
        return {
            "ratio": 1.0,
            "flag": False
        }

    original_rate = (
        len(original_top_k)
        / len(all_candidates)
    )

    masked_rate = (
        len(masked_top_k)
        / len(all_candidates)
    )

    if original_rate == 0:
        ratio = 1.0
    else:
        ratio = (
            masked_rate
            / original_rate
        )

    return {
        "original_selection_rate":
            round(original_rate, 4),

        "masked_selection_rate":
            round(masked_rate, 4),

        "selection_rate_ratio":
            round(ratio, 4),

        "flag_four_fifths":
            ratio < 0.80
    }


# ============================================================
# AUDIT
# ============================================================

def run_fairness_audit(
    original_ranking,
    masked_ranking,
    k=5
):

    tau = kendall_tau(
        original_ranking,
        masked_ranking
    )

    rho = spearman_rho(
        original_ranking,
        masked_ranking
    )

    selection = top_k_selection_difference(
        original_ranking,
        masked_ranking,
        k
    )

    four_fifths = four_fifths_audit(
        original_ranking,
        masked_ranking,
        k
    )

    return {
        "kendall_tau": round(tau, 4),
        "spearman_rho": round(rho, 4),
        "top_k_selection": selection,
        "four_fifths_audit": four_fifths
    }


# ============================================================
# DEMO
# ============================================================

def main():

    # --------------------------------------------------------
    # Example resume
    # Replace this with an actual resume when integrating
    # with the Streamlit application.
    # --------------------------------------------------------

    original_resume = """
    Rahul Sharma
    Software Engineer

    Male

    B.Tech in Computer Science
    Indian Institute of Technology Example

    Graduated: 2024

    Address: Kolkata, West Bengal - 700001

    2 years of software engineering experience.

    Skills:
    Python, Java, SQL, Machine Learning
    """

    masked_resume = mask_resume(
        original_resume
    )

    print("\n===================================")
    print("       FAIRNESS MASKING")
    print("===================================")

    print("\n--- ORIGINAL RESUME ---")
    print(original_resume)

    print("\n--- MASKED RESUME ---")
    print(masked_resume)

    # --------------------------------------------------------
    # Example rankings
    # These represent rankings returned by the SAME matching
    # pipeline before and after masking.
    # --------------------------------------------------------

    original_ranking = [
        "RES001",
        "RES002",
        "RES003",
        "RES004",
        "RES005"
    ]

    masked_ranking = [
        "RES001",
        "RES003",
        "RES002",
        "RES004",
        "RES005"
    ]

    report = run_fairness_audit(
        original_ranking,
        masked_ranking,
        k=5
    )

    print("\n===================================")
    print("        FAIRNESS AUDIT")
    print("===================================")

    print(
        "Kendall's tau :",
        report["kendall_tau"]
    )

    print(
        "Spearman's rho:",
        report["spearman_rho"]
    )

    print(
        "Top-K selection difference:",
        round(
            report["top_k_selection"][
                "selection_difference"
            ],
            4
        )
    )

    print(
        "Four-fifths ratio:",
        report["four_fifths_audit"][
            "selection_rate_ratio"
        ]
    )

    print(
        "Four-fifths flag:",
        report["four_fifths_audit"][
            "flag_four_fifths"
        ]
    )

    print("\n===================================")
    print(
        "Audit only — no scores or rankings "
        "were automatically changed."
    )
    print("===================================\n")


if __name__ == "__main__":
    main()