import pandas as pd
import math

def compute_reorder(row):
    daily = float(row.get("daily_consumption", 1.0) or 1.0)
    lead = int(row.get("lead_time_days", 0) or 0)
    safety = int(row.get("safety_stock", 0) or 0)
    current = int(row.get("current_stock", 0) or 0)

    days_until_depletion = current / (daily + 1e-9)
    suggested = max(0, math.ceil(lead * daily + safety - current))
    return {
        "product_id": row.get("product_id"),
        "days_until_depletion": days_until_depletion,
        "suggested_qty": suggested,
        "reorder_needed": suggested > 0
    }

def run_forecast(inventory_df):
    results = []
    for _, r in inventory_df.iterrows():
        results.append(compute_reorder(r))
    return pd.DataFrame(results)

if __name__ == "__main__":
    df = pd.read_csv("../data/mock_inventory_mard.csv")
    out = run_forecast(df)
    out.to_csv("../output/draft_pos.csv", index=False)
    print(out)
