import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Temperature between 0 and 0.3 for consistent answers
generation_config = {
    "temperature": 0.2,
}

model = genai.GenerativeModel(
    'gemini-2.5-flash',
    generation_config=generation_config
)

def get_answer(context, history, question):

    history_part = ""
    if history and history.strip():
        history_part = f"Previous Conversation:\n{history}\n"

    prompt = f"""You are a helpful customer support assistant.
You have access to a knowledge base (context) and previous conversation history.

IMPORTANT RULES:
1. Use the context to answer questions
2. If a follow-up question refers to something from conversation history, use history to understand it
3. If user asks "where is that", "what did you mean", "tell me more" — refer to conversation history
4. Only say "I could not find enough information" if NEITHER context NOR history can answer

Context:
{context}

{history_part}
Current Question: {question}

Answer:"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_msg = str(e)

        if "429" in error_msg:
            return "Rate limit exceeded — please try again later"
        elif "401" in error_msg:
            return "Invalid API key — please check your API key"
        elif "timeout" in error_msg.lower():
            return "Request timeout — please try again"
        else:
            return f"Error: {error_msg}"