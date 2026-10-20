"""Mini pipeline Batik Kinanthi: omzet harian per kanal penjualan."""
import logging, os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("pipeline_mini")

load_dotenv()
DB_URL = (f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
          f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}"
          f"/{os.getenv('DB_NAME')}")
RAW_DIR = Path("data/raw")


def ingest(engine) -> pd.DataFrame:
    """INGESTION: ambil data transaksi dari sistem sumber."""
    df = pd.read_sql("SELECT id_transaksi, tanggal, kanal, total FROM transaksi", engine)
    log.info("Ingestion: %d baris transaksi diambil", len(df))
    return df


def store_raw(df: pd.DataFrame) -> None:
    """STORAGE: simpan salinan mentah apa adanya sebelum diolah."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / "transaksi.csv"
    df.to_csv(path, index=False)
    log.info("Storage: data mentah disimpan di %s", path)


def check_quality(df: pd.DataFrame) -> None:
    """Pemeriksaan kualitas data. Pipeline berhenti jika gagal."""
    masalah = []
    if df["id_transaksi"].duplicated().any():
        masalah.append("ada id_transaksi ganda")
    if (df["total"] <= 0).any():
        masalah.append("ada total <= 0")
    if df["kanal"].isna().any():
        masalah.append("ada kanal kosong")
    if masalah:
        raise ValueError(f"Data tidak lolos pemeriksaan: {masalah}")
    log.info("Kualitas data: lolos")


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """TRANSFORMATION: hitung omzet harian per kanal."""
    df = df.copy()
    df["tanggal"] = pd.to_datetime(df["tanggal"]).dt.date
    hasil = df.groupby(["tanggal", "kanal"], as_index=False).agg(
        jumlah_transaksi=("id_transaksi", "count"), omzet=("total", "sum"))
    log.info("Transformation: %d baris omzet harian dihasilkan", len(hasil))
    return hasil


def serve(df: pd.DataFrame, engine) -> None:
    """SERVING: tulis ke tabel siap pakai untuk analis dan dashboard."""
    df.to_sql("mart_omzet_harian", engine, if_exists="replace", index=False)
    log.info("Serving: tabel mart_omzet_harian siap dipakai")


def main() -> None:
    log.info("Pipeline dimulai")
    engine = create_engine(DB_URL)
    data = ingest(engine)
    store_raw(data)
    check_quality(data)
    omzet = transform(data)
    serve(omzet, engine)
    log.info("Pipeline selesai")


if __name__ == "__main__":
    main()