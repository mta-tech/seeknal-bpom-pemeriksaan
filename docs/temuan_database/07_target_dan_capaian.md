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
