"""
TaxApex SDK Data Models
=======================

Pydantic models for API request/response handling.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class NoticeType(str, Enum):
    """Types of tax notices supported by TaxApex."""
    CP2000 = "CP2000"
    CP501 = "CP501"
    CP503 = "CP503"
    CP504 = "CP504"
    CP14 = "CP14"
    CP90 = "CP90"
    CP91 = "CP91"
    CP297 = "CP297"
    LT11 = "LT11"
    LT16 = "LT16"
    LT17 = "LT17"
    STATE_NOTICE = "STATE_NOTICE"
    OTHER = "OTHER"


class RiskLevel(str, Enum):
    """Audit risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class APIError(Exception):
    """Base exception for TaxApex API errors."""
    
    def __init__(self, message: str, status_code: int = None, response: Dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class AuthenticationError(APIError):
    """Raised when API authentication fails."""
    pass


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: int = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ValidationError(APIError):
    """Raised when request validation fails."""
    pass


@dataclass
class ExtractedField:
    """A single extracted field from a tax notice."""
    name: str
    value: Any
    confidence: float
    bounding_box: Optional[List[float]] = None


@dataclass
class ExtractionResult:
    """Result of document extraction."""
    id: str
    notice_type: NoticeType
    issuing_agency: str
    notice_date: Optional[datetime]
    due_date: Optional[datetime]
    amount_due: Optional[float]
    taxpayer_name: Optional[str]
    taxpayer_id: Optional[str]
    tax_year: Optional[int]
    fields: List[ExtractedField] = field(default_factory=list)
    raw_text: Optional[str] = None
    confidence_score: float = 0.0
    processing_time_ms: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ExtractionResult":
        """Create ExtractionResult from API response dictionary."""
        fields = [
            ExtractedField(**f) for f in data.get("fields", [])
        ]
        
        notice_date = None
        if data.get("notice_date"):
            notice_date = datetime.fromisoformat(data["notice_date"].replace("Z", "+00:00"))
        
        due_date = None
        if data.get("due_date"):
            due_date = datetime.fromisoformat(data["due_date"].replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", ""),
            notice_type=NoticeType(data.get("notice_type", "OTHER")),
            issuing_agency=data.get("issuing_agency", ""),
            notice_date=notice_date,
            due_date=due_date,
            amount_due=data.get("amount_due"),
            taxpayer_name=data.get("taxpayer_name"),
            taxpayer_id=data.get("taxpayer_id"),
            tax_year=data.get("tax_year"),
            fields=fields,
            raw_text=data.get("raw_text"),
            confidence_score=data.get("confidence_score", 0.0),
            processing_time_ms=data.get("processing_time_ms", 0),
        )


@dataclass
class RiskFactor:
    """A single audit risk factor."""
    category: str
    description: str
    severity: RiskLevel
    score: float
    recommendation: str


@dataclass
class AuditRiskAssessment:
    """Result of audit risk analysis."""
    id: str
    client_id: str
    tax_year: int
    overall_score: float
    risk_level: RiskLevel
    income_score: float
    deductions_score: float
    credits_score: float
    compliance_score: float
    risk_factors: List[RiskFactor] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    industry_comparison: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AuditRiskAssessment":
        """Create AuditRiskAssessment from API response dictionary."""
        risk_factors = [
            RiskFactor(
                category=rf.get("category", ""),
                description=rf.get("description", ""),
                severity=RiskLevel(rf.get("severity", "medium")),
                score=rf.get("score", 0.0),
                recommendation=rf.get("recommendation", ""),
            )
            for rf in data.get("risk_factors", [])
        ]
        
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        
        return cls(
            id=data.get("id", ""),
            client_id=data.get("client_id", ""),
            tax_year=data.get("tax_year", 0),
            overall_score=data.get("overall_score", 0.0),
            risk_level=RiskLevel(data.get("risk_level", "medium")),
            income_score=data.get("income_score", 0.0),
            deductions_score=data.get("deductions_score", 0.0),
            credits_score=data.get("credits_score", 0.0),
            compliance_score=data.get("compliance_score", 0.0),
            risk_factors=risk_factors,
            recommendations=data.get("recommendations", []),
            industry_comparison=data.get("industry_comparison"),
            created_at=created_at,
        )


@dataclass
class SearchResultItem:
    """A single search result item."""
    document_id: str
    title: str
    content_snippet: str
    similarity_score: float
    document_type: str
    tax_year: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SearchResult:
    """Result of semantic search."""
    query: str
    total_results: int
    results: List[SearchResultItem] = field(default_factory=list)
    processing_time_ms: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict) -> "SearchResult":
        """Create SearchResult from API response dictionary."""
        results = [
            SearchResultItem(
                document_id=r.get("document_id", ""),
                title=r.get("title", ""),
                content_snippet=r.get("content_snippet", ""),
                similarity_score=r.get("similarity_score", 0.0),
                document_type=r.get("document_type", ""),
                tax_year=r.get("tax_year"),
                metadata=r.get("metadata"),
            )
            for r in data.get("results", [])
        ]
        
        return cls(
            query=data.get("query", ""),
            total_results=data.get("total_results", 0),
            results=results,
            processing_time_ms=data.get("processing_time_ms", 0),
        )


@dataclass
class ResearchSource:
    """A source used in tax research."""
    title: str
    url: str
    source_type: str
    relevance_score: float
    snippet: str


@dataclass
class ResearchResult:
    """Result of tax research query."""
    query: str
    answer: str
    confidence: float
    sources: List[ResearchSource] = field(default_factory=list)
    related_topics: List[str] = field(default_factory=list)
    processing_time_ms: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ResearchResult":
        """Create ResearchResult from API response dictionary."""
        sources = [
            ResearchSource(
                title=s.get("title", ""),
                url=s.get("url", ""),
                source_type=s.get("source_type", ""),
                relevance_score=s.get("relevance_score", 0.0),
                snippet=s.get("snippet", ""),
            )
            for s in data.get("sources", [])
        ]
        
        return cls(
            query=data.get("query", ""),
            answer=data.get("answer", ""),
            confidence=data.get("confidence", 0.0),
            sources=sources,
            related_topics=data.get("related_topics", []),
            processing_time_ms=data.get("processing_time_ms", 0),
        )


@dataclass
class UsageStats:
    """API usage statistics."""
    period_start: datetime
    period_end: datetime
    document_extractions: int
    ai_analysis_calls: int
    search_queries: int
    audit_risk_assessments: int
    total_api_calls: int
    
    @classmethod
    def from_dict(cls, data: Dict) -> "UsageStats":
        """Create UsageStats from API response dictionary."""
        return cls(
            period_start=datetime.fromisoformat(data["period_start"].replace("Z", "+00:00")),
            period_end=datetime.fromisoformat(data["period_end"].replace("Z", "+00:00")),
            document_extractions=data.get("document_extractions", 0),
            ai_analysis_calls=data.get("ai_analysis_calls", 0),
            search_queries=data.get("search_queries", 0),
            audit_risk_assessments=data.get("audit_risk_assessments", 0),
            total_api_calls=data.get("total_api_calls", 0),
        )
