import numpy as np

from src.matching.embeddings import EmbeddingModel


class RequirementMatcher:

    MATCH_THRESHOLD = 0.45

    def __init__(self, embedding_model=None):

        self.embedding_model = (
            embedding_model
            if embedding_model
            else EmbeddingModel()
        )

    def _split_into_chunks(self, text):

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        chunks = []

        current = ""

        for line in lines:

            # Start a new section when the line
            # looks like a heading.
            if len(line) < 80 and current:

                chunks.append(current)

                current = line

            else:

                if current:
                    current += " " + line
                else:
                    current = line

        if current:
            chunks.append(current)

        if not chunks:
            chunks = [text]

        return chunks

    def _semantic_matches(
        self,
        items,
        resume_text,
        item_name
    ):

        if not items:

            return {
                "matched": [],
                "unmatched": [],
                "coverage": 0.0
            }

        resume_chunks = self._split_into_chunks(
            resume_text
        )

        item_embeddings = self.embedding_model.encode(
            items
        )

        resume_embeddings = self.embedding_model.encode(
            resume_chunks
        )

        similarities = np.matmul(
            item_embeddings,
            resume_embeddings.T
        )

        matched = []
        unmatched = []

        for i, item in enumerate(items):

            best_index = int(
                np.argmax(similarities[i])
            )

            similarity = float(
                similarities[
                    i,
                    best_index
                ]
            )

            evidence = resume_chunks[
                best_index
            ]

            result = {
                item_name: item,
                "similarity": similarity,
                "evidence": evidence
            }

            if similarity >= self.MATCH_THRESHOLD:

                matched.append(result)

            else:

                unmatched.append(result)

        coverage = (
            len(matched) / len(items)
        )

        return {
            "matched": matched,
            "unmatched": unmatched,
            "coverage": coverage
        }

    def match_requirements(
        self,
        requirements,
        resume_text
    ):

        result = self._semantic_matches(
            requirements,
            resume_text,
            "requirement"
        )

        return {
            "matched_requirements":
                result["matched"],

            "unmatched_requirements":
                result["unmatched"],

            "coverage":
                result["coverage"]
        }

    def match_skills(
        self,
        required_skills,
        resume_text
    ):

        result = self._semantic_matches(
            required_skills,
            resume_text,
            "skill"
        )

        return {
            "matched_skills":
                result["matched"],

            "unmatched_skills":
                result["unmatched"],

            "coverage":
                result["coverage"]
        }