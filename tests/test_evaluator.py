import pytest

from src.evaluator import evaluate_bid
from src.models import Bid, TenderRequirements


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


def test_compliant_bid_passes(tender, compliant_bid):
    result = evaluate_bid(compliant_bid, tender)

    assert result.overall_compliant is True


def test_technical_specification_failure(tender, compliant_bid):
    bid = compliant_bid.model_copy(
        update={
            "vendor_name": "Delta Industrial Systems",
            "technical_specification": "Different specification",
        }
    )

    result = evaluate_bid(bid, tender)

    assert result.overall_compliant is False
    assert next(
        check for check in result.checks
        if check.requirement == "Technical Specification"
    ).compliant is False


def test_quantity_failure(tender, compliant_bid):
    bid = compliant_bid.model_copy(
        update={
            "vendor_name": "National Switchgear Corp",
            "quantity": 250,
        }
    )

    result = evaluate_bid(bid, tender)

    assert result.overall_compliant is False
    assert next(
        check for check in result.checks
        if check.requirement == "Quantity"
    ).compliant is False


def test_warranty_failure(tender, compliant_bid):
    bid = compliant_bid.model_copy(update={"warranty_months": 29})

    result = evaluate_bid(bid, tender)

    assert result.overall_compliant is False
    assert next(
        check for check in result.checks
        if check.requirement == "Warranty"
    ).compliant is False


def test_delivery_failure(tender, compliant_bid):
    bid = compliant_bid.model_copy(
        update={"delivery_completion_date": "01-JUN-27"}
    )

    result = evaluate_bid(bid, tender)

    assert result.overall_compliant is False
    assert next(
        check for check in result.checks
        if check.requirement == "Delivery"
    ).compliant is False


def test_quantity_tolerance_is_respected(tender, compliant_bid):
    bid = compliant_bid.model_copy(update={"quantity": 252})

    result = evaluate_bid(bid, tender)

    assert result.overall_compliant is True
    quantity_check = next(
        check for check in result.checks
        if check.requirement == "Quantity"
    )
    assert quantity_check.compliant is True
    assert quantity_check.required_value == "251.75 - 278.25"
