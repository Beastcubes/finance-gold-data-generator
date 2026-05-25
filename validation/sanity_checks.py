from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "output" / "gold_dataset.csv"


def assert_true(condition, message):
    if not condition:
        raise AssertionError(f"FAILED: {message}")
    print(f"PASSED: {message}")


def main():
    print("=== SANITY CHECKS START ===")

    df = pd.read_csv(DATA_PATH)

    # -------------------------------------------------
    # 1. Schema check
    # -------------------------------------------------
    expected_columns = 29
    assert_true(len(df.columns) == expected_columns,
                "Column count matches GOLD schema (29 columns)")

    # -------------------------------------------------
    # 2. No nulls in critical finance columns
    # -------------------------------------------------
    critical_cols = [
        "actual_amount",
        "budget_amount",
        "variance_amount",
        "variance_pct",
        "cost_center_id",
        "gl_account_id",
    ]

    for col in critical_cols:
        assert_true(df[col].isnull().sum() == 0,
                    f"No nulls in {col}")

    # -------------------------------------------------
    # 3. Variance math integrity
    # -------------------------------------------------
    recompute = (df["actual_amount"] - df["budget_amount"]).round(2)
    assert_true((recompute == df["variance_amount"]).all(),
                "Variance amount matches actual - budget")

    # -------------------------------------------------
    # 4. Materiality logic
    # -------------------------------------------------
    material_rows = df[df["is_material"] == True]
    assert_true(len(material_rows) > 0,
                "Material rows exist")

    # -------------------------------------------------
    # 5. Q4 volatility check
    # -------------------------------------------------
    q4 = df[df["fiscal_period"] >= 10]
    q1 = df[df["fiscal_period"] <= 3]

    q4_vol = q4["variance_pct"].abs().mean()
    q1_vol = q1["variance_pct"].abs().mean()

    assert_true(q4_vol >= q1_vol,
                "Q4 volatility >= Q1 volatility")

    print("=== ALL SANITY CHECKS PASSED ===")


if __name__ == "__main__":
    main()
