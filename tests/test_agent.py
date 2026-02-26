"""
Tests for Financial Analysis Agent and Agent-based endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.agent_service import FinancialAnalysisAgent, get_financial_agent

# Disable rate limiting for tests
try:
    if hasattr(app, 'state') and hasattr(app.state, 'limiter'):
        app.state.limiter.enabled = False
except Exception:
    pass


@pytest.fixture
def client():
    """Create test client for the app"""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Return Firebase Bearer token headers"""
    return {"Authorization": "Bearer mock-firebase-token"}


class TestFinancialAnalysisAgent:
    """Test Financial Analysis Agent core functionality"""

    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        agent = get_financial_agent()
        assert agent is not None
        assert "extract_financial_metrics" in agent.tools
        assert "detect_risk_patterns" in agent.tools
        assert "generate_structured_report" in agent.tools

    def test_extract_financial_metrics(self):
        """Test Tool 1: Extract financial metrics from document"""
        agent = get_financial_agent()
        
        # Sample financial document
        doc = """
        Q3 2025 Financial Report
        Revenue: $150 Million
        Net Income: $45 Million
        Current Assets: $120 Million
        Current Liabilities: $92 Million
        Total Debt: $200 Million
        Total Equity: $120 Million
        """
        
        metrics = agent._extract_financial_metrics(doc)
        
        # Verify metrics extraction
        assert "revenue" in metrics
        assert metrics["revenue"] == 150.0
        assert "net_income" in metrics
        assert metrics["net_income"] == 45.0
        assert "liquidity_ratio" in metrics
        assert 1.2 < metrics["liquidity_ratio"] < 1.35
        assert "debt_ratio" in metrics
        assert 0.6 < metrics["debt_ratio"] < 0.65

    def test_detect_risk_patterns(self):
        """Test Tool 2: Detect risk patterns"""
        agent = get_financial_agent()
        
        metrics = {
            "liquidity_ratio": 0.8,  # Low liquidity
            "debt_ratio": 0.75,      # High debt
            "profit_margin": -0.10   # Negative margin
        }
        
        doc = "Company facing bankruptcy crisis and restructuring"
        
        risks = agent._detect_risk_patterns(doc, metrics)
        
        # Verify risk detection
        assert risks["risk_level"] == "high"
        assert risks["risk_score"] > 60
        assert len(risks["identified_risks"]) > 0
        assert any("liquidity" in risk.lower() for risk in risks["identified_risks"])

    def test_detect_risk_low(self):
        """Test low-risk scenario"""
        agent = get_financial_agent()
        
        metrics = {
            "liquidity_ratio": 2.0,  # Strong liquidity
            "debt_ratio": 0.3,       # Low debt
            "profit_margin": 0.20    # Good margin
        }
        
        doc = "Strong financial position with steady growth"
        
        risks = agent._detect_risk_patterns(doc, metrics)
        
        assert risks["risk_level"] == "low"
        assert risks["risk_score"] < 30

    def test_generate_structured_report(self):
        """Test Tool 3: Generate structured report"""
        agent = get_financial_agent()
        
        metrics = {
            "revenue": 150.0,
            "net_income": 45.0,
            "liquidity_ratio": 1.3,
            "debt_ratio": 0.62
        }
        
        risks = {
            "risk_level": "medium",
            "risk_score": 45,
            "identified_risks": ["Moderate debt ratio"]
        }
        
        report = agent._generate_structured_report(metrics, risks)
        
        # Verify report structure
        assert report["analysis_status"] == "completed"
        assert "financial_metrics" in report
        assert "risk_assessment" in report
        assert "recommendations" in report
        assert len(report["recommendations"]) > 0
        assert "timestamp" in report

    def test_full_analysis_workflow(self):
        """Test complete analysis workflow"""
        agent = get_financial_agent()
        
        doc = """
        2025 Q3 Financial Performance
        
        Revenue: $150 Million
        Net Income: $45 Million
        Cost of Goods Sold: $45 Million
        
        Assets
        Current Assets: $100 Million
        Total Assets: $250 Million
        
        Liabilities
        Current Liabilities: $80 Million
        Total Debt: $150 Million
        
        Equity
        Total Equity: $100 Million
        
        The company has faced some operational challenges
        but maintains solid market position.
        """
        
        result = agent.analyze(doc)
        
        # Verify complete result
        assert result["analysis_status"] == "completed"
        assert "financial_metrics" in result
        assert "risk_assessment" in result
        assert "recommendations" in result
        assert result["risk_assessment"]["risk_level"] in ["low", "medium", "high"]
        assert len(result["recommendations"]) > 0


class TestAnalyzeEndpoint:
    """Test /analyze endpoint"""

    def test_analyze_endpoint_success(self, client, auth_headers):
        """Test successful financial analysis via endpoint"""
        doc = """
        Financial Report Q3 2025
        Revenue: $150 Million
        Net Income: $45 Million
        Current Assets: $100 Million
        Current Liabilities: $80 Million
        """
        
        response = client.post(
            "/analyze",
            json={"question": doc},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "analysis" in data
        assert "timestamp" in data
        assert data["analysis"]["analysis_status"] == "completed"

    def test_analyze_endpoint_no_auth(self, client):
        """Test endpoint requires authentication"""
        response = client.post(
            "/analyze",
            json={"question": "Test document"}
        )
        
        assert response.status_code == 401

    def test_analyze_endpoint_empty_document(self, client, auth_headers):
        """Test endpoint rejects empty documents"""
        response = client.post(
            "/analyze",
            json={"question": ""},
            headers=auth_headers
        )
        
        assert response.status_code == 400


class TestWebhookEndpoint:
    """Test /webhooks/analysis-complete endpoint"""

    def test_webhook_success(self, client, auth_headers):
        """Test webhook endpoint accepts events"""
        payload = {
            "event_id": "evt_123",
            "analysis_id": "analysis_456",
            "risk_level": "medium",
            "processing_time_ms": 2500
        }
        
        response = client.post(
            "/webhooks/analysis-complete",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["webhook_status"] == "acknowledged"
        assert data["event_id"] == "evt_123"
        assert "delivery_results" in data
        assert len(data["delivery_results"]) > 0

    def test_webhook_no_auth(self, client):
        """Test webhook requires authentication"""
        response = client.post(
            "/webhooks/analysis-complete",
            json={"event_id": "evt_123"}
        )
        
        assert response.status_code == 401

    def test_webhook_delivery_results(self, client, auth_headers):
        """Test webhook shows delivery status"""
        payload = {
            "event_id": "evt_789",
            "risk_level": "high"
        }
        
        response = client.post(
            "/webhooks/analysis-complete",
            json=payload,
            headers=auth_headers
        )
        
        data = response.json()
        
        # Verify delivery results
        assert "delivery_results" in data
        for result in data["delivery_results"]:
            assert "endpoint" in result
            assert "status" in result
            assert result["status"] in ["queued", "failed"]


class TestRootEndpointUpdate:
    """Test updated root endpoint with new features"""

    def test_root_endpoint_includes_analyze(self, client):
        """Test root endpoint lists /analyze endpoint"""
        response = client.get("/")
        data = response.json()
        
        assert "analyze_financial" in data["endpoints"]
        assert data["endpoints"]["analyze_financial"] == "POST /analyze"

    def test_root_endpoint_includes_webhook(self, client):
        """Test root endpoint lists webhook endpoint"""
        response = client.get("/")
        data = response.json()
        
        assert "webhook" in data["endpoints"]
        assert data["endpoints"]["webhook"] == "POST /webhooks/analysis-complete"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
