import pytest

from src import graph as workflow
from src.evaluator import evaluate_bids
from src.models import Bid, ComplianceCheck, TenderRequirements


@pytest.fixture
def tender():
    return TenderRequirements(
        tender_number="21261162",
        item_description="Rotary switch",
        quantity="265.00 Numbers",
        quantity_tolerance="5 %age",
        technical_specification="CLW SPEC. NO. CLW/ES/3/0108, ALT-A",
        drawing_number="CLW/ES/3/SK-1/0108/A",
        warranty_period="30 Months after the date of delivery",
        delivery_completion_date="On or before 31-MAY-27",
        delivery_schedule="April-2027 to May-2027",
        inspection_requirements="Inspection required",
        evaluation_criteria="Lowest to Highest",
    )


@pytest.fixture
def compliant_bid():
    return Bid(
        vendor_name="Bharat Electricals Ltd",
        quantity=265,
        technical_specification="CLW/ES/3/0108, ALT-A",
        warranty_months=30,
        delivery_completion_date="31-MAY-27",
        price=1180000,
    )


def state_for(tender, bids):
    return {
        "tender_requirements": tender,
        "bids": bids,
        "bid_evaluations": evaluate_bids(tender, bids),
    }


def test_validation_passes_with_compliant_bid(tender, compliant_bid):
    result = workflow.validate_evaluation_node(
        state_for(tender, [compliant_bid])
    )

    assert result["status"] == "evaluation_valid"
    assert result["review_required"] is False


def test_validation_routes_to_human_review_when_no_compliant_bids(
    tender,
    compliant_bid,
):
    non_compliant_bid = compliant_bid.model_copy(
        update={"quantity": 250}
    )

    result = workflow.validate_evaluation_node(
        state_for(tender, [non_compliant_bid])
    )

    assert result["status"] == "needs_review"
    assert result["review_required"] is True
    assert "No compliant bids" in result["review_reason"]


def test_non_compliant_vendor_does_not_trigger_review_if_other_bid_is_compliant(
    tender,
    compliant_bid,
):
    non_compliant_bid = compliant_bid.model_copy(
        update={
            "vendor_name": "Delta Industrial Systems",
            "technical_specification": "Different specification",
        }
    )

    result = workflow.validate_evaluation_node(
        state_for(tender, [compliant_bid, non_compliant_bid])
    )

    assert result["status"] == "evaluation_valid"
    assert result["review_required"] is False


def test_route_after_validation_returns_expected_routes():
    assert workflow.route_after_validation({}) == "rank_bids"
    assert workflow.route_after_validation({"review_required": True}) == "human_review"
    assert workflow.route_after_validation({"error": "failure"}) == "error"


def test_normal_graph_workflow_preserves_ranking(
    monkeypatch,
    tender,
    compliant_bid,
):
    abc_bid = compliant_bid.model_copy(
        update={
            "vendor_name": "ABC Engineering Pvt Ltd",
            "price": 1250000,
            "warranty_months": 36,
            "delivery_completion_date": "15-MAY-27",
        }
    )
    delta_bid = compliant_bid.model_copy(
        update={
            "vendor_name": "Delta Industrial Systems",
            "price": 1050000,
            "technical_specification": "Different specification",
        }
    )
    national_bid = compliant_bid.model_copy(
        update={
            "vendor_name": "National Switchgear Corp",
            "price": 1100000,
            "quantity": 250,
        }
    )
    bids_by_path = {
        "abc.pdf": abc_bid,
        "bharat.pdf": compliant_bid,
        "delta.pdf": delta_bid,
        "national.pdf": national_bid,
    }

    monkeypatch.setattr(workflow, "_get_workflow_llm", lambda: object())
    monkeypatch.setattr(
        workflow,
        "load_tender",
        lambda path, llm: (tender, None),
    )
    monkeypatch.setattr(
        workflow,
        "extract_bid_from_pdf",
        lambda path, llm: bids_by_path[path],
    )

    result = workflow.run_tender_evaluation(
        "tender.pdf",
        ["abc.pdf", "bharat.pdf", "delta.pdf", "national.pdf"],
    )

    assert [bid.vendor_name for bid in result.ranked_bids] == [
        "Bharat Electricals Ltd",
        "ABC Engineering Pvt Ltd",
    ]
    assert result.recommended_bid.vendor_name == "Bharat Electricals Ltd"
