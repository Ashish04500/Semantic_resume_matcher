from src.resume_processor import ResumeProcessor
from src.matching.embeddings import EmbeddingModel
from src.matching.retrieval import ResumeRetriever


resume_paths = [
    r"C:\Users\pranj\Downloads\resume.pdf",
]


print("Processing resumes...\n")

processor = ResumeProcessor()

processed_resumes = processor.process_files(resume_paths)

successful_resumes = [
    resume
    for resume in processed_resumes
    if "error" not in resume
]

if not successful_resumes:
    raise ValueError("No resumes were processed successfully.")


print(f"Successfully processed: {len(successful_resumes)} resume(s)\n")


embedding_model = EmbeddingModel()

resume_texts = [
    resume["raw_text"]
    for resume in successful_resumes
]

print("Creating resume embeddings...\n")

resume_embeddings = embedding_model.encode(resume_texts)

print("Resume embedding shape:")
print(resume_embeddings.shape)


print("\nBuilding FAISS retrieval index...\n")

retriever = ResumeRetriever(resume_embeddings)


query_embedding = embedding_model.encode_one(
    successful_resumes[0]["raw_text"]
)

scores, indices = retriever.search(
    query_embedding,
    top_k=1
)


print("===== RETRIEVAL RESULTS =====")

for rank, (score, index) in enumerate(
    zip(scores, indices),
    start=1
):
    resume = successful_resumes[index]

    print(f"\nRank: {rank}")
    print(f"Resume: {resume['filename']}")
    print(f"Similarity: {score:.4f}")


print("\n===== RETRIEVAL TEST PASSED =====")