# import os
# import pandas as pd
# from dotenv import load_dotenv
# from .hana_connector import get_hana_connection

# load_dotenv()
# USE_MOCK = os.getenv("USE_MOCK_DATA", "true").lower() == "true"

# INVENTORY_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "mock_inventory_mard.csv")
# INVENTORY_SQL = '''
# SELECT M.MATNR AS product_id,
#        M.LGORT AS storage_loc,
#        M.LABST AS current_stock,
#        C.BSTMI AS reorder_point
# FROM MARD M
# JOIN MARC C ON M.MATNR = C.MATNR AND M.WERKS = C.WERKS
# '''

# def extract_inventory():
#     if USE_MOCK:
#         csv_path = os.path.abspath(INVENTORY_CSV)
#         df = pd.read_csv(csv_path)
#     else:
#         conn = get_hana_connection()
#         df = pd.read_sql(INVENTORY_SQL, conn)
#         conn.close()
#     return df

# if __name__ == "__main__":
#     df = extract_inventory()
#     print(df.head())
#     out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output", "inventory_snapshot.csv"))
#     df.to_csv(out_path, index=False)
#     print("Wrote", out_path)

# sap/extract_inventory_odata.py
import os
import pandas as pd
from sap.odata_connector import fetch_odata_entity
from dotenv import load_dotenv

load_dotenv()

# Example entity path - replace with your actual OData service and entity set
# e.g. 'ZINVENTORY_SRV/InventorySet' or 'API_MATERIAL/Inventory'
INVENTORY_ENTITY = os.getenv("ODATA_INVENTORY_ENTITY", "ZINVENTORY_SRV/InventorySet")

# Fields we want from the OData service. Map to SAP internal fields:
# MATNR -> product_id, LGORT -> storage_loc, LABST -> current_stock
# daily_consumption may not be present in a single table; you can compute from movements or have a dedicated view
DEFAULT_SELECT = os.getenv("ODATA_INVENTORY_SELECT", 
                           "MATNR,LGORT,LABST,PLIFZ,SAF_STOCK,UNIT,PRODUCT_DESC")

def extract_inventory(select_fields: str = None, filter_expr: str = None):
    """
    Extracts inventory records from OData. Returns pandas.DataFrame
    select_fields: comma-separated field list for $select
    filter_expr: OData $filter expression, e.g. \"PLANT eq '1000'\"
    """
    select = select_fields or DEFAULT_SELECT
    params = {"$select": select}
    if filter_expr:
        params["$filter"] = filter_expr
    raw = fetch_odata_entity(INVENTORY_ENTITY, params=params)
    if not raw:
        return pd.DataFrame()

    # Normalize to DataFrame
    df = pd.json_normalize(raw)

    # Rename typical SAP fields to your internal names if present
    rename_map = {}
    if "MATNR" in df.columns:
        rename_map["MATNR"] = "product_id"
    if "LGORT" in df.columns:
        rename_map["LGORT"] = "storage_loc"
    if "LABST" in df.columns:
        rename_map["LABST"] = "current_stock"
    if "PLIFZ" in df.columns:
        rename_map["lead_time_days"] = "PLIFZ"  # will map below if present

    df = df.rename(columns=rename_map)

    # Example: if SAF_STOCK exists rename to safety_stock
    if "SAF_STOCK" in df.columns:
        df = df.rename(columns={"SAF_STOCK": "safety_stock"})
    if "PRODUCT_DESC" in df.columns:
        df = df.rename(columns={"PRODUCT_DESC": "product_name"})

    # Convert numeric columns if they exist
    for col in ["current_stock", "lead_time_days", "safety_stock"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # Your OData view might not have daily_consumption - you can compute it later from movements or use a column here
    return df
