# 09 — Performa Balai & Petugas

> Ranking balai berdasarkan kecepatan, distribusi petugas, analisis peran.

## 9.1 Ranking Balai: Median Durasi DRAFT → FINISHED

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
GROUP BY balai HAVING count(*) >= 100 ORDER BY median_hari;
```

### Terlambat (median tertinggi)

| Balai | Selesai | Median (hari) |
|---|---|---|
| LOKA POM KAB. BONE | 114 | **396** |
| LOKA POM KAB. KARAWANG | 328 | 333 |
| LOKA POM KAB. ACEH TENGAH | 109 | 330 |
| DIREKTORAT PENGAWASAN OTSK | 15.440 | 329 |
| LOKA POM KOTAWARINGIN BARAT | 231 | 290 |
| LOKA POM LUBUKLINGGAU | 293 | 268 |
| LOKA POM MERAUKE | 115 | 230 |

### Tercepat

| Balai | Selesai | Median (hari) |
|---|---|---|
| LOKA POM KAB. TEGAL | 128 | **90** |
| DIREKTORAT PENGAWASAN KOSMETIK | 9.380 | 102 |
| LOKA POM TANAH BUMBU | 186 | 117 |
| LOKA POM REJANG LEBONG | 111 | 122 |
| LOKA POM ACEH SELATAN | 176 | 141 |

**Rentang 90-396 hari.** Bahkan tercepat (90 hari) masih lambat karena pipeline pusat (~67 hari).
Variasi balai daerah kecil dibanding bottleneck pusat — **lambat utamanya karena Jakarta, bukan daerah.**

## 9.2 Distribusi Petugas

```sql
SELECT count(DISTINCT petugas_id) AS total_petugas_unik,
  round(avg(c),1) AS avg_inspeksi_per_petugas, max(c) AS max_inspeksi
FROM (SELECT petugas_id, count(*) c FROM mv_pemeriksaan_petugas GROUP BY 1) x;
```

- **Total petugas unik**: 2.997 (dengan petugas_id valid)
- **Avg inspeksi per petugas**: ~194
- **Max**: 1.556 inspeksi (petugas superaktif)
- **216 baris** punya petugas_id NULL

### Ukuran Tim per Inspeksi

| Ukuran Tim | Inspeksi | % |
|---|---|---|
| 1 petugas | 15.583 | 6,1% |
| **2 petugas** | **194.860** | **75,7%** |
| 3 petugas | 25.541 | 9,9% |
| 4 petugas | 16.137 | 6,3% |
| 5 petugas | 1.632 | 0,6% |
| 6 petugas | 2.264 | 0,9% |
| 7+ petugas | ~2.000 | ~0,8% |

**75,7% inspeksi dilakukan oleh tim 2 orang** — standar BPOM.
Tim besar (6+) = inspeksi pabrik/gudang besar.

## 9.3 `jenis_id` — 25 Kode Peran (Tak Berkamus)

| jenis_id | Count | Tebakan peran (TIDAK terverifikasi) |
|---|---|---|
| 16 | 140.617 | ? (dominan — mungkin Petugas Lapangan) |
| 13 | 81.763 | ? |
| 109 | 60.104 | ? |
| 5 | 59.742 | ? |
| 107 | 43.471 | ? |
| 15 | 39.043 | ? |
| 108 | 22.450 | ? |
| 18 | 22.448 | ? |
| 10 | 22.134 | ? |
| 14 | 15.750 | ? |
| 105 | 14.847 | ? |
| 17 | 14.406 | ? |
| 106 | 10.349 | ? |
| 748 | 8.737 | ? |
| 747 | 7.127 | ? |
| 4-12 | ~20.000 | ? |
| **211265** | **26** | **❓ Kode 6-digit tak dikenal** |
| **211337** | **2** | **❓** |
| **223447** | **2** | **❓** |

**⚠️ TIDAK ADA kamus resmi untuk jenis_id.** Semua peran di atas adalah TEBAKAN.
3 kode 6-digit (211265, 211337, 223447) = kode tak dikenal. Bukan FK petugas_id (max < 100.000).
Kemungkinan ID dari tabel referensi yang tidak ada di DB ini.

**Perlu konfirmasi tim sumber**: Apa label resmi tiap jenis_id?

## 9.4 Aktor Log (Verifikator) — Populasi Berbeda dari Petugas

```sql
SELECT fullname, count(*) AS jml_aksi FROM mv_pemeriksaan_log GROUP BY 1 ORDER BY 2 DESC LIMIT 10;
```

Top aktor (verifikator/approver):
- Beragam nama individu, 2.063 distinct
- Paling aktif: ~19.619 aksi (Rizka Ayu Kusuma Widjanarko)

**Penting**: `fullname` di log = **verifikator/approver** (orang yang approve status workflow).
**BERBEDA** dari `petugas` di tabel petugas (= **pemeriksa lapangan**). Dua populasi orang berbeda.

## 9.5 Catatan Log (NLP Potensial)

Top catatan di log:
| Catatan | Count |
|---|---|
| Verifikasi Kepala Balai | 243.394 |
| Verifikasi Supervisor Pemdik Satu | 102.261 |
| ( "-" ) | 65.646 |
| ok | 32.384 |
| MK | 29.320 |
| Verifikasi Supervisor Pemdik Dua | 23.558 |
| MK Memenuhi Ketentuan | 16.206 |
| MK - Memenuhi Ketentuan | 14.747 |

Mayoritas catatan = label verifikasi standar. `catatan` free-text (207.850 distinct) = sumber NLP
untuk alasan revisi/penolakan.
