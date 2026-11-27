from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(title="Sentiment Analysis API")


class PredictRequest(BaseModel):
    text: str = Field(min_length=1, description="Input text for sentiment analysis")


class PredictResponse(BaseModel):
    label: Literal["positive", "negative", "neutral"] = Field(
        description="Predicted sentiment label"
    )
    score: float = Field(
        ge=0,
        le=1,
        description="Confidence score of the prediction",
    )


def mock_sentiment_analysis(text: str) -> PredictResponse:
    if any(word in text.lower() for word in ["good", "great", "excellent"]):
        return PredictResponse(label="positive", score=0.95)
    if any(word in text.lower() for word in ["bad", "terrible", "awful"]):
        return PredictResponse(label="negative", score=0.9)
    return PredictResponse(label="neutral", score=0.5)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    return mock_sentiment_analysis(request.text)
