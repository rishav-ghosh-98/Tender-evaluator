# Tender RAG

Tender RAG extracts procurement requirements from a tender PDF, answers tender questions with retrieval-augmented generation, extracts vendor bids from PDFs, evaluates compliance with deterministic Python rules, and ranks compliant bids by price.

## Structure

- `src/config.py`: Environment variables, paths, and model configuration.
- `src/models.py`: Pydantic data models.
- `src/tender_processor.py`: Tender loading, chunking, embeddings, Pinecone indexing, and requirement extraction.
- `src/rag.py`: Retrieval, question answering, and source display.
- `src/bid_processor.py`: Vendor bid PDF extraction.
- `src/evaluator.py`: Deterministic compliance checks.
- `src/ranking.py`: Compliant bid ranking by price.
- `src/main.py`: Application orchestration and display.

## Run

Install dependencies:

```powershell
pip install -r requirements.txt
```

Set `OPENAI_API_KEY` and `PINECONE_API_KEY` in `.env`, keep the tender at `data/tender.pdf`, and place vendor PDFs in `bids/`.

```powershell
python src/main.py
```
