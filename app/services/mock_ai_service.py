class MockAIService:
    def ask(self, question: str) -> str:
        return f"""
        [MOCK RESPONSE]

        Financial analysis for:
        "{question}"

        - Liquidity Ratio: Measures short-term financial stability.
        - Capital Adequacy Ratio: Measures bank solvency.
        - Risk Assessment: Moderate risk profile detected.

        This is a simulated AI response for development purposes.
        """
