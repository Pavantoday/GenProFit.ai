# agents/fee_tax_agent.py
import json
import math

class FeeTaxAgent:
    """
    Loads platform fee profiles and computes net outcome after fees/taxes.
    """

    def __init__(self, profiles_path="tools/platform_profiles.json", tax_bracket_pct=0.30):
        with open(profiles_path, "r") as f:
            self.profiles = json.load(f)
        self.tax_bracket = tax_bracket_pct

    def compute_fees(self, platform_key, trade_type, price, quantity):
        """
        trade_type: 'delivery' or 'intraday'
        returns dict of fee components
        """
        if platform_key not in self.profiles:
            raise ValueError("Unknown platform")
        p = self.profiles[platform_key]
        notional = price * quantity
        brk_info = p["brokerage"]
        if trade_type == "delivery":
            brokerage = notional * brk_info.get("delivery_pct", 0.0)
        else:
            brokerage = max(notional * brk_info.get("intraday_pct", 0.0) / 100.0, brk_info.get("min_intraday", 0.0))
            # some profiles stored pct as fraction; handle both (prototype)
            if brokerage < 1 and brk_info.get("intraday_pct", 0.0) > 0:
                brokerage = notional * brk_info.get("intraday_pct", 0.0)
        stt = notional * p.get("stt_pct", 0.0)
        gst = brokerage * p.get("gst_pct", 0.0)
        sebi = notional * p.get("sebi_charges_pct", 0.0)
        stamp = notional * p.get("stamp_duty_pct", 0.0)
        total_fees = brokerage + stt + gst + sebi + stamp
        return {
            "notional": notional,
            "brokerage": brokerage,
            "stt": stt,
            "gst": gst,
            "sebi": sebi,
            "stamp": stamp,
            "total_fees": total_fees
        }

    def compute_net_after_profit(self, platform_key, trade_type, buy_price, sell_price, quantity, is_long_term=False):
        """
        Computes net profit after fees and estimated taxes.
        is_long_term flag toggles capital gains treatment for prototype.
        """
        buy_fees = self.compute_fees(platform_key, trade_type, buy_price, quantity)
        sell_fees = self.compute_fees(platform_key, trade_type, sell_price, quantity)
        gross_profit = (sell_price - buy_price) * quantity
        total_fees = buy_fees["total_fees"] + sell_fees["total_fees"]
        # simple capital gains tax handling
        if gross_profit <= 0:
            tax = 0.0
        else:
            if is_long_term:
                # reduced rate example
                tax = gross_profit * 0.10
            else:
                tax = gross_profit * self.tax_bracket
        net_profit = gross_profit - total_fees - tax
        net_return_pct = (net_profit / (buy_price * quantity)) if (buy_price*quantity) > 0 else 0.0
        return {
            "gross_profit": gross_profit,
            "total_fees": total_fees,
            "tax": tax,
            "net_profit": net_profit,
            "net_return_pct": net_return_pct,
            "breakdown": {"buy": buy_fees, "sell": sell_fees}
        }
