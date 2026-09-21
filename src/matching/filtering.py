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

            experience_score = 0.0
            experience_status = "Below Requirement"

        scores.append(experience_score)

        details["experience"] = {
            "required_years": required_years,
            "candidate_years": candidate_years,
            "status": experience_status,
            "score": experience_score
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
            "filter_score": filter_score,
            "details": details
        }