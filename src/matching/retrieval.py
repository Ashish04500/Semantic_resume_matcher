import numpy as np
import faiss


class ResumeRetriever:
    def __init__(self, embeddings):
        """
        embeddings shape:
        (number_of_resumes, 384)
        """

        self.embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        dimension = self.embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(self.embeddings)

    def search(self, query_embedding, top_k=None):
        """
        Search for the most semantically similar resumes.

        query_embedding:
        shape (384,)
        """

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        ).reshape(1, -1)

        if top_k is None:
            top_k = len(self.embeddings)

        top_k = min(top_k, len(self.embeddings))

        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        return scores[0], indices[0]