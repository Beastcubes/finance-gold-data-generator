from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List
import yaml
import random
import pandas as pd

random.seed(42)

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
OUTPUT_DIR = ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# LOCKED GOLD SCHEMA (29 columns)
# ============================================================

GOLD_SCHEMA_COLUMNS = [
    "fiscal_year",
    "fiscal_period",
    "fiscal_period_name",
    "cost_center_id",
    "cost_center_name",
    "department_name",
    "gl_account_id",
    "gl_account_name",
    "pnl_category",
    "actual_amount",
    "budget_amount",
    "variance_amount",
    "variance_pct",
    "variance_direction",
    "is_material",
    "variance_driver",
    "variance_driver_detail",
    "driver_confidence",
    "prior_period_variance_amount",
    "variance_change_vs_prior",
    "variance_trend_direction",
    "rolling_3_period_variance",
    "period_close_status",
    "has_late_posting",
    "late_posting_amount",
    "late_posting_period_count",
    "data_maturity_level",
    "explanation_readiness",
    "finance_signoff_flag",
]


# ============================================================
# STRUCTURE
# ============================================================

@dataclass(frozen=True)
class FiscalPeriod:
    fiscal_year: int
    fiscal_period: int
    fiscal_period_name: str
    period_close_status: str


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing config file: {path}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def validate_structure_cfg(cfg: Dict[str, Any]) -> None:
    if "calendar" not in cfg:
        raise ValueError("finance_structure.yaml must contain 'calendar'")
    if "dimensions" not in cfg:
        raise ValueError("finance_structure.yaml must contain 'dimensions'")


def build_fiscal_calendar(cfg: Dict[str, Any]) -> List[FiscalPeriod]:
    cal = cfg["calendar"]

    start_year = int(cal["start_fiscal_year"])
    start_period = int(cal["start_fiscal_period"])
    num_periods = int(cal["num_periods"])

    label_prefix = str(cal.get("fiscal_year_label_prefix", "FY"))
    label_fmt = str(cal.get("period_label_format", "{fy}-P{p:02d}"))

    close_policy = cal["close_policy"]
    open_last_n = int(close_policy["open_last_n_periods"])
    soft_closed_prior_n = int(close_policy["soft_closed_prior_n_periods"])

    periods = []
    y, p = start_year, start_period

    for _ in range(num_periods):
        periods.append((y, p))
        p += 1
        if p == 13:
            p = 1
            y += 1

    result = []

    for idx, (fy, fp) in enumerate(periods):
        from_end = (len(periods) - 1) - idx

        if from_end < open_last_n:
            status = "Open"
        elif from_end < open_last_n + soft_closed_prior_n:
            status = "Soft Closed"
        else:
            status = "Hard Closed"

        fy_label = f"{label_prefix}{str(fy)[-2:]}"
        period_name = label_fmt.format(fy=fy_label, p=fp)

        result.append(FiscalPeriod(fy, fp, period_name, status))

    return result


# ============================================================
# BUDGET ENGINE
# ============================================================

def base_budget_by_gl(gl_account_id: str) -> float:
    base_map = {
        "6100": 300000.0,
        "6200": 600000.0,
        "6300": 180000.0,
        "6400": 90000.0,
        "6500": 220000.0,
        "6600": 250000.0,
        "6700": 400000.0,
        "6800": 70000.0,
        "6900": 85000.0,
        "7000": 150000.0,
    }
    return base_map.get(gl_account_id, 100000.0)


def cost_center_multiplier(cost_center_id: str) -> float:
    if cost_center_id.startswith("CC2"):
        return 1.5
    elif cost_center_id.startswith("CC1"):
        return 1.1
    elif cost_center_id.startswith("CC3"):
        return 0.8
    elif cost_center_id.startswith("CC4"):
        return 1.3
    return 1.0


def yoy_growth_factor(fiscal_year: int, base_year: int) -> float:
    return (1 + 0.04) ** (fiscal_year - base_year)


def generate_budget_amount(fy, fp, gl_id, cc_id, base_year):
    return round(
        base_budget_by_gl(gl_id)
        * cost_center_multiplier(cc_id)
        * yoy_growth_factor(fy, base_year)
        * (1 + (fp - 6) * 0.005),
        2,
    )


# ============================================================
# VARIANCE ENGINE + CLOUD EXPANSION EVENT
# ============================================================

