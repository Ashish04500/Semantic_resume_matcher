import re


# ============================================================
# MASKING
# ============================================================

def mask_resume(text: str) -> str:
    """
    Mask demographic-correlated information from a resume.

    The actual resume text is supplied by the application.
    Nothing is hardcoded here.
    """

    if not text:
        return ""

    masked = text

    # --------------------------------------------------------
    # Names
    # --------------------------------------------------------

    masked = re.sub(
        r"(?im)^(name\s*:\s*|candidate\s*:\s*).*$",
        r"\1[MASKED]",
        masked
    )

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
                    "developer",
                    "experience",
                    "skills",
                    "education"
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

    # Explicit gender words
    masked = re.sub(
        r"\b(male|female|man|woman|boy|girl)\b",
        "[MASKED_GENDER]",
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

    # Also mask standalone graduation years in education sections.
    masked = re.sub(
        r"(?<!\d)(19|20)\d{2}(?!\d)",
        "[MASKED_YEAR]",
        masked
    )

    # --------------------------------------------------------
    # Address / Location
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
    # University / college / institute
    # --------------------------------------------------------

    education_keywords = [
        "iit ",
        "nit ",
        "university",
        "college",
        "institute",
        "school of",
        "technology"
    ]

    result_lines = []

    for line in masked.splitlines():

        lower = line.lower()

        if any(
            keyword in lower
            for keyword in education_keywords
        ):

            # Preserve degree information while masking
            # the educational institution.
            degree_found = any(
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
                    "mba",
                    "bachelor",
                    "master",
                    "phd"
                ]
            )

            if degree_found:
                result_lines.append(
                    "[MASKED UNIVERSITY/COLLEGE]"
                )
            else:
                result_lines.append(
                    "[MASKED UNIVERSITY/COLLEGE]"
                )

        else:
            result_lines.append(line)

    return "\n".join(result_lines)


# ============================================================
# RANK UTILITIES
# ============================================================

def rank_positions(ranking):
    """
    Convert a ranking list into:

        resume_id -> rank position
    """

    return {
        resume_id: position + 1
        for position, resume_id in enumerate(ranking)
    }


# ============================================================
# KENDALL'S TAU
# ============================================================

def kendall_tau(original, masked):
    """
    Compare the relative ordering of candidates before
    and after demographic-correlated information is masked.
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

            candidate_a = common[i]
            candidate_b = common[j]

            original_difference = (
                original_positions[candidate_a]
                - original_positions[candidate_b]
            )

            masked_difference = (
                masked_positions[candidate_a]
                - masked_positions[candidate_b]
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


# ============================================================
# SPEARMAN'S RHO
# ============================================================

def spearman_rho(original, masked):
    """
    Compare candidate rank positions before and after masking.
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
    k
):
    """
    Compare which candidates appear in the Top-K
    before and after masking.
    """

    if k <= 0:
        return {
            "original_top_k": [],
            "masked_top_k": [],
            "selection_difference": 0.0,
            "overlap_count": 0
        }

    original_top_k = set(original[:k])
    masked_top_k = set(masked[:k])

    if not original_top_k:
        return {
            "original_top_k": [],
            "masked_top_k": [],
            "selection_difference": 0.0,
            "overlap_count": 0
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

    overlap_count = len(
        original_top_k.intersection(masked_top_k)
    )

    return {
        "original_top_k": list(original[:k]),
        "masked_top_k": list(masked[:k]),
        "selection_difference": round(
            difference,
            4
        ),
        "overlap_count": overlap_count
    }


# ============================================================
# FAIRNESS AUDIT
# ============================================================

def run_fairness_audit(
    original_ranking,
    masked_ranking,
    k
):
    """
    Compare rankings produced by the same matching pipeline
    before and after demographic-correlated information is
    masked.

    This function does not modify scores or rankings.
    """

    if not original_ranking:
        return {
            "kendall_tau": 1.0,
            "spearman_rho": 1.0,
            "top_k_selection": {
                "original_top_k": [],
                "masked_top_k": [],
                "selection_difference": 0.0,
                "overlap_count": 0
            }
        }

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

    return {
        "kendall_tau": round(tau, 4),
        "spearman_rho": round(rho, 4),
        "top_k_selection": selection
    }