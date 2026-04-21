import os

# Chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH  = os.path.join(BASE_DIR, "sales.db")

# Paramètres ETL
RAW_FILE = os.path.join(DATA_DIR, "sales_raw.csv")