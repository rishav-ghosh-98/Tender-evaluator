import os
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .application import evaluate_tender
from .bid_processor import extract_bid_from_pdf
from .config import create_llm
from .models import TenderEvaluation
from .tender_processor import load_tender


app = FastAPI(
    title="Tender Bid Evaluation API",
    description="API for evaluating vendor bids against tender requirements",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.post("/evaluate", response_model=TenderEvaluation)
async def evaluate(
    tender: UploadFile = File(...),
    bid1: UploadFile | None = File(None),
    bid2: UploadFile | None = File(None),
    bid3: UploadFile | None = File(None),
    bid4: UploadFile | None = File(None),
):
    """
    Upload one tender PDF and up to four vendor bid PDFs.
    """

    # -------------------------
    # Validate tender
    # -------------------------

    if tender.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Tender file must be a PDF."
        )

    # -------------------------
    # Collect uploaded bids
    # -------------------------

    bids = [
        bid
        for bid in [bid1, bid2, bid3, bid4]
        if bid is not None
    ]

    # -------------------------
    # Validate bids
    # -------------------------

    for bid in bids:
        if bid.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail=f"Bid file '{bid.filename}' must be a PDF."
            )

    temporary_paths = []

    try:
        tender_file = tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False
        )
        try:
            tender_file.write(await tender.read())
        finally:
            tender_file.close()
        temporary_paths.append(tender_file.name)

        bid_paths = []
        for bid in bids:
            bid_file = tempfile.NamedTemporaryFile(
                suffix=".pdf",
                delete=False
            )
            try:
                bid_file.write(await bid.read())
            finally:
                bid_file.close()
            bid_paths.append(bid_file.name)
            temporary_paths.append(bid_file.name)

        llm = create_llm()
        tender_requirements, _ = load_tender(
            tender_file.name,
            llm
        )
        extracted_bids = [
            extract_bid_from_pdf(bid_path, llm)
            for bid_path in bid_paths
        ]

        return evaluate_tender(
            tender_requirements,
            extracted_bids
        )
    finally:
        for temporary_path in temporary_paths:
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass