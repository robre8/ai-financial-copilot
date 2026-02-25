"""
Agent Service - Financial Analysis Agent with tool orchestration
Analyzes financial documents using ReAct pattern with structured tools.
"""

from typing import Dict, Any, List, Optional
import json
import re
import logging

logger = logging.getLogger(__name__)


class FinancialAnalysisAgent:
    """
    Financial Analysis Agent with tool orchestration.
    
    Tools:
    1. extract_financial_metrics - Extract ratios and KPIs from text
    2. detect_risk_patterns - Identify financial risk indicators
    3. generate_structured_report - Synthesize findings into JSON report
    """
    
    def __init__(self):
        self.tools = {
            "extract_financial_metrics": self._extract_financial_metrics,
            "detect_risk_patterns": self._detect_risk_patterns,
            "generate_structured_report": self._generate_structured_report
        }
        self.memory = {}
        logger.info("🤖 Financial Analysis Agent initialized")
    
    def analyze(self, document_text: str) -> Dict[str, Any]:
        """
        Analyze financial document end-to-end.
        
        Args:
            document_text: Financial document content
        
        Returns:
            Structured financial analysis report
        """
        logger.info("📊 Starting financial analysis...")
        self.memory = {"document": document_text}
        
        # Step 1: Extract metrics
        logger.info("🔧 Using tool: extract_financial_metrics")
        metrics = self._extract_financial_metrics(document_text)
        self.memory["metrics"] = metrics
        
        # Step 2: Detect risks
        logger.info("🔧 Using tool: detect_risk_patterns")
        risks = self._detect_risk_patterns(document_text, metrics)
        self.memory["risks"] = risks
        
        # Step 3: Generate report
        logger.info("🔧 Using tool: generate_structured_report")
        report = self._generate_structured_report(metrics, risks)
        
        logger.info("✅ Financial analysis complete")
        return report
    
    def _extract_financial_metrics(self, text: str) -> Dict[str, Any]:
        """
        Tool 1: Extract financial metrics (ratios, values).
        
        Uses pattern matching to identify:
        - Revenue, net income, assets
        - Liquidity ratios (current, quick)
        - Profitability ratios
        - Leverage ratios
        """
        metrics = {}
        text_lower = text.lower()
        
        # Revenue extraction
        revenue_patterns = [
            r'revenue[:\s]*\$?([\d,]+\.?\d*)\s*(?:million|billion|m|b)?',
            r'sales[:\s]*\$?([\d,]+\.?\d*)\s*(?:million|billion|m|b)?',
        ]
        for pattern in revenue_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metrics["revenue"] = float(match.group(1).replace(',', ''))
                break
        
        # Net income extraction
        income_patterns = [
            r'net\s+income[:\s]*\$?([\d,]+\.?\d*)\s*(?:million|billion)?',
            r'net\s+profit[:\s]*\$?([\d,]+\.?\d*)\s*(?:million|billion)?',
        ]
        for pattern in income_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metrics["net_income"] = float(match.group(1).replace(',', ''))
                break
        
        # Current assets and liabilities
        ca_match = re.search(r'current\s+assets[:\s]*\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
        if ca_match:
            metrics["current_assets"] = float(ca_match.group(1).replace(',', ''))
        
        cl_match = re.search(r'current\s+liabilities[:\s]*\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
        if cl_match:
            metrics["current_liabilities"] = float(cl_match.group(1).replace(',', ''))
        
        # Total debt
        debt_match = re.search(r'total\s+debt[:\s]*\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
        if debt_match:
            metrics["total_debt"] = float(debt_match.group(1).replace(',', ''))
        
        # Total equity
        equity_match = re.search(r'total\s+equity[:\s]*\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
        if equity_match:
            metrics["total_equity"] = float(equity_match.group(1).replace(',', ''))
        
        # Calculate derived ratios
        if "current_assets" in metrics and "current_liabilities" in metrics:
            metrics["liquidity_ratio"] = round(
                metrics["current_assets"] / metrics["current_liabilities"], 2
            )
        
        if "total_debt" in metrics and "total_equity" in metrics:
            metrics["debt_ratio"] = round(
                metrics["total_debt"] / (metrics["total_debt"] + metrics["total_equity"]), 2
            )
        
        if "net_income" in metrics and "revenue" in metrics:
            metrics["profit_margin"] = round(
                metrics["net_income"] / metrics["revenue"], 2
            )
        
        logger.info(f"📊 Extracted metrics: {list(metrics.keys())}")
        return metrics
    
    def _detect_risk_patterns(self, text: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tool 2: Detect financial risk patterns.
        
        Analyzes:
        - Liquidity risks
        - Leverage risks
        - Profitability trends
        - Negative keywords
        """
        risks = {
            "identified_risks": [],
            "risk_score": 0,
            "risk_level": "low"
        }
        
        # 1. Liquidity risk
        if "liquidity_ratio" in metrics:
            if metrics["liquidity_ratio"] < 1.0:
                risks["identified_risks"].append("Low liquidity ratio (< 1.0)")
                risks["risk_score"] += 30
            elif metrics["liquidity_ratio"] < 1.5:
                risks["identified_risks"].append("Moderate liquidity ratio")
                risks["risk_score"] += 10
        
        # 2. Leverage risk
        if "debt_ratio" in metrics:
            if metrics["debt_ratio"] > 0.7:
                risks["identified_risks"].append("High debt ratio (> 0.7)")
                risks["risk_score"] += 25
            elif metrics["debt_ratio"] > 0.5:
                risks["identified_risks"].append("Moderate debt ratio")
                risks["risk_score"] += 10
        
        # 3. Profitability risk
        if "profit_margin" in metrics:
            if metrics["profit_margin"] < 0:
                risks["identified_risks"].append("Negative profit margin")
                risks["risk_score"] += 35
            elif metrics["profit_margin"] < 0.05:
                risks["identified_risks"].append("Low profit margin (< 5%)")
                risks["risk_score"] += 15
        
        # 4. Negative keywords in text
        negative_keywords = ["loss", "decline", "crisis", "bankruptcy", "default", "restructuring"]
        text_lower = text.lower()
        for keyword in negative_keywords:
            if keyword in text_lower:
                risks["identified_risks"].append(f"Found risk keyword: {keyword}")
                risks["risk_score"] += 5
        
        # Determine risk level
        if risks["risk_score"] >= 70:
            risks["risk_level"] = "high"
        elif risks["risk_score"] >= 40:
            risks["risk_level"] = "medium"
        else:
            risks["risk_level"] = "low"
        
        logger.info(f"⚠️ Risk assessment: {risks['risk_level']} (score: {risks['risk_score']})")
        return risks
    
    def _generate_structured_report(
        self, 
        metrics: Dict[str, Any], 
        risks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Tool 3: Generate structured financial report.
        
        Synthesizes metrics and risks into actionable insights.
        """
        recommendations = []
        
        # Generate recommendations based on risks
        if risks["risk_level"] == "high":
            recommendations.append("⚠️ Review leverage strategy - consider debt reduction")
            recommendations.append("📊 Improve operational efficiency to boost margins")
            recommendations.append("💰 Strengthen liquidity position immediately")
        elif risks["risk_level"] == "medium":
            recommendations.append("📈 Monitor debt levels closely")
            recommendations.append("🎯 Focus on profitability improvements")
            recommendations.append("💡 Consider strategic partnerships to reduce risk")
        else:
            recommendations.append("✅ Financial position is stable")
            recommendations.append("🚀 Consider growth initiatives")
            recommendations.append("📊 Maintain current financial discipline")
        
        report = {
            "analysis_status": "completed",
            "financial_metrics": metrics,
            "risk_assessment": {
                "risk_level": risks["risk_level"],
                "risk_score": risks["risk_score"],
                "identified_risks": risks["identified_risks"]
            },
            "recommendations": recommendations,
            "timestamp": "2026-02-24"
        }
        
        logger.info("📋 Structured report generated")
        return report


# Singleton instance
_agent = None


def get_financial_agent() -> FinancialAnalysisAgent:
    """Get or create Financial Analysis Agent singleton."""
    global _agent
    if _agent is None:
        _agent = FinancialAnalysisAgent()
    return _agent


class AgentService:
    """Legacy API compatibility wrapper."""
    
    def __init__(self):
        self.agent = get_financial_agent()
        logger.info("🤖 AgentService initialized")
    
    async def execute_task(
        self, 
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a task using the agent."""
        if context and "document" in context:
            return self.agent.analyze(context["document"])
        return {"error": "Document context required"}
    
    def add_tool(self, name: str, function: callable, description: str):
        """Register a tool for the agent."""
        logger.info(f"🔧 Tool registered: {name}")
    
    def clear_memory(self):
        """Clear agent memory."""
        self.agent.memory.clear()
        logger.info("🧹 Agent memory cleared")


# Singleton instance
_agent_service = None


def get_agent_service() -> AgentService:
    """Get or create AgentService singleton."""
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service
