"""
TaxApex API Client
==================

Main client class for interacting with the TaxApex API.
"""

import os
import time
import base64
import hashlib
import hmac
from typing import Optional, Dict, Any, BinaryIO, Union
from urllib.parse import urljoin

import requests

from .models import (
    ExtractionResult,
    AuditRiskAssessment,
    SearchResult,
    ResearchResult,
    UsageStats,
    APIError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
)


class ExtractAPI:
    """Document extraction API endpoints."""
    
    def __init__(self, client: "TaxApexClient"):
        self._client = client
    
    def from_file(
        self,
        file_path: str,
        *,
        document_type: Optional[str] = None,
        extract_tables: bool = True,
        extract_signatures: bool = False,
    ) -> ExtractionResult:
        """
        Extract data from a tax notice file.
        
        Args:
            file_path: Path to the PDF or image file
            document_type: Optional hint for document type (e.g., "CP2000", "STATE_NOTICE")
            extract_tables: Whether to extract table data
            extract_signatures: Whether to detect signatures
        
        Returns:
            ExtractionResult with extracted data
        
        Example:
            result = client.extract.from_file("notice.pdf")
            print(f"Notice Type: {result.notice_type}")
            print(f"Amount Due: ${result.amount_due}")
        """
        with open(file_path, "rb") as f:
            return self.from_bytes(
                f.read(),
                filename=os.path.basename(file_path),
                document_type=document_type,
                extract_tables=extract_tables,
                extract_signatures=extract_signatures,
            )
    
    def from_bytes(
        self,
        data: bytes,
        filename: str,
        *,
        document_type: Optional[str] = None,
        extract_tables: bool = True,
        extract_signatures: bool = False,
    ) -> ExtractionResult:
        """
        Extract data from raw file bytes.
        
        Args:
            data: Raw file bytes
            filename: Original filename (used for type detection)
            document_type: Optional hint for document type
            extract_tables: Whether to extract table data
            extract_signatures: Whether to detect signatures
        
        Returns:
            ExtractionResult with extracted data
        """
        files = {"file": (filename, data)}
        params = {
            "extract_tables": extract_tables,
            "extract_signatures": extract_signatures,
        }
        if document_type:
            params["document_type"] = document_type
        
        response = self._client._request(
            "POST",
            "/extract",
            files=files,
            params=params,
        )
        return ExtractionResult.from_dict(response)
    
    def from_url(
        self,
        url: str,
        *,
        document_type: Optional[str] = None,
        extract_tables: bool = True,
        extract_signatures: bool = False,
    ) -> ExtractionResult:
        """
        Extract data from a document URL.
        
        Args:
            url: URL to the PDF or image file
            document_type: Optional hint for document type
            extract_tables: Whether to extract table data
            extract_signatures: Whether to detect signatures
        
        Returns:
            ExtractionResult with extracted data
        """
        response = self._client._request(
            "POST",
            "/extract",
            json={
                "url": url,
                "document_type": document_type,
                "extract_tables": extract_tables,
                "extract_signatures": extract_signatures,
            },
        )
        return ExtractionResult.from_dict(response)
    
    def get_status(self, extraction_id: str) -> Dict[str, Any]:
        """
        Get the status of an extraction job.
        
        Args:
            extraction_id: The extraction job ID
        
        Returns:
            Status dictionary with job details
        """
        return self._client._request("GET", f"/extract/{extraction_id}/status")
    
    def get_result(self, extraction_id: str) -> ExtractionResult:
        """
        Get the result of a completed extraction.
        
        Args:
            extraction_id: The extraction job ID
        
        Returns:
            ExtractionResult with extracted data
        """
        response = self._client._request("GET", f"/extract/{extraction_id}")
        return ExtractionResult.from_dict(response)


