from datetime import datetime
import re

from models import Bid, BidEvaluationReport, ComplianceCheck, TenderRequirements


def evaluate_bid(
    bid: Bid,
    tender: TenderRequirements
) -> BidEvaluationReport:
    reasons = []

    tender_quantity = float(tender.quantity.split()[0])
    tolerance_percentage = float(
        tender.quantity_tolerance
        .replace("%age", "")
        .replace("%", "")
        .strip()
    )

    minimum_quantity = tender_quantity * (1 - tolerance_percentage / 100)
    maximum_quantity = tender_quantity * (1 + tolerance_percentage / 100)
    quantity_compliant = minimum_quantity <= bid.quantity <= maximum_quantity
    quantity_reason = (
        f"Quantity offered: {bid.quantity}. "
        f"Allowed quantity range: {minimum_quantity:.2f} - {maximum_quantity:.2f}."
    )

    if not quantity_compliant:
        reasons.append(quantity_reason)

    required_spec = tender.technical_specification.upper()
    offered_spec = bid.technical_specification.upper()

    spec_matches = re.findall(
        r"[A-Z]+/[A-Z0-9]+(?:/[A-Z0-9]+)+",
        required_spec
    )

    alt_matches = re.findall(
        r"ALT-[A-Z0-9]+",
        required_spec
    )

    required_identifiers = spec_matches[:1] + alt_matches

    technical_compliant = all(
        identifier in offered_spec
        for identifier in required_identifiers
    )
    technical_reason = (
        "Technical specification does not match "
        "the required tender specification."
    )

    if not technical_compliant:
        reasons.append(technical_reason)

    warranty_numbers = [
        int(word)
        for word in tender.warranty_period.split()
        if word.isdigit()
    ]
    warranty_required = warranty_numbers[0] if warranty_numbers else 0
    warranty_compliant = bid.warranty_months >= warranty_required
    warranty_reason = (
        f"Warranty offered: {bid.warranty_months} months. "
        f"Required: {warranty_required} months."
    )

    if not warranty_compliant:
        reasons.append(warranty_reason)

    required_delivery_text = (
        tender.delivery_completion_date
        .replace("On or before", "")
        .strip()
    )
    required_delivery_date = datetime.strptime(
        required_delivery_text,
        "%d-%b-%y"
    )
    offered_delivery_date = datetime.strptime(
        bid.delivery_completion_date.strip(),
        "%d-%b-%y"
    )
    delivery_compliant = offered_delivery_date <= required_delivery_date
    delivery_reason = (
        f"Delivery offered: {bid.delivery_completion_date}. "
        f"Required completion: {tender.delivery_completion_date}."
    )

    if not delivery_compliant:
        reasons.append(delivery_reason)

    checks = [
        ComplianceCheck(
            requirement="Quantity",
            required_value=f"{minimum_quantity:.2f} - {maximum_quantity:.2f}",
            offered_value=str(bid.quantity),
            compliant=quantity_compliant,
            reason="" if quantity_compliant else quantity_reason
        ),
        ComplianceCheck(
            requirement="Technical Specification",
            required_value=tender.technical_specification,
            offered_value=bid.technical_specification,
            compliant=technical_compliant,
            reason="" if technical_compliant else technical_reason
        ),
        ComplianceCheck(
            requirement="Warranty",
            required_value=f"{warranty_required} months",
            offered_value=f"{bid.warranty_months} months",
            compliant=warranty_compliant,
            reason="" if warranty_compliant else warranty_reason
        ),
        ComplianceCheck(
            requirement="Delivery",
            required_value=tender.delivery_completion_date,
            offered_value=bid.delivery_completion_date,
            compliant=delivery_compliant,
            reason="" if delivery_compliant else delivery_reason
        )
    ]

    return BidEvaluationReport(
        vendor_name=bid.vendor_name,
        price=bid.price,
        checks=checks,
        overall_compliant=all(check.compliant for check in checks),
        reasons=reasons
    )


def evaluate_bids(
    tender: TenderRequirements,
    bids: list[Bid]
) -> list[BidEvaluationReport]:
    return [evaluate_bid(bid, tender) for bid in bids]
