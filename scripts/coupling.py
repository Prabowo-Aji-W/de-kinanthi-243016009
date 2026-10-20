stok, analitik = [], []

def kurangi_stok(e): stok.append(e["id"])
def catat_analitik(e): analitik.append(e["id"])
def kirim_email(e):
    if e["id"] == 2:
        raise ConnectionError("layanan email down")

# Desain A: tightly coupled (order service memanggil semuanya langsung)
def buat_pesanan_tight(e):
    kurangi_stok(e); kirim_email(e); catat_analitik(e)

# Desain B: loosely coupled (producer -> router -> consumer)
class Router:
    def __init__(self):
        self.pelanggan, self.dlq = {}, []

    def subscribe(self, topik, handler):
        self.pelanggan.setdefault(topik, []).append(handler)

    def publish(self, topik, event):
        for h in self.pelanggan.get(topik, []):
            try:
                h(event)
            except Exception as err:
                self.dlq.append({"handler": h.__name__, "event": event, "error": str(err)})

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
    

