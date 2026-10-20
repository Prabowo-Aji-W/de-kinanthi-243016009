import random

random.seed(11)
JAM = 365 * 24

print("== Availability ==")
for a in (0.99, 0.999, 0.9999):
    print(f"{a * 100:.2f}% -> downtime {(1 - a) * JAM:6.1f} jam/tahun")

total = 1.0
for a in (0.999, 0.999, 0.995):  # aplikasi, database, jaringan
    total *= a
print(f"Berantai -> {total * 100:.2f}% | downtime {(1 - total) * JAM:.1f} jam/tahun")

print("== RPO: 20 transaksi/menit, crash di waktu acak ==")
TRX, BIAYA = 20, 500  # biaya per backup (rupiah, asumsi)
for iv in (1, 15, 60, 1440):  # interval backup dalam menit
    hilang = sum((random.uniform(0, 1440) % iv) * TRX for _ in range(2000)) / 2000
    print(f"backup tiap {iv:>4} mnt | rata-rata hilang {hilang:6.0f} trx | biaya {1440 / iv * BIAYA:>9,.0f} rp/hari")

print("== Retry: komponen gagal 30% ==")
for r in range(4):
    ok = sum(any(random.random() > 0.3 for _ in range(1 + r)) for _ in range(20000)) / 20000
    print(f"retry {r}x -> tingkat sukses {ok * 100:.1f}%")