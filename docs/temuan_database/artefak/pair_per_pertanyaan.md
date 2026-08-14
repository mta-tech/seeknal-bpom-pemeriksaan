# Pair per Pertanyaan — database `pemeriksaan`

Setiap pasangan pertanyaan→SQL dari `context_stores` KAI, ditembakkan ke database live **2026-08-13**, lalu didiagnosis sebabnya. Total **213 pertanyaan**, **208 menghasilkan data (98%)**.

## Sebaran diagnosa

| Kode | Arti | Jumlah |
|---|---|--:|
| `OK_LANGSUNG` | ✅ Jalan apa adanya | 166 |
| `PULIH_RELASI_KOLOM` | 🔧 Pulih: relasi + kolom | 38 |
| `NOL_TIDAK_DITEMUKAN` | ○ Nol baris — pencarian teks tidak ketemu (jawaban sah) | 3 |
| `OK_TAPI_RAKSASA` | ⚠️ Jalan tapi >100rb baris tanpa agregasi | 3 |
| `NOL_KOLOM_PECAH` | 🔴 Nol baris — kolom lama pecah jadi dua di skema live | 2 |
| `PULIH_RELASI_KOLOM_NILAI` | 🔧 Pulih: relasi + kolom + nilai | 1 |

> Berkas pendamping: `pair_ringkas.csv` (tabel, satu baris per pertanyaan) dan `pair_detail_sql.csv` (SQL diratakan satu baris).

---

## Generasi v1 — koneksi awal (Jul 2025), SQL menunjuk view `vw_*`

45 pertanyaan.

### [1] "bagaimana riwayat pemeriksaan sarana alfamart dalam periode tahun 2024?"

| | |
|---|---|
| Bentuk NER | `"bagaimana riwayat pemeriksaan sarana <COMPANY NAME> dalam periode tahun <YEAR>?"` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 587 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom jenis_sarana→sarana ; kolom tujuan→tujuan_pemeriksaan |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT nama_sarana, lower(jenis_sarana), lower(komoditi), tujuan, kesimpulan, count(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND LOWER(nama_sarana) LIKE '%alfamart%' GROUP BY nama_sarana , lower(jenis_sarana) , lower(komoditi) , tujuan , kesimpulan
-- DIPAKAI: SELECT nama_sarana, lower(sarana), lower(komoditi), tujuan_pemeriksaan, kesimpulan, count(*) FROM mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND LOWER(nama_sarana) LIKE '%alfamart%' GROUP BY nama_sarana , lower(sarana) , lower(komoditi) , tujuan_pemeriksaan , kesimpulan
```

### [2] "bagaimana riwayat pemeriksaan sarana apotek kimia farma dalam periode tahun 2025?"

| | |
|---|---|
| Bentuk NER | `"bagaimana riwayat pemeriksaan sarana <FACILITY TYPE> <COMPANY NAME> dalam periode tahun <YEAR>?"` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: tidak |
| Status | ERR_SCHEMA → **OK** · 38 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT * FROM public.vw_pemeriksaan_bcc WHERE LOWER(nama_sarana) LIKE '%apotek kimia farma%' AND EXTRACT(YEAR FROM tgl_start) = 2025;
-- DIPAKAI: SELECT * FROM mv_pemeriksaan WHERE LOWER(nama_sarana) LIKE '%apotek kimia farma%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
```

### [3] "bagaimana tren data hasil pengawasan sarana obat tradisional; suplemen kesehatan; obat kuasi (profil hasil pengawasan) di upt balai besar pom di jakarta dalam periode tahun 2025?"

| | |
|---|---|
| Bentuk NER | `"bagaimana tren data hasil pengawasan sarana <COMMODITY NAME>; <COMMODITY NAME>; <COMMODITY NAME> (profil hasil pengawasan) di <FACILITY TYPE> di <CIT` |
| Tabel | `tanggal_selesai + mv_pemeriksaan` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 23 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_end→tanggal_selesai ; kolom nama_balai→nama_upt |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : select extract(month from tgl_end) as bulan, extract(year from tgl_end) as tahun, komoditi, count(*) as jumlah_pemeriksaan from vw_pemeriksaan_bcc where nama_balai = 'BALAI BESAR POM DI JAKARTA' and lower(komoditi) in ('obat tradisional', 'suplemen kesehatan','obat kuasi') and extract(year from tgl_end) = 2025 group by extract(month from tgl_end), extract(year from tgl_end), komoditi order by komoditi, extract(month 
-- DIPAKAI: select extract(month from tanggal_selesai) as bulan, extract(year from tanggal_selesai) as tahun, komoditi, count(*) as jumlah_pemeriksaan from mv_pemeriksaan where nama_upt = 'BALAI BESAR POM DI JAKARTA' and lower(komoditi) in ('obat tradisional', 'suplemen kesehatan','obat kuasi') and extract(year from tanggal_selesai) = 2025 group by extract(month from tanggal_selesai), extract(year from tanggal_selesai), komoditi
```

### [4] "bagaimana tren data hasil pengawasan sarana obat tradisional; suplemen kesehatan; obat kuasi dalam periode tahun 2025?"

| | |
|---|---|
| Bentuk NER | `"bagaimana tren data hasil pengawasan sarana obat tradisional; suplemen kesehatan; obat kuasi dalam periode tahun <YEAR>?"` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 12 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT EXTRACT(MONTH FROM tgl_start) AS month, COUNT(*) AS total FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY month ORDER BY month;
-- DIPAKAI: SELECT EXTRACT(MONTH FROM tanggal_mulai) AS month, COUNT(*) AS total FROM mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY month ORDER BY month;
```

### [5] "bagaimana tren data hasil pengawasan sarana produksi kosmetik yang memenuhi ketentuan dan tidak memenuhi ketentuan dalam periode tahun 2024?"

| | |
|---|---|
| Bentuk NER | `"bagaimana tren data hasil pengawasan sarana produksi kosmetik yang memenuhi ketentuan dan tidak memenuhi ketentuan dalam periode tahun <YEAR>?"` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 1 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom jenis_sarana→sarana |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(jenis_sarana) = 'produksi';
-- DIPAKAI: SELECT COUNT(*) FROM mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND lower(sarana) = 'produksi';
```

### [6] "bagaimana tren hasil pemeriksaan sarana peredaran sejak tahun 2025"

| | |
|---|---|
| Bentuk NER | `"bagaimana tren hasil pemeriksaan sarana peredaran sejak tahun <YEAR>"` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 3 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) >= 2025 GROUP BY tahun ORDER BY tahun;
-- DIPAKAI: SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, COUNT(*) AS jumlah FROM mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) >= 2025 GROUP BY tahun ORDER BY tahun;
```

### [7] "bagaimana tren hasil pemeriksaan sarana produksi md dan pirt sejak tahun 2024 hingga 2025?"

| | |
|---|---|
| Bentuk NER | `"bagaimana tren hasil pemeriksaan <FACILITY TYPE> md dan pirt sejak tahun <YEAR> hingga <YEAR>?"` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: ya |
| Status | ERR_SCHEMA → **NOL_BARIS** · 0 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom jenis_sarana→sarana ; kolom klasifikasi→komoditi |
| Diagnosa | **○ Nol baris — pencarian teks tidak ketemu (jawaban sah)** |
| Sebab | Pencarian teks bebas tidak menemukan padanan — nol baris adalah jawaban ("tidak ditemukan"), bukan kegagalan |

```sql
-- ASLI   : SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, kesimpulan, klasifikasi, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) BETWEEN 2024 AND 2025 AND lower(jenis_sarana) ILIKE '%produksi%' AND (klasifikasi ILIKE '%MD%' OR klasifikasi ILIKE '%IRT%') GROUP BY EXTRACT(YEAR FROM tgl_start), kesimpulan, klasifikasi ORDER BY tahun, kesimpulan, klasifikasi;
-- DIPAKAI: SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, kesimpulan, komoditi, COUNT(*) AS jumlah FROM mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) BETWEEN 2024 AND 2025 AND lower(sarana) ILIKE '%produksi%' AND (komoditi ILIKE '%MD%' OR komoditi ILIKE '%IRT%') GROUP BY EXTRACT(YEAR FROM tanggal_mulai), kesimpulan, komoditi ORDER BY tahun, kesimpulan, komoditi;
```

### [8] "bagaimana tren hasil pemeriksaan sarana produksi md jenis pangan garam, tepung, lemak dan minyak nabati sejak tahun 2020?"

| | |
|---|---|
| Bentuk NER | `"bagaimana tren hasil pemeriksaan <FACILITY TYPE> md jenis pangan <COMMODITY NAME>, <COMMODITY NAME>, <COMMODITY NAME> dan <COMMODITY NAME> sejak tahu` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: ya |
| Status | ERR_SCHEMA → **NOL_BARIS** · 0 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom jenis_sarana→sarana ; kolom klasifikasi→komoditi |
| Diagnosa | **○ Nol baris — pencarian teks tidak ketemu (jawaban sah)** |
| Sebab | Pencarian teks bebas tidak menemukan padanan — nol baris adalah jawaban ("tidak ditemukan"), bukan kegagalan |

```sql
-- ASLI   : SELECT komoditi, EXTRACT(YEAR FROM tgl_start), kesimpulan, count(*) FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) like 'produksi' AND lower(klasifikasi) LIKE '%md%' GROUP BY 1, 2, 3 ORDER BY count(*) DESC
-- DIPAKAI: SELECT komoditi, EXTRACT(YEAR FROM tanggal_mulai), kesimpulan, count(*) FROM mv_pemeriksaan WHERE lower(sarana) like 'produksi' AND lower(komoditi) LIKE '%md%' GROUP BY 1, 2, 3 ORDER BY count(*) DESC
```

### [9] "berapa total sarana yang tutup dan/atau tidak berproduksi saat diperiksa di tahun 2025 di wilayah kerja jakarta utara?"

| | |
|---|---|
| Bentuk NER | `"berapa total sarana yang tutup dan/atau tidak berproduksi saat diperiksa di tahun <YEAR> di wilayah kerja <CITY NAME>?"` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 1 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom kabupaten→kabupaten_kota ; kolom jenis_sarana→sarana |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT count(*) FROM vw_pemeriksaan_bcc WHERE kesimpulan = 'TTP' AND lower(jenis_sarana) like 'produksi' AND EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(kabupaten) LIKE '%jakarta utara%'
-- DIPAKAI: SELECT count(*) FROM mv_pemeriksaan WHERE kesimpulan = 'TTP' AND lower(sarana) like 'produksi' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(kabupaten_kota) LIKE '%jakarta utara%'
```

### [10] "dari seluruh upt, sarana produksi md dengan jenis pangan apa yang paling banyak tmk di tahun 2025?"

| | |
|---|---|
| Bentuk NER | `"dari seluruh upt, sarana produksi md dengan jenis pangan apa yang paling banyak tmk di tahun <YEAR>?"` |
| Tabel | `mv_pemeriksaan` · agregasi: ya |
| Status | ERR_SCHEMA → **NOL_BARIS** · 0 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom jenis_sarana→sarana ; kolom klasifikasi→komoditi |
| Diagnosa | **○ Nol baris — pencarian teks tidak ketemu (jawaban sah)** |
| Sebab | Pencarian teks bebas tidak menemukan padanan — nol baris adalah jawaban ("tidak ditemukan"), bukan kegagalan |

```sql
-- ASLI   : SELECT nama_sarana, komoditi, count(*) FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) like 'produksi' AND kesimpulan = 'TMK' AND lower(klasifikasi) LIKE '%md%' GROUP BY nama_sarana, komoditi ORDER BY count(*) DESC LIMIT 5
-- DIPAKAI: SELECT nama_sarana, komoditi, count(*) FROM mv_pemeriksaan WHERE lower(sarana) like 'produksi' AND kesimpulan = 'TMK' AND lower(komoditi) LIKE '%md%' GROUP BY nama_sarana, komoditi ORDER BY count(*) DESC LIMIT 5
```

### [11] "merekap jumlah dan nama sarana distribusi dan pelayanan yang belum pernah diperiksa dalam kurun waktu 1 tahun terakhir"

| | |
|---|---|
| Bentuk NER | `"merekap jumlah dan nama sarana distribusi dan pelayanan yang belum pernah diperiksa dalam kurun waktu <YEAR>"` |
| Tabel | `mv_pemeriksaan` · agregasi: tidak |
| Status | ERR_SCHEMA → **OK** · 214,166 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom jenis_sarana→sarana |
| Diagnosa | **⚠️ Jalan tapi >100rb baris tanpa agregasi** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live. TAPI hasilnya 214,166 baris tanpa agregasi — jalan, bukan jawaban |

```sql
-- ASLI   : SELECT nama_sarana, jenis_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) IN ('distribusi', 'pelayanan') AND nama_sarana NOT IN ( SELECT DISTINCT nama_sarana FROM vw_pemeriksaan_bcc WHERE tgl_start = tgl_start - interval '1 year' );
-- DIPAKAI: SELECT nama_sarana, sarana FROM mv_pemeriksaan WHERE lower(sarana) IN ('distribusi', 'pelayanan') AND nama_sarana NOT IN ( SELECT DISTINCT nama_sarana FROM mv_pemeriksaan WHERE tanggal_mulai = tanggal_mulai - interval '1 year' );
```

### [12] "sarana distribusi apa saja yang pernah memiliki riwayat memenuhi ketentuan berdasarkan tahun temuannya?"

| | |
|---|---|
| Bentuk NER | `"sarana distribusi apa saja yang pernah memiliki riwayat memenuhi ketentuan berdasarkan tahun temuannya?"` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: tidak |
| Status | ERR_SCHEMA → **OK** · 88,734 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom jenis_sarana→sarana |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT nama_sarana, EXTRACT(YEAR FROM tgl_start) AS tahun_temuan FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE '%distribusi%' AND kesimpulan = 'MK' GROUP BY nama_sarana, tahun_temuan;
-- DIPAKAI: SELECT nama_sarana, EXTRACT(YEAR FROM tanggal_mulai) AS tahun_temuan FROM mv_pemeriksaan WHERE lower(sarana) LIKE '%distribusi%' AND kesimpulan = 'MK' GROUP BY nama_sarana, tahun_temuan;
```

### [13] "sarana distribusi apa saja yang pernah memiliki riwayat tidak memenuhi ketentuan berdasarkan tahun temuannya?"

| | |
|---|---|
| Bentuk NER | `"sarana distribusi apa saja yang pernah memiliki riwayat tidak memenuhi ketentuan berdasarkan tahun temuannya?"` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: tidak |
| Status | ERR_SCHEMA → **OK** · 35,146 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom jenis_sarana→sarana |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT DISTINCT nama_sarana, EXTRACT(YEAR FROM tgl_start) AS tahun_temuan FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND kesimpulan LIKE 'TMK' GROUP BY nama_sarana, tahun_temuan;
-- DIPAKAI: SELECT DISTINCT nama_sarana, EXTRACT(YEAR FROM tanggal_mulai) AS tahun_temuan FROM mv_pemeriksaan WHERE lower(sarana) LIKE 'distribusi' AND kesimpulan LIKE 'TMK' GROUP BY nama_sarana, tahun_temuan;
```

### [14] "sarana distribusi kosmetik apa saja yang pernah diperiksa oleh badan pom setiap tahun dari tahun 2020 hingga 2024?"

| | |
|---|---|
| Bentuk NER | `"<FACILITY TYPE> apa saja yang pernah diperiksa oleh badan pom setiap tahun dari tahun <YEAR> hingga <YEAR>?"` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: tidak |
| Status | ERR_SCHEMA → **OK** · 96,777 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom jenis_sarana→sarana |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, nama_sarana FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) BETWEEN 2020 AND 2024 AND lower(jenis_sarana) LIKE '%distribusi%' GROUP BY tahun, nama_sarana ORDER BY tahun, nama_sarana;
-- DIPAKAI: SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, nama_sarana FROM mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) BETWEEN 2020 AND 2024 AND lower(sarana) LIKE '%distribusi%' GROUP BY tahun, nama_sarana ORDER BY tahun, nama_sarana;
```

### [15] "sarana distribusi kosmetik apa saja yang pernah diperiksa oleh badan pom?"

| | |
|---|---|
| Bentuk NER | `"<FACILITY TYPE> apa saja yang pernah diperiksa oleh <COMPANY NAME>?"` |
| Tabel | `mv_pemeriksaan` · agregasi: tidak |
| Status | ERR_SCHEMA → **OK** · 24,259 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom jenis_sarana→sarana |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND lower(komoditi) LIKE 'kosmetik' GROUP BY nama_sarana;
-- DIPAKAI: SELECT nama_sarana FROM mv_pemeriksaan WHERE lower(sarana) LIKE 'distribusi' AND lower(komoditi) LIKE 'kosmetik' GROUP BY nama_sarana;
```

### [16] "sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang belum dilakukan pemeriksaan dalam periode 2 tahun terakhir?"

| | |
|---|---|
| Bentuk NER | `"<FACILITY TYPE>; <COMMODITY NAME>; <COMMODITY NAME> apa saja yang belum dilakukan pemeriksaan dalam periode 2 tahun terakhir?"` |
| Tabel | `mv_pemeriksaan` · agregasi: tidak |
| Status | ERR_SCHEMA → **OK** · 44,013 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_end→tanggal_selesai |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(komoditi) IN ('obat tradisional', 'suplemen kesehatan', 'obat') AND tgl_end < NOW() - INTERVAL '2 year' GROUP BY nama_sarana;
-- DIPAKAI: SELECT nama_sarana FROM mv_pemeriksaan WHERE lower(komoditi) IN ('obat tradisional', 'suplemen kesehatan', 'obat') AND tanggal_selesai < NOW() - INTERVAL '2 year' GROUP BY nama_sarana;
```

### [17] "sarana produksi kosmetik apa saja yang memiliki riwayat pemeriksaan tidak memenuhi ketentuan dalam periode tahun 2024?"

