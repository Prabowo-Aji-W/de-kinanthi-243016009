import os, random
import pandas as pd
from dotenv import load_dotenv
from faker import Faker
from sqlalchemy import create_engine

load_dotenv()
fake = Faker("id_ID")
Faker.seed(42)
random.seed(42)

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME')}"
)

KOTA = ["Surakarta", "Sukoharjo", "Klaten", "Boyolali",
        "Karanganyar", "Yogyakarta", "Semarang", "Jakarta"]
MOTIF = ["Parang", "Kawung", "Truntum", "Sidomukti", "Sekar Jagad", "Mega Mendung"]
KATEGORI = {"Kemeja": (150_000, 450_000), "Kain": (200_000, 1_500_000),
            "Dress": (250_000, 600_000), "Selendang": (75_000, 250_000)}
TEKNIK = ["Tulis", "Cap", "Kombinasi"]
KANAL = ["toko", "web", "marketplace"]

pelanggan = pd.DataFrame({
    "id_pelanggan": range(1, 501),
    "nama": [fake.name() for _ in range(500)],
    "kota": [random.choice(KOTA) for _ in range(500)],
    "tanggal_daftar": [fake.date_between("-3y", "-1y") for _ in range(500)],
})

kombinasi = random.sample([(m, k, t) for m in MOTIF for k in KATEGORI for t in TEKNIK], 60)
produk = pd.DataFrame([
    {"id_produk": i + 1, "nama": f"{k} Batik {m} {t}", "motif": m, "kategori": k,
     "harga": round(random.randint(*KATEGORI[k]), -3)}
    for i, (m, k, t) in enumerate(kombinasi)
])

harga_produk = dict(zip(produk.id_produk, produk.harga))
tgl_daftar = dict(zip(pelanggan.id_pelanggan, pelanggan.tanggal_daftar))

transaksi, detail = [], []
for id_trx in range(1, 5001):
    id_plg = random.randint(1, 500)
    tanggal = fake.date_time_between(start_date=tgl_daftar[id_plg], end_date="now")
    total = 0
    for id_prd in random.sample(range(1, 61), random.randint(1, 4)):
        jumlah = random.randint(1, 3)
        harga = int(harga_produk[id_prd])
        detail.append({"id_transaksi": id_trx, "id_produk": id_prd,
                       "jumlah": jumlah, "harga_satuan": harga})
        total += jumlah * harga
    transaksi.append({"id_transaksi": id_trx, "id_pelanggan": id_plg, "tanggal": tanggal,
                      "kanal": random.choices(KANAL, weights=[0.3, 0.2, 0.5])[0], "total": total})

for nama, df in {"pelanggan": pelanggan, "produk": produk,
                 "transaksi": pd.DataFrame(transaksi),
                 "detail_transaksi": pd.DataFrame(detail)}.items():
    df.to_sql(nama, engine, if_exists="replace", index=False)
    print(f"{nama}: {len(df)} baris dimuat")