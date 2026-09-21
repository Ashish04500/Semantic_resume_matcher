from sentence_transformers import CrossEncoder


class ResumeReranker:
    def __init__(self):
        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    def rerank(self, jd_text, resume_texts):
        """
        Compare one JD against multiple retrieved resumes.

        Returns a cross-encoder score for each resume.
        """

        pairs = [
            [jd_text, resume_text]
            for resume_text in resume_texts
        ]

        scores = self.model.predict(pairs)

        return scores