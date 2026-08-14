#DATABASE STRUCTURE MAP — TABLE INVENTORY, JOIN RULES, STAR TOPOLOGY, AND DATA QUALITY TRAPS#

Domain: **Pemeriksaan BPOM** — inspeksi sarana produksi/distribusi/pelayanan obat, pangan, kosmetik,
suplemen, narkotika, dan bahan berbahaya. Single database, single schema (`public`).
No dual-system like ERBA/ERLA — but naming conventions and case formats vary across tables.

## Tables

| Table | Rows | Types | Notes |
|---|---|---|---|
| `mv_pemeriksaan` | 257.434 | native (bigint, text, date) | **FACT UTAMA** — 1 baris = 1 inspeksi. PK: `id`. |
| `mv_pemeriksaan_log` | 1.311.582 | native | Audit trail workflow. N:1 via `id_pemeriksaan`. `id_steps` ≈ unique. |
| `mv_pemeriksaan_petugas` | 581.810 | native | Tim pemeriksa. N:1 via `id_pemeriksaan`. `jenis_id` = peran (25 nilai). |
| `mv_pemeriksaan_temuan` | 296.946 | native | Produk temuan. N:1 via `id_pemeriksaan`. Hanya 12,6% punya temuan. |
| `mv_pemeriksaan_timeline` | 288.133 | native | Durasi per tahap. 1:1 via `id_pemeriksaan`. **30.699 ORPHAN** (12%). |
| `mv_pemeriksaan_jenis_pangan` | 67.192 | native | Exploded array jenis pangan. N:1 via `id_pemeriksaan`. 18,8% pemeriksaan. |
| `mv_pemeriksaan_kategori_temuan` | 241.609 | native | Exploded array kategori temuan. N:1 via `id_pemeriksaan`. 49 kategori. |
| `mv_kriteria_pemeriksaan` | 5.892 | native | Checklist audit CPKB/CPOB. N:1 via `pemeriksaan_id`. 0,35% pemeriksaan. |
| `mv_pemeriksaan_agg` | 366.767 | native | Pre-computed rollup. 2 granularitas: `day` dan `month`. |
| `coverage_balai` | 668 | native | Dimensi balai → kabupaten. 88 balai, 514 kabupaten. |
| `target_balai` | 532 | native | Target tahunan. 76 balai × 7 komoditi. **Tahun 2024 only.** |

**All tables are physical (`relkind='r'`)** — prefix `mv_` is misleading; these are NOT materialized
views. Refresh is done via external ETL (kolom `sync` shows batch load timestamps).

**No primary keys, no foreign keys, no indexes defined** — integrity must be enforced by query logic,
not by DB constraints.

## Joins (no foreign keys — these must be known, not guessed)

**Fact to Child tables** (via `id_pemeriksaan`):

| Child | Rel | Coverage | Notes |
|---|---|---|---|
| `mv_pemeriksaan_log` | 1:N | 100% | Solid. Avg 5,09 langkah/pemeriksaan. |
| `mv_pemeriksaan_petugas` | 1:N | 100% | Solid. Avg 2,26 petugas/pemeriksaan. |
| `mv_pemeriksaan_temuan` | 1:N | 12,6% | Wajar — hanya TMK punya temuan. |
| `mv_pemeriksaan_timeline` | 1:1 | 100% + orphan | 30.699 orphan = pemeriksaan dihapus tapi timeline tersisa. |
| `mv_pemeriksaan_jenis_pangan` | 1:N | 18,8% | Wajar — hanya pangan. |
| `mv_pemeriksaan_kategori_temuan` | 1:N | 11,5% | Exploded array dari temuan. |
| `mv_kriteria_pemeriksaan` | 1:N | 0,35% | Hanya sertifikasi CPKB/CPOB. FK: `pemeriksaan_id`. |

**Fact to Dimension tables** (SOFT JOIN — string matching):

| Dimension | Join Key | Issue |
|---|---|---|
| `target_balai` | `mapping_komoditi_target_balai` + `lower(nama_upt) = lower(nama_balai)` | Case sensitivity. 15 unmatched (6 direktorat + 2 demo + 7 loka). |
| `coverage_balai` | `lower(nama_upt) = lower(nama_balai)` | Case sensitivity. 1 kabupaten unmatched (Intan Jaya). |

