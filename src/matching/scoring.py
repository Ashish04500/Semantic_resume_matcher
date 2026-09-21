import numpy as np


class MatchScorer:
    def score(self, retrieval_scores):
        """
        Normalize retrieval scores into a 0-1 range.

        Input:
            retrieval_scores -> similarity scores from FAISS

        Output:
            normalized scores
        """

        scores = np.asarray(
            retrieval_scores,
            dtype=float
        )

        if len(scores) == 0:
            return np.array([])

        minimum = scores.min()
        maximum = scores.max()

        if maximum == minimum:
            return np.ones_like(scores)

        normalized_scores = (
            (scores - minimum)
            / (maximum - minimum)
        )

        return normalized_scores