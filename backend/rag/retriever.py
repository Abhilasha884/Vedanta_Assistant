
from pathlib import Path
from FlagEmbedding import BGEM3FlagModel
from qdrant_client import QdrantClient


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_DB_PATH = BASE_DIR / "vector_store" / "qdrant_bge_m3"

MODEL_NAME = "BAAI/bge-m3"
COLLECTION_NAME = "vedanta_passages"

TOP_K = 3

# Initial threshold; we will calibrate this through testing.
SIMILARITY_THRESHOLD = 0.20


# --------------------------------------------------
# Retriever
# --------------------------------------------------

class VedantaRetriever:

    def __init__(self):

        print("Loading embedding model...")

        self.model = BGEM3FlagModel(
            MODEL_NAME,
            use_fp16=False
        )

        print("Connecting to Qdrant...")

        self.client = QdrantClient(
            path=str(VECTOR_DB_PATH)
        )

        if not self.client.collection_exists(COLLECTION_NAME):

            self.client.close()

            raise ValueError(
                f"Collection '{COLLECTION_NAME}' does not exist. "
                "Please run vectore_store.py first."
            )

        print("Retriever initialized successfully!")

    def retrieve(self, question: str, top_k: int = TOP_K):

        question = question.strip()

        if not question:
            raise ValueError("Question cannot be empty.")

        # Convert the user's question into an embedding.
        output = self.model.encode(
                [question],
                batch_size=1,
                max_length=8192,
                return_dense=True,
                return_sparse=False,
                return_colbert_vecs=False
                
                )

        query_vector = output["dense_vecs"][0].tolist()

        # Search for the closest passages in Qdrant.
        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
            with_payload=True
        ).points

        # Filter out passages below the relevance threshold.
        results = [
            result for result in results
            if result.score >= SIMILARITY_THRESHOLD
        ]

        retrieved_passages = []

        for result in results:

            payload = result.payload or {}

            retrieved_passages.append({

                "passage_id": payload.get("passage_id"),

                "topic": payload.get("topic"),

                "source_summary": payload.get("source_summary"),

                "core_teaching": payload.get("core_teaching"),

                "english_explanation": payload.get("english_explanation"),

                "hindi_explanation": payload.get("hindi_explanation"),

                "original_work": payload.get("original_work"),

                "author_commentator": payload.get("author_commentator"),

                "translator": payload.get("translator"),

                "source_reference": payload.get("source_reference"),

                "start_book_page": payload.get("start_book_page"),

                "end_book_page": payload.get("end_book_page"),

                "pdf_page": payload.get("pdf_page"),

                "score": result.score

            })

        return retrieved_passages

    def close(self):

        self.client.close()


# --------------------------------------------------
# Test the retriever independently
# --------------------------------------------------

def main():

    retriever = VedantaRetriever()

    try:

        question = input("\nAsk a Vedanta-related question: ")

        results = retriever.retrieve(question)

        print("\nRetrieved passages:")
        print("-" * 60)

        if not results:

            print("No relevant passages found.")
            print(
                "The question may be outside the available "
                "Vedanta knowledge base."
            )

            return

        for index, passage in enumerate(results, start=1):

            print(f"\nResult {index}")

            print(f"Passage ID: {passage['passage_id']}")

            print(f"Topic: {passage['topic']}")

            print(f"Source: {passage['original_work']}")

            print(f"Reference: {passage['source_reference']}")

            print(f"Author: {passage['author_commentator']}")

            print(
                f"Similarity score: {passage['score']:.4f}"
            )

            print(
                f"Core teaching: {passage['core_teaching']}"
            )

            print(
                f"Summary: {passage['source_summary']}"
            )

    finally:

        retriever.close()


if __name__ == "__main__":

    main()
