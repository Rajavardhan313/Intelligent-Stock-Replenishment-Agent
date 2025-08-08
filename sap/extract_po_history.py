import os
import pandas as pd
from dotenv import load_dotenv
from .hana_connector import get_hana_connection

load_dotenv()
USE_MOCK = os.getenv("USE_MOCK_DATA", "true").lower() == "true"
PO_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "mock_po_history.csv")

PO_SQL = '''
SELECT E.EBELN AS po_number, P.MATNR AS material_id,
       P.MENGE AS order_qty, P.WEMNG AS received_qty, P.EINDT AS delivery_date
FROM EKKO E JOIN EKPO P ON E.EBELN = P.EBELN
ORDER BY P.EINDT DESC
'''

def extract_po_history():
    if USE_MOCK:
        df = pd.read_csv(os.path.abspath(PO_CSV))
    else:
        conn = get_hana_connection()
        df = pd.read_sql(PO_SQL, conn)
        conn.close()
    return df

if __name__ == "__main__":
    df = extract_po_history()
    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output", "po_history_snapshot.csv"))
    df.to_csv(out_path, index=False)
    print("Wrote", out_path)
