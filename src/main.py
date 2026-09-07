from src.bid_processor import load_bids
from src.config import BIDS_DIRECTORY, TENDER_PATH, create_llm
from src.application import evaluate_tender
from src.rag import answer_question
from src.tender_processor import load_tender


def display_evaluations(evaluations):
    print("\n--- BID EVALUATION ---")

    for result in evaluations:
        print(f"\nVendor: {result.vendor_name}")
        print(f"Price: ₹{result.price:,.2f}")

        for check in result.checks:
            print(
                f"{check.requirement}: "
                f"{check.offered_value} "
                f"(Required: {check.required_value}) "
                f"→ "
                f"{'PASS' if check.compliant else 'FAIL'}"
            )

        print(
            "Overall Compliance: "
            f"{'COMPLIANT' if result.overall_compliant else 'NON-COMPLIANT'}"
        )

        if result.reasons:
            print("Reasons:")
            for reason in result.reasons:
                print(f" - {reason}")


def display_ranking(ranked_bids):
    print("\n--- BID RANKING ---")

    for index, result in enumerate(ranked_bids, start=1):
        print(
            f"L{index}: "
            f"{result.vendor_name} - "
            f"₹{result.price:,.2f}"
        )


def display_recommendation(recommended_bid):
    print("\n--- RECOMMENDATION ---")

    if recommended_bid is None:
        print("No compliant bids were found.")
        return

    print(f"Recommended L1 bidder: {recommended_bid.vendor_name}")
    print(f"Bid Price: ₹{recommended_bid.price:,.2f}")
    print("\nThis is a system recommendation only.")
    print(
        "Final tender award must be decided "
        "by the authorized procurement official."
    )


def main():
    llm = create_llm()

    tender, retriever = load_tender(
        str(TENDER_PATH),
        llm
    )

    answer_question(
        "What is the warranty period?",
        retriever,
        llm
    )

    bids = load_bids(BIDS_DIRECTORY, llm)
    result = evaluate_tender(tender, bids)

    display_evaluations(result.bid_evaluations)
    display_ranking(result.ranked_bids)
    display_recommendation(result.recommended_bid)


if __name__ == "__main__":
    main()
