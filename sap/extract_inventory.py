import os
import pandas as pd
from dotenv import load_dotenv
from .hana_connector import get_hana_connection

load_dotenv()
USE_MOCK = os.getenv("USE_MOCK_DATA", "true").lower() == "true"

INVENTORY_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "mock_inventory_mard.csv")
INVENTORY_SQL = '''
SELECT M.MATNR AS product_id,
       M.LGORT AS storage_loc,
       M.LABST AS current_stock,
       C.BSTMI AS reorder_point
FROM MARD M
JOIN MARC C ON M.MATNR = C.MATNR AND M.WERKS = C.WERKS
'''

def extract_inventory():
    if USE_MOCK:
        csv_path = os.path.abspath(INVENTORY_CSV)
        df = pd.read_csv(csv_path)
    else:
        conn = get_hana_connection()
        df = pd.read_sql(INVENTORY_SQL, conn)
        conn.close()
    return df

if __name__ == "__main__":
    df = extract_inventory()
    print(df.head())
    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output", "inventory_snapshot.csv"))
    df.to_csv(out_path, index=False)
    print("Wrote", out_path)
