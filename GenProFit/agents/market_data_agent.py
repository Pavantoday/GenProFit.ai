# agents/market_data_agent.py
import pandas as pd
import numpy as np

class MarketDataAgent:
    """
    Responsible for fetching or loading historical price data.
    For this prototype there are two modes:
      - load from CSV (if path provided)
      - generate synthetic series (demo mode)
    """

    def load_from_csv(self, path, price_col="close", date_col="date"):
        df = pd.read_csv(path, parse_dates=[date_col])
        df = df.sort_values(date_col)
        return df[[date_col, price_col]].rename(columns={date_col: "date", price_col: "close"})

    def generate_synthetic(self, days=365, seed=0, start_price=100.0, mu=0.0002, sigma=0.02):
        """Generate synthetic daily close prices using geometric Brownian motion."""
        rng = np.random.default_rng(seed)
        dt = 1/252
        prices = [start_price]
        for _ in range(days-1):
            shock = rng.normal(loc=mu*dt, scale=sigma*(dt**0.5))
            next_price = prices[-1] * (1 + shock)
            prices.append(max(0.01, next_price))
        import pandas as pd
        dates = pd.date_range(end=pd.Timestamp.today(), periods=days)
        return pd.DataFrame({"date": dates, "close": prices})
