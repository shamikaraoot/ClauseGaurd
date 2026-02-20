import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
client = None
if openai_api_key:
    try:
        client = OpenAI(api_key=openai_api_key)
    except Exception as e:
        print(f"Warning: Could not initialize OpenAI client: {e}")


def get_chat_response(question: str, context: str) -> str:
    """
    Generate a response to a question about the Terms and Conditions.
    Uses OpenAI if available, otherwise returns a simple response.
    """
    if client:
        return get_openai_chat_response(question, context)
    else:
        return get_simple_chat_response(question, context)


def get_openai_chat_response(question: str, context: str) -> str:
    """Generate response using OpenAI API."""
    try:
        prompt = f"""You are a helpful assistant that answers questions about Terms and Conditions documents.

Context (summary of the analyzed Terms and Conditions):
{context}

User Question: {question}

Provide a clear, concise answer based on the context. If the question cannot be answered from the context, say so politely.
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions about legal documents. Be clear and concise."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"OpenAI chat failed: {e}, using fallback")
        return get_simple_chat_response(question, context)


def get_simple_chat_response(question: str, context: str) -> str:
    """Simple rule-based response when OpenAI is not available."""
    question_lower = question.lower()

    # Simple keyword matching
    if any(word in question_lower for word in ["cancel", "refund", "money back"]):
        return "Based on the analyzed document, please review the cancellation and refund policies carefully. Look for terms like 'no refund', 'cancellation fee', or 'refund policy' in the original document."

    elif any(word in question_lower for word in ["data", "privacy", "information", "personal"]):
        return "The document indicates data collection practices. Review the privacy policy section for details on what data is collected and how it's shared with third parties."

    elif any(word in question_lower for word in ["renew", "subscription", "automatic", "auto"]):
        return "The document contains automatic renewal clauses. Check for terms related to recurring charges and how to cancel subscriptions."

    elif any(word in question_lower for word in ["risk", "safe", "dangerous", "concern"]):
        return f"Based on the analysis, the document has been assessed with certain risk factors. Review the alerts and summary provided for specific concerns."

    else:
        return f"I can help answer questions about the Terms and Conditions. Based on the analysis: {context[:200]}... For specific details, please refer to the original document or ask about specific clauses like cancellation, data privacy, or payment terms."
