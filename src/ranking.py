from models import BidEvaluationReport


def rank_bids(
    evaluations: list[BidEvaluationReport]
) -> list[BidEvaluationReport]:
    return sorted(
        (
            evaluation
            for evaluation in evaluations
            if evaluation.overall_compliant
        ),
        key=lambda evaluation: evaluation.price
    )
