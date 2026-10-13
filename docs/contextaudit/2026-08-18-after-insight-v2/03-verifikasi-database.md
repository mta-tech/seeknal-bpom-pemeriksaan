# Verifikasi database — pemeriksaan

Dijalankan 18 Agustus 2026 ke database `pemeriksaan` via tunnel `localhost:5533`.

## 1. Kondisi tabel

| Tabel | Baris |
|---|---:|
| `mv_pemeriksaan` (fakta) | 257.607 |
| `mv_pemeriksaan_agg` | 367.048 |
| `mv_pemeriksaan_temuan` | 297.058 |
| `mv_pemeriksaan_timeline` | 288.335 |
| `mv_pemeriksaan_petugas` | 582.211 |
| `mv_pemeriksaan_log` | 1.312.259 |
| `mv_pemeriksaan_jenis_pangan` | 67.223 |
| `mv_kriteria_pemeriksaan` | 5.892 |
| `target_balai` · `coverage_balai` | 532 · 668 |

`max(sync)` = 2026-08-18 05:48.

## 2. Grain

```sql
SELECT count(*), count(DISTINCT id) FROM mv_pemeriksaan;   -- 257607 | 257607
```

`id` unik penuh — sesuai klaim `context/00-menghitung.md` §1. Kelas kegagalan entity yang
mendominasi domain pengawasan **tidak mungkin muncul di sini**.

## 3. Kolom `sarana` (GT `TC-PMR-RANK-SARANA-01`)

```sql
SELECT sarana, count(*) FROM mv_pemeriksaan
 WHERE sarana IS NOT NULL AND btrim(sarana)<>'' GROUP BY 1 ORDER BY 2 DESC;
-- DISTRIBUSI 141559 | PELAYANAN 72680 | PRODUKSI 43367
```

GT (14 Agu) 141.509 vs hari ini 141.559 → drift +50 baris. Jawaban agent (`PANGAN` 61.576) berasal
dari kolom **`jenis_sarana`**, bukan `sarana`.

## 4. `TC-PMR-VONIS-MK-TMK-01`

```sql
-- nama_upt ILIKE '%surabaya%' AND kesimpulan='TMK' AND tanggal_mulai dalam 2025
count(*)                    -- 455  (GT)
count(DISTINCT nama_sarana) -- 443  (jawaban agent)
```

## 5. `TC-PMR-TREN-HASIL-PEMERIKSAAN-02`

```sql
SELECT count(*) FROM mv_pemeriksaan
 WHERE sarana='PRODUKSI' AND komoditi='KOSMETIK' AND kesimpulan IN ('MK','TMK')
   AND tanggal_mulai>='2024-01-01' AND tanggal_mulai<'2025-01-01';  -- 471  (jawaban agent, BENAR)

SELECT count(*) FROM mv_pemeriksaan
 WHERE lower(sarana)='produksi'
   AND tanggal_mulai>='2024-01-01' AND tanggal_mulai<'2025-01-01';  -- 8062 (SQL di note GT)
```

`assert_any_of` testcase ini menuntut kata `'tidak ada'`/`'tidak ditemukan'` — tidak konsisten
dengan kedua angka di atas. Testcase-nya yang perlu diperbaiki.
