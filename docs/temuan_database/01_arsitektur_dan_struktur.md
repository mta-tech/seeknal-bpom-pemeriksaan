# 01 — Arsitektur & Struktur Database

> Database: `pemeriksaan` | Schema: `public` (11 tabel) + `dimension` (8 tabel) | Total: **19 tabel**

## 1.1 Inventory Tabel Lengkap

### Schema `public` (11 tabel — FACT + satelit + dimensi)

| # | Tabel | Baris (verified) | Kolom | Peran |
|---|---|---|---|---|
| 1 | `mv_pemeriksaan` | **257.456** | 31 | **FACT UTAMA** — 1 baris = 1 inspeksi |
| 2 | `mv_pemeriksaan_log` | **1.311.757** | 11 | Audit trail workflow (5,09 langkah/inspeksi) |
| 3 | `mv_pemeriksaan_petugas` | **581.864** | 11 | Tim pemeriksa (2,26 petugas/inspeksi) |
| 4 | `mv_pemeriksaan_temuan` | **296.981** | 18 | Produk temuan/sitaan |
| 5 | `mv_pemeriksaan_timeline` | **288.157** | 11 | Durasi per tahap pipeline |
| 6 | `mv_pemeriksaan_agg` | **366.800** | 26 | Pre-computed rollup (day + month) |
| 7 | `mv_pemeriksaan_jenis_pangan` | **48.511** | 4 | Exploded array jenis pangan |
| 8 | `mv_pemeriksaan_kategori_temuan` | **241.609** | 4 | Exploded array kategori temuan (49 nilai) |
| 9 | `mv_kriteria_pemeriksaan` | **5.892** | 12 | Checklist audit CPOB/CPKB |
| 10 | `coverage_balai` | **668** | 5 | Dimensi balai → kabupaten (84 balai) |
| 11 | `target_balai` | **532** | 12 | Target tahunan 2024 (76 balai × 7 komoditi) |

### Schema `dimension` (8 tabel — BUKAN mirror public)

| # | Tabel | Baris | Kolom | Peran sebenarnya |
|---|---|---|---|---|
| 1 | `mv_pemeriksaan` | 150.603 | 18 | Proyeksi dimensi murni (tanpa id/tanggal/measures) |
| 2 | `mv_pemeriksaan_log` | 194.015 | ~8 | Subset log (hanya 15% dari public) |
| 3 | `mv_pemeriksaan_petugas` | ~— | ~8 | Subset petugas |
| 4 | `mv_pemeriksaan_temuan` | 80.843 | ~12 | Subset temuan (hanya 27% dari public) |
| 5 | `mv_pemeriksaan_timeline` | **18** | **1** | **🆕 TABEL REFERENSI kode status** (bukan timeline!) |
| 6 | `mv_kriteria_pemeriksaan` | ~— | ~8 | Subset kriteria |
| 7 | `coverage_balai` | 513 | 2 | Subset coverage (tanpa id) |
| 8 | `target_balai` | ~— | ~8 | Subset target |

## 1.2 Constraint, Index, PK/FK — SEMUA NOL

```sql
SELECT conrelid::regclass, conname, contype FROM pg_constraint
WHERE conrelid IN (SELECT oid FROM pg_class WHERE relnamespace IN
  (SELECT oid FROM pg_namespace WHERE nspname IN ('public','dimension')));
-- Hasil: 0 rows
```

```sql
SELECT schemaname, tablename, indexname FROM pg_indexes
WHERE schemaname IN ('public','dimension');
-- Hasil: 0 rows
```

**Konsekuensi:**
- Tidak ada jaminan integritas referensial (FK) — orphan data bisa terjadi (dan terjadi: 30.699 orphan timeline).
- Tidak ada index — **semua query = full sequential scan**. Query besar bisa lambat atau gagal (shared memory).
- Tidak ada PK deklarasi — `id` di fact TIDAK dijamin unik oleh DB (meskipun verified unik secara empirik).
- Integritas harus dienforc oleh query logic, bukan DB constraint.

## 1.3 Penipuan Prefix `mv_` — Semua Tabel Fisik

