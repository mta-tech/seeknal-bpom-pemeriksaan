# 07 — Target & Capaian 2024

> Analisis target vs realisasi inspeksi tahun 2024. Bridge key: `mapping_komoditi_target_balai` + `lower(nama_upt)`.

## 7.1 Struktur Target

`target_balai` (532 baris) = 76 balai × 7 komoditi × **1 tahun (hanya 2024)**.

| Kolom target | Deskripsi | Sample |
|---|---|---|
| `target_penandaan` | Target labeling produk | bervariasi |
| `target_pengawasan` | Target inspeksi sarana | 600-620 per balai utama |
| `target_pengujian` | Target uji lab | bervariasi |
| `target_pengujian_pangan` | Uji lab pangan (khusus pangan) | structural NULL untuk non-pangan |
| `target_sarana_distribusi` | Sarana distribusi | bervariasi |
| `target_sarana_produksi` | Sarana produksi | bervariasi |

## 7.2 Capaian per Komoditi Nasional (tanpa fan-out)

```sql
WITH target_agg AS (
  SELECT komoditi, sum(target_pengawasan) AS target_nas
  FROM target_balai WHERE tahun=2024 AND target_pengawasan > 0 GROUP BY 1
),
realisasi_agg AS (
  SELECT upper(mapping_komoditi_target_balai) AS komoditi_map, count(*) AS realisasi
  FROM mv_pemeriksaan
  WHERE tanggal_mulai BETWEEN '2024-01-01' AND '2024-12-31'
    AND mapping_komoditi_target_balai IS NOT NULL GROUP BY 1
)
SELECT t.komoditi, t.target_nas, r.realisasi,
  round(100.0*r.realisasi/t.target_nas,1) AS pct_capai
FROM target_agg t LEFT JOIN realisasi_agg r ON upper(t.komoditi)=r.komoditi_map
ORDER BY pct_capai DESC NULLS LAST;
```

| Komoditi | Target Nasional | Realisasi | % Capai |
|---|---|---|---|
| **Produk Pangan** | 13.124 | 19.809 | **150,9%** 🟢 over-achieve |
| Obat Tradisional (OT) | 5.000 | 4.045 | 80,9% |
| Suplemen Kesehatan | 2.000 | 1.549 | 77,5% |
| Kosmetika | 15.000 | 8.276 | 55,2% |
| Obat Kuasi | 1.000 | 4 | **0,4%** 🔴 |
| Rokok | 21.504 | **0** | **0%** 🔴 |
| Obat | (target=0) | 14.225 | — (target nol = kebijakan) |

## 7.3 Catatan Penting per Komoditi

### Produk Pangan (150,9% — over-achieve)
Melebihi target 50%. Pengawasan pangan sangat aktif (termasuk INTENSIFIKASI PANGAN).
Sektor PANGAN IRT tetap bermasalah meskipun target tercapai (lihat [06](06_korelasi_dan_peta_risiko.md)).

### Obat (target = 0)
**Semua 76 balai punya `target_pengawasan = 0`** untuk Obat. Ini **bukan NULL, benar-benar angka 0**.
Ini keputusan kebijakan — pengawasan obat mungkin diukur via mekanisme lain (CPOB/sertifikasi),
bukan via `target_pengawasan`. Tetap ada 14.225 inspeksi Obat tanpa pembanding target.

### Rokok (0% — gap data total)
Target 21.504, realisasi **0**. Tidak ada satu pun komoditi 'ROKOK' di fact table.
**Gap cakupan data, bukan kegagalan kinerja** — inspeksi rokok mungkin tercatat di sistem lain.
Perlu konfirmasi: di mana data inspeksi rokok tercatat?

### Obat Kuasi (0,4%)
Target 1.000, realisasi hanya 4. BAHAN BERBAHAYA (yang map ke Obat Kuasi) hanya 108 inspeksi total.
Sangat sedikit — mungkin komoditi kecil atau memang jarang diinspeksi.

## 7.4 ⚠️ Fan-Out Trap pada Query Target

**JANGAN lakukan JOIN langsung** target × fact:

```sql
-- ❌ SALAH — fan-out menggelembungkan angka:
SELECT t.komoditi, sum(t.target_pengawasan), count(p.id)
FROM target_balai t LEFT JOIN mv_pemeriksaan p ON ...
-- Hasil: target jutaan (karena setiap baris target dikali banyak baris fact)
```

**BENAR**: agregasi target dan realisasi **TERPISAH**, lalu join hasil agregat (seperti query di §7.2).

## 7.5 Unmatched Target Balai

15 `nama_balai` di `target_balai` tidak match ke `mv_pemeriksaan.nama_upt`:

| Tipe | Jumlah | Penyebab |
|---|---|---|
| DIREKTORAT | 6 | Central office Jakarta, bukan balai daerah |
| DEMO | 2 | Data test (DEMO BALAI BESAR, DEMO TIPE A) |
| LOKA POM | 7 | Sub-balai, perlu roll-up ke Balai induk |

**Untuk hitung capaian akurat**: Loka POM harus digulung ke Balai induknya.
Filter DEMO (93 baris di fact, 2 di target).