| | |
|---|---|
| Bentuk NER | `"<FACILITY TYPE> apa saja yang memiliki riwayat pemeriksaan tidak memenuhi ketentuan dalam periode tahun <YEAR>?"` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: tidak |
| Status | ERR_SCHEMA → **OK** · 2,393 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom jenis_sarana→sarana |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(jenis_sarana) ILIKE 'produksi' AND kesimpulan = 'TMK';
-- DIPAKAI: SELECT nama_sarana FROM mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND lower(sarana) ILIKE 'produksi' AND kesimpulan = 'TMK';
```

### [18] "sarana produksi md apa yang paling sering memiliki riwayat tmk?"

| | |
|---|---|
| Bentuk NER | `"<FACILITY TYPE> md apa yang paling sering memiliki riwayat tmk?"` |
| Tabel | `mv_pemeriksaan` · agregasi: ya |
| Status | ERR_SCHEMA → **NOL_BARIS** · 0 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom jenis_sarana→sarana ; kolom klasifikasi→komoditi |
| Diagnosa | **🔴 Nol baris — kolom lama pecah jadi dua di skema live** |
| Sebab | Penanda MD/IRT ada di jenis_sarana, bukan komoditi — kolom lama `klasifikasi` pecah jadi dua di skema live |

```sql
-- ASLI   : SELECT nama_sarana, count(*) FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE '%produksi%' AND kesimpulan = 'TMK' AND klasifikasi LIKE '%MD%' GROUP BY nama_sarana ORDER BY COUNT(*) DESC LIMIT 5;
-- DIPAKAI: SELECT nama_sarana, count(*) FROM mv_pemeriksaan WHERE lower(sarana) LIKE '%produksi%' AND kesimpulan = 'TMK' AND komoditi LIKE '%MD%' GROUP BY nama_sarana ORDER BY COUNT(*) DESC LIMIT 5;
```

### [19] "tampilkan daftar sarana dengan hasil tmk berulang lebih dari sekali pada kurun 5 tahun terakhir hingga saat ini pada wilayah kerja balai pom di tangerang"

| | |
|---|---|
| Bentuk NER | `"tampilkan daftar sarana dengan hasil tmk berulang lebih dari sekali pada kurun 5 tahun terakhir hingga saat ini pada wilayah kerja balai pom di <REGE` |
| Tabel | `mv_pemeriksaan` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 96 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom nama_balai→nama_upt |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT nama_sarana, count(*) FROM vw_pemeriksaan_bcc WHERE kesimpulan = 'TMK' AND lower(nama_balai) LIKE '%tangerang%' AND tgl_start >= '2020-07-29' GROUP BY nama_sarana HAVING COUNT(*) > 1 ORDER BY 2 DESC;
-- DIPAKAI: SELECT nama_sarana, count(*) FROM mv_pemeriksaan WHERE kesimpulan = 'TMK' AND lower(nama_upt) LIKE '%tangerang%' AND tanggal_mulai >= '2020-07-29' GROUP BY nama_sarana HAVING COUNT(*) > 1 ORDER BY 2 DESC;
```

### [20] "tampilkan data persentase pirt yang aman dan bermutu selama periode 2025"

| | |
|---|---|
| Bentuk NER | `"tampilkan data persentase pirt yang aman dan bermutu selama periode <YEAR>"` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 1 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT CAST(SUM(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE 0 END) AS FLOAT) * 100 / COUNT(*) AS percentage_mk FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025;
-- DIPAKAI: SELECT CAST(SUM(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE 0 END) AS FLOAT) * 100 / COUNT(*) AS percentage_mk FROM mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025;
```

### [21] "tampilkan data profil jenis sarana yang sudah dilakukan pemeriksaan dari tahun 2025"

| | |
|---|---|
| Bentuk NER | `"tampilkan data profil jenis <FACILITY TYPE> yang sudah dilakukan pemeriksaan dari tahun <YEAR>"` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 3 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom jenis_sarana→sarana |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT jenis_sarana , count(*) FROM vw_pemeriksaan_bcc vpb WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY 1 LIMIT 5;
-- DIPAKAI: SELECT sarana , count(*) FROM mv_pemeriksaan vpb WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY 1 LIMIT 5;
```

### [22] "tampilkan jumlah dan nama sarana distribusi dan pelayanan yang mk/tmk masing-masing upt pada tahun 2025."

| | |
|---|---|
| Bentuk NER | `"tampilkan jumlah dan nama sarana distribusi dan pelayanan yang mk/tmk masing-masing upt pada tahun <YEAR>."` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 4 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom jenis_sarana→sarana |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT lower(jenis_sarana), kesimpulan, COUNT(nama_sarana) FROM public.vw_pemeriksaan_bcc WHERE lower(jenis_sarana) IN ('distribusi', 'pelayanan') AND kesimpulan IN ('MK', 'TMK') AND EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY lower(jenis_sarana), kesimpulan;
-- DIPAKAI: SELECT lower(sarana), kesimpulan, COUNT(nama_sarana) FROM mv_pemeriksaan WHERE lower(sarana) IN ('distribusi', 'pelayanan') AND kesimpulan IN ('MK', 'TMK') AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY lower(sarana), kesimpulan;
```

### [23] "tampilkan jumlah sarana produksi kategori mk dan tmk per komoditi, periode, wilayah, dan cakupan upt."

| | |
|---|---|
| Bentuk NER | `"tampilkan jumlah <FACILITY TYPE> kategori <CLASSIFICATION> dan <CLASSIFICATION> per <COMMODITY NAME>, periode, wilayah, dan cakupan upt."` |
| Tabel | `mv_pemeriksaan` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 29,909 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom nama_balai→nama_upt ; kolom jenis_sarana→sarana |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT lower(komoditi), DATE(tgl_start) AS periode, provinsi, nama_balai, kesimpulan, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE '%produksi%' GROUP BY lower(komoditi), periode, provinsi, nama_balai, kesimpulan
-- DIPAKAI: SELECT lower(komoditi), DATE(tanggal_mulai) AS periode, provinsi, nama_upt, kesimpulan, COUNT(*) AS jumlah FROM mv_pemeriksaan WHERE lower(sarana) LIKE '%produksi%' GROUP BY lower(komoditi), periode, provinsi, nama_upt, kesimpulan
```

### [24] "tampilkan jumlah sarana yang tidak dapat diperiksa di wilayah upt surabaya dan pada tahun 2025"

| | |
|---|---|
| Bentuk NER | `"tampilkan jumlah sarana yang tidak dapat diperiksa di wilayah upt <CITY NAME> dan pada tahun <YEAR>"` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 1 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom nama_balai→nama_upt |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT nama_balai, count(*) FROM vw_pemeriksaan_bcc vpb WHERE lower(nama_balai) LIKE '%surabaya%' AND EXTRACT(YEAR FROM tgl_start) = 2025 AND kesimpulan LIKE 'TDP' GROUP BY 1
-- DIPAKAI: SELECT nama_upt, count(*) FROM mv_pemeriksaan vpb WHERE lower(nama_upt) LIKE '%surabaya%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND kesimpulan LIKE 'TDP' GROUP BY 1
```

### [25] "tampilkan jumlah sarana yang tidak memenuhi ketentuan di wilayah upt surabaya dan pada tahun 2025"

| | |
|---|---|
| Bentuk NER | `"tampilkan jumlah sarana yang tidak memenuhi ketentuan di wilayah upt <CITY NAME> dan pada tahun <YEAR>"` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 1 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom nama_balai→nama_upt |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT nama_balai, count(*) FROM vw_pemeriksaan_bcc vpb WHERE lower(nama_balai) LIKE '%surabaya%' AND EXTRACT(YEAR FROM tgl_start) = 2025 AND kesimpulan LIKE 'TMK' GROUP BY 1
-- DIPAKAI: SELECT nama_upt, count(*) FROM mv_pemeriksaan vpb WHERE lower(nama_upt) LIKE '%surabaya%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND kesimpulan LIKE 'TMK' GROUP BY 1
```

### [26] "tampilkan persebaran pemeriksaan sarana di kab/kota wilayah kerja upt pada tahun 2025."

| | |
|---|---|
| Bentuk NER | `"tampilkan persebaran pemeriksaan sarana di kab/kota wilayah kerja upt pada tahun <YEAR>."` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 1,601 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom nama_balai→nama_upt |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT nama_balai, nama_sarana, count(*) FROM vw_pemeriksaan_bcc vpb WHERE lower(nama_balai) LIKE '%bandung%' AND EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY 1, 2;
-- DIPAKAI: SELECT nama_upt, nama_sarana, count(*) FROM mv_pemeriksaan vpb WHERE lower(nama_upt) LIKE '%bandung%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY 1, 2;
```

### [27] "tampilkan persentase mk tmk hasil pemeriksaan sarana pangan olahan md untuk tujuan pemeriksaan pemeriksaan rutin dari seluruh upt di tahun 2025 dalam bentuk diagram batang"