def determine_variance_pct(cc_id, fiscal_period, fiscal_year, gl_id):

    # === ENGINEERING CLOUD EXPANSION EVENT ===
    if (
        fiscal_year == 2025
        and fiscal_period in [11, 12]
        and cc_id.startswith("CC2")
        and gl_id == "6200"
    ):
        return 0.18  # deterministic 18% overspend

    # Normal volatility
    base_vol = 0.04

    if cc_id.startswith("CC2"):
        base_vol = 0.06
    elif cc_id.startswith("CC1"):
        base_vol = 0.05
    elif cc_id.startswith("CC3"):
        base_vol = 0.03

    if fiscal_period >= 10:
        base_vol *= 1.4

    r = random.random()

    if r < 0.85:
        return random.uniform(-base_vol, base_vol)
    elif r < 0.97:
        return random.uniform(base_vol * 1.5, base_vol * 3)
    else:
        return random.uniform(-base_vol * 3, -base_vol * 2)


def assign_driver(cc_id, gl_id, fiscal_year, fiscal_period, variance_pct):

    if (
        fiscal_year == 2025
        and fiscal_period in [11, 12]
        and cc_id.startswith("CC2")
        and gl_id == "6200"
    ):
        return "Cloud Expansion Program"

    abs_pct = abs(variance_pct)
    if abs_pct <= 0.04:
        return "Timing"
    elif abs_pct <= 0.12:
        return random.choice(["Volume", "Rate"])
    else:
        return "One-Time"


# ============================================================
# MAIN
# ============================================================

def main():

    structure_cfg = load_yaml(CONFIG_DIR / "finance_structure.yaml")
    materiality_cfg = load_yaml(CONFIG_DIR / "materiality.yaml")

    validate_structure_cfg(structure_cfg)

    calendar = build_fiscal_calendar(structure_cfg)
    dims = structure_cfg["dimensions"]
    base_year = calendar[0].fiscal_year

    rows = []
    prior_map = {}

    for period in calendar:
        for cc in dims["cost_centers"]:
            for gl in dims["gl_accounts"]:

                key = (cc["cost_center_id"], gl["gl_account_id"])

                budget = generate_budget_amount(
                    period.fiscal_year,
                    period.fiscal_period,
                    gl["gl_account_id"],
                    cc["cost_center_id"],
                    base_year,
                )

                variance_pct = determine_variance_pct(
                    cc["cost_center_id"],
                    period.fiscal_period,
                    period.fiscal_year,
                    gl["gl_account_id"],
                )

                actual = round(budget * (1 + variance_pct), 2)
                variance_amount = round(actual - budget, 2)
                variance_direction = "Unfavorable" if variance_amount > 0 else "Favorable"

                driver = assign_driver(
                    cc["cost_center_id"],
                    gl["gl_account_id"],
                    period.fiscal_year,
                    period.fiscal_period,
                    variance_pct,
                )

                is_material = (
                    abs(variance_amount) >= materiality_cfg["materiality"]["dollar_threshold"]
                    or abs(variance_pct) >= materiality_cfg["materiality"]["pct_threshold"]
                )

                prior = prior_map.get(key, 0.0)
                prior_map[key] = variance_amount

                rows.append({
                    "fiscal_year": period.fiscal_year,
                    "fiscal_period": period.fiscal_period,
                    "fiscal_period_name": period.fiscal_period_name,
                    "cost_center_id": cc["cost_center_id"],
                    "cost_center_name": cc["cost_center_name"],
                    "department_name": cc["department_name"],
                    "gl_account_id": gl["gl_account_id"],
                    "gl_account_name": gl["gl_account_name"],
                    "pnl_category": gl["pnl_category"],
                    "actual_amount": actual,
                    "budget_amount": budget,
                    "variance_amount": variance_amount,
                    "variance_pct": variance_pct,
                    "variance_direction": variance_direction,
                    "is_material": is_material,
                    "variance_driver": driver,
                    "variance_driver_detail": driver,
                    "driver_confidence": "High" if is_material else "Medium",
                    "prior_period_variance_amount": prior,
                    "variance_change_vs_prior": variance_amount - prior,
                    "variance_trend_direction": "Stable",
                    "rolling_3_period_variance": variance_amount,
                    "period_close_status": period.period_close_status,
                    "has_late_posting": False,
                    "late_posting_amount": 0.0,
                    "late_posting_period_count": 0,
                    "data_maturity_level": "Final" if period.period_close_status == "Hard Closed" else "Preliminary",
                    "explanation_readiness": "Ready",
                    "finance_signoff_flag": period.period_close_status == "Hard Closed",
                })

    df = pd.DataFrame(rows)[GOLD_SCHEMA_COLUMNS]

    df.to_csv(OUTPUT_DIR / "gold_dataset.csv", index=False)
    df.to_parquet(OUTPUT_DIR / "gold_dataset.parquet", index=False)

    print("Dataset generated.")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("Material %:", round(df["is_material"].mean() * 100, 2))


if __name__ == "__main__":
    main()
