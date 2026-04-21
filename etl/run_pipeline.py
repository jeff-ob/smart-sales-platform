import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from etl.extract       import extract_data
from etl.transform     import transform_data
from etl.load          import load_data
from etl.feature_store import build_feature_store
from etl.rfm_analysis  import calculate_rfm, save_rfm_to_db
import sqlalchemy
from config import DB_PATH

def run():
    print("=" * 50)
    print("   SMART SALES PLATFORM — ETL Pipeline")
    print("=" * 50)

    df = extract_data()
    df = transform_data(df)
    load_data(df)

    print("\n>>> [FEATURE STORE] Construction des features...")
    df_features = build_feature_store(df)
    engine = sqlalchemy.create_engine(f"sqlite:///{DB_PATH}")
    df_features.to_sql("sales_features", con=engine,
                       if_exists="replace", index=False)
    print("    Table 'sales_features' sauvegardée.")

    print("\n>>> [RFM] Analyse et segmentation clients...")
    rfm = calculate_rfm(df)
    save_rfm_to_db(rfm)

    print("\n" + "=" * 50)
    print("   Pipeline complet — 3 tables en base :")
    print("   · sales          (données transformées)")
    print("   · sales_features (données enrichies)")
    print("   · rfm_segments   (segmentation RFM)")
    print("=" * 50)

if __name__ == "__main__":
    run()