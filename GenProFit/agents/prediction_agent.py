# agents/prediction_agent.py
import numpy as np
import pandas as pd

class PredictionAgent:
    """
    Uses Monte Carlo simulation on historical returns to estimate
    P(>= target%) within various time horizons.
    """

    def __init__(self, n_sims=5000, seed=0):
        self.n_sims = n_sims
        self.rng = np.random.default_rng(seed)

    def compute_log_returns(self, price_series):
        # price_series: pd.Series of closes
        return np.log(price_series).diff().dropna()

    def monte_carlo_probabilities(self, price_series, horizons_days=[3,7,14,30,90], targets_pct=[0.05, 0.10, 0.20]):
        """
        Returns dictionary mapping each target to horizon -> probability.
        price_series: pd.Series (close prices indexed by date)
        """
        logrets = self.compute_log_returns(price_series)
        mu = logrets.mean() * 252  # annualized
        sigma = logrets.std() * (252**0.5)  # annualized
        last_price = price_series.iloc[-1]
        results = {int(t*100): {} for t in targets_pct}

        # simulate for each horizon
        for horizon in horizons_days:
            T = horizon / 252.0
            # simulate terminal price using Geometric Brownian motion
            # vectorized simulation: n_sims
            drift = (mu - 0.5 * sigma**2) * T
            diffusion = sigma * np.sqrt(T) * self.rng.normal(size=self.n_sims)
            terminal = last_price * np.exp(drift + diffusion)
            returns = (terminal - last_price) / last_price
            for target in targets_pct:
                prob = float((returns >= target).sum() / self.n_sims)
                results[int(target*100)][horizon] = round(prob, 4)
        return results

    def best_horizon_for_target(self, probs_dict, target_pct, min_prob_threshold=0.6):
        """
        Choose smallest horizon where P(target) >= threshold.
        probs_dict: output of monte_carlo_probabilities
        """
        target_key = int(target_pct*100)
        horizon_probs = probs_dict.get(target_key, {})
        sorted_horizons = sorted(horizon_probs.keys())
        for h in sorted_horizons:
            if horizon_probs[h] >= min_prob_threshold:
                return h, horizon_probs[h]
        # if none meet threshold, return highest prob at longest horizon
        if sorted_horizons:
            last = sorted_horizons[-1]
            return last, horizon_probs[last]
        return None, 0.0
