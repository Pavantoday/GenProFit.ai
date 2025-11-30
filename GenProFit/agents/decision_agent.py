# agents/decision_agent.py
from typing import Dict

class DecisionAgent:
    def __init__(self):
        pass

    def make_decision(self, ticker, financials_report: Dict, predict_probs: Dict, best_horizons: Dict,
                      risk_rating: str, fee_tax_report: Dict, sentiment_score: float, user_threshold=0.6):
        """
        Simple policy:
          - If probability for +10% within recommended horizon >= user_threshold and risk not High -> BUY
          - Else HOLD or AVOID
        """
        decision = "HOLD"
        reasons = []
        prob10 = predict_probs.get(10, {})
        # choose default horizon
        # if best_horizons has entry for 10 use it
        horizon, prob = best_horizons.get(10, (None, 0.0))
        if prob >= user_threshold and risk_rating != "High":
            decision = "BUY"
            reasons.append(f"P(+10%)={prob} at horizon {horizon} days (>= {user_threshold})")
        else:
            reasons.append(f"P(+10%)={prob} at horizon {horizon} days (< {user_threshold}) or risk={risk_rating}")
        # assemble report
        report = {
            "ticker": ticker,
            "decision": decision,
            "reasons": reasons,
            "financials": financials_report,
            "probabilities": predict_probs,
            "best_horizons": best_horizons,
            "risk": risk_rating,
            "fee_tax": fee_tax_report,
            "sentiment": sentiment_score
        }
        return report
