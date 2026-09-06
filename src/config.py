from pathlib import Path
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

TENDER_PATH = Path("data/tender.pdf")
BIDS_DIRECTORY = Path("bids")
PINECONE_INDEX_NAME = "tender-rag"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL_NAME = "gpt-4.1-mini"


def create_llm() -> ChatOpenAI:
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is missing from .env")

    return ChatOpenAI(
        model=LLM_MODEL_NAME,
        temperature=0
    )


def get_pinecone_api_key() -> str:
    api_key = os.getenv("PINECONE_API_KEY")

    if not api_key:
        raise ValueError("PINECONE_API_KEY is missing from .env")

    return api_key
