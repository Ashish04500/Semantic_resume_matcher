import re


def extract_years_from_text(text: str):
    """
    Extract experience years from resume text.

    Examples:
    '2 years of experience' -> 2.0
    '2+ years experience' -> 2.0
    '3 yrs of experience' -> 3.0
    'at least 2 years' -> 2.0
    """

    if not text:
        return None

    text = text.lower()

    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?(?:relevant\s+|professional\s+|work\s+|software\s+)?experience",
        r"(\d+(?:\.\d+)?)\s*\+?\s*yrs?\s+(?:of\s+)?(?:relevant\s+|professional\s+|work\s+)?experience",
        r"(?:minimum|at least)\s+(\d+(?:\.\d+)?)\s*\+?\s*years?",
    ]

    values = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text
        )

        for value in matches:

            try:
                values.append(float(value))
            except ValueError:
                pass

    if not values:
        return None

    return max(values)


class FilterScorer:

    def score(self, jd_data, resume_data):

        scores = []

        details = {}

        # -----------------------------------------
        # EXPERIENCE
        # -----------------------------------------

        required_years = jd_data.get(
            "min_years_experience"
        )

        candidate_years = (
            resume_data
            .get("structured_data", {})
            .get("total_years_experience")
        )

        if required_years in (None, 0):

            experience_score = 1.0
            experience_status = "Not Required"

        elif candidate_years is None:

            experience_score = 0.5
            experience_status = "Unknown"

        elif candidate_years >= required_years:

            experience_score = 1.0
            experience_status = "Match"

        else:

            # Partial experience score.
            # Example: 2 years / 3 years = 0.667
            experience_score = (
                candidate_years / required_years
            )

            experience_status = "Below Requirement"

        scores.append(experience_score)

        details["experience"] = {

            "required_years":
                required_years,

            "candidate_years":
                candidate_years,

            "status":
                experience_status,

            "score":
                experience_score
        }

        # -----------------------------------------
        # CERTIFICATIONS
        # -----------------------------------------

        required_certifications = (
            jd_data.get(
                "certifications_required",
                []
            )
        )

        candidate_certifications = (
            resume_data
            .get("structured_data", {})
            .get("certifications", [])
        )

        if not required_certifications:

            certification_score = 1.0
            certification_status = "Not Required"

        elif not candidate_certifications:

            certification_score = 0.5
            certification_status = "Unknown"

        else:

            candidate_text = " ".join(
                str(cert).lower()
                for cert in candidate_certifications
            )

            matched = sum(
                1
                for cert in required_certifications
                if str(cert).lower()
                in candidate_text
            )

            certification_score = (
                matched /
                len(required_certifications)
            )

            certification_status = (
                "Match"
                if certification_score == 1.0
                else "Partial"
            )

        scores.append(certification_score)

        details["certifications"] = {

            "required":
                required_certifications,

            "candidate":
                candidate_certifications,

            "status":
                certification_status,

            "score":
                certification_score
        }

        # -----------------------------------------
        # FINAL FILTER SCORE
        # -----------------------------------------

        filter_score = (
            sum(scores) / len(scores)
            if scores
            else 1.0
        )

        return {

            "filter_score":
                filter_score,

            "details":
                details
        }