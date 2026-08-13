# Lampiran — SQL Playbook (Semua Query Investigasi Siap Re-Run)

> Kumpulan semua query yang dipakai dalam analisis ini, dikelompokkan per tema.
> Jalankan dengan: `PGPASSWORD='p670V2GwB' psql -h localhost -p 5533 -U postgres -d pemeriksaan -c "<query>"`
> **Satu statement per call** (multi-statement ditolak oleh beberapa connector).

---

## A. Struktur & Schema

### A1. Inventory semua tabel + schema
```sql
SELECT table_schema, table_name FROM information_schema.tables
WHERE table_schema NOT IN ('pg_catalog','information_schema') ORDER BY 1,2;
```

### A2. Cek constraint (PK/FK) — harus 0
```sql
SELECT conrelid::regclass, conname, contype FROM pg_constraint
WHERE conrelid IN (SELECT oid FROM pg_class WHERE relnamespace IN
  (SELECT oid FROM pg_namespace WHERE nspname IN ('public','dimension')));
```

### A3. Cek index — harus 0
```sql
SELECT schemaname, tablename, indexname FROM pg_indexes
WHERE schemaname IN ('public','dimension');
```

### A4. Cek relkind (semua harus 'r' = regular table)
```sql
SELECT relname, relkind FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='public' AND relkind IN ('r','m','v');
```

### A5. Row count public vs dimension
```sql
SELECT 'public.mv_pemeriksaan' AS t, count(*) FROM public.mv_pemeriksaan
UNION ALL SELECT 'dimension.mv_pemeriksaan', count(*) FROM dimension.mv_pemeriksaan
UNION ALL SELECT 'public.mv_pemeriksaan_timeline', count(*) FROM public.mv_pemeriksaan_timeline
UNION ALL SELECT 'dimension.mv_pemeriksaan_timeline', count(*) FROM dimension.mv_pemeriksaan_timeline;
```

### A6. Dimension timeline = tabel referensi status (18 baris)
```sql
SELECT * FROM dimension.mv_pemeriksaan_timeline;
```

### A7. Sync pattern (semua identik = full-reload)
```sql
SELECT min(sync), max(sync), max(sync)-min(sync) FROM mv_pemeriksaan;
```

---

## B. Null Rate & Unique Count per Kolom

### B1. mv_pemeriksaan — identitas & waktu
```sql
SELECT 'nama_upt' kolom, count(*) FILTER(WHERE nama_upt IS NULL) nulls,
  count(DISTINCT nama_upt) unik FROM mv_pemeriksaan
UNION ALL SELECT 'tanggal_mulai', count(*) FILTER(WHERE tanggal_mulai IS NULL), count(DISTINCT tanggal_mulai) FROM mv_pemeriksaan
UNION ALL SELECT 'tanggal_selesai', count(*) FILTER(WHERE tanggal_selesai IS NULL), count(DISTINCT tanggal_selesai) FROM mv_pemeriksaan
UNION ALL SELECT 'grade', count(*) FILTER(WHERE grade IS NULL), count(DISTINCT grade) FROM mv_pemeriksaan;
```

### B2. Kolom kategorikal — distribusi
```sql
SELECT sarana, count(*) FROM mv_pemeriksaan GROUP BY 1 ORDER BY 2 DESC;
SELECT komoditi, count(*) FROM mv_pemeriksaan GROUP BY 1 ORDER BY 2 DESC;
SELECT kesimpulan, count(*) FROM mv_pemeriksaan GROUP BY 1 ORDER BY 2 DESC;
SELECT status, status_label, count(*) FROM mv_pemeriksaan GROUP BY 1,2 ORDER BY 3 DESC;
SELECT grade, count(*) FROM mv_pemeriksaan GROUP BY 1 ORDER BY 2 DESC;
SELECT tujuan_pemeriksaan, count(*) FROM mv_pemeriksaan GROUP BY 1 ORDER BY 2 DESC LIMIT 12;
```

---

## C. Workflow & Bottleneck

### C1. Funnel status terakhir per inspeksi
```sql
WITH last_status AS (
  SELECT DISTINCT ON (id_pemeriksaan) id_pemeriksaan, status, status_label
  FROM mv_pemeriksaan_log ORDER BY id_pemeriksaan, urutan_step DESC, created_at DESC
)
SELECT status, status_label, count(*), round(100.0*count(*)/sum(count(*)) over(),1)
FROM last_status GROUP BY 1,2 ORDER BY 3 DESC;
```

