from functools import lru_cache
import math
from numbers import Real
from typing import Any, TypedDict

print("[startup] before importing langgraph", flush=True)
from langgraph.graph import END, START, StateGraph
print("[startup] after importing langgraph", flush=True)

print("[startup] before importing bid_processor", flush=True)
from .bid_processor import extract_bid_from_pdf
print("[startup] after importing bid_processor", flush=True)

print("[startup] before importing config", flush=True)
from .config import create_llm
print("[startup] after importing config", flush=True)

print("[startup] before importing application", flush=True)
from .application import evaluate_tender
print("[startup] after importing application", flush=True)

print("[startup] before importing models", flush=True)
from .models import Bid, BidEvaluationReport, TenderEvaluation, TenderRequirements
print("[startup] after importing models", flush=True)

print("[startup] before importing tender_processor", flush=True)
from .tender_processor import load_tender
print("[startup] after importing tender_processor", flush=True)


class GraphState(TypedDict, total=False):
    tender_path: str
    bid_paths: list[str]
    tender_requirements: TenderRequirements
    bids: list[Bid]
    bid_evaluations: list[BidEvaluationReport]
    evaluation: TenderEvaluation
    status: str
    error: str
    review_required: bool
    review_reason: str


@lru_cache(maxsize=1)
def _get_workflow_llm():
    """Reuse one LLM instance without putting it in the graph state."""
    return create_llm()


def extract_tender_node(state: GraphState) -> dict[str, Any]:
    """Extract tender requirements using the existing tender processor."""
    if state.get("error"):
        return {}

    tender_path = state.get("tender_path")
    if tender_path is None:
        return {
            "error": "Tender extraction failed: tender path is missing.",
            "status": "error"
        }

    try:
        tender_requirements, _ = load_tender(
            tender_path,
            _get_workflow_llm()
        )
        return {
            "tender_requirements": tender_requirements,
            "status": "tender_extracted"
        }
    except Exception as error:
        return {
            "error": f"Tender extraction failed: {error}",
            "status": "error"
        }


def process_bids_node(state: GraphState) -> dict[str, Any]:
    """Extract each vendor bid using the existing bid processor."""
    if state.get("error"):
        return {}

    bid_paths = state.get("bid_paths")
    if bid_paths is None:
        return {
            "error": "Bid processing failed: bid paths are missing.",
            "status": "error"
        }

    try:
        bids = [
            extract_bid_from_pdf(bid_path, _get_workflow_llm())
            for bid_path in bid_paths
        ]
        return {
            "bids": bids,
            "status": "bids_processed"
        }
    except Exception as error:
        return {
            "error": f"Bid processing failed: {error}",
            "status": "error"
        }


def evaluate_bids_node(state: GraphState) -> dict[str, Any]:
    """Delegate evaluation and result construction to the application layer."""
    if state.get("error"):
        return {}

    tender_requirements = state.get("tender_requirements")
    bids = state.get("bids")
    if tender_requirements is None or bids is None:
        return {
            "error": "Bid evaluation failed: required input state is missing.",
            "status": "error"
        }

    try:
        evaluation = evaluate_tender(
            tender_requirements,
            bids
        )
        return {
            "bid_evaluations": evaluation.bid_evaluations,
            "evaluation": evaluation,
            "status": "bids_evaluated"
        }
    except Exception as error:
        return {
            "error": f"Bid evaluation failed: {error}",
            "status": "error"
        }


def validate_evaluation_node(state: GraphState) -> dict[str, Any]:
    """Validate evaluation structure and decide whether ranking is safe."""
    if state.get("error"):
        return {}

    if not state.get("tender_requirements"):
        return {
            "review_required": True,
            "review_reason": "Tender requirements are missing.",
            "status": "needs_review"
        }

    bids = state.get("bids")
    if not bids:
        return {
            "review_required": True,
            "review_reason": "No vendor bids were extracted.",
            "status": "needs_review"
        }

    bid_evaluations = state.get("bid_evaluations")
    if not bid_evaluations:
        return {
            "review_required": True,
            "review_reason": "No bid evaluations are available.",
            "status": "needs_review"
        }

    for evaluation in bid_evaluations:
        if not evaluation.checks:
            return {
                "review_required": True,
                "review_reason": (
                    f"Bid evaluation for {evaluation.vendor_name} "
                    "contains no compliance checks."
                ),
                "status": "needs_review"
            }

        if (
            isinstance(evaluation.price, bool)
            or not isinstance(evaluation.price, Real)
            or not math.isfinite(float(evaluation.price))
        ):
            return {
                "review_required": True,
                "review_reason": (
                    f"Bid evaluation for {evaluation.vendor_name} "
                    "does not contain a valid numeric price."
                ),
                "status": "needs_review"
            }

    if not any(
        evaluation.overall_compliant
        for evaluation in bid_evaluations
    ):
        return {
            "review_required": True,
            "review_reason": "No compliant bids are available for ranking.",
            "status": "needs_review"
        }

    return {
        "review_required": False,
        "review_reason": "",
        "status": "evaluation_valid"
    }


