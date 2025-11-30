# agents/risk_agent.py

def risk_score_from_vol_sentiment(volatility_annualized, sentiment_score):
    """
    Simple heuristic:
      - volatility_annualized: e.g., std(log returns) * sqrt(252)
      - sentiment_score: in [-1,1] (prototype uses [-0.4,0.6])
    Returns risk_str, risk_numeric (0 low - 1 high)
    """
    # normalize volatility into [0,1] using a soft cap (example)
    v = min(volatility_annualized / 1.0, 1.0)  # assuming 100% annual vol => 1.0
    # sentiment reduces risk when positive
    s = max(min(sentiment_score, 1.0), -1.0)
    risk = 0.6 * v + 0.4 * (1 - (s + 1) / 2)  # combine
    # clamp
    risk = max(0.0, min(1.0, risk))
    if risk < 0.33:
        return "Low", risk
    elif risk < 0.66:
        return "Medium", risk
    else:
        return "High", risk
