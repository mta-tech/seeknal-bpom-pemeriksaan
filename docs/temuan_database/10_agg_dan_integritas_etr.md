# 10 — Agg & Integritas ETL

> `mv_pemeriksaan_agg` adalah rollup pre-computed yang **TIDAK boleh di-SUM langsung** — fan-out 2×.
> Plus analisis sync pattern dan implikasi ETL.

## 10.1 Struktur `mv_pemeriksaan_agg` (26 kolom)

| Kolom | Tipe | Catatan |
|---|---|---|
| `periode_type` | text | `day` (202.104 baris) atau `month` (164.696 baris) |
| `tanggal_periode` | date | Range: 0004-02-01 s/d 2027-07-27 (outlier!) |
| `nama_upt` | text | 91 distinct |
| `provinsi` | text | 34 distinct (35 NULL) |
| `kabupaten_kota` | text | |
| `sarana` | text | |
| `jenis_sarana` | text | |
| `legal` | text | |
| `tujuan_pemeriksaan` | text | |
| `komoditi` | text | |
| `kesimpulan` | text | MK, TMK, NULL, TTP, TDP, TMBB |
| `status` | text | |
| `jumlah_pemeriksaan` | bigint | **⚠️ FAN-OUT — lihat §10.2** |
| `jumlah_sarana_unik` | bigint | ✅ Aman untuk SUM |
| `total_critical_issue` | bigint | |
| `total_major_issue` | bigint | |
| `total_minor_issue` | bigint | |
| `avg_critical_issue` | double | |
| `avg_major_issue` | double | |
| `avg_minor_issue` | double | |
| `avg_day_input_mulai` | double | ⚠️ Tercemar outlier tanggal |
| `avg_day_input_selesai` | double | ⚠️ Tercemar |
| `avg_day_mulai_selesai` | double | ⚠️ Tercemar |
| `min_day_mulai_selesai` | bigint | |
| `max_day_mulai_selesai` | bigint | |
| `last_updated` | timestamp | 2026-08-11 22:56:52 (1 jam sebelum sync fact) |

## 10.2 ⚠️ FAN-OUT 2× — `jumlah_pemeriksaan` TIDAK BOLEH DI-SUM

```sql
SELECT sum(jumlah_pemeriksaan) FROM mv_pemeriksaan_agg;
-- Hasil: 513.026

SELECT count(*) FROM mv_pemeriksaan;
-- Hasil: 257.456
```

**513.026 ≈ 2 × 257.456.** Agg menggandakan fact!

### Mengapa terjadi?

`mv_pemeriksaan_agg` punya 366.800 baris untuk 257.456 inspeksi = **1,42 baris per inspeksi**.
Setiap inspeksi muncul di **multiple baris agg** karena dikelompokkan per kombinasi dimensi
(sarana, jenis_sarana, legal, tujuan, komoditi, kesimpulan, status).

### Per kesimpulan (buktinya):

```sql
SELECT kesimpulan, count(*) AS n_baris, sum(jumlah_pemeriksaan) AS n_sum
FROM mv_pemeriksaan_agg GROUP BY 1 ORDER BY n_sum DESC;
```

| kesimpulan | Baris agg | Sum agg | Fact seharusnya |
|---|---|---|---|
| MK | 241.707 | **353.556** | 241.707 (1,46×) |
| TMK | 117.239 | **150.772** | 117.239 (1,29×) |
| NULL | 3.609 | 4.004 | |
| TTP | 2.722 | 3.080 | |
| TDP | 1.497 | 1.578 | |
| TMBB | 26 | 36 | |

### Per-UPT/day mismatch:

```sql
-- 8.530 dari 56.814 hari-UPT combination mismatch (selisih total 23.740)
WITH a AS (SELECT nama_upt, tanggal_periode, sum(jumlah_pemeriksaan) n_agg
           FROM mv_pemeriksaan_agg WHERE periode_type='day' GROUP BY 1,2),
f AS (SELECT nama_upt, tanggal_mulai d, count(*) n_fact
      FROM mv_pemeriksaan WHERE tanggal_mulai IS NOT NULL GROUP BY 1,2)
SELECT count(*) FILTER(WHERE a.n_agg<>f.n_fact) AS hari_mismatch
FROM a LEFT JOIN f ON f.nama_upt=a.nama_upt AND f.d=a.tanggal_periode;
-- Hasil: 8.530
```

## 10.3 Implikasi

**Dashboard yang membaca `sum(jumlah_pemeriksaan)` dari agg akan menampilkan angka ~2× lipat.**

Yang AMAN dari agg:
- `sum(jumlah_sarana_unik)` — kolom ini sudah deduplicated di source
- `avg_*` — metrik rata-rata tidak terpengaruh fan-out (asalkan pembagi konsisten)
- Filter + GROUP BY spesifik (bukan total nasional)

Yang **TIDAK AMAN**:
- `sum(jumlah_pemeriksaan)` tanpa dedup → 2× lipat
- Total nasional dari agg → selalu overstated

**Rekomendasi**: Hitung total dari FACT (`mv_pemeriksaan`), bukan dari agg.
Agg hanya untuk breakdown dimensional yang sudah didefinisikan jelas.

## 10.4 Sync Pattern — Full-Reload

```sql
SELECT min(sync), max(sync), max(sync)-min(sync) FROM mv_pemeriksaan;
-- min: 2026-08-12 05:56:33.724077
-- max: 2026-08-12 05:56:33.724077
-- rentang: 00:00:00
```

**Semua record punya timestamp sync identik** → ETL melakukan **full-reload** (truncate + insert),
bukan incremental upsert.

**Konsekuensi:**
- Kolom `sync` **tidak berguna untuk CDC** — semua record tampak "diubah" bersamaan.
- Tidak ada cara mengetahui record mana yang berubah di refresh terakhir.
- `last_updated` di agg (22:56:52) lebih awal dari sync fact (05:56:33) → agg dihitung sebelum fact di-reload.

## 10.5 Konsistensi Total: agg vs fact (granularitas grand total)

```sql
-- agg: sum per periode_type
SELECT periode_type, count(*) AS n_rows, sum(jumlah_pemeriksaan) AS total
FROM mv_pemeriksaan_agg GROUP BY 1;
-- day:   202.104 baris, 256.513 total
-- month: 164.696 baris, 256.513 total
```

**256.513 vs fact 257.456 = selisih 943 = persis kohort NULL tanggal_mulai!**

Jadi agg KONSISTEN dengan fact pada level **grand total per periode_type** (karena agg hanya menghitung
record ber-tanggal). Tetapi pada level **per-UPT/day** atau **per-kombinasi dimensi**, terjadi fan-out.

**Inti**: agg di-build dari fact yang sudah exclude NULL tanggal, lalu di-federasi per kombinasi dimensi.
Total nasional cocok (selisih 943 = NULL), tapi SUM semua baris menggandakan karena fan-out dimensional.
