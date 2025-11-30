# main.py
from agents.logging_agent import LoggingAgent
from agents.memory_agent import MemoryAgent
from agents.market_data_agent import MarketDataAgent
from agents.financials_agent import FinancialsAgent
from agents.news_sentiment_agent import NewsSentimentAgent
from agents.prediction_agent import PredictionAgent
from agents.risk_agent import risk_score_from_vol_sentiment
from agents.fee_tax_agent import FeeTaxAgent
from agents.decision_agent import DecisionAgent
import pandas as pd

def demo_pipeline(ticker="SYNTH", user_platform="zerodha"):
    logger = LoggingAgent()
    trace = logger.start_trace(f"analysis-{ticker}")

    mem = MemoryAgent()
    md = MarketDataAgent()
    fin = FinancialsAgent()
    news = NewsSentimentAgent()
    pred = PredictionAgent(n_sims=3000)
    fee_agent = FeeTaxAgent()
    decider = DecisionAgent()

    logger.log_event(trace, "generate_synthetic_prices")
    df = md.generate_synthetic(days=252*2, seed=42, start_price=100.0)  # 2 years
    prices = df["close"]

    logger.log_event(trace, "compute_financials")
    # demo financials (years -> revenue, eps)
    demo_fin = {2019: {"revenue": 1000, "eps": 5},
                2020: {"revenue": 1150, "eps": 6},
                2021: {"revenue": 1350, "eps": 7},
                2022: {"revenue": 1600, "eps": 8},
                2023: {"revenue": 1800, "eps": 9}}
    fin_report = fin.summarize_growth(demo_fin)

    logger.log_event(trace, "fetch_news_sentiment")
    headlines = news.fetch_news(ticker, limit=5)
    sentiment = news.sentiment_score(headlines)

    logger.log_event(trace, "prediction_monte_carlo")
    probs = pred.monte_carlo_probabilities(prices, horizons_days=[3,7,14,30,90], targets_pct=[0.05, 0.10, 0.20])
    # best horizons for each target
    best_horizons = {}
    for t in [0.05, 0.10, 0.20]:
        h, p = pred.best_horizon_for_target(probs, t, min_prob_threshold=0.6)
        best_horizons[int(t*100)] = (h, p)

    logger.log_event(trace, "compute_volatility")
    logrets = pred.compute_log_returns(prices)
    vol_annualized = float(logrets.std() * (252**0.5))

    logger.log_event(trace, "risk_assessment")
    risk_str, risk_num = risk_score_from_vol_sentiment(vol_annualized, sentiment)

    logger.log_event(trace, "fee_tax_calc")
    buy_price = float(prices.iloc[-1])
    # assume target sell price = buy * 1.10 for 10% scenario for demonstration
    sell_price = buy_price * 1.10
    quantity = 10
    fee_report = fee_agent.compute_net_after_profit(user_platform, "delivery", buy_price, sell_price, quantity, is_long_term=False)

    logger.log_event(trace, "decision")
    decision_report = decider.make_decision(
        ticker=ticker,
        financials_report=fin_report,
        predict_probs=probs,
        best_horizons=best_horizons,
        risk_rating=risk_str,
        fee_tax_report=fee_report,
        sentiment_score=sentiment,
        user_threshold=0.6
    )

    # save session
    session_id = f"{ticker}-session"
    mem.save_session(session_id, decision_report)

    trace_log = logger.end_trace(trace)
    print("=== Decision Report ===")
    import json
    print(json.dumps(decision_report, indent=2, default=str))
    print("\n=== Trace ===")
    print(logger.export())

if __name__ == "__main__":
    demo_pipeline("TCS", user_platform="zerodha")
