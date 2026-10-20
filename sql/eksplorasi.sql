-- 1. Jumlah baris per tabel
SELECT 'pelanggan' AS tabel, COUNT(*) FROM pelanggan
UNION ALL SELECT 'produk', COUNT(*) FROM produk
UNION ALL SELECT 'transaksi', COUNT(*) FROM transaksi
UNION ALL SELECT 'detail_transaksi', COUNT(*) FROM detail_transaksi;

-- 2. Omzet per kanal penjualan
SELECT kanal, COUNT(*) AS jumlah_transaksi, SUM(total) AS omzet
FROM transaksi GROUP BY kanal ORDER BY omzet DESC;

-- 3. Lima produk terlaris
SELECT p.nama, SUM(d.jumlah) AS terjual
FROM detail_transaksi d JOIN produk p ON p.id_produk = d.id_produk
GROUP BY p.nama ORDER BY terjual DESC LIMIT 5;