class AuditRiskAPI:
    """Audit risk analysis API endpoints."""
    
    def __init__(self, client: "TaxApexClient"):
        self._client = client
    
    def analyze(
        self,
        client_id: str,
        tax_year: int,
        *,
        income_data: Optional[Dict[str, Any]] = None,
        deduction_data: Optional[Dict[str, Any]] = None,
        credit_data: Optional[Dict[str, Any]] = None,
        filing_history: Optional[Dict[str, Any]] = None,
        industry: Optional[str] = None,
    ) -> AuditRiskAssessment:
        """
        Analyze audit risk for a client.
        
        Args:
            client_id: Unique identifier for the client
            tax_year: Tax year to analyze
            income_data: Optional income breakdown
            deduction_data: Optional deduction breakdown
            credit_data: Optional credit breakdown
            filing_history: Optional filing history data
            industry: Optional industry for comparison
        
        Returns:
            AuditRiskAssessment with risk analysis
        
        Example:
            risk = client.audit_risk.analyze(
                client_id="12345",
                tax_year=2023,
                income_data={"wages": 150000, "investments": 25000},
                industry="technology"
            )
            print(f"Risk Level: {risk.risk_level}")
            for rec in risk.recommendations:
                print(f"- {rec}")
        """
        response = self._client._request(
            "POST",
            "/audit-risk",
            json={
                "client_id": client_id,
                "tax_year": tax_year,
                "income_data": income_data,
                "deduction_data": deduction_data,
                "credit_data": credit_data,
                "filing_history": filing_history,
                "industry": industry,
            },
        )
        return AuditRiskAssessment.from_dict(response)
    
    def get_assessment(self, assessment_id: str) -> AuditRiskAssessment:
        """
        Get a previous audit risk assessment.
        
        Args:
            assessment_id: The assessment ID
        
        Returns:
            AuditRiskAssessment with risk analysis
        """
        response = self._client._request("GET", f"/audit-risk/{assessment_id}")
        return AuditRiskAssessment.from_dict(response)
    
    def list_assessments(
        self,
        client_id: Optional[str] = None,
        tax_year: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List audit risk assessments.
        
        Args:
            client_id: Filter by client ID
            tax_year: Filter by tax year
            limit: Maximum results to return
            offset: Pagination offset
        
        Returns:
            Dictionary with assessments list and pagination info
        """
        params = {"limit": limit, "offset": offset}
        if client_id:
            params["client_id"] = client_id
        if tax_year:
            params["tax_year"] = tax_year
        
        return self._client._request("GET", "/audit-risk", params=params)


class SearchAPI:
    """Semantic search API endpoints."""
    
    def __init__(self, client: "TaxApexClient"):
        self._client = client
    
    def query(
        self,
        query: str,
        *,
        document_type: Optional[str] = None,
        tax_year: Optional[int] = None,
        limit: int = 10,
        min_similarity: float = 0.5,
    ) -> SearchResult:
        """
        Perform semantic search across documents.
        
        Args:
            query: Natural language search query
            document_type: Filter by document type
            tax_year: Filter by tax year
            limit: Maximum results to return
            min_similarity: Minimum similarity score (0-1)
        
        Returns:
            SearchResult with matching documents
        
        Example:
            results = client.search.query(
                "IRS penalty abatement procedures",
                document_type="IRS_NOTICE",
                limit=5
            )
            for item in results.results:
                print(f"{item.title}: {item.similarity_score:.2f}")
        """
        response = self._client._request(
            "POST",
            "/search",
            json={
                "query": query,
                "document_type": document_type,
                "tax_year": tax_year,
                "limit": limit,
                "min_similarity": min_similarity,
            },
        )
        return SearchResult.from_dict(response)
    
    def index_document(
        self,
        document_id: str,
        content: str,
        *,
        title: Optional[str] = None,
        document_type: Optional[str] = None,
        tax_year: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Index a document for semantic search.
        
        Args:
            document_id: Unique document identifier
            content: Document text content
            title: Document title
            document_type: Type of document
            tax_year: Associated tax year
            metadata: Additional metadata
        
        Returns:
            Indexing result with document ID and status
        """
        return self._client._request(
            "POST",
            "/search/index",
            json={
                "document_id": document_id,
                "content": content,
                "title": title,
                "document_type": document_type,
                "tax_year": tax_year,
                "metadata": metadata,
            },
        )
    
    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Remove a document from the search index.
        
        Args:
            document_id: Document ID to remove
        
        Returns:
            Deletion result
        """
        return self._client._request("DELETE", f"/search/index/{document_id}")


class ResearchAPI:
    """Tax research API endpoints."""
    
    def __init__(self, client: "TaxApexClient"):
        self._client = client
    
    def query(
        self,
        question: str,
        *,
        sources: Optional[list] = None,
        include_citations: bool = True,
        max_sources: int = 5,
    ) -> ResearchResult:
        """
        Research a tax question using AI.
        
        Args:
            question: Natural language tax question
            sources: Specific sources to search (e.g., ["IRS", "STATE_CA"])
            include_citations: Whether to include source citations
            max_sources: Maximum sources to include
        
        Returns:
            ResearchResult with answer and sources
        
        Example:
            result = client.research.query(
                "What are the requirements for claiming the home office deduction?"
            )
            print(result.answer)
            for source in result.sources:
                print(f"- {source.title}: {source.url}")
        """
        response = self._client._request(
            "POST",
            "/research",
            json={
                "question": question,
                "sources": sources,
                "include_citations": include_citations,
                "max_sources": max_sources,
            },
        )
        return ResearchResult.from_dict(response)


class TaxApexClient:
    """
    TaxApex API Client.
    
    The main entry point for interacting with the TaxApex API.
    
    Example:
        from taxapex import TaxApexClient
        
        # Initialize with API key
        client = TaxApexClient(api_key="your-api-key")
        
        # Or use environment variable
        client = TaxApexClient()  # Uses TAXAPEX_API_KEY env var
        
        # Extract data from a notice
        result = client.extract.from_file("notice.pdf")
        
        # Analyze audit risk
        risk = client.audit_risk.analyze(client_id="123", tax_year=2023)
        
        # Search documents
        results = client.search.query("penalty abatement")
        
        # Research tax questions
        answer = client.research.query("What is Form 1099-K?")
    """
    
    DEFAULT_BASE_URL = "https://taxnotices-api.jollysea-2fe81643.centralus.azurecontainerapps.io/api/v1"
    DEFAULT_TIMEOUT = 60
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize the TaxApex client.
        
        Args:
            api_key: API key for authentication (or set TAXAPEX_API_KEY env var)
            base_url: API base URL (defaults to production)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
            retry_delay: Base delay between retries (exponential backoff)
        """
        self.api_key = api_key or os.environ.get("TAXAPEX_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Pass api_key parameter or set TAXAPEX_API_KEY environment variable."
            )
        
        self.base_url = base_url or os.environ.get("TAXAPEX_BASE_URL", self.DEFAULT_BASE_URL)
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "TaxApex-Python-SDK/1.0.0",
            "Accept": "application/json",
        })
        
        # Initialize API namespaces
        self.extract = ExtractAPI(self)
        self.audit_risk = AuditRiskAPI(self)
        self.search = SearchAPI(self)
        self.research = ResearchAPI(self)
    
    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
        files: Optional[Dict] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Make an API request with retry logic.
        
        Args:
            method: HTTP method
            path: API path
            params: Query parameters
            json: JSON body
            files: Files to upload
            **kwargs: Additional request arguments
        
        Returns:
            Response JSON data
        
        Raises:
            AuthenticationError: Invalid API key
            RateLimitError: Rate limit exceeded
            ValidationError: Invalid request
            APIError: Other API errors
        """
        url = urljoin(self.base_url, path.lstrip("/"))
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = self._session.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    files=files,
                    timeout=self.timeout,
                    **kwargs,
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    if attempt < self.max_retries - 1:
                        time.sleep(retry_after)
                        continue
                    raise RateLimitError(
                        "Rate limit exceeded",
                        status_code=429,
                        retry_after=retry_after,
                    )
                
                # Handle authentication errors
                if response.status_code == 401:
                    raise AuthenticationError(
                        "Invalid API key",
                        status_code=401,
                        response=response.json() if response.text else None,
                    )
                
                # Handle validation errors
                if response.status_code == 400:
                    error_data = response.json() if response.text else {}
                    raise ValidationError(
                        error_data.get("message", "Validation error"),
                        status_code=400,
                        response=error_data,
                    )
                
                # Handle server errors with retry
                if response.status_code >= 500:
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (2 ** attempt))
                        continue
                    raise APIError(
                        f"Server error: {response.status_code}",
                        status_code=response.status_code,
                    )
                
                # Handle other client errors
                if response.status_code >= 400:
                    error_data = response.json() if response.text else {}
                    raise APIError(
                        error_data.get("message", f"API error: {response.status_code}"),
                        status_code=response.status_code,
                        response=error_data,
                    )
                
                # Success
                return response.json() if response.text else {}
                
            except requests.exceptions.Timeout:
                last_error = APIError("Request timed out")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                    
            except requests.exceptions.ConnectionError:
                last_error = APIError("Connection error")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
        
        raise last_error or APIError("Request failed after retries")
    
    def get_usage(self) -> UsageStats:
        """
        Get current billing period usage statistics.
        
        Returns:
            UsageStats with usage data
        
        Example:
            usage = client.get_usage()
            print(f"Document extractions: {usage.document_extractions}")
            print(f"Total API calls: {usage.total_api_calls}")
        """
        response = self._request("GET", "/usage")
        return UsageStats.from_dict(response)
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status.
        
        Returns:
            Health status dictionary
        """
        return self._request("GET", "/health")
    
    def close(self):
        """Close the HTTP session."""
        self._session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