---

## 7.6 Verifikasi kunci join komoditi (2026-08-13)

§4.5 `04_kamus_unique_value.md` sudah menetapkan `mapping_komoditi_target_balai` sebagai bridge
key. Berikut **bukti kuantitatif** seberapa besar bedanya kalau aturan itu dilanggar — memakai
realisasi sarana distribusi 2025 sebagai contoh:

```sql
-- A) SALAH: join pakai komoditi mentah
WITH ld AS (
  SELECT nama_upt, komoditi AS k, count(*) AS j FROM mv_pemeriksaan
  WHERE extract(year FROM tanggal_selesai)=2025 AND lower(sarana)='distribusi' GROUP BY 1,2)
SELECT count(*) AS pasangan, count(tb.id) AS ketemu FROM ld
LEFT JOIN target_balai tb ON lower(trim(tb.nama_balai))=lower(trim(ld.nama_upt))
                         AND lower(trim(tb.komoditi))=lower(trim(ld.k)) AND tb.tahun=2024;
--  385 | 228        ← 41% pasangan kehilangan target

-- B) BENAR: join pakai mapping_komoditi_target_balai
--    (ganti `komoditi AS k` menjadi `mapping_komoditi_target_balai AS k`)
--  385 | 381        ← 99% ketemu
```

Selisihnya **153 pasangan balai×komoditi** yang diam-diam kehilangan target dan karenanya
menghilang dari perhitungan capaian (atau muncul sebagai capaian NULL).

### Peta jembatan lengkap

```sql
SELECT komoditi, mapping_komoditi_target_balai, count(*) FROM mv_pemeriksaan GROUP BY 1,2 ORDER BY 1;
```

| `komoditi` (13 nilai) | → `mapping_komoditi_target_balai` (6 nilai) | Baris |
|---|---|--:|
| BAHAN BAKU OBAT · BAHAN OBAT · NARKOTIKA · OBAT · OBAT OBAT TERTENTU · PREKURSOR · PRODUK BIOLOGI DAN SARANA KHUSUS · PSIKOTROPIKA | **OBAT** | 83.752 |
| KOSMETIK | **KOSMETIKA** | 39.317 |
| OBAT TRADISIONAL | **OBAT TRADISIONAL (OT)** | 19.925 |
| PRODUK PANGAN | **PRODUK PANGAN** | 107.254 |
| SUPLEMEN KESEHATAN | **SUPLEMEN KESEHATAN** | 7.126 |
| **BAHAN BERBAHAYA** | **OBAT KUASI** ⚠️ | 108 |

⚠️ Pemetaan terakhir janggal secara semantik: **BAHAN BERBAHAYA dipetakan ke OBAT KUASI**.
Perlu konfirmasi domain sebelum dipakai untuk pelaporan capaian Obat Kuasi. Sementara itu, kalau
pertanyaannya spesifik "Obat Kuasi", sebutkan bahwa realisasinya berasal dari komoditi
BAHAN BERBAHAYA.

Catatan: `target_balai.komoditi` punya nilai `Rokok` yang **tidak punya pasangan sama sekali** di
`mv_pemeriksaan` — pemeriksaan sarana memang tidak mengenal komoditi rokok.

### Nama balai — 15 tanpa target, dan tiga di antaranya bukan balai

Setelah normalisasi `lower(trim())`, masih ada 15 dari 91 `nama_upt` tanpa target:

```sql
SELECT x.nama_upt, x.n FROM (SELECT nama_upt, count(*) n FROM mv_pemeriksaan GROUP BY 1) x
LEFT JOIN (SELECT DISTINCT lower(trim(nama_balai)) nb FROM target_balai) t
  ON lower(trim(x.nama_upt)) = t.nb
WHERE t.nb IS NULL ORDER BY 2 DESC;
```

| `nama_upt` | Baris | Sifat |
|---|--:|---|
| DIREKTORAT PENGAWASAN DISTRIBUSI DAN PELAYANAN ONPP | 410 | unit pusat |
| DIREKTORAT PENGAWASAN PRODUKSI ONPP | 168 | unit pusat |
| DIREKTORAT PENGAWASAN PRODUKSI PANGAN OLAHAN | 158 | unit pusat |
| DIREKTORAT PENGAWASAN KOSMETIK | 128 | unit pusat |
| **DEMO TIPE A** | **90** | **akun uji — harus dikecualikan** |
| DIREKTORAT PENGAWASAN PEREDARAN PANGAN OLAHAN | 72 | unit pusat |
| LOKA POM DI KABUPATEN BONE · KARAWANG · GROBOGAN · TEGAL · dll | 9 loka | loka baru, belum ada target |

Tiga kelompok yang berbeda penanganannya: **unit pusat** dilaporkan terpisah (memang tidak
bertarget), **DEMO TIPE A** adalah akun uji dan harus dikecualikan dari semua hitungan
(analog akun uji `trader_id IN (5,17,50,85)` di domain registrasi), **loka baru** dilaporkan
sebagai "target belum ditetapkan".
