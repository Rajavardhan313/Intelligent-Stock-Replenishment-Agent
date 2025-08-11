# import os
# import pandas as pd
# from dotenv import load_dotenv
# from .hana_connector import get_hana_connection

# load_dotenv()
# USE_MOCK = os.getenv("USE_MOCK_DATA", "true").lower() == "true"
# PO_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "mock_po_history.csv")

# PO_SQL = '''
# SELECT E.EBELN AS po_number, P.MATNR AS material_id,
#        P.MENGE AS order_qty, P.WEMNG AS received_qty, P.EINDT AS delivery_date
# FROM EKKO E JOIN EKPO P ON E.EBELN = P.EBELN
# ORDER BY P.EINDT DESC
# '''

# def extract_po_history():
#     if USE_MOCK:
#         df = pd.read_csv(os.path.abspath(PO_CSV))
#     else:
#         conn = get_hana_connection()
#         df = pd.read_sql(PO_SQL, conn)
#         conn.close()
#     return df

# if __name__ == "__main__":
#     df = extract_po_history()
#     out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output", "po_history_snapshot.csv"))
#     df.to_csv(out_path, index=False)
#     print("Wrote", out_path)

# sap/extract_po_history_odata.py
import os
import pandas as pd
from sap.odata_connector import fetch_odata_entity
from dotenv import load_dotenv

load_dotenv()

PO_ENTITY = os.getenv("ODATA_PO_ENTITY", "ZPO_SRV/PurchaseOrderSet")
PO_SELECT = os.getenv("ODATA_PO_SELECT", "EBELN,EBELP,MATNR,MENGE,NETPR,WAERS,DELIVERY_DATE,VENDOR")

def extract_po_history(select_fields: str = None, filter_expr: str = None):
    params = {"$select": select_fields or PO_SELECT}
    if filter_expr:
        params["$filter"] = filter_expr
    raw = fetch_odata_entity(PO_ENTITY, params=params)
    if not raw:
        return pd.DataFrame()

    df = pd.json_normalize(raw)
    # rename fields if necessary
    if "MATNR" in df.columns:
        df = df.rename(columns={"MATNR": "material_id"})
    if "EBELN" in df.columns:
        df = df.rename(columns={"EBELN": "po_number"})
    if "MENGE" in df.columns:
        df = df.rename(columns={"MENGE": "order_qty"})
    if "DELIVERY_DATE" in df.columns:
        df = df.rename(columns={"DELIVERY_DATE": "delivery_date"})
        df["delivery_date"] = pd.to_datetime(df["delivery_date"], errors="coerce")
    return df
