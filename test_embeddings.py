from src.parser import extract_text
from src.resume_extractor import ResumeExtractor
from src.matching.embeddings import EmbeddingModel


resume_path = r"C:\Users\pranj\Downloads\resume.pdf"

print("Reading resume...\n")

resume_text = extract_text(resume_path)

print("Extracting resume information...\n")

extractor = ResumeExtractor()
resume_data = extractor.extract(resume_text)

print("Creating resume embedding...\n")

embedding_model = EmbeddingModel()

resume_embedding = embedding_model.encode_one(
    resume_text
)

print("===== EMBEDDING TEST =====")

print("\nResume:")
print(resume_path)

print("\nEmbedding shape:")
print(resume_embedding.shape)

print("\nFirst 10 embedding values:")
print(resume_embedding[:10])

print("\n===== TEST PASSED =====")