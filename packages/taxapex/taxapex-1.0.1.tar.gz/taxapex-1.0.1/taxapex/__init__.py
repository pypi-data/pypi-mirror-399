"""
TaxApex Python SDK
==================

A Python client library for the TaxApex Tax Notice Management API.

Example usage:
    from taxapex import TaxApexClient
    
    client = TaxApexClient(api_key="your-api-key")
    
    # Extract data from a tax notice
    result = client.extract.from_file("notice.pdf")
    print(result.notice_type, result.amount_due)
    
    # Analyze audit risk
    risk = client.audit_risk.analyze(client_id="12345", tax_year=2023)
    print(risk.overall_score, risk.recommendations)
"""

__version__ = "1.0.0"
__author__ = "Innorve"

from .client import TaxApexClient
from .models import (
    ExtractionResult,
    AuditRiskAssessment,
    SearchResult,
    ResearchResult,
    APIError,
    RateLimitError,
    AuthenticationError,
)

__all__ = [
    "TaxApexClient",
    "ExtractionResult",
    "AuditRiskAssessment",
    "SearchResult",
    "ResearchResult",
    "APIError",
    "RateLimitError",
    "AuthenticationError",
]
