from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate

from .models import Bid


BID_PROMPT = ChatPromptTemplate.from_template("""
You are an AI assistant analyzing a vendor bid submitted
against a government tender.

Extract the vendor's bid information according to the
provided Bid schema.

Rules:
1. Use ONLY information present in the bid document.
2. Do not invent or assume values.
3. Preserve the vendor name exactly.
4. Extract quantity as an integer.
5. Extract warranty as the number of months.
6. Extract the delivery completion date exactly as stated.
7. Extract the total bid price as a number without currency symbols.
8. Extract the technical specification exactly as stated.

Bid Document:
{context}
""")


def extract_bid_from_pdf(pdf_path: str, llm) -> Bid:
    documents = PyPDFLoader(pdf_path).load()
    bid_context = "\n\n".join(
        document.page_content
        for document in documents
    )

    formatted_prompt = BID_PROMPT.invoke({
        "context": bid_context
    })

    structured_bid_llm = llm.with_structured_output(Bid)

    return Bid.model_validate(
        structured_bid_llm.invoke(formatted_prompt)
    )


def load_bids(bids_directory: Path, llm) -> list[Bid]:
    bids = []

    print("\n--- EXTRACTING VENDOR BIDS ---")

    for bid_file in sorted(bids_directory.glob("*.pdf")):
        print(f"\nProcessing: {bid_file.name}")

        bid = extract_bid_from_pdf(str(bid_file), llm)
        bids.append(bid)

        print(f"Vendor: {bid.vendor_name}")
        print(f"Quantity: {bid.quantity}")
        print(f"Specification: {bid.technical_specification}")
        print(f"Warranty: {bid.warranty_months} months")
        print(f"Delivery: {bid.delivery_completion_date}")
        print(f"Price: ₹{bid.price:,.2f}")

    return bids