### C2. Durasi median per transisi
```sql
WITH step_dur AS (
  SELECT id_pemeriksaan, status, created_at,
    lag(created_at) OVER w AS prev_ts, lag(status) OVER w AS prev_status
  FROM mv_pemeriksaan_log WHERE created_at > '2000-01-01'
  WINDOW w AS (PARTITION BY id_pemeriksaan ORDER BY urutan_step, created_at)
)
SELECT prev_status || ' -> ' || status AS transisi, count(*) AS jml,
  round(percentile_cont(0.5) WITHIN GROUP (ORDER BY EXTRACT(epoch FROM created_at-prev_ts)/86400),1) AS median_hari
FROM step_dur WHERE prev_ts IS NOT NULL AND created_at > prev_ts
GROUP BY 1 HAVING count(*) >= 100 ORDER BY median_hari DESC;
```

### C3. Trend TMK per tahun
```sql
SELECT date_part('year',tanggal_mulai)::int AS tahun, count(*) AS jml,
  count(*) FILTER(WHERE kesimpulan='TMK') AS tmk,
  round(100.0*count(*) FILTER(WHERE kesimpulan='TMK')/count(*),1) AS pct_tmk
FROM mv_pemeriksaan WHERE tanggal_mulai BETWEEN '2020-01-01' AND '2026-12-31'
GROUP BY 1 ORDER BY 1;
```

---

## D. Korelasi & Peta Risiko

### D1. Grade ↔ temuan (korelasi)
```sql
SELECT p.grade,
  count(DISTINCT p.id) AS jml,
  count(DISTINCT t.id_pemeriksaan) AS punya_temuan,
  round(100.0*count(DISTINCT t.id_pemeriksaan)/count(DISTINCT p.id),1) AS pct_bertemuan
FROM mv_pemeriksaan p
LEFT JOIN (SELECT DISTINCT id_pemeriksaan FROM mv_pemeriksaan_temuan) t ON t.id_pemeriksaan=p.id
WHERE p.grade IN ('A','B','C') GROUP BY p.grade ORDER BY p.grade;
```

### D2. Hotspot RUTIN (kontrol tujuan)
```sql
SELECT provinsi, komoditi, jenis_sarana, count(*) AS total,
  count(*) FILTER(WHERE kesimpulan='TMK') AS tmk,
  round(100.0*count(*) FILTER(WHERE kesimpulan='TMK')/count(*),0) AS pct_tmk
FROM mv_pemeriksaan
WHERE kesimpulan IN ('MK','TMK') AND tujuan_pemeriksaan = 'PEMERIKSAAN RUTIN'
GROUP BY provinsi, komoditi, jenis_sarana HAVING count(*) >= 200
ORDER BY pct_tmk DESC LIMIT 20;
```

### D3. Residivis 100% TMK
```sql
SELECT upper(regexp_replace(nama_sarana,'[^a-zA-Z0-9 ]','','g')) AS sarana_norm, nama_upt,
  count(*) AS jml, count(*) FILTER(WHERE kesimpulan='TMK') AS tmk
FROM mv_pemeriksaan WHERE nama_sarana IS NOT NULL
GROUP BY 1,2 HAVING count(*) >= 8 AND round(100.0*count(*) FILTER(WHERE kesimpulan='TMK')/count(*),0) = 100
ORDER BY jml DESC;
```

---

## E. Target & Capaian

### E1. Capaian nasional per komoditi (TANPA fan-out)
```sql
WITH target_agg AS (
  SELECT komoditi, sum(target_pengawasan) AS target_nas
  FROM target_balai WHERE tahun=2024 AND target_pengawasan > 0 GROUP BY 1
),
realisasi_agg AS (
  SELECT upper(mapping_komoditi_target_balai) AS komoditi_map, count(*) AS realisasi
  FROM mv_pemeriksaan WHERE tanggal_mulai BETWEEN '2024-01-01' AND '2024-12-31'
    AND mapping_komoditi_target_balai IS NOT NULL GROUP BY 1
)
SELECT t.komoditi, t.target_nas, r.realisasi,
  round(100.0*r.realisasi/t.target_nas,1) AS pct_capai
FROM target_agg t LEFT JOIN realisasi_agg r ON upper(t.komoditi)=r.komoditi_map
ORDER BY pct_capai DESC NULLS LAST;
```

---

## F. Nilai Sitaan & Produk

### F1. Nilai bersih (minus outlier)
```sql
SELECT 'bruto' AS metrik, round(sum(tp_harga_total),0) AS nilai, count(*) FROM mv_pemeriksaan_temuan WHERE tp_harga_total IS NOT NULL
UNION ALL
SELECT 'bersih_<1M', round(sum(tp_harga_total),0), count(*) FROM mv_pemeriksaan_temuan WHERE tp_harga_total > 0 AND tp_harga_total < 1000000000;
```