```sql
SELECT relname, relkind FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='public' AND relkind IN ('r','m','v');
-- Hasil: SEMUA relkind='r' (regular table). Tidak ada 'm' (materialized view) atau 'v' (view).
```

**Interpretasi:** Prefix `mv_` menyiratkan "materialized view" — tetapi SEMUA tabel adalah regular table (`relkind='r'`).
Tidak ada `REFRESH MATERIALIZED VIEW`. Isi di-update oleh ETL eksternal lewat kolom `sync`.

## 1.4 `dimension` BUKAN Mirror `public` — Dua Hal Berbeda

Dokumen `context/data_architecture.md` yang ada menyebut dimension sebagai "snapshot lama, tidak dipakai."
Analisis mendalam membuktikan karakterisasinya lebih spesifik:

### Perbedaan struktur kolom

| Aspek | `public.mv_pemeriksaan` | `dimension.mv_pemeriksaan` |
|---|---|---|
| Kolom | **31** (lengkap) | **18** (subset) |
| `id` | ✅ ada (bigint PK empirik) | ❌ tidak ada |
| `tanggal_*` | ✅ input/mulai/selesai | ❌ tidak ada |
| `day_*` | ✅ 3 kolom durasi | ❌ tidak ada |
| `tx_*_issue` | ✅ critical/major/minor | ❌ tidak ada |
| `tl_saran_names` | ✅ array tindak lanjut | ❌ tidak ada |
| `mapping_komoditi_*` | ✅ bridge ke target | ❌ tidak ada |
| `sync` | ✅ timestamp ETL | ❌ tidak ada |
| Atribut deskriptif | ✅ | ✅ (nama_upt, sarana, komoditi, grade, dll) |

**Kesimpulan:** Dimension adalah **proyeksi dimensi murni** — hanya atribut deskriptif (untuk dimensi analitik),
tanpa key, timestamp, atau measures. Sesuai namanya secara harfiah: "dimension."

### Perbedaan row count (bukan timestamp-based)

| Tabel | public | dimension | % dari public |
|---|---|---|---|
| mv_pemeriksaan | 257.456 | 150.603 | 58% |
| mv_pemeriksaan_log | 1.311.757 | 194.015 | 15% |
| mv_pemeriksaan_temuan | 296.981 | 80.843 | 27% |
| mv_pemeriksaan_timeline | 288.157 | **18** | 0,006% |

Dimension BUKAN distinct projection juga: `SELECT COUNT(DISTINCT [18 kolom dimensi]) FROM public.mv_pemeriksaan` = 230.400 ≠ 150.603.

### 🆕 `dimension.mv_pemeriksaan_timeline` = TABEL REFERENSI STATUS

```sql
\d dimension.mv_pemeriksaan_timeline
-- Column | Type
-- status | text

SELECT * FROM dimension.mv_pemeriksaan_timeline;
-- 18 baris, 1 kolom:
-- 0, DRAFT, DRAFT_PUSAT, DRAFT_REVISE, DRAFT_PUSAT_REVISE,
-- VERIFY1, VERIFY2, VERIFY3, VERIFY4, VERIFY5, VERIFY6, VERIFY7,
-- VERIFY_P1, VERIFY_P2, VERIFY_P3,
-- FINISHED, FINISHED_PUSAT, NULL
```

Ini adalah **tabel referensi 18 kode status workflow** — bukan data timeline.
Penemuan ini melengkapi (bukan menggantikan) karakterisasi "snapshot lama" di dokumen context yang ada.

## 1.5 Sync Pattern — Full-Reload (Bukan Incremental)

```sql
SELECT min(sync), max(sync), max(sync)-min(sync) AS rentang FROM mv_pemeriksaan;
-- min: 2026-08-12 05:56:33.724077
-- max: 2026-08-12 05:56:33.724077
-- rentang: 00:00:00  ← SEMUA identik
```

**Semua 257.456 record punya timestamp sync yang persis sama** (hingga mikrodetik).

