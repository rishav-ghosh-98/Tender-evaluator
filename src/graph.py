from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from .bid_processor import extract_bid_from_pdf
from .config import create_llm
from .application import evaluate_tender
from .models import Bid, BidEvaluationReport, TenderEvaluation, TenderRequirements
from .tender_processor import load_tender


class GraphState(TypedDict, total=False):
    tender_path: str
    bid_paths: list[str]
    llm: Any
    tender_requirements: TenderRequirements
    bids: list[Bid]
    bid_evaluations: list[BidEvaluationReport]
    evaluation: TenderEvaluation
    status: str
    error: str


def extract_tender_node(state: GraphState) -> dict[str, Any]:
    """Extract tender requirements using the existing tender processor."""
    if state.get("error"):
        return {}

    tender_path = state.get("tender_path")
    llm = state.get("llm")
    if tender_path is None or llm is None:
        return {
            "error": "Tender extraction failed: required input state is missing.",
            "status": "error"
        }

    try:
        tender_requirements, _ = load_tender(
            tender_path,
            llm
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
    llm = state.get("llm")
    if bid_paths is None or llm is None:
        return {
            "error": "Bid processing failed: required input state is missing.",
            "status": "error"
        }

    try:
        bids = [
            extract_bid_from_pdf(bid_path, llm)
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
    """Confirm that the evaluation contains the data needed for ranking."""
    if state.get("error"):
        return {}

    if not state.get("tender_requirements"):
        return {
            "error": "Evaluation validation failed: tender requirements are missing.",
            "status": "error"
        }

    if state.get("bid_evaluations") is None:
        return {
            "error": "Evaluation validation failed: bid evaluations are missing.",
            "status": "error"
        }

    return {"status": "evaluation_valid"}


def route_after_validation(state: GraphState) -> str:
    """Continue to ranking only when validation completed without an error."""
    return "error" if state.get("error") else "rank_bids"


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
        "error": "error"
    }
)
builder.add_edge("rank_bids", END)
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
        "llm": create_llm(),
        "status": "started"
    })

    if result.get("error"):
        raise RuntimeError(result["error"])

    evaluation = result.get("evaluation")
    if evaluation is None:
        raise RuntimeError("Tender evaluation graph completed without a result.")

    return evaluation