### F2. Top produk tertemuan
```sql
SELECT product_name, count(*) AS jml, sum(tp_jml_temuan) AS unit, sum(tp_harga_total) AS nilai
FROM mv_pemeriksaan_temuan GROUP BY 1 ORDER BY count(*) DESC LIMIT 20;
```

### F3. Top negara asal
```sql
SELECT upper(trim(tp_negara)) AS negara, count(*) FROM mv_pemeriksaan_temuan
WHERE tp_negara IS NOT NULL GROUP BY 1 ORDER BY 2 DESC LIMIT 15;
```

---

## G. Kualitas Data & Anomali

### G1. Validasi 943 NULL (bukan batch migrasi)
```sql
SELECT min(id), max(id), max(id)-min(id) AS span,
  min(tanggal_input), max(tanggal_input),
  count(DISTINCT status), count(DISTINCT nama_upt)
FROM mv_pemeriksaan WHERE tanggal_mulai IS NULL AND tujuan_pemeriksaan IS NULL;
```

### G2. Orphan timeline
```sql
SELECT t.status, count(*) FROM mv_pemeriksaan_timeline t
WHERE NOT EXISTS (SELECT 1 FROM mv_pemeriksaan p WHERE p.id = t.id_pemeriksaan)
GROUP BY 1 ORDER BY 2 DESC;
```

### G3. Outlier tanggal
```sql
SELECT id, tanggal_mulai, nama_upt, nama_sarana, komoditi
FROM mv_pemeriksaan WHERE tanggal_mulai < '2010-01-01' OR tanggal_mulai > '2027-12-31'
ORDER BY tanggal_mulai LIMIT 20;
```

### G4. DEMO data
```sql
SELECT nama_upt, count(*) FROM mv_pemeriksaan
WHERE nama_upt ILIKE '%demo%' GROUP BY 1;
```

---

## H. Agg Fan-Out

### H1. Sum agg vs fact (harus 2×)
```sql
SELECT sum(jumlah_pemeriksaan) FROM mv_pemeriksaan_agg;
SELECT count(*) FROM mv_pemeriksaan;
```

### H2. Per-UPT/day mismatch
```sql
WITH a AS (SELECT nama_upt, tanggal_periode, sum(jumlah_pemeriksaan) n_agg
           FROM mv_pemeriksaan_agg WHERE periode_type='day' GROUP BY 1,2),
f AS (SELECT nama_upt, tanggal_mulai d, count(*) n_fact
      FROM mv_pemeriksaan WHERE tanggal_mulai IS NOT NULL GROUP BY 1,2)
SELECT count(*) FILTER(WHERE a.n_agg<>f.n_fact) AS hari_mismatch
FROM a LEFT JOIN f ON f.nama_upt=a.nama_upt AND f.d=a.tanggal_periode;
```

---

## I. Performa Balai

### I1. Ranking median durasi DRAFT→FINISHED
```sql
WITH d AS (
  SELECT id_pemeriksaan,
    min(created_at) FILTER (WHERE status='DRAFT') AS mulai,
    max(created_at) FILTER (WHERE status IN ('FINISHED','FINISHED_PUSAT')) AS selesai,
    max(nama_balai) AS balai
  FROM mv_pemeriksaan_log GROUP BY id_pemeriksaan
)
SELECT balai, count(*) FILTER(WHERE selesai IS NOT NULL) AS jml_selesai,
  round(percentile_cont(0.5) WITHIN GROUP (ORDER BY EXTRACT(epoch FROM selesai-mulai)/86400)) AS median_hari
FROM d WHERE selesai IS NOT NULL AND mulai IS NOT NULL
GROUP BY balai HAVING count(*) >= 100 ORDER BY median_hari DESC LIMIT 15;
```

---

## Catatan Penggunaan

- **Selalu pakai filter hygiene**: `tanggal_mulai >= '2015-01-01'`, `nama_upt NOT IN ('DEMO BALAI BESAR','DEMO TIPE A')`.
- **Jangan JOIN multi-tabel tanpa agregasi** (fan-out trap).
- **Hitung durasi dari LOG, bukan timeline** (timeline tercemar outlier).
- **Total dari FACT, bukan agg** (agg fan-out 2×).
- **Kontrol `tujuan_pemeriksaan`** saat membandingkan kepatuhan antar dimensi.
