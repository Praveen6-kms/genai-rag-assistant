from flask import Flask, request, jsonify, send_from_directory
from embeddings import get_embedding
from retrieval import find_similar
from llm import get_answer
import json
import os

app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Load documents
with open('docs.json') as f:
    documents = json.load(f)

# Generate embeddings on startup
print("Loading documents and generating embeddings...")
stored_embeddings = []
for doc in documents:
    embedding = get_embedding(doc['content'])
    stored_embeddings.append({
        'text': doc['content'],
        'title': doc['title'],
        'embedding': embedding
    })
print(f"✅ {len(stored_embeddings)} documents loaded!")

# Store sessions
sessions = {}

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

@app.route('/')
def home():
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json

    # Validate request
    if not data:
        return jsonify({'error': 'Invalid JSON request'}), 400
    if 'message' not in data:
        return jsonify({'error': 'Message field is required'}), 400
    if 'sessionId' not in data:
        return jsonify({'error': 'SessionId field is required'}), 400

    message = data.get('message', '').strip()
    session_id = data.get('sessionId', 'default')

    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    # Initialize session if new
    if session_id not in sessions:
        sessions[session_id] = []

    # Get existing history
    history = sessions[session_id]
    history_text = '\n'.join([
        f"User: {h['user']}\nAssistant: {h['assistant']}"
        for h in history[-3:]
    ])

    # Check greetings
    greetings = ['hi', 'hii', 'hello', 'hey', 'good morning',
                 'good evening', 'good afternoon', 'howdy']

    if any(message.lower().strip() == g for g in greetings):
        reply = "Hello! I'm your AI assistant. How can I help you today? You can ask me about password reset, account settings, payment methods, and more!"
        sessions[session_id].append({
            'user': message,
            'assistant': reply
        })
        return jsonify({
            'reply': reply,
            'tokensUsed': len(reply.split()) * 2,
            'retrievedChunks': 0
        })

    # For follow-up questions combine with last message
    search_query = message
    if history and len(history) > 0:
        last_user_msg = history[-1]['user']
        last_bot_msg = history[-1]['assistant']
        search_query = f"{last_user_msg} {last_bot_msg} {message}"

    # Generate embedding for combined query
    query_embedding = get_embedding(search_query)
    results = find_similar(query_embedding, stored_embeddings)

    # If no results found with combined query try original
    if not results:
        query_embedding = get_embedding(message)
        results = find_similar(query_embedding, stored_embeddings)

    # Log similarity scores
    if results:
        print(f"Top similarity score: {results[0]['score']:.4f}")
        print(f"Retrieved {len(results)} chunks")

    if not results:
        reply = "I could not find enough information in the knowledge base to answer this question."
    else:
        context = '\n'.join([r['text'] for r in results])
        reply = get_answer(context, history_text, message)

    # Debug prints
    print(f"Session: {session_id}")
    print(f"Message: {message}")
    print(f"History: {history_text}")
    print(f"Results found: {len(results) if results else 0}")

    # Save to history
    sessions[session_id].append({
        'user': message,
        'assistant': reply
    })

    return jsonify({
        'reply': reply,
        'tokensUsed': len(reply.split()) * 2,
        'retrievedChunks': len(results) if results else 0
    })

if __name__ == '__main__':
    app.run(debug=True)