def route_after_validation(state: GraphState) -> str:
    """Route valid evaluations to ranking and unsafe ones to review."""
    if state.get("error"):
        return "error"
    if state.get("review_required"):
        return "human_review"
    return "rank_bids"


def route_after_tender(state: GraphState) -> str:
    """Continue only when tender extraction succeeded."""
    return "error" if state.get("error") else "process_bids"


def route_after_bids(state: GraphState) -> str:
    """Continue only when all bid PDFs were processed successfully."""
    return "error" if state.get("error") else "evaluate_bids"


def route_after_evaluation(state: GraphState) -> str:
    """Continue only when evaluation completed without an error."""
    return "error" if state.get("error") else "validate_evaluation"


def rank_bids_node(state: GraphState) -> dict[str, Any]:
    """Finalize the application result after the graph's ranking stage."""
    if state.get("error"):
        return {}

    if state.get("evaluation") is None:
        return {
            "error": "Ranking failed: application evaluation is missing.",
            "status": "error"
        }

    return {"status": "completed"}


def human_review_node(state: GraphState) -> dict[str, Any]:
    """End safely with a review message; interactive review comes later."""
    return {
        "status": "needs_human_review",
        "review_required": True,
        "review_reason": state.get(
            "review_reason",
            "The evaluation requires human review."
        )
    }


def error_node(state: GraphState) -> dict[str, Any]:
    """Terminate the workflow after recording a useful error status."""
    return {
        "status": "error"
    }


builder = StateGraph(GraphState)
builder.add_node("extract_tender", extract_tender_node)
builder.add_node("process_bids", process_bids_node)
builder.add_node("evaluate_bids", evaluate_bids_node)
builder.add_node("validate_evaluation", validate_evaluation_node)
builder.add_node("rank_bids", rank_bids_node)
builder.add_node("human_review", human_review_node)
builder.add_node("error", error_node)

builder.add_edge(START, "extract_tender")
builder.add_conditional_edges(
    "extract_tender",
    route_after_tender,
    {
        "process_bids": "process_bids",
        "error": "error"
    }
)
builder.add_conditional_edges(
    "process_bids",
    route_after_bids,
    {
        "evaluate_bids": "evaluate_bids",
        "error": "error"
    }
)
builder.add_conditional_edges(
    "evaluate_bids",
    route_after_evaluation,
    {
        "validate_evaluation": "validate_evaluation",
        "error": "error"
    }
)
builder.add_conditional_edges(
    "validate_evaluation",
    route_after_validation,
    {
        "rank_bids": "rank_bids",
        "human_review": "human_review",
        "error": "error"
    }
)
builder.add_edge("rank_bids", END)
builder.add_edge("human_review", END)
builder.add_edge("error", END)

graph = builder.compile()


def run_tender_evaluation(
    tender_path: str,
    bid_paths: list[str]
) -> TenderEvaluation:
    """Run the compiled graph and return its final TenderEvaluation."""
    result = graph.invoke({
        "tender_path": tender_path,
        "bid_paths": bid_paths,
        "status": "started"
    })

    if result.get("error"):
        raise RuntimeError(result["error"])

    if result.get("review_required"):
        raise RuntimeError(
            result.get(
                "review_reason",
                "Tender evaluation requires human review."
            )
        )

    evaluation = result.get("evaluation")
    if evaluation is None:
        raise RuntimeError("Tender evaluation graph completed without a result.")

    return evaluation
