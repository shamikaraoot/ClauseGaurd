from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv

from analyzer import analyze_text
from scraper import scrape_terms_and_conditions
from chatbot import get_chat_response

load_dotenv()

app = FastAPI(title="ClauseGuard API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None


class AnalyzeResponse(BaseModel):
    summary: str
    risk_score: str  # "Low" | "Medium" | "High"
    alerts: List[str]


class ChatRequest(BaseModel):
    question: str
    context: str


class ChatResponse(BaseModel):
    answer: str


@app.get("/")
def root():
    return {"message": "ClauseGuard API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Analyze Terms and Conditions text or URL.
    Returns summary, risk score, and alerts.
    """
    try:
        # Validate input
        if not request.text and not request.url:
            raise HTTPException(
                status_code=400,
                detail="Either 'text' or 'url' must be provided"
            )

        # Get text from URL or use provided text
        text_to_analyze = ""
        if request.url:
            # scrape_terms_and_conditions raises HTTPException directly with proper error messages
            text_to_analyze = scrape_terms_and_conditions(request.url)
        else:
            text_to_analyze = request.text

        if not text_to_analyze or len(text_to_analyze.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Text is too short or empty"
            )

        # Analyze the text
        result = analyze_text(text_to_analyze)

        return AnalyzeResponse(
            summary=result["summary"],
            risk_score=result["risk_score"],
            alerts=result["alerts"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Answer questions about the analyzed Terms and Conditions.
    """
    try:
        if not request.question or not request.question.strip():
            raise HTTPException(
                status_code=400,
                detail="Question is required"
            )

        if not request.context or not request.context.strip():
            raise HTTPException(
                status_code=400,
                detail="Context is required"
            )

        answer = get_chat_response(request.question, request.context)

        return ChatResponse(answer=answer)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
