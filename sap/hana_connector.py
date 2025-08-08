import os
from hdbcli import dbapi

def get_hana_connection():
    return dbapi.connect(
        address=os.getenv("HANA_HOST"),
        port=int(os.getenv("HANA_PORT", "30015")),
        user=os.getenv("HANA_USER"),
        password=os.getenv("HANA_PASSWORD")
    )
