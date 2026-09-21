import numpy as np

from src.matching.embeddings import EmbeddingModel
from src.matching.retrieval import ResumeRetriever
from src.matching.reranker import ResumeReranker
from src.matching.requirement_matcher import RequirementMatcher
from src.matching.filtering import FilterScorer


class MatchingPipeline:

    def __init__(self):

        # -----------------------------------------
        # ML COMPONENTS
        # -----------------------------------------

        self.embedding_model = EmbeddingModel()

        self.reranker = ResumeReranker()

        self.requirement_matcher = RequirementMatcher(
            self.embedding_model
        )

        self.filter_scorer = FilterScorer()


    # =================================================
    # NORMALIZE CROSS-ENCODER SCORES
    # =================================================

    def _normalize_reranker_scores(self, scores):

        scores = np.asarray(
            scores,
            dtype=float
        )

        if len(scores) == 0:
            return scores

        minimum = scores.min()
        maximum = scores.max()

        if maximum == minimum:

            return np.ones_like(scores)

        return (
            (scores - minimum)
            / (maximum - minimum)
        )


    # =================================================
    # EXPERIENCE MATCH
    # =================================================

    def _experience_match(
        self,
        jd_data,
        resume_data
    ):

        required_years = jd_data.get(
            "min_years_experience"
        )

        structured_data = resume_data.get(
            "structured_data",
            {}
        )

        candidate_years = structured_data.get(
            "total_years_experience"
        )

        # No experience requirement
        if required_years in (
            None,
            0
        ):

            return {
                "status": "Not Required",
                "score": 1.0,
                "required_years":
                    required_years,
                "candidate_years":
                    candidate_years
            }

        # Candidate experience unknown
        if candidate_years is None:

            return {
                "status": "Unknown",
                "score": 0.5,
                "required_years":
                    required_years,
                "candidate_years":
                    None
            }

        # Candidate meets requirement
        if candidate_years >= required_years:

            return {
                "status": "Match",
                "score": 1.0,
                "required_years":
                    required_years,
                "candidate_years":
                    candidate_years
            }

        # Candidate below requirement
        return {
            "status": "Below Requirement",
            "score": 0.0,
            "required_years":
                required_years,
            "candidate_years":
                candidate_years
        }


    # =================================================
    # CREATE HUMAN-READABLE EXPLANATION
    # =================================================

    def _create_explanation(
        self,
        skill_result,
        requirement_result,
        experience_result,
        filter_result
    ):

        # Skill statistics

        matched_skills = len(
            skill_result[
                "matched_skills"
            ]
        )

        total_skills = (
            len(
                skill_result[
                    "matched_skills"
                ]
            )
            +
            len(
                skill_result[
                    "unmatched_skills"
                ]
            )
        )

        skill_percentage = (
            skill_result["coverage"]
            * 100
        )


        # Requirement statistics

        matched_requirements = len(
            requirement_result[
                "matched_requirements"
            ]
        )

        total_requirements = (
            len(
                requirement_result[
                    "matched_requirements"
                ]
            )
            +
            len(
                requirement_result[
                    "unmatched_requirements"
                ]
            )
        )

        requirement_percentage = (
            requirement_result["coverage"]
            * 100
        )


        explanation = (
            f"Matched {matched_skills} of "
            f"{total_skills} required skills "
            f"({skill_percentage:.0f}%) and "
            f"{matched_requirements} of "
            f"{total_requirements} job requirements "
            f"({requirement_percentage:.0f}%). "
        )


        # Experience explanation

        if experience_result["status"] == "Match":

            explanation += (
                "The candidate meets the "
                "stated experience requirement. "
            )

        elif (
            experience_result["status"]
            == "Below Requirement"
        ):

            explanation += (
                "The candidate's stated "
                "experience is below the "
                "requested level. "
            )

        elif (
            experience_result["status"]
            == "Unknown"
        ):

            explanation += (
                "Experience information "
                "could not be confidently "
                "determined. "
            )

        else:

            explanation += (
                "No minimum experience "
                "requirement was specified. "
            )


        # Filter explanation

        explanation += (
            f"Structured filter score: "
            f"{filter_result['filter_score'] * 100:.0f}%."
        )


        return explanation


    # =================================================
    # MAIN MATCHING PIPELINE
    # =================================================

    def match(
        self,
        jd_text: str,
        jd_data: dict,
        resumes: list[dict],
        retrieval_top_k: int = 20
    ):

        if not resumes:
            return []


        # =============================================
        # STEP 1 — CREATE RESUME EMBEDDINGS
        # =============================================

        resume_texts = [
            resume["raw_text"]
            for resume in resumes
        ]

        resume_embeddings = (
            self.embedding_model.encode(
                resume_texts
            )
        )


        # =============================================
        # STEP 2 — FAISS SEMANTIC RETRIEVAL
        # =============================================

        retriever = ResumeRetriever(
            resume_embeddings
        )

        jd_embedding = (
            self.embedding_model.encode_one(
                jd_text
            )
        )

        retrieval_scores, indices = (
            retriever.search(
                jd_embedding,
                top_k=retrieval_top_k
            )
        )


        retrieved_resumes = [
            resumes[index]
            for index in indices
        ]

        retrieved_texts = [
            resume["raw_text"]
            for resume in retrieved_resumes
        ]


        # =============================================
        # STEP 3 — CROSS-ENCODER RE-RANKING
        # =============================================

        rerank_scores = (
            self.reranker.rerank(
                jd_text,
                retrieved_texts
            )
        )

        normalized_rerank_scores = (
            self._normalize_reranker_scores(
                rerank_scores
            )
        )


        results = []


        # =============================================
        # STEP 4 — PROCESS EACH CANDIDATE
        # =============================================

        for (
            resume,
            retrieval_score,
            rerank_score,
            normalized_rerank_score
        ) in zip(
            retrieved_resumes,
            retrieval_scores,
            rerank_scores,
            normalized_rerank_scores
        ):


            # -----------------------------------------
            # REQUIREMENT MATCHING
            # -----------------------------------------

            requirement_result = (
                self.requirement_matcher
                .match_requirements(
                    jd_data.get(
                        "requirements",
                        []
                    ),
                    resume["raw_text"]
                )
            )


            # -----------------------------------------
            # SKILL MATCHING
            # -----------------------------------------

            skill_result = (
                self.requirement_matcher
                .match_skills(
                    jd_data.get(
                        "required_skills",
                        []
                    ),
                    resume["raw_text"]
                )
            )


            # -----------------------------------------
            # EXPERIENCE MATCHING
            # -----------------------------------------

            experience_result = (
                self._experience_match(
                    jd_data,
                    resume
                )
            )


            # -----------------------------------------
            # STRUCTURED FILTER SCORE
            # -----------------------------------------

            filter_result = (
                self.filter_scorer.score(
                    jd_data,
                    resume
                )
            )


            # =========================================
            # STEP 5 — FINAL SCORE FUSION
            # =========================================
            #
            # Prototype fusion:
            #
            # 50% Cross Encoder
            # 30% Filter Score
            # 20% Skill Coverage
            #
            # This keeps the cross-encoder as the
            # strongest relevance signal while also
            # incorporating structured requirements.
            # =========================================

            final_score = (
                0.50
                * normalized_rerank_score

                +

                0.30
                * filter_result[
                    "filter_score"
                ]

                +

                0.20
                * skill_result[
                    "coverage"
                ]
            )


            final_score *= 100


            # =========================================
            # STEP 6 — EXPLANATION
            # =========================================

            explanation = (
                self._create_explanation(
                    skill_result,
                    requirement_result,
                    experience_result,
                    filter_result
                )
            )


            # =========================================
            # STEP 7 — STORE COMPLETE RESULT
            # =========================================

            results.append({

                # Candidate identity
                "resume_id":
                    resume["resume_id"],

                "filename":
                    resume["filename"],


                # Ranking signals
                "retrieval_score":
                    float(
                        retrieval_score
                    ),

                "cross_encoder_score":
                    float(
                        normalized_rerank_score
                    ),

                "filter_score":
                    float(
                        filter_result[
                            "filter_score"
                        ]
                    ),

                "final_score":
                    float(
                        final_score
                    ),


                # Skill information
                "skill_coverage":
                    float(
                        skill_result[
                            "coverage"
                        ]
                        * 100
                    ),

                "matched_skills":
                    skill_result[
                        "matched_skills"
                    ],

                "unmatched_skills":
                    skill_result[
                        "unmatched_skills"
                    ],


                # Requirement information
                "matched_requirements":
                    requirement_result[
                        "matched_requirements"
                    ],

                "unmatched_requirements":
                    requirement_result[
                        "unmatched_requirements"
                    ],


                # Experience
                "experience_match":
                    experience_result,


                # Filter details
                "filter_details":
                    filter_result[
                        "details"
                    ],


                # Explanation
                "explanation":
                    explanation
            })


        # =============================================
        # STEP 8 — SORT BY FINAL SCORE
        # =============================================

        results.sort(
            key=lambda x: x["final_score"],
            reverse=True
        )


        # =============================================
        # STEP 9 — ASSIGN FINAL RANK
        # =============================================

        for rank, result in enumerate(
            results,
            start=1
        ):

            result["rank"] = rank


        return results