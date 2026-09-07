from .evaluator import evaluate_bids
from .models import Bid, TenderEvaluation, TenderRequirements
from .ranking import rank_bids


def evaluate_tender(
    tender: TenderRequirements,
    bids: list[Bid]
) -> TenderEvaluation:
    evaluations = evaluate_bids(tender, bids)
    ranked_bids = rank_bids(evaluations)

    recommended_bid = ranked_bids[0] if ranked_bids else None

    return TenderEvaluation(
        tender=tender,
        bid_evaluations=evaluations,
        ranked_bids=ranked_bids,
        recommended_bid=recommended_bid,
    )