**Konsekuensi:**
- ETL melakukan **full-reload** (truncate + insert) setiap kali, bukan incremental upsert.
- Kolom `sync` **tidak berguna untuk change data capture (CDC)** — semua record tampak "diubah" bersamaan.
- Tidak ada cara untuk mengetahui kapan record individual terakhir diperbarui.
- `last_updated` di `mv_pemeriksaan_agg` = `2026-08-11 22:56:52` (1 jam lebih awal dari sync fact).

## 1.6 Inkonsistensi Nama Foreign Key

| Tabel anak | Kolom FK | Seharusnya konsisten? |
|---|---|---|
| `mv_pemeriksaan_log` | `id_pemeriksaan` | ✅ standar |
| `mv_pemeriksaan_petugas` | `id_pemeriksaan` | ✅ standar |
| `mv_pemeriksaan_temuan` | `id_pemeriksaan` | ✅ standar |
| `mv_pemeriksaan_timeline` | `id_pemeriksaan` | ✅ standar |
| `mv_pemeriksaan_jenis_pangan` | `id_pemeriksaan` | ✅ standar |
| `mv_pemeriksaan_kategori_temuan` | `id_pemeriksaan` | ✅ standar |
| **`mv_kriteria_pemeriksaan`** | **`pemeriksaan_id`** | ❌ **BERBEDA!** |

**`mv_kriteria_pemeriksaan`** menggunakan `pemeriksaan_id` (bukan `id_pemeriksaan`).
Siapa pun yang JOIN dengan asumsi konsistensi nama akan miss join.

## 1.7 Cakupan Waktu Data

```sql
SELECT min(tanggal_mulai), max(tanggal_mulai) FROM mv_pemeriksaan
WHERE tanggal_mulai BETWEEN '2000-01-01' AND '2030-01-01';
-- min: 2008-04-07  (outlier — lihat §11)
-- max: 2027-07-27  (outlier future — lihat §11)
```

Data signifikan dimulai **2020**. Distribusi per tahun:

| Tahun | Inspeksi | % | TMK % |
|---|---|---|---|
| 2020 | 29.761 | 11,6% | 37,1% |
| 2021 | 40.308 | 15,7% | 29,4% |
| 2022 | 46.293 | 18,0% | 30,5% |
| 2023 | 45.831 | 17,9% | 25,9% |
| 2024 | 48.006 | 18,7% | 24,1% |
| 2025 | 33.365 | 13,0% | 32,1% |
| 2026 | 12.865 | 5,0% | 32,8% |

Data 2026 partial (sampai Agustus). Lihat [05_workflow_dan_bottleneck.md](05_workflow_dan_bottleneck.md) untuk tren lengkap.

## 1.8 ERD Logis (Relasi Tanpa FK)

```
                          target_balai (532)
                          (soft join via mapping_komoditi + lower(nama_upt))
                          coverage_balai (668)
                          (soft join via lower(nama_upt))
                     mv_pemeriksaan (FACT — 257.456, 31 kolom)
   +----------+----------+----------+----------+----------+----------+
   |          |          |          |          |          |          |
   ▼          ▼          ▼          ▼          ▼          ▼          ▼
 _log      _petugas   _temuan   _timeline  _jenis     _kategori   _kriteria
(1.31M)   (581k)     (296k)    (288k)     _pangan    _temuan     (5.892)
1:N       1:N        1:N       1:1+orphan 1:N        1:N         1:N
id_pem    id_pem     id_pem    id_pem     id_pem     id_pem      PEMERIKSAAN_ID ← nama beda!

                     mv_pemeriksaan_agg (366k) — rollup, NO id, fan-out 2× (lihat bab 10)
```

**Tiga subgraf tersembunyi** (lihat [02_pemetaan_tabel_per_tabel.md](02_pemetaan_tabel_per_tabel.md) untuk detail):
1. **Proses administrasi**: fact → log → timeline → petugas (siapa, kapan, tahap apa)
2. **Hasil pengawasan produk**: fact → temuan → kategori_temuan → jenis_pangan (apa yang ilegal)
3. **Kepatuhan sarana**: fact → kriteria → (grade, tx_issue di fact) (seberapa patuh sarana)

Ketiganya hanya bertemu di `mv_pemeriksaan.id`. Tidak ada relasi langsung antar-subgraf.
