from FlagEmbedding import BGEM3FlagModel

MODEL_NAME = "BAAI/bge-m3"

def main():
    print("Loading embedding model...")
    model = BGEM3FlagModel(
        MODEL_NAME,
        use_fp16=False
    )
    print("Model loaded successfully.")

    test_text = [
        "How can I make better decisions in life?"
    ]

    print("Generating test embedding...")
    output = model.encode(
        test_text,
        batch_size=1,
        max_length=8192
    )

    embeddings = output["dense_vecs"]

    print("Embedding generated successfully.")
    print("Number of embeddings:", len(embeddings))
    print("Vector dimensions:", embeddings.shape[1])

if __name__ == "__main__":
    main()
