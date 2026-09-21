from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def encode(self, texts):
        return self.model.encode(
            texts,
            normalize_embeddings=True
        )

    def encode_one(self, text):
        return self.model.encode(
            text,
            normalize_embeddings=True
        )