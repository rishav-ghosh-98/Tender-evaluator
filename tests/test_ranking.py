from src.models import BidEvaluationReport, ComplianceCheck
from src.ranking import rank_bids


def evaluation(vendor_name, price, compliant):
    return BidEvaluationReport(
        vendor_name=vendor_name,
        price=price,
        checks=[
            ComplianceCheck(
                requirement="Quantity",
                required_value="251.75 - 278.25",
                offered_value="265",
                compliant=compliant,
                reason="" if compliant else "Quantity failure",
            )
        ],
        overall_compliant=compliant,
        reasons=[] if compliant else ["Compliance failure"],
    )


def test_rank_bids_excludes_non_compliant_bids():
    bids = [
        evaluation("Bharat Electricals Ltd", 1180000, True),
        evaluation("ABC Engineering Pvt Ltd", 1250000, True),
        evaluation("National Switchgear Corp", 1100000, False),
        evaluation("Delta Industrial Systems", 1050000, False),
    ]

    ranked_bids = rank_bids(bids)

    assert [bid.vendor_name for bid in ranked_bids] == [
        "Bharat Electricals Ltd",
        "ABC Engineering Pvt Ltd",
    ]


def test_rank_bids_orders_by_lowest_price():
    bids = [
        evaluation("Higher", 200, True),
        evaluation("Lowest", 100, True),
        evaluation("Middle", 150, True),
    ]

    ranked_bids = rank_bids(bids)

    assert [bid.vendor_name for bid in ranked_bids] == [
        "Lowest",
        "Middle",
        "Higher",
    ]


def test_rank_bids_lowest_compliant_price_is_first():
    ranked_bids = rank_bids([
        evaluation("Bharat Electricals Ltd", 1180000, True),
        evaluation("ABC Engineering Pvt Ltd", 1250000, True),
    ])

    assert ranked_bids[0].vendor_name == "Bharat Electricals Ltd"


def test_rank_bids_higher_compliant_price_is_second():
    ranked_bids = rank_bids([
        evaluation("Bharat Electricals Ltd", 1180000, True),
        evaluation("ABC Engineering Pvt Ltd", 1250000, True),
    ])

    assert ranked_bids[1].vendor_name == "ABC Engineering Pvt Ltd"


def test_rank_bids_empty_list_returns_empty_list():
    assert rank_bids([]) == []


def test_rank_bids_all_non_compliant_returns_empty_list():
    assert rank_bids([
        evaluation("Delta Industrial Systems", 1050000, False),
        evaluation("National Switchgear Corp", 1100000, False),
    ]) == []