| | |
|---|---|
| Bentuk NER | `"tampilkan persentase mk tmk hasil pemeriksaan <FACILITY TYPE> untuk tujuan pemeriksaan <PURPOSE TYPE> dari seluruh upt di tahun <YEAR> dalam bentuk d` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 1 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom jenis_sarana→sarana ; kolom tujuan→tujuan_pemeriksaan |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT SUM(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS percentage_mk, SUM(CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS percentage_tmk FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(tujuan) like 'pemeriksaan rutin' AND lower(jenis_sarana) like 'produksi';
-- DIPAKAI: SELECT SUM(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS percentage_mk, SUM(CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS percentage_tmk FROM mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(tujuan_pemeriksaan) like 'pemeriksaan rutin' AND lower(sarana) like 'produksi';
```

### [28] "tampilkan profil pemeriksaan sarana produksi obat dan makanan selama periode 2025 dalam bentuk tabel dan grafik jumlah sarana produksi mk, tmk, tidak dapat dinilai, tutup per jenis komoditi (obat, ob

| | |
|---|---|
| Bentuk NER | `"tampilkan profil pemeriksaan <FACILITY TYPE> selama periode <YEAR> dalam bentuk tabel dan grafik jumlah sarana produksi <CLASSIFICATION>, <CLASSIFICA` |
| Tabel | `mv_pemeriksaan + tanggal_selesai` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 20 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_end→tanggal_selesai ; nilai 'Kosmetik'→'KOSMETIK' ; nilai 'Obat'→'OBAT' ; nilai 'Produk Pangan'→'PRODUK PANGAN' ; nilai 'Suplemen Kesehatan'→'SUPLEMEN KESEHATAN' |
| Diagnosa | **🔧 Pulih: relasi + kolom + nilai** |
| Sebab | Pulih setelah penyesuaian relasi + kolom + nilai ke skema live |

```sql
-- ASLI   : SELECT komoditi, kesimpulan, COUNT(*) AS jumlah_pemeriksaan FROM vw_pemeriksaan_bcc where kesimpulan != 'Null' and extract(year from tgl_end) = 2025 and komoditi in ('OBAT', 'KOSMETIK', 'SUPLEMEN KESEHATAN', 'PRODUK Pangan') GROUP BY komoditi, kesimpulan ORDER BY komoditi, kesimpulan
-- DIPAKAI: SELECT komoditi, kesimpulan, COUNT(*) AS jumlah_pemeriksaan FROM mv_pemeriksaan where kesimpulan != 'Null' and extract(year from tanggal_selesai) = 2025 and komoditi in ('OBAT', 'KOSMETIK', 'SUPLEMEN KESEHATAN', 'PRODUK PANGAN') GROUP BY komoditi, kesimpulan ORDER BY komoditi, kesimpulan
```

### [29] "tampilkan riwayat pemeriksaan sarana produksi 'nida food' pada rentang tahun yang tersedia."

| | |
|---|---|
| Bentuk NER | `"tampilkan riwayat pemeriksaan sarana produksi '<COMPANY NAME>' pada rentang tahun yang tersedia."` |
| Tabel | `mv_pemeriksaan` · agregasi: tidak |
| Status | ERR_SCHEMA → **OK** · 2 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom jenis_sarana→sarana |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT * FROM vw_pemeriksaan_bcc WHERE LOWER(nama_sarana) LIKE '%nida food%' AND lower(jenis_sarana) LIKE '%produksi%'
-- DIPAKAI: SELECT * FROM mv_pemeriksaan WHERE LOWER(nama_sarana) LIKE '%nida food%' AND lower(sarana) LIKE '%produksi%'
```

### [30] "tampilkan sarana distribusi dan pelayanan yang tutup pada periode tahun 2025"

| | |
|---|---|
| Bentuk NER | `"tampilkan sarana distribusi dan pelayanan yang tutup pada periode tahun <YEAR>"` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: tidak |
| Status | ERR_SCHEMA → **OK** · 79 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom jenis_sarana→sarana |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(jenis_sarana) IN ('distribusi', 'Pelayanan') AND kesimpulan = 'TTP'
-- DIPAKAI: SELECT nama_sarana FROM mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(sarana) IN ('distribusi', 'Pelayanan') AND kesimpulan = 'TTP'
```

### [31] "tampilkan sarana peredaran yang memiliki riwayat hasil tmk terbanyak di upt dengan nama balai pom di jakarta".

| | |
|---|---|
| Bentuk NER | `"tampilkan sarana peredaran yang memiliki riwayat hasil tmk terbanyak di upt dengan nama <HALL NAME> di <CITY NAME>".` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 233 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom nama_balai→nama_upt ; kolom jenis_sarana→sarana |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT nama_sarana , count(*) FROM vw_pemeriksaan_bcc vpb WHERE lower(nama_balai) LIKE '%jakarta%' AND EXTRACT(YEAR FROM tgl_start) = 2025 AND kesimpulan LIKE 'TMK' AND lower(jenis_sarana) LIKE 'distribusi' GROUP BY 1 ORDER BY 2 DESC
-- DIPAKAI: SELECT nama_sarana , count(*) FROM mv_pemeriksaan vpb WHERE lower(nama_upt) LIKE '%jakarta%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND kesimpulan LIKE 'TMK' AND lower(sarana) LIKE 'distribusi' GROUP BY 1 ORDER BY 2 DESC
```

### [32] "upt mana saja yang paling banyak melaporkan hasil pemeriksaan sarana produksi yang tmk?"

| | |
|---|---|
| Bentuk NER | `"upt mana saja yang paling banyak melaporkan hasil pemeriksaan <FACILITY TYPE> yang tmk?"` |
| Tabel | `mv_pemeriksaan` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 5 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom nama_balai→nama_upt ; kolom jenis_sarana→sarana |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT nama_balai, count(*) FROM vw_pemeriksaan_bcc WHERE kesimpulan = 'TMK' AND lower(jenis_sarana) like 'produksi' GROUP BY nama_balai ORDER BY COUNT(*) DESC LIMIT 5
-- DIPAKAI: SELECT nama_upt, count(*) FROM mv_pemeriksaan WHERE kesimpulan = 'TMK' AND lower(sarana) like 'produksi' GROUP BY nama_upt ORDER BY COUNT(*) DESC LIMIT 5
```

### [33] "upt manakah yang hasil pemeriksaan tmk sarana produksi md nya paling banyak di tahun 2025?"

| | |
|---|---|
| Bentuk NER | `"upt manakah yang hasil pemeriksaan tmk sarana produksi md nya paling banyak di tahun <YEAR>?"` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | ERR_SCHEMA → **NOL_BARIS** · 0 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom nama_balai→nama_upt ; kolom jenis_sarana→sarana ; kolom klasifikasi→komoditi |
| Diagnosa | **🔴 Nol baris — kolom lama pecah jadi dua di skema live** |
| Sebab | Penanda MD/IRT ada di jenis_sarana, bukan komoditi — kolom lama `klasifikasi` pecah jadi dua di skema live |

```sql
-- ASLI   : SELECT nama_balai, count(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND kesimpulan = 'TMK' AND lower(jenis_sarana) like 'produksi' AND klasifikasi LIKE '%MD%' GROUP BY nama_balai ORDER BY COUNT(*) DESC LIMIT 5;
-- DIPAKAI: SELECT nama_upt, count(*) FROM mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND kesimpulan = 'TMK' AND lower(sarana) like 'produksi' AND komoditi LIKE '%MD%' GROUP BY nama_upt ORDER BY COUNT(*) DESC LIMIT 5;
```

### [34] "upt manakah yang hasil pemeriksaannya memiliki perserntase tmk terbanyak pada tahun 2025"

| | |
|---|---|
| Bentuk NER | `"upt manakah yang hasil pemeriksaannya memiliki perserntase tmk terbanyak pada tahun <YEAR>"` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 1 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom nama_balai→nama_upt |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT nama_balai, count(*) as jumlah_tmk FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND kesimpulan = 'TMK' GROUP BY nama_balai ORDER BY COUNT(*) DESC LIMIT 1;
-- DIPAKAI: SELECT nama_upt, count(*) as jumlah_tmk FROM mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND kesimpulan = 'TMK' GROUP BY nama_upt ORDER BY COUNT(*) DESC LIMIT 1;
```

### [35] Analisis data realisasi inspeksi pada periode waktu 2025 yang dilaksanakan oleh pusat maupun UPT secara mandiri

| | |
|---|---|
| Bentuk NER | `Analisis data realisasi inspeksi pada periode waktu <YEAR> yang dilaksanakan oleh pusat maupun UPT secara mandiri` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 1 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT count(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025;
-- DIPAKAI: SELECT count(*) FROM mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025;
```

### [36] berapa jumlah sarana yang diperiksa dalam rangka kasus di wilayah kerja bbpom di bandung pada tahun 2024?

| | |
|---|---|
| Bentuk NER | `berapa jumlah <FACILITY TYPE> yang diperiksa dalam rangka kasus di wilayah kerja bbpom di <CITY NAME> pada tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 3 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom tujuan→tujuan_pemeriksaan |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT tujuan, COUNT(id) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(tujuan) LIKE '%kasus%' GROUP BY tujuan;
-- DIPAKAI: SELECT tujuan_pemeriksaan, COUNT(id) FROM mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND lower(tujuan_pemeriksaan) LIKE '%kasus%' GROUP BY tujuan_pemeriksaan;
```

### [37] sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang tutup dalam periode tahun 2025?

| | |
|---|---|
| Bentuk NER | `sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang tutup dalam periode tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + tanggal_selesai` · agregasi: tidak |
| Status | ERR_SCHEMA → **OK** · 110 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_end→tanggal_selesai |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(komoditi) IN ('obat tradisional', 'suplemen kesehatan', 'obat') AND kesimpulan = 'TTP' AND EXTRACT(YEAR FROM tgl_end) = 2025;
-- DIPAKAI: SELECT nama_sarana FROM mv_pemeriksaan WHERE lower(komoditi) IN ('obat tradisional', 'suplemen kesehatan', 'obat') AND kesimpulan = 'TTP' AND EXTRACT(YEAR FROM tanggal_selesai) = 2025;
```

### [38] sebutkan sarana distribusi yang tutup tahun 2025?

| | |
|---|---|
| Bentuk NER | `sebutkan sarana distribusi yang tutup tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + tanggal_selesai` · agregasi: tidak |
| Status | ERR_SCHEMA → **OK** · 79 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_end→tanggal_selesai ; kolom jenis_sarana→sarana |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND EXTRACT(YEAR FROM tgl_end) = 2025 AND kesimpulan LIKE 'TTP' GROUP BY nama_sarana;
-- DIPAKAI: SELECT nama_sarana FROM mv_pemeriksaan WHERE lower(sarana) LIKE 'distribusi' AND EXTRACT(YEAR FROM tanggal_selesai) = 2025 AND kesimpulan LIKE 'TTP' GROUP BY nama_sarana;
```

### [39] tampilkan jenis sarana yang paling banyak diperiksa pada tahun 2025.

| | |
|---|---|
| Bentuk NER | `tampilkan jenis sarana yang paling banyak diperiksa pada tahun <YEAR>.` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 3 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom jenis_sarana→sarana |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT jenis_sarana , count(*) FROM vw_pemeriksaan_bcc vpb WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY 1 LIMIT 5;
-- DIPAKAI: SELECT sarana , count(*) FROM mv_pemeriksaan vpb WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY 1 LIMIT 5;
```

### [40] tampilkan jumlah inspeksi rutin kategori mk dan tmk per periode 2025

| | |
|---|---|
| Bentuk NER | `tampilkan jumlah inspeksi rutin kategori <CLASSIFICATION> dan <CLASSIFICATION> per periode <YEAR>` |
| Tabel | `mv_pemeriksaan` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 2 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom tujuan→tujuan_pemeriksaan |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT kesimpulan, COUNT(*) FROM vw_pemeriksaan_bcc WHERE kesimpulan IN ('MK', 'TMK') AND lower(tujuan) LIKE '%rutin%' AND tgl_start BETWEEN '2025-01-01' AND '2025-12-31' GROUP BY 1;
-- DIPAKAI: SELECT kesimpulan, COUNT(*) FROM mv_pemeriksaan WHERE kesimpulan IN ('MK', 'TMK') AND lower(tujuan_pemeriksaan) LIKE '%rutin%' AND tanggal_mulai BETWEEN '2025-01-01' AND '2025-12-31' GROUP BY 1;
```

### [41] tampilkan jumlah sarana yang memenuhi ketentuan di wilayah upt surabaya dan pada tahun 2025.

| | |
|---|---|
| Bentuk NER | `tampilkan jumlah <FACILITY TYPE> yang memenuhi ketentuan di wilayah upt <CITY NAME> dan pada tahun <YEAR>.` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 1 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom nama_balai→nama_upt |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT nama_balai, count(*) FROM vw_pemeriksaan_bcc vpb WHERE lower(nama_balai) LIKE '%surabaya%' AND EXTRACT(YEAR FROM tgl_start) = 2025 AND kesimpulan LIKE 'MK' GROUP BY 1
-- DIPAKAI: SELECT nama_upt, count(*) FROM mv_pemeriksaan vpb WHERE lower(nama_upt) LIKE '%surabaya%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND kesimpulan LIKE 'MK' GROUP BY 1
```

### [42] tampilkan perbandingan jumlah sarana mk dibanding jumlah keseluruhan sarana yang diperiksa pada loka pom di kab. belitung pada triwulan i tahun 2025 dalam bentuk angka dan presentase.

| | |
|---|---|
| Bentuk NER | `tampilkan perbandingan jumlah <FACILITY TYPE> dibanding jumlah keseluruhan <FACILITY TYPE> pada loka pom di <REGENCY NAME> pada triwulan i tahun <YEAR` |
| Tabel | `mv_pemeriksaan` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 1 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom kabupaten→kabupaten_kota |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT COUNT(CASE WHEN kesimpulan = 'MK' THEN 1 END) AS jumlah_sarana_mk, COUNT(*) AS jumlah_keseluruhan_sarana, CASE WHEN COUNT(*) > 0 THEN ROUND( (CAST(COUNT(CASE WHEN kesimpulan = 'MK' THEN 1 END) AS NUMERIC) * 100.0) / COUNT(*), 2 ) ELSE 0.00 END AS persentase_sarana_mk FROM public.vw_pemeriksaan_bcc WHERE lower(kabupaten) LIKE '%belitung%' AND tgl_start BETWEEN '2025-01-01'::date AND '2025-03-31'::date;
-- DIPAKAI: SELECT COUNT(CASE WHEN kesimpulan = 'MK' THEN 1 END) AS jumlah_sarana_mk, COUNT(*) AS jumlah_keseluruhan_sarana, CASE WHEN COUNT(*) > 0 THEN ROUND( (CAST(COUNT(CASE WHEN kesimpulan = 'MK' THEN 1 END) AS NUMERIC) * 100.0) / COUNT(*), 2 ) ELSE 0.00 END AS persentase_sarana_mk FROM mv_pemeriksaan WHERE lower(kabupaten_kota) LIKE '%belitung%' AND tanggal_mulai BETWEEN '2025-01-01'::date AND '2025-03-31'::date;
```

### [43] tampilkan perbandingan jumlah sarana tmk dibanding jumlah keseluruhan sarana yang diperiksa loka pom di kab. belitung pada triwulan i tahun 205 dalam bentuk angka dan presentase

| | |
|---|---|
| Bentuk NER | `tampilkan perbandingan jumlah <FACILITY TYPE> dibanding jumlah keseluruhan <FACILITY TYPE> loka pom di <REGENCY NAME> pada triwulan i tahun <YEAR> dal` |
| Tabel | `mv_pemeriksaan` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 1 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom kabupaten→kabupaten_kota |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT COUNT(CASE WHEN kesimpulan = 'MK' THEN 1 END) AS jumlah_sarana_mk, COUNT(*) AS jumlah_keseluruhan_sarana, CASE WHEN COUNT(*) > 0 THEN ROUND( (CAST(COUNT(CASE WHEN kesimpulan = 'TMK' THEN 1 END) AS NUMERIC) * 100.0) / COUNT(*), 2 ) ELSE 0.00 END AS persentase_sarana_mk FROM public.vw_pemeriksaan_bcc WHERE lower(kabupaten) LIKE '%belitung%' AND tgl_start BETWEEN '2025-01-01'::date AND '2025-03-31'::date;
-- DIPAKAI: SELECT COUNT(CASE WHEN kesimpulan = 'MK' THEN 1 END) AS jumlah_sarana_mk, COUNT(*) AS jumlah_keseluruhan_sarana, CASE WHEN COUNT(*) > 0 THEN ROUND( (CAST(COUNT(CASE WHEN kesimpulan = 'TMK' THEN 1 END) AS NUMERIC) * 100.0) / COUNT(*), 2 ) ELSE 0.00 END AS persentase_sarana_mk FROM mv_pemeriksaan WHERE lower(kabupaten_kota) LIKE '%belitung%' AND tanggal_mulai BETWEEN '2025-01-01'::date AND '2025-03-31'::date;
```

### [44] tampilkan tiga temuan kritis paling sering ditemui beserta jumlah masing-masing temuannya pada balai besar pom di dki jakarta tahun 2024.

| | |
|---|---|
| Bentuk NER | `tampilkan tiga temuan kritis paling sering ditemui beserta jumlah masing-masing temuannya pada <HALL NAME> tahun <YEAR>.` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 3 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom tgl_start→tanggal_mulai ; kolom nama_balai→nama_upt |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT kesimpulan, COUNT(*) AS jumlah FROM public.vw_pemeriksaan_bcc WHERE nama_balai = 'BALAI BESAR POM DI JAKARTA' AND EXTRACT(YEAR FROM tgl_start) = 2024 AND kesimpulan IS NOT NULL GROUP BY kesimpulan ORDER BY jumlah DESC LIMIT 3;
-- DIPAKAI: SELECT kesimpulan, COUNT(*) AS jumlah FROM mv_pemeriksaan WHERE nama_upt = 'BALAI BESAR POM DI JAKARTA' AND EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND kesimpulan IS NOT NULL GROUP BY kesimpulan ORDER BY jumlah DESC LIMIT 3;
```

### [45] upt mana saja yang paling banyak melaporkan hasil pemeriksaan sarana yang tmk?

| | |
|---|---|
| Bentuk NER | `upt mana saja yang paling banyak melaporkan hasil pemeriksaan <FACILITY TYPE> yang tmk?` |
| Tabel | `mv_pemeriksaan` · agregasi: ya |
| Status | ERR_SCHEMA → **OK** · 5 baris |
| Lapis terjemahan | relasi vw_pemeriksaan_bcc→mv_pemeriksaan ; kolom nama_balai→nama_upt |
| Diagnosa | **🔧 Pulih: relasi + kolom** |
| Sebab | Pulih setelah penyesuaian relasi + kolom ke skema live |

```sql
-- ASLI   : SELECT nama_balai, COUNT(*) as jumlah_pemeriksaan FROM vw_pemeriksaan_bcc WHERE kesimpulan = 'TMK' GROUP BY nama_balai ORDER BY count(*) desc limit 5
-- DIPAKAI: SELECT nama_upt, COUNT(*) as jumlah_pemeriksaan FROM mv_pemeriksaan WHERE kesimpulan = 'TMK' GROUP BY nama_upt ORDER BY count(*) desc limit 5
```

---

## Generasi v2 — koneksi `_all` (Ags 2025)

70 pertanyaan.

### [46] analisis jumlah seluruh sarana produksi dan distribusi (tanpa pengulangan nama yang sama) per komoditi produk (obat/oba/sk/kos/po) yang telah diperiksa bpom dalam periode 2025

| | |
|---|---|
| Bentuk NER | `analisis jumlah seluruh sarana produksi dan distribusi (tanpa pengulangan nama yang sama) per komoditi produk (<COMMODITY NAME>/<COMMODITY NAME>/<COMM` |
| Tabel | `mv_pemeriksaan + mp` · agregasi: ya |
| Status | OK → **OK** · 46 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT sarana, komoditi, kesimpulan, count(DISTINCT nama_sarana) FROM public.mv_pemeriksaan mp WHERE (lower(sarana) LIKE '%produksi%' OR lower(sarana) LIKE '%distribusi%') AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 GROUP BY 1, 2, 3;
```

### [47] apa temuan/ketidaksesuaian yang paling banyak ditemukan dari hasil pemeriksaan sarana produksi md?

| | |
|---|---|
| Bentuk NER | `apa temuan/ketidaksesuaian yang paling banyak ditemukan dari hasil pemeriksaan <FACILITY TYPE>?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 6 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT jenis_sarana, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(jenis_sarana) LIKE '%pangan md%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2 ORDER BY 3 DESC;
```

### [48] apa temuan/ketidaksesuaian yang paling banyak ditemukan pada seluruh sarana distribusi tmk di wilayah kerja balai pom di payakumbuh?

| | |
|---|---|
| Bentuk NER | `apa temuan/ketidaksesuaian yang paling banyak ditemukan pada seluruh sarana distribusi tmk di wilayah kerja balai pom di <REGENCY NAME>?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 8 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT kabupaten_kota, mp.sarana, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(kabupaten_kota) LIKE '%payakumbuh%' AND lower(mp.sarana) LIKE '%distribusi%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3 ORDER BY 4 DESC;
```

### [49] bagaimana riwayat pemeriksaan sarana alfamart dalam periode tahun 2024?

| | |
|---|---|
| Bentuk NER | `bagaimana riwayat pemeriksaan sarana <COMPANY NAME> dalam periode tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 583 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, alamat, tanggal_mulai, tanggal_selesai, jenis_sarana, tujuan_pemeriksaan, kesimpulan FROM public.mv_pemeriksaan WHERE LOWER(nama_sarana) LIKE '%alfamart%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ORDER BY tanggal_mulai;
```

### [50] bagaimana tren data hasil pengawasan sarana obat tradisional; suplemen kesehatan; obat kuasi dalam periode tahun 2025?

| | |
|---|---|
| Bentuk NER | `bagaimana tren data hasil pengawasan sarana <COMMODITY NAME>; <COMMODITY NAME>; <COMMODITY NAME> dalam periode tahun <YEAR>?` |
| Tabel | `mp + mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 246 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT EXTRACT(MONTH FROM mp.tanggal_mulai), sarana, komoditi, kesimpulan, count(nama_sarana) FROM public.mv_pemeriksaan mp WHERE (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 GROUP BY 1, 2, 3, 4;
```

### [51] bagaimana tren data hasil pengawasan sarana obat tradisional; suplemen kesehatan; obat kuasi yang tidak memenuhi ketentuan berdasarkan kategori temuan (tmk tie/cpotb/cpotb habis/tidak memiliki cpotb) 

| | |
|---|---|
| Bentuk NER | `bagaimana tren data hasil pengawasan <COMMODITY NAME>; <COMMODITY NAME>; <COMMODITY NAME> yang tidak memenuhi ketentuan berdasarkan kategori temuan (<` |
| Tabel | `tanggal_mulai + mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 281 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT EXTRACT(MONTH FROM tanggal_mulai) AS bulan, mp.sarana, mp.komoditi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') GROUP BY 1, 2, 3, 4;
```

### [52] bagaimana tren data hasil pengawasan sarana produksi kosmetik (profil hasil pengawasan) di upt balai pom di palembang dalam periode tahun 2024?

| | |
|---|---|
| Bentuk NER | `bagaimana tren data hasil pengawasan <FACILITY TYPE> (profil hasil pengawasan) di <HALL NAME> di <CITY NAME> dalam periode tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + mp` · agregasi: tidak |
| Status | OK → **OK** · 1,313 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.nama_upt, tanggal_mulai, nama_sarana, jenis_sarana, mpt.product_name, mpt.tp_kategori FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(nama_upt) LIKE '%palembang%' AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2024 AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ORDER BY 1, 2, 3, 4;
```

### [53] bagaimana tren data hasil pengawasan sarana produksi kosmetik yang memenuhi ketentuan dan tidak memenuhi ketentuan dalam periode tahun 2024?

| | |
|---|---|
| Bentuk NER | `bagaimana tren data hasil pengawasan sarana produksi kosmetik yang memenuhi ketentuan dan tidak memenuhi ketentuan dalam periode tahun <YEAR>?` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 31 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS bulan, kesimpulan, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND lower(komoditi) like '%kosmetik%' AND lower(sarana) like '%produksi%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1,2,3 ORDER BY 1,2,3;
```

### [54] bagaimana tren data hasil pengawasan sarana produksi kosmetik yang tidak memenuhi ketentuan berdasarkan kategori temuan (tmk tie/cpkb/cpkb habis/tidak memiliki cpkb) dalam periode tahun 2025?

| | |
|---|---|
| Bentuk NER | `bagaimana tren data hasil pengawasan <FACILITY TYPE> yang tidak memenuhi ketentuan berdasarkan kategori temuan (<CLASSIFICATION>) dalam periode tahun ` |
| Tabel | `tanggal_mulai + mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 25 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT EXTRACT(MONTH FROM tanggal_mulai) AS bulan, mp.sarana, mp.komoditi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(komoditi) like '%kosmetik%' AND lower(sarana) like '%produksi%' GROUP BY 1, 2, 3, 4;
```

### [55] bagaimana tren hasil pemeriksaan sarana peredaran sejak tahun 2025

| | |
|---|---|
| Bentuk NER | `bagaimana tren hasil pemeriksaan sarana peredaran sejak tahun <YEAR>` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 53 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS BULAN, sarana, kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE lower(sarana) LIKE '%distribusi%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3, 4 ORDER BY 1, 2, 3, 4;
```

### [56] bagaimana tren hasil pemeriksaan sarana produksi md dan pirt sejak tahun 2024 hingga 2025?

| | |
|---|---|
| Bentuk NER | `bagaimana tren hasil pemeriksaan <FACILITY TYPE> dan <FACILITY TYPE> sejak tahun <YEAR> hingga <YEAR>?` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 48 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS bulan, jenis_sarana, count(*) FROM mv_pemeriksaan mp WHERE (lower(jenis_sarana) LIKE '%pangan md%' OR lower(jenis_sarana) LIKE '%pangan irt%') AND EXTRACT(YEAR FROM tanggal_mulai) BETWEEN 2024 AND 2025 AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3 ORDER BY 1, 2, 3;
```

### [57] berapa jumlah sarana yang diperiksa dalam rangka kasus di wilayah kerja bbpom di bandung pada tahun 2024?

| | |
|---|---|
| Bentuk NER | `berapa jumlah <FACILITY TYPE> yang diperiksa dalam rangka kasus di wilayah kerja bbpom di <CITY NAME> pada tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + mp` · agregasi: tidak |
| Status | OK → **OK** · 11 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_upt, nama_sarana, tujuan_pemeriksaan, mp.kesimpulan FROM public.mv_pemeriksaan mp WHERE lower(tujuan_pemeriksaan) LIKE '%kasus%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND lower(kabupaten_kota) LIKE '%bandung%' AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2024;
```

### [58] berapa total sarana yang tutup dan/atau tidak berproduksi saat diperiksa di tahun 2024 di wilayah kerja jakarta utara?

| | |
|---|---|
| Bentuk NER | `berapa total sarana yang tutup dan/atau tidak berproduksi saat diperiksa di tahun <YEAR> di wilayah kerja <CITY NAME>?` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 3 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT kabupaten_kota, nama_sarana, tanggal_mulai, kesimpulan FROM public.mv_pemeriksaan WHERE kesimpulan = 'TTP' AND lower(sarana) LIKE '%produksi%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND lower(kabupaten_kota) ILIKE '%jakarta utara%';
```

### [59] merekap jumlah dan nama sarana distribusi dan pelayanan yang belum pernah diperiksa dalam kurun waktu 1 tahun terakhir

| | |
|---|---|
| Bentuk NER | `merekap jumlah dan nama sarana distribusi dan pelayanan yang belum pernah diperiksa dalam kurun waktu 1 tahun terakhir` |
| Tabel | `mv_pemeriksaan` · agregasi: tidak |
| Status | OK → **OK** · 146,493 baris |
| Lapis terjemahan | - |
| Diagnosa | **⚠️ Jalan tapi >100rb baris tanpa agregasi** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah. TAPI hasilnya 146,493 baris tanpa agregasi — jalan, bukan jawaban |

```sql
SELECT DISTINCT nama_sarana, komoditi, tanggal_mulai FROM public.mv_pemeriksaan mp WHERE (lower(sarana) LIKE '%distribusi%' OR lower(sarana) LIKE '%pelayanan%') AND mp.nama_sarana NOT IN ( SELECT nama_sarana FROM public.mv_pemeriksaan WHERE tanggal_mulai >= NOW() - INTERVAL '1 year' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ) ORDER BY nama_sarana;
```

### [60] sarana distribusi apa saja yang pernah memiliki riwayat memenuhi ketentuan berdasarkan tahun temuannya?

| | |
|---|---|
| Bentuk NER | `sarana distribusi apa saja yang pernah memiliki riwayat memenuhi ketentuan berdasarkan tahun temuannya?` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: tidak |
| Status | OK → **OK** · 99,586 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, sarana, EXTRACT(YEAR FROM tanggal_mulai) AS tahun_temuan FROM mv_pemeriksaan WHERE lower(sarana) = 'distribusi' AND kesimpulan = 'MK' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ORDER BY 1, 2;
```

### [61] sarana distribusi apa saja yang pernah memiliki riwayat tidak memenuhi ketentuan berdasarkan tahun temuannya?

| | |
|---|---|
| Bentuk NER | `sarana distribusi apa saja yang pernah memiliki riwayat tidak memenuhi ketentuan berdasarkan tahun temuannya?` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: tidak |
| Status | OK → **OK** · 36,358 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, sarana, EXTRACT(YEAR FROM tanggal_mulai) AS tahun_temuan FROM mv_pemeriksaan WHERE lower(sarana) = 'distribusi' AND kesimpulan = 'TMK' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ORDER BY 1, 2;
```

### [62] sarana distribusi kosmetik apa saja yang pernah diperiksa oleh badan pom setiap tahun dari tahun 2020 hingga 2024?

| | |
|---|---|
| Bentuk NER | `<FACILITY TYPE> apa saja yang pernah diperiksa oleh badan pom setiap tahun dari tahun <YEAR> hingga <YEAR>?` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: tidak |
| Status | OK → **OK** · 35,566 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, EXTRACT(YEAR FROM tanggal_mulai) AS tahun FROM mv_pemeriksaan WHERE lower(sarana) = 'distribusi' AND LOWER(komoditi) LIKE '%kosmetik%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ORDER BY 2;
```

### [63] sarana distribusi kosmetik apa saja yang pernah diperiksa oleh badan pom?

| | |
|---|---|
| Bentuk NER | `<FACILITY TYPE> apa saja yang pernah diperiksa oleh <CLASSIFICATION>?` |
| Tabel | `mv_pemeriksaan` · agregasi: tidak |
| Status | OK → **OK** · 23,752 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT DISTINCT (nama_sarana) FROM mv_pemeriksaan WHERE lower(sarana) = 'distribusi' AND LOWER(komoditi) LIKE '%kosmetik%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED');
```

### [64] sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang belum dilakukan pemeriksaan dalam periode 2 tahun terakhir?

| | |
|---|---|
| Bentuk NER | `<FACILITY TYPE>; <CLASSIFICATION>; <CLASSIFICATION> apa saja yang belum dilakukan pemeriksaan dalam periode 2 tahun terakhir?` |
| Tabel | `mv_pemeriksaan` · agregasi: tidak |
| Status | OK → **OK** · 11,471 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT DISTINCT nama_sarana, komoditi, tanggal_mulai FROM public.mv_pemeriksaan mp WHERE (lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%' OR lower(komoditi) LIKE '%obat kuasi%') AND mp.nama_sarana NOT IN ( SELECT nama_sarana FROM public.mv_pemeriksaan WHERE tanggal_mulai >= NOW() - INTERVAL '2 year' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ) ORDER BY
```

### [65] sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang memiliki riwayat pemeriksaan tidak memenuhi ketentuan dalam periode tahun 2025?

| | |
|---|---|
| Bentuk NER | `sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang memiliki riwayat pemeriksaan tidak memenuhi ketentuan dalam periode tahun <YEAR>` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 4,571 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT DISTINCT mp.nama_sarana, mp.sarana, mp.komoditi FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND lower(kesimpulan) = 'tmk';
```

### [66] sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang pernah memproduksi dan mengedarkan obat tradisional; suplemen kesehatan; obat kuasi tie dalam periode tahun 2025?

| | |
|---|---|
| Bentuk NER | `sarana <COMMODITY NAME>; <COMMODITY NAME>; <COMMODITY NAME> apa saja yang pernah memproduksi dan mengedarkan <COMMODITY NAME>; <COMMODITY NAME>; <COMM` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 26,549 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.nama_sarana, mpt.product_name, mp.sarana, mp.komoditi, mpt.tp_kategori FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND lower(tp_kategori) LIKE '%tie%';
```

### [67] sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang tutup dalam periode tahun 2025?

| | |
|---|---|
| Bentuk NER | `sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang tutup dalam periode tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 107 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, kesimpulan FROM public.mv_pemeriksaan mp WHERE mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND lower(kesimpulan) = 'ttp' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
```

### [68] sarana produksi kosmetik apa saja yang belum dilakukan pemeriksaan dalam periode 2 tahun terakhir?

| | |
|---|---|
| Bentuk NER | `<FACILITY TYPE> apa saja yang belum dilakukan pemeriksaan dalam periode 2 tahun terakhir?` |
| Tabel | `mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 607 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, MAX(tanggal_mulai) AS terakhir_diperiksa FROM mv_pemeriksaan WHERE komoditi ILIKE '%kosmetik%' AND sarana ILIKE 'produksi' GROUP BY nama_sarana HAVING COALESCE(MAX(tanggal_mulai), DATE '-infinity') < (CURRENT_DATE - INTERVAL '2 years') ORDER BY terakhir_diperiksa NULLS FIRST, nama_sarana;
```

### [69] sarana produksi kosmetik apa saja yang memiliki riwayat pemeriksaan tidak memenuhi ketentuan dalam periode tahun 2025?

| | |
|---|---|
| Bentuk NER | `sarana produksi kosmetik apa saja yang memiliki riwayat pemeriksaan tidak memenuhi ketentuan dalam periode tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 207 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.sarana, mp.nama_sarana, mpt.product_name, mp.tanggal_mulai, mpt.tp_kategori, mp.kesimpulan FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(komoditi) like '%kosmetik%' AND lower(sarana) like '%produksi%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FIN
```

### [70] sarana produksi kosmetik apa saja yang pernah memproduksi dan mengedarkan kosmetik tie dalam periode tahun 2025?

| | |
|---|---|
| Bentuk NER | `sarana produksi kosmetik apa saja yang pernah memproduksi dan mengedarkan <PRODUCT NAME> dalam periode tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 77 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.sarana, mp.nama_sarana, mpt.product_name, mp.tanggal_mulai, mpt.tp_kategori FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(komoditi) like '%kosmetik%' AND lower(sarana) like '%produksi%' AND lower(mpt.tp_kategori) LIKE '%tie%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED
```

### [71] sarana produksi kosmetik apa saja yang tutup dalam periode tahun 2025?

| | |
|---|---|
| Bentuk NER | `sarana produksi kosmetik apa saja yang tutup dalam periode tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 4 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, tanggal_mulai, kesimpulan FROM public.mv_pemeriksaan WHERE LOWER(sarana) LIKE '%produksi%' AND LOWER(komoditi) LIKE '%kosmetik%' AND kesimpulan = 'TTP' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
```

### [72] sarana produksi md apa yang paling sering memiliki riwayat tmk?

| | |
|---|---|
| Bentuk NER | `<FACILITY TYPE> md apa yang paling sering memiliki riwayat tmk?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 10 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, jenis_sarana, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(jenis_sarana) LIKE '%pangan md%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3 ORDER BY 4 DESC LIMIT 10;
```

### [73] sebutkan sarana distribusi yang tutup tahun 2025?

| | |
|---|---|
| Bentuk NER | `sebutkan sarana distribusi yang tutup tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 79 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, tanggal_mulai FROM public.mv_pemeriksaan WHERE sarana = 'DISTRIBUSI' AND kesimpulan = 'TTP' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
```

### [74] sebutkan sarana distribusi yang tutup tahun 2025?

| | |
|---|---|
| Bentuk NER | `sebutkan sarana distribusi yang tutup tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 79 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, tanggal_mulai, kesimpulan FROM mv_pemeriksaan WHERE LOWER(sarana) = 'distribusi' AND LOWER(kesimpulan) = 'ttp' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
```

### [75] tampilkan aspek temuan yang berulang dari tahun ke tahun pada sarana dengan nama siloam.

| | |
|---|---|
| Bentuk NER | `tampilkan aspek temuan yang berulang dari tahun ke tahun pada sarana dengan nama <COMPANY NAME>.` |
| Tabel | `tanggal_mulai + mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 2 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.nama_sarana, mp.sarana, mpt.tp_kategori, EXTRACT(YEAR FROM tanggal_mulai) AS tahun, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(nama_sarana) LIKE '%siloam%' GROUP BY 1, 2, 3, 4;
```

### [76] tampilkan daftar sarana dengan hasil tmk berulang lebih dari sekali pada kurun 5 tahun terakhir hingga saat ini pada wilayah kerja balai pom di tangerang

| | |
|---|---|
| Bentuk NER | `tampilkan daftar <FACILITY TYPE> dengan hasil tmk berulang lebih dari sekali pada kurun 5 tahun terakhir hingga saat ini pada wilayah kerja balai pom ` |
| Tabel | `tanggal_mulai + mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 530 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, mp.nama_sarana, mp.sarana, kabupaten_kota, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.kabupaten_kota) LIKE '%tangerang%' AND mp.tanggal_mulai >= (CURRENT_DATE - INTERVAL '5 years') GROUP BY 1, 2, 3, 4, 5 HAVING COUNT(*) > 1 ORDER BY 1, 2, 3, 4, 5;
```

### [77] tampilkan data jumlah pemeriksaan sarana peredaran oleh adiyati pada tahun 2025

| | |
|---|---|
| Bentuk NER | `tampilkan data jumlah pemeriksaan sarana peredaran oleh adiyati pada tahun <YEAR>` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_petugas + t1` · agregasi: ya |
| Status | OK → **OK** · 1 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT T2.petugas, sarana, COUNT(T1.id) FROM public.mv_pemeriksaan AS T1 INNER JOIN public.mv_pemeriksaan_petugas AS T2 ON T1.id = T2.id_pemeriksaan WHERE LOWER(T1.sarana) like '%distribusi%' AND lower(T2.petugas) LIKE '%adiyati%' AND EXTRACT(YEAR FROM T1.tanggal_mulai) = 2025 GROUP BY 1, 2;
```

### [78] tampilkan data profil jenis sarana yang sudah dilakukan pemeriksaan dari tahun 2025

| | |
|---|---|
| Bentuk NER | `tampilkan data profil jenis sarana yang sudah dilakukan pemeriksaan dari tahun <YEAR>` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 421 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.jenis_sarana, mp.kesimpulan, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3;
```

### [79] tampilkan jenis sarana yang paling banyak diperiksa pada tahun 2025.

| | |
|---|---|
| Bentuk NER | `tampilkan jenis sarana yang paling banyak diperiksa pada tahun <YEAR>.` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 21 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT sarana, jenis_sarana, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY 1, 2 ORDER BY 3 DESC;
```

### [80] tampilkan jumlah dan nama sarana distribusi dan pelayanan yang mk/tmk masing-masing upt pada tahun 2025.

| | |
|---|---|
| Bentuk NER | `tampilkan jumlah dan nama <FACILITY TYPE> yang mk/tmk masing-masing upt pada tahun <YEAR>.` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 4,527 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, sarana, kesimpulan, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE (lower(sarana) LIKE '%distribusi%' OR lower(sarana) LIKE '%pelayanan%') AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3;
```

### [81] tampilkan jumlah inspeksi rutin kategori mk dan tmk per periode 2025

| | |
|---|---|
| Bentuk NER | `tampilkan jumlah inspeksi rutin kategori <CLASSIFICATION> dan <CLASSIFICATION> per periode <YEAR>` |
| Tabel | `mv_pemeriksaan + mp` · agregasi: ya |
| Status | OK → **OK** · 6 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT tujuan_pemeriksaan, mp.kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE lower(tujuan_pemeriksaan) LIKE '%rutin%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 GROUP BY 1, 2;
```

### [82] tampilkan jumlah nilai temuan produk sarana distribusi pada tahun 2025 dalam rupiah?

| | |
|---|---|
| Bentuk NER | `tampilkan jumlah nilai temuan produk <PRODUCT NAME> pada tahun <YEAR> dalam rupiah?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 89 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.sarana, mp.komoditi, mpt.tp_kategori, sum(mpt.tp_harga_total) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(sarana) like '%distribusi%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3;
```

### [83] tampilkan jumlah nilai temuan produk sarana distribusi pada tahun 2025?

| | |
|---|---|
| Bentuk NER | `tampilkan jumlah nilai temuan produk sarana distribusi pada tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 90 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.komoditi, mpt.tp_kategori, sum(mpt.tp_harga_total) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(sarana) LIKE '%distribusi%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2;
```

### [84] tampilkan jumlah sarana produksi kategori mk dan tmk per komoditi, periode, wilayah, dan cakupan upt.

| | |
|---|---|
| Bentuk NER | `tampilkan jumlah <FACILITY TYPE> kategori <CLASSIFICATION> dan <CLASSIFICATION> per <COMMODITY NAME>, periode, wilayah, dan cakupan upt.` |
| Tabel | `mp + mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 8,361 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT EXTRACT(YEAR FROM mp.tanggal_mulai), sarana, komoditi, kabupaten_kota, kesimpulan, count(nama_sarana) FROM public.mv_pemeriksaan mp WHERE lower(sarana) LIKE '%produksi%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3, 4, 5;
```

### [85] tampilkan jumlah temuan produk sarana distribusi pada tahun 2025?

| | |
|---|---|
| Bentuk NER | `tampilkan jumlah temuan produk sarana distribusi pada tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 90 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.komoditi, mpt.tp_kategori, sum(mpt.tp_jml_temuan) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(sarana) LIKE '%distribusi%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2;
```

### [86] tampilkan ketepatan waktu pelaporan sipt oleh balai besar pom di bandung dengan menampilkan data tanggal pemeriksaan dan tanggal kirim data sipt ke pusat yang kurang dari 30 hari kerja dan lebih dari 

| | |
|---|---|
| Bentuk NER | `tampilkan ketepatan waktu pelaporan sipt oleh <HALL NAME> dengan menampilkan data tanggal pemeriksaan dan tanggal kirim data sipt ke pusat yang kurang` |
| Tabel | `mv_pemeriksaan_log + generate_series + hari + waktu + kerja + mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 10,172 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
WITH waktu AS ( SELECT mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS t3, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 4) AS t4 FROM public.mv_pemeriksaan_log AS mpl GROUP BY mpl.id_pemeriksaan ), kerja AS ( SELECT w.id_pemeriksaan, w.t3, w.t4, ( SELECT COUNT(*) FROM generate_series(w.t3::date, w.t4::date - 1, '1 day') AS d(hari) WHERE EXTRACT(DOW FROM hari) BETWEEN 1 AND 5 -- Se
```

### [87] tampilkan ketepatan waktu pelaporan sipt oleh balai dengan menampilkan data tanggal pemeriksaan dan tanggal kirim data sipt ke pusat yang kurang dari 30 hari kerja dan lebih dari 30 hari kerja untuk b

| | |
|---|---|
| Bentuk NER | `tampilkan ketepatan waktu pelaporan sipt oleh balai dengan menampilkan data tanggal pemeriksaan dan tanggal kirim data sipt ke pusat yang kurang dari ` |
| Tabel | `mv_pemeriksaan_log + generate_series + hari + waktu + kerja + mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 6,704 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
WITH waktu AS ( SELECT mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS t3, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 4) AS t4 FROM public.mv_pemeriksaan_log AS mpl GROUP BY mpl.id_pemeriksaan ), kerja AS ( SELECT w.id_pemeriksaan, w.t3, w.t4, ( SELECT COUNT(*) FROM generate_series(w.t3::date, w.t4::date - 1, '1 day') AS d(hari) WHERE EXTRACT(DOW FROM hari) BETWEEN 1 AND 5 -- Se
```

### [88] tampilkan merek-merek temuan produk kosmetik pada pemeriksaan tahun 2025 diurutkan berdasarkan temuan yang terbanyak?

| | |
|---|---|
| Bentuk NER | `tampilkan merek-merek temuan <PRODUCT NAME> pada pemeriksaan tahun <YEAR> diurutkan berdasarkan temuan yang terbanyak?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 809 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mpt.product_brands, mp.komoditi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND LOWER(komoditi) LIKE '%kosmetik%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3;
```

### [89] tampilkan merek-merek temuan produk obat tradisional; suplemen kesehatan; obat kuasi pada pemeriksaan tahun 2025?

| | |
|---|---|
| Bentuk NER | `tampilkan merek-merek temuan <CLASSIFICATION>; <CLASSIFICATION>; <CLASSIFICATION> pada pemeriksaan tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 198 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mpt.product_brands, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1 ORDER BY 2 DESC;
```

### [90] tampilkan negara-negara dengan temuan impor pada tahun 2025?

| | |
|---|---|
| Bentuk NER | `tampilkan negara-negara dengan temuan impor pada tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: tidak |
| Status | OK → **OK** · 99,938 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, tanggal_mulai, mpt.product_name, mpt.tp_negara, mpt.tp_kategori FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mpt.tp_negara) NOT LIKE '%indonesia%'
```

### [91] tampilkan perbandingan jumlah sarana mk dibanding jumlah keseluruhan sarana yang diperiksa pada loka pom di kab. belitung pada triwulan i tahun 2025 dalam bentuk angka dan presentase.

| | |
|---|---|
| Bentuk NER | `tampilkan perbandingan jumlah <FACILITY TYPE> dibanding jumlah keseluruhan <FACILITY TYPE> pada loka pom di <REGENCY NAME> pada triwulan i tahun <YEAR` |
| Tabel | `mv_pemeriksaan + mp` · agregasi: ya |
| Status | OK → **OK** · 1 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT COUNT(*) AS total_sarana, COUNT(CASE WHEN lower(mp.kesimpulan) = 'mk' THEN 1 END) AS jumlah_sarana_mk, CAST( COUNT(CASE WHEN lower(mp.kesimpulan) = 'mk' THEN 1 END) AS NUMERIC ) * 100 / COUNT(*) AS persentase_mk FROM public.mv_pemeriksaan mp WHERE lower(mp.kabupaten_kota) LIKE '%belitung%' AND mp.status IN ('VERIFY4', 'VERIFY5', 'VERIFY6', 'VERIFY7', 'FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 A
```

### [92] tampilkan perbandingan jumlah sarana tmk dibanding jumlah keseluruhan sarana yang diperiksa loka pom di kab. belitung pada triwulan i tahun 2025 dalam bentuk angka dan presentase

| | |
|---|---|
| Bentuk NER | `tampilkan perbandingan jumlah <FACILITY TYPE> dibanding jumlah keseluruhan <FACILITY TYPE> loka pom di <REGENCY NAME> pada triwulan i tahun <YEAR> dal` |
| Tabel | `mv_pemeriksaan + mp` · agregasi: ya |
| Status | OK → **OK** · 1 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT COUNT(*) AS total_sarana, COUNT(CASE WHEN lower(mp.kesimpulan) = 'tmk' THEN 1 END) AS jumlah_sarana_tmk, CAST( COUNT(CASE WHEN lower(mp.kesimpulan) = 'tmk' THEN 1 END) AS NUMERIC ) * 100 / COUNT(*) AS persentase_tmk FROM public.mv_pemeriksaan mp WHERE lower(mp.kabupaten_kota) LIKE '%belitung%' AND mp.status IN ('VERIFY4', 'VERIFY5', 'VERIFY6', 'VERIFY7', 'FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 20
```

### [93] tampilkan persentase ketepatan waktu pelaporan hasil pemeriksaan dari upt dengan nama Balai POM di Bogor di tw 1 2025 (syarat : tepat waktu jika pelaporan hasil pemeriksaan maksimal tanggal 15 bulan s

| | |
|---|---|
| Bentuk NER | `tampilkan persentase ketepatan waktu pelaporan hasil pemeriksaan dari upt dengan nama <HALL NAME> di <REGENCY NAME> di tw 1 <YEAR> (syarat : tepat wak` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_log + mpl + laporan_q1_2025` · agregasi: ya |
| Status | OK → **OK** · 1 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
WITH laporan_q1_2025 AS ( -- Langkah 1: Ambil data tanggal penting dari Balai POM di Bogor di Q1 2025 SELECT mp.nama_upt, mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 2) AS tanggal_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS tanggal_pelaporan FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_log AS mpl ON mp.id = mpl.id_pemeriksaan WHERE lower(mp.nama_up
```

### [94] tampilkan persentase mk tmk hasil pemeriksaan sarana pangan olahan md untuk tujuan pemeriksaan pemeriksaan rutin dari seluruh upt di tahun 2025 dalam bentuk diagram batang

| | |
|---|---|
| Bentuk NER | `tampilkan persentase mk tmk hasil pemeriksaan <FACILITY TYPE> untuk tujuan pemeriksaan <PURPOSE TYPE> dari seluruh upt di tahun <YEAR> dalam bentuk di` |
| Tabel | `mv_pemeriksaan + mp` · agregasi: ya |
| Status | OK → **OK** · 197 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_upt, mp.kesimpulan, COUNT(*) FROM public.mv_pemeriksaan mp WHERE lower(jenis_sarana) LIKE '%pangan md%' AND lower(tujuan_pemeriksaan) LIKE '%pemeriksaan rutin%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 GROUP BY 1,2;
```

### [95] tampilkan profil pemeriksaan sarana produksi obat dan makanan selama periode 2025 dalam bentuk tabel dan grafik jumlah sarana produksi mk, tmk, tidak dapat dinilai, tutup per jenis komoditi (obat, oba

| | |
|---|---|
| Bentuk NER | `tampilkan profil pemeriksaan <FACILITY TYPE> selama periode <YEAR> dalam bentuk tabel dan grafik jumlah sarana produksi <CLASSIFICATION>, <CLASSIFICAT` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 111 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS BULAN, sarana, jenis_sarana, kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE lower(sarana) LIKE '%produksi%' AND (lower(jenis_sarana) LIKE '%obat' OR lower(jenis_sarana) LIKE '%pangan%') AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3, 4, 5 OR
```

### [96] tampilkan profil temuan ketidaksesuaian berdasarkan hasil pemeriksaan pada tahun 2025.

| | |
|---|---|
| Bentuk NER | `tampilkan profil temuan ketidaksesuaian berdasarkan hasil pemeriksaan pada tahun <YEAR>.` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 71 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mpt.tp_kategori, count(*) AS jumlah_pemeriksaan, sum(mpt.tp_jml_temuan) AS jumlah_temuan, sum(mpt.tp_harga_total) AS nilai_temuan FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY 1;
```

### [97] tampilkan rekapitulasi produktivitas penguji (jumlah parameter per orang) dari tanggal 1 januari 2025 hingga 31 desember 2025.

| | |
|---|---|
| Bentuk NER | `tampilkan rekapitulasi produktivitas penguji (jumlah parameter per orang) dari tanggal 1 januari <YEAR> hingga 31 desember <YEAR>.` |
| Tabel | `mv_pemeriksaan_petugas + mpp` · agregasi: ya |
| Status | OK → **OK** · 1,777 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mpp.petugas, count(*) FROM public.mv_pemeriksaan_petugas mpp WHERE EXTRACT(YEAR FROM mpp.tgl_surat) = 2025 GROUP BY 1 ORDER BY 2 DESC;
```

### [98] tampilkan riwayat pemeriksaan sarana produksi 'maha siri jaya' pada rentang tahun yang tersedia.

| | |
|---|---|
| Bentuk NER | `tampilkan riwayat pemeriksaan sarana produksi '<COMPANY NAME>' pada rentang tahun yang tersedia.` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: tidak |
| Status | OK → **OK** · 9 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, sarana, jenis_sarana, mpt.product_name, tanggal_mulai, mpt.tp_kategori FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(sarana) LIKE '%produksi%' AND lower(mp.nama_sarana) LIKE '%maha siri jaya%';
```

### [99] tampilkan sarana distribusi dan pelayanan yang tutup pada periode tahun 2025

| | |
|---|---|
| Bentuk NER | `tampilkan <FACILITY TYPE> yang tutup pada periode tahun <YEAR>` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 125 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, sarana, tanggal_mulai FROM public.mv_pemeriksaan WHERE (lower(sarana) LIKE '%distribusi%' OR lower(sarana) LIKE '%pelayanan%') AND kesimpulan = 'TTP' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
```

### [100] tampilkan sarana peredaran yang memiliki riwayat hasil tmk terbanyak di upt dengan nama balai pom di jakarta.

| | |
|---|---|
| Bentuk NER | `tampilkan sarana peredaran yang memiliki riwayat hasil tmk terbanyak di upt dengan nama <HALL NAME> di <CITY NAME>.` |
| Tabel | `mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 979 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.nama_sarana, mp.kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND kesimpulan = 'TMK' AND lower(mp.sarana) LIKE '%distribusi%' AND lower(nama_upt) LIKE '%pom di jakarta%' GROUP BY 1, 2;
```

### [101] tampilkan temuan ketidaksesuaian untuk klausul untuk upt balai besar pom di bandung.

| | |
|---|---|
| Bentuk NER | `tampilkan temuan ketidaksesuaian untuk klausul untuk <HALL NAME> di <CITY NAME>.` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 26 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mpt.tp_kategori, count(*) AS jumlah_pemeriksaan, sum(mpt.tp_jml_temuan) AS jumlah_temuan, sum(mpt.tp_harga_total) AS nilai_temuan FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(kesimpulan) = 'tmk' AND lower(mp.nama_upt) LIKE '%pom di bandung%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1;
```

### [102] tampilkan temuan produk berdasarkan kategori sarana distribusi yang ada di sipt?

| | |
|---|---|
| Bentuk NER | `tampilkan <PRODUCT NAME> berdasarkan kategori <FACILITY TYPE> yang ada di sipt?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 132 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.komoditi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(sarana) LIKE '%distribusi%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2;
```

### [103] tampilkan tiga temuan/ketidaksesuaian paling sering ditemui di wilayah kerja bbpom di dki jakarta pada triwulan 1 tahun 2025.

| | |
|---|---|
| Bentuk NER | `tampilkan tiga temuan/ketidaksesuaian paling sering ditemui di wilayah kerja bbpom di <PROVINCE NAME> pada triwulan 1 tahun <YEAR>.` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 7 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_upt, provinsi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(provinsi) LIKE '%dki jakarta%' AND mp.tanggal_mulai BETWEEN '2025-01-01' AND '2025-04-01' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3;
```

### [104] tampilkan total nilai keekonomian produk tmk (tie, rusak kedaluwarsa) di balai pom di batam pada tahun 2025.

| | |
|---|---|
| Bentuk NER | `tampilkan total nilai keekonomian produk tmk (tie, rusak kedaluwarsa) di <HALL NAME> di <CITY NAME> pada tahun <YEAR>.` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 12 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mpt.tp_kategori, sum(mpt.tp_harga_total) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%pom di batam%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY 1;
```

### [105] tampilkan total temuan produk dan total nilai temuan pada kategori 'lainnya'.

| | |
|---|---|
| Bentuk NER | `tampilkan total temuan produk dan total nilai temuan pada kategori '<CLASSIFICATION>'.` |
| Tabel | `mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 7 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT tp_kategori, SUM(tp_jml_temuan) AS total_temuan_produk, SUM(tp_harga_total) AS total_nilai_temuan FROM mv_pemeriksaan_temuan WHERE LOWER(tp_kategori) LIKE '%lain - lain%' GROUP BY 1;
```

### [106] tampilkan total temuan produk dan total nilai temuan pada kategori bahan berbahaya.

| | |
|---|---|
| Bentuk NER | `tampilkan total temuan produk dan total nilai temuan pada kategori <CLASSIFICATION>.` |
| Tabel | `mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 10 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT tp_kategori, SUM(tp_jml_temuan) AS total_temuan_produk, SUM(tp_harga_total) AS total_nilai_temuan FROM mv_pemeriksaan_temuan WHERE LOWER(tp_kategori) LIKE '%bahan berbahaya%' GROUP BY 1;
```

### [107] tampilkan total temuan produk dan total nilai temuan pada kategori kedaluarsa.

| | |
|---|---|
| Bentuk NER | `tampilkan total temuan <PRODUCT NAME> dan total nilai temuan pada kategori kedaluarsa.` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 22 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mpt.tp_kategori, sum(mpt.tp_harga_total) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mpt.tp_kategori) LIKE '%kedaluwarsa%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1;
```

### [108] tampilkan total temuan produk dan total nilai temuan pada kategori kedaluarsa.

| | |
|---|---|
| Bentuk NER | `tampilkan total temuan <PRODUCT NAME> dan total nilai temuan pada kategori kedaluarsa.` |
| Tabel | `mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 22 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT tp_kategori, SUM(tp_jml_temuan) AS total_temuan_produk, SUM(tp_harga_total) AS total_nilai_temuan FROM mv_pemeriksaan_temuan WHERE LOWER(tp_kategori) LIKE '%kedaluwarsa%' GROUP BY 1;
```

### [109] tampilkan total temuan produk dan total nilai temuan pada kategori lainnya.

| | |
|---|---|
| Bentuk NER | `tampilkan total temuan <PRODUCT NAME> dan total nilai temuan pada kategori lainnya.` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 7 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mpt.tp_kategori, sum(mpt.tp_harga_total) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mpt.tp_kategori) LIKE '%lain - lain%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1;
```

### [110] tampilkan total temuan produk dan total nilai temuan pada kategori tanpa izin edar.

| | |
|---|---|
| Bentuk NER | `tampilkan total temuan <PRODUCT NAME> dan total nilai temuan pada kategori tanpa izin edar.` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 50 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mpt.tp_kategori, sum(mpt.tp_harga_total) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mpt.tp_kategori) LIKE '%tie%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1;
```

### [111] tampilkan total temuan produk dan total nilai temuan pada kategori tanpa izin edar.

| | |
|---|---|
| Bentuk NER | `tampilkan total temuan <PRODUCT NAME> dan total nilai temuan pada kategori tanpa izin edar.` |
| Tabel | `mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 50 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT tp_kategori, SUM(tp_jml_temuan) AS total_temuan_produk, SUM(tp_harga_total) AS total_nilai_temuan FROM mv_pemeriksaan_temuan WHERE LOWER(tp_kategori) LIKE '%tie%' GROUP BY 1;
```

### [112] upt mana saja yang paling banyak melaporkan hasil pemeriksaan sarana produksi yang tmk?

| | |
|---|---|
| Bentuk NER | `upt mana saja yang paling banyak melaporkan hasil pemeriksaan <FACILITY TYPE> yang tmk?` |
| Tabel | `mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 10 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_upt, count(*) FROM public.mv_pemeriksaan WHERE sarana ILIKE '%produksi%' AND kesimpulan = 'TMK' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY nama_upt ORDER BY COUNT(*) DESC LIMIT 10;
```

### [113] upt mana saja yang paling banyak melaporkan hasil pemeriksaan sarana yang tmk?

| | |
|---|---|
| Bentuk NER | `upt mana saja yang paling banyak melaporkan hasil pemeriksaan <FACILITY TYPE> yang tmk?` |
| Tabel | `mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 5 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_upt, kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND lower(kesimpulan) = 'tmk' GROUP BY 1, 2 ORDER BY 3 DESC LIMIT 5;
```

### [114] upt mana saja yang sering melaporkan hasil pemeriksaan lebih dari 30 hari kerja dari tanggal pemeriksaan hingga tanggal kirim ka upt?

| | |
|---|---|
| Bentuk NER | `upt mana saja yang sering melaporkan hasil pemeriksaan lebih dari 30 hari kerja dari tanggal pemeriksaan hingga tanggal kirim ka upt?` |
| Tabel | `mv_pemeriksaan_log + generate_series + hari + waktu + kerja + mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 13,347 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
WITH waktu AS ( SELECT mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 2) AS t2, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS t3 FROM public.mv_pemeriksaan_log AS mpl GROUP BY mpl.id_pemeriksaan ), kerja AS ( SELECT w.id_pemeriksaan, w.t2, w.t3, ( SELECT COUNT(*) FROM generate_series(w.t2::date, w.t3::date - 1, '1 day') AS d(hari) WHERE EXTRACT(DOW FROM hari) BETWEEN 1 AND 5 -- Se
```

### [115] upt manakah yang hasil pemeriksaan tmk sarana produksi md nya paling banyak di tahun 2025?

| | |
|---|---|
| Bentuk NER | `upt manakah yang hasil pemeriksaan tmk sarana produksi md nya paling banyak di tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 75 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_upt, jenis_sarana, count(*) FROM mv_pemeriksaan mp WHERE lower(jenis_sarana) LIKE '%pangan md%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2 ORDER BY 3 DESC;
```

---

## Generasi v3 — koneksi `_all_v2` (Nov 2025), skema berlaku

98 pertanyaan.

### [116] Ada berapa sarana produksi AMDK dengan hasil pemeriksaan TMK di wilayah kerja Balai POM di Bogor pada tahun 2024

| | |
|---|---|
| Bentuk NER | `Ada berapa <FACILITY TYPE> dengan hasil pemeriksaan <CONCLUSION TYPE> di wilayah kerja Balai POM di <REGENCY NAME> pada tahun <YEAR>` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_jenis_pangan + mp` · agregasi: ya |
| Status | OK → **OK** · 1 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT COUNT(DISTINCT mp.id) AS jumlah_sarana_tmk FROM mv_pemeriksaan mp JOIN mv_pemeriksaan_jenis_pangan mpjp ON mp.id = mpjp.id_pemeriksaan WHERE EXTRACT(YEAR FROM mp.tanggal_mulai) = 2024 AND LOWER(mp.nama_upt) LIKE '%bogor%' AND LOWER(mp.sarana) LIKE '%produksi%' AND LOWER(mpjp.jenis_pangan_name) LIKE '%air minum dalam kemasan%' AND UPPER(mp.kesimpulan) = 'TMK';
```

### [117] analisis jumlah seluruh sarana produksi dan distribusi (tanpa pengulangan nama yang sama) per komoditi produk (obat/oba/sk/kos/po) yang telah diperiksa bpom dalam periode 2025

| | |
|---|---|
| Bentuk NER | `analisis jumlah seluruh sarana produksi dan distribusi (tanpa pengulangan nama yang sama) per komoditi produk (<COMMODITY NAME>/<COMMODITY NAME>/<COMM` |
| Tabel | `mv_pemeriksaan + mp` · agregasi: ya |
| Status | OK → **OK** · 46 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT sarana, komoditi, kesimpulan, count(DISTINCT nama_sarana) FROM public.mv_pemeriksaan mp WHERE (lower(sarana) LIKE '%produksi%' OR lower(sarana) LIKE '%distribusi%') AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 GROUP BY 1, 2, 3;
```

### [118] apa temuan/ketidaksesuaian yang paling banyak ditemukan dari hasil pemeriksaan sarana produksi md?

| | |
|---|---|
| Bentuk NER | `apa temuan/ketidaksesuaian yang paling banyak ditemukan dari hasil pemeriksaan <FACILITY TYPE>?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 6 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT jenis_sarana, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(jenis_sarana) LIKE '%pangan md%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2 ORDER BY 3 DESC;
```

### [119] apa temuan/ketidaksesuaian yang paling banyak ditemukan pada seluruh sarana distribusi tmk di wilayah kerja balai pom di payakumbuh?

| | |
|---|---|
| Bentuk NER | `apa temuan/ketidaksesuaian yang paling banyak ditemukan pada seluruh sarana distribusi tmk di wilayah kerja balai pom di <REGENCY NAME>?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 8 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT kabupaten_kota, mp.sarana, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(kabupaten_kota) LIKE '%payakumbuh%' AND lower(mp.sarana) LIKE '%distribusi%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3 ORDER BY 4 DESC;
```

### [120] bagaimana riwayat pemeriksaan sarana alfamart dalam periode tahun 2024?

| | |
|---|---|
| Bentuk NER | `bagaimana riwayat pemeriksaan sarana <COMPANY NAME> dalam periode tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 583 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, alamat, tanggal_mulai, tanggal_selesai, jenis_sarana, tujuan_pemeriksaan, kesimpulan FROM public.mv_pemeriksaan WHERE LOWER(nama_sarana) LIKE '%alfamart%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ORDER BY tanggal_mulai;
```

### [121] bagaimana tren data hasil pengawasan sarana obat tradisional; suplemen kesehatan; obat kuasi dalam periode tahun 2025?

| | |
|---|---|
| Bentuk NER | `bagaimana tren data hasil pengawasan sarana <COMMODITY NAME>; <COMMODITY NAME>; <COMMODITY NAME> dalam periode tahun <YEAR>?` |
| Tabel | `mp + mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 246 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT EXTRACT(MONTH FROM mp.tanggal_mulai), sarana, komoditi, kesimpulan, count(nama_sarana) FROM public.mv_pemeriksaan mp WHERE (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 GROUP BY 1, 2, 3, 4;
```

### [122] bagaimana tren data hasil pengawasan sarana obat tradisional; suplemen kesehatan; obat kuasi yang tidak memenuhi ketentuan berdasarkan kategori temuan (tmk tie/cpotb/cpotb habis/tidak memiliki cpotb) 

| | |
|---|---|
| Bentuk NER | `bagaimana tren data hasil pengawasan <COMMODITY NAME>; <COMMODITY NAME>; <COMMODITY NAME> yang tidak memenuhi ketentuan berdasarkan kategori temuan (<` |
| Tabel | `tanggal_mulai + mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 281 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT EXTRACT(MONTH FROM tanggal_mulai) AS bulan, mp.sarana, mp.komoditi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') GROUP BY 1, 2, 3, 4;
```

### [123] bagaimana tren data hasil pengawasan sarana produksi kosmetik (profil hasil pengawasan) di upt balai pom di palembang dalam periode tahun 2024?

| | |
|---|---|
| Bentuk NER | `bagaimana tren data hasil pengawasan <FACILITY TYPE> (profil hasil pengawasan) di <HALL NAME> di <CITY NAME> dalam periode tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + mp` · agregasi: tidak |
| Status | OK → **OK** · 1,104 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.nama_upt, tanggal_mulai, nama_sarana, jenis_sarana, kesimpulan FROM public.mv_pemeriksaan mp WHERE lower(nama_upt) LIKE '%palembang%' AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2024 AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ORDER BY 1, 2, 3, 4;
```

### [124] bagaimana tren data hasil pengawasan sarana produksi kosmetik yang memenuhi ketentuan dan tidak memenuhi ketentuan dalam periode tahun 2024?

| | |
|---|---|
| Bentuk NER | `bagaimana tren data hasil pengawasan sarana produksi kosmetik yang memenuhi ketentuan dan tidak memenuhi ketentuan dalam periode tahun <YEAR>?` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 31 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS bulan, kesimpulan, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND lower(komoditi) like '%kosmetik%' AND lower(sarana) like '%produksi%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1,2,3 ORDER BY 1,2,3;
```

### [125] bagaimana tren data hasil pengawasan sarana produksi kosmetik yang tidak memenuhi ketentuan berdasarkan kategori temuan (tmk tie/cpkb/cpkb habis/tidak memiliki cpkb) dalam periode tahun 2025?

| | |
|---|---|
| Bentuk NER | `bagaimana tren data hasil pengawasan <FACILITY TYPE> yang tidak memenuhi ketentuan berdasarkan kategori temuan (<CLASSIFICATION>) dalam periode tahun ` |
| Tabel | `tanggal_mulai + mv_pemeriksaan + mv_pemeriksaan_kategori_temuan` · agregasi: ya |
| Status | OK → **OK** · 22 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT EXTRACT(MONTH FROM tanggal_mulai) AS bulan, mp.sarana, mp.komoditi, mpkt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN mv_pemeriksaan_kategori_temuan mpkt ON mp.id = mpkt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(komoditi) like '%kosmetik%' AND lower(sarana) like '%produksi%' GROUP BY 1, 2, 3, 4;
```

### [126] bagaimana tren hasil pemeriksaan sarana peredaran sejak tahun 2025

| | |
|---|---|
| Bentuk NER | `bagaimana tren hasil pemeriksaan sarana peredaran sejak tahun <YEAR>` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 53 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS BULAN, sarana, kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE lower(sarana) LIKE '%distribusi%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3, 4 ORDER BY 1, 2, 3, 4;
```

### [127] bagaimana tren hasil pemeriksaan sarana produksi md dan pirt sejak tahun 2024 hingga 2025?

| | |
|---|---|
| Bentuk NER | `bagaimana tren hasil pemeriksaan <FACILITY TYPE> dan <FACILITY TYPE> sejak tahun <YEAR> hingga <YEAR>?` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 48 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS bulan, jenis_sarana, count(*) FROM mv_pemeriksaan mp WHERE (lower(jenis_sarana) LIKE '%pangan md%' OR lower(jenis_sarana) LIKE '%pangan irt%') AND EXTRACT(YEAR FROM tanggal_mulai) BETWEEN 2024 AND 2025 AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3 ORDER BY 1, 2, 3;
```

### [128] berapa jumlah sarana yang diperiksa dalam rangka kasus di wilayah kerja bbpom di bandung pada tahun 2024?

| | |
|---|---|
| Bentuk NER | `berapa jumlah <FACILITY TYPE> yang diperiksa dalam rangka kasus di wilayah kerja bbpom di <CITY NAME> pada tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + mp` · agregasi: tidak |
| Status | OK → **OK** · 11 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_upt, nama_sarana, tujuan_pemeriksaan, mp.kesimpulan FROM public.mv_pemeriksaan mp WHERE lower(tujuan_pemeriksaan) LIKE '%kasus%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND lower(kabupaten_kota) LIKE '%bandung%' AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2024;
```

### [129] berapa total sarana yang tutup dan/atau tidak berproduksi saat diperiksa di tahun 2024 di wilayah kerja jakarta utara?

| | |
|---|---|
| Bentuk NER | `berapa total sarana yang tutup dan/atau tidak berproduksi saat diperiksa di tahun <YEAR> di wilayah kerja <CITY NAME>?` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 3 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT kabupaten_kota, nama_sarana, tanggal_mulai, kesimpulan FROM public.mv_pemeriksaan WHERE kesimpulan = 'TTP' AND lower(sarana) LIKE '%produksi%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND lower(kabupaten_kota) ILIKE '%jakarta utara%';
```

### [130] Berdasarkan hasil pemeriksaan selama 2 tahun terakhir, untuk sarana produksi dengan jenis pangan AMDK di seluruh Indonesia 10 temuan yang terbanyak adalah kategori apa?

| | |
|---|---|
| Bentuk NER | `Berdasarkan hasil pemeriksaan selama 2 tahun terakhir, untuk <FACILITY TYPE> dengan jenis pangan <PRODUCT NAME> di seluruh <COUNTRY NAME> 10 temuan ya` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_jenis_pangan + mp + current_date + mv_pemeriksaan_kategori_temuan + pemeriksaan_amdk` · agregasi: ya |
| Status | OK → **OK** · 1 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
WITH pemeriksaan_amdk AS ( SELECT mp.id FROM mv_pemeriksaan mp JOIN mv_pemeriksaan_jenis_pangan mpjp ON mp.id = mpjp.id_pemeriksaan WHERE LOWER(mp.sarana) LIKE '%produksi%' AND LOWER(mpjp.jenis_pangan_name) LIKE '%air minum dalam kemasan%' AND EXTRACT(YEAR FROM mp.tanggal_mulai) >= EXTRACT(YEAR FROM CURRENT_DATE) - 1 ) SELECT mpkt.tp_kategori, COUNT(*) AS jumlah_temuan FROM mv_pemeriksaan_kategori_temuan mpkt JOIN pe
```

### [131] Berikan temuan inspeksi CPOB berdasarkan tingkat pemenuhan CPOB

| | |
|---|---|
| Bentuk NER | `Berikan temuan inspeksi CPOB berdasarkan tingkat pemenuhan CPOB` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: tidak |
| Status | OK → **OK** · 5 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
select mp.tingkat_pemenuhan_cpob, mpt.tp_kategori, mpt.product_name, mpt.tp_harga_total from mv_pemeriksaan mp join mv_pemeriksaan_temuan mpt on mp.id = mpt.id_pemeriksaan where mp.tingkat_pemenuhan_cpob is not null
```

### [132] Berikan tingkat pemenuhan CPOB terhadap seluruh fasilitas produksi pada tahun 2025

| | |
|---|---|
| Bentuk NER | `Berikan tingkat pemenuhan CPOB terhadap seluruh <FACILITY TYPE> pada tahun <YEAR>` |
| Tabel | `mv_pemeriksaan + mp` · agregasi: ya |
| Status | OK → **OK** · 5 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
select sarana, mp.tingkat_pemenuhan_cpob, count(*) from mv_pemeriksaan mp where extract(year from mp.tanggal_mulai) = 2025 and lower(mp.sarana) like '%produksi%' group by 1, 2 order by 1, 2
```

### [133] count pemeriksaan untuk tiap inspektur beserta tujuan dan nama balainya untuk tahun 2025

| | |
|---|---|
| Bentuk NER | `count pemeriksaan untuk tiap inspektur beserta tujuan dan nama balainya untuk tahun <YEAR>` |
| Tabel | `mv_pemeriksaan_petugas + mpp` · agregasi: ya |
| Status | OK → **OK** · 5,112 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
select mpp.daftar_balai_pemeriksa, mpp.petugas, mpp.tujuan, count(*) from mv_pemeriksaan_petugas mpp where extract(year from mpp.tgl_surat) = 2025 group by 1, 2, 3 order by 1, 2, 3
```

### [134] Dari seluruh UPT, sarana produksi MD dengan jenis pangan apa yang paling banyak TMK di tahun 2025?

| | |
|---|---|
| Bentuk NER | `Dari seluruh <FACILITY TYPE>, sarana produksi <COMMODITY NAME> dengan jenis pangan apa yang paling banyak TMK di tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan_jenis_pangan + mv_pemeriksaan + mp` · agregasi: ya |
| Status | OK → **OK** · 10 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
select mpjp.jenis_pangan_name, count(*) from mv_pemeriksaan_jenis_pangan mpjp join mv_pemeriksaan mp on mpjp.id_pemeriksaan = mp.id where lower(mp.jenis_sarana) like '%pangan md%' and lower(mp.sarana) = 'produksi' and lower(mp.kesimpulan) = 'tmk' and extract(year from mp.tanggal_selesai) = 2025 group by 1 order by 2 desc limit 10
```

### [135] Jumlah sarana distribusi pada Balai POM di Jakarta tahun 2025 yang memiliki Nomor Notifikasi baik yang memenuhi ketentuan dan tidak memenuhi ketentuan

| | |
|---|---|
| Bentuk NER | `Jumlah sarana distribusi pada <HALL NAME> di <CITY NAME> tahun <YEAR> yang memiliki Nomor Notifikasi baik yang memenuhi ketentuan dan tidak memenuhi k` |
| Tabel | `mv_pemeriksaan + mp` · agregasi: ya |
| Status | OK → **OK** · 10 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.nama_upt, mp.klasifikasi_distribusi, mp.kesimpulan, COUNT(*) AS jumlah FROM mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM mp.tanggal_selesai) = 2025 AND LOWER(mp.nama_upt) LIKE '%jakarta%' AND ( LOWER(mp.klasifikasi_distribusi) LIKE '%notifikasi%' OR LOWER(mp.klasifikasi_distribusi) LIKE '%importir%' ) GROUP BY 1, 2, 3
```

### [136] Jumlah sarana distribusi pada Balai POM di Jakarta tahun 2025 yang tidak memiliki Nomor Notifikasi baik yang memenuhi ketentuan dan tidak memenuhi ketentuan

| | |
|---|---|
| Bentuk NER | `Jumlah sarana distribusi pada <HALL NAME> di <CITY NAME> tahun <YEAR> yang tidak memiliki Nomor Notifikasi baik yang memenuhi ketentuan dan tidak meme` |
| Tabel | `mv_pemeriksaan + mp` · agregasi: ya |
| Status | OK → **OK** · 27 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.nama_upt, mp.klasifikasi_distribusi, mp.kesimpulan, COUNT(*) AS jumlah FROM mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM mp.tanggal_selesai) = 2025 AND LOWER(mp.nama_upt) LIKE '%jakarta%' AND ( LOWER(mp.klasifikasi_distribusi) NOT LIKE '%notifikasi%' OR LOWER(mp.klasifikasi_distribusi) NOT LIKE '%importir%' ) GROUP BY 1, 2, 3
```

### [137] Jumlah temuan produk dan nilai temuannya dikategorikan berdasarkan Bahan Berbahaya, TIE, Kedaluarsa, dll

| | |
|---|---|
| Bentuk NER | `Jumlah temuan produk dan nilai temuannya dikategorikan berdasarkan <CLASSIFICATION>, <CLASSIFICATION>, <CLASSIFICATION>, dll` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 99 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
select komoditi, mpt.tp_kategori, count(*), sum(mpt.tp_harga_total) from mv_pemeriksaan mp join mv_pemeriksaan_temuan mpt on mp.id = mpt.id_pemeriksaan where mp.klasifikasi_distribusi is not null group by 1, 2
```

### [138] merekap jumlah dan nama sarana distribusi dan pelayanan yang Tidak pernah diperiksa dalam kurun waktu 1 tahun terakhir

| | |
|---|---|
| Bentuk NER | `merekap jumlah dan nama sarana distribusi dan pelayanan yang Tidak pernah diperiksa dalam kurun waktu 1 tahun terakhir` |
| Tabel | `mv_pemeriksaan` · agregasi: tidak |
| Status | OK → **OK** · 146,493 baris |
| Lapis terjemahan | - |
| Diagnosa | **⚠️ Jalan tapi >100rb baris tanpa agregasi** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah. TAPI hasilnya 146,493 baris tanpa agregasi — jalan, bukan jawaban |

```sql
SELECT DISTINCT nama_sarana, komoditi, tanggal_mulai FROM public.mv_pemeriksaan mp WHERE (lower(sarana) LIKE '%distribusi%' OR lower(sarana) LIKE '%pelayanan%') AND mp.nama_sarana NOT IN ( SELECT nama_sarana FROM public.mv_pemeriksaan WHERE tanggal_mulai >= NOW() - INTERVAL '1 year' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ) ORDER BY nama_sarana;
```

### [139] Riwayat kepatuhan CPOB dari Soho Industri Pharmasi dalam periode 2 tahun pengawasan

| | |
|---|---|
| Bentuk NER | `Riwayat kepatuhan CPOB dari <COMPANY NAME> dalam periode 2 tahun pengawasan` |
| Tabel | `mv_pemeriksaan` · agregasi: tidak |
| Status | OK → **OK** · 12 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
select mp.tanggal_mulai, nama_sarana, kabupaten_kota, mp.tingkat_pemenuhan_cpob from mv_pemeriksaan mp where mp.tingkat_pemenuhan_cpob is not null and status in ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') and lower(nama_sarana) like '%soho industri%' order by 1, 2, 3
```

### [140] Sarana BUPN Apa saja yang pernah diperiksa?

| | |
|---|---|
| Bentuk NER | `Sarana <FACILITY TYPE> Apa saja yang pernah diperiksa?` |
| Tabel | `mv_pemeriksaan` · agregasi: tidak |
| Status | OK → **OK** · 1,112 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
select distinct(nama_sarana), sarana, klasifikasi_sarana, klasifikasi_distribusi from mv_pemeriksaan mp where mp.klasifikasi_distribusi = 'BADAN USAHA/USAHA PERORANGAN PEMILIK NOTIFIKASI KOSMETIK'
```

### [141] sarana distribusi apa saja yang pernah memiliki riwayat memenuhi ketentuan berdasarkan tahun temuannya?

| | |
|---|---|
| Bentuk NER | `sarana distribusi apa saja yang pernah memiliki riwayat memenuhi ketentuan berdasarkan tahun temuannya?` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: tidak |
| Status | OK → **OK** · 99,586 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, sarana, EXTRACT(YEAR FROM tanggal_mulai) AS tahun_temuan FROM mv_pemeriksaan WHERE lower(sarana) = 'distribusi' AND kesimpulan = 'MK' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ORDER BY 1, 2;
```

### [142] sarana distribusi apa saja yang pernah memiliki riwayat tidak memenuhi ketentuan berdasarkan tahun temuannya?

| | |
|---|---|
| Bentuk NER | `sarana distribusi apa saja yang pernah memiliki riwayat tidak memenuhi ketentuan berdasarkan tahun temuannya?` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: tidak |
| Status | OK → **OK** · 36,358 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, sarana, EXTRACT(YEAR FROM tanggal_mulai) AS tahun_temuan FROM mv_pemeriksaan WHERE lower(sarana) = 'distribusi' AND kesimpulan = 'TMK' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ORDER BY 1, 2;
```

### [143] sarana distribusi kosmetik apa saja yang pernah diperiksa oleh badan pom setiap tahun dari tahun 2020 hingga 2024?

| | |
|---|---|
| Bentuk NER | `<FACILITY TYPE> apa saja yang pernah diperiksa oleh badan pom setiap tahun dari tahun <YEAR> hingga <YEAR>?` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: tidak |
| Status | OK → **OK** · 35,566 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, EXTRACT(YEAR FROM tanggal_mulai) AS tahun FROM mv_pemeriksaan WHERE lower(sarana) = 'distribusi' AND LOWER(komoditi) LIKE '%kosmetik%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ORDER BY 2;
```

### [144] sarana distribusi kosmetik apa saja yang pernah diperiksa oleh badan pom?

| | |
|---|---|
| Bentuk NER | `<FACILITY TYPE> apa saja yang pernah diperiksa oleh <CLASSIFICATION>?` |
| Tabel | `mv_pemeriksaan` · agregasi: tidak |
| Status | OK → **OK** · 23,752 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT DISTINCT (nama_sarana) FROM mv_pemeriksaan WHERE lower(sarana) = 'distribusi' AND LOWER(komoditi) LIKE '%kosmetik%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED');
```

### [145] Sarana Importir apa saja yang pernah diperiksa?

| | |
|---|---|
| Bentuk NER | `<FACILITY TYPE> apa saja yang pernah diperiksa?` |
| Tabel | `mv_pemeriksaan` · agregasi: tidak |
| Status | OK → **OK** · 1,289 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
select distinct(nama_sarana), klasifikasi_distribusi from mv_pemeriksaan mp where lower(mp.klasifikasi_distribusi) like '%importir%'
```

### [146] sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang memiliki riwayat pemeriksaan tidak memenuhi ketentuan dalam periode tahun 2025?

| | |
|---|---|
| Bentuk NER | `sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang memiliki riwayat pemeriksaan tidak memenuhi ketentuan dalam periode tahun <YEAR>` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 4,571 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT DISTINCT mp.nama_sarana, mp.sarana, mp.komoditi FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND lower(kesimpulan) = 'tmk';
```

### [147] sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang pernah memproduksi dan mengedarkan obat tradisional; suplemen kesehatan; obat kuasi tie dalam periode tahun 2025?

| | |
|---|---|
| Bentuk NER | `sarana <COMMODITY NAME>; <COMMODITY NAME>; <COMMODITY NAME> apa saja yang pernah memproduksi dan mengedarkan <COMMODITY NAME>; <COMMODITY NAME>; <COMM` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 26,549 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.nama_sarana, mpt.product_name, mp.sarana, mp.komoditi, mpt.tp_kategori FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND lower(tp_kategori) LIKE '%tie%';
```

### [148] sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang Tidak dilakukan pemeriksaan dalam periode 2 tahun terakhir?

| | |
|---|---|
| Bentuk NER | `<FACILITY TYPE>; <CLASSIFICATION>; <CLASSIFICATION> apa saja yang Tidak dilakukan pemeriksaan dalam periode 2 tahun terakhir?` |
| Tabel | `mv_pemeriksaan` · agregasi: tidak |
| Status | OK → **OK** · 11,471 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT DISTINCT nama_sarana, komoditi, tanggal_mulai FROM public.mv_pemeriksaan mp WHERE (lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%' OR lower(komoditi) LIKE '%obat kuasi%') AND mp.nama_sarana NOT IN ( SELECT nama_sarana FROM public.mv_pemeriksaan WHERE tanggal_mulai >= NOW() - INTERVAL '2 year' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ) ORDER BY
```

### [149] sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang tutup dalam periode tahun 2025?

| | |
|---|---|
| Bentuk NER | `sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang tutup dalam periode tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 107 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, kesimpulan FROM public.mv_pemeriksaan mp WHERE mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND lower(kesimpulan) = 'ttp' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
```

### [150] sarana produksi kosmetik apa saja yang memiliki riwayat pemeriksaan tidak memenuhi ketentuan dalam periode tahun 2025?

| | |
|---|---|
| Bentuk NER | `sarana produksi kosmetik apa saja yang memiliki riwayat pemeriksaan tidak memenuhi ketentuan dalam periode tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 131 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.sarana, mp.nama_sarana, mp.tanggal_mulai, mp.kesimpulan FROM public.mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(komoditi) like '%kosmetik%' AND lower(sarana) like '%produksi%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED');
```

### [151] sarana produksi kosmetik apa saja yang pernah memproduksi dan mengedarkan kosmetik tie dalam periode tahun 2025?

| | |
|---|---|
| Bentuk NER | `sarana produksi kosmetik apa saja yang pernah memproduksi dan mengedarkan <PRODUCT NAME> dalam periode tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_kategori_temuan + mp` · agregasi: tidak |
| Status | OK → **OK** · 57 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.sarana, mp.nama_sarana, mp.tanggal_mulai, mpkt.tp_kategori FROM public.mv_pemeriksaan mp LEFT JOIN public.mv_pemeriksaan_kategori_temuan mpkt ON mp.id = mpkt.id_pemeriksaan WHERE EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND lower(mp.komoditi) LIKE '%kosmetik%' AND lower(mp.sarana) LIKE '%produksi%' AND lower(mpkt.tp_kategori) LIKE '%tie%' AND mp.status IN ('VERIFY4', 'VERIFY5', 'VERIFY6', 'VERIFY7', 'FINI
```

### [152] sarana produksi kosmetik apa saja yang Tidak dilakukan pemeriksaan dalam periode 2 tahun terakhir?

| | |
|---|---|
| Bentuk NER | `sarana produksi kosmetik apa saja yang Tidak dilakukan pemeriksaan dalam periode <YEAR>?` |
| Tabel | `mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 607 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, MAX(tanggal_mulai) AS terakhir_diperiksa FROM mv_pemeriksaan WHERE komoditi ILIKE '%kosmetik%' AND sarana ILIKE 'produksi' GROUP BY nama_sarana HAVING COALESCE(MAX(tanggal_mulai), DATE '-infinity') < (CURRENT_DATE - INTERVAL '2 years') ORDER BY terakhir_diperiksa NULLS FIRST, nama_sarana;
```

### [153] sarana produksi kosmetik apa saja yang tutup dalam periode tahun 2025?

| | |
|---|---|
| Bentuk NER | `sarana produksi kosmetik apa saja yang tutup dalam periode tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 4 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, tanggal_mulai, kesimpulan FROM public.mv_pemeriksaan WHERE LOWER(sarana) LIKE '%produksi%' AND LOWER(komoditi) LIKE '%kosmetik%' AND kesimpulan = 'TTP' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
```

### [154] sarana produksi md apa yang paling sering memiliki riwayat tmk?

| | |
|---|---|
| Bentuk NER | `<FACILITY TYPE> md apa yang paling sering memiliki riwayat tmk?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 10 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, jenis_sarana, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(jenis_sarana) LIKE '%pangan md%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3 ORDER BY 4 DESC LIMIT 10;
```

### [155] sebutkan sarana distribusi yang tutup tahun 2025?

| | |
|---|---|
| Bentuk NER | `sebutkan sarana distribusi yang tutup tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 79 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, tanggal_mulai FROM public.mv_pemeriksaan WHERE sarana = 'DISTRIBUSI' AND kesimpulan = 'TTP' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
```

### [156] sebutkan sarana distribusi yang tutup tahun 2025?

| | |
|---|---|
| Bentuk NER | `sebutkan sarana distribusi yang tutup tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 79 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, tanggal_mulai, kesimpulan FROM mv_pemeriksaan WHERE LOWER(sarana) = 'distribusi' AND LOWER(kesimpulan) = 'ttp' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
```

### [157] tampilkan aspek temuan yang berulang dari tahun ke tahun pada sarana dengan nama siloam.

| | |
|---|---|
| Bentuk NER | `tampilkan aspek temuan yang berulang dari tahun ke tahun pada sarana dengan nama <COMPANY NAME>.` |
| Tabel | `tanggal_mulai + mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 2 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.nama_sarana, mp.sarana, mpt.tp_kategori, EXTRACT(YEAR FROM tanggal_mulai) AS tahun, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(nama_sarana) LIKE '%siloam%' GROUP BY 1, 2, 3, 4;
```

### [158] tampilkan daftar sarana dengan hasil tmk berulang lebih dari sekali pada kurun 5 tahun terakhir hingga saat ini pada wilayah kerja balai pom di tangerang

| | |
|---|---|
| Bentuk NER | `tampilkan daftar <FACILITY TYPE> dengan hasil tmk berulang lebih dari sekali pada kurun 5 tahun terakhir hingga saat ini pada wilayah kerja balai pom ` |
| Tabel | `tanggal_mulai + mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 530 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, mp.nama_sarana, mp.sarana, kabupaten_kota, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.kabupaten_kota) LIKE '%tangerang%' AND mp.tanggal_mulai >= (CURRENT_DATE - INTERVAL '5 years') GROUP BY 1, 2, 3, 4, 5 HAVING COUNT(*) > 1 ORDER BY 1, 2, 3, 4, 5;
```

### [159] tampilkan data jumlah pemeriksaan sarana peredaran oleh adiyati pada tahun 2025

| | |
|---|---|
| Bentuk NER | `tampilkan data jumlah pemeriksaan sarana peredaran oleh adiyati pada tahun <YEAR>` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_petugas + t1` · agregasi: ya |
| Status | OK → **OK** · 1 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT T2.petugas, sarana, COUNT(T1.id) FROM public.mv_pemeriksaan AS T1 INNER JOIN public.mv_pemeriksaan_petugas AS T2 ON T1.id = T2.id_pemeriksaan WHERE LOWER(T1.sarana) like '%distribusi%' AND lower(T2.petugas) LIKE '%adiyati%' AND EXTRACT(YEAR FROM T1.tanggal_mulai) = 2025 GROUP BY 1, 2;
```

### [160] tampilkan data profil jenis sarana yang sudah dilakukan pemeriksaan dari tahun 2025

| | |
|---|---|
| Bentuk NER | `tampilkan data profil jenis sarana yang sudah dilakukan pemeriksaan dari tahun <YEAR>` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 421 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.jenis_sarana, mp.kesimpulan, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3;
```

### [161] Tampilkan data realisasi inspeksi pada tahun 2025 yang dilaksanakan oleh pusat maupun UPT secara mandiri

| | |
|---|---|
| Bentuk NER | `Tampilkan data realisasi inspeksi pada tahun <YEAR> yang dilaksanakan oleh pusat maupun UPT secara mandiri` |
| Tabel | `mv_pemeriksaan + mp` · agregasi: ya |
| Status | OK → **OK** · 719 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
select mp.nama_upt, sarana, mp.komoditi, count(*) from mv_pemeriksaan mp where extract(year from mp.tanggal_mulai) = 2025 group by 1, 2, 3 order by 1, 3, 3
```

### [162] Tampilkan hasil tingkat kekritisan berdasarkan klasifikasi dan tujuan pemeriksaan

| | |
|---|---|
| Bentuk NER | `Tampilkan hasil <CLASSIFICATION> berdasarkan klasifikasi dan <PURPOSE TYPE>` |
| Tabel | `mv_kriteria_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 53 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
select mkp.klasifikasi, mkp.tujuan, mkp.tx_criteria, count(*) from mv_kriteria_pemeriksaan mkp group by 1, 2, 3 order by 1, 2, 3
```

### [163] tampilkan jenis sarana yang paling banyak diperiksa pada tahun 2025.

| | |
|---|---|
| Bentuk NER | `tampilkan jenis sarana yang paling banyak diperiksa pada tahun <YEAR>.` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 21 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT sarana, jenis_sarana, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY 1, 2 ORDER BY 3 DESC;
```

### [164] tampilkan jumlah dan nama sarana distribusi dan pelayanan yang mk/tmk masing-masing upt pada tahun 2025.

| | |
|---|---|
| Bentuk NER | `tampilkan jumlah dan nama <FACILITY TYPE> yang mk/tmk masing-masing upt pada tahun <YEAR>.` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 4,527 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, sarana, kesimpulan, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE (lower(sarana) LIKE '%distribusi%' OR lower(sarana) LIKE '%pelayanan%') AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3;
```

### [165] tampilkan jumlah inspeksi rutin kategori mk dan tmk per periode 2025

| | |
|---|---|
| Bentuk NER | `tampilkan jumlah inspeksi rutin kategori <CLASSIFICATION> dan <CLASSIFICATION> per periode <YEAR>` |
| Tabel | `mv_pemeriksaan + mp` · agregasi: ya |
| Status | OK → **OK** · 6 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT tujuan_pemeriksaan, mp.kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE lower(tujuan_pemeriksaan) LIKE '%rutin%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 GROUP BY 1, 2;
```

### [166] tampilkan jumlah nilai temuan produk sarana distribusi pada tahun 2025 dalam rupiah?

| | |
|---|---|
| Bentuk NER | `tampilkan jumlah nilai temuan produk <PRODUCT NAME> pada tahun <YEAR> dalam rupiah?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 89 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.sarana, mp.komoditi, mpt.tp_kategori, sum(mpt.tp_harga_total) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(sarana) like '%distribusi%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3;
```

### [167] tampilkan jumlah nilai temuan produk sarana distribusi pada tahun 2025?

| | |
|---|---|
| Bentuk NER | `tampilkan jumlah nilai temuan produk sarana distribusi pada tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 90 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.komoditi, mpt.tp_kategori, sum(mpt.tp_harga_total) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(sarana) LIKE '%distribusi%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2;
```

### [168] tampilkan jumlah sarana produksi kategori mk dan tmk per komoditi, periode, wilayah, dan cakupan upt.

| | |
|---|---|
| Bentuk NER | `tampilkan jumlah <FACILITY TYPE> kategori <CLASSIFICATION> dan <CLASSIFICATION> per <COMMODITY NAME>, periode, wilayah, dan cakupan upt.` |
| Tabel | `mp + mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 8,361 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT EXTRACT(YEAR FROM mp.tanggal_mulai), sarana, komoditi, kabupaten_kota, kesimpulan, count(nama_sarana) FROM public.mv_pemeriksaan mp WHERE lower(sarana) LIKE '%produksi%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3, 4, 5;
```

### [169] tampilkan jumlah sarana yang tidak dapat diperiksa di wilayah upt surabaya dan pada tahun 2025

| | |
|---|---|
| Bentuk NER | `tampilkan jumlah sarana yang tidak dapat diperiksa di wilayah upt <CITY NAME> dan pada tahun <YEAR>` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 16 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, kabupaten_kota, kesimpulan, tanggal_mulai FROM public.mv_pemeriksaan WHERE kabupaten_kota ILIKE '%surabaya%' AND kesimpulan = 'TDP' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
```

### [170] tampilkan jumlah temuan produk sarana distribusi pada tahun 2025?

| | |
|---|---|
| Bentuk NER | `tampilkan jumlah temuan produk sarana distribusi pada tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 90 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.komoditi, mpt.tp_kategori, sum(mpt.tp_jml_temuan) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(sarana) LIKE '%distribusi%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2;
```

### [171] tampilkan jumlah temuan produk tmk (tie, rusak, kedaluwarsa) pada sarana peredaran per wilayah kerja masing-masing upt.

| | |
|---|---|
| Bentuk NER | `tampilkan jumlah temuan produk tmk (tie, rusak, kedaluwarsa) pada sarana peredaran per wilayah kerja masing-masing upt.` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 388 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.kabupaten_kota, mpt.tp_kategori, sum(mpt.tp_jml_temuan) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mpt.tp_kategori) LIKE '%lain - lain%' AND lower(kesimpulan) = 'tmk' AND lower(mp.sarana) LIKE '%distribusi%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1,2;
```

### [172] tampilkan ketepatan waktu pelaporan sipt oleh balai besar pom di bandung dengan menampilkan data tanggal pemeriksaan dan tanggal kirim data sipt ke pusat yang kurang dari 30 hari kerja dan lebih dari 

| | |
|---|---|
| Bentuk NER | `tampilkan ketepatan waktu pelaporan sipt oleh <HALL NAME> dengan menampilkan data tanggal pemeriksaan dan tanggal kirim data sipt ke pusat yang kurang` |
| Tabel | `mv_pemeriksaan_log + generate_series + hari + waktu + kerja + mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 10,172 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
WITH waktu AS ( SELECT mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS t3, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 4) AS t4 FROM public.mv_pemeriksaan_log AS mpl GROUP BY mpl.id_pemeriksaan ), kerja AS ( SELECT w.id_pemeriksaan, w.t3, w.t4, ( SELECT COUNT(*) FROM generate_series(w.t3::date, w.t4::date - 1, '1 day') AS d(hari) WHERE EXTRACT(DOW FROM hari) BETWEEN 1 AND 5 -- Se
```

### [173] tampilkan ketepatan waktu pelaporan sipt oleh balai dengan menampilkan data tanggal pemeriksaan dan tanggal kirim data sipt ke pusat yang kurang dari 30 hari kerja dan lebih dari 30 hari kerja untuk b

| | |
|---|---|
| Bentuk NER | `tampilkan ketepatan waktu pelaporan sipt oleh balai dengan menampilkan data tanggal pemeriksaan dan tanggal kirim data sipt ke pusat yang kurang dari ` |
| Tabel | `mv_pemeriksaan_log + generate_series + hari + waktu + kerja + mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 6,704 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
WITH waktu AS ( SELECT mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS t3, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 4) AS t4 FROM public.mv_pemeriksaan_log AS mpl GROUP BY mpl.id_pemeriksaan ), kerja AS ( SELECT w.id_pemeriksaan, w.t3, w.t4, ( SELECT COUNT(*) FROM generate_series(w.t3::date, w.t4::date - 1, '1 day') AS d(hari) WHERE EXTRACT(DOW FROM hari) BETWEEN 1 AND 5 -- Se
```

### [174] tampilkan merek-merek temuan produk kosmetik pada pemeriksaan tahun 2025 diurutkan berdasarkan temuan yang terbanyak?

| | |
|---|---|
| Bentuk NER | `tampilkan merek-merek temuan <PRODUCT NAME> pada pemeriksaan tahun <YEAR> diurutkan berdasarkan temuan yang terbanyak?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 809 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mpt.product_brands, mp.komoditi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND LOWER(komoditi) LIKE '%kosmetik%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3;
```

### [175] tampilkan merek-merek temuan produk obat tradisional; suplemen kesehatan; obat kuasi pada pemeriksaan tahun 2025?

| | |
|---|---|
| Bentuk NER | `tampilkan merek-merek temuan <CLASSIFICATION>; <CLASSIFICATION>; <CLASSIFICATION> pada pemeriksaan tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 198 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mpt.product_brands, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1 ORDER BY 2 DESC;
```

### [176] Tampilkan negara-negara dengan temuan impor pada tahun 2025 negara dengan input text selain indonesia

| | |
|---|---|
| Bentuk NER | `Tampilkan negara-negara dengan temuan impor pada tahun <YEAR> negara dengan input text selain <COUNTRY NAME>` |
| Tabel | `mv_pemeriksaan_temuan + mv_pemeriksaan + mp` · agregasi: ya |
| Status | OK → **OK** · 347 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
select mpt.tp_negara, sum(mpt.tp_harga_total) from mv_pemeriksaan_temuan mpt join mv_pemeriksaan mp on mpt.id_pemeriksaan = mp.id where lower(mpt.tp_negara) != 'indonesia' and mpt.tp_harga_total is not null and extract(year from mp.tanggal_selesai) = 2025 group by 1 order by 2 desc
```

### [177] tampilkan perbandingan jumlah sarana mk dibanding jumlah keseluruhan sarana yang diperiksa pada loka pom di kab. belitung pada triwulan i tahun 2025 dalam bentuk angka dan presentase.

| | |
|---|---|
| Bentuk NER | `tampilkan perbandingan jumlah <FACILITY TYPE> dibanding jumlah keseluruhan <FACILITY TYPE> pada loka pom di <REGENCY NAME> pada triwulan i tahun <YEAR` |
| Tabel | `mv_pemeriksaan + mp` · agregasi: ya |
| Status | OK → **OK** · 1 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT COUNT(*) AS total_sarana, COUNT(CASE WHEN lower(mp.kesimpulan) = 'mk' THEN 1 END) AS jumlah_sarana_mk, CAST( COUNT(CASE WHEN lower(mp.kesimpulan) = 'mk' THEN 1 END) AS NUMERIC ) * 100 / COUNT(*) AS persentase_mk FROM public.mv_pemeriksaan mp WHERE lower(mp.kabupaten_kota) LIKE '%belitung%' AND mp.status IN ('VERIFY4', 'VERIFY5', 'VERIFY6', 'VERIFY7', 'FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 A
```

### [178] tampilkan perbandingan jumlah sarana tmk dibanding jumlah keseluruhan sarana yang diperiksa loka pom di kab. belitung pada triwulan i tahun 2025 dalam bentuk angka dan presentase

| | |
|---|---|
| Bentuk NER | `tampilkan perbandingan jumlah <FACILITY TYPE> dibanding jumlah keseluruhan <FACILITY TYPE> loka pom di <REGENCY NAME> pada triwulan i tahun <YEAR> dal` |
| Tabel | `mv_pemeriksaan + mp` · agregasi: ya |
| Status | OK → **OK** · 1 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT COUNT(*) AS total_sarana, COUNT(CASE WHEN lower(mp.kesimpulan) = 'tmk' THEN 1 END) AS jumlah_sarana_tmk, CAST( COUNT(CASE WHEN lower(mp.kesimpulan) = 'tmk' THEN 1 END) AS NUMERIC ) * 100 / COUNT(*) AS persentase_tmk FROM public.mv_pemeriksaan mp WHERE lower(mp.kabupaten_kota) LIKE '%belitung%' AND mp.status IN ('VERIFY4', 'VERIFY5', 'VERIFY6', 'VERIFY7', 'FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 20
```

### [179] Tampilkan persentase ketepatan grading hasil pemeriksaan di UPT Balai POM di Bogor pada tahun 2025 Grading A -> kesimpulan harus MK Grading B-C -> kesimpulan harus TMK

| | |
|---|---|
| Bentuk NER | `Tampilkan persentase ketepatan grading hasil pemeriksaan di <FACILITY TYPE> di <REGENCY NAME> pada tahun <YEAR> <CLASSIFICATION> -> kesimpulan harus <` |
| Tabel | `mv_pemeriksaan + mp + data_grading` · agregasi: ya |
| Status | OK → **OK** · 3 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
WITH data_grading AS ( SELECT mp.grade, mp.kesimpulan, CASE WHEN UPPER(mp.grade) = 'A' AND UPPER(mp.kesimpulan) = 'MK' THEN 1 WHEN UPPER(mp.grade) IN ('B', 'C') AND UPPER(mp.kesimpulan) = 'TMK' THEN 1 ELSE 0 END AS tepat FROM mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND mp.grade IS NOT NULL AND LOWER(mp.nama_upt) LIKE '%bogor%' ) SELECT grade, COUNT(*) AS total_pemeriksaan, SUM(tepat) AS jum
```

### [180] tampilkan persentase ketepatan waktu pelaporan hasil pemeriksaan dari upt dengan nama Balai POM di Bogor di tw 1 2025 (syarat : tepat waktu jika pelaporan hasil pemeriksaan maksimal tanggal 15 bulan s

| | |
|---|---|
| Bentuk NER | `tampilkan persentase ketepatan waktu pelaporan hasil pemeriksaan dari upt dengan nama <HALL NAME> di <REGENCY NAME> di tw 1 <YEAR> (syarat : tepat wak` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_log + mpl + laporan_q1_2025` · agregasi: ya |
| Status | OK → **OK** · 1 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
WITH laporan_q1_2025 AS ( -- Langkah 1: Ambil data tanggal penting dari Balai POM di Bogor di Q1 2025 SELECT mp.nama_upt, mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 2) AS tanggal_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS tanggal_pelaporan FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_log AS mpl ON mp.id = mpl.id_pemeriksaan WHERE lower(mp.nama_up
```

### [181] Tampilkan persentase ketepatan waktu pelaporan SIPT oleh Balai POM di Bandung

| | |
|---|---|
| Bentuk NER | `Tampilkan persentase ketepatan waktu pelaporan SIPT oleh Balai POM di <CITY NAME>` |
| Tabel | `mv_pemeriksaan + data_sipt` · agregasi: ya |
| Status | OK → **OK** · 2 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
WITH data_sipt AS ( SELECT mp.nama_upt, mp.day_mulai_selesai, CASE WHEN mp.day_mulai_selesai < 30 THEN 'Tepat Waktu' ELSE 'Terlambat' END AS kategori_waktu FROM mv_pemeriksaan mp WHERE LOWER(mp.nama_upt) LIKE '%bandung%' AND mp.day_mulai_selesai IS NOT NULL ) SELECT kategori_waktu, COUNT(*) AS jumlah_laporan, ROUND((COUNT(*)::decimal / NULLIF(SUM(COUNT(*)) OVER (), 0)) * 100, 2) AS persentase FROM data_sipt GROUP BY 
```

### [182] tampilkan persentase mk tmk hasil pemeriksaan sarana pangan olahan md untuk tujuan pemeriksaan pemeriksaan rutin dari seluruh upt di tahun 2025 dalam bentuk diagram batang

| | |
|---|---|
| Bentuk NER | `tampilkan persentase mk tmk hasil pemeriksaan <FACILITY TYPE> untuk tujuan pemeriksaan <PURPOSE TYPE> dari seluruh upt di tahun <YEAR> dalam bentuk di` |
| Tabel | `mv_pemeriksaan + mp` · agregasi: ya |
| Status | OK → **OK** · 197 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_upt, mp.kesimpulan, COUNT(*) FROM public.mv_pemeriksaan mp WHERE lower(jenis_sarana) LIKE '%pangan md%' AND lower(tujuan_pemeriksaan) LIKE '%pemeriksaan rutin%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 GROUP BY 1,2;
```

### [183] Tampilkan profil kepatuhan pelaku usaha sarana produksi dan distribusi per komoditi untuk tahun 2025

| | |
|---|---|
| Bentuk NER | `Tampilkan profil kepatuhan pelaku usaha <FACILITY TYPE> dan <FACILITY TYPE> per <COMMODITY NAME> untuk tahun <YEAR>` |
| Tabel | `mv_pemeriksaan + mp` · agregasi: ya |
| Status | OK → **OK** · 50 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
select sarana, mp.komoditi, mp.kesimpulan, count(*) from mv_pemeriksaan mp where extract(year from mp.tanggal_mulai) = 2025 and lower(mp.sarana) in ('produksi', 'distribusi') group by 1, 2, 3
```

### [184] tampilkan profil pemeriksaan sarana produksi obat dan makanan selama periode 2025 dalam bentuk tabel dan grafik jumlah sarana produksi mk, tmk, tidak dapat dinilai, tutup per jenis komoditi (obat, oba

| | |
|---|---|
| Bentuk NER | `tampilkan profil pemeriksaan <FACILITY TYPE> selama periode <YEAR> dalam bentuk tabel dan grafik jumlah sarana produksi <CLASSIFICATION>, <CLASSIFICAT` |
| Tabel | `tanggal_mulai + mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 111 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS BULAN, sarana, jenis_sarana, kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE lower(sarana) LIKE '%produksi%' AND (lower(jenis_sarana) LIKE '%obat' OR lower(jenis_sarana) LIKE '%pangan%') AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3, 4, 5 OR
```

### [185] tampilkan profil temuan ketidaksesuaian berdasarkan hasil pemeriksaan pada tahun 2025.

| | |
|---|---|
| Bentuk NER | `tampilkan profil temuan ketidaksesuaian berdasarkan hasil pemeriksaan pada tahun <YEAR>.` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 71 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mpt.tp_kategori, count(*) AS jumlah_pemeriksaan, sum(mpt.tp_jml_temuan) AS jumlah_temuan, sum(mpt.tp_harga_total) AS nilai_temuan FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY 1;
```

### [186] Tampilkan proporsi klasifikasi sarana peredaran yang diperiksa di Balai POM di Bandung

| | |
|---|---|
| Bentuk NER | `Tampilkan proporsi klasifikasi sarana peredaran yang diperiksa di <HALL NAME> di <CITY NAME>` |
| Tabel | `mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 5 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
select mp.klasifikasi_sarana, count(*) from mv_pemeriksaan mp where lower(mp.sarana) = 'distribusi' and lower(mp.nama_upt) like '%bandung%' group by 1
```

### [187] Tampilkan realisasi inspeksi sarana distribusi periode pemeriksaan tahun 2025

| | |
|---|---|
| Bentuk NER | `Tampilkan realisasi inspeksi sarana distribusi periode pemeriksaan tahun <YEAR>` |
| Tabel | `target_balai + mp + mv_pemeriksaan + current_date + laporan_dikirim + latest_target_year` · agregasi: ya |
| Status | OK → **OK** · 410 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
WITH latest_target_year AS ( SELECT MAX(tb.tahun) AS tahun_terbaru FROM target_balai tb ), laporan_dikirim AS ( SELECT mp.nama_upt, mp.komoditi, EXTRACT(YEAR FROM mp.tanggal_selesai) AS tahun, COUNT(*) AS jumlah_laporan FROM mv_pemeriksaan mp WHERE mp.tanggal_selesai IS NOT NULL AND EXTRACT(YEAR FROM mp.tanggal_selesai) = EXTRACT(YEAR FROM CURRENT_DATE) and lower(mp.sarana) = 'distribusi' GROUP BY mp.nama_upt, mp.kom
```

### [188] tampilkan rekapitulasi produktivitas penguji (jumlah parameter per orang) dari tanggal 1 januari 2025 hingga 31 desember 2025.

| | |
|---|---|
| Bentuk NER | `tampilkan rekapitulasi produktivitas penguji (jumlah parameter per orang) dari tanggal 1 januari <YEAR> hingga 31 desember <YEAR>.` |
| Tabel | `mv_pemeriksaan_petugas + mpp` · agregasi: ya |
| Status | OK → **OK** · 1,777 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mpp.petugas, count(*) FROM public.mv_pemeriksaan_petugas mpp WHERE EXTRACT(YEAR FROM mpp.tgl_surat) = 2025 GROUP BY 1 ORDER BY 2 DESC;
```

### [189] Tampilkan riwayat pemenuhan CPOB untuk harsen laboratories

| | |
|---|---|
| Bentuk NER | `Tampilkan riwayat pemenuhan CPOB untuk <COMPANY NAME>` |
| Tabel | `mv_pemeriksaan` · agregasi: tidak |
| Status | OK → **OK** · 17 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
select mp.tanggal_selesai, mp.nama_sarana, mp.tingkat_pemenuhan_cpob from mv_pemeriksaan mp where mp.tingkat_pemenuhan_cpob is not null and lower(mp.nama_sarana) like '%harsen laboratories%' order by 1, 2, 3
```

### [190] tampilkan riwayat pemeriksaan sarana produksi 'maha siri jaya' pada rentang tahun yang tersedia.

| | |
|---|---|
| Bentuk NER | `tampilkan riwayat pemeriksaan sarana produksi '<COMPANY NAME>' pada rentang tahun yang tersedia.` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: tidak |
| Status | OK → **OK** · 9 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, sarana, jenis_sarana, mpt.product_name, tanggal_mulai, mpt.tp_kategori FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(sarana) LIKE '%produksi%' AND lower(mp.nama_sarana) LIKE '%maha siri jaya%';
```

### [191] tampilkan sarana distribusi dan pelayanan yang tutup pada periode tahun 2025

| | |
|---|---|
| Bentuk NER | `tampilkan <FACILITY TYPE> yang tutup pada periode tahun <YEAR>` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: tidak |
| Status | OK → **OK** · 125 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_sarana, sarana, tanggal_mulai FROM public.mv_pemeriksaan WHERE (lower(sarana) LIKE '%distribusi%' OR lower(sarana) LIKE '%pelayanan%') AND kesimpulan = 'TTP' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
```

### [192] tampilkan sarana peredaran yang memiliki riwayat hasil tmk terbanyak di upt dengan nama balai pom di jakarta.

| | |
|---|---|
| Bentuk NER | `tampilkan sarana peredaran yang memiliki riwayat hasil tmk terbanyak di upt dengan nama <HALL NAME> di <CITY NAME>.` |
| Tabel | `mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 979 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.nama_sarana, mp.kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND kesimpulan = 'TMK' AND lower(mp.sarana) LIKE '%distribusi%' AND lower(nama_upt) LIKE '%pom di jakarta%' GROUP BY 1, 2;
```

### [193] Tampilkan sarana produksi TMK pada tiga tahun terakhir di wilayah kerja Balai POM di Pangkalpinang beserta tindak lanjut masing-masing sarana

| | |
|---|---|
| Bentuk NER | `Tampilkan <FACILITY TYPE> pada tiga tahun terakhir di wilayah kerja Balai POM di <PROVINCE NAME> beserta tindak lanjut masing-masing sarana` |
| Tabel | `mv_pemeriksaan` · agregasi: tidak |
| Status | OK → **OK** · 23 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.tanggal_input, mp.nama_upt, mp.kesimpulan, mp.tl_saran_names FROM mv_pemeriksaan mp WHERE LOWER(mp.sarana) LIKE '%produksi%' AND mp.tanggal_input >= (CURRENT_DATE - INTERVAL '3 years') AND LOWER(mp.nama_upt) LIKE '%pangkalpinang%' AND mp.kesimpulan = 'TMK' ORDER BY 1;
```

### [194] tampilkan temuan ketidaksesuaian untuk klausul untuk upt balai besar pom di bandung.

| | |
|---|---|
| Bentuk NER | `tampilkan temuan ketidaksesuaian untuk klausul untuk <HALL NAME> di <CITY NAME>.` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 26 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mpt.tp_kategori, count(*) AS jumlah_pemeriksaan, sum(mpt.tp_jml_temuan) AS jumlah_temuan, sum(mpt.tp_harga_total) AS nilai_temuan FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(kesimpulan) = 'tmk' AND lower(mp.nama_upt) LIKE '%pom di bandung%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1;
```

### [195] tampilkan temuan produk berdasarkan kategori sarana distribusi yang ada di sipt?

| | |
|---|---|
| Bentuk NER | `tampilkan <PRODUCT NAME> berdasarkan kategori <FACILITY TYPE> yang ada di sipt?` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 132 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mp.komoditi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(sarana) LIKE '%distribusi%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2;
```

### [196] tampilkan tiga temuan kritis paling sering ditemui pada Balai Besar POM di DKI Jakarta tahun 2024

| | |
|---|---|
| Bentuk NER | `tampilkan tiga temuan kritis paling sering ditemui pada <HALL NAME> di <PROVINCE NAME> tahun <YEAR>` |
| Tabel | `mv_pemeriksaan + mp` · agregasi: ya |
| Status | OK → **OK** · 6 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
select mp.nama_upt, mp.tx_critical_issue, count(*) from mv_pemeriksaan mp where mp.tx_critical_issue is not null and lower(mp.nama_upt) like '%jakarta%' and extract(year from mp.tanggal_input) = 2024 group by 1, 2
```

### [197] tampilkan tiga temuan/ketidaksesuaian paling sering ditemui di wilayah kerja bbpom di dki jakarta pada triwulan 1 tahun 2025.

| | |
|---|---|
| Bentuk NER | `tampilkan tiga temuan/ketidaksesuaian paling sering ditemui di wilayah kerja bbpom di <PROVINCE NAME> pada triwulan 1 tahun <YEAR>.` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 7 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_upt, provinsi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(provinsi) LIKE '%dki jakarta%' AND mp.tanggal_mulai BETWEEN '2025-01-01' AND '2025-04-01' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3;
```

### [198] tampilkan total nilai keekonomian produk tmk (tie, rusak kedaluwarsa) di balai pom di batam pada tahun 2025.

| | |
|---|---|
| Bentuk NER | `tampilkan total nilai keekonomian produk tmk (tie, rusak kedaluwarsa) di <HALL NAME> di <CITY NAME> pada tahun <YEAR>.` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 12 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mpt.tp_kategori, sum(mpt.tp_harga_total) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%pom di batam%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY 1;
```

### [199] tampilkan total temuan produk dan total nilai temuan pada kategori 'lainnya'.

| | |
|---|---|
| Bentuk NER | `tampilkan total temuan produk dan total nilai temuan pada kategori '<CLASSIFICATION>'.` |
| Tabel | `mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 7 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT tp_kategori, SUM(tp_jml_temuan) AS total_temuan_produk, SUM(tp_harga_total) AS total_nilai_temuan FROM mv_pemeriksaan_temuan WHERE LOWER(tp_kategori) LIKE '%lain - lain%' GROUP BY 1;
```

### [200] tampilkan total temuan produk dan total nilai temuan pada kategori bahan berbahaya.

| | |
|---|---|
| Bentuk NER | `tampilkan total temuan produk dan total nilai temuan pada kategori <CLASSIFICATION>.` |
| Tabel | `mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 10 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT tp_kategori, SUM(tp_jml_temuan) AS total_temuan_produk, SUM(tp_harga_total) AS total_nilai_temuan FROM mv_pemeriksaan_temuan WHERE LOWER(tp_kategori) LIKE '%bahan berbahaya%' GROUP BY 1;
```

### [201] tampilkan total temuan produk dan total nilai temuan pada kategori kedaluarsa.

| | |
|---|---|
| Bentuk NER | `tampilkan total temuan <PRODUCT NAME> dan total nilai temuan pada kategori kedaluarsa.` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 22 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mpt.tp_kategori, sum(mpt.tp_harga_total) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mpt.tp_kategori) LIKE '%kedaluwarsa%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1;
```

### [202] tampilkan total temuan produk dan total nilai temuan pada kategori kedaluarsa.

| | |
|---|---|
| Bentuk NER | `tampilkan total temuan <PRODUCT NAME> dan total nilai temuan pada kategori kedaluarsa.` |
| Tabel | `mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 22 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT tp_kategori, SUM(tp_jml_temuan) AS total_temuan_produk, SUM(tp_harga_total) AS total_nilai_temuan FROM mv_pemeriksaan_temuan WHERE LOWER(tp_kategori) LIKE '%kedaluwarsa%' GROUP BY 1;
```

### [203] tampilkan total temuan produk dan total nilai temuan pada kategori lainnya.

| | |
|---|---|
| Bentuk NER | `tampilkan total temuan <PRODUCT NAME> dan total nilai temuan pada kategori lainnya.` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 7 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mpt.tp_kategori, sum(mpt.tp_harga_total) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mpt.tp_kategori) LIKE '%lain - lain%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1;
```

### [204] tampilkan total temuan produk dan total nilai temuan pada kategori tanpa izin edar.

| | |
|---|---|
| Bentuk NER | `tampilkan total temuan <PRODUCT NAME> dan total nilai temuan pada kategori tanpa izin edar.` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 50 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT mpt.tp_kategori, sum(mpt.tp_harga_total) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mpt.tp_kategori) LIKE '%tie%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1;
```

### [205] tampilkan total temuan produk dan total nilai temuan pada kategori tanpa izin edar.

| | |
|---|---|
| Bentuk NER | `tampilkan total temuan <PRODUCT NAME> dan total nilai temuan pada kategori tanpa izin edar.` |
| Tabel | `mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 50 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT tp_kategori, SUM(tp_jml_temuan) AS total_temuan_produk, SUM(tp_harga_total) AS total_nilai_temuan FROM mv_pemeriksaan_temuan WHERE LOWER(tp_kategori) LIKE '%tie%' GROUP BY 1;
```

### [206] Tampilkan tren audit komprehensif berdasarkan tingkat kritikalitas untuk tahun 2024

| | |
|---|---|
| Bentuk NER | `Tampilkan tren audit komprehensif berdasarkan tingkat kritikalitas untuk tahun <YEAR>` |
| Tabel | `mv_kriteria_pemeriksaan + mkp` · agregasi: ya |
| Status | OK → **OK** · 7 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT TO_CHAR(mkp.tgl_end, 'YYYY-MM') AS bulan_tahun, mkp.tx_criteria AS tingkat_kritikalitas, COUNT(*) AS jumlah_audit FROM mv_kriteria_pemeriksaan mkp WHERE LOWER(mkp.tujuan) LIKE '%komprehensif%' AND EXTRACT(YEAR FROM mkp.tgl_end) = 2024 GROUP BY TO_CHAR(mkp.tgl_end, 'YYYY-MM'), mkp.tx_criteria ORDER BY bulan_tahun, tingkat_kritikalitas;
```

### [207] temuan produk berdasarkan kategori sarana distribusi

| | |
|---|---|
| Bentuk NER | `temuan produk berdasarkan kategori <CLASSIFICATION>` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_temuan` · agregasi: ya |
| Status | OK → **OK** · 304 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
select klasifikasi_distribusi, komoditi, mpt.tp_kategori, count(*), sum(mpt.tp_harga_total) from mv_pemeriksaan mp join mv_pemeriksaan_temuan mpt on mp.id = mpt.id_pemeriksaan where mp.klasifikasi_distribusi is not null group by 1, 2, 3
```

### [208] Trend hasil pemeriksaan sarana produksi MD untuk jenis pangan AMDK di UPT Bogor (tahun 2025)

| | |
|---|---|
| Bentuk NER | `Trend hasil pemeriksaan <FACILITY TYPE> untuk jenis pangan <PRODUCT NAME> di UPT <REGENCY NAME> (tahun <YEAR>)` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_jenis_pangan + mp + pemeriksaan_amdk` · agregasi: ya |
| Status | OK → **OK** · 5 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
WITH pemeriksaan_amdk AS ( SELECT mp.id, mp.tanggal_mulai, TO_CHAR(mp.tanggal_mulai, 'YYYY-MM') AS bulan_tahun, mp.nama_upt FROM mv_pemeriksaan mp JOIN mv_pemeriksaan_jenis_pangan mpjp ON mp.id = mpjp.id_pemeriksaan WHERE EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND LOWER(mp.nama_upt) LIKE '%bogor%' AND LOWER(mpjp.jenis_pangan_name) LIKE '%air minum dalam kemasan%' and mp.sarana = 'PRODUKSI' ) SELECT pa.bulan_tahun
```

### [209] Trend hasil pemeriksaan sarana produksi MD untuk jenis pangan Garam, Tepung, Lemak, dan Minyak Nabati sejak tahun 2024

| | |
|---|---|
| Bentuk NER | `Trend hasil pemeriksaan <FACILITY TYPE> untuk jenis pangan <COMMODITY NAME>, <COMMODITY NAME>, <COMMODITY NAME>, dan <COMMODITY NAME> sejak tahun <YEA` |
| Tabel | `mv_pemeriksaan + mv_pemeriksaan_jenis_pangan + mp + pemeriksaan_pangan` · agregasi: ya |
| Status | OK → **OK** · 228 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
WITH pemeriksaan_pangan AS ( SELECT mp.id, mp.tanggal_mulai, TO_CHAR(mp.tanggal_mulai, 'YYYY-MM') AS bulan_tahun, mp.nama_upt, mpjp.jenis_pangan_name FROM mv_pemeriksaan mp JOIN mv_pemeriksaan_jenis_pangan mpjp ON mp.id = mpjp.id_pemeriksaan WHERE EXTRACT(YEAR FROM mp.tanggal_mulai) >= 2024 AND LOWER(mpjp.jenis_pangan_name) ~ '(garam|tepung|lemak|minyak nabati)' AND LOWER(mp.sarana) LIKE '%produksi%' -- karena fokusn
```

### [210] upt mana saja yang paling banyak melaporkan hasil pemeriksaan sarana produksi yang tmk?

| | |
|---|---|
| Bentuk NER | `upt mana saja yang paling banyak melaporkan hasil pemeriksaan <FACILITY TYPE> yang tmk?` |
| Tabel | `mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 10 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_upt, count(*) FROM public.mv_pemeriksaan WHERE sarana ILIKE '%produksi%' AND kesimpulan = 'TMK' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY nama_upt ORDER BY COUNT(*) DESC LIMIT 10;
```

### [211] upt mana saja yang paling banyak melaporkan hasil pemeriksaan sarana yang tmk?

| | |
|---|---|
| Bentuk NER | `upt mana saja yang paling banyak melaporkan hasil pemeriksaan <FACILITY TYPE> yang tmk?` |
| Tabel | `mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 5 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_upt, kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND lower(kesimpulan) = 'tmk' GROUP BY 1, 2 ORDER BY 3 DESC LIMIT 5;
```

### [212] upt mana saja yang sering melaporkan hasil pemeriksaan lebih dari 30 hari kerja dari tanggal pemeriksaan hingga tanggal kirim ka upt?

| | |
|---|---|
| Bentuk NER | `upt mana saja yang sering melaporkan hasil pemeriksaan lebih dari 30 hari kerja dari tanggal pemeriksaan hingga tanggal kirim ka upt?` |
| Tabel | `mv_pemeriksaan_log + generate_series + hari + waktu + kerja + mv_pemeriksaan` · agregasi: ya |
| Status | OK → **OK** · 13,347 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
WITH waktu AS ( SELECT mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 2) AS t2, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS t3 FROM public.mv_pemeriksaan_log AS mpl GROUP BY mpl.id_pemeriksaan ), kerja AS ( SELECT w.id_pemeriksaan, w.t2, w.t3, ( SELECT COUNT(*) FROM generate_series(w.t2::date, w.t3::date - 1, '1 day') AS d(hari) WHERE EXTRACT(DOW FROM hari) BETWEEN 1 AND 5 -- Se
```

### [213] upt manakah yang hasil pemeriksaan tmk sarana produksi md nya paling banyak di tahun 2025?

| | |
|---|---|
| Bentuk NER | `upt manakah yang hasil pemeriksaan tmk sarana produksi md nya paling banyak di tahun <YEAR>?` |
| Tabel | `mv_pemeriksaan + tanggal_mulai` · agregasi: ya |
| Status | OK → **OK** · 75 baris |
| Lapis terjemahan | - |
| Diagnosa | **✅ Jalan apa adanya** |
| Sebab | SQL generasi berjalan sudah cocok dengan skema live; tidak perlu diubah |

```sql
SELECT nama_upt, jenis_sarana, count(*) FROM mv_pemeriksaan mp WHERE lower(jenis_sarana) LIKE '%pangan md%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2 ORDER BY 3 DESC;
```
