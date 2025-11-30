# agents/financials_agent.py
import numpy as np

class FinancialsAgent:
    """
    Compute YoY and CAGR-like metrics from provided financials dictionary.
    For this prototype we accept a small dict of yearly revenue/EPS numbers.
    """

    def compute_cagr(self, start_value, end_value, years):
        if start_value <= 0 or end_value <= 0 or years <= 0:
            return None
        return (end_value / start_value) ** (1.0/years) - 1.0

    def summarize_growth(self, yearly_financials):
        """
        yearly_financials: dict year -> {"revenue": float, "eps": float}
        returns growth report
        """
        years = sorted(yearly_financials.keys())
        if len(years) < 2:
            return {"note": "insufficient data"}
        start_year, end_year = years[0], years[-1]
        years_count = end_year - start_year
        rev_start = yearly_financials[start_year]["revenue"]
        rev_end = yearly_financials[end_year]["revenue"]
        eps_start = yearly_financials[start_year]["eps"]
        eps_end = yearly_financials[end_year]["eps"]
        cagr_rev = self.compute_cagr(rev_start, rev_end, years_count) if rev_start>0 else None
        cagr_eps = self.compute_cagr(eps_start, eps_end, years_count) if eps_start>0 else None
        return {
            "years": years_count,
            "cagr_revenue": cagr_rev,
            "cagr_eps": cagr_eps,
            "rev_start": rev_start,
            "rev_end": rev_end,
            "eps_start": eps_start,
            "eps_end": eps_end
        }
