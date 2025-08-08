import math
import hashlib
from datetime import datetime, timedelta

DEFAULT_VENDOR = "VENDOR_1"

def make_draft_id(product_id, snapshot_ts):
    key = f"{product_id}|{snapshot_ts}"
    return "draft-" + hashlib.sha1(key.encode()).hexdigest()[:10]

def apply_business_rules(item, product_meta):
    qty = int(item.get('suggested_qty', 0) or 0)
    moq = int(product_meta.get('moq', 0) or 0)
    lot = int(product_meta.get('lot_size', 1) or 1)
    max_cap = int(product_meta.get('max_order_qty', 0) or 0)

    reasons = []

    if qty <= 0:
        return {"qty": 0, "reasons": ["no_reorder_needed"]}

    if moq and qty < moq:
        reasons.append(f"applied_moq({moq})")
        qty = moq

    if lot > 1 and qty % lot != 0:
        qty = math.ceil(qty / lot) * lot
        reasons.append(f"rounded_to_lot({lot})")

    if max_cap and qty > max_cap:
        reasons.append(f"capped_to_max({max_cap})")
        qty = max_cap

    return {"qty": qty, "reasons": reasons}

def generate_draft_pos(forecast_df, inventory_df, snapshot_ts, vendor_lookup_fn):
    pos = []
    for _, r in forecast_df.iterrows():
        if not r.get('reorder_needed'):
            continue
        product_id = r['product_id']
        item_meta = inventory_df[inventory_df['product_id'] == product_id].iloc[0].to_dict()

        br = apply_business_rules(r, item_meta)
        if br['qty'] <= 0:
            continue

        vendor = vendor_lookup_fn(product_id, item_meta)
        eta = (datetime.utcnow() + timedelta(days=int(item_meta.get('lead_time_days', 0)))).date().isoformat()

        draft = {
            'po_id': make_draft_id(product_id, snapshot_ts),
            'product_id': product_id,
            'product_name': item_meta.get('product_name'),
            'storage_loc': item_meta.get('storage_loc'),
            'vendor': vendor,
            'qty': br['qty'],
            'unit_cost': float(item_meta.get('unit_cost', 0) or 0),
            'total_cost': br['qty'] * float(item_meta.get('unit_cost', 0) or 0),
            'requested_eta': eta,
            'lead_time_days': int(item_meta.get('lead_time_days', 0) or 0),
            'current_stock': int(item_meta.get('current_stock', 0) or 0),
            'daily_consumption': float(item_meta.get('daily_consumption', 0) or 0),
            'safety_stock': int(item_meta.get('safety_stock', 0) or 0),
            'moq': int(item_meta.get('moq', 0) or 0),
            'lot_size': int(item_meta.get('lot_size', 1) or 1),
            'reorder_reason': ';'.join(br['reasons']) if br['reasons'] else 'forecast_shortfall',
            'commentary': '',
            'created_by': 'system',
            'created_at': datetime.utcnow().isoformat(),
            'source_snapshot_id': snapshot_ts,
            'status': 'draft'
        }

        pos.append(draft)

    return pos
