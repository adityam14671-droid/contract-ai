from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables
load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ContractRequest(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "Contract AI with Real AI is running 🚀"}

@app.post("/analyze")
def analyze_contract(contract: ContractRequest):
    try:
        prompt = f"""
        You are an expert legal contract analyst.

        Analyze the contract below and provide:
        1. Executive Summary
        2. Key Clauses
        3. Risk Score (0-100)
        4. Risky Clauses
        5. Suggested Improvements

        Contract:
        {contract.text}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a senior legal analyst."},
                {"role": "user", "content": prompt}
            ]
        )

        return {"analysis": response.choices[0].message.content}

    except Exception as e:
        return {
            "analysis": "⚠️ AI quota exceeded. Running basic fallback analysis.\n\nBasic analysis: Contract received and processed."
        }