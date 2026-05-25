from sklearn.metrics.pairwise import cosine_similarity

def find_similar(query_embedding, stored_embeddings, threshold=0.3):
    scores = []
    
    # Compare query with every document
    for item in stored_embeddings:
        # Calculate similarity score between 0 and 1
        score = cosine_similarity(
            [query_embedding],
            [item['embedding']]
        )[0][0]
        
        scores.append({
            'text': item['text'],
            'score': float(score)
        })
    
    # Sort by highest score first
    scores.sort(key=lambda x: x['score'], reverse=True)
    
    # Get top 3 most similar
    top3 = scores[:3]
    
    # Check if best score is above threshold
    if top3[0]['score'] < threshold:
        return None
    
    return top3