**WARNING:** `komoditi` in `target_balai` uses Title Case ("Kosmetika"), fact uses UPPER ("KOSMETIK").
Always use `mapping_komoditi_target_balai` as the bridge key for target comparisons.

**WARNING:** `komoditi` in `mv_pemeriksaan_petugas` means DIFFERENT thing — it encodes facility type
(APOTEK, PBF, PKM) not product category. Same column name, different semantic.

## Data Coverage and Freshness

| Metric | Value |
|---|---|
| Periode data | 2020-2026 (signifikan mulai 2020) |
| Refresh terakhir | 2026-08-11 05:52 (sync timestamp) |
| Balai aktif | 91 (di mv_pemeriksaan) |
| Provinsi tercakup | 34 |
| Kabupaten tercakup | 514 (100% dari coverage_balai) |

## Schema Paralel: public vs dimension

Schema `dimension` berisi 8 tabel yang OVERLAP dengan `public`:
- `dimension.mv_pemeriksaan` = 150.603 baris vs `public.mv_pemeriksaan` = 257.434 baris
- `dimension.target_balai` = 76 baris vs `public.target_balai` = 532 baris

`public` adalah versi yang LEBIH LENGKAP dan LEBIH BARU. `dimension` adalah snapshot lama.
**Selalu query dari `public`** — `dimension` tidak dipakai untuk analisis.

## Data Quality Traps

| Trap | Severity | Detail |
|---|---|---|
| No PK/FK/Indexes | CRITICAL | Integritas tidak terjamin. Semua query = seq scan. |
| 30.699 orphan timeline | CRITICAL | `id_pemeriksaan` tidak ada di fact. Filter: `WHERE EXISTS (SELECT 1 FROM mv_pemeriksaan p WHERE p.id=t.id_pemeriksaan)`. |
| 14 outlier tanggal | CRITICAL | Tanggal: 0004, 0020, 1922-1928, 1970. Filter: `tanggal_mulai >= '2015-01-01'`. |
| 2 future tanggal | CRITICAL | Tanggal 2027. Filter: `tanggal_mulai <= CURRENT_DATE`. |
| 64 corrupt log | CRITICAL | `id_steps`, `status`, `created_at` null bersamaan. |
| day_input_mulai max 736.685 | CRITICAL | ~2018 tahun. Nilai tidak valid. |
| day_mulai_selesai max 34.706 | CRITICAL | ~95 tahun. Nilai tidak valid. |
| tp_jml_temuan negatif | MEDIUM | Min -196. Jumlah temuan tidak bisa negatif. |
| tp_harga_total negatif | MEDIUM | Min -5.360.000. Harga tidak bisa negatif. |
| Case mismatch | MEDIUM | coverage Title Case, fact UPPER, target campuran. JOIN harus pakai `lower()`. |
| Komoditi naming mismatch | MEDIUM | "Kosmetika" vs "KOSMETIK". Pakai `mapping_komoditi_target_balai`. |
| Sinonim ganda | MEDIUM | "Pemusnahan"/"Dimusnahkan", "Pengamanan"/"Diamankan". |
| 2 kolom mati | LOW | `tp_pelanggaran` (99,996% null), `tp_netto` (99,998% null). |
| 83% grade NULL | LOW | Grade hanya untuk sebagian pemeriksaan. |
| DEMO data | LOW | 3 baris: "DEMO BALAI BESAR", "DEMO TIPE A". Exclude dari analisis. |

## ERD (Relasi Logik)

```
                         target_balai
                         (532 rows)
                              | soft join via mapping_komoditi + nama
                         coverage_balai
                         (668 rows)
                              | soft join via nama
                    mv_pemeriksaan (FACT)
                    (257.434 rows)
   +--------+--------+--------+--------+--------+--------+--------+
   |        |        |        |        |        |        |        |
   _log    _petugas _temuan _timeline _jenis   _kategori _kriteria
  (1.3M)   (581k)   (296k)  (288k)   _pangan  _temuan  (5.892)
                                   (67k)  (241k)
```
