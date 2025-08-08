from forecasting.forecasting_pipeline import compute_reorder

def test_compute_reorder_zero_consumption():
    row = {'product_id':'P0','current_stock':100,'daily_consumption':0,'lead_time_days':5,'safety_stock':10}
    out = compute_reorder(row)
    assert 'product_id' in out
