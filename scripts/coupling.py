stok, analitik = [], []
layanan_email_hidup = False  # TUGAS 5: simulasi, False = layanan email sedang down

def kurangi_stok(e): stok.append(e["id"])
def catat_analitik(e): analitik.append(e["id"])
def kirim_email(e):
    if e["id"] == 2 and not layanan_email_hidup:  # TUGAS 5: tambah kondisi
        raise ConnectionError("layanan email down")

# Desain A: tightly coupled (order service memanggil semuanya langsung)
def buat_pesanan_tight(e):
    kurangi_stok(e); kirim_email(e); catat_analitik(e)

# Desain B: loosely coupled (producer -> router -> consumer)
class Router:
    def __init__(self):
        self.pelanggan, self.dlq = {}, []
        # TUGAS 5: pasangan (nama handler, id event) yang SUDAH berhasil diproses
        self.selesai = set()

    def subscribe(self, topik, handler):
        self.pelanggan.setdefault(topik, []).append(handler)

    # TUGAS 5: menjalankan satu handler secara idempotent
    def _jalankan(self, h, event):
        kunci = (h.__name__, event["id"])
        if kunci in self.selesai:
            return True  # sudah pernah sukses: lewati, jangan diproses dua kali
        try:
            h(event)
        except Exception as err:
            self.dlq.append({"handler": h.__name__, "event": event, "error": str(err)})
            return False
        self.selesai.add(kunci)
        return True

    def publish(self, topik, event):
        for h in self.pelanggan.get(topik, []):
            self._jalankan(h, event)  # TUGAS 5: memakai _jalankan

    # TUGAS 5: ulang event di DLQ, hanya handler yang gagal
    def ulang_dlq(self):
        semua = {h.__name__: h for hs in self.pelanggan.values() for h in hs}
        antrean, self.dlq = self.dlq, []
        berhasil = 0
        for item in antrean:
            if self._jalankan(semua[item["handler"]], item["event"]):
                berhasil += 1
        print(f"ulang_dlq: {berhasil} berhasil, {len(self.dlq)} masih di DLQ")

router = Router()
for h in (kurangi_stok, kirim_email, catat_analitik):
    router.subscribe("pesanan_baru", h)

print("== Desain A ==")
for i in (1, 2, 3):
    try:
        buat_pesanan_tight({"id": i}); print(f"pesanan {i}: sukses")
    except Exception as err:
        print(f"pesanan {i}: GAGAL ({err})")
print("stok:", stok, "| analitik:", analitik)

stok.clear(); analitik.clear()

print("== Desain B ==")
for i in (1, 2, 3):
    router.publish("pesanan_baru", {"id": i}); print(f"pesanan {i}: diterima")
print("stok:", stok, "| analitik:", analitik)
print("dead-letter:", router.dlq)

def cek_fraud(e):
    if e["id"] % 2 == 0:
        print(f"PERINGATAN fraud: pesanan {e['id']} mencurigakan")

router.subscribe("pesanan_baru", cek_fraud)

def buat_pesanan_tight(e):
    kurangi_stok(e); kirim_email(e); cek_fraud(e); catat_analitik(e)

# ===== TUGAS 5: uji ulang_dlq() =====
print("== Tugas 5: ulang_dlq() ==")
print("dead-letter sebelum:", router.dlq)
layanan_email_hidup = True  # layanan email sudah diperbaiki
router.ulang_dlq()
print("stok:", stok, "| analitik:", analitik)
print("dead-letter sesudah:", router.dlq)

print("-- uji idempotent: ulang_dlq() lagi dan publish ulang pesanan 1 --")
router.ulang_dlq()
router.publish("pesanan_baru", {"id": 1})
print("stok:", stok, "| analitik:", analitik)