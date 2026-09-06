from pydantic import BaseModel, Field


class TenderRequirements(BaseModel):
    tender_number: str = Field(description="Tender number")
    item_description: str = Field(description="Description of the tender item")
    quantity: str = Field(description="Required quantity")
    quantity_tolerance: str = Field(description="Allowed quantity tolerance")
    technical_specification: str = Field(description="Technical specification")
    drawing_number: str = Field(description="Drawing number")
    warranty_period: str = Field(description="Warranty period")
    delivery_completion_date: str = Field(description="Final delivery/completion date")
    delivery_schedule: str = Field(description="Detailed delivery schedule")
    inspection_requirements: str = Field(description="Inspection requirements")
    evaluation_criteria: str = Field(description="Bid evaluation criteria")


class Bid(BaseModel):
    vendor_name: str = Field(description="Name of the bidding vendor")
    quantity: int = Field(description="Quantity offered by the vendor")
    technical_specification: str = Field(description="Technical specification offered by the vendor")
    warranty_months: int = Field(description="Warranty offered by the vendor in months")
    delivery_completion_date: str = Field(description="Vendor's committed delivery completion date")
    price: float = Field(description="Total bid price")


class ComplianceCheck(BaseModel):
    requirement: str
    required_value: str
    offered_value: str
    compliant: bool
    reason: str


class BidEvaluationReport(BaseModel):
    vendor_name: str
    price: float
    checks: list[ComplianceCheck]
    overall_compliant: bool
    reasons: list[str]
