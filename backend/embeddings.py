from sentence_transformers import SentenceTransformer

# Load the embedding model
# all-MiniLM-L6-v2 is a free, lightweight model that works offline
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    # Convert text meaning into numbers (vector)
    embedding = model.encode(text)
    return embedding.tolist()