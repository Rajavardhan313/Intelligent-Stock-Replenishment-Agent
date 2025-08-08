from dotenv import load_dotenv
load_dotenv()

from sap.extract_inventory import extract_inventory
from sap.extract_po_history import extract_po_history
from forecasting.forecasting_pipeline import run_forecast
from forecasting.po_generator import generate_draft_pos
from forecasting.gpt_commentary import generate_commentary
from notifier import send_slack_message
import pandas as pd
from datetime import datetime
import os
import json

def default_vendor_lookup(product_id, meta):
    return meta.get('best_vendor') or 'VENDOR_1'

def main():
    inv = extract_inventory()
    po_hist = extract_po_history()
    snapshot_ts = datetime.utcnow().isoformat()
    forecast = run_forecast(inv)
    draft_list = generate_draft_pos(forecast, inv, snapshot_ts, default_vendor_lookup)

    # attach commentary and save
    if not os.path.exists('output'):
        os.makedirs('output')
    drafts = []
    for d in draft_list:
        # enrich with days_until_depletion from forecast
        row = forecast[forecast['product_id'] == d['product_id']].iloc[0].to_dict()
        d['days_until_depletion'] = row.get('days_until_depletion')
        d['commentary'] = generate_commentary(d)
        drafts.append(d)
        # notify
        send_slack_message(f"Draft PO for {d['product_id']}: qty={d['qty']}\n{d['commentary']}")
    df = pd.DataFrame(drafts)
    out_path = os.path.join('output', 'draft_pos.csv')
    df.to_csv(out_path, index=False)
    print('Wrote', out_path)

if __name__ == '__main__':
    main()
