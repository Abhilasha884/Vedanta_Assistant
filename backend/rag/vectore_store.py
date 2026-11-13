
import json
import uuid
from pathlib import Path
from FlagEmbedding import BGEM3FlagModel
from qdrant_client import QdrantClient, models

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "prepared_passages.json"
VECTOR_DB_PATH = BASE_DIR / "vector_store" / "qdrant_bge_m3"

# Model and Qdrant settings
MODEL_NAME = "BAAI/bge-m3"
COLLECTION_NAME = "vedanta_passages"
VECTOR_SIZE = 1024


def load_passages():
    """Load prepared passages from the JSON file."""
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    print("Loading passages...")
    passages = load_passages()
    print(f"Loaded {len(passages)} passages.")

    print("\nLoading BGE-M3 embedding model...")
    model = BGEM3FlagModel(
        MODEL_NAME,
        use_fp16=False
    )
    print("Model loaded successfully.")

    texts = [
        passage.get("embedding_text", "").strip()
        for passage in passages
    ]

    if any(not text for text in texts):
        raise ValueError("Some passages have empty embedding_text fields.")

    print("\nGenerating embeddings...")
    output = model.encode(
        texts,
        batch_size=4,
        max_length=8192,
        return_dense=True,
        return_sparse=False,
        return_colbert_vecs=False
    )

    embeddings = output["dense_vecs"]

    if embeddings.shape[1] != VECTOR_SIZE:
        raise ValueError(
            f"Embedding dimension mismatch: expected {VECTOR_SIZE}, "
            f"got {embeddings.shape[1]}"
        )

    print("Embeddings generated successfully.")
    print("Vector dimensions:", embeddings.shape[1])

    VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)

    print("\nConnecting to Qdrant vector database...")
    client = QdrantClient(path=str(VECTOR_DB_PATH))

    try:
        # Remove the old 384-dimensional collection
        if client.collection_exists(COLLECTION_NAME):
            print("\nDeleting old Qdrant collection...")
            client.delete_collection(COLLECTION_NAME)
            print("Old collection deleted successfully.")

        # Create a new 1024-dimensional collection
        print(f"\nCreating collection '{COLLECTION_NAME}'...")

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE
            )
        )

        print("New collection created successfully.")

        points = []

        for passage, embedding in zip(passages, embeddings):
            passage_id = passage["passage_id"]

            point_id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f"vedanta:{passage_id}"
                )
            )

            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=embedding.tolist(),
                    payload=passage
                )
            )

        print("\nUploading passages to Qdrant...")

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
            wait=True
        )

        info = client.get_collection(COLLECTION_NAME)

        print("\nUpload completed successfully!")
        print("Collection:", COLLECTION_NAME)
        print("Stored points:", info.points_count)
        print("Vector dimensions:", VECTOR_SIZE)

    finally:
        client.close()
        print("\nQdrant client connection closed.")


if __name__ == "__main__":
    main()
