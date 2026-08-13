# 15 — Mapping KAI → Warehouse & Katalog SQL Pair (LENGKAP)

> **Katalog LENGKAP**: SEMUA 963 pertanyaan unik untuk DB `pemeriksaan` + SQL pair KAI aslinya.
> - 811 "bisa dijawab" dikelompokkan per **primary intent** (eksklusif).
> - 71 gap, 81 cross-domain. Hanya pertanyaan yang menyangkut DB `pemeriksaan` (sesuai instruksi: sematkan hanya untuk database kita).
> - SQL KAI memakai view `vw_pemeriksaan_bcc` (kolom beda dengan warehouse — lihat §15.1).
> - 857/963 punya SQL pair asli; 106 tanpa SQL (pertanyaan meta/gagal generate) ditandai `[no-sql]`.

## 15.1 Mapping Nama Kolom: KAI (`vw_pemeriksaan_bcc`) vs Warehouse (`mv_pemeriksaan`)

| Konsep | Kolom KAI | Kolom Warehouse |
|---|---|---|
| Tanggal mulai | `tgl_start` | `tanggal_mulai` |
| Tanggal selesai | `tgl_end` | `tanggal_selesai` |
| Tanggal input | — | `tanggal_input` |
| Nama UPT/Balai | `nama_balai` | `nama_upt` |
| ID unit (Loka) | `id_unit` | (tidak ada — bagian dari `nama_upt`) |
| Kesimpulan | `kesimpulan` | `kesimpulan` |
| Jenis sarana | `jenis_sarana` | `jenis_sarana` |
| Komoditi | `komoditi` | `komoditi` |
| Nama sarana | `nama_sarana` | `nama_sarana` |
| Sarana (tipe) | `sarana` | `sarana` |
| Status | `status` | `status` |
| Provinsi | `provinsi` | `provinsi` |
| Kabupaten | `kabupaten` | `kabupaten_kota` |
| Grade | `grade` | `grade` |

**Case sensitivity**: KAI Title Case (`kosmetik`) vs warehouse UPPER (`KOSMETIK`). Pakai `komoditi = 'KOSMETIK'`.

## 15.2 Katalog LENGKAP — 811 Pertanyaan Bisa Dijawab (per Primary Intent)

### SLA / ketepatan waktu pelaporan — 10 pertanyaan

**SQL template warehouse (kanonik):**
```sql
SELECT nama_upt, COUNT(DISTINCT id) FILTER (WHERE day_input_mulai > 30) AS telat
FROM mv_pemeriksaan
GROUP BY 1 ORDER BY 2 DESC;
```
*PROXY: day_input_mulai = proxy keterlambatan. Tanggal kirim SIPT TIDAK ada di warehouse.*

- **"upt mana saja yang sering melaporkan hasil pemeriksaan lebih dari 30 hari kerja dari tanggal pemeriksaan hingga tanggal kirim ka upt?"**
  ```sql
  SELECT nama_balai FROM public.vw_pemeriksaan_bcc WHERE tgl_end IS NOT NULL AND tgl_start IS NOT NULL AND tgl_end - tgl_start > INTERVAL '30 days' GROUP BY nama_balai;
  ```
- **Pertanyaan:  tampilkan persentase ketepatan waktu pelaporan hasil pemeriksaan dari upt dengan nama Balai POM di Bogor di tw 1 2025 syarat : tepat waktu jika pelaporan hasil pemeriksaan maksimal tanggal 15 bulan selanjutnya dari bulan dilakukan pemeriksaan.**
  ```sql
  WITH laporan_q1_2025 AS ( -- Langkah 1: Ambil data tanggal penting dari Balai POM di Bogor di Q1 2025 SELECT mp.nama_upt, mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 2) AS tanggal_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS tanggal_pelaporan FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_log AS mpl ON mp.id = mpl.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%balai pom di bogor%' AND EXTRACT(YEAR FROM mpl.created_at) = 2025 AND EXTRACT(MONTH FROM mpl.created_at) IN (1, 2, 3) -- Q1 (Januari, Februari, Maret) GROUP BY 1, 2 ) -- Langkah 2: Hitung jumlah total laporan dan jumlah laporan yang tepat waktu SELECT CAST( COUNT(CASE WHEN -- Syarat tepat waktu: tanggal pelaporan maksimal tgl 15 bulan berikutnya tanggal_pelaporan::date <= (DATE_TRUNC('month', tanggal_pemeriksaan) + INTERVAL '1 month' + INTERVAL '14 days')::date THEN 1 END) AS NUMERIC ) * 100 / COUNT(*) AS persentase_tepat_waktu FROM laporan_q1_2025;
  ```
- **tampilkan persentase ketepatan waktu pelaporan hasil pemeriksaan dari upt dengan nama Balai POM di Bogor di tw 1 2025 (syarat : tepat waktu jika pelaporan hasil pemeriksaan maksimal tanggal 15 bulan selanjutnya dari bulan dilakukan pemeriksaan) dan tampilkan list hasil pemeriksaan sarana yang tidak tepat waktu pelaporannya.**  `[no-sql]`
- **tampilkan persentase ketepatan waktu pelaporan hasil pemeriksaan dari upt dengan nama Balai POM di Bogor di tw 1 2025 syarat : tepat waktu jika pelaporan hasil pemeriksaan maksimal tanggal 15 bulan selanjutnya dari bulan dilakukan pemeriksaan**
  ```sql
  WITH laporan_q1_2025 AS ( -- Langkah 1: Ambil data tanggal penting dari Balai POM di Bogor di Q1 2025 SELECT mp.nama_upt, mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 2) AS tanggal_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS tanggal_pelaporan FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_log AS mpl ON mp.id = mpl.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%balai pom di bogor%' AND EXTRACT(YEAR FROM mpl.created_at) = 2025 AND EXTRACT(MONTH FROM mpl.created_at) IN (1, 2, 3) -- Q1 (Januari, Februari, Maret) GROUP BY 1, 2 ) -- Langkah 2: Hitung jumlah total laporan dan jumlah laporan yang tepat waktu SELECT CAST( COUNT(CASE WHEN -- Syarat tepat waktu: tanggal pelaporan maksimal tgl 15 bulan berikutnya tanggal_pelaporan::date <= (DATE_TRUNC('month', tanggal_pemeriksaan) + INTERVAL '1 month' + INTERVAL '14 days')::date THEN 1 END) AS NUMERIC ) * 100 / COUNT(*) AS persentase_tepat_waktu FROM laporan_q1_2025;
  ```
- **tampilkan persentase ketepatan waktu pelaporan hasil pemeriksaan dari upt dengan nama Balai POM di Bogor di tw 1 2025 syarat : tepat waktu jika pelaporan hasil pemeriksaan maksimal tanggal 15 bulan selanjutnya dari bulan dilakukan pemeriksaan.**
  ```sql
  WITH laporan_q1_2025 AS ( -- Langkah 1: Ambil data tanggal penting dari Balai POM di Bogor di Q1 2025 SELECT mp.nama_upt, mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 2) AS tanggal_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS tanggal_pelaporan FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_log AS mpl ON mp.id = mpl.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%balai pom di bogor%' AND EXTRACT(YEAR FROM mpl.created_at) = 2025 AND EXTRACT(MONTH FROM mpl.created_at) IN (1, 2, 3) -- Q1 (Januari, Februari, Maret) GROUP BY 1, 2 ) -- Langkah 2: Hitung jumlah total laporan dan jumlah laporan yang tepat waktu SELECT CAST( COUNT(CASE WHEN -- Syarat tepat waktu: tanggal pelaporan maksimal tgl 15 bulan berikutnya tanggal_pelaporan::date <= (DATE_TRUNC('month', tanggal_pemeriksaan) + INTERVAL '1 month' + INTERVAL '14 days')::date THEN 1 END) AS NUMERIC ) * 100 / COUNT(*) AS persentase_tepat_waktu FROM laporan_q1_2025;
  ```
- **Tampilkan persentase ketepatan waktu pelaporan hasil pemeriksaan dari UPT x di TW 1 2025**
  ```sql
  SELECT CAST(SUM(CASE WHEN tgl_end <= '2025-03-31' THEN 1 ELSE 0 END) AS NUMERIC) * 100 / COUNT(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) = 2025 AND EXTRACT( QUARTER FROM tgl_start ) = 1 AND nama_balai = 'UPT x';
  ```
- **Tampilkan persentase ketepatan waktu pelaporan hasil pemeriksaan dari UPT x di TW 1 2025 (Syarat : tepat waktu jika pelaporan hasil pemeriksaan maksimal tanggal 15 bulan selanjutnya dari bulan dilakukan pemeriksaan) dan tampilkan list hasil pemeriksaan sarana yang tidak tepat waktu pelaporannya**  `[no-sql]`
- **Tolong buatkan query untuk: tampilkan persentase ketepatan waktu pelaporan hasil pemeriksaan dari upt dengan nama Balai POM di Bogor di tw 1 2025 syarat : tepat waktu jika pelaporan hasil pemeriksaan maksimal tanggal 15 bulan selanjutnya dari bulan dilakukan pemeriksaan.**
  ```sql
  WITH laporan_q1_2025 AS ( -- Langkah 1: Ambil data tanggal penting dari Balai POM di Bogor di Q1 2025 SELECT mp.nama_upt, mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 2) AS tanggal_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS tanggal_pelaporan FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_log AS mpl ON mp.id = mpl.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%balai pom di bogor%' AND EXTRACT(YEAR FROM mpl.created_at) = 2025 AND EXTRACT(MONTH FROM mpl.created_at) IN (1, 2, 3) -- Q1 (Januari, Februari, Maret) GROUP BY 1, 2 ) -- Langkah 2: Hitung jumlah total laporan dan jumlah laporan yang tepat waktu SELECT CAST( COUNT(CASE WHEN -- Syarat tepat waktu: tanggal pelaporan maksimal tgl 15 bulan berikutnya tanggal_pelaporan::date <= (DATE_TRUNC('month', tanggal_pemeriksaan) + INTERVAL '1 month' + INTERVAL '14 days')::date THEN 1 END) AS NUMERIC ) * 100 / COUNT(*) AS persentase_tepat_waktu FROM laporan_q1_2025;
  ```
- **Tolong buatkan query untuk: upt mana saja yang sering melaporkan hasil pemeriksaan lebih dari 30 hari kerja dari tanggal pemeriksaan hingga tanggal kirim ka upt?**
  ```sql
  WITH waktu AS ( SELECT mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 2) AS t2, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS t3 FROM public.mv_pemeriksaan_log AS mpl GROUP BY mpl.id_pemeriksaan ), kerja AS ( SELECT w.id_pemeriksaan, w.t2, w.t3, ( SELECT COUNT(*) FROM generate_series(w.t2::date, w.t3::date - 1, '1 day') AS d(hari) WHERE EXTRACT(DOW FROM hari) BETWEEN 1 AND 5 -- Senin–Jumat ) AS workdays_between FROM waktu w WHERE w.t2 IS NOT NULL AND w.t3 IS NOT NULL AND w.t3::date > w.t2::date ) SELECT mp.nama_upt, count(*) FROM kerja k JOIN public.mv_pemeriksaan mp ON mp.id = k.id_pemeriksaan WHERE k.workdays_between > 30 GROUP BY mp.nama_upt ORDER BY count(*) DESC;
  ```
- **upt mana saja yang sering melaporkan hasil pemeriksaan lebih dari 30 hari kerja dari tanggal pemeriksaan hingga tanggal kirim ka upt?**
  ```sql
  SELECT nama_upt, COUNT(*) AS jumlah_laporan_terlambat FROM public.mv_pemeriksaan WHERE day_input_mulai > 30 GROUP BY nama_upt ORDER BY jumlah_laporan_terlambat DESC;
  ```

### Riwayat sarana by nama (free-text) — 10 pertanyaan

**SQL template warehouse (kanonik):**
```sql
SELECT * FROM mv_pemeriksaan
WHERE nama_sarana ILIKE '%ALFAMART%'
  AND tanggal_mulai >= '2024-01-01' AND tanggal_mulai < '2025-01-01'
ORDER BY tanggal_mulai;
```
*ILIKE untuk discover, lalu exact. nama_sarana inkonsisten (130k nama → 126k normalized).*

- **"bagaimana riwayat pemeriksaan sarana alfamart dalam periode tahun 2024?"**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND LOWER(nama_sarana) LIKE '%alfamart%'
  ```
- **"bagaimana riwayat pemeriksaan sarana apotek kimia farma dalam periode tahun 2025?"**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE LOWER(nama_sarana) LIKE '%apotek kimia farma%' AND EXTRACT(YEAR FROM tgl_start) = 2025;
  ```
- **"tampilkan riwayat pemeriksaan sarana produksi 'nida food' pada rentang tahun yang tersedia."**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE LOWER(nama_sarana) LIKE '%nida food%' AND LOWER(jenis_sarana) LIKE '%produksi%'
  ```
- **bagaimana riwayat pemeriksaan sarana alfamart dalam periode tahun 2024?**
  ```sql
  SELECT nama_sarana, alamat, tanggal_mulai, tanggal_selesai, jenis_sarana, tujuan_pemeriksaan, kesimpulan FROM public.mv_pemeriksaan WHERE LOWER(nama_sarana) LIKE '%alfamart%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2024 ORDER BY tanggal_mulai;
  ```
- **bagaimana riwayat pemeriksaan sarana apotek kimia farma dalam periode tahun 2025?**
  ```sql
  SELECT nama_sarana, tanggal_mulai, tanggal_selesai, jenis_sarana, tujuan_pemeriksaan, kesimpulan FROM public.mv_pemeriksaan WHERE LOWER(nama_sarana) LIKE '%apotek kimia farma%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Bagaimana riwayat pemeriksaan sarana CIPTA ANUGERAH BAKTI MANDIRI dalam periode tahun 2024?**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE nama_sarana LIKE '%CIPTA ANUGERAH BAKTI MANDIRI%' AND EXTRACT( YEAR FROM tgl_start ) = 2024;
  ```
- **tampilkan riwayat pemeriksaan sarana produksi 'maha siri jaya' pada rentang tahun yang tersedia.**
  ```sql
  SELECT tanggal_mulai FROM public.mv_pemeriksaan WHERE lower(nama_sarana) LIKE '%maha siri jaya%' AND lower(sarana) LIKE '%produksi%'
  ```
- **tampilkan riwayat pemeriksaan sarana produksi 'nida food' pada rentang tahun yang tersedia.**
  ```sql
  SELECT nama_sarana, jenis_sarana, tanggal_mulai, tanggal_selesai, kesimpulan FROM public.mv_pemeriksaan WHERE nama_sarana ILIKE '%nida food%' AND jenis_sarana ILIKE '%produksi%';
  ```
- **Tolong buatkan query untuk: bagaimana riwayat pemeriksaan sarana alfamart dalam periode tahun 2024?**
  ```sql
  SELECT nama_sarana, alamat, tanggal_mulai, tanggal_selesai, jenis_sarana, tujuan_pemeriksaan, kesimpulan FROM public.mv_pemeriksaan WHERE LOWER(nama_sarana) LIKE '%alfamart%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ORDER BY tanggal_mulai;
  ```
- **Tolong buatkan query untuk: tampilkan riwayat pemeriksaan sarana produksi 'maha siri jaya' pada rentang tahun yang tersedia.**
  ```sql
  SELECT nama_sarana, sarana, jenis_sarana, mpt.product_name, tanggal_mulai, mpt.tp_kategori FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(sarana) LIKE '%produksi%' AND lower(mp.nama_sarana) LIKE '%maha siri jaya%';
  ```

### Permintaan chart — 33 pertanyaan

**SQL template warehouse (kanonik):**
```sql
(data query sesuai intent, lalu render chart)
-- bar chart: ranking/top N
-- line chart: trend temporal
-- pie chart: komposisi/distribusi
```
*Chart = presentation. Data query dulu, render belakangan (Gate 5).*

- **"analisis jam terbang masing-masing inspektur dalam penugasan ke sarana produksi pangan md dan irtp dengan kategori jenis pangan yang diperiksa dalam rangka peningkatan kompetensi maupun kualifikasi inspektur dan tampilkan data dalam bentuk grafik."**
  ```sql
  SELECT nama_balai, COUNT(CASE WHEN komoditi = 'Makanan' THEN 1 ELSE NULL END) AS jumlah_makanan, COUNT(CASE WHEN komoditi = 'Obat Tradisional' THEN 1 ELSE NULL END) AS jumlah_obat_tradisional, COUNT(CASE WHEN komoditi = 'Suplemen Kesehatan' THEN 1 ELSE NULL END) AS jumlah_suplemen_kesehatan, COUNT(CASE WHEN komoditi = 'Kosmetik' THEN 1 ELSE NULL END) AS jumlah_kosmetik, COUNT(CASE WHEN komoditi = 'Obat' THEN 1 ELSE NULL END) AS jumlah_obat FROM public.vw_pemeriksaan_bcc WHERE jenis_sarana = 'Produksi' GROUP BY nama_balai;
  ```
- **"analisis jam terbang masing-masing inspektur dalam rangka peningkatan kompetensi maupun kualifikasi inspektur dalam penugasan ke if dengan kategori maturitas tertentu dan jenis fasilitas, tampilkan data dalam bentuk grafik."**
  ```sql
  SELECT nama_balai, COUNT(id) AS jumlah_inspeksi FROM public.vw_pemeriksaan_bcc GROUP BY nama_balai ORDER BY jumlah_inspeksi DESC;
  ```
- **"analisis jumlah pemeriksaan oleh masing-masing inspektur dalam rangka rekapitulasi untuk peningkatan kompetensi maupun kualifikasi inspektur pada semua jenis fasilitas sardis dan saryan, dan sajikan hasilnya dalam bentuk grafik."**
  ```sql
  -- Tidak ada informasi mengenai inspektur pada tabel vw_pemeriksaan_bcc. -- Asumsi: Pertanyaan mengacu pada jumlah pemeriksaan secara keseluruhan. -- Karena tidak ada informasi inspektur, kita hanya bisa menghitung total pemeriksaan. -- Jika ada kolom yang merepresentasikan inspektur, mohon berikan informasi lebih lanjut. SELECT COUNT(id) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc;
  ```
- **"analisis kesesuaian realisasi inspeksi pada periode pengawasan tertentu terhadap target inspeksi yang telah ditetapkan setiap tahunnya dan tampilkan data grafik kesesuaian beserta daftar justifikasi atas adanya ketidaksesuaian, serta crosscheck kembali realisasi lain yang tidak sesuai dan tidak terdokumentasi."**
  ```sql
  WITH TargetInspeksi AS ( SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, COUNT(id) AS target_inspeksi FROM public.vw_pemeriksaan_bcc GROUP BY EXTRACT(YEAR FROM tgl_start) ), RealisasiInspeksi AS ( SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, COUNT(id) AS realisasi_inspeksi FROM public.vw_pemeriksaan_bcc GROUP BY EXTRACT(YEAR FROM tgl_start) ) SELECT TargetInspeksi.tahun, TargetInspeksi.target_inspeksi, RealisasiInspeksi.realisasi_inspeksi, CAST(RealisasiInspeksi.realisasi_inspeksi AS NUMERIC) / CAST(TargetInspeksi.target_inspeksi AS NUMERIC) AS tingkat_kesesuaian, CASE WHEN RealisasiInspeksi.realisasi_inspeksi < TargetInspeksi.target_inspeksi THEN 'Ketidaksesuaian: Realisasi inspeksi kurang dari target.' ELSE 'Sesuai atau melebihi target.' END AS justifikasi_ketidaksesuaian FROM TargetInspeksi JOIN RealisasiInspeksi ON TargetInspeksi.tahun = RealisasiInspeksi.tahun;
  ```
- **"tampilkan profil pemeriksaan sarana produksi obat dan makanan selama periode 2025 dalam bentuk tabel dan grafik jumlah sarana produksi mk, tmk, tidak dapat dinilai, tutup per jenis komoditi (obat, oba, sk, kos dan pangan)."**  `[no-sql]`
- **analisis jam terbang masing-masing inspektur dalam penugasan ke sarana produksi pangan md dan irtp dengan kategori jenis pangan yang diperiksa dalam rangka peningkatan kompetensi maupun kualifikasi inspektur dan tampilkan data dalam bentuk grafik.**  `[no-sql]`
- **analisis jam terbang masing-masing inspektur dalam rangka peningkatan kompetensi maupun kualifikasi inspektur dalam penugasan ke IF dengan kategori maturitas tertentu dan jenis fasilitas, tampilkan data dalam bentuk grafik.**
  ```sql
  SELECT t2.petugas AS inspector_name, SUM(t1.day_mulai_selesai) AS total_flight_hours, t1.jenis_sarana FROM public.mv_pemeriksaan AS t1 JOIN public.mv_pemeriksaan_petugas AS t2 ON t1.id = t2.id_pemeriksaan WHERE t1.day_mulai_selesai IS NOT NULL AND t2.petugas IS NOT NULL AND t1.jenis_sarana IS NOT NULL GROUP BY t2.petugas, t1.jenis_sarana ORDER BY total_flight_hours DESC;
  ```
- **analisis kesesuaian realisasi inspeksi pada periode pengawasan tertentu terhadap target inspeksi yang telah ditetapkan setiap tahunnya dan tampilkan data grafik kesesuaian beserta daftar justifikasi atas adanya ketidaksesuaian, serta crosscheck kembali realisasi lain yang tidak sesuai dan tidak terdokumentasi.**
  ```sql
  SELECT mp.nama_sarana, mp.jenis_sarana, mp.tanggal_mulai, mp.tanggal_selesai, mp.kesimpulan, mpt.product_name, mpt.tp_pelanggaran, mpt.tp_keterangan FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE mp.kesimpulan = 'TMK' AND (mpt.tp_pelanggaran IS NOT NULL OR mpt.tp_keterangan IS NOT NULL) ORDER BY mp.tanggal_mulai DESC;
  ```
- **berapa jumlah pemeriksaan pangan MD dengan tujuan sertifikasi pada januari sampai oktober tahun 2025? buatkan juga grafik perbandingan MK dan TMKnya**
  ```sql
  SELECT kesimpulan, COUNT(*) FROM public.mv_pemeriksaan mp WHERE lower(jenis_sarana) LIKE '%pangan md%' AND lower(tujuan_pemeriksaan) LIKE '%sertifikasi%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM mp.tanggal_mulai) BETWEEN 1 AND 10 GROUP BY 1;
  ```
- **berapa jumlah pemeriksaan pangan MD dengan tujuan sertifikasi pada tahun 2025? buatkan juga grafik perbandingan MK dan TMKnya**
  ```sql
  SELECT kesimpulan, COUNT(*) FROM public.mv_pemeriksaan mp WHERE lower(jenis_sarana) LIKE '%pangan md%' AND lower(tujuan_pemeriksaan) LIKE '%sertifikasi%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 GROUP BY 1;
  ```
- **Berikan jumlah MK dan TMK bulan Mei 2025 dalam pie chart**
  ```sql
  SELECT kesimpulan, COUNT(*) FROM vw_pemeriksaan_bcc WHERE kesimpulan IN ('MK', 'TMK') AND tgl_start BETWEEN '2025-05-01' AND '2025-05-31' GROUP BY 1;
  ```
- **Berikan top 5 balai dengan pemeriksaan tertinggi bulan juni 2025 dalam bar chart**
  ```sql
  SELECT nama_balai , count(*) FROM vw_pemeriksaan_bcc vpb WHERE EXTRACT(MONTH FROM tgl_start) = 6 AND EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY 1 ORDER BY 2 DESC LIMIT 5;
  ```
- **berikan top 5 pemeriksaan berdasarkan balai dalam kategori dalam pie chart**
  ```sql
  SELECT nama_balai, COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc GROUP BY nama_balai ORDER BY jumlah_pemeriksaan DESC LIMIT 5;
  ```
- **berikan total pemeriksaan berdasarkan jenis sarana per tahun 2023, 2024, sampai bulan juni tahun 2025 dalam tampilan bar chart**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, jenis_sarana, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) >= 2023 AND EXTRACT(YEAR FROM tgl_start) <= 2025 AND (EXTRACT(YEAR FROM tgl_start) < 2025 OR EXTRACT(MONTH FROM tgl_start) <= 6) GROUP BY tahun, jenis_sarana ORDER BY tahun, jenis_sarana;
  ```
- **berikan total pemeriksaan berdasarkan jenis sarana per tahun 2024 sampai bulan Agustus tahun 2025 dalam tampilan bar chart**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, jenis_sarana, COUNT(*) FROM public.mv_pemeriksaan WHERE tanggal_mulai >= '2024-01-01' AND tanggal_mulai <= '2025-08-31' GROUP BY 1, 2 ORDER BY 1, 2;
  ```
- **berikan total pemeriksaan berdasarkan jenis sarana per tahun2024 sampai bulan juni tahun 2025 dalam tampilan bar chart**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, jenis_sarana, COUNT(*) AS total_pemeriksaan FROM public.mv_pemeriksaan WHERE tanggal_mulai >= '2024-01-01' AND tanggal_mulai <= '2025-06-30' GROUP BY 1, 2 ORDER BY 1, 2;
  ```
- **buat dalam bentuk grafik**
  ```sql
  SELECT komoditi, kesimpulan, COUNT(*) AS jumlah_pemeriksaan FROM vw_pemeriksaan_bcc where kesimpulan != 'Null' and extract(year from tgl_end) = 2025 and komoditi in ('OBAT', 'KOSMETIK', 'SUPLEMEN KESEHATAN', 'PRODUK Pangan') GROUP BY komoditi, kesimpulan ORDER BY komoditi, kesimpulan
  ```
- **Buatkan analisis terkait jumlah pemeriksaan berdasarkan kesimpulan setiap bulannya, buat dalam bentuk grouped bar chart**
  ```sql
  SELECT EXTRACT(YEAR FROM TO_DATE(tgl_start, 'YYYY-MM-DD')) AS tahun, EXTRACT(MONTH FROM TO_DATE(tgl_start, 'YYYY-MM-DD')) AS bulan, kesimpulan, CAST(COUNT(*) AS NUMERIC) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc GROUP BY tahun, bulan, kesimpulan ORDER BY tahun, bulan, kesimpulan;
  ```
- **buatkan dalam bentuk grafik untuk masing sarana**
  ```sql
  SELECT jenis_sarana , count(*) FROM vw_pemeriksaan_bcc vpb GROUP BY 1;
  ```
- **coba buatkan hasil grafik tadi dalam bentuk narasi 1 halaman**  `[no-sql]`
- **Pertanyaan:  apakah kamu dapat menunjukkan jumlah pemeriksaan dalam bentuk grafik yang dibagi berdasarkan pulau di indonesia?**
  ```sql
  SELECT provinsi, COUNT(*) AS jumlah_pemeriksaan FROM public.mv_pemeriksaan WHERE provinsi IS NOT NULL GROUP BY provinsi ORDER BY jumlah_pemeriksaan DESC;
  ```
- **Pertanyaan:  Bagaimana line chart untuk komoditas obat pada jumlah total pemeriksaan di tahun 2025**
  ```sql
  SELECT EXTRACT(MONTH FROM tanggal_mulai) AS bulan, mp.komoditi, count(*) FROM public.mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(komoditi) LIKE '%obat%' GROUP BY 1, 2;
  ```
- **Pertanyaan:  berapa jumlah pemeriksaan komoditi kosmetik untuk tahun 2024 perbulan dalam line chart**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS bulan, komoditi, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND lower(komoditi) like '%kosmetik%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1,2,3 ORDER BY 1,2,3;
  ```
- **Pertanyaan:  berapa jumlah pemeriksaan pangan MD dengan tujuan fortifikasi pada tahun 2025? buatkan juga grafik perbandingan MK dan TMKnya**
  ```sql
  SELECT kesimpulan, COUNT(*) FROM public.mv_pemeriksaan mp WHERE lower(jenis_sarana) LIKE '%pangan md%' AND lower(tujuan_pemeriksaan) LIKE '%fortifikasi%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 GROUP BY 1;
  ```
- **Pertanyaan:  berikan jumlah pemeriksaan untuk komoditas kosmetik pada tahun 2024 secara line chart per bulan**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS bulan, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND lower(komoditi) like '%kosmetik%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1,2 ORDER BY 1,2
  ```
- **tampilkan jumlah perbandingan sarana MK dengan keseluruhan dalam bentuk pie chart untuk loka pom belitung pada tahun 2025**
  ```sql
  SELECT COUNT(CASE WHEN kesimpulan = 'MK' THEN 1 END) AS jumlah_sarana_mk, COUNT(*) AS jumlah_keseluruhan_sarana FROM public.vw_pemeriksaan_bcc WHERE lower(kabupaten) LIKE '%belitung%' AND tgl_start BETWEEN '2025-01-01'::date AND '2025-12-31'::date;
  ```
- **Tolong buatkan query untuk: tampilkan profil pemeriksaan sarana produksi obat dan makanan selama periode 2025 dalam bentuk tabel dan grafik jumlah sarana produksi mk, tmk, tidak dapat dinilai, tutup per jenis komoditi obat, oba, sk, kos dan pangan.**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, sarana, jenis_sarana, kesimpulan, komoditi, COUNT(*) FROM public.mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(sarana) LIKE '%produksi%' AND lower(komoditi) IN ('obat', 'oba', 'sk', 'kosmetika', 'pangan') AND kesimpulan IN ('MK', 'TMK', 'TDP', 'TTP') AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3, 4, 5 ORDER BY 1, 2, 3, 4, 5;
  ```
- **Tunjukan 5 balai dengan jumlah pemeriksaan terbanyak pada bulan Juni 2025 menggunakan bar chart**
  ```sql
  SELECT nama_balai, COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE tgl_start >= '2025-06-01' AND tgl_start < '2025-07-01' GROUP BY nama_balai ORDER BY COUNT(*) DESC LIMIT 5;
  ```
- **Tunjukan trend jumlah pemeriksaan dalam 5 bulan terakhir buat dalam bentuk line chart**
  ```sql
  SELECT DATE_TRUNC('month', tgl_start::DATE) AS month, COUNT(*)::NUMERIC AS total_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE tgl_start::DATE >= CURRENT_DATE - INTERVAL '5 months' GROUP BY month ORDER BY month;
  ```
- **Tunjukkan jumlah pemeriksaaan 3 bulan terakhir dalam bar chart**
  ```sql
  SELECT DATE_TRUNC('month', tgl_start::DATE) AS month, COUNT(*)::NUMERIC AS total_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE tgl_start::DATE >= CURRENT_DATE - INTERVAL '3 months' GROUP BY month ORDER BY month;
  ```
- **Tunjukkan jumlah pemeriksaan 3 bulan terakhir dalam bar chart**
  ```sql
  SELECT CAST(EXTRACT(MONTH FROM tgl_start) AS TEXT) AS month, COUNT(id) AS total_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE tgl_start >= NOW() - INTERVAL '3 months' GROUP BY EXTRACT(MONTH FROM tgl_start) ORDER BY EXTRACT(MONTH FROM tgl_start);
  ```
- **Tunjukkan pemeriksaan 3 bulan terakhir dalam bar chart**
  ```sql
  SELECT TO_CHAR(tgl_start, 'YYYY-MM') AS month, CAST(COUNT(id) AS NUMERIC) AS examination_count FROM public.vw_pemeriksaan_bcc WHERE tgl_start >= NOW() - INTERVAL '3 months' GROUP BY month ORDER BY month;
  ```
- **Tunjukkan trend jumlah pemeriksaan dalam 5 bulan terakhir dalam line chart**
  ```sql
  SELECT DATE_TRUNC('month', tgl_start::DATE) AS month, COUNT(id::BIGINT) AS total_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE tgl_start::DATE >= CURRENT_DATE - INTERVAL '5 months' GROUP BY month ORDER BY month;
  ```

### Tren temporal — 67 pertanyaan

**SQL template warehouse (kanonik):**
```sql
SELECT date_trunc('month', tanggal_mulai)::date AS bln, COUNT(DISTINCT id)
FROM mv_pemeriksaan
WHERE tanggal_mulai >= '2025-01-01' AND tanggal_mulai < '2026-01-01'
GROUP BY 1 ORDER BY 1;
```
*Untuk tren jawab TABEL (bulan × count), bukan 1 angka.*

- **"bagaimana tren hasil pemeriksaan sarana peredaran sejak tahun 2025"**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, COUNT(id) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) >= 2025 GROUP BY tahun ORDER BY tahun;
  ```
- **"bagaimana tren hasil pemeriksaan sarana produksi md dan pirt sejak tahun 2024 hingga 2025?"**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, kesimpulan, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) BETWEEN 2024 AND 2025 AND jenis_sarana ILIKE '%produksi%' AND (nama_sarana ILIKE '%MD%' OR nama_sarana ILIKE '%PIRT%') GROUP BY EXTRACT(YEAR FROM tgl_start), kesimpulan ORDER BY tahun, kesimpulan;
  ```
- **"bagaimana tren hasil pemeriksaan sarana produksi md jenis pangan garam, tepung, lemak dan minyak nabati sejak tahun 2020?"**
  ```sql
  SELECT EXTRACT( YEAR FROM tgl_start ) AS tahun, COUNT(CASE WHEN komoditi LIKE '%Garam%' THEN id END) AS jumlah_garam, COUNT(CASE WHEN komoditi LIKE '%Tepung%' THEN id END) AS jumlah_tepung, COUNT(CASE WHEN komoditi LIKE '%Lemak%' THEN id END) AS jumlah_lemak, COUNT(CASE WHEN komoditi LIKE '%Minyak Nabati%' THEN id END) AS jumlah_minyak_nabati FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) >= 2020 AND jenis_sarana LIKE '%produksi%' GROUP BY tahun ORDER BY tahun;
  ```
- **"bagaimana trend hasil pemeriksaan sarana produksi md untuk jenis pangan amdk yang tidak memenuhi syarat dengan parameter uji tms dalam 5 tahun terakhir, dan dikaitkan dengan temuan-temuan hasil pemeriksaan sarana produksi di wilayah kerja upt bogor?"**
  ```sql
  SELECT EXTRACT( YEAR FROM tgl_start ) AS tahun, COUNT(CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE NULL END) AS jumlah_tidak_memenuhi_syarat FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) BETWEEN EXTRACT( YEAR FROM CURRENT_DATE ) - 5 AND EXTRACT( YEAR FROM CURRENT_DATE ) AND jenis_sarana = 'Produksi' AND komoditi = 'AMDK' AND kabupaten LIKE '%Bogor%' GROUP BY tahun ORDER BY tahun;
  ```
- **"berdasarkan hasil pemeriksaan selama 5 tahun terakhir, untuk sarana produksi dengan jenis pangan amdk di seluruh indonesia, bagaimana trend terkait temuan untuk pengendalian proses produksi dari masing-masing upt?"**
  ```sql
  SELECT EXTRACT( YEAR FROM tgl_start ) AS tahun, nama_balai, COUNT(CASE WHEN kesimpulan = 'MK' THEN id ELSE NULL END) AS jumlah_mk, COUNT(CASE WHEN kesimpulan = 'TMK' THEN id ELSE NULL END) AS jumlah_tmk FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) BETWEEN EXTRACT( YEAR FROM CURRENT_DATE ) - 5 AND EXTRACT( YEAR FROM CURRENT_DATE ) AND jenis_sarana = 'Produksi' AND komoditi = 'AMDK' GROUP BY tahun, nama_balai ORDER BY tahun, nama_balai;
  ```
- **"tampilkan tren audit komprehensif yang dihubungkan dengan region, kategori temuan dan tahun atau periode pengawasan tertentu untuk analisis lebih lanjut."**
  ```sql
  SELECT vw_pemeriksaan_bcc.provinsi AS region, 'temuan' AS kategori_temuan, EXTRACT(YEAR FROM vw_pemeriksaan_bcc.tgl_start) AS tahun, COUNT(vw_pemeriksaan_bcc.id) AS jumlah_temuan FROM public.vw_pemeriksaan_bcc WHERE vw_pemeriksaan_bcc.kesimpulan = 'TMK' GROUP BY vw_pemeriksaan_bcc.provinsi, EXTRACT(YEAR FROM vw_pemeriksaan_bcc.tgl_start) ORDER BY vw_pemeriksaan_bcc.provinsi, EXTRACT(YEAR FROM vw_pemeriksaan_bcc.tgl_start);
  ```
- **"tampilkan tren temuan hasil pemeriksaan pada aspek pemusnahan selama periode 2022-01-01 sampai 2023-12-31"**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, EXTRACT(MONTH FROM tgl_start) AS bulan, COUNT(CASE WHEN kesimpulan = 'MK' THEN id END) AS jumlah_memenuhi_ketentuan, COUNT(CASE WHEN kesimpulan = 'TMK' THEN id END) AS jumlah_tidak_memenuhi_ketentuan, COUNT(CASE WHEN kesimpulan = 'TDP' THEN id END) AS jumlah_tidak_dapat_diperiksa, COUNT(CASE WHEN kesimpulan = 'TTP' THEN id END) AS jumlah_tutup FROM public.vw_pemeriksaan_bcc WHERE tgl_start BETWEEN '2022-01-01' AND '2023-12-31' GROUP BY tahun, bulan ORDER BY tahun, bulan;
  ```
- **"tampilkan tren temuan hasil pemeriksaan pada aspek penerimaan selama periode 2022-2023"**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, COUNT(CASE WHEN kesimpulan = 'MK' THEN id END) AS jumlah_mk, COUNT(CASE WHEN kesimpulan = 'TMK' THEN id END) AS jumlah_tmk, COUNT(CASE WHEN kesimpulan = 'TDP' THEN id END) AS jumlah_tdp, COUNT(CASE WHEN kesimpulan = 'TTP' THEN id END) AS jumlah_ttp FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) BETWEEN 2022 AND 2023 GROUP BY tahun ORDER BY tahun;
  ```
- **"tampilkan tren temuan hasil pemeriksaan pada aspek pengadaan selama periode 2022-2023"**
  ```sql
  SELECT EXTRACT( YEAR FROM tgl_start ) AS tahun, COUNT(CASE WHEN kesimpulan = 'TMK' THEN id ELSE NULL END) AS jumlah_tidak_memenuhi_ketentuan FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) BETWEEN 2022 AND 2023 GROUP BY tahun ORDER BY tahun;
  ```
- **"tampilkan tren temuan hasil pemeriksaan pada aspek pengembalian selama periode 2022-2023"**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, COUNT(CASE WHEN kesimpulan = 'TMK' THEN id END) AS jumlah_tidak_memenuhi_ketentuan FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) BETWEEN 2022 AND 2023 GROUP BY tahun ORDER BY tahun;
  ```
- **"tampilkan tren temuan hasil pemeriksaan pada aspek penyerahan selama periode 2022-01-01 sampai 2023-12-31"**
  ```sql
  SELECT CAST(EXTRACT(YEAR FROM tgl_start) AS TEXT) AS tahun, CAST(EXTRACT(MONTH FROM tgl_start) AS TEXT) AS bulan, COUNT(CASE WHEN kesimpulan = 'MK' THEN id END) AS jumlah_memenuhi_ketentuan, COUNT(CASE WHEN kesimpulan = 'TMK' THEN id END) AS jumlah_tidak_memenuhi_ketentuan, COUNT(CASE WHEN kesimpulan = 'TDP' THEN id END) AS jumlah_tidak_dapat_diperiksa, COUNT(CASE WHEN kesimpulan = 'TTP' THEN id END) AS jumlah_tutup FROM public.vw_pemeriksaan_bcc WHERE tgl_start BETWEEN '2022-01-01' AND '2023-12-31' GROUP BY tahun, bulan ORDER BY tahun, bulan;
  ```
- **"tampilkan tren temuan hasil pemeriksaan pada aspek penyimpanan selama periode 2022-01-01 sampai 2022-12-31"**
  ```sql
  SELECT COUNT(CASE WHEN kesimpulan = 'MK' THEN id END) AS memenuhi_ketentuan, COUNT(CASE WHEN kesimpulan = 'TMK' THEN id END) AS tidak_memenuhi_ketentuan, COUNT(CASE WHEN kesimpulan = 'TDP' THEN id END) AS tidak_dapat_diperiksa, COUNT(CASE WHEN kesimpulan = 'TTP' THEN id END) AS tutup FROM public.vw_pemeriksaan_bcc WHERE tgl_start BETWEEN '2022-01-01' AND '2022-12-31';
  ```
- **Bagaimana tren data kesimpulan pemeriksaan sarana produksi kosmetik dalam periode tahun 2024?**
  ```sql
  SELECT EXTRACT(MONTH FROM tgl_start) AS bulan, COUNT(CASE WHEN kesimpulan = 'MK' THEN id END) AS jumlah_mk FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 GROUP BY bulan ORDER BY bulan;
  ```
- **bagaimana tren hasil pemeriksaan sarana peredaran sejak tahun 2025**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, kesimpulan, COUNT(*) AS jumlah_pemeriksaan FROM public.mv_pemeriksaan WHERE jenis_sarana = 'Distribusi' AND EXTRACT(YEAR FROM tanggal_mulai) >= 2025 GROUP BY tahun, kesimpulan ORDER BY tahun, kesimpulan;
  ```
- **bagaimana tren hasil pemeriksaan sarana produksi kosmetik setiap bulan tahun 2025?**
  ```sql
  SELECT EXTRACT(MONTH FROM tgl_start) AS bulan, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(jenis_sarana) = 'produksi' GROUP BY bulan ORDER BY bulan;
  ```
- **Bagaimana tren hasil pemeriksaan sarana produksi MD dan PIRT sejak tahun 2024 ?**
  ```sql
  SELECT EXTRACT( MONTH FROM tgl_start ) AS bulan, COUNT(CASE WHEN komoditi = 'Obat' THEN id ELSE NULL END) AS jumlah_obat, COUNT(CASE WHEN komoditi = 'PIRT' THEN id ELSE NULL END) AS jumlah_pirt FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) = 2024 GROUP BY bulan ORDER BY bulan;
  ```
- **bagaimana tren hasil pemeriksaan sarana produksi md dan pirt sejak tahun 2024 hingga 2025?**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS bulan, jenis_sarana, count(*) FROM mv_pemeriksaan mp WHERE (lower(jenis_sarana) LIKE '%pangan md%' OR lower(jenis_sarana) LIKE '%pangan irt%') AND EXTRACT(YEAR FROM tanggal_mulai) BETWEEN 2024 AND 2025 AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3 ORDER BY 1, 2, 3;
  ```
- **bagaimana tren hasil pemeriksaan sarana produksi md jenis pangan garam, tepung, lemak dan minyak nabati sejak tahun 2020?**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, kesimpulan, COUNT(*) AS jumlah_pemeriksaan FROM public.mv_pemeriksaan WHERE jenis_sarana ILIKE '%produksi%' AND ( komoditi ILIKE '%garam%' OR komoditi ILIKE '%tepung%' OR komoditi ILIKE '%lemak%' OR komoditi ILIKE '%minyak nabati%' ) AND tanggal_mulai >= '2020-01-01' GROUP BY tahun, kesimpulan ORDER BY tahun, kesimpulan;
  ```
- **Bagaimana tren hasil pemeriksaan sarana produksi MD jenis pangan Garam, Tepung, Lemak dan Minyak Nabati sejak tahun 2024?**
  ```sql
  WITH pemeriksaan_pangan AS ( SELECT mp.id, mp.tanggal_mulai, TO_CHAR(mp.tanggal_mulai, 'YYYY-MM') AS bulan_tahun, mp.nama_upt, mpjp.jenis_pangan_name FROM mv_pemeriksaan mp JOIN mv_pemeriksaan_jenis_pangan mpjp ON mp.id = mpjp.id_pemeriksaan WHERE EXTRACT(YEAR FROM mp.tanggal_mulai) >= 2024 AND LOWER(mpjp.jenis_pangan_name) ~ '(garam|tepung|lemak|minyak nabati)' AND LOWER(mp.sarana) LIKE '%produksi%' -- karena fokusnya sarana produksi MD ) SELECT pp.bulan_tahun, pp.jenis_pangan_name, COUNT(DISTINCT pp.id) AS jumlah_pemeriksaan FROM pemeriksaan_pangan pp GROUP BY pp.bulan_tahun, pp.jenis_pangan_name ORDER BY pp.bulan_tahun, pp.jenis_pangan_name;
  ```
- **Bagaimana tren tiap kesimpulan pemeriksaan komoditi kosmetik dalam periode tahun 2024?**
  ```sql
  SELECT komoditi, kesimpulan, COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 GROUP BY komoditi, kesimpulan ORDER BY komoditi, kesimpulan;
  ```
- **Bagaimana tren tiap kesimpulan pemeriksaan sarana kosmetika dalam periode tahun 2024?**
  ```sql
  SELECT kesimpulan, COUNT(*) AS jumlah FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 GROUP BY kesimpulan ORDER BY jumlah DESC;
  ```
- **bagaimana trend hasil pemeriksaan sarana produksi md untuk jenis pangan amdk yang tidak memenuhi syarat dengan parameter uji tms dalam 5 tahun terakhir, dan dikaitkan dengan temuan-temuan hasil pemeriksaan sarana produksi di wilayah kerja upt bogor?**
  ```sql
  SELECT EXTRACT(YEAR FROM mp.tanggal_mulai) AS tahun, COUNT(DISTINCT mp.id) AS jumlah_temuan_tmk FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_temuan AS mpt ON mp.id = mpt.id_pemeriksaan WHERE mp.jenis_sarana ILIKE '%produksi%' AND mp.nama_sarana ILIKE '%md%' AND mp.komoditi ILIKE '%pangan amdk%' AND mp.kesimpulan = 'TMK' AND mpt.tp_kategori ILIKE '%tms%' AND mp.nama_upt ILIKE '%bogor%' AND EXTRACT(YEAR FROM mp.tanggal_mulai) >= EXTRACT(YEAR FROM '2025-08-13'::DATE) - 5 GROUP BY tahun ORDER BY tahun;
  ```
- **bagaimana trend pemeriksaan untuk balai besar pom di bandung**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, COUNT(*) AS jumlah_pemeriksaan FROM vw_pemeriksaan_bcc WHERE lower(nama_balai) LIKE '%bandung%' GROUP BY tahun ORDER BY tahun;
  ```
- **bagaimana trend pemeriksaan untuk balai besar pom di bandung Januari 2024 - Mei 2024 per komoditi dalam tabel?**
  ```sql
  select extract(month from tgl_end) as bulan, extract(year from tgl_end) as tahun, komoditi, count(*) as jumlah_pemeriksaan from vw_pemeriksaan_bcc where nama_balai = 'BALAI BESAR POM DI BANDUNG' and extract(year from tgl_end) = 2024 and extract(month from tgl_end) BETWEEN 1 AND 5 group by extract(month from tgl_end), extract(year from tgl_end), komoditi order by komoditi, extract(month from tgl_end), extract(year from tgl_end)
  ```
- **bagaimana trend pemeriksaan untuk balai besar pom di bandung selama tahun 2024**
  ```sql
  SELECT EXTRACT(MONTH FROM tgl_end) AS bulan, EXTRACT(YEAR FROM tgl_end) AS tahun, komoditi, COUNT(*) AS jumlah_pemeriksaan FROM vw_pemeriksaan_bcc WHERE nama_balai = 'BALAI BESAR POM DI BANDUNG' AND EXTRACT(YEAR FROM tgl_end) = 2024 GROUP BY EXTRACT(MONTH FROM tgl_end), EXTRACT(YEAR FROM tgl_end), komoditi ORDER BY komoditi, EXTRACT(MONTH FROM tgl_end), EXTRACT(YEAR FROM tgl_end)
  ```
- **berdasarkan hasil pemeriksaan selama 5 tahun terakhir, untuk sarana produksi dengan jenis pangan amdk di seluruh indonesia, bagaimana trend terkait temuan untuk pengendalian proses produksi dari masing-masing upt?**
  ```sql
  SELECT mp.nama_upt, EXTRACT(YEAR FROM mp.tanggal_mulai) AS tahun, SUM(mpt.tp_jml_temuan) AS total_temuan FROM mv_pemeriksaan AS mp JOIN mv_pemeriksaan_temuan AS mpt ON mp.id = mpt.id_pemeriksaan WHERE mp.jenis_sarana ILIKE '%produksi%' AND mp.komoditi ILIKE '%AMDK%' AND mpt.tp_kategori ILIKE '%Pengendalian Proses Produksi%' AND mp.tanggal_mulai >= '2019-01-01' GROUP BY mp.nama_upt, tahun ORDER BY mp.nama_upt, tahun;
  ```
- **Pertanyaan:  bagaimana tren hasil pemeriksaan sarana peredaran sejak tahun 2025**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS BULAN, sarana, kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE lower(sarana) LIKE '%distribusi%' AND EXTRACT(YEAR FROM tanggal_mulai) >= 2025 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3, 4 ORDER BY 1, 2, 3, 4;
  ```
- **Pertanyaan:  Tampilkan tren audit komprehensif berdasarkan tingkat kritikalitas untuk tahun 2024**
  ```sql
  SELECT TO_CHAR(mkp.tgl_end, 'YYYY-MM') AS bulan_tahun, mkp.tx_criteria AS tingkat_kritikalitas, COUNT(*) AS jumlah_audit FROM mv_kriteria_pemeriksaan mkp WHERE LOWER(mkp.tujuan) LIKE '%komprehensif%' AND EXTRACT(YEAR FROM mkp.tgl_end) = 2024 GROUP BY TO_CHAR(mkp.tgl_end, 'YYYY-MM'), mkp.tx_criteria ORDER BY bulan_tahun, tingkat_kritikalitas;
  ```
- **Pertanyaan:  tren hasil pemeriksaan MK selama tahun 2025**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS BULAN, sarana, kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE kesimpulan = 'MK' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3, 4 ORDER BY 1, 2, 3, 4;
  ```
- **Pertanyaan:  tren hasil pemeriksaan sarana pada bulan april hingga juli 2025 berdasarkan hasil kesimpulan pemeriksaannya**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS BULAN, sarana, kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) BETWEEN 4 AND 7 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3, 4 ORDER BY 1, 2, 3, 4;
  ```
- **Pertanyaan:  tren jumlah pemeriksaan sarana selama tahun 2025**  `[no-sql]`
- **Pertanyaan:  Tren tindak lanjut hasil pemeriksaan tahun 2024 terhadap industri farmasi di bandung**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS bulan, kesimpulan, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND lower(komoditi) like '%farmasi%' AND lower(kabupaten_kota) like '%bandung%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1,2,3 ORDER BY 1,2,3;
  ```
- **Pertanyaan:  Trend hasil pemeriksaan sarana produksi MD untuk jenis pangan AMDK di UPT Bogor tahun 2025**
  ```sql
  WITH pemeriksaan_amdk AS ( SELECT mp.id, mp.tanggal_mulai, TO_CHAR(mp.tanggal_mulai, 'YYYY-MM') AS bulan_tahun, mp.nama_upt FROM mv_pemeriksaan mp JOIN mv_pemeriksaan_jenis_pangan mpjp ON mp.id = mpjp.id_pemeriksaan WHERE EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND LOWER(mp.nama_upt) LIKE '%bogor%' AND LOWER(mpjp.jenis_pangan_name) LIKE '%air minum dalam kemasan%' and mp.sarana = 'PRODUKSI' ) SELECT pa.bulan_tahun, COUNT(DISTINCT pa.id) AS jumlah_pemeriksaan_amdk FROM pemeriksaan_amdk pa GROUP BY pa.bulan_tahun ORDER BY pa.bulan_tahun;
  ```
- **Pertanyaan:  Trend hasil pemeriksaan sarana produksi MD untuk jenis pangan Garam, Tepung, Lemak, dan Minyak Nabati sejak tahun 2024**
  ```sql
  WITH pemeriksaan_pangan AS ( SELECT mp.id, mp.tanggal_mulai, TO_CHAR(mp.tanggal_mulai, 'YYYY-MM') AS bulan_tahun, mp.nama_upt, mpjp.jenis_pangan_name FROM mv_pemeriksaan mp JOIN mv_pemeriksaan_jenis_pangan mpjp ON mp.id = mpjp.id_pemeriksaan WHERE EXTRACT(YEAR FROM mp.tanggal_mulai) >= 2024 AND LOWER(mpjp.jenis_pangan_name) ~ '(garam|tepung|lemak|minyak nabati)' AND LOWER(mp.sarana) LIKE '%produksi%' -- karena fokusnya sarana produksi MD ) SELECT pp.bulan_tahun, pp.jenis_pangan_name, COUNT(DISTINCT pp.id) AS jumlah_pemeriksaan FROM pemeriksaan_pangan pp GROUP BY pp.bulan_tahun, pp.jenis_pangan_name ORDER BY pp.bulan_tahun, pp.jenis_pangan_name;
  ```
- **Tampilkan data tren pemeriksaan sarana distribusi pangan pada tahun 2021**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, nama_sarana FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2021 AND lower(jenis_sarana) LIKE '%distribusi%' AND lower(komoditi) LIKE '%pangan%' GROUP BY tahun, nama_sarana ORDER BY tahun, nama_sarana
  ```
- **Tampilkan data tren pemeriksaan sarana distribusi pangan pada tahun 2021 sampai 2025**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) BETWEEN 2021 AND 2025 AND lower(jenis_sarana) LIKE 'distribusi' GROUP BY tahun ORDER BY tahun;
  ```
- **Tampilkan temuan produk kosmetik di tahun 2025 berdasarkan tren konsumen.**
  ```sql
  SELECT mpt.product_brands, mp.komoditi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND LOWER(komoditi) LIKE '%kosmetik%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3;
  ```
- **tampilkan tren audit komprehensif yang dihubungkan dengan region, kategori temuan dan tahun atau periode pengawasan 2025 untuk analisis lebih lanjut.**
  ```sql
  SELECT T1.provinsi, T2.tp_kategori, EXTRACT(YEAR FROM T1.tanggal_mulai) AS tahun_pengawasan, COUNT(DISTINCT T1.id) AS jumlah_audit FROM public.mv_pemeriksaan AS T1 JOIN public.mv_pemeriksaan_temuan AS T2 ON T1.id = T2.id_pemeriksaan WHERE EXTRACT(YEAR FROM T1.tanggal_mulai) = 2025 GROUP BY T1.provinsi, T2.tp_kategori, tahun_pengawasan ORDER BY T1.provinsi, T2.tp_kategori, tahun_pengawasan;
  ```
- **Tampilkan tren hasil kesimpulan pemeriksaan BCC untuk fasilitas produksi kosmetik pada tahun x.**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, kesimpulan, COUNT(*) FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE '%produksi%' GROUP BY tahun, kesimpulan ORDER BY tahun;
  ```
- **Tampilkan tren jumlah pemeriksaan BCC untuk fasilitas produksi kosmetik pada tahun x.**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) = 'produksi';
  ```
- **Tampilkan tren jumlah pemeriksaan dari waktu ke waktu untuk mengidentifikasi potensi penurunan pada bulan Juli 2025.**
  ```sql
  SELECT DATE_TRUNC('month', tgl_start) AS month, COUNT(*) AS total_examinations FROM public.vw_pemeriksaan_bcc WHERE tgl_start >= '2025-07-01' AND tgl_start < '2025-08-01' GROUP BY month ORDER BY month;
  ```
- **Tampilkan tren jumlah pemeriksaan dari waktu ke waktu.**
  ```sql
  SELECT tgl_start, COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE tgl_start IS NOT NULL GROUP BY tgl_start ORDER BY tgl_start;
  ```
- **Tampilkan tren jumlah pemeriksaan sarana per bulan dari Januari hingga September 2025.**
  ```sql
  SELECT EXTRACT(MONTH FROM tanggal_mulai) AS bulan, COUNT(*) AS jumlah_pemeriksaan FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) BETWEEN 1 AND 9 GROUP BY bulan ORDER BY bulan;
  ```
- **Tampilkan tren jumlah pengawasan untuk fasilitas produksi kosmetik pada tahun x.**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) = 'produksi';
  ```
- **Tampilkan tren temuan hasil pemeriksaan jenis sarana pbf pada aspek pengadaan selama periode 2022**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS BULAN, sarana, kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE lower(sarana) LIKE '%distribusi%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2022 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3, 4 ORDER BY 1, 2, 3, 4;
  ```
- **tampilkan tren temuan hasil pemeriksaan pada aspek pemusnahan selama periode 2022-01-01 sampai 2025-12-31**
  ```sql
  SELECT EXTRACT(YEAR FROM T1.tanggal_mulai) AS tahun, COUNT(T2.id_pemeriksaan) AS jumlah_temuan FROM mv_pemeriksaan AS T1 INNER JOIN mv_pemeriksaan_temuan AS T2 ON T1.id = T2.id_pemeriksaan WHERE T1.tanggal_mulai BETWEEN '2022-01-01' AND '2025-12-31' AND T2.tp_kategori ILIKE '%pemusnahan%' GROUP BY tahun ORDER BY tahun;
  ```
- **tampilkan tren temuan hasil pemeriksaan pada aspek pencatatan dan pelaporan selama periode 1 januari 2023 sampai 31 desember 2023.**
  ```sql
  SELECT TO_CHAR(tgl_start, 'YYYY-MM') AS bulan, COUNT(CASE WHEN kesimpulan = 'MK' THEN id ELSE NULL END) AS memenuhi_ketentuan, COUNT(CASE WHEN kesimpulan = 'TMK' THEN id ELSE NULL END) AS tidak_memenuhi_ketentuan, COUNT(CASE WHEN kesimpulan = 'TDP' THEN id ELSE NULL END) AS tidak_dapat_diperiksa, COUNT(CASE WHEN kesimpulan = 'TTP' THEN id ELSE NULL END) AS tutup FROM public.vw_pemeriksaan_bcc WHERE tgl_start BETWEEN '2023-01-01' AND '2023-12-31' GROUP BY bulan ORDER BY bulan;
  ```
- **tampilkan tren temuan hasil pemeriksaan pada aspek pencatatan dan pelaporan selama periode 1 januari 2025 sampai 31 desember 2025.**
  ```sql
  SELECT EXTRACT( YEAR FROM mp.tanggal_mulai ) AS tahun, EXTRACT( MONTH FROM mp.tanggal_mulai ) AS bulan, COUNT(mpt.id_pemeriksaan) AS jumlah_temuan FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_temuan AS mpt ON mp.id = mpt.id_pemeriksaan WHERE mp.tanggal_mulai >= '2025-01-01' AND mp.tanggal_mulai <= '2025-12-31' AND mpt.tp_keterangan ILIKE '%pencatatan dan pelaporan%' GROUP BY tahun, bulan ORDER BY tahun, bulan;
  ```
- **Tampilkan tren temuan hasil pemeriksaan pada aspek pencatatan dan pelaporan untuk tahun 2023.**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2023 GROUP BY tahun ORDER BY tahun;
  ```
- **Tampilkan tren temuan hasil pemeriksaan pada aspek penerimaan selama periode 2022**  `[no-sql]`
- **tampilkan tren temuan hasil pemeriksaan pada aspek penerimaan selama periode 2022-2025**
  ```sql
  SELECT EXTRACT(YEAR FROM mp.tanggal_mulai) AS tahun, SUM(mpt.tp_jml_temuan) AS total_temuan FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_temuan AS mpt ON mp.id = mpt.id_pemeriksaan WHERE mpt.tp_kategori ILIKE '%penerimaan%' AND ( EXTRACT(YEAR FROM mp.tanggal_mulai) BETWEEN 2022 AND 2025 OR EXTRACT(YEAR FROM mp.tanggal_selesai) BETWEEN 2022 AND 2025 ) GROUP BY tahun ORDER BY tahun;
  ```
- **Tampilkan tren temuan hasil pemeriksaan pada aspek penerimaan selama periode desember 2023**  `[no-sql]`
- **Tampilkan tren temuan hasil pemeriksaan pada aspek pengadaan berdasarkan jenis komoditas selama tahun 2024.**  `[no-sql]`
- **Tampilkan tren temuan hasil pemeriksaan pada aspek pengadaan berdasarkan lembaga pelaksana selama tahun 2024.**  `[no-sql]`
- **Tampilkan tren temuan hasil pemeriksaan pada aspek pengadaan berdasarkan tujuan pemeriksaan selama tahun 2024.**  `[no-sql]`
- **tampilkan tren temuan hasil pemeriksaan pada aspek pengadaan selama periode 2022-2025**
  ```sql
  SELECT EXTRACT(YEAR FROM mp.tanggal_mulai) AS tahun_pemeriksaan, SUM(mpt.tp_jml_temuan) AS total_temuan FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_temuan AS mpt ON mp.id = mpt.id_pemeriksaan WHERE mp.jenis_sarana IN ('Distribusi', 'Produksi') AND EXTRACT(YEAR FROM mp.tanggal_mulai) BETWEEN 2022 AND 2025 GROUP BY tahun_pemeriksaan ORDER BY tahun_pemeriksaan;
  ```
- **tampilkan tren temuan hasil pemeriksaan pada aspek pengembalian selama periode 2022-2025**
  ```sql
  SELECT EXTRACT( YEAR FROM mp.tanggal_mulai ) AS tahun, SUM(mpt.tp_jml_temuan) AS total_temuan FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_temuan AS mpt ON mp.id = mpt.id_pemeriksaan WHERE mp.tanggal_mulai BETWEEN '2022-01-01' AND '2025-12-31' AND mpt.tp_tindakan ILIKE '%PENARIKAN%' GROUP BY tahun ORDER BY tahun;
  ```
- **tampilkan tren temuan hasil pemeriksaan pada aspek penyerahan selama periode 2022-01-01 sampai 2025-12-31**
  ```sql
  SELECT EXTRACT(YEAR FROM mp.tanggal_mulai) AS year, EXTRACT(MONTH FROM mp.tanggal_mulai) AS month, SUM(mpt.tp_jml_temuan) AS total_temuan FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE mp.tanggal_mulai >= '2022-01-01' AND mp.tanggal_mulai <= '2025-12-31' GROUP BY year, month ORDER BY year, month;
  ```
- **tampilkan tren temuan hasil pemeriksaan pada aspek penyimpanan selama periode 2022-01-01 sampai 2025-12-31**
  ```sql
  SELECT EXTRACT( YEAR FROM p.tanggal_mulai ) AS tahun_pemeriksaan, COUNT(t.id_pemeriksaan) AS jumlah_temuan_penyimpanan FROM public.mv_pemeriksaan AS p JOIN public.mv_pemeriksaan_temuan AS t ON p.id = t.id_pemeriksaan WHERE p.tanggal_mulai >= '2022-01-01' AND p.tanggal_mulai <= '2025-12-31' AND t.tp_keterangan ILIKE '%penyimpanan%' GROUP BY tahun_pemeriksaan ORDER BY tahun_pemeriksaan;
  ```
- **tampilkan trend pemeriksaan di Jakarta tahun 2024**
  ```sql
  SELECT EXTRACT(MONTH FROM mp.tanggal_mulai) AS bulan, COUNT(*) AS jumlah_pemeriksaan FROM mv_pemeriksaan mp WHERE mp.nama_upt LIKE '%Jakarta%' AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2024 GROUP BY 1 ORDER BY 1;
  ```
- **Tolong buatkan query untuk: bagaimana tren hasil pemeriksaan sarana peredaran sejak tahun 2025**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS BULAN, nama_sarana, kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE lower(nama_sarana) LIKE '%distribusi%' AND EXTRACT(YEAR FROM tanggal_mulai) >= 2025 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3, 4 ORDER BY 1, 2, 3, 4;
  ```
- **Tolong buatkan query untuk: bagaimana tren hasil pemeriksaan sarana produksi md dan pirt sejak tahun 2024 hingga 2025?**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS bulan, jenis_sarana, count(*) FROM mv_pemeriksaan mp WHERE (lower(jenis_sarana) LIKE '%pangan md%' OR lower(jenis_sarana) LIKE '%pangan irt%') AND EXTRACT(YEAR FROM tanggal_mulai) BETWEEN 2024 AND 2025 AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3 ORDER BY 1, 2, 3;
  ```
- **tren audit komprehensif yang dihubungkan dengan region, kategori temuan dan tahun atau periode pengawasan**
  ```sql
  SELECT EXTRACT(YEAR FROM mp.tanggal_mulai) AS tahun, mp.provinsi, mpt.tp_kategori, COUNT(DISTINCT mp.id) AS jumlah_pemeriksaan FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.tujuan_pemeriksaan) LIKE '%komprehensif%' GROUP BY 1, 2, 3 ORDER BY 1, 2, 3;
  ```
- **tren hasil pemeriksaan per bulan dengan kesimpulan MK selama tahun 2025**  `[no-sql]`
- **trend hasil pemeriksaan balai pom di dumai pada bulan september 2025**
  ```sql
  SELECT kesimpulan, COUNT(*) AS jumlah_pemeriksaan FROM public.mv_pemeriksaan WHERE lower(nama_upt) LIKE '%balai pom di dumai%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) = 9 GROUP BY kesimpulan;
  ```
- **Tunjukan hasil tren pemeriksaan sarana distribusi pangan olahan mulai dari tahun 2021 sampai dengan 2025**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) >= 2021 and EXTRACT(YEAR FROM tgl_start) <= 2025 and lower(jenis_sarana) like 'distribusi' GROUP BY tahun ORDER BY tahun;
  ```
- **visualisasikan trend perkembangan jumlah pemeriksaan per bulan di 2025**
  ```sql
  SELECT EXTRACT(MONTH FROM tgl_start) AS month, COUNT(id) AS total_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY month ORDER BY month;
  ```

### Perbandingan A vs B — 6 pertanyaan

**SQL template warehouse (kanonik):**
```sql
SELECT date_trunc('month', tanggal_mulai)::date AS bln, COUNT(DISTINCT id)
FROM mv_pemeriksaan
WHERE tanggal_mulai >= '2025-01-01' AND tanggal_mulai < '2025-03-01'
GROUP BY 1 ORDER BY 1;
```
*Jawab dua angka + selisih + arah (naik/turun).*

- **Apakah jumlah entri tahun lalu lebih banyak dari jumlah pemeriksaan tahun ini?**
  ```sql
  SELECT CASE WHEN ( SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) = EXTRACT( YEAR FROM CURRENT_DATE - INTERVAL '1 year' ) ) > ( SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) = EXTRACT( YEAR FROM CURRENT_DATE ) ) THEN 'Yes' ELSE 'No' END;
  ```
- **Apakah jumlah pemeriksaan tahun ini lebih banyak dibandingkan tahun lalu?**
  ```sql
  SELECT CASE WHEN ( SELECT COUNT(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) = EXTRACT( YEAR FROM CURRENT_DATE ) ) > ( SELECT COUNT(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) = EXTRACT( YEAR FROM CURRENT_DATE ) - 1 ) THEN 'Yes' ELSE 'No' END;
  ```
- **Berapa perbandingan jumlah pemeriksaan sarana produksi pangan olahan dibandingkan dengan pemeriksaan sarana produksi pangan fortifikasi pada rentang waktu Januari sampai dengan Juli 2025?**
  ```sql
  SELECT SUM(CASE WHEN lower(komoditi) LIKE '%pangan olahan%' THEN 1 ELSE 0 END) AS jumlah_pangan_olahan, SUM(CASE WHEN lower(komoditi) LIKE '%pangan fortifikasi%' THEN 1 ELSE 0 END) AS jumlah_pangan_fortifikasi, CAST(SUM(CASE WHEN lower(komoditi) LIKE '%pangan olahan%' THEN 1 ELSE 0 END) AS NUMERIC) / NULLIF(SUM(CASE WHEN lower(komoditi) LIKE '%pangan fortifikasi%' THEN 1 ELSE 0 END), 0) AS perbandingan FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) BETWEEN 1 AND 7 AND lower(jenis_sarana) LIKE '%produksi%';
  ```
- **Tampilkan jumlah pemeriksaan sarana produksi pangan dengan hasil TMK dibandingkan dengan jumlah pemeriksaan rutin sarana produksi pangan selama Januari hingga Juli 2025 berdasarkan Jenis Fasilitas.**
  ```sql
  SELECT jenis_sarana, SUM(CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE 0 END) AS jumlah_tmk, SUM(CASE WHEN lower(tujuan) LIKE '%rutin%' THEN 1 ELSE 0 END) AS jumlah_rutin FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) BETWEEN 1 AND 7 AND lower(jenis_sarana) LIKE '%produksi%' GROUP BY jenis_sarana;
  ```
- **Tampilkan jumlah pemeriksaan sarana produksi pangan dengan hasil TMK dibandingkan dengan jumlah pemeriksaan rutin sarana produksi pangan selama Januari hingga Juli 2025 berdasarkan Tingkat Pelatihan Inspektur.**
  ```sql
  SELECT SUM(CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE 0 END) AS jumlah_tmk, COUNT(id) AS jumlah_rutin FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) BETWEEN 1 AND 7 AND lower(jenis_sarana) LIKE 'produksi';
  ```
- **total pemeriksaan bulan januari gimana? kalau dibandingkan dengan bulan februari gimana? secara keseluruhan apakah menurun atau malah lebih banyak? kalo lebih banyak, pemeriksaan yang memenuhi ketentuan lebih banyak mana sih**
  ```sql
  WITH MonthlyCounts AS ( SELECT EXTRACT(MONTH FROM tgl_start) AS month, COUNT(*) AS total_pemeriksaan, SUM(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE 0 END) AS pemeriksaan_memenuhi_ketentuan FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(MONTH FROM tgl_start) IN (1,2) GROUP BY EXTRACT(MONTH FROM tgl_start) ), JanCount AS ( SELECT total_pemeriksaan AS total_jan, pemeriksaan_memenuhi_ketentuan AS memenuhi_jan FROM MonthlyCounts WHERE month = 1 ), FebCount AS ( SELECT total_pemeriksaan AS total_feb, pemeriksaan_memenuhi_ketentuan AS memenuhi_feb FROM MonthlyCounts WHERE month = 2 ) SELECT (SELECT total_jan FROM JanCount) AS total_pemeriksaan_januari, (SELECT total_feb FROM FebCount) AS total_pemeriksaan_februari, CASE WHEN (SELECT total_jan FROM JanCount) > (SELECT total_feb FROM FebCount) THEN 'Menurun' WHEN (SELECT total_jan FROM JanCount) < (SELECT total_feb FROM FebCount) THEN 'Lebih Banyak' ELSE 'Sama' END AS perbandingan_total, (SELECT memenuhi_jan FROM JanCount) AS pemeriksaan_memenuhi_ketentuan_januari, (SELECT memenuhi_feb FROM FebCount) AS pemeriksaan_memenuhi_ketentuan_februari, CASE WHEN (SELECT memenuhi_jan FROM JanCount) > (SELECT memenuhi_feb FROM FebCount) THEN 'Januari' WHEN (SELECT memenuhi_jan FROM JanCount) < (SELECT memenuhi_feb FROM FebCount) THEN 'Februari' ELSE 'Sama' END AS perbandingan_memenuhi_ketentuan FROM JanCount LIMIT 1;
  ```

### Ranking top N — 40 pertanyaan

**SQL template warehouse (kanonik):**
```sql
SELECT nama_upt, COUNT(DISTINCT id) AS jml
FROM mv_pemeriksaan
WHERE tanggal_mulai >= '2025-01-01' AND tanggal_mulai < '2026-01-01'
GROUP BY 1 ORDER BY 2 DESC LIMIT 5;
```
*Group by dimensi + ORDER BY DESC + LIMIT N.*

- **"berdasarkan hasil pemeriksaan selama 5 tahun terakhir, untuk sarana produksi dengan jenis pangan amdk di seluruh indonesia, 10 temuan yang terbanyak terkait unsur apa?"**
  ```sql
  SELECT 'unsur yang tidak memenuhi ketentuan' AS unsur FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) >= EXTRACT( YEAR FROM CURRENT_DATE ) - 5 AND jenis_sarana = 'Produksi' AND komoditi = 'AMDK' AND kesimpulan = 'TMK' LIMIT 10;
  ```
- **"tampilkan merek-merek temuan produk kosmetik pada pemeriksaan tahun 2023 diurutkan berdasarkan temuan yang terbanyak?"**
  ```sql
  SELECT nama_sarana, COUNT(*) AS jumlah_temuan FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2023 GROUP BY nama_sarana ORDER BY jumlah_temuan DESC;
  ```
- **"upt manakah yang hasil pemeriksaannya memiliki perserntase tmk terbanyak pada tahun 2025"**
  ```sql
  SELECT nama_upt FROM ( SELECT nama_balai AS nama_upt, SUM(CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE 0 END) AS jumlah_tmk, COUNT(*) AS total, (SUM(CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)::NUMERIC) * 100 AS persentase_tmk FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY nama_balai ) AS subquery ORDER BY persentase_tmk DESC LIMIT 1;
  ```
- **'Tolong buatkan query untuk: 'Balai mana yang melakukan jumlah pemeriksaan terbanyak?**
  ```sql
  SELECT nama_upt, count(*) FROM public.mv_pemeriksaan GROUP BY nama_upt ORDER BY count(*) DESC LIMIT 10;
  ```
- **balai mana yang melakukan pemeriksaan terbanyak**
  ```sql
  SELECT nama_balai FROM public.vw_pemeriksaan_bcc GROUP BY nama_balai ORDER BY COUNT(*) DESC LIMIT 1;
  ```
- **Balai mana yang melakukan pemeriksaan terbanyak pada bulan Juli 2025?**
  ```sql
  SELECT nama_balai FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) = 7 GROUP BY nama_balai ORDER BY COUNT(*) DESC LIMIT 1;
  ```
- **Balai mana yang memiliki jumlah pemeriksaan 'TMK' tertinggi pada bulan Juli 2025?**
  ```sql
  SELECT nama_balai, count(*) as jumlah_tmk FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) = 7 AND kesimpulan = 'TMK' GROUP BY nama_balai ORDER BY COUNT(*) DESC LIMIT 1;
  ```
- **Balai mana yang memiliki jumlah pemeriksaan dengan kesimpulan 'TMK' tertinggi pada bulan Juli 2025?**
  ```sql
  SELECT nama_balai, count(*) AS jumlah_tmk FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) = 7 AND kesimpulan = 'TMK' GROUP BY nama_balai ORDER BY COUNT(*) DESC LIMIT 1;
  ```
- **Balai mana yang memiliki jumlah pemeriksaan tertinggi**
  ```sql
  SELECT nama_balai, COUNT(*) AS jumlah_pemeriksaan FROM vw_pemeriksaan_bcc GROUP BY nama_balai ORDER BY jumlah_pemeriksaan DESC LIMIT 1
  ```
- **Balai mana yang memiliki jumlah pemeriksaan tertinggi pada bulan Juli 2025?**
  ```sql
  SELECT nama_balai, count(*) as jumlah_pemeriksaan FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) = 7 GROUP BY nama_balai ORDER BY COUNT(*) DESC LIMIT 1;
  ```
- **Balai mana yang memiliki jumlah pemeriksaan tertinggi pada bulan Juni 2025**
  ```sql
  SELECT nama_balai, COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE tgl_start >= '2025-06-01' AND tgl_end <= '2025-06-30' GROUP BY nama_balai ORDER BY jumlah_pemeriksaan DESC LIMIT 1;
  ```
- **Balai mana yang memiliki jumlah pemeriksaan tertinggi?**
  ```sql
  SELECT nama_balai, COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc GROUP BY nama_balai ORDER BY jumlah_pemeriksaan DESC LIMIT 1;
  ```
- **Balai mana yang terdaftar dalam data Top 5 Balai?**
  ```sql
  SELECT DISTINCT nama_balai FROM vw_pemeriksaan_bcc;
  ```
- **berdasarkan hasil pemeriksaan selama 5 tahun terakhir, untuk sarana produksi dengan jenis pangan amdk di seluruh indonesia, 10 temuan yang terbanyak terkait unsur apa?**
  ```sql
  SELECT t2.tp_kategori, COUNT(t2.tp_kategori) AS jumlah_temuan FROM mv_pemeriksaan AS t1 INNER JOIN mv_pemeriksaan_temuan AS t2 ON t1.id = t2.id_pemeriksaan WHERE t1.jenis_sarana ILIKE '%produksi%' AND t1.komoditi ILIKE '%amdk%' AND t1.tanggal_mulai >= '2020-08-13' GROUP BY t2.tp_kategori ORDER BY jumlah_temuan DESC LIMIT 10;
  ```
- **berikan top 5 pemeriksaan berdasar provinsi**
  ```sql
  SELECT provinsi, COUNT(id) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc GROUP BY provinsi ORDER BY jumlah_pemeriksaan DESC LIMIT 5;
  ```
- **berikan top 5 pemeriksaan berdasarkan balai**
  ```sql
  SELECT nama_balai, COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc GROUP BY nama_balai ORDER BY jumlah_pemeriksaan DESC LIMIT 5;
  ```
- **berikan top 5 pemeriksaan berdasarkan balai dalam tabel**
  ```sql
  SELECT nama_balai, COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc GROUP BY nama_balai ORDER BY jumlah_pemeriksaan DESC LIMIT 5;
  ```
- **pemeriksaan untuk komoditas obat tertinggi**
  ```sql
  SELECT komoditi, COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc GROUP BY komoditi ORDER BY jumlah_pemeriksaan DESC LIMIT 1;
  ```
- **Pertanyaan:  Balai mana yang melakukan jumlah pemeriksaan terbanyak di bulan Oktober 2025?**
  ```sql
  SELECT nama_upt, count(*) AS jumlah_pemeriksaan FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) = 10 GROUP BY nama_upt ORDER BY jumlah_pemeriksaan DESC LIMIT 1;
  ```
- **Pertanyaan:  Balai mana yang memiliki jumlah pemeriksaan 'TMK' tertinggi pada bulan Juli 2025?**
  ```sql
  SELECT nama_upt, kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND lower(kesimpulan) = 'tmk' AND EXTRACT(MONTH FROM tanggal_mulai) = 7 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY 1, 2 ORDER BY 3 DESC LIMIT 5;
  ```
- **Pertanyaan:  Berdasarkan hasil pemeriksaan selama 2 tahun terakhir, untuk sarana produksi dengan jenis pangan AMDK di seluruh Indonesia 10 temuan yang terbanyak adalah kategori apa?**
  ```sql
  WITH pemeriksaan_amdk AS ( SELECT mp.id FROM mv_pemeriksaan mp JOIN mv_pemeriksaan_jenis_pangan mpjp ON mp.id = mpjp.id_pemeriksaan WHERE LOWER(mp.sarana) LIKE '%produksi%' AND LOWER(mpjp.jenis_pangan_name) LIKE '%air minum dalam kemasan%' AND EXTRACT(YEAR FROM mp.tanggal_mulai) >= EXTRACT(YEAR FROM CURRENT_DATE) - 2 ) SELECT mpkt.tp_kategori, COUNT(*) AS jumlah_temuan FROM mv_pemeriksaan_kategori_temuan mpkt JOIN pemeriksaan_amdk pam ON pam.id = mpkt.id_pemeriksaan GROUP BY mpkt.tp_kategori ORDER BY jumlah_temuan DESC LIMIT 10;
  ```
- **Pertanyaan:  Produk apa yang memiliki jumlah 'Tidak Memenuhi Ketentuan' TMK terbanyak dari hasil pemeriksaan Balai POM di Dumai pada tahun 2024 - 2025?**
  ```sql
  SELECT mpt.product_name, COUNT(mpt.product_name) AS jumlah_tmk FROM public.mv_pemeriksaan mp LEFT JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM mp.tanggal_mulai) BETWEEN 2024 AND 2025 AND mp.nama_upt LIKE '%Dumai%' AND mp.kesimpulan = 'TMK' GROUP BY mpt.product_name ORDER BY jumlah_tmk DESC LIMIT 1;
  ```
- **Pertanyaan:  Provinsi mana yang memiliki jumlah pemeriksaan terbanyak di bulan Oktober 2025?**
  ```sql
  SELECT provinsi, COUNT(*) AS jumlah_pemeriksaan FROM mv_pemeriksaan WHERE EXTRACT(MONTH FROM tanggal_mulai) = 10 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY provinsi ORDER BY jumlah_pemeriksaan DESC LIMIT 1;
  ```
- **Pertanyaan:  sebutkan 10 temuan terbanyak dari hasil pemeriksaan sarana produksi pangan pada tw 1 tahun 2025**
  ```sql
  SELECT mpt.tp_pelanggaran, COUNT(*) AS jumlah_temuan FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE mp.sarana LIKE '%produksi%' AND EXTRACT( YEAR FROM mp.tanggal_mulai ) = 2025 AND EXTRACT( QUARTER FROM mp.tanggal_mulai ) = 1 GROUP BY mpt.tp_pelanggaran ORDER BY jumlah_temuan DESC LIMIT 10;
  ```
- **provinsi mana yang memiliki jumlah pemeriksaan terbanyak di bulan desember 2024?**
  ```sql
  SELECT provinsi, COUNT(*) AS jumlah_pemeriksaan FROM mv_pemeriksaan WHERE EXTRACT(MONTH FROM tanggal_mulai) = 12 AND EXTRACT(YEAR FROM tanggal_mulai) = 2024 GROUP BY provinsi ORDER BY jumlah_pemeriksaan DESC LIMIT 1;
  ```
- **Provinsi mana yang memiliki jumlah pemeriksaan tertinggi pada bulan Juni 2025**
  ```sql
  SELECT provinsi, COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE tgl_start >= '2025-06-01' AND tgl_end <= '2025-06-30' GROUP BY provinsi ORDER BY jumlah_pemeriksaan DESC LIMIT 1;
  ```
- **Provinsi mana yang memiliki jumlah sarana terbanyak yang diperiksa?**
  ```sql
  SELECT provinsi FROM public.vw_pemeriksaan_bcc GROUP BY provinsi ORDER BY count(*) DESC LIMIT 1
  ```
- **Tampilkan dalam bentuk tabel daftar nama Balai, jumlah total target, jumlah total pemeriksaan dikelompokkan berdasarkan sarana dan tahun dari tahun 2023 sampai dengan juni 2025 dan peringkat jumlah pemeriksaan terbesar ke terkecil**  `[no-sql]`
- **Tampilkan dalam bentuk tabel daftar nama Balai, jumlah total target, jumlah total pemeriksaan dikelompokkan berdasarkan sarana dan tahun dari tahun 2023 sampai dengan juni 2025 fan peringkat jumlah pemeriksaan terbesar ke terkecil**
  ```sql
  SELECT nama_balai, EXTRACT(YEAR FROM tgl_start) AS tahun, nama_sarana, SUM(target) AS total_target, COUNT(*) AS total_pemeriksaan FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) >= 2023 AND tgl_start <= '2025-06-30' GROUP BY nama_balai, EXTRACT(YEAR FROM tgl_start), nama_sarana ORDER BY total_pemeriksaan DESC;
  ```
- **Tampilkan dalam bentuk tabel daftar nama Balai, jumlah total target, jumlah total pemeriksaan dikelompokkan berdasarkan sarana selma tahun 2024 dengan peringkat jumlah pemeriksaan terbesar ke terkecil**
  ```sql
  SELECT nama_balai, COUNT(DISTINCT target), COUNT(id), nama_sarana FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 GROUP BY nama_balai, nama_sarana ORDER BY COUNT(id) DESC;
  ```
- **tampilkan merek-merek temuan produk kosmetik pada pemeriksaan tahun 2025 diurutkan berdasarkan temuan yang terbanyak?**
  ```sql
  SELECT mpt.product_brands, mp.komoditi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND LOWER(komoditi) LIKE '%kosmetik%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3 ORDER BY 4 DESC;
  ```
- **tampilkan sarana peredaran yang memiliki riwayat hasil tmk terbanyak di upt dengan nama balai pom di jakarta.**
  ```sql
  SELECT nama_sarana FROM public.mv_pemeriksaan WHERE kesimpulan = 'TMK' AND nama_upt ILIKE '%BALAI BESAR POM DI JAKARTA%' GROUP BY nama_sarana ORDER BY COUNT(kesimpulan) DESC LIMIT 1;
  ```
- **Tolong buatkan query untuk: Balai mana yang melakukan jumlah pemeriksaan terbanyak?**
  ```sql
  SELECT nama_upt, count(*) FROM public.mv_pemeriksaan GROUP BY nama_upt ORDER BY COUNT(*) DESC LIMIT 10;
  ```
- **Tolong buatkan query untuk: berikan top 5 upt yang paling banyak melaporkan hasil pemeriksaan penandaan dengan kesimpulan upt memenuhi ketentuan?**
  ```sql
  SELECT nama_balai, count(*) FROM vw_penandaan WHERE kesimpulan_penilaian_pusat = 'MK' GROUP BY nama_balai ORDER BY COUNT(*) DESC LIMIT 5
  ```
- **Tolong buatkan query untuk: tampilkan sarana peredaran yang memiliki riwayat hasil tmk terbanyak di upt dengan nama balai pom di jakarta.**
  ```sql
  SELECT mp.nama_sarana, mp.kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND kesimpulan = 'TMK' AND lower(mp.sarana) LIKE '%distribusi%' AND lower(nama_upt) LIKE '%pom di jakarta%' GROUP BY 1, 2 ORDER BY 3 DESC;
  ```
- **Tunjukan data UPT dengan hasil pemeriksaan sarana distribusi pangan dengan jumlah Tidak Memenuhi Ketentuan terbanyak**
  ```sql
  SELECT nama_balai, COUNT(*) as jumlah_pemeriksaan FROM vw_pemeriksaan_bcc WHERE kesimpulan = 'TMK' AND lower(jenis_sarana) LIKE 'distribusi' GROUP BY nama_balai ORDER BY count(*) desc limit 5
  ```
- **Tunjukan data UPT dengan hasil pemeriksaan sarana distribusi pangan terbanyak**
  ```sql
  SELECT nama_balai, count(*) FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) like 'distribusi' GROUP BY nama_balai ORDER BY COUNT(*) DESC LIMIT 5
  ```
- **tunjukkan 5 balai dengan jumlah pemeriksaan tertinggi untuk berdasarkan komoditas**
  ```sql
  SELECT nama_balai, komoditi, COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc GROUP BY nama_balai, komoditi ORDER BY jumlah_pemeriksaan DESC LIMIT 5;
  ```
- **upt manakah yang hasil pemeriksaannya memiliki perserntase tmk terbanyak pada tahun 2025**
  ```sql
  SELECT nama_upt, CAST(SUM(CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE 0 END) AS DECIMAL) * 100 / COUNT(*) AS percentage_tmk FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY nama_upt ORDER BY percentage_tmk DESC LIMIT 1;
  ```
- **UPT manakah yang memiliki jumlah hasil pemeriksaan TMK sarana produksi MD terbanyak di tahun 2025?**
  ```sql
  SELECT nama_balai FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND jenis_sarana = 'Produksi' AND kesimpulan = 'TMK' GROUP BY nama_balai ORDER BY COUNT(*) DESC LIMIT 1;
  ```

### Ranking bottom N — 3 pertanyaan

**SQL template warehouse (kanonik):**
```sql
SELECT nama_upt, COUNT(DISTINCT id) AS jml
FROM mv_pemeriksaan
WHERE tanggal_mulai >= '2025-01-01' AND tanggal_mulai < '2026-01-01'
GROUP BY 1 ORDER BY 2 ASC LIMIT 5;
```
*Sama dengan top, ORDER BY ASC. Hati-hati balai kecil = mungkin Loka/baru.*

- **Balai mana saja yang termasuk dalam Bottom 5 Balai berdasarkan jumlah pemeriksaan**
  ```sql
  SELECT nama_balai, COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc GROUP BY nama_balai ORDER BY jumlah_pemeriksaan ASC LIMIT 5;
  ```
- **Balai mana yang memiliki jumlah pemeriksaan 'TMK' terendah pada bulan Juli 2025?**
  ```sql
  SELECT nama_balai, count(*) as jumlah_tmk FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) = 7 AND kesimpulan = 'TMK' GROUP BY nama_balai ORDER BY COUNT(*) ASC LIMIT 1;
  ```
- **Balai mana yang memiliki jumlah pemeriksaan paling sedikit**
  ```sql
  SELECT nama_balai, COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc GROUP BY nama_balai ORDER BY jumlah_pemeriksaan ASC LIMIT 1;
  ```

### Grade — 1 pertanyaan

**SQL template warehouse (kanonik):**
```sql
SELECT grade, COUNT(DISTINCT id) FROM mv_pemeriksaan
WHERE grade IN ('A','B','C')
GROUP BY 1;
```
*Grade 83% NULL (structural). User kadang definisikan grading logic custom.*

- **Pertanyaan:  Tampilkan persentase ketepatan grading hasil pemeriksaan di UPT Balai POM di Bogor pada tahun 2025 Grading A -> kesimpulan harus MK Grading B-C -> kesimpulan harus TMK**
  ```sql
  WITH data_grading AS ( SELECT mp.grade, mp.kesimpulan, CASE WHEN UPPER(mp.grade) = 'A' AND UPPER(mp.kesimpulan) = 'MK' THEN 1 WHEN UPPER(mp.grade) IN ('B', 'C') AND UPPER(mp.kesimpulan) = 'TMK' THEN 1 ELSE 0 END AS tepat FROM mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND mp.grade IS NOT NULL AND LOWER(mp.nama_upt) LIKE '%bogor%' ) SELECT grade, COUNT(*) AS total_pemeriksaan, SUM(tepat) AS jumlah_tepat, COUNT(*) - SUM(tepat) AS jumlah_tidak_tepat, ROUND((SUM(tepat)::decimal / NULLIF(COUNT(*), 0)) * 100, 2) AS persentase_ketepatan FROM data_grading GROUP BY grade ORDER BY grade;
  ```

### Filter status workflow — 6 pertanyaan

**SQL template warehouse (kanonik):**
```sql
SELECT status, COUNT(DISTINCT id) FROM mv_pemeriksaan
WHERE status IN ('FINISHED','FINISHED_PUSAT')
GROUP BY 1;
```
*17 status. "selesai" = FINISHED + FINISHED_PUSAT. "draft" = DRAFT*.*

- **Pertanyaan:  bisakan tampilkan data pemeriksaan MD tahun 2025 yang statusnya TMK**
  ```sql
  SELECT mpt.tp_kategori, count(*) AS jumlah_pemeriksaan, sum(mpt.tp_jml_temuan) AS jumlah_temuan, sum(mpt.tp_harga_total) AS nilai_temuan FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY 1;
  ```
- **Tampilkan catatan pemeliharaan atau status kalibrasi peralatan yang menunjukkan masalah atau ketidaksesuaian di sarana produksi alat kesehatan.**
  ```sql
  SELECT mp.nama_sarana, mpt.tp_pelanggaran, mpt.tp_keterangan, mpt.tp_tindakan FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.jenis_sarana) LIKE '%alat kesehatan%' AND lower(mp.sarana) LIKE '%produksi%' AND (mpt.tp_pelanggaran IS NOT NULL OR mpt.tp_keterangan IS NOT NULL OR mpt.tp_tindakan IS NOT NULL);
  ```
- **Tampilkan jumlah pengawasan bulanan yang selesai untuk komoditi kosmetika di tahun 2025.**
  ```sql
  SELECT EXTRACT(MONTH FROM tgl_start) AS bulan, COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND komoditi ILIKE '%kosmetika%' GROUP BY EXTRACT(MONTH FROM tgl_start) ORDER BY EXTRACT(MONTH FROM tgl_start);
  ```
- **Tampilkan Profil Pemeriksaan Sarana Distribusi Obat dan Makanan selama periode 2022 - 2024 dengan status MK**
  ```sql
  SELECT komoditi, kesimpulan, COUNT(*) AS jumlah_pemeriksaan FROM vw_pemeriksaan_bcc where kesimpulan = 'MK' and EXTRACT(YEAR FROM tgl_end) BETWEEN 2022 AND 2024 and lower(jenis_sarana) like 'distribusi' and komoditi in ('OBAT', 'KOSMETIK', 'SUPLEMEN KESEHATAN', 'PRODUK Pangan') GROUP BY komoditi, kesimpulan ORDER BY komoditi, kesimpulan
  ```
- **Tampilkan Profil Pemeriksaan Sarana Distribusi Obat dan Makanan selama periode 2022 - 2024 dengan status TMK**
  ```sql
  SELECT komoditi, kesimpulan, COUNT(*) AS jumlah_pemeriksaan FROM vw_pemeriksaan_bcc where kesimpulan = 'TMK' and extract(year from tgl_end) BETWEEN 2022 AND 2024 and lower(jenis_sarana) LIKE '%distribusi%' and komoditi in ('OBAT', 'KOSMETIK', 'SUPLEMEN KESEHATAN', 'PRODUK Pangan') GROUP BY komoditi, kesimpulan ORDER BY komoditi, kesimpulan
  ```
- **Tampilkan status kepatuhan regulasi sarana yang diperiksa BPOM terkait kosmetik setiap tahunnya.**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, kesimpulan, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE lower(komoditi) LIKE '%kosmetik%' GROUP BY EXTRACT(YEAR FROM tgl_start), kesimpulan ORDER BY EXTRACT(YEAR FROM tgl_start);
  ```

### Produk impor / importir — 36 pertanyaan

**SQL template warehouse (kanonik):**
```sql
SELECT DISTINCT nama_sarana FROM mv_pemeriksaan
WHERE jenis_sarana ILIKE '%IMPORTIR%'
  AND tanggal_mulai >= '2023-01-01' AND tanggal_mulai < '2024-01-01';
```
*Importir = jenis_sarana LIKE %importir%. Negara asal di tp_negara (1.299 varian!).*

- **"sarana importir apa saja yang pernah diperiksa oleh badan pom pada tahun 2023?"**
  ```sql
  SELECT DISTINCT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2023 AND jenis_sarana LIKE '%Pelayanan%' ;
  ```
- **"tampilkan negara-negara dengan temuan impor pada tahun 2023?"**
  ```sql
  -- Belum ada informasi mengenai impor pada table vw_pemeriksaan_bcc -- Mencoba mencari informasi negara berdasarkan nama sarana SELECT DISTINCT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2023;
  ```
- **bagaimana riwayat importasi untuk PT Qiqi Kosmetik Indonesia**  `[no-sql]`
- **Berapa jumlah fasilitas importir yang tidak memenuhi ketentuan**
  ```sql
  SELECT count(*) FROM vw_pemeriksaan_bcc vpb WHERE kesimpulan LIKE 'TMK'
  ```
- **Berapa jumlah sarana importir yang diperiksa tahun 2025**
  ```sql
  SELECT count(*) FROM vw_pemeriksaan_bcc vpb WHERE EXTRACT(YEAR FROM tgl_start) = 2025
  ```
- **hasil pemeriksaan importir di Surabaya tahun 2025**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE lower(nama_balai) LIKE '%surabaya%' AND EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(nama_sarana) LIKE '%importir%'
  ```
- **Hasil pemeriksaan sarana importir tahun 2025**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY tahun ORDER BY tahun;
  ```
- **jumlah importir yang dilakukan pemeriksaan pada tahun 2025 di tangerang**
  ```sql
  SELECT count(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND LOWER(kabupaten) LIKE '%tangerang%';
  ```
- **jumlah importit yang dilakukan pemeriksaan pada tahun 2025**
  ```sql
  SELECT COUNT(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025;
  ```
- **jumlah pemeriksaan sarana importir yang tidak memenuhi ketentuan**
  ```sql
  SELECT count(*) FROM vw_pemeriksaan_bcc vpb WHERE lower(jenis_sarana) LIKE '%importir%' AND kesimpulan LIKE 'TMK'
  ```
- **Jumlah sarana importir yang memenuhi ketentuan tahun 2025**
  ```sql
  SELECT count(*) FROM vw_pemeriksaan_bcc vpb WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND kesimpulan LIKE 'MK' AND lower(jenis_pelaku) LIKE '%importir%'
  ```
- **Pertanyaan:  Sarana Importir apa saja yang pernah diperiksa oleh Badan POM?**
  ```sql
  select distinct(nama_sarana), klasifikasi_distribusi from mv_pemeriksaan mp where lower(mp.klasifikasi_distribusi) like '%importir%'
  ```
- **Pertanyaan:  Sarana Importir apa saja yang pernah diperiksa?**
  ```sql
  select distinct(nama_sarana), klasifikasi_distribusi from mv_pemeriksaan mp where lower(mp.klasifikasi_distribusi) like '%importir%'
  ```
- **Pertanyaan:  Tampilkan negara-negara dengan temuan impor pada tahun 2025 negara dengan input text selain indonesia**
  ```sql
  select mpt.tp_negara, sum(mpt.tp_harga_total) from mv_pemeriksaan_temuan mpt join mv_pemeriksaan mp on mpt.id_pemeriksaan = mp.id where lower(mpt.tp_negara) != 'indonesia' and mpt.tp_harga_total is not null and extract(year from mp.tanggal_selesai) = 2025 group by 1 order by 2 desc
  ```
- **Pertanyaan:  tampilkan negara-negara dengan temuan impor pada tahun 2025?**
  ```sql
  SELECT mpt.tp_negara FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND lower(mpt.tp_negara) NOT LIKE '%indonesia%' GROUP BY mpt.tp_negara;
  ```
- **Sarana Importir apa saja yang pernah diperiksa oleh Badan POM**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE '%importir%' GROUP BY nama_sarana;
  ```
- **sarana importir apa saja yang pernah diperiksa oleh badan pom pada tahun 2025?**
  ```sql
  SELECT DISTINCT nama_sarana FROM public.mv_pemeriksaan WHERE LOWER(nama_sarana) LIKE '%importir%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Sarana Importir apa saja yang pernah diperiksa oleh Badan POM?**
  ```sql
  select distinct(nama_sarana), klasifikasi_distribusi from mv_pemeriksaan mp where lower(mp.klasifikasi_distribusi) like '%importir%'
  ```
- **sarana importir apa saja yang pernah diperiksa oleh BPOM**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(nama_sarana) LIKE '%importir%' GROUP BY nama_sarana;
  ```
- **Sarana Importir apa saja yang pernah diperiksa?**
  ```sql
  select distinct(nama_sarana), klasifikasi_distribusi from mv_pemeriksaan mp where lower(mp.klasifikasi_distribusi) like '%importir%'
  ```
- **Sarana Importir kosmetik apa saja yang pernah diperiksa oleh Badan POM?**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE '%importir%' AND lower(komoditi) LIKE '%kosmetik%' GROUP BY nama_sarana;
  ```
- **Sarana Importir kosmetika apa saja yang pernah diperiksa oleh Badan POM**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE '%importir%' AND lower(komoditi) LIKE '%kosmetik%' GROUP BY nama_sarana;
  ```
- **sarana importir yang melakukan pelanggaran tahun 2024**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(jenis_sarana) ILIKE 'importir' AND kesimpulan = 'TMK';
  ```
- **sarana importir yang melakukan pelanggaran tahun 2025**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'importir' AND EXTRACT(YEAR FROM tgl_start) = 2025 AND kesimpulan LIKE 'TMK' GROUP BY nama_sarana;
  ```
- **tampilkan importir yang diperiksa tahun 2024**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(tujuan) LIKE '%importir%';
  ```
- **tampilkan kategori importir tahun 2024**
  ```sql
  SELECT kategori_importir, COUNT(*) FROM importir WHERE EXTRACT(YEAR FROM tgl_daftar) = 2024 GROUP BY kategori_importir;
  ```
- **tampilkan klausul yang sering tmk untuk klasifikasi sarana peredaran ritel tradisional, ritel modern, distributor, dan importir di tingkat nasional**
  ```sql
  SELECT t2.tp_kategori, COUNT(t2.tp_kategori) AS frequency FROM mv_pemeriksaan AS t1 JOIN mv_pemeriksaan_temuan AS t2 ON t1.id = t2.id_pemeriksaan WHERE t1.kesimpulan = 'TMK' AND t1.sarana IN ('Ritel Tradisional', 'Ritel Modern', 'Distributor', 'Importir') GROUP BY t2.tp_kategori ORDER BY frequency DESC LIMIT 5;
  ```
- **tampilkan negara temuan kosmetik impor**
  ```sql
  SELECT DISTINCT negara_temuan FROM vw_pemeriksaan_bcc WHERE lower(asal_komoditi) LIKE 'impor' AND komoditi LIKE 'Kosmetik' GROUP BY negara_temuan;
  ```
- **Tampilkan negara-negara dengan temuan impor pada tahun 2024**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024
  ```
- **Tampilkan negara-negara dengan temuan impor pada tahun 2025**
  ```sql
  SELECT negara_asal_temuan FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(keterangan_temuan) LIKE '%impor%' GROUP BY negara_asal_temuan
  ```
- **tampilkan negara-negara dengan temuan impor pada tahun 2025?**
  ```sql
  SELECT mpt.tp_negara FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025
  ```
- **tampilkan negara-negara dengan temuan impor tahun 2024**  `[no-sql]`
- **Tampilkan pemeriksaan sarana distribusi dengan klasifikasi importir pada tahun 2024**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(jenis_sarana) LIKE 'distribusi' AND klasifikasi LIKE '%Importir%' GROUP BY nama_sarana
  ```
- **tampilkan persentase hasil pemeriksaan mk terhadap total pada sarana importir di tahun 2025**
  ```sql
  SELECT CAST(SUM(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE 0 END) AS NUMERIC) * 100 / COUNT(*) AS percentage_mk FROM mv_pemeriksaan WHERE sarana = 'Importir' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **tampilkan proporsi klasifikasi sarana peredaran (ritel tradisional, ritel modern, distributor, importir) yang diperiksa di upt balai pom di batam pada tahun 2025.**  `[no-sql]`
- **Tolong buatkan query untuk: tampilkan negara-negara dengan temuan impor pada tahun 2025?**
  ```sql
  SELECT nama_sarana, tanggal_mulai, mpt.product_name, mpt.tp_negara, mpt.tp_kategori FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mpt.tp_negara) NOT LIKE '%indonesia%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025
  ```

### Nilai temuan (rupiah) — 31 pertanyaan

**SQL template warehouse (kanonik):**
```sql
SELECT round(sum(tp_harga_total)) FROM mv_pemeriksaan_temuan t
JOIN mv_pemeriksaan p ON p.id = t.id_pemeriksaan
WHERE tp_harga_total > 0 AND tp_harga_total < 1000000000
  AND p.tanggal_mulai >= '2023-01-01' AND p.tanggal_mulai < '2024-01-01';
```
*WAJIB filter outlier (tp_harga_total < 1 M). Tanpa filter = Rp 7,74T tercemar INFALGIN.*

- **"tampilkan jumlah nilai temuan produk sarana distribusi pada tahun 2023 dalam rupiah?"**
  ```sql
  SELECT SUM( CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE 0 END ) AS jumlah_temuan_rupiah FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) = 2023 AND jenis_sarana = 'Distribusi';
  ```
- **"tampilkan jumlah nilai temuan produk sarana distribusi pada tahun 2023?"**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2023 AND jenis_sarana = 'Distribusi' AND kesimpulan = 'TMK';
  ```
- **berapa data yang memiliki nilai major**
  ```sql
  SELECT COUNT(*) FROM public.mv_pemeriksaan_temuan WHERE lower(product_brands) LIKE '%major%';
  ```
- **berapa data yang memiliki nilai mayor**  `[no-sql]`
- **berapa total nilai temuan tahun 2025**
  ```sql
  SELECT SUM(nilai_temuan) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025
  ```
- **Pertanyaan:  Jumlah temuan produk dan nilai temuannya dikategorikan berdasarkan Bahan Berbahaya, TIE, Kedaluarsa, dll**
  ```sql
  select komoditi, mpt.tp_kategori, count(*), sum(mpt.tp_harga_total) from mv_pemeriksaan mp join mv_pemeriksaan_temuan mpt on mp.id = mpt.id_pemeriksaan where mp.klasifikasi_distribusi is not null group by 1, 2
  ```
- **Pertanyaan:  tampilkan jumlah nilai temuan produk sarana distribusi pada tahun 2025?**
  ```sql
  SELECT mp.komoditi, mpt.tp_kategori, sum(mpt.tp_harga_total) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(nama_sarana) LIKE '%distribusi%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2;
  ```
- **Pertanyaan:  tampilkan total temuan produk dan total nilai temuan pada kategori kedaluarsa.**
  ```sql
  SELECT tp_kategori, SUM(tp_jml_temuan) AS total_temuan_produk, SUM(tp_harga_total) AS total_nilai_temuan FROM mv_pemeriksaan_temuan WHERE LOWER(tp_kategori) LIKE '%kedaluarsa%' GROUP BY 1;
  ```
- **tampilkan harga temuan produk yang kedaluarsa tahun 2024**
  ```sql
  SELECT harga_temuan FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(komoditi) LIKE '%kedaluarsa%'
  ```
- **tampilkan jumlah nilai ekonomi temuan CV Anare Kemilau Indonesia tahun 2025**  `[no-sql]`
- **tampilkan jumlah nilai temuan CV Anare Kemilau Indonesia tahun 2025**
  ```sql
  SELECT COUNT(*) FROM public.vw_temuan_bpom WHERE lower(nama_perusahaan) LIKE '%anare kemilau indonesia%' AND EXTRACT(YEAR FROM tanggal) = 2025
  ```
- **tampilkan jumlah nilai temuan produk CV Anare Kemilau Indonesia tahun 2025**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND nama_sarana = 'CV Anare Kemilau Indonesia' AND lower(jenis_sarana) like 'produksi'
  ```
- **Tampilkan jumlah nilai temuan produk sarana distribusi pada tahun 2024**
  ```sql
  SELECT COUNT(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(jenis_sarana) = 'produksi'
  ```
- **tampilkan jumlah nilai temuan produk sarana distribusi pada tahun 2025 dalam rupiah?**
  ```sql
  SELECT SUM(t2.tp_harga_total) FROM mv_pemeriksaan AS t1 INNER JOIN mv_pemeriksaan_temuan AS t2 ON t1.id = t2.id_pemeriksaan WHERE t1.jenis_sarana ILIKE '%distribusi%' AND EXTRACT(YEAR FROM t1.tanggal_mulai) = 2025;
  ```
- **Tampilkan jumlah nilai temuan produk sarana distribusi pada tahun 2025?**
  ```sql
  SELECT kesimpulan, COUNT(nama_sarana) FROM public.vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY kesimpulan;
  ```
- **Tampilkan jumlah temuan produk dan harga total temuan produk untuk sarana distribusi kosmetik tahun 2024-2025**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(jenis_sarana) = 'distribusi';
  ```
- **tampilkan total nilai keekonomian produk tmk (tie, rusak kedaluwarsa) di balai pom di batam pada tahun 2025.**  `[no-sql]`
- **tampilkan total temuan produk dan total nilai temuan pada kategori 'lainnya'.**
  ```sql
  SELECT COUNT(CASE WHEN komoditi = 'lainnya' THEN id END) AS total_temuan_produk, COUNT(CASE WHEN komoditi = 'lainnya' THEN id END) AS total_nilai_temuan FROM public.vw_pemeriksaan_bcc WHERE komoditi = 'lainnya';
  ```
- **Tampilkan total temuan produk dan total nilai temuan pada kategori Bahan Berbahaya**  `[no-sql]`
- **Tampilkan total temuan produk dan total nilai temuan pada kategori Bahan Berbahaya tahun 2024**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(komoditi) LIKE '%bahan berbahaya%';
  ```
- **tampilkan total temuan produk dan total nilai temuan pada kategori bahan berbahaya.**
  ```sql
  SELECT COUNT(CASE WHEN komoditi = 'Bahan Berbahaya' THEN 1 END) AS total_temuan_produk, SUM(CASE WHEN komoditi = 'Bahan Berbahaya' THEN 1 ELSE 0 END) AS total_nilai_temuan FROM public.vw_pemeriksaan_bcc WHERE komoditi = 'Bahan Berbahaya';
  ```
- **Tampilkan total temuan produk dan total nilai temuan pada kategori Kadaluarsa**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE lower(komoditi) LIKE '%kadaluarsa%'
  ```
- **tampilkan total temuan produk dan total nilai temuan pada kategori kedaluarsa.**
  ```sql
  SELECT COUNT(CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE NULL END) AS total_temuan_produk, SUM(CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE 0 END) AS total_nilai_temuan FROM public.vw_pemeriksaan_bcc;
  ```
- **Tampilkan total temuan produk dan total nilai temuan pada kategori Lainnya**  `[no-sql]`
- **tampilkan total temuan produk dan total nilai temuan pada kategori lainnya.**
  ```sql
  SELECT COUNT(CASE WHEN komoditi = 'Obat' THEN id END) AS total_temuan_obat, COUNT(CASE WHEN komoditi != 'Obat' THEN id END) AS total_temuan_lainnya, SUM(CASE WHEN komoditi = 'Obat' THEN 1 ELSE 0 END) AS nilai_temuan_obat, SUM(CASE WHEN komoditi != 'Obat' THEN 1 ELSE 0 END) AS nilai_temuan_lainnya FROM public.vw_pemeriksaan_bcc WHERE kesimpulan = 'TMK';
  ```
- **Tolong buatkan query untuk: tampilkan jumlah nilai temuan produk sarana distribusi pada tahun 2025?**
  ```sql
  SELECT mp.komoditi, mpt.tp_kategori, sum(mpt.tp_harga_total) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(nama_sarana) LIKE '%distribusi%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2;
  ```
- **Tolong buatkan query untuk: tampilkan total nilai keekonomian produk tmk tie, rusak kedaluwarsa di balai pom di batam pada tahun 2025.**
  ```sql
  SELECT mpt.tp_kategori, sum(mpt.tp_harga_total) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%pom di batam%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY 1;
  ```
- **Tolong buatkan query untuk: tampilkan total temuan produk dan total nilai temuan pada kategori 'lainnya'.**
  ```sql
  SELECT tp_kategori, SUM(tp_jml_temuan) AS total_temuan_produk, SUM(tp_harga_total) AS total_nilai_temuan FROM mv_pemeriksaan_temuan WHERE LOWER(tp_kategori) LIKE '%lain - lain%' GROUP BY 1;
  ```
- **Tolong buatkan query untuk: tampilkan total temuan produk dan total nilai temuan pada kategori bahan berbahaya.**
  ```sql
  SELECT tp_kategori, SUM(tp_jml_temuan) AS total_temuan_produk, SUM(tp_harga_total) AS total_nilai_temuan FROM mv_pemeriksaan_temuan WHERE LOWER(tp_kategori) LIKE '%bahan berbahaya%' GROUP BY 1;
  ```
- **Tolong buatkan query untuk: tampilkan total temuan produk dan total nilai temuan pada kategori kedaluarsa.**
  ```sql
  SELECT tp_kategori, SUM(tp_jml_temuan) AS total_temuan_produk, SUM(tp_harga_total) AS total_nilai_temuan FROM mv_pemeriksaan_temuan WHERE LOWER(tp_kategori) LIKE '%kedaluarsa%' GROUP BY 1;
  ```
- **Tolong buatkan query untuk: tampilkan total temuan produk dan total nilai temuan pada kategori lainnya.**
  ```sql
  SELECT tp_kategori, SUM(tp_jml_temuan) AS total_temuan_produk, SUM(tp_harga_total) AS total_nilai_temuan FROM mv_pemeriksaan_temuan WHERE LOWER(tp_kategori) LIKE '%lain - lain%' GROUP BY 1;
  ```

### Temuan produk — 81 pertanyaan

**SQL template warehouse (kanonik):**
```sql
SELECT tp_kategori, COUNT(*) AS jml_temuan
FROM mv_pemeriksaan_temuan t
JOIN mv_pemeriksaan p ON p.id = t.id_pemeriksaan
WHERE p.tanggal_mulai >= '2023-01-01' AND p.tanggal_mulai < '2024-01-01'
GROUP BY 1 ORDER BY 2 DESC;
```
*Temuan = COUNT(*) di tabel temuan (1 baris = 1 produk).*

- **"apa temuan/ketidaksesuaian yang paling banyak ditemukan dari hasil pemeriksaan sarana produksi md?"**
  ```sql
  -- Tidak ada informasi tentang "temuan/ketidaksesuaian" di tabel. -- Pertanyaan ini tidak dapat dijawab hanya dengan informasi yang tersedia. -- Menampilkan jumlah pemeriksaan sarana produksi. SELECT COUNT(*) AS jumlah_pemeriksaan_sarana_produksi FROM public.vw_pemeriksaan_bcc WHERE jenis_sarana = 'Produksi';
  ```
- **"apa temuan/ketidaksesuaian yang paling banyak ditemukan pada seluruh sarana produksi tmk di wilayah kerja balai pom di payakumbuh?"**
  ```sql
  SELECT temuan FROM ( SELECT 'Tidak Memenuhi Ketentuan' AS temuan, COUNT(CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE NULL END) AS jumlah FROM public.vw_pemeriksaan_bcc WHERE nama_balai LIKE '%Payakumbuh%' AND jenis_sarana LIKE '%Produksi%' UNION ALL SELECT 'Tidak Dapat Diperiksa' AS temuan, COUNT(CASE WHEN kesimpulan = 'TDP' THEN 1 ELSE NULL END) AS jumlah FROM public.vw_pemeriksaan_bcc WHERE nama_balai LIKE '%Payakumbuh%' AND jenis_sarana LIKE '%Produksi%' UNION ALL SELECT 'Tutup' AS temuan, COUNT(CASE WHEN kesimpulan = 'TTP' THEN 1 ELSE NULL END) AS jumlah FROM public.vw_pemeriksaan_bcc WHERE nama_balai LIKE '%Payakumbuh%' AND jenis_sarana LIKE '%Produksi%' ) AS subquery ORDER BY jumlah DESC LIMIT 1;
  ```
- **"kepatuhan pemenuhan timeline penyelesaian laporan inspeksi, dengan analisis korelasi timeline dengan tingkat kompleksitas temuan (kategori temuan)."**  `[no-sql]`
- **"sarana distribusi apa saja yang pernah memiliki riwayat memenuhi ketentuan berdasarkan tahun temuannya?"**
  ```sql
  SELECT nama_sarana, MIN(EXTRACT(YEAR FROM tgl_start)) AS tahun_temuan FROM public.vw_pemeriksaan_bcc WHERE kesimpulan = 'MK' AND jenis_sarana = 'Distribusi' GROUP BY nama_sarana ORDER BY tahun_temuan;
  ```
- **"sarana distribusi apa saja yang pernah memiliki riwayat tidak memenuhi ketentuan berdasarkan tahun temuannya?"**
  ```sql
  SELECT nama_sarana, tgl_start FROM public.vw_pemeriksaan_bcc WHERE kesimpulan = 'TMK' AND jenis_sarana = 'Distribusi' GROUP BY nama_sarana, tgl_start;
  ```
- **"tampilkan merek-merek temuan produk obat tradisional; suplemen kesehatan; obat kuasi pada pemeriksaan tahun 2023?"**
  ```sql
  SELECT DISTINCT nama_sarana FROM vw_pemeriksaan_bcc WHERE komoditi IN ('OBAT TRADISIONAL', 'SUPLEMEN KESEHATAN', 'OBAT') AND EXTRACT(YEAR FROM tgl_start) = 2023;
  ```
- **"tampilkan profil temuan ketidaksesuaian berdasarkan hasil pemeriksaan pada tahun 2023".**
  ```sql
  SELECT nama_sarana, COUNT(id) AS jumlah_temuan FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) = 2023 AND kesimpulan = 'TMK' GROUP BY nama_sarana ORDER BY jumlah_temuan DESC;
  ```
- **"tampilkan temuan ketidaksesuaian untuk klausul (nomor klausul) di upt (nama upt)."**  `[no-sql]`
- **apa rincian temuan pemeriksaan CV Sinar Intan Raya 2025**
  ```sql
  SELECT nama_sarana, lower(jenis_sarana), lower(komoditi), tujuan, kesimpulan, count(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND LOWER(nama_sarana) LIKE '%sinar intan raya%' GROUP BY nama_sarana , lower(jenis_sarana) , lower(komoditi) , tujuan , kesimpulan
  ```
- **apa temuan/ketidaksesuaian yang paling banyak ditemukan dari hasil pemeriksaan sarana produksi md?**
  ```sql
  SELECT t2.tp_pelanggaran, COUNT(t2.tp_pelanggaran) AS jumlah_temuan FROM mv_pemeriksaan AS t1 INNER JOIN mv_pemeriksaan_temuan AS t2 ON t1.id = t2.id_pemeriksaan WHERE LOWER(t1.jenis_sarana) LIKE '%produksi%' AND LOWER(t1.nama_sarana) LIKE '%md%' GROUP BY t2.tp_pelanggaran ORDER BY jumlah_temuan DESC LIMIT 1;
  ```
- **apa temuan/ketidaksesuaian yang paling banyak ditemukan pada seluruh sarana produksi tmk di wilayah kerja balai pom di payakumbuh?**
  ```sql
  SELECT t2.tp_pelanggaran FROM mv_pemeriksaan AS t1 INNER JOIN mv_pemeriksaan_temuan AS t2 ON t1.id = t2.id_pemeriksaan WHERE t1.jenis_sarana ILIKE '%produksi%' AND t1.kesimpulan = 'TMK' AND t1.kabupaten ILIKE '%payakumbuh%' GROUP BY t2.tp_pelanggaran ORDER BY COUNT(t2.tp_pelanggaran) DESC LIMIT 1;
  ```
- **bagaimana detil temuan hasil pemeriksaan sarana Alfa Viva Famili tahun 2025**
  ```sql
  SELECT nama_sarana, lower(jenis_sarana), lower(komoditi), tujuan, kesimpulan, count(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND LOWER(nama_sarana) LIKE '%alfa viva famili%' GROUP BY nama_sarana , lower(jenis_sarana) , lower(komoditi) , tujuan , kesimpulan
  ```
- **Bagaimana perbandingan jumlah temuan MK dan TMK pada bulan Juli 2025?**
  ```sql
  SELECT SUM(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE 0 END) AS jumlah_mk, SUM(CASE WHEN kesimpulan != 'MK' THEN 1 ELSE 0 END) AS jumlah_tmk FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) = 2025 AND EXTRACT( MONTH FROM tgl_start ) = 7;
  ```
- **berapa jumlah temuan hasil pemeriksaan PT Alfa Viva Famili tahun 2025?**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND LOWER(nama_sarana) LIKE '%alfa viva famili%'
  ```
- **Daftar semua ketidaksesuaian dari pemeriksaan sarana produksi MD.**
  ```sql
  SELECT mpt.tp_kategori FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(jenis_sarana) LIKE '%pangan md%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1 ORDER BY count(*) DESC;
  ```
- **Daftar semua temuan dari pemeriksaan sarana produksi MD.**
  ```sql
  SELECT mpt.tp_kategori FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(jenis_sarana) LIKE '%pangan md%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1
  ```
- **Hitung jumlah masing-masing jenis temuan dan ketidaksesuaian yang ditemukan pada pemeriksaan sarana produksi MD.**
  ```sql
  SELECT jenis_sarana, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(jenis_sarana) LIKE '%pangan md%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2 ORDER BY 3 DESC;
  ```
- **kepatuhan pemenuhan timeline penyelesaian laporan inspeksi, dengan analisis korelasi timeline dengan tingkat kompleksitas temuan (kategori temuan).**  `[no-sql]`
- **menganalisis temuan berulang dari suatu sarana pada semua pemeriksaan yang tercatat.**
  ```sql
  SELECT nama_sarana, COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc GROUP BY nama_sarana HAVING COUNT(*) > 1 ORDER BY jumlah_pemeriksaan DESC;
  ```
- **Pertanyaan:  apa temuan/ketidaksesuaian yang paling banyak ditemukan dari hasil pemeriksaan sarana produksi md?**
  ```sql
  SELECT jenis_sarana, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(jenis_sarana) LIKE '%pangan md%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2 ORDER BY 3 DESC;
  ```
- **Pertanyaan:  apa temuan/ketidaksesuaian yang paling banyak ditemukan pada seluruh sarana distribusi tmk di wilayah kerja balai pom di payakumbuh?**
  ```sql
  SELECT kabupaten_kota, mp.sarana, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(kabupaten_kota) LIKE '%payakumbuh%' AND lower(mp.sarana) LIKE '%distribusi%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3 ORDER BY 4 DESC;
  ```
- **Pertanyaan:  Buatkan analisa temuan produk TIE Kosmetik di Balai Besar POM di Bandar Lampung**
  ```sql
  SELECT mp.nama_upt, tanggal_mulai, nama_sarana, jenis_sarana, mpt.product_name, mpt.tp_kategori FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(nama_upt) LIKE '%bandar lampung%' AND lower(komoditi) LIKE '%kosmetik%' AND mpt.tp_kategori LIKE '%TIE%' ORDER BY 1, 2, 3, 4;
  ```
- **Pertanyaan:  Tampilkan data temuan obat TIE/ilegal/palsu masing-masing UPT pada tahun 2024**
  ```sql
  SELECT mp.nama_upt, COUNT(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT( YEAR FROM tanggal_mulai ) = 2024 AND ( lower(mpt.tp_kategori) LIKE '%tie%' OR lower(mpt.tp_kategori) LIKE '%ilegal%' OR lower(mpt.tp_kategori) LIKE '%palsu%' ) GROUP BY mp.nama_upt;
  ```
- **Pertanyaan:  tampilkan jumlah temuan produk sarana distribusi pada tahun 2025?**
  ```sql
  SELECT mp.komoditi, mpt.tp_kategori, sum(mpt.tp_jml_temuan) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(nama_sarana) LIKE '%distribusi%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2;
  ```
- **Pertanyaan:  Tampilkan negara temuan produk pada sarana distribusi kosmetik tahun 2024**
  ```sql
  SELECT DISTINCT mpt.tp_negara FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND lower(mp.komoditi) LIKE '%kosmetik%' AND lower(mp.sarana) LIKE '%distribusi%' AND mp.status IN ('VERIFY4', 'VERIFY5', 'VERIFY6', 'VERIFY7', 'FINISHED') AND lower(mpt.tp_negara) NOT LIKE '%indonesia%';
  ```
- **Pertanyaan:  Tampilkan temuan produk berdasarkan kategori sarana distribusi?**  `[no-sql]`
- **Pertanyaan:  tampilkan tiga temuan kritis paling sering ditemui pada Balai Besar POM di DKI Jakarta tahun 2024**
  ```sql
  select mp.nama_upt, mp.tx_critical_issue, count(*) from mv_pemeriksaan mp where mp.tx_critical_issue is not null and lower(mp.nama_upt) like '%jakarta%' and extract(year from mp.tanggal_input) = 2024 group by 1, 2 order by count(*) desc limit 3
  ```
- **Pertanyaan:  temuan produk berdasarkan kategori sarana distribusi**
  ```sql
  select klasifikasi_distribusi, komoditi, mpt.tp_kategori, count(*), sum(mpt.tp_harga_total) from mv_pemeriksaan mp join mv_pemeriksaan_temuan mpt on mp.id = mpt.id_pemeriksaan where mp.klasifikasi_distribusi is not null group by 1, 2, 3
  ```
- **sarana distribusi apa saja yang pernah memiliki riwayat memenuhi ketentuan berdasarkan tahun temuannya?**
  ```sql
  SELECT nama_sarana, sarana, EXTRACT(YEAR FROM tanggal_mulai) AS tahun_temuan FROM mv_pemeriksaan WHERE lower(sarana) = 'distribusi' AND kesimpulan = 'MK' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ORDER BY 1, 2;
  ```
- **sarana distribusi apa saja yang pernah memiliki riwayat tidak memenuhi ketentuan berdasarkan tahun temuannya?**
  ```sql
  SELECT nama_sarana, sarana, EXTRACT(YEAR FROM tanggal_mulai) AS tahun_temuan FROM mv_pemeriksaan WHERE lower(sarana) = 'distribusi' AND kesimpulan = 'TMK' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ORDER BY 1, 2;
  ```
- **sebutkan 10 sarana produksi kosmetik yang Memenuhi Ketentuan pada tahun 2025 dan sebutkan kategori temuannya**
  ```sql
  SELECT nama_sarana, kesimpulan FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(jenis_sarana) LIKE '%produksi%' AND kesimpulan = 'MK' LIMIT 10;
  ```
- **sebutkan 10 sarana produksi kosmetik yang Tidak Memenuhi Ketentuan pada tahun 2025 dan sebutkan kategori temuannya**
  ```sql
  SELECT nama_sarana, tujuan FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(jenis_sarana) LIKE '%produksi%' AND kesimpulan = 'TMK' LIMIT 10;
  ```
- **tampilan jenis observasi dan temuan yang terkait dengan tag yang tersedia dengan kata kunci tertentu.**
  ```sql
  SELECT jenis_sarana, COUNT(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE NULL END) AS memenuhi_ketentuan, COUNT(CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE NULL END) AS tidak_memenuhi_ketentuan, COUNT(CASE WHEN kesimpulan = 'TDP' THEN 1 ELSE NULL END) AS tidak_dapat_diperiksa, COUNT(CASE WHEN kesimpulan = 'TTP' THEN 1 ELSE NULL END) AS tutup FROM public.vw_pemeriksaan_bcc GROUP BY jenis_sarana;
  ```
- **tampilkan aspek temuan yang berulang dari tahun ke tahun pada sarana dengan nama 'sarana x'.**
  ```sql
  SELECT nama_sarana, COUNT(*) AS jumlah_temuan FROM public.vw_pemeriksaan_bcc WHERE nama_sarana LIKE '%sarana x%' GROUP BY nama_sarana HAVING COUNT(*) > 1;
  ```
- **tampilkan aspek temuan yang berulang dari tahun ke tahun pada sarana dengan nama siloam.**
  ```sql
  SELECT mt.tp_kategori FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_temuan AS mt ON mp.id = mt.id_pemeriksaan WHERE mp.nama_sarana ILIKE '%siloam%' GROUP BY mt.tp_kategori HAVING COUNT(DISTINCT EXTRACT(YEAR FROM mp.tanggal_mulai)) > 1;
  ```
- **Tampilkan data kepatuhan SOP atau data kontrol kualitas yang menunjukkan ketidaksesuaian proses di sarana produksi alat kesehatan.**
  ```sql
  SELECT mpt.tp_kategori, mpt.tp_pelanggaran, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.jenis_sarana) LIKE '%produksi%' AND mp.kesimpulan = 'TMK' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND mpt.tp_kategori IS NOT NULL AND mpt.tp_pelanggaran IS NOT NULL GROUP BY 1, 2 ORDER BY 3 DESC;
  ```
- **tampilkan data temuan obat tie/ilegal/palsu masing-masing upt pada tahun 2023.**
  ```sql
  SELECT nama_balai, COUNT(CASE WHEN kesimpulan = 'TMK' THEN 1 END) AS jumlah_obat_ilegal_palsu FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2023 AND komoditi = 'Obat' GROUP BY nama_balai ORDER BY nama_balai;
  ```
- **Tampilkan data temuan obat TIE/ilegal/palsu masing-masing UPT pada tahun 2024**
  ```sql
  SELECT nama_balai, COUNT(*) AS jumlah_temuan FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(tujuan) LIKE '%ilegal%' GROUP BY nama_balai ORDER BY nama_balai;
  ```
- **tampilkan data temuan obat tie/ilegal/palsu masing-masing upt pada tahun 2025.**
  ```sql
  SELECT m.nama_upt, COUNT(mt.id_pemeriksaan) AS jumlah_temuan FROM public.mv_pemeriksaan_temuan AS mt JOIN public.mv_pemeriksaan AS m ON mt.id_pemeriksaan = m.id WHERE ( mt.tp_kategori ILIKE '%ilegal%' OR mt.tp_kategori ILIKE '%tie%' OR mt.tp_kategori ILIKE '%palsu%' ) AND EXTRACT(YEAR FROM m.tanggal_mulai) = 2025 GROUP BY m.nama_upt ORDER BY m.nama_upt;
  ```
- **Tampilkan jumlah insiden atau pelanggaran yang dilaporkan untuk sarana dari Januari hingga September 2025.**
  ```sql
  SELECT COUNT(mpt.id_pemeriksaan) FROM public.mv_pemeriksaan_temuan mpt JOIN public.mv_pemeriksaan mp ON mpt.id_pemeriksaan = mp.id WHERE EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM mp.tanggal_mulai) BETWEEN 1 AND 9;
  ```
- **Tampilkan jumlah temuan di sarana dengan nama 'Siloam' berdasarkan departemen dan tahun.**
  ```sql
  SELECT mp.departemen, EXTRACT(YEAR FROM tanggal_mulai) AS tahun, count(*) FROM public.mv_pemeriksaan mp WHERE lower(nama_sarana) LIKE '%siloam%' GROUP BY 1, 2;
  ```
- **Tampilkan jumlah temuan di sarana dengan nama 'Siloam' berdasarkan peralatan medis dan tahun.**
  ```sql
  SELECT mp.nama_sarana, mp.sarana, mpt.tp_kategori, EXTRACT(YEAR FROM tanggal_mulai) AS tahun, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(nama_sarana) LIKE '%siloam%' GROUP BY 1, 2, 3, 4;
  ```
- **tampilkan jumlah temuan produk sarana Alfa Viva Famili tahun 2025**
  ```sql
  SELECT count(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND LOWER(nama_sarana) LIKE '%alfa viva famili%'
  ```
- **tampilkan jumlah temuan produk sarana distribusi pada tahun 2023?**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2023 AND jenis_sarana = 'Distribusi';
  ```
- **Tampilkan jumlah temuan produk sarana distribusi pada tahun 2024**
  ```sql
  SELECT COUNT(nama_sarana) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(jenis_sarana) LIKE 'distribusi'
  ```
- **Tampilkan jumlah temuan produk sarana distribusi pada tahun 2024?**
  ```sql
  SELECT COUNT(*) FROM public.vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND EXTRACT(YEAR FROM tgl_start) = 2024;
  ```
- **tampilkan jumlah temuan produk sarana distribusi pada tahun 2025?**
  ```sql
  SELECT SUM(t1.tp_jml_temuan) FROM mv_pemeriksaan_temuan AS t1 INNER JOIN mv_pemeriksaan AS t2 ON t1.id_pemeriksaan = t2.id WHERE t2.jenis_sarana ILIKE '%distribusi%' AND EXTRACT(YEAR FROM t2.tanggal_mulai) = 2025;
  ```
- **tampilkan jumlah temuan produk tmk (tie, rusak, kedaluwarsa) pada sarana peredaran per wilayah kerja masing-masing upt.**  `[no-sql]`
- **Tampilkan merek-merek temuan produk kosmetik pada pemeriksaan tahun 2024?**
  ```sql
  SELECT DISTINCT merek FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024;
  ```
- **Tampilkan merek-merek temuan produk kosmetik pada pemeriksaan tahun 2025?**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025;
  ```
- **tampilkan merek-merek temuan produk obat tradisional; suplemen kesehatan; obat kuasi pada pemeriksaan tahun 2025?**
  ```sql
  SELECT DISTINCT t2.product_brands FROM public.mv_pemeriksaan AS t1 INNER JOIN public.mv_pemeriksaan_temuan AS t2 ON t1.id = t2.id_pemeriksaan WHERE LOWER(t1.komoditi) LIKE '%obat tradisional%' OR LOWER(t1.komoditi) LIKE '%suplemen kesehatan%' AND EXTRACT(YEAR FROM t1.tanggal_mulai) = 2025;
  ```
- **Tampilkan negara temuan produk pada sarana distribusi kosmetik tahun 2024**
  ```sql
  SELECT negara_temuan_produk FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(jenis_sarana) LIKE '%distribusi%' GROUP BY negara_temuan_produk;
  ```
- **Tampilkan negara-negara sumber temuan produk tahun 2024**  `[no-sql]`
- **tampilkan profil temuan ketidaksesuaian berdasarkan hasil pemeriksaan pada tahun 2025.**
  ```sql
  SELECT mt.tp_kategori, COUNT(mt.id_pemeriksaan) AS jumlah_temuan FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_temuan AS mt ON mp.id = mt.id_pemeriksaan WHERE EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND mp.kesimpulan = 'TMK' AND mt.tp_kategori IS NOT NULL GROUP BY mt.tp_kategori ORDER BY jumlah_temuan DESC;
  ```
- **Tampilkan semua temuan yang tercatat di sarana dengan nama 'Siloam' beserta tahun terjadinya.**
  ```sql
  SELECT mp.nama_sarana, mpt.temuan, EXTRACT(YEAR FROM tanggal_mulai) AS tahun FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.nama_sarana) LIKE '%siloam%';
  ```
- **Tampilkan temuan atau ketidaksesuaian dari laporan audit atau inspeksi sarana produksi alat kesehatan.**
  ```sql
  SELECT mp.nama_sarana, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.jenis_sarana) LIKE '%produksi%' AND lower(mp.komoditi) LIKE '%alat kesehatan%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2 ORDER BY 3 DESC;
  ```
- **Tampilkan temuan bahan berbahaya tahun 2024**
  ```sql
  SELECT komoditi, COUNT(*) AS jumlah FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(komoditi) LIKE '%bahan berbahaya%' GROUP BY komoditi ORDER BY jumlah DESC LIMIT 3;
  ```
- **Tampilkan temuan hasil pemeriksaan pada aspek pencatatan dan pelaporan di tahun 2023 berdasarkan fasilitas.**  `[no-sql]`
- **Tampilkan temuan hasil pemeriksaan pada aspek pencatatan dan pelaporan di tahun 2023 berdasarkan kesimpulan pemeriksaan.**
  ```sql
  SELECT kesimpulan, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2023 AND lower(aspek_penilaian) LIKE '%pencatatan dan pelaporan%' GROUP BY kesimpulan
  ```
- **tampilkan temuan ketidaksesuaian untuk klausul untuk upt balai besar pom di bandung.**
  ```sql
  SELECT t2.tp_pelanggaran FROM public.mv_pemeriksaan AS t1 INNER JOIN public.mv_pemeriksaan_temuan AS t2 ON t1.id = t2.id_pemeriksaan WHERE t1.nama_upt ILIKE '%balai besar pom di bandung%' AND t2.tp_pelanggaran IS NOT NULL;
  ```
- **Tampilkan temuan produk berdasarkan kategori sarana distribusi**
  ```sql
  SELECT komoditi, kesimpulan FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE '%distribusi%' GROUP BY komoditi, kesimpulan;
  ```
- **Tampilkan temuan produk berdasarkan kategori sarana distribusi?**
  ```sql
  SELECT kesimpulan FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE '%distribusi%' GROUP BY kesimpulan
  ```
- **Tampilkan temuan produk kosmetik di tahun 2025 berdasarkan kemajuan teknologi.**
  ```sql
  SELECT mpt.product_brands, mp.komoditi, mpt.tp_kategori FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND LOWER(komoditi) LIKE '%kosmetik%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED');
  ```
- **Tampilkan temuan produk kosmetik di tahun 2025 berdasarkan perubahan regulasi.**
  ```sql
  SELECT mpt.product_brands, mp.komoditi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND LOWER(komoditi) LIKE '%kosmetik%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3;
  ```
- **Tampilkan temuan produk untuk PT Niaga Warna Persada**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE LOWER(nama_sarana) LIKE '%niaga warna persada%' AND lower(jenis_sarana) LIKE '%produksi%'
  ```
- **Tampilkan temuan/ketidaksesuaian pada sarana distribusi TMK di Balai POM Payakumbuh berdasarkan laporan audit atau pemeriksaan kualitas.**
  ```sql
  SELECT mp.nama_sarana, mpt.tp_kategori, COUNT(mpt.tp_kategori) AS jumlah_temuan FROM public.mv_pemeriksaan mp LEFT JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.kabupaten) LIKE '%payakumbuh%' AND lower(mp.sarana) LIKE '%distribusi%' AND lower(mp.kesimpulan) = 'tmk' GROUP BY mp.nama_sarana, mpt.tp_kategori ORDER BY jumlah_temuan DESC;
  ```
- **Tampilkan temuan/ketidaksesuaian pada sarana distribusi TMK di Balai POM Payakumbuh berdasarkan metrik operasional.**
  ```sql
  SELECT mp.kabupaten_kota, mp.nama_sarana, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.kabupaten_kota) LIKE '%payakumbuh%' AND lower(mp.nama_sarana) LIKE '%distribusi%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3 ORDER BY 4 DESC;
  ```
- **Tampilkan temuan/ketidaksesuaian paling banyak ditemukan pada sarana distribusi TMK di Balai POM Payakumbuh.**
  ```sql
  SELECT mp.nama_sarana, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.kabupaten) LIKE '%payakumbuh%' AND lower(mp.sarana) LIKE '%distribusi%' AND mp.kesimpulan = 'TMK' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2 ORDER BY 3 DESC;
  ```
- **tampilkan tiga temuan kritis paling sering ditemui beserta jumlah masing-masing temuannya pada balai besar pom di dki jakarta tahun 2024.**
  ```sql
  SELECT kesimpulan, COUNT(*) AS jumlah FROM public.vw_pemeriksaan_bcc WHERE nama_balai = 'BALAI BESAR POM DI JAKARTA' AND EXTRACT(YEAR FROM tgl_start) = 2024 AND kesimpulan IS NOT NULL GROUP BY kesimpulan ORDER BY jumlah DESC LIMIT 3;
  ```
- **tampilkan tiga temuan/ketidaksesuaian paling sering ditemui di wilayah kerja bbpom di dki jakarta pada triwulan 1 tahun 2025.**
  ```sql
  SELECT t2.tp_kategori, COUNT(t2.tp_kategori) AS jumlah_temuan FROM public.mv_pemeriksaan AS t1 INNER JOIN public.mv_pemeriksaan_temuan AS t2 ON t1.id = t2.id_pemeriksaan WHERE t1.provinsi ILIKE '%dki jakarta%' AND t1.tanggal_mulai BETWEEN '2025-01-01' AND '2025-03-31' GROUP BY t2.tp_kategori ORDER BY jumlah_temuan DESC LIMIT 3;
  ```
- **tampilkan tiga temuan/ketidaksesuaian paling sering ditemui di wilayah kerja bbpom di dki jakarta pada triwulan i tahun 2025.**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE provinsi = 'DKI JAKARTA' AND tgl_start BETWEEN '2025-01-01' AND '2025-03-31' AND kesimpulan = 'TMK' GROUP BY nama_sarana ORDER BY count(*) DESC LIMIT 3;
  ```
- **tampilkan total temuan produk yang kedaluarsa tahun 2024**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024;
  ```
- **temuan produk berdasarkan kategori sarana distribusi**
  ```sql
  select klasifikasi_distribusi, komoditi, mpt.tp_kategori, count(*), sum(mpt.tp_harga_total) from mv_pemeriksaan mp join mv_pemeriksaan_temuan mpt on mp.id = mpt.id_pemeriksaan where mp.klasifikasi_distribusi is not null group by 1, 2, 3
  ```
- **Tolong buatkan query untuk: apa temuan/ketidaksesuaian yang paling banyak ditemukan dari hasil pemeriksaan sarana produksi md?**
  ```sql
  SELECT jenis_sarana, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(jenis_sarana) LIKE '%pangan md%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2 ORDER BY 3 DESC;
  ```
- **Tolong buatkan query untuk: apa temuan/ketidaksesuaian yang paling banyak ditemukan pada seluruh sarana distribusi tmk di wilayah kerja balai pom di payakumbuh?**
  ```sql
  SELECT kabupaten_kota, mp.nama_sarana, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(kabupaten_kota) LIKE '%payakumbuh%' AND lower(mp.sarana) LIKE '%distribusi%' AND lower(kesimpulan) = 'tmk' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3 ORDER BY 4 DESC;
  ```
- **Tolong buatkan query untuk: tampilkan jumlah temuan produk sarana distribusi pada tahun 2025?**
  ```sql
  SELECT mp.komoditi, mpt.tp_kategori, sum(mpt.tp_jml_temuan) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(mp.nama_sarana) LIKE '%distribusi%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2;
  ```
- **Tolong buatkan query untuk: tampilkan jumlah temuan produk tmk tie, rusak, kedaluwarsa pada sarana peredaran per wilayah kerja masing-masing upt.**
  ```sql
  SELECT mp.kabupaten_kota, mpt.tp_kategori, sum(mpt.tp_jml_temuan) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mpt.tp_kategori) LIKE '%tie%' OR lower(mpt.tp_kategori) LIKE '%rusak%' OR lower(mpt.tp_kategori) LIKE '%kedaluwarsa%' AND lower(kesimpulan) = 'tmk' AND lower(mp.sarana) LIKE '%peredaran%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1,2;
  ```
- **Tolong buatkan query untuk: tampilkan merek-merek temuan produk obat tradisional; suplemen kesehatan; obat kuasi pada pemeriksaan tahun 2025?**
  ```sql
  SELECT mpt.product_brands, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 GROUP BY 1 ORDER BY 2 DESC;
  ```
- **Tolong buatkan query untuk: tampilkan profil temuan ketidaksesuaian berdasarkan hasil pemeriksaan pada tahun 2025.**
  ```sql
  SELECT mpt.tp_kategori, count(*) AS jumlah_pemeriksaan, sum(mpt.tp_jml_temuan) AS jumlah_temuan, sum(mpt.tp_harga_total) AS nilai_temuan FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY 1;
  ```
- **Tolong buatkan query untuk: tampilkan temuan ketidaksesuaian untuk klausul untuk upt balai besar pom di bandung.**
  ```sql
  SELECT mpt.tp_kategori, count(*) AS jumlah_pemeriksaan, sum(mpt.tp_jml_temuan) AS jumlah_temuan, sum(mpt.tp_harga_total) AS nilai_temuan FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(kesimpulan) = 'tmk' AND lower(mp.nama_upt) LIKE '%pom di bandung%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1;
  ```
- **Tolong buatkan query untuk: tampilkan tiga temuan/ketidaksesuaian paling sering ditemui di wilayah kerja bbpom di dki jakarta pada triwulan 1 tahun 2025.**
  ```sql
  SELECT nama_upt, provinsi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(provinsi) LIKE '%dki jakarta%' AND mp.tanggal_mulai BETWEEN '2025-01-01' AND '2025-04-01' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3 ORDER BY count(*) DESC LIMIT 3;
  ```

### Filter sarana produksi/distribusi/pelayanan — 149 pertanyaan

**SQL template warehouse (kanonik):**
```sql
SELECT nama_sarana, COUNT(DISTINCT id)
FROM mv_pemeriksaan
WHERE sarana = 'PRODUKSI' AND komoditi = 'KOSMETIK'
  AND tanggal_mulai >= '2025-01-01' AND tanggal_mulai < '2026-01-01'
GROUP BY 1;
```
*sarana = PRODUKSI/DISTRIBUSI/PELAYANAN (3 nilai, UPPER).*

- **"analisis jumlah seluruh sarana produksi dan distribusi (tanpa pengulangan nama yang sama) per komoditi produk (obat/oba/sk/kos/po) yang telah diperiksa bpom dalam periode 2025**  `[no-sql]`
- **"dari seluruh upt, sarana produksi md dengan jenis pangan apa yang paling banyak tmk di tahun 2025?"**
  ```sql
  SELECT komoditi FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND jenis_sarana LIKE '%produksi%' AND kesimpulan = 'TMK' GROUP BY komoditi ORDER BY COUNT(*) DESC LIMIT 1;
  ```
- **"merekap jumlah dan nama sarana distribusi dan pelayanan yang belum pernah diperiksa dalam kurun waktu 1 tahun terakhir"**
  ```sql
  SELECT jenis_sarana, COUNT(nama_sarana) AS jumlah_sarana FROM public.vw_pemeriksaan_bcc WHERE tgl_start < NOW() - INTERVAL '1 year' GROUP BY jenis_sarana;
  ```
- **"sarana distribusi kosmetik apa saja yang pernah diperiksa oleh badan pom setiap tahun dari tahun 2020 hingga 2024?"**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, nama_sarana FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) BETWEEN 2020 AND 2024 AND LOWER(jenis_sarana) LIKE '%distribusi%' GROUP BY tahun, nama_sarana ORDER BY tahun, nama_sarana;
  ```
- **"sarana distribusi kosmetik apa saja yang pernah diperiksa oleh badan pom?"**
  ```sql
  SELECT DISTINCT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE jenis_sarana LIKE '%Distribusi%' AND komoditi LIKE '%Kosmetik%'
  ```
- **"sarana produksi kosmetik apa saja yang memiliki riwayat pemeriksaan tidak memenuhi ketentuan dalam periode tahun 2024?"**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND jenis_sarana ILIKE 'produksi' AND kesimpulan = 'TMK';
  ```
- **"sarana produksi kosmetik apa saja yang pernah memproduksi dan mengedarkan kosmetik tie dalam periode tahun 2022?"**
  ```sql
  SELECT DISTINCT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2022 AND jenis_sarana = 'Produksi' AND kesimpulan = 'TMK';
  ```
- **"sarana produksi kosmetik apa saja yang tutup dalam periode tahun 2023?"**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2023 AND kesimpulan = 'TTP' AND jenis_sarana = 'Produksi' GROUP BY nama_sarana;
  ```
- **"sarana produksi md apa yang paling sering memiliki riwayat tmk?"**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE jenis_sarana = 'Produksi' AND kesimpulan = 'TMK' GROUP BY nama_sarana ORDER BY COUNT(*) DESC LIMIT 1;
  ```
- **"tampilkan jumlah dan nama sarana distribusi dan pelayanan yang mk/tmk masing-masing upt pada tahun 2025."**
  ```sql
  SELECT nama_balai, SUM(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE 0 END) AS jumlah_mk, SUM(CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE 0 END) AS jumlah_tmk FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) = 2025 AND ( jenis_sarana = 'Distribusi' OR jenis_sarana = 'Pelayanan' ) GROUP BY nama_balai;
  ```
- **"tampilkan jumlah sarana produksi kategori mk dan tmk per komoditi, periode, wilayah, dan cakupan upt."**
  ```sql
  SELECT komoditi, EXTRACT( YEAR FROM tgl_start ) AS periode, provinsi, nama_balai, COUNT( CASE WHEN kesimpulan = 'MK' THEN id ELSE NULL END ) AS jumlah_mk, COUNT( CASE WHEN kesimpulan = 'TMK' THEN id ELSE NULL END ) AS jumlah_tmk FROM public.vw_pemeriksaan_bcc WHERE jenis_sarana = 'Produksi' GROUP BY komoditi, periode, provinsi, nama_balai;
  ```
- **"tampilkan sarana distribusi dan pelayanan yang tutup pada periode tahun 2025"**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND jenis_sarana = 'Distribusi' AND kesimpulan = 'TTP' UNION ALL SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND jenis_sarana = 'Pelayanan' AND kesimpulan = 'TTP';
  ```
- **"upt mana saja yang paling banyak melaporkan hasil pemeriksaan sarana produksi yang tmk?"**
  ```sql
  SELECT nama_balai FROM public.vw_pemeriksaan_bcc WHERE kesimpulan = 'TMK' AND jenis_sarana = 'Produksi' GROUP BY nama_balai ORDER BY COUNT(*) DESC LIMIT 1;
  ```
- **"upt manakah yang hasil pemeriksaan tmk sarana produksi md nya paling banyak di tahun 2025?"**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND kesimpulan = 'TMK' AND jenis_sarana = 'Produksi' GROUP BY nama_sarana ORDER BY COUNT(id) DESC LIMIT 1;
  ```
- **'Tolong buatkan query untuk: 'UPT manakah yang hasil pemeriksaan TMK sarana produksi MD nya paling banyak di tahun 2025?**
  ```sql
  SELECT nama_upt, jenis_sarana, count(*) FROM mv_pemeriksaan mp WHERE lower(jenis_sarana) LIKE '%pangan md%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND mp.kesimpulan = 'TMK' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2 ORDER BY 3 DESC;
  ```
- **ada berapa sarana distribusi yang tutup tahun 2024**
  ```sql
  SELECT count(nama_sarana) FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND EXTRACT(YEAR FROM tgl_end) = 2024 AND kesimpulan LIKE 'TTP'
  ```
- **ada berapa sarana produksi amdk dengan hasil pemeriksaan tmk di wilayah kerja balai pom di bogor pada tahun 2024?**
  ```sql
  SELECT COUNT(CASE WHEN vw_pemeriksaan_bcc.kesimpulan = 'TMK' THEN 1 ELSE NULL END) FROM public.vw_pemeriksaan_bcc WHERE vw_pemeriksaan_bcc.nama_balai = 'Balai POM di Bogor' AND EXTRACT( YEAR FROM vw_pemeriksaan_bcc.tgl_start ) = 2024 AND vw_pemeriksaan_bcc.jenis_sarana = 'Produksi';
  ```
- **ada berapa sarana produksi kosmetik yang Memenuhi Ketentuan pada tahun 2025**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(jenis_sarana) = 'produksi' AND kesimpulan = 'MK';
  ```
- **ada berapa sarana produksi kosmetik yang Tidak Memenuhi Ketentuan pada tahun 2025**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(jenis_sarana) = 'produksi' AND kesimpulan = 'TMK';
  ```
- **ada berapa total sarana produksi kosmetik?**
  ```sql
  SELECT count(DISTINCT nama_sarana) FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'produksi';
  ```
- **analisis jumlah seluruh sarana produksi dan distribusi (tanpa pengulangan nama yang sama) per komoditi produk (obat/oba/sk/kos/po) yang telah diperiksa bpom dalam periode 2025**  `[no-sql]`
- **Apakah hasil pemeriksaan sarana produksi mengalami kenaikan dalam hal sarana memenuhi ketentuan MK?**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, COUNT(*) AS jumlah_mk FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'produksi' AND kesimpulan = 'MK' GROUP BY tahun ORDER BY tahun;
  ```
- **berapa % sarana produksi pangan MD dengan hasil memenuhi ketentuan yang diperiksa dalam rangka pemeriksaan rutin oleh BBPOM Jakarta selama tahun 2025 ini?**
  ```sql
  SELECT CAST(SUM(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE 0 END) AS DECIMAL) * 100 / COUNT(*) AS percentage_mk FROM public.mv_pemeriksaan WHERE lower(sarana) LIKE '%produksi%' AND lower(jenis_sarana) LIKE '%pangan md%' AND lower(tujuan_pemeriksaan) LIKE '%pemeriksaan rutin%' AND lower(nama_upt) LIKE '%balai besar pom di jakarta%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Berapa jumlah pemeriksaan sarana produksi obat untuk yang memiliki durasi 2 hari?**
  ```sql
  SELECT COUNT(*) FROM public.vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE '%produksi%' AND tgl_end - tgl_start = 2;
  ```
- **Berapa jumlah pemeriksaan sarana produksi obat untuk yang memiliki durasi lebih dari 3 hari?**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE jenis_sarana = 'produksi' AND komoditi = 'OBAT' AND (tgl_end - tgl_start) > interval '3 days';
  ```
- **Berapa jumlah pemeriksaan sarana produksi pangan dalam rangka pemeriksaan rutin dibandingan dengan jumlah pemeriksaan sarana produksi pangan dalam rangka sertifikasi selama Januari hingga Juli 2025?**
  ```sql
  SELECT SUM(CASE WHEN LOWER(tujuan) LIKE '%rutin%' THEN 1 ELSE 0 END) AS jumlah_pemeriksaan_rutin, SUM(CASE WHEN LOWER(tujuan) LIKE '%sertifikasi%' THEN 1 ELSE 0 END) AS jumlah_pemeriksaan_sertifikasi FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) BETWEEN 1 AND 7 AND LOWER(jenis_sarana) LIKE '%produksi%';
  ```
- **berapa jumlah pemeriksaan sarana produksi pangan olahan yang diperiksa oleh Balai besar POM di Jakarta tahun 2024?**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(nama_balai) LIKE '%jakarta%' AND lower(jenis_sarana) LIKE '%produksi%';
  ```
- **Berapa jumlah sarana produksi pangan fortifikasi yang telah diperiksa selama Januari sampai Juli 2025?**
  ```sql
  SELECT count(*) AS jumlah_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) BETWEEN 1 AND 7 AND lower(jenis_sarana) LIKE '%produksi%'
  ```
- **berapa jumlah sarana produksi pangan olahan yang diperiksa oleh BBPOM Bandung di tahun 2024?**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(jenis_sarana) LIKE '%produksi%' AND lower(nama_balai) LIKE '%bbpom bandung%';
  ```
- **berapa sarana produksi pangan olahan yang diperiksa oleh BBPOM Jakarta pada februari 2025**
  ```sql
  SELECT count(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) = 2 AND lower(nama_balai) LIKE '%bbpom jakarta%' AND lower(jenis_sarana) LIKE '%produksi%'
  ```
- **Berapa total hasil pemeriksaan sarana distribusi pangan pada tahun 2025?**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(jenis_sarana) LIKE 'distribusi'
  ```
- **buatkan daftar 275 pemeriksaan sarana produksi obat yang memiliki durasi 2 hari.**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'produksi' AND day_start_end = 2 LIMIT 275;
  ```
- **buatkan daftar Terdapat 275 pemeriksaan sarana produksi obat yang memiliki durasi 2 hari.**
  ```sql
  SELECT COUNT(*) FROM public.vw_pemeriksaan_bcc WHERE jenis_sarana ILIKE 'produksi' AND komoditi ILIKE 'obat' AND AGE(tgl_end, tgl_start) = INTERVAL '2 days';
  ```
- **buatkan profil sarana peredaran paramex**
  ```sql
  SELECT * FROM public.mv_pemeriksaan WHERE jenis_sarana ILIKE '%distribusi%' AND (komoditi ILIKE '%paramex%' OR nama_sarana ILIKE '%paramex%');
  ```
- **Daftar sarana distribusi kosmetik yang diperiksa oleh Badan POM per tahun pemeriksaan.**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE '%distribusi%' AND lower(komoditi) LIKE '%kosmetik%' GROUP BY tahun, nama_sarana ORDER BY tahun, nama_sarana;
  ```
- **Daftar semua sarana distribusi kosmetik yang diperiksa oleh Badan POM.**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND lower(komoditi) LIKE 'kosmetik' GROUP BY nama_sarana;
  ```
- **dari seluruh upt, sarana produksi md dengan jenis pangan apa yang paling banyak tmk di tahun 2025?**
  ```sql
  SELECT nama_sarana FROM public.mv_pemeriksaan WHERE jenis_sarana ILIKE '%pangan md%' AND komoditi ILIKE '%produk pangan%' AND kesimpulan ILIKE '%tmk%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY nama_sarana ORDER BY COUNT(nama_sarana) DESC LIMIT 1;
  ```
- **Gambarkan hasil pemeriksaan sarana peredaran pangan pada bulan juli 2025**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE EXTRACT(MONTH FROM tgl_start) = 7 AND EXTRACT(YEAR FROM tgl_start) = 2025;
  ```
- **Identifikasi semua pemeriksaan BCC yang dilakukan pada sarana produksi obat di Surabaya selama tahun 2024 dan hasilnya.**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(jenis_sarana) ILIKE 'produksi' AND lower(kota) LIKE '%surabaya%';
  ```
- **merekap jumlah dan nama sarana distribusi dan pelayanan yang belum pernah diperiksa dalam kurun waktu 1 tahun terakhir**  `[no-sql]`
- **Merekap jumlah dan nama sarana distribusi obat dan pelayanan farmasi yang belum pernah diperiksa dalam kurun waktu tertentu**
  ```sql
  SELECT nama_sarana, jenis_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) IN ('distribusi', 'pelayanan') AND nama_sarana NOT IN ( SELECT DISTINCT nama_sarana FROM vw_pemeriksaan_bcc WHERE tgl_start <= NOW() - interval '1 year' );
  ```
- **Pertanyaan:  
Internal QA - BPOM - Feedback Recap
Internal QA - BPOM - Feedback Recap

100%
10
C157

tampilkan data jumlah pemeriksaan sarana peredaran oleh adiyati pada tahun 2025
 
Table1
 
 	

824 dari 997 baris ditampilkan
tampilkan data jumlah pemeriksaan sarana peredaran oleh adiyati pada tahun 2025
Aktifkan dukungan pembaca layar
 
Untuk mengaktifkan dukungan pembaca layar, tekan ⌘+Opsi+Z. Untuk mempelajari pintasan keyboard, tekan ⌘garis miring.Kukang Anonim telah meninggalkan dokumen.
Mencoba buka menu sisipkan?
Sekarang Anda dapat mengaktifkan pintasan spreadsheet yang kompatibel, sehingga Anda dapat menggunakan perintah kunci yang biasa digunakan**
  ```sql
  SELECT T2.petugas, sarana, COUNT(T1.id) FROM public.mv_pemeriksaan AS T1 INNER JOIN public.mv_pemeriksaan_petugas AS T2 ON T1.id = T2.id_pemeriksaan WHERE LOWER(T1.sarana) like '%distribusi%' AND lower(T2.petugas) LIKE '%adiyati%' AND EXTRACT(YEAR FROM T1.tanggal_mulai) = 2025 GROUP BY 1, 2;
  ```
- **Pertanyaan:  Ada berapa sarana produksi AMDK dengan hasil pemeriksaan TMK di wilayah kerja Balai POM di Bogor pada tahun 2024**
  ```sql
  SELECT COUNT(DISTINCT mp.id) AS jumlah_sarana_tmk FROM mv_pemeriksaan mp JOIN mv_pemeriksaan_jenis_pangan mpjp ON mp.id = mpjp.id_pemeriksaan WHERE EXTRACT(YEAR FROM mp.tanggal_mulai) = 2024 AND LOWER(mp.nama_upt) LIKE '%bogor%' AND LOWER(mp.sarana) LIKE '%produksi%' AND LOWER(mpjp.jenis_pangan_name) LIKE '%air minum dalam kemasan%' AND UPPER(mp.kesimpulan) = 'TMK';
  ```
- **Pertanyaan:  berapa total pemeriksaan rutin sarana produksi pangan olahan MD pada bulan oktober di balai besar pom di jakarta?**
  ```sql
  SELECT COUNT(*) FROM public.mv_pemeriksaan WHERE lower(jenis_sarana) LIKE '%pangan md%' AND lower(tujuan_pemeriksaan) LIKE '%pemeriksaan rutin%' AND lower(nama_upt) LIKE '%balai besar pom di jakarta%' AND EXTRACT(MONTH FROM tanggal_mulai) = 10;
  ```
- **Pertanyaan:  Dari seluruh UPT, sarana produksi MD dengan jenis pangan apa yang paling banyak TMK di tahun 2025?**
  ```sql
  select mpjp.jenis_pangan_name, count(*) from mv_pemeriksaan_jenis_pangan mpjp join mv_pemeriksaan mp on mpjp.id_pemeriksaan = mp.id where lower(mp.jenis_sarana) like '%pangan md%' and lower(mp.sarana) = 'produksi' and lower(mp.kesimpulan) = 'tmk' and extract(year from mp.tanggal_selesai) = 2025 group by 1 order by 2 desc limit 10
  ```
- **Pertanyaan:  merekap jumlah dan nama sarana distribusi dan pelayanan yang Tidak pernah diperiksa dalam kurun waktu 1 tahun terakhir**
  ```sql
  SELECT DISTINCT nama_sarana, komoditi, tanggal_mulai FROM public.mv_pemeriksaan mp WHERE (lower(sarana) LIKE '%distribusi%' OR lower(sarana) LIKE '%pelayanan%') AND mp.nama_sarana NOT IN ( SELECT nama_sarana FROM public.mv_pemeriksaan WHERE tanggal_mulai >= NOW() - INTERVAL '1 year' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ) ORDER BY nama_sarana;
  ```
- **Pertanyaan:  pemeriksaan sarana produksi untuk komoditi kosmetik tahun 2025?**
  ```sql
  SELECT mp.sarana, mp.nama_sarana, mp.komoditi, mp.tanggal_mulai FROM public.mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(komoditi) like '%kosmetik%' AND lower(sarana) like '%produksi%'
  ```
- **Pertanyaan:  sebutkan sarana distribusi yang tutup tahun 2025?**
  ```sql
  SELECT nama_sarana, tanggal_mulai FROM public.mv_pemeriksaan WHERE sarana = 'DISTRIBUSI' AND kesimpulan = 'TTP' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Pertanyaan:  tampilkan data jumlah pemeriksaan sarana peredaran oleh adiyati pada tahun 2025**
  ```sql
  SELECT T2.petugas, sarana, COUNT(T1.id) FROM public.mv_pemeriksaan AS T1 INNER JOIN public.mv_pemeriksaan_petugas AS T2 ON T1.id = T2.id_pemeriksaan WHERE LOWER(T1.sarana) like '%peredaran%' AND lower(T2.petugas) LIKE '%adiyati%' AND EXTRACT(YEAR FROM T1.tanggal_mulai) = 2025 GROUP BY T2.petugas, T1.sarana;
  ```
- **Pertanyaan:  tampilkan data jumlah pemeriksaan sarana peredaran oleh adiyati pada tahun 2025?**
  ```sql
  SELECT T2.petugas, sarana, COUNT(T1.id) FROM public.mv_pemeriksaan AS T1 INNER JOIN public.mv_pemeriksaan_petugas AS T2 ON T1.id = T2.id_pemeriksaan WHERE LOWER(T1.sarana) like '%distribusi%' AND lower(T2.petugas) LIKE '%adiyati%' AND EXTRACT(YEAR FROM T1.tanggal_mulai) = 2025 GROUP BY 1, 2;
  ```
- **Pertanyaan:  tampilkan jumlah sarana produksi kategori mk dan tmk per komoditi, periode, wilayah, dan cakupan upt.**
  ```sql
  SELECT EXTRACT(YEAR FROM mp.tanggal_mulai), sarana, komoditi, kabupaten_kota, kesimpulan, count(nama_sarana) FROM public.mv_pemeriksaan mp WHERE lower(sarana) LIKE '%produksi%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3, 4, 5;
  ```
- **Pertanyaan:  Tampilkan profil kepatuhan pelaku usaha sarana produksi dan distribusi per komoditi untuk tahun 2025**
  ```sql
  select sarana, mp.komoditi, mp.kesimpulan, count(*) from mv_pemeriksaan mp where extract(year from mp.tanggal_mulai) = 2025 and lower(mp.sarana) in ('produksi', 'distribusi') group by 1, 2, 3
  ```
- **Pertanyaan:  Tampilkan proporsi klasifikasi sarana peredaran yang diperiksa di Balai POM di Bandung**
  ```sql
  select mp.klasifikasi_sarana, count(*) from mv_pemeriksaan mp where lower(mp.sarana) = 'distribusi' and lower(mp.nama_upt) like '%bandung%' group by 1
  ```
- **Pertanyaan:  Tampilkan realisasi inspeksi sarana distribusi periode pemeriksaan tahun 2025**
  ```sql
  WITH latest_target_year AS ( SELECT MAX(tb.tahun) AS tahun_terbaru FROM target_balai tb ), laporan_dikirim AS ( SELECT mp.nama_upt, mp.komoditi, EXTRACT(YEAR FROM mp.tanggal_selesai) AS tahun, COUNT(*) AS jumlah_laporan FROM mv_pemeriksaan mp WHERE mp.tanggal_selesai IS NOT NULL AND EXTRACT(YEAR FROM mp.tanggal_selesai) = 2025 and lower(mp.sarana) = 'distribusi' GROUP BY mp.nama_upt, mp.komoditi, EXTRACT(YEAR FROM mp.tanggal_selesai) ) SELECT ld.nama_upt, ld.komoditi, ld.tahun AS tahun_laporan, tb.tahun AS tahun_target, ld.jumlah_laporan, tb.target_sarana_distribusi, ROUND( (ld.jumlah_laporan::decimal / NULLIF(tb.target_sarana_distribusi, 0)) * 100, 2 ) AS capaian_persen FROM laporan_dikirim ld CROSS JOIN latest_target_year lty LEFT JOIN target_balai tb ON LOWER(TRIM(tb.nama_balai)) = LOWER(TRIM(ld.nama_upt)) AND LOWER(TRIM(tb.komoditi)) = LOWER(TRIM(ld.komoditi)) AND tb.tahun = lty.tahun_terbaru ORDER BY ld.nama_upt, ld.komoditi;
  ```
- **Pertanyaan:  Tampilkan sarana produksi TMK pada tiga tahun terakhir di wilayah kerja Balai POM di Pangkalpinang beserta tindak lanjut masing-masing sarana**
  ```sql
  SELECT mp.tanggal_input, mp.nama_upt, mp.kesimpulan, mp.tl_saran_names FROM mv_pemeriksaan mp WHERE LOWER(mp.sarana) LIKE '%produksi%' AND mp.tanggal_input >= (CURRENT_DATE - INTERVAL '3 years') AND LOWER(mp.nama_upt) LIKE '%pangkalpinang%' AND mp.kesimpulan = 'TMK' ORDER BY 1;
  ```
- **Pertanyaan:  tolong tampilkan hasil pemeriksaan sarana produksi MD Januari 2025**
  ```sql
  SELECT EXTRACT(MONTH FROM tanggal_mulai) AS bulan, EXTRACT(YEAR FROM tanggal_mulai) AS tahun, jenis_sarana, count(*) FROM mv_pemeriksaan mp WHERE lower(jenis_sarana) LIKE '%pangan md%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) = 1 AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3 ORDER BY 1, 2, 3;
  ```
- **Pertanyaan:  Tunjukan hasil pemeriksaan sarana peredaran pangan olahan yang Memenuhi Ketentuan dan Tidak Memenuhi Ketentuan pada bulan September 2025**
  ```sql
  SELECT sarana, kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE lower(sarana) LIKE '%distribusi%' AND kesimpulan IN ('MK', 'TMK') AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) = 9 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2 ORDER BY 1, 2;
  ```
- **Sarana distribusi apa saja yang pernah memiliki riwayat Memenuhi Ketentuan?**
  ```sql
  SELECT DISTINCT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE '%distribusi%' AND kesimpulan = 'MK';
  ```
- **Sarana distribusi apa saja yang pernah memiliki riwayat Tidak Memenuhi Ketentuan**
  ```sql
  SELECT DISTINCT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND kesimpulan LIKE 'TMK' GROUP BY nama_sarana;
  ```
- **Sarana distribusi apa saja yang pernah memiliki riwayat Tidak Memenuhi Ketentuan?**
  ```sql
  SELECT DISTINCT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND kesimpulan LIKE 'TMK' GROUP BY nama_sarana;
  ```
- **sarana distribusi di Jawa Timur apa saja yang pernah memiliki Tidak Memenuhi Ketentuan**
  ```sql
  SELECT DISTINCT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND kesimpulan LIKE 'TMK' AND lower(provinsi) LIKE 'jawa timur';
  ```
- **sarana distribusi kosmetik apa saja yang pernah diperiksa BPOM tahun 2024?**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(jenis_sarana) ILIKE 'distribusi' AND lower(komoditi) LIKE 'kosmetik' GROUP BY nama_sarana;
  ```
- **sarana distribusi kosmetik apa saja yang pernah diperiksa BPOM tahun 2025 di kota Malang**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND lower(komoditi) LIKE 'kosmetik' AND EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(kabupaten) LIKE '%malang%' GROUP BY nama_sarana;
  ```
- **sarana distribusi kosmetik apa saja yang pernah diperiksa oleh badan pom setiap tahun dari tahun 2020 hingga 2024?**
  ```sql
  SELECT nama_sarana, EXTRACT(YEAR FROM tanggal_mulai) AS tahun FROM mv_pemeriksaan WHERE lower(sarana) = 'distribusi' AND LOWER(komoditi) LIKE '%kosmetik%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM tanggal_mulai) BETWEEN 2020 AND 2024 ORDER BY 2;
  ```
- **Sarana distribusi kosmetik apa saja yang pernah diperiksa oleh Badan POM setiap tahunnya?**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE '%distribusi%' AND lower(komoditi) LIKE '%kosmetik%' GROUP BY tahun, nama_sarana ORDER BY tahun, nama_sarana;
  ```
- **Sarana distribusi kosmetik apa saja yang pernah diperiksa oleh Badan POM?**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND lower(komoditi) LIKE 'kosmetik' GROUP BY nama_sarana;
  ```
- **sarana distribusi kosmetik apa saja yang pernah diperiksan BPOM tiap tahunnya?**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE '%distribusi%' AND lower(komoditi) LIKE '%kosmetik%' GROUP BY tahun, nama_sarana ORDER BY tahun, nama_sarana;
  ```
- **Sarana produksi apa saja dengan komoditi kosmetik yang memiliki riwayat pemeriksaan Tidak Memenuhi Ketentuan dalam periode tahun 2025?**
  ```sql
  SELECT DISTINCT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND komoditi = 'Kosmetik' AND kesimpulan <> 'MK';
  ```
- **Sarana produksi apa saja dengan komoditi kosmetik yang memiliki riwayat pemeriksaan Tidak Memenuhi Ketentuan pada desember 2024**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(MONTH FROM tgl_end) = 12 AND EXTRACT(YEAR FROM tgl_end) = 2024 AND komoditi = 'Kosmetik' AND kesimpulan = 'TMK';
  ```
- **sarana produksi kosmetik apa saja yang belum dilakukan pemeriksaan dalam periode 2 tahun terakhir?**
  ```sql
  SELECT DISTINCT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE jenis_sarana = 'Produksi' AND tgl_start < (CURRENT_DATE - INTERVAL '2 year') AND nama_sarana NOT IN (SELECT DISTINCT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE jenis_sarana = 'Produksi' AND tgl_start >= (CURRENT_DATE - INTERVAL '2 year'));
  ```
- **Sarana produksi kosmetik apa saja yang memiliki riwayat pemeriksaan Tidak Memenuhi Ketentuan dalam periode tahun 2025?**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(jenis_sarana) ILIKE 'produksi' AND kesimpulan = 'TMK';
  ```
- **Sarana produksi kosmetik apa saja yang pernah memproduksi dan mengedarkan kosmetik TIE dalam periode tahun 2025?**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(jenis_sarana) ILIKE 'produksi' AND lower(temuan) LIKE '%TIE%';
  ```
- **sarana produksi kosmetik apa saja yang Tidak dilakukan pemeriksaan dalam periode 2 tahun terakhir?**
  ```sql
  SELECT nama_sarana, tanggal_mulai, kesimpulan FROM public.mv_pemeriksaan WHERE LOWER(sarana) LIKE '%produksi%' AND LOWER(komoditi) LIKE '%kosmetik%' AND kesimpulan = 'TDP' AND EXTRACT(YEAR FROM tanggal_mulai) IN (2023, 2024);
  ```
- **Sarana produksi kosmetik apa saja yang tutup dalam periode tahun 2025?**  `[no-sql]`
- **Sarana produksi kosmetik apa saja yang tutup dalam periode tahun 202?**  `[no-sql]`
- **sarana produksi kosmetik apa saja yang tutup pada tahun 2024**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(jenis_sarana) ILIKE 'produksi' AND kesimpulan = 'TTP';
  ```
- **Sarana produksi kosmetik apa saja yang tutup pada tahun 2024?**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND kesimpulan = 'TTP' AND jenis_sarana = 'Produksi' GROUP BY nama_sarana;
  ```
- **sarana produksi md apa yang paling sering memiliki riwayat tmk?**
  ```sql
  SELECT nama_sarana FROM mv_pemeriksaan WHERE jenis_sarana ILIKE '%produksi%' AND kesimpulan = 'TMK' GROUP BY nama_sarana ORDER BY COUNT(*) DESC LIMIT 1;
  ```
- **sebutkan 10 sarana produksi kosmetik yang Memenuhi Ketentuan**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE lower(jenis_sarana) ILIKE 'produksi' AND kesimpulan = 'MK' LIMIT 10;
  ```
- **sebutkan 10 sarana produksi kosmetik yang Memenuhi Ketentuan pada tahun 2025**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(jenis_sarana) ILIKE 'produksi' AND kesimpulan = 'MK' LIMIT 10;
  ```
- **Sebutkan jumlah sarana distribusi yang tutup tahun 2023, 2024 dan 2025**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_end), COUNT(nama_sarana) FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND EXTRACT(YEAR FROM tgl_end) IN (2023, 2024, 2025) AND kesimpulan LIKE 'TTP' GROUP BY EXTRACT(YEAR FROM tgl_end);
  ```
- **Sebutkan sarana distribusi yang tutup tahun 2023, 2024 dan 2025**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND EXTRACT(YEAR FROM tgl_end) IN (2023, 2024, 2025) AND kesimpulan LIKE 'TTP' GROUP BY nama_sarana;
  ```
- **sebutkan sarana distribusi yang tutup tahun 2023?**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE kesimpulan = 'TTP' AND EXTRACT(YEAR FROM tgl_end) = 2023 AND jenis_sarana = 'Distribusi' GROUP BY nama_sarana;
  ```
- **Sebutkan sarana distribusi yang tutup tahun 2024**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND EXTRACT(YEAR FROM tgl_end) = 2024 AND kesimpulan LIKE 'TTP' GROUP BY nama_sarana;
  ```
- **Sebutkan sarana distribusi yang tutup tahun 2024?**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND EXTRACT(YEAR FROM tgl_end) = 2024 AND kesimpulan LIKE 'TTP' GROUP BY nama_sarana;
  ```
- **sebutkan sarana distribusi yang tutup tahun 2025?**
  ```sql
  SELECT nama_sarana FROM public.mv_pemeriksaan WHERE jenis_sarana = 'PBF' AND kesimpulan = 'TTP' AND EXTRACT(YEAR FROM tanggal_selesai) = 2025;
  ```
- **tampilkan 10 list sarana produksi kosmetik yang pernah memproduksi dan mengedarkan kosmetik TIE**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'produksi' AND lower(komoditi) LIKE 'kosmetik' AND lower(tujuan) LIKE '%tie%' GROUP BY nama_sarana LIMIT 10;
  ```
- **Tampilkan 10 sarana produksi kosmetik teratas yang memiliki kesimpulan pemeriksaan 'Tidak Memenuhi Ketentuan' pada tahun 2025, beserta kesimpulan pemeriksaannya.**
  ```sql
  SELECT nama_sarana, kesimpulan FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(jenis_sarana) LIKE '%produksi%' AND kesimpulan = 'TMK' LIMIT 10;
  ```
- **tampilkan 100 list sarana produksi kosmetik berawalan huruf D**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'produksi' AND lower(nama_sarana) LIKE 'd%' limit 100;
  ```
- **tampilkan 200 sarana produksi kosmetik**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'produksi' LIMIT 200;
  ```
- **Tampilkan daftar fasilitas yang merupakan sarana distribusi untuk komoditas kosmetik.**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND lower(komoditi) LIKE 'kosmetik' GROUP BY nama_sarana;
  ```
- **Tampilkan data hasil pemeriksaan sarana distribusi pangan pada tahun 2021**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2021 AND lower(jenis_sarana) LIKE '%distribusi%'
  ```
- **Tampilkan data hasil pemeriksaan sarana distribusi pangan pada tahun 2022**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND EXTRACT(YEAR FROM tgl_start) = 2022;
  ```
- **Tampilkan data hasil pemeriksaan sarana distribusi pangan pada tahun 2023**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2023 AND lower(jenis_sarana) LIKE '%distribusi%';
  ```
- **tampilkan data jumlah pemeriksaan sarana peredaran oleh adiyati pada tahun 2024?**
  ```sql
  SELECT T2.petugas, sarana, COUNT(T1.id) FROM public.mv_pemeriksaan AS T1 INNER JOIN public.mv_pemeriksaan_petugas AS T2 ON T1.id = T2.id_pemeriksaan WHERE LOWER(T1.sarana) like '%distribusi%' AND lower(T2.petugas) LIKE '%adiyati%' AND EXTRACT(YEAR FROM T1.tanggal_mulai) = 2024 GROUP BY 1, 2;
  ```
- **tampilkan data jumlah pemeriksaan sarana peredaran oleh merytasari pada tahun 2025**
  ```sql
  SELECT COUNT(DISTINCT T1.id) FROM public.mv_pemeriksaan AS T1 INNER JOIN public.mv_pemeriksaan_petugas AS T2 ON T1.id = T2.id_pemeriksaan WHERE LOWER(T2.petugas) = 'merytasari' AND LOWER(T1.jenis_sarana) = 'distribusi' AND EXTRACT(YEAR FROM T1.tanggal_mulai) = 2025;
  ```
- **Tampilkan data pemeriksaan tahunan untuk sarana distribusi kosmetik oleh Badan POM.**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE '%distribusi%' AND lower(komoditi) LIKE '%kosmetik%' GROUP BY tahun, nama_sarana ORDER BY tahun, nama_sarana;
  ```
- **Tampilkan hasil pemeriksaan TMK sarana produksi MD untuk setiap PT di tahun 2025.**
  ```sql
  SELECT nama_sarana, provinsi, kabupaten, nama_balai, id_unit, klasifikasi, komoditi, tujuan, kesimpulan, tgl_start, tgl_end FROM public.vw_pemeriksaan_bcc WHERE kesimpulan = 'TMK' AND jenis_sarana = 'Produksi' AND tgl_start IS NOT NULL AND EXTRACT(YEAR FROM tgl_start) = 2025;
  ```
- **Tampilkan hasil pemeriksaan TMK sarana produksi MD untuk setiap UPT di tahun 2025.**
  ```sql
  SELECT id_unit, nama_sarana, provinsi, kabupaten, nama_balai, tgl_start, tgl_end FROM public.vw_pemeriksaan_bcc WHERE kesimpulan = 'TMK' AND EXTRACT(YEAR FROM tgl_start) = 2025;
  ```
- **Tampilkan jumlah dan nama sarana distribusi dan pelayanan yang MK/TMK masing-masing UPT pada tahun 2021**
  ```sql
  SELECT nama_balai, COUNT(CASE WHEN kesimpulan = 'MK' THEN nama_sarana ELSE NULL END) AS jumlah_mk, COUNT(CASE WHEN kesimpulan = 'TMK' THEN nama_sarana ELSE NULL END) AS jumlah_tmk FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2021 AND lower(jenis_sarana) IN ('distribusi', 'pelayanan') GROUP BY nama_balai
  ```
- **Tampilkan jumlah dan nama sarana distribusi dan pelayanan yang MK/TMK masing-masing UPT pada tahun 2024**
  ```sql
  SELECT nama_sarana, sarana, kesimpulan, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE (lower(sarana) LIKE '%distribusi%' OR lower(sarana) LIKE '%pelayanan%') AND EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3;
  ```
- **tampilkan jumlah dan nama sarana distribusi dan pelayanan yang mk/tmk masing-masing upt pada tahun 2025.**
  ```sql
  SELECT nama_upt, nama_sarana, COUNT(nama_sarana) AS jumlah_sarana FROM mv_pemeriksaan WHERE jenis_sarana IN ('distribusi', 'pelayanan') AND kesimpulan IN ('MK', 'TMK') AND EXTRACT( YEAR FROM tanggal_mulai ) = 2025 GROUP BY nama_upt, nama_sarana;
  ```
- **Tampilkan jumlah dan nama sarana distribusi obat yang MK/TMK masing-masing UPT pada tahun 2024**
  ```sql
  SELECT nama_upt, mp.kesimpulan, mp.sarana, COUNT(*) FROM public.mv_pemeriksaan mp WHERE lower(sarana) LIKE '%distribusi%' AND mp.kesimpulan IN ('MK', 'TMK') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2024 GROUP BY 1, 2, 3;
  ```
- **Tampilkan jumlah pemeriksaan sarana produksi pangan dari Januari hingga Juli 2025 berdasarkan badan pelaksana.**
  ```sql
  SELECT nama_balai, COUNT(*) AS jumlah_pemeriksaan FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) BETWEEN 1 AND 7 AND LOWER(jenis_sarana) LIKE '%produksi%' AND LOWER(komoditi) LIKE '%pangan%' GROUP BY nama_balai
  ```
- **Tampilkan jumlah pemeriksaan sarana produksi pangan dengan tujuan rutin dari Januari hingga Juli 2025.**
  ```sql
  SELECT count(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) BETWEEN 1 AND 7 AND lower(jenis_sarana) LIKE 'produksi' AND lower(tujuan) LIKE 'pemeriksaan rutin'
  ```
- **Tampilkan jumlah pemeriksaan sarana produksi pangan yang berkesimpulan TMK dari Januari hingga Juli 2025.**
  ```sql
  SELECT count(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) BETWEEN 1 AND 7 AND kesimpulan = 'TMK' AND lower(jenis_sarana) like 'produksi' AND lower(komoditi) like '%pangan%'
  ```
- **Tampilkan jumlah pemeriksaan untuk setiap sarana distribusi kosmetik oleh Badan POM per tahun.**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, nama_sarana, COUNT(*) AS jumlah_pemeriksaan FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE '%distribusi%' AND lower(komoditi) LIKE '%kosmetik%' GROUP BY tahun, nama_sarana ORDER BY tahun, nama_sarana;
  ```
- **tampilkan jumlah sarana distribusi yang tutup tahun 2022, 2023, 2024**
  ```sql
  SELECT COUNT(nama_sarana) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) IN (2022, 2023, 2024) AND lower(jenis_sarana) LIKE 'distribusi' AND kesimpulan = 'TTP'
  ```
- **tampilkan jumlah sarana produksi kategori mk dan tmk per komoditi, periode, wilayah, dan cakupan upt.**
  ```sql
  SELECT komoditi, EXTRACT(YEAR FROM tanggal_mulai) AS periode, provinsi AS wilayah, nama_upt AS cakupan_upt, kesimpulan, COUNT(DISTINCT nama_sarana) AS jumlah_sarana FROM mv_pemeriksaan WHERE jenis_sarana ILIKE '%produksi%' AND kesimpulan IN ('MK', 'TMK') AND komoditi IS NOT NULL AND tanggal_mulai IS NOT NULL AND provinsi IS NOT NULL AND nama_upt IS NOT NULL AND nama_sarana IS NOT NULL GROUP BY komoditi, periode, wilayah, cakupan_upt, kesimpulan ORDER BY komoditi, periode, wilayah, cakupan_upt, kesimpulan;
  ```
- **Tampilkan jumlah sarana produksi kosmetik yang Tidak Memenuhi Ketentuan pada tahun 2025 berdasarkan wilayah geografis.**
  ```sql
  SELECT nama_balai, count(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(jenis_sarana) LIKE 'produksi' AND kesimpulan = 'TMK' GROUP BY nama_balai
  ```
- **tampilkan list sarana produksi kosmetik**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE lower(jenis_sarana) ILIKE 'produksi' AND lower(komoditi) LIKE 'kosmetik' GROUP BY nama_sarana;
  ```
- **tampilkan list sarana produksinya**  `[no-sql]`
- **Tampilkan metrik kepatuhan regulasi untuk sarana produksi kosmetik yang memiliki kesimpulan pemeriksaan 'Tidak Memenuhi Ketentuan' pada tahun 2025.**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(jenis_sarana) ILIKE 'produksi' AND kesimpulan = 'TMK';
  ```
- **tampilkan pemeriksaan sarana distribusi kosmetik CHILA CORP pada tahun 2023**
  ```sql
  SELECT tgl_start, nama_sarana, jenis_sarana, kesimpulan FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2023 AND lower(nama_sarana) LIKE '%chila corp%' AND lower(jenis_sarana) LIKE '%distribusi%';
  ```
- **tampilkan pemeriksaan sarana distribusi kosmetik CHILA CORP pada tahun 2023, 2024 dan 2025**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, nama_sarana FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) BETWEEN 2023 AND 2025 AND lower(jenis_sarana) LIKE '%distribusi%' AND lower(nama_sarana) LIKE '%chila corp%' GROUP BY tahun, nama_sarana ORDER BY tahun, nama_sarana;
  ```
- **Tampilkan Profil Pemeriksaan Sarana Distribusi Obat dan Makanan selama periode 2022 - 2024**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, nama_sarana FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) BETWEEN 2022 AND 2024 AND lower(jenis_sarana) LIKE '%distribusi%' GROUP BY tahun, nama_sarana ORDER BY tahun, nama_sarana;
  ```
- **Tampilkan Profil Pemeriksaan Sarana Distribusi Obat dan Makanan selama periode 2022 - 2024 berdasarkan komoditi dan kesimpulan**
  ```sql
  SELECT komoditi, kesimpulan, COUNT(*) AS jumlah_pemeriksaan FROM vw_pemeriksaan_bcc where kesimpulan != 'Null' and EXTRACT(YEAR FROM tgl_end) BETWEEN 2022 AND 2024 and lower(jenis_sarana) LIKE '%distribusi%' and komoditi in ('OBAT', 'KOSMETIK', 'SUPLEMEN KESEHATAN', 'PRODUK Pangan') GROUP BY komoditi, kesimpulan ORDER BY komoditi, kesimpulan
  ```
- **Tampilkan Profil Pemeriksaan Sarana Produksi Obat dan Makanan selama periode 2023**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2023 AND jenis_sarana = 'Produksi';
  ```
- **Tampilkan Profil Pemeriksaan Sarana Produksi Obat dan Makanan selama periode 2024**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND jenis_sarana = 'Produksi';
  ```
- **Tampilkan Profil Pemeriksaan Sarana Produksi Obat dan Makanan selama periode bulan juli 2025**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) = 7 AND LOWER(jenis_sarana) LIKE '%produksi%'
  ```
- **Tampilkan Profil Pemeriksaan Sarana Produksi Obat dan Makanan selama periode Maret -   April 2025**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) BETWEEN 3 AND 4 AND LOWER(jenis_sarana) LIKE '%produksi%';
  ```
- **Tampilkan riwayat pemeriksaan untuk sarana distribusi CHILA CORP**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE LOWER(nama_sarana) LIKE '%chila corp%' AND lower(jenis_sarana) LIKE '%distribusi%'
  ```
- **Tampilkan riwayat pemeriksaan untuk sarana distribusi PT Niaga Warna Persada?**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE LOWER(nama_sarana) LIKE '%niaga warna persada%' AND lower(jenis_sarana) LIKE '%distribusi%'
  ```
- **tampilkan sarana distribusi dan pelayanan yang tutup pada periode tahun 2025**
  ```sql
  SELECT nama_sarana FROM public.mv_pemeriksaan WHERE jenis_sarana IN ('distribusi', 'pelayanan') AND kesimpulan = 'TTP' AND EXTRACT( YEAR FROM tanggal_mulai ) = 2025;
  ```
- **Tampilkan sarana distribusi kosmetik yang telah diperiksa oleh Badan POM.**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND lower(komoditi) LIKE 'kosmetik' GROUP BY nama_sarana;
  ```
- **tampilkan sarana distribusi yang tutup tahun 2022, 2023, 2024**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND EXTRACT(YEAR FROM tgl_end) IN (2022, 2023, 2024) AND kesimpulan LIKE 'TTP' GROUP BY nama_sarana;
  ```
- **tampilkan sarana produksi tmk pada tiga tahun terakhir dari tahun 2024 di wilayah kerja balai pom di pangkalpinang berserta tindak lanjut masing-masing sarana.**
  ```sql
  SELECT nama_sarana, tgl_start, kesimpulan FROM public.vw_pemeriksaan_bcc WHERE nama_balai = 'Balai POM di Pangkalpinang' AND EXTRACT( YEAR FROM tgl_start ) BETWEEN 2021 AND 2024 AND jenis_sarana = 'Produksi' AND kesimpulan = 'TMK';
  ```
- **Tampilkan sarana produksi TMK pada tiga tahun terakhir di wilayah kerja Balai POM di Pangkalpinang berserta tindak lanjut masing-masing sarana**
  ```sql
  SELECT mp.tanggal_input, mp.nama_upt, mp.kesimpulan, mp.tl_saran_names FROM mv_pemeriksaan mp WHERE LOWER(mp.sarana) LIKE '%produksi%' AND mp.tanggal_input >= (CURRENT_DATE - INTERVAL '3 years') AND LOWER(mp.nama_upt) LIKE '%pangkalpinang%' AND mp.kesimpulan = 'TMK' ORDER BY 1;
  ```
- **Tampilkan total data hasil pemeriksaan sarana distribusi pangan pada tahun 2021**
  ```sql
  SELECT count(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2021 AND lower(jenis_sarana) like 'distribusi'
  ```
- **Tampilkan total data hasil pemeriksaan sarana distribusi pangan pada tahun 2023**
  ```sql
  SELECT count(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2023 AND lower(jenis_sarana) like 'distribusi';
  ```
- **Tampilkan UPT dan hasil pemeriksaan TMK sarana produksi MD untuk setiap UPT di tahun 2025.**
  ```sql
  SELECT nama_balai, COUNT(CASE WHEN kesimpulan = 'TMK' THEN 1 END) AS jumlah_tmk FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) = 2025 AND jenis_sarana = 'Produksi' GROUP BY nama_balai;
  ```
- **Tolong buatkan query untuk: analisis jumlah seluruh sarana produksi dan distribusi tanpa pengulangan nama yang sama per komoditi produk obat/oba/sk/kos/po yang telah diperiksa bpom dalam periode 2025**
  ```sql
  SELECT sarana, komoditi, kesimpulan, count(DISTINCT nama_sarana) FROM public.mv_pemeriksaan mp WHERE (lower(sarana) LIKE '%produksi%' OR lower(sarana) LIKE '%distribusi%') AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%oba%' OR lower(komoditi) LIKE '%sk%' OR lower(komoditi) LIKE '%kos%' OR lower(komoditi) LIKE '%po%') GROUP BY 1, 2, 3;
  ```
- **Tolong buatkan query untuk: merekap jumlah dan nama sarana distribusi dan pelayanan yang Tidak pernah diperiksa dalam kurun waktu 1 tahun terakhir**
  ```sql
  SELECT DISTINCT nama_sarana FROM public.mv_pemeriksaan mp WHERE (lower(sarana) LIKE '%distribusi%' OR lower(sarana) LIKE '%pelayanan%') AND mp.nama_sarana NOT IN ( SELECT nama_sarana FROM public.mv_pemeriksaan WHERE tanggal_mulai >= NOW() - INTERVAL '1 year' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ) ORDER BY nama_sarana;
  ```
- **Tolong buatkan query untuk: sarana produksi kosmetik apa saja yang memiliki riwayat pemeriksaan tidak memenuhi ketentuan dalam periode tahun 2025?**
  ```sql
  SELECT mp.sarana, mp.nama_sarana, mpt.product_name, mp.tanggal_mulai, mpt.tp_kategori, mp.kesimpulan FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(komoditi) like '%kosmetik%' AND lower(sarana) like '%produksi%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED');
  ```
- **Tolong buatkan query untuk: sarana produksi kosmetik apa saja yang pernah memproduksi dan mengedarkan kosmetik tie dalam periode tahun 2025?**
  ```sql
  SELECT mp.sarana, mp.nama_sarana, mpt.product_name, mp.tanggal_mulai, mpt.tp_kategori FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(komoditi) like '%kosmetik%' AND lower(sarana) like '%produksi%' AND lower(mpt.tp_kategori) LIKE '%tie%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED');
  ```
- **Tolong buatkan query untuk: sarana produksi kosmetik apa saja yang Tidak dilakukan pemeriksaan dalam periode 2 tahun terakhir?**
  ```sql
  SELECT nama_sarana, MAX(tanggal_mulai) AS terakhir_diperiksa FROM mv_pemeriksaan WHERE komoditi ILIKE '%kosmetik%' AND sarana ILIKE 'produksi' GROUP BY nama_sarana HAVING COALESCE(MAX(tanggal_mulai), DATE '-infinity') < (CURRENT_DATE - INTERVAL '2 years') ORDER BY terakhir_diperiksa NULLS FIRST, nama_sarana;
  ```
- **Tolong buatkan query untuk: sarana produksi kosmetik apa saja yang tutup dalam periode tahun 2025?**
  ```sql
  SELECT nama_sarana, tanggal_mulai, kesimpulan FROM public.mv_pemeriksaan WHERE LOWER(sarana) LIKE '%produksi%' AND LOWER(komoditi) LIKE '%kosmetik%' AND kesimpulan = 'TTP' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Tolong buatkan query untuk: sarana produksi md apa yang paling sering memiliki riwayat tmk?**
  ```sql
  SELECT nama_sarana, jenis_sarana, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(jenis_sarana) LIKE '%pangan md%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3 ORDER BY 4 DESC LIMIT 10;
  ```
- **Tolong buatkan query untuk: sebutkan sarana distribusi yang tutup tahun 2025?**
  ```sql
  SELECT nama_sarana, tanggal_mulai FROM public.mv_pemeriksaan WHERE lower(sarana) LIKE '%distribusi%' AND kesimpulan = 'TTP' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Tolong buatkan query untuk: tampilkan data jumlah pemeriksaan sarana peredaran oleh adiyati pada tahun 2025**
  ```sql
  SELECT T2.petugas, T1.nama_sarana, COUNT(T1.id) FROM public.mv_pemeriksaan AS T1 INNER JOIN public.mv_pemeriksaan_petugas AS T2 ON T1.id = T2.id_pemeriksaan WHERE LOWER(T1.nama_sarana) like '%peredaran%' AND lower(T2.petugas) LIKE '%adiyati%' AND EXTRACT(YEAR FROM T1.tanggal_mulai) = 2025 GROUP BY T2.petugas, T1.nama_sarana;
  ```
- **Tolong buatkan query untuk: tampilkan jumlah dan nama sarana distribusi dan pelayanan yang mk/tmk masing-masing upt pada tahun 2025.**
  ```sql
  SELECT nama_sarana, sarana, kesimpulan, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE (lower(sarana) LIKE '%distribusi%' OR lower(sarana) LIKE '%pelayanan%') AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3;
  ```
- **Tolong buatkan query untuk: tampilkan jumlah sarana produksi kategori mk dan tmk per komoditi, periode, wilayah, dan cakupan upt.**
  ```sql
  SELECT EXTRACT(YEAR FROM mp.tanggal_mulai), mp.komoditi, mp.kabupaten, mp.nama_upt, mp.kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE lower(mp.sarana) LIKE '%produksi%' AND mp.kesimpulan IN ('MK', 'TMK') AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3, 4, 5;
  ```
- **Tolong buatkan query untuk: tampilkan sarana distribusi dan pelayanan yang tutup pada periode tahun 2025**
  ```sql
  SELECT nama_sarana, sarana, tanggal_mulai FROM public.mv_pemeriksaan WHERE (lower(sarana) LIKE '%distribusi%' OR lower(sarana) LIKE '%pelayanan%') AND kesimpulan = 'TTP' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Tolong buatkan query untuk: UPT manakah yang hasil pemeriksaan TMK sarana produksi MD nya paling banyak di tahun 2025?**
  ```sql
  SELECT nama_balai, count(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND kesimpulan = 'TMK' AND lower(jenis_sarana) like 'produksi' AND klasifikasi LIKE '%MD%' GROUP BY nama_balai ORDER BY COUNT(*) DESC LIMIT 5;
  ```
- **Tunjukan hasil pemeriksaan sarana peredaran pangan olahan yang Memenuhi Ketentuan dan Tidak Memenuhi Ketentuan pada bulan Januari sampai Agustus 2025 untuk Balai Besar POM di Yogyakarta**
  ```sql
  SELECT sarana, kesimpulan, COUNT(*) FROM public.mv_pemeriksaan mp WHERE lower(sarana) LIKE '%distribusi%' AND kesimpulan IN ('MK', 'TMK') AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) BETWEEN 1 AND 8 AND lower(nama_upt) LIKE '%balai besar pom di yogyakarta%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2 ORDER BY 1, 2;
  ```
- **Untuk komoditas kosmetik, sarana produksi apa saja yang tutup pada tahun 2024?**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND kesimpulan = 'TTP' AND jenis_sarana = 'Produksi' GROUP BY nama_sarana;
  ```
- **upt mana saja yang paling banyak melaporkan hasil pemeriksaan sarana produksi yang tmk?**
  ```sql
  SELECT nama_upt FROM public.mv_pemeriksaan WHERE jenis_sarana ILIKE '%produksi%' AND kesimpulan = 'TMK' GROUP BY nama_upt ORDER BY COUNT(id) DESC LIMIT 1;
  ```
- **UPT manakah yang hasil pemeriksaan TMK sarana produksi MD nya paling banyak di tahun 2023?**
  ```sql
  SELECT nama_balai FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2023 AND kesimpulan = 'TMK' AND jenis_sarana = 'Produksi' GROUP BY nama_balai ORDER BY COUNT(*) DESC LIMIT 1;
  ```
- **UPT manakah yang hasil pemeriksaan TMK sarana produksi MD nya paling banyak di tahun 2025?**
  ```sql
  SELECT nama_balai FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND kesimpulan = 'TMK' AND jenis_sarana = 'Produksi' GROUP BY nama_balai ORDER BY COUNT(*) DESC LIMIT 1;
  ```

### Geografis (provinsi/kabupaten) — 9 pertanyaan

**SQL template warehouse (kanonik):**
```sql
SELECT provinsi, COUNT(DISTINCT id) FROM mv_pemeriksaan
WHERE kesimpulan = 'TMK'
GROUP BY 1 ORDER BY 2 DESC;
```
*provinsi (34 nilai). kabupaten_kota Title Case — pakai lower() untuk join.*

- **Berapa jumlah pemeriksaan dengan kesimpulan Memenuhi Ketentuan di provinsi Jawa Barat pada bulan Juni 2025**
  ```sql
  SELECT COUNT(*) FROM public.vw_pemeriksaan_bcc WHERE provinsi = 'Jawa Barat' AND kesimpulan = 'Memenuhi Ketentuan' AND tgl_start >= '2025-06-01' AND tgl_end <= '2025-06-30';
  ```
- **Berapa jumlah pemeriksaan dengan kesimpulan MK di provinsi Jawa Barat pada bulan Juni 2025?**
  ```sql
  SELECT COUNT(*) FROM public.vw_pemeriksaan_bcc WHERE provinsi = 'Jawa Barat' AND kesimpulan = 'MK' AND tgl_start >= '2025-06-01' AND tgl_end <= '2025-06-30';
  ```
- **Berapa jumlah pemeriksaan dengan kesimpulan MK di provinsi Jawa Tengah pada bulan Juni 2025?**
  ```sql
  SELECT COUNT(*) FROM public.vw_pemeriksaan_bcc WHERE provinsi = 'Jawa Tengah' AND kesimpulan = 'MK' AND tgl_start >= '2025-06-01' AND tgl_end <= '2025-06-30';
  ```
- **Berapa jumlah pemeriksaan dengan kesimpulan TMK di provinsi Jawa Tengah pada bulan Juni 2025?**
  ```sql
  SELECT COUNT(*) FROM public.vw_pemeriksaan_bcc WHERE provinsi = 'Jawa Tengah' AND kesimpulan = 'TMK' AND tgl_start >= '2025-06-01' AND tgl_end <= '2025-06-30';
  ```
- **Berapa jumlah pemeriksaan pada komoditi Kosmetik dengan kesimpulan TMK di provinsi Jawa Tengah pada bulan Juni 2025?**
  ```sql
  SELECT COUNT(*) FROM public.vw_pemeriksaan_bcc WHERE komoditi = 'Kosmetik' AND kesimpulan = 'TMK' AND provinsi = 'Jawa Tengah' AND tgl_start >= '2025-06-01' AND tgl_end <= '2025-06-30';
  ```
- **Berikan daftar sarana berdasarkan provinsi.**
  ```sql
  SELECT provinsi, count(*) FROM vw_pemeriksaan_bcc GROUP BY 1
  ```
- **berikan nama sarana, provinsi, kabupaten pada tabel pemeriksaan tahun 2025**
  ```sql
  SELECT nama_sarana, provinsi, kabupaten FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025;
  ```
- **provinsi mana yang hasil pemeriksaan kosmetiknya paling banyak TMS?**
  ```sql
  SELECT provinsi FROM public.vw_pemeriksaan_bcc WHERE kesimpulan = 'TMK' GROUP BY provinsi ORDER BY COUNT(*) DESC LIMIT 1;
  ```
- **tampilkan persebaran pemeriksaan sarana di kab/kota wilayah kerja upt pada tahun 2025.**
  ```sql
  SELECT nama_balai, nama_sarana, count(*) FROM vw_pemeriksaan_bcc vpb WHERE lower(nama_balai) LIKE '%bandung%' AND EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY 1, 2;
  ```

### Filter komoditi — 15 pertanyaan

**SQL template warehouse (kanonik):**
```sql
SELECT komoditi, COUNT(DISTINCT id) FROM mv_pemeriksaan
WHERE komoditi = 'OBAT'
  AND tanggal_mulai >= '2025-01-01' AND tanggal_mulai < '2026-01-01'
GROUP BY 1;
```
*13 nilai komoditi (UPPER). "obat" informal bisa = 8 sub-komoditi (lihat dok 04).*

- **Pertanyaan:  bagaimana jumlah pemeriksaan per komoditas pada oktober 2025**
  ```sql
  SELECT komoditi, count(*) FROM mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) = 10 GROUP BY komoditi
  ```
- **Pertanyaan:  tampilkan semua komodit yang aman dan bermutu**
  ```sql
  SELECT DISTINCT komoditi FROM public.mv_pemeriksaan WHERE kesimpulan = 'MK';
  ```
- **Tampilkan 'BCC examination' yang dilakukan untuk jenis komoditas kosmetik pada tahun 2025.**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(komoditi) LIKE '%kosmetik%';
  ```
- **Tampilkan 'Examination conclusion' dari 'BCC examination' yang dilakukan untuk jenis komoditas kosmetik pada tahun 2025.**
  ```sql
  SELECT kesimpulan FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(komoditi) LIKE '%kosmetik%';
  ```
- **Tampilkan data pengawasan bulanan untuk komoditi kosmetika selama tahun 2025 berdasarkan lembaga pelaksana.**
  ```sql
  SELECT EXTRACT(MONTH FROM tgl_start) AS bulan, nama_balai, COUNT(*) AS jumlah_pemeriksaan FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND komoditi = 'Kosmetika' GROUP BY bulan, nama_balai ORDER BY bulan, nama_balai;
  ```
- **Tampilkan data pengawasan bulanan untuk komoditi kosmetika selama tahun 2025.**
  ```sql
  SELECT EXTRACT(MONTH FROM tgl_start) AS bulan, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND komoditi ILIKE 'KOSMETIK' GROUP BY bulan ORDER BY bulan;
  ```
- **Tampilkan jenis komoditas kosmetik yang diperiksa di berbagai sarana oleh BPOM setiap tahunnya.**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, komoditi FROM vw_pemeriksaan_bcc WHERE lower(komoditi) LIKE '%kosmetik%' GROUP BY tahun, komoditi ORDER BY tahun, komoditi;
  ```
- **Tampilkan jumlah pemeriksaan BCC berdasarkan komoditi pada tahun 2025.**
  ```sql
  SELECT komoditi, COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY komoditi;
  ```
- **Tampilkan metrik kepatuhan regulasi bulanan terkait pengawasan komoditi kosmetika di tahun 2025.**
  ```sql
  SELECT EXTRACT(MONTH FROM tgl_start) AS bulan, COUNT(CASE WHEN kesimpulan = 'MK' THEN 1 END) AS jumlah_memenuhi_ketentuan, COUNT(CASE WHEN kesimpulan = 'TMK' THEN 1 END) AS jumlah_tidak_memenuhi_ketentuan, COUNT(CASE WHEN kesimpulan = 'TDP' THEN 1 END) AS jumlah_tidak_dapat_diperiksa, COUNT(CASE WHEN kesimpulan = 'TTP' THEN 1 END) AS jumlah_tutup FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY bulan ORDER BY bulan;
  ```
- **Tampilkan metrik kepatuhan regulasi pemeriksaan BCC berdasarkan komoditi pada tahun 2025.**
  ```sql
  SELECT komoditi, kesimpulan, COUNT(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY komoditi, kesimpulan;
  ```
- **tampilkan nama produk komoditi kosmetika yang TMS pada periode bulan juli 2025**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(MONTH FROM tgl_start) = 7 AND EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(jenis_sarana) ILIKE 'produksi' AND kesimpulan = 'TMK';
  ```
- **Tampilkan sarana yang menjalani pemeriksaan BCC terkait komoditas kosmetik setiap tahunnya.**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(komoditi) LIKE '%kosmetik%' GROUP BY tahun, nama_sarana ORDER BY tahun, nama_sarana;
  ```
- **Tampilkan tingkat kepatuhan regulasi dari pengawasan bulanan komoditi kosmetika di tahun 2025.**
  ```sql
  SELECT EXTRACT(MONTH FROM tgl_start) AS month, SUM(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE 0 END) AS compliant_count, COUNT(*) AS total_count, CASE WHEN COUNT(*) = 0 THEN 0 -- Avoid division by zero ELSE (SUM(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100 END AS compliance_rate FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND LOWER(komoditi) LIKE '%kosmetika%' GROUP BY month ORDER BY month;
  ```
- **Tampilkan tujuan pemeriksaan BCC berdasarkan komoditi pada tahun 2025.**
  ```sql
  SELECT tujuan, COUNT(id) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY tujuan;
  ```
- **Tunjukkan jumlah pemeriksaaan 3 bulan terakhir berdasarkan komoditas**
  ```sql
  SELECT komoditi, COUNT(CAST(id AS NUMERIC)) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE tgl_start::DATE >= CURRENT_DATE - INTERVAL '3 months' GROUP BY komoditi;
  ```

### Filter jenis_sarana — 20 pertanyaan

**SQL template warehouse (kanonik):**
```sql
SELECT jenis_sarana, COUNT(DISTINCT id) FROM mv_pemeriksaan
WHERE jenis_sarana IN ('PANGAN IRT (CPPB - IRT)','PANGAN MD','APOTEK')
GROUP BY 1 ORDER BY 2 DESC;
```
*24 nilai jenis_sarana. PANGAN IRT = hotspot #1 TMK.*

- **"tampilkan data persentase pirt yang aman dan bermutu selama periode 2025"**
  ```sql
  SELECT CAST(SUM(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE 0 END) AS NUMERIC) * 100 / COUNT(*) AS persentase_pirt_aman_dan_bermutu FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) = 2025;
  ```
- **Apa jenis sarana yang paling sering diperiksa?**
  ```sql
  SELECT jenis_sarana FROM public.vw_pemeriksaan_bcc GROUP BY jenis_sarana ORDER BY COUNT(*) DESC LIMIT 1;
  ```
- **berapa jumlah pemeriksaan sarana dari januari sampai september tahun 2025 untuk obat detailkan per jenis sarana**  `[no-sql]`
- **berapa jumlah pemeriksaan sarana obat per jenis sarana selama periode januari sampai september 2035**  `[no-sql]`
- **Berapa perbandingan total pemeriksaan berdasarkan tahun dan jenis sarana dari tahun 2023 sampai dengan Juni tahun 2025**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, jenis_sarana, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) >= 2023 AND EXTRACT(YEAR FROM tgl_start) <= 2025 AND (EXTRACT(YEAR FROM tgl_start) < 2025 OR (EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) <= 6)) GROUP BY tahun, jenis_sarana ORDER BY tahun, jenis_sarana;
  ```
- **Berapa perbandingan total pemeriksaan dari tahun 2023 sampai dengan Juni tahun 2025 berdasarkan jenis sarana**
  ```sql
  SELECT jenis_sarana, COUNT(*) AS total_pemeriksaan FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) >= 2023 AND EXTRACT(YEAR FROM tgl_start) <= 2025 AND (EXTRACT(YEAR FROM tgl_start) < 2025 OR EXTRACT(MONTH FROM tgl_start) <= 6) GROUP BY jenis_sarana;
  ```
- **Berikan daftar sarana berdasarkan jenis sarana.**
  ```sql
  SELECT jenis_sarana FROM vw_pemeriksaan_bcc GROUP BY jenis_sarana
  ```
- **berikan total pemeriksaan berdasarkan jenis sarana dari tahun 2023 sampai bulan juni tahun 2025**
  ```sql
  SELECT jenis_sarana , count(*) FROM vw_pemeriksaan_bcc vpb WHERE EXTRACT(YEAR FROM tgl_start) >= 2023 AND EXTRACT(YEAR FROM tgl_start) <= 2025 AND EXTRACT(MONTH FROM tgl_start) <= 6 GROUP BY 1 LIMIT 5;
  ```
- **berikan total pemeriksaan berdasarkan jenis sarana per tahun 2023, 2024, sampai bulan juni tahun 2025**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, jenis_sarana, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) >= 2023 AND EXTRACT(YEAR FROM tgl_start) <= 2025 AND (EXTRACT(YEAR FROM tgl_start) < 2025 OR EXTRACT(MONTH FROM tgl_start) <= 6) GROUP BY tahun, jenis_sarana ORDER BY tahun, jenis_sarana;
  ```
- **Pertanyaan:  berapa jumlah pemeriksaan pangan MD dengan tujuan pemeriksaan fortifikasi untuk tahun 2025, detailkan dengan jumlah MK dan TMK nya**
  ```sql
  SELECT mp.kesimpulan, COUNT(*) FROM public.mv_pemeriksaan mp WHERE lower(jenis_sarana) LIKE '%pangan md%' AND lower(tujuan_pemeriksaan) LIKE '%fortifikasi%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 GROUP BY 1;
  ```
- **Pertanyaan:  data IRTP tahun 2024**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, jenis_sarana, count(*) FROM mv_pemeriksaan mp WHERE lower(jenis_sarana) LIKE '%pangan irt%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2 ORDER BY 1, 2;
  ```
- **Pertanyaan:  Tampilkan data Persentase PIRT yang aman dan bermutu selama tahun 2024**
  ```sql
  -- A well-formed multi-line SQL query between
  ```
- **Pertanyaan:  tampilkan data profil jenis sarana yang sudah dilakukan pemeriksaan dari tahun 2025**
  ```sql
  SELECT mp.jenis_sarana, mp.kesimpulan, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3;
  ```
- **Pertanyaan:  tampilkan jenis sarana yang paling banyak diperiksa pada tahun 2025.**
  ```sql
  SELECT sarana, jenis_sarana, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY 1, 2 ORDER BY 3 DESC;
  ```
- **tampilkan data profil jenis sarana yang sudah dilakukan pemeriksaan dari tahun 2025**
  ```sql
  SELECT DISTINCT jenis_sarana FROM mv_pemeriksaan WHERE tanggal_mulai >= '2025-01-01';
  ```
- **tampilkan jenis sarana yang paling banyak diperiksa pada tahun 2025.**
  ```sql
  SELECT jenis_sarana FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY jenis_sarana ORDER BY COUNT(id) DESC LIMIT 1;
  ```
- **tampilkan jenis sarana yang paling banyak diperiksa pada tahun sebelumnya**
  ```sql
  SELECT sarana, jenis_sarana, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 GROUP BY 1, 2 ORDER BY 3 DESC;
  ```
- **Tampilkan jumlah pemeriksaan sarana per jenis sarana dari Januari hingga September 2025.**
  ```sql
  SELECT mp.jenis_sarana, count(*) FROM public.mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) BETWEEN 1 AND 9 GROUP BY 1;
  ```
- **Tolong buatkan query untuk: tampilkan data profil jenis sarana yang sudah dilakukan pemeriksaan dari tahun 2025**
  ```sql
  SELECT mp.jenis_sarana, mp.kesimpulan, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY 1, 2, 3;
  ```
- **Tolong buatkan query untuk: tampilkan jenis sarana yang paling banyak diperiksa pada tahun 2025.**
  ```sql
  SELECT nama_sarana, jenis_sarana, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY 1, 2 ORDER BY 3 DESC;
  ```

### Filter tujuan pemeriksaan — 19 pertanyaan

**SQL template warehouse (kanonik):**
```sql
SELECT tujuan_pemeriksaan, COUNT(DISTINCT id) FROM mv_pemeriksaan
WHERE tujuan_pemeriksaan = 'PEMERIKSAAN RUTIN'
GROUP BY 1;
```
*36 nilai. RUTIN = baseline kepatuhan. KASUS/INTENSIFIKASI = targeted.*

- **"tampilkan persentase mk tmk hasil pemeriksaan sarana pangan olahan md untuk tujuan pemeriksaan pemeriksaan rutin dari seluruh upt di tahun 2025 dalam bentuk diagram batang"**
  ```sql
  SELECT SUM(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS percentage_mk, SUM(CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS percentage_tmk FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND tujuan = 'Pemeriksaan Rutin' AND jenis_sarana = 'Produksi';
  ```
- **ada berapa sertifikasi yang udah expired per hari tahun 2025**
  ```sql
  SELECT tanggal_selesai, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND tanggal_selesai < '2026-03-03' GROUP BY tanggal_selesai ORDER BY tanggal_selesai;
  ```
- **Berapa jumlah pemeriksaan sarana 'produksi pangan' dalam rangka pemeriksaan rutin dibandingan dengan jumlah pemeriksaan sarana 'produksi pangan' dalam rangka sertifikasi selama Januari hingga Juli 2025?**
  ```sql
  SELECT SUM(CASE WHEN LOWER(tujuan) LIKE '%rutin%' THEN 1 ELSE 0 END) AS jumlah_rutin, SUM(CASE WHEN LOWER(tujuan) LIKE '%sertifikasi%' THEN 1 ELSE 0 END) AS jumlah_sertifikasi FROM vw_pemeriksaan_bcc WHERE EXTRACT(MONTH FROM tgl_start) BETWEEN 1 AND 7 AND EXTRACT(YEAR FROM tgl_start) = 2025 AND LOWER(jenis_sarana) LIKE '%produksi%';
  ```
- **berapa jumlah sarana yang diperiksa dalam rangka kasus di wilayah kerja bbpom di bandung pada tahun 2024?**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE nama_balai = 'BBPOM di Bandung' AND EXTRACT( YEAR FROM tgl_start ) = 2024;
  ```
- **berapa jumlah sarana yang diperiksa dalam rangka kasus di wilayah kerja bbpom di bandung pada tahun 2025?**
  ```sql
  SELECT count(*) FROM public.mv_pemeriksaan mp WHERE lower(tujuan_pemeriksaan) LIKE '%kasus%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND lower(kabupaten_kota) LIKE '%bandung%' AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025;
  ```
- **Berapa jumlah sarana yang memenuhi ketentuan dalam pemeriksaan rutin?**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE kesimpulan = 'MK';
  ```
- **Berapa jumlah sarana yang tidak memenuhi ketentuan dalam pemeriksaan rutin?**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE kesimpulan = 'TMK';
  ```
- **berapa sertifikasi yang keluar tahun 2025**
  ```sql
  SELECT count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND kesimpulan = 'MK';
  ```
- **Pertanyaan:  berapa jumlah sarana yang diperiksa dalam rangka kasus di wilayah kerja bbpom di bandung pada tahun 2024?**
  ```sql
  SELECT count(*) FROM public.mv_pemeriksaan mp WHERE lower(tujuan_pemeriksaan) LIKE '%kasus%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND lower(nama_sarana) LIKE '%bandung%' AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2024;
  ```
- **Pertanyaan:  count pemeriksaan untuk tiap inspektur beserta tujuan dan nama balainya untuk tahun 2025**
  ```sql
  SELECT mpp.daftar_balai_pemeriksa, mpp.petugas, mpp.tujuan, COUNT(*) FROM mv_pemeriksaan_petugas mpp WHERE EXTRACT(YEAR FROM mpp.tgl_surat) = 2025 GROUP BY mpp.daftar_balai_pemeriksa, mpp.petugas, mpp.tujuan ORDER BY mpp.daftar_balai_pemeriksa, mpp.petugas, mpp.tujuan;
  ```
- **Pertanyaan:  Tampilkan hasil tingkat kekritisan berdasarkan klasifikasi dan tujuan pemeriksaan**
  ```sql
  select mkp.klasifikasi, mkp.tujuan, mkp.tx_criteria, count(*) from mv_kriteria_pemeriksaan mkp group by 1, 2, 3 order by 1, 2, 3
  ```
- **Pertanyaan:  tampilkan persentase mk tmk hasil pemeriksaan sarana pangan olahan md untuk tujuan pemeriksaan pemeriksaan rutin dari seluruh upt di tahun 2025 dalam bentuk diagram batang**
  ```sql
  SELECT nama_upt, mp.kesimpulan, COUNT(*) FROM public.mv_pemeriksaan mp WHERE lower(jenis_sarana) LIKE '%pangan md%' AND lower(tujuan_pemeriksaan) LIKE '%pemeriksaan rutin%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 GROUP BY 1,2;
  ```
- **tampilkan jumlah inspeksi rutin kategori mk dan tmk per periode 2025**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS periode, COUNT(CASE WHEN kesimpulan = 'MK' THEN 1 END) AS jumlah_mk, COUNT(CASE WHEN kesimpulan = 'TMK' THEN 1 END) AS jumlah_tmk FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY periode;
  ```
- **tampilkan persentase mk tmk hasil pemeriksaan sarana pangan olahan md untuk tujuan pemeriksaan pemeriksaan rutin dari seluruh upt di tahun 2025 dalam bentuk diagram batang**
  ```sql
  WITH filtered_data AS ( SELECT kesimpulan FROM public.mv_pemeriksaan WHERE LOWER(jenis_sarana) LIKE '%pangan md%' AND LOWER(tujuan_pemeriksaan) LIKE '%pemeriksaan rutin%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND kesimpulan IN ('MK', 'TMK') ), total_counts AS ( SELECT COUNT(*) AS total_mk_tmk FROM filtered_data ) SELECT fd.kesimpulan, COUNT(fd.kesimpulan) AS count, (COUNT(fd.kesimpulan) * 100.0 / tc.total_mk_tmk) AS percentage FROM filtered_data fd, total_counts tc GROUP BY fd.kesimpulan, tc.total_mk_tmk;
  ```
- **Tampilkan tujuan pemeriksaan untuk CV Sinar Intan Raya di tahun 2024.**
  ```sql
  SELECT tujuan FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(nama_sarana) LIKE '%sinar intan raya%' GROUP BY tujuan;
  ```
- **Tampilkan tujuan spesifik dari pemeriksaan BCC.**
  ```sql
  SELECT DISTINCT tujuan FROM vw_pemeriksaan_bcc;
  ```
- **Tolong buatkan query untuk: berapa jumlah sarana yang diperiksa dalam rangka kasus di wilayah kerja bbpom di bandung pada tahun 2024?**
  ```sql
  SELECT count(nama_sarana) FROM public.mv_pemeriksaan WHERE lower(tujuan_pemeriksaan) LIKE '%kasus%' AND status IN ('VERIFY4', 'VERIFY5', 'VERIFY6', 'VERIFY7', 'FINISHED') AND lower(kabupaten) LIKE '%bandung%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2024;
  ```
- **Tolong buatkan query untuk: tampilkan jumlah inspeksi rutin kategori mk dan tmk per periode 2025**
  ```sql
  SELECT tujuan_pemeriksaan, mp.kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE lower(tujuan_pemeriksaan) LIKE '%rutin%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND mp.kesimpulan IN ('MK', 'TMK') GROUP BY 1, 2;
  ```
- **Tolong buatkan query untuk: tampilkan persentase mk tmk hasil pemeriksaan sarana pangan olahan md untuk tujuan pemeriksaan pemeriksaan rutin dari seluruh upt di tahun 2025 dalam bentuk diagram batang**
  ```sql
  SELECT nama_upt, mp.kesimpulan, COUNT(*) FROM public.mv_pemeriksaan mp WHERE lower(jenis_sarana) LIKE '%pangan md%' AND lower(tujuan_pemeriksaan) LIKE '%pemeriksaan rutin%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND mp.kesimpulan IN ('MK', 'TMK') GROUP BY 1,2;
  ```

### Jumlah pemeriksaan per periode — 82 pertanyaan

**SQL template warehouse (kanonik):**
```sql
SELECT COUNT(DISTINCT id) FROM mv_pemeriksaan
WHERE tanggal_mulai >= '2025-06-01' AND tanggal_mulai < '2025-07-01'
  AND nama_upt NOT IN ('DEMO BALAI BESAR','DEMO TIPE A');
```
*Entity = COUNT(DISTINCT id). Kolom tanggal = tanggal_mulai (BUKAN tanggal_input).*

- **"berapa total sarana yang tutup dan/atau tidak berproduksi saat diperiksa di tahun 2025 di wilayah kerja jakarta utara?"**
  ```sql
  SELECT COUNT(CASE WHEN EXTRACT(YEAR FROM tgl_start) = 2025 THEN id ELSE NULL END) FROM public.vw_pemeriksaan_bcc WHERE kabupaten LIKE '%Jakarta Utara%' AND kesimpulan = 'TTP' AND jenis_sarana = 'Produksi';
  ```
- **ada berapa pemeriksaan di bulan juli dan berapa yang tidak memenuhi ketentuan**
  ```sql
  SELECT COUNT(*) AS total_inspections, SUM(CASE WHEN kesimpulan != 'MK' THEN 1 ELSE 0 END) AS inspections_not_meeting_criteria FROM public.vw_pemeriksaan_bcc WHERE (tgl_start BETWEEN '2025-07-01' AND '2025-07-31' OR tgl_end BETWEEN '2025-07-01' AND '2025-07-31');
  ```
- **Ada pemeriksaan berapa tahun ini?**
  ```sql
  SELECT COUNT(DISTINCT EXTRACT(YEAR FROM tgl_start)) AS jumlah_tahun FROM public.vw_pemeriksaan_bcc;
  ```
- **berapa banyak hasil pemeriksaan MK pada bulan april tahun 2025**
  ```sql
  SELECT COUNT(*) FROM public.mv_pemeriksaan mp WHERE EXTRACT(MONTH FROM mp.tanggal_mulai) = 4 AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND lower(mp.kesimpulan) = 'mk';
  ```
- **Berapa jumlah pemeriksaan di tahun 2024?**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024;
  ```
- **Berapa jumlah pemeriksaan di tahun 2025?**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025
  ```
- **Berapa jumlah pemeriksaan pada bulan Juli 2025?**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(MONTH FROM tgl_start) = 7 AND EXTRACT(YEAR FROM tgl_start) = 2025
  ```
- **Berapa Jumlah Pemeriksaan pada bulan Juni 2025**
  ```sql
  SELECT COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE (tgl_start >= '2025-06-01' AND tgl_start < '2025-07-01') OR (tgl_end >= '2025-06-01' AND tgl_end < '2025-07-01');
  ```
- **Berapa jumlah pemeriksaan pada bulan Juni 2025?**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(MONTH FROM tgl_start) = 6 AND EXTRACT(YEAR FROM tgl_start) = 2025
  ```
- **berapa jumlah pemeriksaan pada tahun 2024**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024;
  ```
- **Berapa jumlah pemeriksaan pada tahun ini?**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = EXTRACT(YEAR FROM CURRENT_DATE);
  ```
- **berapa jumlah pemeriksaan sarana dari januari sampai september tahun 2025 untuk obat detailkan per klasifikasi sarana**  `[no-sql]`
- **berapa jumlah pemeriksaan sarana per klasifikasi dan pemeriksaan sarana yang sudah ada hasilnya dan belum dari januari sampai september tahun 2025 untuk obat**  `[no-sql]`
- **Berapa jumlah pemeriksaan tahun 2024?**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024
  ```
- **berapa jumlah pemeriksaan tahun ini**
  ```sql
  SELECT COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pengujian_bcc WHERE EXTRACT(YEAR FROM tglsampling) = EXTRACT(YEAR FROM CURRENT_DATE);
  ```
- **Berapa jumlah pemeriksaan tahun ini?**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = EXTRACT(YEAR FROM CURRENT_DATE);
  ```
- **Berapa jumlah pemeriksaan tahun lalu?**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '1 year');
  ```
- **berapa jumlah pemeriksaan tahun sebelumnya di periode yang sama**
  ```sql
  SELECT count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(MONTH FROM tanggal_mulai) = 9 AND EXTRACT(YEAR FROM tanggal_mulai) = 2024
  ```
- **Berapa jumlah pemeriksaan untuk masing-masing kesimpulan (MK, TMK, NULL, TTP, TDP) pada bulan Agustus 2025?**  `[no-sql]`
- **Berapa jumlah pemeriksaan untuk masing-masing kesimpulan (MK, TMK, NULL, TTP, TDP) pada bulan Juli 2024?**  `[no-sql]`
- **Berapa jumlah pemeriksaan untuk masing-masing kesimpulan (MK, TMK, NULL, TTP, TDP) pada bulan Juli 2025?**  `[no-sql]`
- **Berapa jumlah pemeriksaan untuk masing-masing kesimpulan (MK, TMK, NULL, TTP, TDP) pada bulan Mei 2025?**  `[no-sql]`
- **Berapa jumlah pemeriksaan untuk masing-masing kesimpulan (MK, TMK, NULL, TTP, TDP) pada tahun 2025?**  `[no-sql]`
- **Berapa jumlah pemeriksaan untuk masing-masing kesimpulan pada bulan Juli 2025?**
  ```sql
  SELECT kesimpulan, COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(MONTH FROM tgl_start) = 7 AND EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY kesimpulan;
  ```
- **Berapa jumlah pemeriksaan untuk setiap kesimpulan pada bulan Juli 2025?**
  ```sql
  SELECT kesimpulan, COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(MONTH FROM tgl_start) = 7 AND EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY kesimpulan;
  ```
- **Berapa jumlah pemeriksaan yaang dinyatakan Memenuhi Ketentuan di Balai Besar POM di Jakarta pada bulan Juni 2025**
  ```sql
  SELECT COUNT(*) FROM public.vw_pemeriksaan_bcc WHERE nama_balai = 'Balai Besar POM di Jakarta';
  ```
- **Berapa jumlah pemeriksaan yaang dinyatakan Memenuhi Ketentuan di Balai Besar POM di Jakarta pada bulan Juni 2025?**
  ```sql
  SELECT COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE kesimpulan = 'MK' AND tgl_start >= '2025-06-01' AND tgl_end <= '2025-06-30';
  ```
- **berapa jumlah penurunan pemeriksaan dari mei ke juni 2025**
  ```sql
  SELECT COUNT(*) AS jumlah_penurunan FROM public.vw_pemeriksaan_bcc WHERE tgl_start BETWEEN '2025-05-01' AND '2025-05-31' AND kesimpulan = 'MK' AND NOT EXISTS ( SELECT 1 FROM public.vw_pemeriksaan_bcc AS sub WHERE sub.tgl_start BETWEEN '2025-06-01' AND '2025-06-30' AND sub.kesimpulan = 'MK' AND sub.nama_sarana = vw_pemeriksaan_bcc.nama_sarana );
  ```
- **berapa jumlah sarana yang sudah diperiksa selama periode januari sampai juni 2025 beserta klasifikasinya**
  ```sql
  SELECT jenis_sarana, COUNT(*) FROM public.mv_pemeriksaan WHERE EXTRACT(MONTH FROM tanggal_mulai) BETWEEN 1 AND 6 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY jenis_sarana;
  ```
- **Berapa perbandingan total pemeriksaan dari tahun 2023 sampai dengan Juni tahun 2025**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) >= 2023 AND tgl_start <= '2025-06-30' GROUP BY tahun ORDER BY tahun;
  ```
- **berapa sarana yang diperiksa pada bulan juni 2025**
  ```sql
  SELECT count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(MONTH FROM tanggal_mulai) = 6 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025
  ```
- **berapa sarana yang diperiksa pada bulan juni 2025 per kesimpulannya**
  ```sql
  SELECT kesimpulan, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(MONTH FROM tanggal_mulai) = 6 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY kesimpulan
  ```
- **Berapa total jumlah pemeriksaan pada bulan Agustus 2025?**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(MONTH FROM tgl_start) = 8 AND EXTRACT(YEAR FROM tgl_start) = 2025;
  ```
- **Berapa total jumlah pemeriksaan pada bulan Juni 2025**
  ```sql
  SELECT COUNT(*) FROM public.vw_pemeriksaan_bcc WHERE tgl_start >= '2025-06-01' AND tgl_end <= '2025-06-30';
  ```
- **Berapa total jumlah pemeriksaan per bulan pada 2025?**
  ```sql
  SELECT EXTRACT(MONTH FROM tgl_start) AS bulan, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY bulan ORDER BY bulan;
  ```
- **Berapa total jumlah pemeriksaan untuk bulan agustus 2025?**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) = 8;
  ```
- **Berapa total pemeriksaan di bulan Oktober 2025 Balai besar POM di Bandung?**
  ```sql
  SELECT COUNT(*) FROM public.mv_pemeriksaan WHERE EXTRACT(MONTH FROM tanggal_mulai) = 10 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(nama_upt) LIKE '%balai besar pom di bandung%';
  ```
- **Berapa total pemeriksaan pada bulan Juni 2025?**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE CAST(SUBSTRING(tgl_start, 6, 2) AS INTEGER) = 6 AND CAST(SUBSTRING(tgl_start, 1, 4) AS INTEGER) = 2025;
  ```
- **berapa total pemeriksaan pada bulan mei 2025?**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(MONTH FROM tgl_start) = 5 AND EXTRACT(YEAR FROM tgl_start) = 2025;
  ```
- **Berapa total pemeriksaan yang dilakukan pada bulan Juni 2025**
  ```sql
  SELECT COUNT(*) AS total_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE (tgl_start BETWEEN '2025-06-01' AND '2025-06-30') OR (tgl_end BETWEEN '2025-06-01' AND '2025-06-30');
  ```
- **Berapa total pemeriksaan yang dilakukan pada bulan Juni 2025?**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( MONTH FROM tgl_start ) = 6 AND EXTRACT( YEAR FROM tgl_start ) = 2025;
  ```
- **berapa total sarana yang tutup dan/atau tidak berproduksi saat diperiksa di tahun 2024 di wilayah kerja jakarta utara?**  `[no-sql]`
- **berapa total sarana yang tutup dan/atau tidak berproduksi saat diperiksa di tahun 2025 di wilayah kerja jakarta utara?**
  ```sql
  SELECT COUNT(DISTINCT nama_sarana) FROM public.mv_pemeriksaan WHERE (kesimpulan = 'TTP' OR jenis_sarana NOT ILIKE '%produksi%') AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND kabupaten ILIKE '%jakarta utara%';
  ```
- **berapa untuk tahun 2025?**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS bulan, komoditi, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(komoditi) like '%kosmetik%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1,2,3 ORDER BY 1,2,3;
  ```
- **berdasarkan hasil pemeriksaan sarana, untuk sarana yang tindakannya diamankan ada berapa banyak pada bulan juni 2025**
  ```sql
  SELECT kesimpulan, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(MONTH FROM tanggal_mulai) = 6 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND kesimpulan IS NOT NULL GROUP BY kesimpulan
  ```
- **berikan analisa dari total jumlah pemeriksaan per bulan pada 2025**
  ```sql
  SELECT EXTRACT(MONTH FROM tgl_start) AS bulan, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY bulan ORDER BY bulan;
  ```
- **jmlh pemeriksaan thn 2025**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025;
  ```
- **Pertanyaan:  berapa hasil pemeriksaan sarana pada periode juni 2025**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS BULAN, sarana, kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) = 6 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3, 4 ORDER BY 1, 2, 3, 4;
  ```
- **Pertanyaan:  berapa hasil pemeriksaan sarana sampai akhir juni 2025**  `[no-sql]`
- **Pertanyaan:  berapa jumlah pemeriksaan pangan fortifikasi untuk tahun 2025, detailkan dengan jumlah MK dan TMK nya**
  ```sql
  SELECT kesimpulan, COUNT(*) FROM public.mv_pemeriksaan mp WHERE lower(jenis_sarana) LIKE '%pangan fortifikasi%' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 GROUP BY 1;
  ```
- **Pertanyaan:  berapa jumlah pemeriksaan sarana dari januari sampai september tahun 2025 untuk obat**
  ```sql
  SELECT count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) BETWEEN 1 AND 9 AND lower(komoditi) LIKE '%obat%';
  ```
- **Pertanyaan:  berapa jumlah pemeriksaan sarana per klasifikasi dan hasil pemeriksaan sarana dari januari sampai september tahun 2025 untuk obat**
  ```sql
  SELECT mp.sarana, mp.kesimpulan, COUNT(*) FROM public.mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) BETWEEN 1 AND 9 AND lower(komoditi) LIKE '%obat%' GROUP BY 1, 2;
  ```
- **Pertanyaan:  berapa jumlah pemeriksaan sarana per klasifikasi sarana dari januari sampai september tahun 2025 untuk obat**
  ```sql
  SELECT sarana, COUNT(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) BETWEEN 1 AND 9 AND lower(komoditi) LIKE '%obat%' GROUP BY sarana;
  ```
- **Pertanyaan:  berapa jumlah sarana yang sudah diperiksa pada periode juni 2025**
  ```sql
  SELECT count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(MONTH FROM tanggal_mulai) = 6 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025
  ```
- **Pertanyaan:  berapa jumlah sarana yang sudah diperiksa selama periode januari sampai juni 2025**
  ```sql
  SELECT COUNT(*) FROM public.mv_pemeriksaan WHERE EXTRACT(MONTH FROM tanggal_mulai) BETWEEN 1 AND 6 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Pertanyaan:  berapa jumlah total pemeriksaan pada bulan juni 2025**  `[no-sql]`
- **Pertanyaan:  Berapa jumlah total pemeriksaan pada bulan November 2025?**  `[no-sql]`
- **Pertanyaan:  Berapa jumlah total pemeriksaan pada Januari 2026?**
  ```sql
  SELECT COUNT(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2026 AND EXTRACT(MONTH FROM tanggal_mulai) = 1
  ```
- **Pertanyaan:  Berapa persentase pemeriksaan yang dikategorikan 'Tidak Memenuhi Ketentuan' TMK pada bulan Oktober 2025?**
  ```sql
  SELECT (COUNT(CASE WHEN lower(kesimpulan) = 'tmk' THEN 1 END) * 100.0 / COUNT(*)) AS persentase_tmk FROM mv_pemeriksaan WHERE EXTRACT(MONTH FROM tanggal_mulai) = 10 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Pertanyaan:  berapa total jumlah pemeriksaan sarana pada bulan juli 2025 berdasarkan hasil pemeriksaannya**
  ```sql
  SELECT count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) = 7;
  ```
- **Pertanyaan:  Berapa total pemeriksaan di bulan Oktober 2025?**
  ```sql
  SELECT COUNT(*) FROM public.mv_pemeriksaan WHERE EXTRACT(MONTH FROM tanggal_mulai) = 10 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Pertanyaan:  berapa total pemeriksaan pada bulan september 2025 pada balai pom di jakarta**
  ```sql
  SELECT mp.nama_upt, COUNT(*) AS jumlah FROM mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM mp.tanggal_selesai) = 2025 AND EXTRACT(MONTH FROM mp.tanggal_selesai) = 9 AND LOWER(mp.nama_upt) LIKE '%jakarta%' GROUP BY 1
  ```
- **Pertanyaan:  berapa total pemeriksaan tahun 2025**
  ```sql
  SELECT COUNT(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Pertanyaan:  Berapa total pemeriksaan yang dilakukan pada bulan Oktober 2025?**
  ```sql
  SELECT COUNT(id) FROM public.mv_pemeriksaan WHERE EXTRACT(MONTH FROM tanggal_mulai) = 10 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Pertanyaan:  berapa total sarana yang sudah diperiksa selama periode januari sampai september 2025**
  ```sql
  SELECT COUNT(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) BETWEEN 1 AND 9;
  ```
- **Pertanyaan:  berapa total sarana yang tutup dan/atau tidak berproduksi saat diperiksa di tahun 2024 di wilayah kerja jakarta utara?**
  ```sql
  SELECT kabupaten_kota, nama_sarana, tanggal_mulai, kesimpulan FROM public.mv_pemeriksaan WHERE kesimpulan = 'TTP' AND lower(sarana) LIKE '%produksi%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND lower(kabupaten_kota) ILIKE '%jakarta utara%';
  ```
- **Pertanyaan:  berikan total pemeriksaan tahun 2025**
  ```sql
  SELECT COUNT(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Pertanyaan:  total pemeriksaan sarana yang sudah ada kesimpulannya dari periode januari sampai juni 2025**  `[no-sql]`
- **Pertanyaan:  tunjukkan total data pemeriksaan sarana di sulawesi tengah untuk periode bulan september 2025**
  ```sql
  SELECT COUNT(*) FROM public.mv_pemeriksaan WHERE LOWER(provinsi) LIKE '%sulawesi tengah%' AND EXTRACT(MONTH FROM tanggal_mulai) = 9 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Saat ini tidak ada data yang tersedia untuk ditampilkan dalam bentuk tabel daftar nama Balai, jumlah total target, dan jumlah total pemeriksaan yang dikelompokkan berdasarkan sarana selama tahun 2025.**
  ```sql
  SELECT nama_balai, count(*), count(*) FROM vw_pemeriksaan_bcc vpb WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY 1;
  ```
- **Tampilkan dalam bentuk tabel daftar nama Balai, jumlah total target, jumlah total pemeriksaan dikelompokkan berdasarkan sarana selma tahun 2024**
  ```sql
  SELECT nama_balai, COUNT(DISTINCT target), COUNT(id) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 GROUP BY nama_balai;
  ```
- **Tampilkan jumlah total sarana MK yang terdaftar di Loka POM Belitung pada Triwulan I 2025.**
  ```sql
  SELECT COUNT(*) FROM public.mv_pemeriksaan mp WHERE lower(mp.kabupaten) LIKE '%belitung%' AND mp.status IN ('VERIFY4', 'VERIFY5', 'VERIFY6', 'VERIFY7', 'FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM mp.tanggal_mulai) IN (1, 2, 3) AND lower(mp.kesimpulan) = 'mk';
  ```
- **Tampilkan total jumlah pemeriksaan pada bulan Juli 2025.**
  ```sql
  SELECT COUNT(*) AS total_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE (tgl_start >= '2025-07-01' AND tgl_start < '2025-08-01') OR (tgl_end >= '2025-07-01' AND tgl_end < '2025-08-01');
  ```
- **Tampilkan total pemeriksaan kosmetika bulanan pada tahun 2025.**
  ```sql
  SELECT EXTRACT(MONTH FROM tgl_start) AS bulan, COUNT(*) AS total_pemeriksaan FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY bulan ORDER BY bulan;
  ```
- **Tolong buatkan query untuk: Berapa jumlah pemeriksaan pada bulan September 2025?**
  ```sql
  SELECT count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(MONTH FROM tanggal_mulai) = 9 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025
  ```
- **Tolong buatkan query untuk: Berapa total jumlah pemeriksaan pada bulan September 2025?**
  ```sql
  SELECT COUNT(*) FROM public.mv_pemeriksaan WHERE EXTRACT(MONTH FROM tanggal_mulai) = 9 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Tolong buatkan query untuk: berapa total sarana tahun 2024**
  ```sql
  SELECT COUNT(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024;
  ```
- **Tolong buatkan query untuk: berapa total sarana yang tutup dan/atau tidak berproduksi saat diperiksa di tahun 2024 di wilayah kerja jakarta utara?**
  ```sql
  SELECT nama_sarana, tanggal_mulai, kesimpulan FROM public.mv_pemeriksaan WHERE kesimpulan = 'TTP' AND lower(nama_sarana) LIKE '%produksi%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND lower(kabupaten) ILIKE '%jakarta utara%'
  ```
- **Tolong buatkan query untuk: berapa total sarana yang tutup dan/atau tidak berproduksi saat diperiksa di tahun 2024?**
  ```sql
  SELECT COUNT(nama_sarana) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND (kesimpulan = 'TTP' OR lower(sarana) LIKE '%produksi%');
  ```
- **Tunjukkan data jumlah staf inspektur BPOM selama Oktober 2025 dan beberapa bulan terakhir.**
  ```sql
  SELECT COUNT(DISTINCT petugas) FROM public.mv_pemeriksaan_petugas mp JOIN public.mv_pemeriksaan mpp ON mp.id_pemeriksaan = mpp.id WHERE EXTRACT(YEAR FROM mpp.tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM mpp.tanggal_mulai) <= 10;
  ```
- **Tunjukkan perubahan anggaran operasional atau pendanaan untuk kegiatan pemeriksaan BPOM selama Oktober 2025 dan beberapa bulan terakhir.**  `[no-sql]`
- **Tunjukkan perubahan regulasi yang mempengaruhi jumlah pemeriksaan BPOM selama Oktober 2025 dan beberapa bulan terakhir.**
  ```sql
  SELECT tanggal_mulai, tujuan_pemeriksaan, COUNT(*) AS jumlah_pemeriksaan FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) <= 10 GROUP BY tanggal_mulai, tujuan_pemeriksaan ORDER BY tanggal_mulai DESC;
  ```

### Jumlah total pemeriksaan — 10 pertanyaan

**SQL template warehouse (kanonik):**
```sql
SELECT COUNT(DISTINCT id) FROM mv_pemeriksaan
WHERE tanggal_mulai >= '2015-01-01'
  AND nama_upt NOT IN ('DEMO BALAI BESAR','DEMO TIPE A');
```
*Total nasional. Selalu filter outlier tanggal + DEMO.*

- **Berapa jumlah pemeriksaan dengan kesimpulan TMK untuk kategori produk KOSMETIK?**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE lower(komoditi) LIKE 'kosmetik' AND lower(kesimpulan) LIKE 'tmk';
  ```
- **Berapa jumlah pemeriksaan untuk yang memiliki durasi lebih dari 3 hari?**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE tgl_end - tgl_start > 3
  ```
- **berapa jumlah pemeriksaan yang dilakukan oleh Balai Besar POM di Bandung**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE nama_balai LIKE '%Bandung%'
  ```
- **Berapa jumlah sarana yang memenuhi ketentuan?**
  ```sql
  SELECT count(*) FROM vw_pemeriksaan_bcc WHERE kesimpulan = 'MK'
  ```
- **berapa total jumlah pemeriksaan**
  ```sql
  SELECT COUNT(id) AS total_pemeriksaan FROM public.vw_pemeriksaan_bcc;
  ```
- **berapa total pemeriksaan**
  ```sql
  SELECT COUNT(id) AS total_pemeriksaan FROM public.vw_pemeriksaan_bcc;
  ```
- **jadi data berapa yang ada kalau begitu?**  `[no-sql]`
- **Pertanyaan:  Berapa banyak pemeriksaan untuk kategori 'PRODUK PANGAN' yang ditemukan Tidak Memenuhi Ketentuan TMK?**  `[no-sql]`
- **Pertanyaan:  Berapa waktu yang dibutuhkan untuk pelaporan di Loka Banggai?**
  ```sql
  WITH reporting_times AS ( SELECT mpl.id_pemeriksaan, MIN(mpl.created_at) AS start_time, MAX(mpl.created_at) AS end_time FROM public.mv_pemeriksaan_log mpl JOIN public.mv_pemeriksaan mp ON mpl.id_pemeriksaan = mp.id WHERE lower(mp.nama_upt) LIKE '%loka banggai%' GROUP BY mpl.id_pemeriksaan ) SELECT rt.id_pemeriksaan, rt.start_time, rt.end_time, rt.end_time - rt.start_time AS reporting_duration FROM reporting_times rt;
  ```
- **tunjukkan total pemeriksaan**
  ```sql
  SELECT COUNT(id) AS total_pemeriksaan FROM public.vw_pemeriksaan_bcc;
  ```

### Detail/list (tampilkan) — 102 pertanyaan

**SQL template warehouse (kanonik):**
```sql
SELECT id, nama_sarana, komoditi, kesimpulan, tanggal_mulai, tanggal_selesai
FROM mv_pemeriksaan
WHERE kesimpulan = 'TMK' AND sarana = 'PRODUKSI'
  AND tanggal_mulai >= '2025-01-01' AND tanggal_mulai < '2026-01-01'
LIMIT 20;
```
*User paling banyak minta TAMPILKAN (list). Sertakan kolom identitas + filter DEFAULT.*

- **"tampilkan analisis pemenuhan siklus inspeksi/frekuensi inspeksi masing-masing if maupun seluruh if, dengan menampilkan data dalam bentuk tabel berdasarkan inspeksi sebelumnya atas pemenuhan siklus (steril 2 tahun dan nonsteril 3 tahun), serta menampilkan yang telah terpenuhi dan belum terpenuhi pada masing-masing sertifikat."**  `[no-sql]`
- **"tampilkan daftar sarana dengan hasil tmk berulang lebih dari sekali pada kurun 5 tahun terakhir hingga saat ini pada wilayah kerja balai pom di tangerang"**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE nama_balai = 'Balai POM di Tangerang' AND tgl_start >= NOW() - INTERVAL '5 year' AND kesimpulan = 'TMK' GROUP BY nama_sarana HAVING COUNT(*) > 1;
  ```
- **"tampilkan dashboard data uji petik pada balai pom di jakarta pada rentang waktu 1 januari 2023 hingga 31 desember 2023"**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE nama_balai LIKE '%jakarta%' AND tgl_start BETWEEN '2023-01-01' AND '2023-12-31';
  ```
- **'Tolong buatkan query untuk: 'Berikan 5000 data pemeriksaan, select * limit 5000**
  ```sql
  SELECT * FROM mv_pemeriksaan LIMIT 5000
  ```
- **apa yang dapat kamu bantu coba sebutkan**  `[no-sql]`
- **Berikan 10 pemeriksaan pada tahun 2025**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 LIMIT 10;
  ```
- **Berikan 100 pemeriksaan pada tahun 2025**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 LIMIT 100;
  ```
- **Berikan 1000 pemeriksaan pada tahun 2025**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 LIMIT 1000;
  ```
- **Berikan 10000 pemeriksaan pada tahun 2025**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 LIMIT 10000;
  ```
- **Berikan 2 pemeriksaan pada tahun 2025**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 LIMIT 2;
  ```
- **Berikan 200 pemeriksaan pada tahun 2025**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 LIMIT 200;
  ```
- **Berikan 5000 data pemeriksaan, select * limit 5000**
  ```sql
  SELECT * FROM mv_pemeriksaan LIMIT 5000
  ```
- **Berikan daftar pemeriksaan pada tahun 2025**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025
  ```
- **Berikan daftar sarana berdasarkan klasifikasi.**
  ```sql
  SELECT klasifikasi FROM vw_pemeriksaan_bcc GROUP BY klasifikasi
  ```
- **berikan jumlah pemeriksaan untuk Jawa Tengah, DKI Jakarta, Jawa Barat, Kalimantan Timur**
  ```sql
  SELECT provinsi, COUNT(id) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE provinsi IN ('Jawa Tengah', 'DKI Jakarta', 'Jawa Barat', 'Kalimantan Timur') GROUP BY provinsi;
  ```
- **berikan jumlah pemeriksaan untuk Jawa Tengah, DKI Jakarta, Jawa Barat, Kalimantan Timur tahun 2025**
  ```sql
  SELECT COUNT(CASE WHEN provinsi = 'Jawa Tengah' THEN id ELSE NULL END) AS "Jawa Tengah", COUNT(CASE WHEN provinsi = 'DKI Jakarta' THEN id ELSE NULL END) AS "DKI Jakarta", COUNT(CASE WHEN provinsi = 'Jawa Barat' THEN id ELSE NULL END) AS "Jawa Barat", COUNT(CASE WHEN provinsi = 'Kalimantan Timur' THEN id ELSE NULL END) AS "Kalimantan Timur" FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) = 2025;
  ```
- **Berikan list pemeriksaan pada tahun 2025**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY tahun ORDER BY tahun;
  ```
- **Berikan list semua pemeriksaan pada tahun 2025**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025;
  ```
- **berikan semua list pemeriksaan tahun 2024**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024;
  ```
- **berikan semua list pemeriksaan tahun 2025**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025;
  ```
- **Daftar inisiatif kesehatan masyarakat yang terkait dengan PT Dexa Medica pada periode pengawasan 2024.**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(nama_sarana) LIKE '%dexa medica%';
  ```
- **Daftar semua sarana di Surabaya yang dikategorikan sebagai 'produksi obat' dan riwayat kepatuhan regulasinya di tahun 2024.**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(jenis_sarana) ILIKE 'produksi' AND lower(nama_balai) LIKE '%surabaya%'
  ```
- **Daftarkan semua 'commodity type' yang diuji dalam 'BCC examination' pada tahun 2025.**
  ```sql
  SELECT DISTINCT komoditi FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025
  ```
- **Daftarkan semua pemeriksaan BCC yang terkait dengan CV Sinar Intan Raya di tahun 2024.**
  ```sql
  SELECT nama_sarana, lower(jenis_sarana), lower(komoditi), tujuan, kesimpulan, count(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND LOWER(nama_sarana) LIKE '%sinar intan raya%' GROUP BY nama_sarana , lower(jenis_sarana) , lower(komoditi) , tujuan , kesimpulan
  ```
- **pada periode juni 2025 tidakan apa saja yg diberikan pada hasil pemeriksaan sarana**
  ```sql
  SELECT kesimpulan, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(MONTH FROM tanggal_mulai) = 6 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND kesimpulan IS NOT NULL GROUP BY kesimpulan;
  ```
- **Pertanyaan:  pada periode juni 2025 tidakan apa saja yg diberikan pada hasil pemeriksaan sarana**  `[no-sql]`
- **Pertanyaan:  tampilkan daftar sarana dengan hasil tmk berulang lebih dari sekali pada kurun 5 tahun terakhir hingga saat ini pada wilayah kerja balai pom di tangerang**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, mp.nama_sarana, mp.sarana, kabupaten_kota, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.kabupaten_kota) LIKE '%tangerang%' AND mp.tanggal_mulai >= (CURRENT_DATE - INTERVAL '5 years') AND lower(mp.kesimpulan) LIKE '%tmk%' GROUP BY 1, 2, 3, 4, 5 HAVING COUNT(*) > 1 ORDER BY 1, 2, 3, 4, 5;
  ```
- **Pertanyaan:  tampilkan data pengawasan obat tahun 2024 di wilayah yogyakarta**
  ```sql
  SELECT EXTRACT(MONTH FROM mp.tanggal_mulai), sarana, komoditi, kesimpulan, count(nama_sarana) FROM public.mv_pemeriksaan mp WHERE (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2024 GROUP BY 1, 2, 3, 4;
  ```
- **Pertanyaan:  Tampilkan data realisasi inspeksi pada tahun 2025 yang dilaksanakan oleh pusat maupun UPT secara mandiri**
  ```sql
  select mp.nama_upt, sarana, mp.komoditi, count(*) from mv_pemeriksaan mp where extract(year from mp.tanggal_mulai) = 2025 group by 1, 2, 3 order by 1, 3, 3
  ```
- **Pertanyaan:  tampilkan jumlah pemeriksaan sarana untuk tahun 2025**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY 1 ORDER BY 1;
  ```
- **Pertanyaan:  tampilkan jumlah sarana yang tidak dapat diperiksa di wilayah upt surabaya dan pada tahun 2025**
  ```sql
  SELECT count(*) FROM public.mv_pemeriksaan WHERE kabupaten_kota ILIKE '%surabaya%' AND kesimpulan = 'TDP' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Pertanyaan:  tampilkan perbandingan jumlah sarana mk dibanding jumlah keseluruhan sarana yang diperiksa pada loka pom di kab. belitung pada triwulan i tahun 2025 dalam bentuk angka dan presentase.**
  ```sql
  SELECT COUNT(*) AS total_sarana, COUNT(CASE WHEN lower(mp.kesimpulan) = 'mk' THEN 1 END) AS jumlah_sarana_mk, CAST( COUNT(CASE WHEN lower(mp.kesimpulan) = 'mk' THEN 1 END) AS NUMERIC ) * 100 / COUNT(*) AS persentase_mk FROM public.mv_pemeriksaan mp WHERE lower(mp.kabupaten_kota) LIKE '%belitung%' AND mp.status IN ('VERIFY4', 'VERIFY5', 'VERIFY6', 'VERIFY7', 'FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM mp.tanggal_mulai) IN (1, 2, 3);
  ```
- **Pertanyaan:  tampilkan perbandingan jumlah sarana tmk dibanding jumlah keseluruhan sarana yang diperiksa loka pom di kab. belitung pada triwulan i tahun 2025 dalam bentuk angka dan presentase**
  ```sql
  SELECT COUNT(*) AS total_sarana, COUNT(CASE WHEN lower(mp.kesimpulan) = 'tmk' THEN 1 END) AS jumlah_sarana_tmk, CAST( COUNT(CASE WHEN lower(mp.kesimpulan) = 'tmk' THEN 1 END) AS NUMERIC ) * 100 / COUNT(*) AS persentase_tmk FROM public.mv_pemeriksaan mp WHERE lower(mp.kabupaten_kota) LIKE '%belitung%' AND mp.status IN ('VERIFY4', 'VERIFY5', 'VERIFY6', 'VERIFY7', 'FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM mp.tanggal_mulai) IN (1, 2, 3);
  ```
- **Sebutkan riwayat pemeriksaan balai besar POM di Bandung pada tahun 2024 ?**
  ```sql
  SELECT mp.nama_upt, tanggal_mulai, nama_sarana, jenis_sarana, kesimpulan FROM public.mv_pemeriksaan mp WHERE lower(nama_upt) LIKE '%bandung%' AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2024 AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ORDER BY 1, 2, 3, 4;
  ```
- **Sebutkan riwayat pemeriksaan balai Semarang pada tahun 2024?**
  ```sql
  SELECT nama_sarana, lower(jenis_sarana), lower(komoditi), tujuan, kesimpulan, count(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND LOWER(nama_sarana) LIKE '%semarang%' GROUP BY nama_sarana , lower(jenis_sarana) , lower(komoditi) , tujuan , kesimpulan
  ```
- **Sebutkan riwayat pemeriksaan balai Surabaya pada tahun 2024**
  ```sql
  SELECT nama_sarana, lower(jenis_sarana), lower(komoditi), tujuan, kesimpulan, count(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND LOWER(nama_balai) LIKE '%surabaya%' GROUP BY nama_sarana , lower(jenis_sarana) , lower(komoditi) , tujuan , kesimpulan
  ```
- **selain mv_pemeriksaan_petugas ada tabel apa saja? dan dalam tabelnya ada kolom apa saja? bisa sebutkan?**
  ```sql
  SELECT 'mv_pemeriksaan' AS table_name, column_name FROM information_schema.columns WHERE table_name = 'mv_pemeriksaan' UNION ALL SELECT 'mv_pemeriksaan_petugas' AS table_name, column_name FROM information_schema.columns WHERE table_name = 'mv_pemeriksaan_petugas' UNION ALL SELECT 'mv_pemeriksaan_log' AS table_name, column_name FROM information_schema.columns WHERE table_name = 'mv_pemeriksaan_log' UNION ALL SELECT 'mv_pemeriksaan_temuan' AS table_name, column_name FROM information_schema.columns WHERE table_name = 'mv_pemeriksaan_temuan';
  ```
- **tampilkan analisis pemenuhan siklus inspeksi/frekuensi inspeksi masing-masing if maupun seluruh if, dengan menampilkan data dalam bentuk tabel berdasarkan inspeksi sebelumnya atas pemenuhan siklus (steril 2 tahun dan nonsteril 3 tahun), serta menampilkan yang telah terpenuhi dan belum terpenuhi pada masing-masing sertifikat.**  `[no-sql]`
- **Tampilkan beban kerja personel yang terlibat dalam pembuatan laporan pemeriksaan untuk Balai POM di Bogor di Q1 2025.**
  ```sql
  SELECT mpl.fullname, COUNT(DISTINCT mp.id) AS jumlah_laporan FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_log AS mpl ON mp.id = mpl.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%balai pom di bogor%' AND EXTRACT(YEAR FROM mpl.created_at) = 2025 AND EXTRACT(MONTH FROM mpl.created_at) IN (1, 2, 3) GROUP BY mpl.fullname ORDER BY jumlah_laporan DESC;
  ```
- **tampilkan daftar sarana dengan hasil tmk berulang lebih dari sekali pada kurun 5 tahun terakhir hingga saat ini pada wilayah kerja balai pom di tangerang**
  ```sql
  SELECT nama_sarana FROM public.mv_pemeriksaan WHERE kesimpulan = 'TMK' AND kabupaten ILIKE '%tangerang%' AND tanggal_mulai >= ( SELECT (CURRENT_DATE - INTERVAL '5 year') ) GROUP BY nama_sarana HAVING COUNT(CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE NULL END) > 1;
  ```
- **Tampilkan daftar sarana dengan hasil TMK berulang pada kurun 5 tahun terakhir pada wilayah kerja Balai POM di Tangerang**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE nama_balai = 'Balai POM di Tangerang' AND kesimpulan = 'TMK' AND tgl_start >= DATE(NOW() - INTERVAL '5 year') GROUP BY nama_sarana HAVING COUNT(*) > 1;
  ```
- **tampilkan dashboard data uji petik pada balai pom di jakarta pada rentang waktu 1 januari 2025 hingga 31 desember 2025**  `[no-sql]`
- **Tampilkan dashboard data uji petik pada Balai Surabaya pada rentang waktu 2024-2025**
  ```sql
  SELECT nama_balai, count(*) FROM vw_pemeriksaan_bcc vpb WHERE lower(nama_balai) LIKE '%surabaya%' AND EXTRACT(YEAR FROM tgl_start) BETWEEN 2024 AND 2025 GROUP BY 1
  ```
- **tampilkan data keracunan MBG di sulawesi tengah selama bulan oktober 2025**
  ```sql
  SELECT * FROM public.mv_pemeriksaan WHERE LOWER(provinsi) LIKE '%sulawesi tengah%' AND EXTRACT(MONTH FROM tanggal_mulai) = 10 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND LOWER(tujuan_pemeriksaan) LIKE '%keracunan MBG%'
  ```
- **Tampilkan data pemeriksaan Balai Surabaya pada rentang waktu 2022, 2023, 2024 dan 2025**
  ```sql
  SELECT nama_balai, EXTRACT(YEAR FROM tgl_start), count(*) FROM vw_pemeriksaan_bcc vpb WHERE lower(nama_balai) LIKE '%surabaya%' AND EXTRACT(YEAR FROM tgl_start) IN (2022, 2023, 2024, 2025) GROUP BY 1,2
  ```
- **tampilkan data pemeriksaan dengan tgl_end lebih dari 1 agustus 2025**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE tgl_end > '2025-08-01'
  ```
- **tampilkan data persentase ketepatan tindaklanjut produk dari hasil pemeriksaan oleh upt.**  `[no-sql]`
- **tampilkan data persentase ketepatan tindaklanjut sarana hasil dari pemeriksaan oleh upt.**
  ```sql
  SELECT nama_upt, COUNT(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE NULL END) * 100.0 / COUNT(*) AS persentase_ketepatan_tindaklanjut FROM mv_pemeriksaan WHERE nama_upt IS NOT NULL GROUP BY nama_upt ORDER BY nama_upt;
  ```
- **tampilkan data uji petik pada balai pom di jakarta pada rentang waktu 1 januari 2023 sampai 31 desember 2023.**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE nama_balai LIKE '%Jakarta%' AND tgl_start BETWEEN '2023-01-01' AND '2023-12-31';
  ```
- **tampilkan data uji petik pada balai pom di jakarta pada rentang waktu 1 januari 2025 sampai 31 desember 2025.**  `[no-sql]`
- **Tampilkan data uji petik pada Balai Semarang pada rentang waktu 2024**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(nama_balai) LIKE '%semarang%'
  ```
- **Tampilkan durasi setiap proses pelaporan hasil pemeriksaan untuk Balai POM di Bogor di Q1 2025.**
  ```sql
  WITH laporan_q1_2025 AS ( -- Langkah 1: Ambil data tanggal penting dari Balai POM di Bogor di Q1 2025 SELECT mp.nama_upt, mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 2) AS tanggal_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS tanggal_pelaporan FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_log AS mpl ON mp.id = mpl.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%balai pom di bogor%' AND EXTRACT(YEAR FROM mpl.created_at) = 2025 AND EXTRACT(MONTH FROM mpl.created_at) IN (1, 2, 3) -- Q1 (Januari, Februari, Maret) GROUP BY 1, 2 ) -- Langkah 2: Hitung durasi pelaporan SELECT id_pemeriksaan, tanggal_pemeriksaan, tanggal_pelaporan, (tanggal_pelaporan - tanggal_pemeriksaan) AS durasi_pelaporan FROM laporan_q1_2025 WHERE tanggal_pemeriksaan IS NOT NULL AND tanggal_pelaporan IS NOT NULL;
  ```
- **Tampilkan fasilitas distribusi kosmetik di Surabaya.**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND lower(komoditi) LIKE 'kosmetik' AND lower(kabupaten) LIKE 'kota surabaya' GROUP BY nama_sarana;
  ```
- **Tampilkan fasilitas yang memiliki riwayat ketidakpatuhan.**
  ```sql
  SELECT count(*) FROM vw_pemeriksaan_bcc WHERE kesimpulan = 'TMK'
  ```
- **Tampilkan hasil pemeriksaan BCC untuk fasilitas di Surabaya.**
  ```sql
  SELECT nama_balai, count(*) FROM vw_pemeriksaan_bcc vpb WHERE lower(nama_balai) LIKE '%surabaya%' GROUP BY 1
  ```
- **Tampilkan hasil pemeriksaan BCC untuk PT Dexa Medica pada periode pengawasan 2024.**
  ```sql
  SELECT nama_sarana, lower(jenis_sarana), lower(komoditi), tujuan, kesimpulan, count(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND LOWER(nama_sarana) LIKE '%dexa medica%' GROUP BY nama_sarana , lower(jenis_sarana) , lower(komoditi) , tujuan , kesimpulan ;
  ```
- **Tampilkan jumlah keseluruhan sarana yang diperiksa di Loka POM Belitung pada Triwulan I 2025.**
  ```sql
  SELECT COUNT(*) AS total_sarana FROM public.mv_pemeriksaan mp WHERE lower(mp.kabupaten) LIKE '%belitung%' AND mp.status IN ('VERIFY4', 'VERIFY5', 'VERIFY6', 'VERIFY7', 'FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM mp.tanggal_mulai) IN (1, 2, 3);
  ```
- **Tampilkan jumlah pegawai yang terlibat dalam proses pelaporan hasil pemeriksaan di Balai POM di Bogor pada TW 1 2025.**
  ```sql
  WITH laporan_q1_2025 AS ( SELECT mp.nama_upt, mpl.id_pemeriksaan, mpl.created_at, mpp.petugas FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_log AS mpl ON mp.id = mpl.id_pemeriksaan LEFT JOIN public.mv_pemeriksaan_petugas AS mpp ON mp.id = mpp.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%balai pom di bogor%' AND EXTRACT(YEAR FROM mpl.created_at) = 2025 AND EXTRACT(MONTH FROM mpl.created_at) IN (1, 2, 3) AND mpl.urutan_step = 3 -- Filter for reporting step ) SELECT count(DISTINCT petugas) FROM laporan_q1_2025;
  ```
- **Tampilkan jumlah pemeriksaan di bulan Juli 2025 berdasarkan hasil.**
  ```sql
  SELECT COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE (tgl_start >= '2025-07-01' AND tgl_start < '2025-08-01') OR (tgl_end >= '2025-07-01' AND tgl_end < '2025-08-01');
  ```
- **tampilkan jumlah pemeriksaan sarana untuk tahun sebelumnya**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 GROUP BY 1 ORDER BY 1;
  ```
- **tampilkan jumlah pemeriksaan sarana untuk tahun sebelumnya?**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 GROUP BY 1 ORDER BY 1;
  ```
- **tampilkan jumlah pemeriksaan tidak memenuhi ketentuan tahun 2024**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND kesimpulan = 'TMK';
  ```
- **Tampilkan jumlah pemeriksaan untuk Juli 2025.**
  ```sql
  SELECT COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE (tgl_start BETWEEN '2025-07-01' AND '2025-07-31') OR (tgl_end BETWEEN '2025-07-01' AND '2025-07-31');
  ```
- **Tampilkan jumlah sarana MK yang diperiksa di Loka POM Belitung pada Triwulan I 2025.**
  ```sql
  SELECT COUNT(CASE WHEN lower(mp.kesimpulan) = 'mk' THEN 1 END) AS jumlah_sarana_mk FROM public.mv_pemeriksaan mp WHERE lower(mp.nama_upt) LIKE '%belitung%' AND mp.status IN ('VERIFY4', 'VERIFY5', 'VERIFY6', 'VERIFY7', 'FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM mp.tanggal_mulai) IN (1, 2, 3);
  ```
- **tampilkan jumlah sarana yang memenuhi ketentuan di wilayah upt surabaya dan pada tahun 2025.**
  ```sql
  SELECT COUNT(nama_sarana) FROM public.mv_pemeriksaan WHERE nama_upt ILIKE '%surabaya%' AND kesimpulan = 'MK' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **tampilkan jumlah sarana yang tidak dapat diperiksa di wilayah upt surabaya dan pada tahun 2025**
  ```sql
  SELECT COUNT(DISTINCT nama_sarana) FROM public.mv_pemeriksaan WHERE nama_upt ILIKE '%surabaya%' AND kesimpulan = 'TDP' AND EXTRACT( YEAR FROM tanggal_mulai ) = 2025;
  ```
- **tampilkan jumlah sarana yang tidak memenuhi ketentuan di wilayah upt surabaya dan pada tahun 2025**
  ```sql
  SELECT COUNT(nama_sarana) FROM public.mv_pemeriksaan WHERE kesimpulan = 'TMK' AND nama_upt ILIKE '%surabaya%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Tampilkan kesimpulan dan hasil pemeriksaan untuk CV Sinar Intan Raya di tahun 2024.**
  ```sql
  SELECT kesimpulan, count(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND LOWER(nama_sarana) LIKE '%cv sinar intan raya%' GROUP BY kesimpulan;
  ```
- **Tampilkan kesimpulan pemeriksaan dan detail hasilnya.**
  ```sql
  SELECT kesimpulan, nama_sarana, provinsi, kabupaten, nama_balai, jenis_sarana, komoditi, tujuan, tgl_start, tgl_end FROM vw_pemeriksaan_bcc
  ```
- **Tampilkan metrik kepatuhan regulasi untuk PT Dexa Medica pada periode pengawasan 2024.**
  ```sql
  SELECT nama_sarana, lower(jenis_sarana), lower(komoditi), tujuan, kesimpulan, count(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND LOWER(nama_sarana) LIKE '%dexa medica%' GROUP BY nama_sarana , lower(jenis_sarana) , lower(komoditi) , tujuan , kesimpulan
  ```
- **tampilkan nama produk kosmetik TMS pada periode bulan juli 2025**
  ```sql
  SELECT nama_produk FROM vw_pengujian_bcc WHERE kesimpulan_akhir = 'TMS' AND EXTRACT(MONTH FROM tglsampling) = 7 AND EXTRACT(YEAR FROM tglsampling) = 2025
  ```
- **Tampilkan pemeriksaan sarana dengan hasil tidak memenuhi ketentuan tahun 2024 berdasarkan kategori kedaluarsa.**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND kesimpulan = 'TMK' AND lower(kategori_temuan) LIKE '%kedaluarsa%';
  ```
- **Tampilkan pemeriksaan sarana dengan hasil tidak memenuhi ketentuan tahun 2024 berdasarkan kategori mengandung bahan berbahaya/ dilarang.**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND kesimpulan = 'TMK' AND lower(kategori) LIKE '%bahan berbahaya/ dilarang%';
  ```
- **tampilkan perbandingan jumlah sarana mk dibanding jumlah keseluruhan sarana yang diperiksa pada loka pom di kab. belitung pada triwulan i tahun 2025 dalam bentuk angka dan presentase.**
  ```sql
  SELECT COUNT(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE NULL END) AS jumlah_mk, COUNT(*) AS jumlah_total, CASE WHEN COUNT(*) = 0 THEN 0 ELSE CAST(COUNT(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE NULL END) AS NUMERIC) / CAST(COUNT(*) AS NUMERIC) * 100 END AS presentase FROM public.vw_pemeriksaan_bcc WHERE kabupaten = 'Kab. Belitung' AND tgl_start BETWEEN '2025-01-01' AND '2025-03-31';
  ```
- **tampilkan perbandingan jumlah sarana tmk dibanding jumlah keseluruhan sarana yang diperiksa loka pom di kab. belitung pada triwulan i tahun 205 dalam bentuk angka dan presentase**
  ```sql
  SELECT COUNT(CASE WHEN kesimpulan = 'TMK' THEN 1 END) AS jumlah_sarana_tmk, COUNT(*) AS jumlah_keseluruhan_sarana, CASE WHEN COUNT(*) = 0 THEN 0 ELSE CAST(COUNT(CASE WHEN kesimpulan = 'TMK' THEN 1 END) AS NUMERIC) * 100 / COUNT(*) END AS presentase FROM public.vw_pemeriksaan_bcc WHERE kabupaten = 'Kab. Belitung' AND EXTRACT(QUARTER FROM tgl_start) = 1 AND EXTRACT(YEAR FROM tgl_start) = 2015;
  ```
- **Tampilkan periode waktu pemeriksaan.**
  ```sql
  SELECT tgl_start, tgl_end FROM public.vw_pemeriksaan_bcc
  ```
- **Tampilkan rata-rata durasi proses pelaporan hasil pemeriksaan oleh Balai POM di Bogor pada TW 1 2025.**
  ```sql
  WITH laporan_q1_2025 AS ( SELECT mp.nama_upt, mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 2) AS tanggal_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS tanggal_pelaporan FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_log AS mpl ON mp.id = mpl.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%balai pom di bogor%' AND EXTRACT(YEAR FROM mpl.created_at) = 2025 AND EXTRACT(MONTH FROM mpl.created_at) IN (1, 2, 3) GROUP BY 1, 2 ) SELECT AVG(tanggal_pelaporan - tanggal_pemeriksaan) AS rata_rata_durasi FROM laporan_q1_2025 WHERE tanggal_pemeriksaan IS NOT NULL AND tanggal_pelaporan IS NOT NULL;
  ```
- **tampilkan rekapitulasi produktivitas penguji (jumlah parameter per orang) dari tanggal 1 januari 2025 hingga 31 desember 2025.**  `[no-sql]`
- **tampilkan riwayat pemeriksaan untuk CV Sinar Intan Raya**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE LOWER(nama_sarana) LIKE '%sinar intan raya%'
  ```
- **tampilkan riwayat pemeriksaan untuk PT Alfa Viva Famili**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE LOWER(nama_sarana) LIKE '%alfa viva famili%'
  ```
- **tampilkan riwayat pemeriksaan untuk PT Ozthetique Medika Indoneisa**
  ```sql
  SELECT nama_sarana, jenis_sarana, komoditi, tujuan, kesimpulan FROM public.vw_pemeriksaan_bcc WHERE LOWER(nama_sarana) LIKE '%pt ozthetique medika indoneisa%'
  ```
- **tampilkan riwayat pemeriksaan untuk PT Ozthetique Medika Indonesia**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE lower(nama_sarana) LIKE '%pt ozthetique medika indonesia%';
  ```
- **tampilkan riwayat pemeriksaan untuk PT Qiqi Kosmetik Indonesia**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE LOWER(nama_sarana) LIKE '%qiqi kosmetik indonesia%'
  ```
- **Tampilkan semua faktor yang mempengaruhi 'Cakupan Pengawasan' dalam konteks produk kosmetik.**
  ```sql
  SELECT DISTINCT mp.tujuan_pemeriksaan, mp.komoditi, mp.kesimpulan, mp.sarana, mpt.tp_pelanggaran, mpt.tp_kategori, mpt.tp_tindakan FROM public.mv_pemeriksaan mp LEFT JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.komoditi) LIKE '%kosmetik%'
  ```
- **Tampilkan tanggal pemeriksaan dan tanggal pelaporan untuk semua laporan hasil pemeriksaan yang dilakukan oleh Balai POM di Bogor pada TW 1 2025.**
  ```sql
  WITH laporan_q1_2025 AS ( -- Langkah 1: Ambil data tanggal penting dari Balai POM di Bogor di Q1 2025 SELECT mp.nama_upt, mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 2) AS tanggal_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS tanggal_pelaporan FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_log AS mpl ON mp.id = mpl.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%balai pom di bogor%' AND EXTRACT(YEAR FROM mpl.created_at) = 2025 AND EXTRACT(MONTH FROM mpl.created_at) IN (1, 2, 3) -- Q1 (Januari, Februari, Maret) GROUP BY 1, 2 ) SELECT tanggal_pemeriksaan, tanggal_pelaporan FROM laporan_q1_2025;
  ```
- **Tampilkan waktu penyelesaian laporan pemeriksaan berdasarkan jenis pemeriksaan untuk Balai POM di Bogor di Q1 2025.**
  ```sql
  WITH pemeriksaan_q1_2025 AS ( SELECT mp.jenis_sarana, mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 2) AS tanggal_mulai, MAX(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS tanggal_selesai FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_log AS mpl ON mp.id = mpl.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%balai pom di bogor%' AND EXTRACT(YEAR FROM mpl.created_at) = 2025 AND EXTRACT(MONTH FROM mpl.created_at) IN (1, 2, 3) GROUP BY 1, 2 ) SELECT jenis_sarana, AVG(EXTRACT(EPOCH FROM (tanggal_selesai - tanggal_mulai))) AS avg_waktu_penyelesaian FROM pemeriksaan_q1_2025 GROUP BY jenis_sarana;
  ```
- **tampilkan yang hanya data produsen pangan olahan**
  ```sql
  SELECT mpt.tp_kategori, count(*) AS jumlah_pemeriksaan FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.kesimpulan) = 'tmk' AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND lower(mp.jenis_sarana) LIKE '%pangan olahan%' GROUP BY 1;
  ```
- **Tolong buatkan query untuk: Berikan 5000 data pemeriksaan, select * limit 5000**
  ```sql
  SELECT * FROM mv_pemeriksaan LIMIT 5000;
  ```
- **Tolong buatkan query untuk: tampilkan daftar sarana dengan hasil tmk berulang lebih dari sekali pada kurun 5 tahun terakhir hingga saat ini pada wilayah kerja balai pom di tangerang**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, mp.nama_sarana, mp.sarana, kabupaten_kota, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.kabupaten_kota) LIKE '%tangerang%' AND mp.tanggal_mulai >= (CURRENT_DATE - INTERVAL '5 years') GROUP BY 1, 2, 3, 4, 5 HAVING COUNT(*) > 1 ORDER BY 1, 2, 3, 4, 5;
  ```
- **Tolong buatkan query untuk: tampilkan jumlah sarana yang tidak dapat diperiksa di wilayah upt surabaya dan pada tahun 2025**
  ```sql
  SELECT count(*) FROM public.mv_pemeriksaan WHERE kabupaten_kota ILIKE '%surabaya%' AND kesimpulan = 'TDP' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Tolong buatkan query untuk: tampilkan perbandingan jumlah sarana mk dibanding jumlah keseluruhan sarana yang diperiksa pada loka pom di kab. belitung pada triwulan i tahun 2025 dalam bentuk angka dan presentase.**
  ```sql
  SELECT COUNT(*) AS total_sarana, COUNT(CASE WHEN lower(mp.kesimpulan) = 'mk' THEN 1 END) AS jumlah_sarana_mk, CAST( COUNT(CASE WHEN lower(mp.kesimpulan) = 'mk' THEN 1 END) AS NUMERIC ) * 100 / COUNT(*) AS persentase_mk FROM public.mv_pemeriksaan mp WHERE lower(mp.nama_loka_pom) LIKE '%belitung%' AND mp.status IN ('VERIFY4', 'VERIFY5', 'VERIFY6', 'VERIFY7', 'FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM mp.tanggal_mulai) IN (1, 2, 3);
  ```
- **Tolong buatkan query untuk: tampilkan perbandingan jumlah sarana tmk dibanding jumlah keseluruhan sarana yang diperiksa loka pom di jakarta pada triwulan i tahun 2025 dalam bentuk angka dan presentase**
  ```sql
  SELECT COUNT(*) AS total_sarana, COUNT(CASE WHEN lower(mp.kesimpulan) = 'tmk' THEN 1 END) AS jumlah_sarana_tmk, CAST( COUNT(CASE WHEN lower(mp.kesimpulan) = 'tmk' THEN 1 END) AS NUMERIC ) * 100 / COUNT(*) AS persentase_tmk FROM public.mv_pemeriksaan mp WHERE lower(mp.nama_upt) LIKE '%jakarta%' AND mp.status IN ('VERIFY4', 'VERIFY5', 'VERIFY6', 'VERIFY7', 'FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM mp.tanggal_mulai) IN (1, 2, 3);
  ```
- **Tolong buatkan query untuk: tampilkan perbandingan jumlah sarana tmk dibanding jumlah keseluruhan sarana yang diperiksa loka pom di kab. belitung pada triwulan i tahun 2025 dalam bentuk angka dan presentase**
  ```sql
  SELECT COUNT(*) AS total_sarana, COUNT(CASE WHEN lower(mp.kesimpulan) = 'tmk' THEN 1 END) AS jumlah_sarana_tmk, CAST( COUNT(CASE WHEN lower(mp.kesimpulan) = 'tmk' THEN 1 END) AS NUMERIC ) * 100 / COUNT(*) AS persentase_tmk FROM public.mv_pemeriksaan mp WHERE lower(mp.kabupaten) LIKE '%belitung%' AND mp.status IN ('VERIFY4', 'VERIFY5', 'VERIFY6', 'VERIFY7', 'FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM mp.tanggal_mulai) IN (1, 2, 3);
  ```
- **Tolong buatkan query untuk: tampilkan perbandingan jumlah sarana tmk dibanding jumlah keseluruhan sarana yang diperiksa loka pom di kab. belitung pada triwulan i tahun 205 dalam bentuk angka dan presentase**
  ```sql
  SELECT COUNT(*) AS total_sarana, COUNT(CASE WHEN lower(mp.kesimpulan) = 'tmk' THEN 1 END) AS jumlah_sarana_tmk, CAST( COUNT(CASE WHEN lower(mp.kesimpulan) = 'tmk' THEN 1 END) AS NUMERIC ) * 100 / COUNT(*) AS persentase_tmk FROM public.mv_pemeriksaan mp WHERE lower(mp.kabupaten) LIKE '%belitung%' AND mp.status IN ('VERIFY4', 'VERIFY5', 'VERIFY6', 'VERIFY7', 'FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2005 AND EXTRACT(MONTH FROM mp.tanggal_mulai) IN (1, 2, 3);
  ```
- **Tolong buatkan query untuk: tampilkan rekapitulasi produktivitas penguji jumlah parameter per orang dari tanggal 1 januari 2025 hingga 31 desember 2025.**
  ```sql
  SELECT mpp.petugas, count(*) FROM public.mv_pemeriksaan_petugas mpp WHERE EXTRACT(YEAR FROM mpp.tgl_surat) = 2025 GROUP BY 1 ORDER BY 2 DESC;
  ```
- **tolong tampilkan detail mulai dari nama balai yang melakukan pemeriksaan, sampai rating sarana nay**
  ```sql
  SELECT EXTRACT(MONTH FROM tanggal_mulai) AS bulan, EXTRACT(YEAR FROM tanggal_mulai) AS tahun, jenis_sarana, mp.nama_upt, COUNT(*) FROM mv_pemeriksaan mp WHERE lower(jenis_sarana) LIKE '%pangan md%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) = 1 AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3, 4 ORDER BY 1, 2, 3;
  ```
- **tunjukkan  semua data pemeriksaan pada bulan Agustus 2025?**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) = 8;
  ```
- **Tunjukkan hasil dan kesimpulan pemeriksaan kosmetika bulanan pada tahun 2025.**
  ```sql
  SELECT EXTRACT(MONTH FROM tgl_start) AS bulan, kesimpulan, COUNT(*) AS jumlah_pemeriksaan FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY bulan, kesimpulan ORDER BY bulan, kesimpulan;
  ```
- **tunjukkan jumlah pemeriksaan**
  ```sql
  SELECT COUNT(id) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc;
  ```
- **Tunjukkan metrik kepatuhan regulasi untuk pemeriksaan kosmetika bulanan pada tahun 2025.**
  ```sql
  SELECT EXTRACT(MONTH FROM tgl_start) AS month, COUNT(*) AS total_inspections, SUM(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE 0 END) AS memenuhi_ketentuan, SUM(CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE 0 END) AS tidak_memenuhi_ketentuan FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(komoditi) LIKE '%kosmetika%' GROUP BY EXTRACT(MONTH FROM tgl_start) ORDER BY month;
  ```
- **tunjukkan semua data pemeriksaan pada bulan Juli 2025?**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) = 7;
  ```
- **Tunjukkan semua pemeriksaan pada tahun 2025**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY tahun ORDER BY tahun;
  ```

### Lainnya (meta, ringkasan, uji petik) — 81 pertanyaan

**SQL template warehouse (kanonik):**
```sql
— bervariasi —
```
*Termasuk pertanyaan meta ("bpom itu apa") dan uji petik (cross-domain pengujian).*

- **"sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang belum dilakukan pemeriksaan dalam periode 2 tahun terakhir?"**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE komoditi IN ('Obat Tradisional', 'Suplemen Kesehatan', 'Obat Kuasi') AND tgl_start < NOW() - INTERVAL '2 year' GROUP BY nama_sarana;
  ```
- **"sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang memiliki riwayat pemeriksaan tidak memenuhi ketentuan dalam periode tahun 2023?"**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2023 AND kesimpulan = 'TMK' AND komoditi IN ('Obat Tradisional', 'Suplemen Kesehatan', 'Obat Kuasi') GROUP BY nama_sarana;
  ```
- **"sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang pernah memproduksi dan mengedarkan obat tradisional; suplemen kesehatan; obat kuasi tie dalam periode tahun 2023?"**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE komoditi IN ('Obat Tradisional', 'Suplemen Kesehatan', 'Obat Kuasi') AND EXTRACT(YEAR FROM tgl_start) = 2023 GROUP BY nama_sarana;
  ```
- **analisis data realisasi inspeksi pada periode 2024 yang dilaksanakan oleh pusat**
  ```sql
  SELECT count(*) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024;
  ```
- **Analisis data realisasi inspeksi pada periode waktu 2025 yang dilaksanakan oleh pusat maupun UPT secara mandiri**
  ```sql
  SELECT COUNT(CASE WHEN EXTRACT(YEAR FROM tgl_start) = 2025 THEN id ELSE NULL END) AS total_inspeksi, COUNT(CASE WHEN EXTRACT(YEAR FROM tgl_start) = 2025 AND nama_balai LIKE '%Pusat%' THEN id ELSE NULL END) AS inspeksi_pusat, COUNT(CASE WHEN EXTRACT(YEAR FROM tgl_start) = 2025 AND nama_balai NOT LIKE '%Pusat%' THEN id ELSE NULL END) AS inspeksi_upt FROM public.vw_pemeriksaan_bcc;
  ```
- **analisis jumlah pemeriksaan oleh masing-masing inspektur**
  ```sql
  SELECT petugas, COUNT(id_pemeriksaan) AS jumlah_pemeriksaan FROM public.mv_pemeriksaan_petugas GROUP BY petugas ORDER BY jumlah_pemeriksaan DESC;
  ```
- **apa rincian TMK untuk pemeriksaan 2023 tersebut**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2023 AND kesimpulan = 'TMK'
  ```
- **apa rincian TMK untuk pemeriksaan CV Sinar Intan Raya tahun 2023**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2023 AND LOWER(nama_sarana) LIKE '%cv sinar intan raya%' AND kesimpulan = 'TMK'
  ```
- **Apakah ada data hasil pemeriksaan PT Bina Estetika Indonesia?**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE lower(nama_sarana) LIKE '%bina estetika indonesia%';
  ```
- **Apakah ada data hasil pemeriksaan PT Bina Estetika?**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE lower(nama_sarana) LIKE '%bina estetika%';
  ```
- **Apakah ada data pengawasan penandaan kosmetik?**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE lower(komoditi) LIKE 'kosmetik';
  ```
- **apakah ada nip?**  `[no-sql]`
- **bagaimana hasil pemeriksaan penandaan kosmetik?**
  ```sql
  SELECT kesimpulan FROM vw_pemeriksaan_bcc WHERE lower(komoditi) LIKE 'kosmetik';
  ```
- **Bagaimana perbandingan jumlah pemeriksaan produk pangan yang memenuhi ketentuan (MK) dan tidak memenuhi ketentuan (TMK) pada bulan Juli 2025?**  `[no-sql]`
- **bagaimana rincian hasil pemeriksaan CV Siar Intan Raya tahun 2025**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(nama_sarana) LIKE '%cv siar intan raya%'
  ```
- **bagaimana rincian hasil pemeriksaan CV Sinar Intan Raya tahun 2025**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(nama_sarana) LIKE '%cv sinar intan raya%'
  ```
- **bagaimana riwayat pemeriksaan CV Anare Kemilau Indonesia**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE LOWER(nama_sarana) LIKE '%anare kemilau indonesia%'
  ```
- **Balai mana yang penurunannya signifikan di bulan juli 2025**
  ```sql
  SELECT nama_balai FROM public.vw_pemeriksaan_bcc WHERE (tgl_start BETWEEN '2025-07-01' AND '2025-07-31' OR tgl_end BETWEEN '2025-07-01' AND '2025-07-31') AND kesimpulan = 'MK';
  ```
- **bpom itu apa**
  ```sql
  -- The question asks "bpom itu apa". This cannot be answered with a SQL query against the provided database schema. -- The database contains information about BCC examinations, not a definition of BPOM. -- Returning a query that retrieves data related to "nama_balai" as a proxy, since it's the closest related information available. SELECT DISTINCT nama_balai FROM public.vw_pemeriksaan_bcc;
  ```
- **buatkan juga per tahunnya**  `[no-sql]`
- **buatlah laporan singkat terkait hasil pemeriksaan selama bulan november 2025**
  ```sql
  SELECT * FROM public.mv_pemeriksaan WHERE EXTRACT(MONTH FROM tanggal_mulai) = 11 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025
  ```
- **Cari semua node dan relasi yang terhubung dengan 'Prudential'.**  `[no-sql]`
- **Dari data tersebut breakdown data berdasarkan Sarana yang Memenuhi Ketentuan dan Tidak Memenuhi Ketentuan**
  ```sql
  SELECT kesimpulan, COUNT(*) FROM vw_pemeriksaan_bcc WHERE lower(kesimpulan) like 'mk' or lower(kesimpulan) like 'tmk' GROUP BY 1;
  ```
- **data apa saja yang bisa kamu sediakan?**  `[no-sql]`
- **data detail petugas pengawas 2024 misal ada nip dll**
  ```sql
  SELECT * FROM public.mv_pemeriksaan_petugas WHERE EXTRACT(YEAR FROM tgl_surat) = 2024;
  ```
- **data petugas pengawas 2024**
  ```sql
  SELECT mpp.petugas, count(*) FROM public.mv_pemeriksaan_petugas mpp WHERE EXTRACT(YEAR FROM mpp.tgl_surat) = 2024 GROUP BY 1 ORDER BY 2 DESC;
  ```
- **detail pegawai pengawas yang lengkap ada apa saja?**
  ```sql
  SELECT nomorsurat, tgl_surat, daftar_balai_pemeriksa, petugas FROM public.mv_pemeriksaan_petugas;
  ```
- **hasil pemeriksaan pada bulan april 2025 lengkap dengan jenis klasifikasi sarananya**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS bulan, sarana, jenis_sarana, kesimpulan, COUNT(*) FROM public.mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) = 4 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3, 4, 5 ORDER BY 1, 2, 3, 4, 5;
  ```
- **hasil pemeriksaan sarana pada periode juni 2025 berdasarkan tindak lanjutnya**
  ```sql
  SELECT kesimpulan, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(MONTH FROM tanggal_mulai) = 6 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND kesimpulan IS NOT NULL GROUP BY kesimpulan
  ```
- **Hasil pemeriksaan tahun 2024**
  ```sql
  SELECT EXTRACT(YEAR FROM tgl_start) AS tahun, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 GROUP BY tahun ORDER BY tahun;
  ```
- **Identifikasi hubungan antara 'Penegakan Regulasi' dan 'Insiden Produk Kosmetik Ilegal'.**  `[no-sql]`
- **Ini bulan oktober saja atau data dari januari sampai dengan oktober 2025?**
  ```sql
  SELECT COUNT(id) FROM public.mv_pemeriksaan WHERE EXTRACT(MONTH FROM tanggal_mulai) BETWEEN 1 AND 10 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **itu dalam 1 bulan?**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE tgl_start >= date_trunc('month', CURRENT_DATE) AND tgl_start < date_trunc('month', CURRENT_DATE) + interval '1 month';
  ```
- **jadi belum ada nomor induk pegawai?**  `[no-sql]`
- **jenis pangan apa yang paling banyak diperiksa di bulan tersebut?**
  ```sql
  SELECT komoditi, COUNT(*) AS jumlah_pemeriksaan FROM public.mv_pemeriksaan WHERE lower(jenis_sarana) LIKE '%pangan md%' AND lower(tujuan_pemeriksaan) LIKE '%pemeriksaan rutin%' AND lower(nama_upt) LIKE '%balai besar pom di jakarta%' AND EXTRACT(MONTH FROM tanggal_mulai) = 10 GROUP BY komoditi ORDER BY jumlah_pemeriksaan DESC LIMIT 1;
  ```
- **jenis pangan apa yang paling banyak diperiksa oleh Balai Besar POM di Jakarta?**
  ```sql
  SELECT komoditi, COUNT(*) AS jumlah_pemeriksaan FROM public.vw_pemeriksaan_bcc WHERE lower(nama_balai) LIKE '%jakarta%' GROUP BY komoditi ORDER BY jumlah_pemeriksaan DESC LIMIT 1;
  ```
- **jenis tms apa yang paling banyak ditemukan selama periode tahun 2025?**
  ```sql
  SELECT param_name, count(*) FROM public.mv_sampel_pengujian msp JOIN public.mv_sampel ms ON msp.id_sampling = ms.id_sampling WHERE EXTRACT(YEAR FROM ms.tglsampling) = 2025 AND hasil_uji LIKE '%TMS%' GROUP BY param_name ORDER BY COUNT(*) DESC LIMIT 5;
  ```
- **Jumlah pemeriksaan pada tahun 2024?**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024
  ```
- **jumlah pemeriksaan tahun 2025**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025
  ```
- **jumlah pemeriksaan yang dilakukan di wiliyaha tangerang**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE lower(nama_balai) LIKE '%tangerang%'
  ```
- **kasih aku visualisasi perkembangan jumlah pemeriksaan per bulan tahun 2025**
  ```sql
  SELECT TO_CHAR(tgl_start, 'YYYY-MM') AS bulan, COUNT(id) AS jumlah_pemeriksaan FROM vw_pemeriksaan_bcc WHERE TO_CHAR(tgl_start, 'YYYY') = '2025' GROUP BY bulan ORDER BY bulan;
  ```
- **Kategori kesimpulan apa yang paling sering muncul dalam pemeriksaan?**
  ```sql
  SELECT kesimpulan, COUNT(*) AS jumlah FROM vw_pemeriksaan_bcc GROUP BY kesimpulan ORDER BY jumlah DESC LIMIT 1
  ```
- **kosmetik jenis apa yang TMS?**
  ```sql
  SELECT komoditi FROM public.vw_pemeriksaan_bcc WHERE kesimpulan = 'TMK' GROUP BY komoditi
  ```
- **lengkapi dengan rating pemeriksaan atau hasil balai nya**
  ```sql
  SELECT EXTRACT(MONTH FROM tanggal_mulai) AS bulan, EXTRACT(YEAR FROM tanggal_mulai) AS tahun, jenis_sarana, mp.nama_upt, mp.kesimpulan, COUNT(*) FROM mv_pemeriksaan mp WHERE lower(jenis_sarana) LIKE '%pangan md%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) = 1 AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3, 4, 5 ORDER BY 1, 2, 3;
  ```
- **Pertanyaan:  buatkan Executive Summary untuk pemeriksaan sarana selama periode triwulan 3 tahun 2025**  `[no-sql]`
- **Pertanyaan:  data pemeriksaaan sarana pada periode triwulan 1 tahun 2025 dengan detail hasil pemeriksaan sarananya dan klasifikasi sarananya**
  ```sql
  SELECT mp.sarana, mp.jenis_sarana, mp.kesimpulan FROM public.mv_pemeriksaan mp WHERE EXTRACT(QUARTER FROM tanggal_mulai) = 1 AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Pertanyaan:  data pengawas 2024**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS bulan, kesimpulan, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1,2,3 ORDER BY 1,2,3;
  ```
- **Pertanyaan:  data pengawasan pangan olahan tahun 2024**
  ```sql
  SELECT * FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024;
  ```
- **Pertanyaan:  hasil pemeriksaan pada bulan april 2025**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS BULAN, sarana, kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND EXTRACT(MONTH FROM tanggal_mulai) = 4 AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2, 3, 4 ORDER BY 1, 2, 3, 4;
  ```
- **Pertanyaan:  informasikan riwayat inspeksi first medifarma**  `[no-sql]`
- **Pertanyaan:  jumlah hasil pemeriksaan MK dan TMK sampai akhir bulan juni 2025**  `[no-sql]`
- **Pertanyaan:  jumlah hasil pemeriksaan MK dan TMK sampai akhir triwulan 2**  `[no-sql]`
- **Pertanyaan:  Kesimpulan apa yang paling sering ditemukan dari semua pemeriksaan?**
  ```sql
  SELECT kesimpulan, COUNT(*) AS jumlah FROM mv_pemeriksaan GROUP BY kesimpulan ORDER BY jumlah DESC LIMIT 1;
  ```
- **Pertanyaan:  Pada bulan apa jumlah pemeriksaan mencapai puncaknya?**
  ```sql
  SELECT EXTRACT(MONTH FROM tanggal_periode) AS month, SUM(jumlah_pemeriksaan) AS total_pemeriksaan FROM public.mv_pemeriksaan_agg GROUP BY month ORDER BY total_pemeriksaan DESC LIMIT 1;
  ```
- **Pertanyaan:  Pemeriksaan sarana obat di bandung**
  ```sql
  SELECT * FROM public.mv_pemeriksaan WHERE lower(kabupaten_kota) LIKE '%bandung%'
  ```
- **Pertanyaan:  Sarana apa saja yang pernah diperiksa oleh Badan POM?**
  ```sql
  SELECT DISTINCT (nama_sarana) FROM mv_pemeriksaan WHERE status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED');
  ```
- **Pertanyaan:  sarana mana yang diperiksa tahun 2025**
  ```sql
  SELECT DISTINCT sarana FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025
  ```
- **Pertanyaan:  sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang memiliki riwayat pemeriksaan tidak memenuhi ketentuan dalam periode tahun 2025?**
  ```sql
  SELECT DISTINCT mp.nama_sarana, mp.sarana, mp.komoditi FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND lower(kesimpulan) = 'tmk';
  ```
- **Pertanyaan:  sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang pernah memproduksi dan mengedarkan obat tradisional; suplemen kesehatan; obat kuasi tie dalam periode tahun 2025?**
  ```sql
  SELECT mp.nama_sarana, mpt.product_name, mp.sarana, mp.komoditi, mpt.tp_kategori FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND lower(tp_kategori) LIKE '%tie%';
  ```
- **Pertanyaan:  sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang Tidak dilakukan pemeriksaan dalam periode 2 tahun terakhir?**
  ```sql
  SELECT DISTINCT nama_sarana, komoditi, tanggal_mulai FROM public.mv_pemeriksaan mp WHERE (lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%' OR lower(komoditi) LIKE '%obat kuasi%') AND mp.nama_sarana NOT IN ( SELECT nama_sarana FROM public.mv_pemeriksaan WHERE tanggal_mulai >= NOW() - INTERVAL '2 year' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ) ORDER BY nama_sarana;
  ```
- **Pertanyaan:  sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang tutup dalam periode tahun 2025?**
  ```sql
  SELECT nama_sarana, kesimpulan FROM public.mv_pemeriksaan mp WHERE mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND lower(kesimpulan) = 'ttp' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Pertanyaan:  sumber datanya dari pemeriksaan produk rumah tangga**  `[no-sql]`
- **pertumbuhan industri kosmetik dalam 10 tahun terakhir**  `[no-sql]`
- **riwayat pemeriksaan untuk PT. Ozthetique Medika Indonesia**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE LOWER(nama_sarana) LIKE '%pt. ozthetique medika indonesia%';
  ```
- **sarana apa saja yang diperiksa?**
  ```sql
  SELECT DISTINCT jenis_sarana FROM vw_pemeriksaan_bcc;
  ```
- **Sarana apa saja yang tutup pada tahun 2024?**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_end) = 2024 GROUP BY nama_sarana;
  ```
- **sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang belum dilakukan pemeriksaan dalam periode 2 tahun terakhir?**
  ```sql
  SELECT DISTINCT nama_sarana FROM public.mv_pemeriksaan WHERE (komoditi ILIKE '%obat tradisional%' OR komoditi ILIKE '%suplemen kesehatan%' OR komoditi ILIKE '%obat kuasi%') AND nama_sarana NOT IN ( SELECT nama_sarana FROM public.mv_pemeriksaan WHERE tanggal_mulai >= '2023-08-13' AND (komoditi ILIKE '%obat tradisional%' OR komoditi ILIKE '%suplemen kesehatan%' OR komoditi ILIKE '%obat kuasi%') );
  ```
- **sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang memiliki riwayat pemeriksaan tidak memenuhi ketentuan dalam periode tahun 2025?**
  ```sql
  SELECT DISTINCT nama_sarana FROM mv_pemeriksaan WHERE komoditi IN ('OBAT TRADISIONAL', 'SUPLEMEN KESEHATAN', 'OBAT KUASI') AND kesimpulan = 'TMK' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang pernah memproduksi dan mengedarkan obat tradisional; suplemen kesehatan; obat kuasi tie dalam periode tahun 2025?**
  ```sql
  SELECT DISTINCT nama_sarana FROM mv_pemeriksaan WHERE LOWER(komoditi) IN ('obat tradisional', 'suplemen kesehatan', 'obat kuasi') AND LOWER(jenis_sarana) IN ('produksi', 'distribusi') AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang tutup dalam periode tahun 2025?**
  ```sql
  SELECT DISTINCT nama_sarana FROM mv_pemeriksaan WHERE ( komoditi = 'OBAT TRADISIONAL' OR komoditi = 'SUPLEMEN KESEHATAN' OR komoditi ILIKE '%obat kuasi%' ) AND kesimpulan = 'TTP' AND ( EXTRACT( YEAR FROM tanggal_mulai ) = 2025 OR EXTRACT( YEAR FROM tanggal_selesai ) = 2025 );
  ```
- **saya mintanya wardah**  `[no-sql]`
- **Temukan node dan hubungan yang menunjukkan dampak 'Kampanye Kesadaran Publik' terhadap 'Penjualan Produk Ilegal'.**  `[no-sql]`
- **Tolong buatkan query untuk: jenis tms apa yang paling banyak ditemukan selama periode tahun 2025?**
  ```sql
  SELECT jenis_sarana, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND kesimpulan = 'TMK' GROUP BY 1 ORDER BY 2 DESC;
  ```
- **Tolong buatkan query untuk: sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang memiliki riwayat pemeriksaan tidak memenuhi ketentuan dalam periode tahun 2025?**
  ```sql
  SELECT DISTINCT mp.nama_sarana, mp.sarana, mp.komoditi FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND lower(kesimpulan) = 'tmk';
  ```
- **Tolong buatkan query untuk: sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang pernah memproduksi dan mengedarkan obat tradisional; suplemen kesehatan; obat kuasi tie dalam periode tahun 2025?**
  ```sql
  SELECT mp.nama_sarana, mpt.product_name, mp.sarana, mp.komoditi, mpt.tp_kategori FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND lower(tp_kategori) LIKE '%tie%';
  ```
- **Tolong buatkan query untuk: sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang Tidak dilakukan pemeriksaan dalam periode 2 tahun terakhir?**
  ```sql
  SELECT DISTINCT nama_sarana, komoditi, tanggal_mulai FROM public.mv_pemeriksaan mp WHERE (lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%' OR lower(komoditi) LIKE '%obat kuasi%') AND mp.nama_sarana NOT IN ( SELECT nama_sarana FROM public.mv_pemeriksaan WHERE tanggal_mulai >= NOW() - INTERVAL '2 year' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') ) ORDER BY nama_sarana;
  ```
- **Tolong buatkan query untuk: sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang tutup dalam periode tahun 2025?**
  ```sql
  SELECT nama_sarana, kesimpulan FROM public.mv_pemeriksaan mp WHERE mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND lower(kesimpulan) = 'ttp' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Tolong buatkan query untuk: upt mana saja yang paling banyak melaporkan hasil pemeriksaan sarana yang tmk?**
  ```sql
  SELECT nama_upt, kesimpulan, count(*) FROM public.mv_pemeriksaan mp WHERE mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND lower(kesimpulan) = 'tmk' GROUP BY 1, 2 ORDER BY 3 DESC LIMIT 5;
  ```
- **untuk tahun 2025?**
  ```sql
  select distinct nama_sarana, klasifikasi_distribusi from mv_pemeriksaan mp where lower(mp.klasifikasi_distribusi) like '%importir%' and EXTRACT(YEAR FROM tanggal_selesai) = 2025
  ```
- **upt mana saja yang paling banyak melaporkan hasil pemeriksaan sarana yang tmk?**
  ```sql
  SELECT nama_balai FROM public.vw_pemeriksaan_bcc WHERE kesimpulan = 'TMK' GROUP BY nama_balai ORDER BY COUNT(*) DESC LIMIT 1;
  ```
- **What is the number of inspections this year?**
  ```sql
  SELECT COUNT(id) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = EXTRACT(YEAR FROM CURRENT_DATE);
  ```

## 15.3 Pertanyaan GAP (71) — Tidak Bisa Dijawab Warehouse

### BUPN column missing — 27 pertanyaan

- **"sarana bupn apa saja yang pernah diperiksa oleh badan pom pada tahun 2023?"**
  ```sql
  SELECT DISTINCT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2023;
  ```
- **"sebutkan riwayat pemeriksaan balai dengan nama x pada tahun y, yang mencakup jumlah sarana distribusi dengan dan tanpa nomor notifikasi (bupn dan importir) yang memenuhi ketentuan dan tidak memenuhi ketentuan, serta jumlah temuan produk dan nilai temuannya dikategorikan berdasarkan bahan berbahaya, tanpa izin edar, kadaluarsa, dan lain-lain?"**  `[no-sql]`
- **"tampilkan temuan produk berdasarkan kategori sarana distribusi bupn, importir, pedagang besar farmasi, dan instalasi farmasi pemerintah?"**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE lower(nama_sarana) LIKE '%bupn%' UNION SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE lower(nama_sarana) LIKE '%importir%' UNION SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE lower(nama_sarana) LIKE '%pedagang besar farmasi%' UNION SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE lower(nama_sarana) LIKE '%instalasi farmasi pemerintah%';
  ```
- **apa pengertian BUPN?**  `[no-sql]`
- **apakah CV Sinar Intan Raya termasuk BUPN kosmetik?**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(nama_sarana) LIKE '%sinar intan raya%' AND lower(komoditi) LIKE '%kosmetik%';
  ```
- **berapa jumlah BUPN di kota Bandung?**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE lower(kabupaten) LIKE '%bandung%' AND lower(nama_sarana) LIKE '%bupn%'
  ```
- **dari daftar sarana di atas, adakah sarana distribusi yang merupakan BUPN?**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND lower(nama_sarana) LIKE '%bupn%' GROUP BY nama_sarana;
  ```
- **Pertanyaan:  Sarana BUPN apa saja yang pernah diperiksa oleh Badan POM?**
  ```sql
  SELECT DISTINCT (nama_sarana) FROM mv_pemeriksaan WHERE lower(sarana) = 'produksi' AND LOWER(komoditi) LIKE '%obat%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED');
  ```
- **Pertanyaan:  Sarana BUPN Apa saja yang pernah diperiksa?**
  ```sql
  select distinct(nama_sarana), sarana, klasifikasi_sarana, klasifikasi_distribusi from mv_pemeriksaan mp where mp.klasifikasi_distribusi = 'BADAN USAHA/USAHA PERORANGAN PEMILIK NOTIFIKASI KOSMETIK'
  ```
- **Sarana BUPN apa saja yang pernah diperiksa oleh Badan POM**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(nama_sarana) LIKE '%bupn%' GROUP BY nama_sarana;
  ```
- **sarana BUPN apa saja yang pernah diperiksa oleh badan pom pada tahun 2025?**
  ```sql
  SELECT DISTINCT nama_sarana FROM public.mv_pemeriksaan WHERE nama_sarana ILIKE '%bupn%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025;
  ```
- **Sarana BUPN apa saja yang pernah diperiksa oleh Badan POM?**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(nama_sarana) LIKE '%bupn%' GROUP BY nama_sarana;
  ```
- **sarana BUPN apa saja yang pernah diperiksa oleh BPOM**
  ```sql
  SELECT DISTINCT sarana FROM mv_pemeriksaan WHERE lower(sarana) LIKE '%bupn%'
  ```
- **sebutkan riwayat pemeriksaan balai besar pom di bandung pada tahun 2025, yang mencakup jumlah sarana distribusi dengan dan tanpa nomor notifikasi (bupn dan importir) yang memenuhi ketentuan dan tidak memenuhi ketentuan, serta jumlah temuan produk dan nilai temuannya dikategorikan berdasarkan bahan berbahaya, tanpa izin edar, kadaluarsa, dan lain-lain?**  `[no-sql]`
- **tampilkan BUPN di kota Bandung yang memiliki riwayat memenuhi ketentuan**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc vpb WHERE lower(kabupaten) LIKE '%bandung%' AND kesimpulan LIKE 'MK' GROUP BY 1
  ```
- **tampilkan BUPN di kota Bandung yang memiliki riwayat tidak memenuhi ketentuan**
  ```sql
  SELECT DISTINCT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(kab_kota) LIKE '%bandung%' AND kesimpulan LIKE 'TMK';
  ```
- **tampilkan BUPN kosmetik yang memiliki riwayat memenuhi ketentuan di surabaya**
  ```sql
  SELECT bupn FROM vw_pemeriksaan_bcc WHERE lower(komoditi) LIKE '%kosmetik%' AND kesimpulan = 'MK' AND lower(kota) LIKE '%surabaya%' GROUP BY bupn;
  ```
- **tampilkan BUPN yang pernah memiliki riwayat tidak memenuhi ketentuan di Surabaya**
  ```sql
  SELECT DISTINCT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(nama_balai) LIKE '%surabaya%' AND kesimpulan LIKE 'TMK'
  ```
- **tampilkan hanya yang BUPN kosmetik saja**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(nama_sarana) LIKE '%bupn%' AND lower(komoditi) LIKE '%kosmetik%' GROUP BY nama_sarana;
  ```
- **Tampilkan hasil atau kesimpulan pemeriksaan terkait riwayat TMK sarana distribusi BUPN di kota Surabaya.**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE lower(kota) LIKE '%surabaya%' AND lower(jenis_sarana) LIKE '%distribusi%' AND lower(nama_sarana) LIKE '%bupn%' AND kesimpulan = 'TMK';
  ```
- **tampilkan hasil pemeriksaan sarana BUPN di Jawa Timur tahun 2025**
  ```sql
  SELECT nama_balai, nama_sarana, count(*) FROM vw_pemeriksaan_bcc vpb WHERE lower(nama_balai) LIKE '%bandung%' AND EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY 1, 2;
  ```
- **Tampilkan riwayat TMK sarana distribusi BUPN di kota Surabaya berdasarkan periode waktu.**
  ```sql
  SELECT nama_sarana, tgl_start, tgl_end, kesimpulan FROM public.vw_pemeriksaan_bcc WHERE lower(nama_sarana) LIKE '%bupn%' AND lower(jenis_sarana) LIKE '%distribusi%' AND lower(kabupaten) LIKE '%surabaya%' AND kesimpulan = 'TMK' ORDER BY tgl_start;
  ```
- **tampilkan sarana BUPN di kota Jakarta yang pernah diperiksa oleh BPOM**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(nama_balai) LIKE '%jakarta%' GROUP BY nama_sarana
  ```
- **Tampilkan sarana distribusi BUPN di kota Surabaya yang memiliki riwayat TMK.**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(nama_balai) LIKE '%surabaya%' AND kesimpulan = 'TMK' AND lower(jenis_sarana) LIKE 'distribusi';
  ```
- **tampilkan sarana distribusi kosmetik BUPN yang pernah memiliki riwayat tidak memenuhi ketentuan di Surabaya**
  ```sql
  SELECT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE 'distribusi' AND lower(komoditi) LIKE 'kosmetik' AND kesimpulan = 'TMK' AND lower(nama_balai) LIKE '%bupn%' AND lower(kabupaten) LIKE '%surabaya%' GROUP BY nama_sarana;
  ```
- **tampilkan temuan produk berdasarkan kategori sarana distribusi bupn, importir, pedagang besar farmasi, dan instalasi farmasi pemerintah?**
  ```sql
  SELECT DISTINCT T1.product_name FROM mv_pemeriksaan_temuan AS T1 INNER JOIN mv_pemeriksaan AS T2 ON T1.id_pemeriksaan = T2.id WHERE LOWER(T2.jenis_sarana) LIKE '%distribusi%' AND LOWER(T2.nama_sarana) IN ('bupn', 'importir', 'pedagang besar farmasi', 'instalasi farmasi pemerintah');
  ```
- **Tampilkan total pemeriksaan sarana distribusi dengan klasifikasi importir dan BUPN Badan Usaha/ Usaha Perorangan Pemilik Notifikasi Kosmetik pada tahun 2024**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(jenis_sarana) LIKE '%distribusi%' AND lower(klasifikasi) IN ('importir', 'bupn badan usaha/ usaha perorangan pemilik notifikasi kosmetik');
  ```

### CPOTB (not CPOB/CPKB) — 4 pertanyaan

- **"bagaimana tren data hasil pengawasan sarana obat tradisional; suplemen kesehatan; obat kuasi yang tidak memenuhi ketentuan berdasarkan kategori temuan (tmk tie/cpotb/cpotb habis/tidak memiliki cpotb) dalam periode tahun 2023?"**  `[no-sql]`
- **bagaimana tren data hasil pengawasan sarana obat tradisional; suplemen kesehatan; obat kuasi yang tidak memenuhi ketentuan berdasarkan kategori temuan (tmk tie/cpotb/cpotb habis/tidak memiliki cpotb) dalam periode tahun 2025?**  `[no-sql]`
- **Pertanyaan:  bagaimana tren data hasil pengawasan sarana obat tradisional; suplemen kesehatan; obat kuasi yang tidak memenuhi ketentuan berdasarkan kategori temuan tmk tie/cpotb/cpotb habis/tidak memiliki cpotb dalam periode tahun 2025?**
  ```sql
  SELECT EXTRACT(MONTH FROM tanggal_mulai) AS bulan, mp.sarana, mp.komoditi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') GROUP BY 1, 2, 3, 4;
  ```
- **Tolong buatkan query untuk: bagaimana tren data hasil pengawasan sarana obat tradisional; suplemen kesehatan; obat kuasi yang tidak memenuhi ketentuan berdasarkan kategori temuan tmk tie/cpotb/cpotb habis/tidak memiliki cpotb dalam periode tahun 2025?**
  ```sql
  SELECT EXTRACT(MONTH FROM mp.tanggal_mulai) AS bulan, mp.nama_sarana, mp.komoditi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND (lower(mp.komoditi) LIKE '%obat%' OR lower(mp.komoditi) LIKE '%obat tradisional%' OR lower(mp.komoditi) LIKE '%suplemen kesehatan%') AND lower(mp.kesimpulan) = 'tmk' AND lower(mpt.temuan) LIKE '%tmk tie/cpotb/cpotb habis/tidak memiliki cpotb%' GROUP BY 1, 2, 3, 4;
  ```

### SIPT/reporting date missing — 21 pertanyaan

- **"tampilkan kepatuhan pemenuhan timeline upt dalam melaporkan hasil pengawasan di sipt, yang diukur dari tanggal pemeriksaan, tanggal verifikasi oleh kepala upt, dan tanggal diterima oleh operator pusat."**
  ```sql
  SELECT nama_balai, COUNT(CASE WHEN tgl_end <= sync THEN id ELSE NULL END) AS tepat_waktu, COUNT(id) AS total, CAST(COUNT(CASE WHEN tgl_end <= sync THEN id ELSE NULL END) AS NUMERIC) / CAST(COUNT(id) AS NUMERIC) * 100 AS persentase_kepatuhan FROM public.vw_pemeriksaan_bcc WHERE kesimpulan = 'MK' GROUP BY nama_balai ORDER BY nama_balai;
  ```
- **"tampilkan ketepatan waktu pelaporan sipt oleh balai dengan menampilkan data tanggal pemeriksaan dan tanggal kirim data sipt ke pusat yang kurang dari 30 hari kerja dan lebih dari 30 hari kerja untuk balai pom di jakarta."**
  ```sql
  SELECT nama_balai, SUM(CASE WHEN (sync::DATE - tgl_end) <= 30 THEN 1 ELSE 0 END) AS tepat_waktu, SUM(CASE WHEN (sync::DATE - tgl_end) > 30 THEN 1 ELSE 0 END) AS tidak_tepat_waktu FROM public.vw_pemeriksaan_bcc WHERE nama_balai LIKE '%Jakarta%' GROUP BY nama_balai;
  ```
- **"tampilkan ketepatan waktu pelaporan sipt oleh balai x dengan menampilkan data tanggal pemeriksaan dan tanggal kirim data sipt ke pusat yang kurang dari 30 hari kerja dan lebih dari 30 hari kerja."**
  ```sql
  SELECT CASE WHEN (vw_pemeriksaan_bcc.sync::DATE - vw_pemeriksaan_bcc.tgl_end) <= 30 THEN 'Kurang dari 30 hari kerja' ELSE 'Lebih dari 30 hari kerja' END AS ketepatan_waktu, COUNT(*) AS jumlah_laporan FROM public.vw_pemeriksaan_bcc WHERE vw_pemeriksaan_bcc.nama_balai = 'Balai X' GROUP BY ketepatan_waktu;
  ```
- **"tampilkan temuan produk berdasarkan kategori sarana distribusi yang ada di sipt?"**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE jenis_sarana = 'Distribusi' GROUP BY nama_sarana;
  ```
- **Pertanyaan:  Tampilkan persentase ketepatan waktu pelaporan SIPT oleh Balai POM di Bandung**
  ```sql
  WITH data_sipt AS ( SELECT mp.nama_upt, mp.day_mulai_selesai, CASE WHEN mp.day_mulai_selesai < 30 THEN 'Tepat Waktu' ELSE 'Terlambat' END AS kategori_waktu FROM mv_pemeriksaan mp WHERE LOWER(mp.nama_upt) LIKE '%bandung%' AND mp.day_mulai_selesai IS NOT NULL ) SELECT kategori_waktu, COUNT(*) AS jumlah_laporan, ROUND((COUNT(*)::decimal / NULLIF(SUM(COUNT(*)) OVER (), 0)) * 100, 2) AS persentase FROM data_sipt GROUP BY kategori_waktu ORDER BY persentase DESC;
  ```
- **Pertanyaan:  tampilkan temuan produk berdasarkan kategori sarana distribusi yang ada di sipt?**
  ```sql
  SELECT mp.komoditi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(nama_sarana) LIKE '%distribusi%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2;
  ```
- **tampilakan persentase ketepatan waktu pelaporan hasil pemeriksaan oleh upt ke sipt.**  `[no-sql]`
- **tampilkan kepatuhan pemenuhan timeline upt dalam melaporkan hasil pengawasan di sipt, yang diukur dari tanggal pemeriksaan, tanggal verifikasi oleh kepala upt, dan tanggal diterima oleh operator pusat.**
  ```sql
  WITH verifikasi_kepala_upt AS ( SELECT id_pemeriksaan, created_at AS tanggal_verifikasi_kepala_upt FROM public.mv_pemeriksaan_log WHERE status_label = 'Kepala Balai / Loka - Verifikasi' ), verifikasi_operator_pusat AS ( SELECT id_pemeriksaan, created_at AS tanggal_diterima_operator_pusat FROM public.mv_pemeriksaan_log WHERE status_label = 'Operator Pusat - Verifikasi' ) SELECT mp.nama_upt, mp.nama_sarana, mp.tanggal_selesai AS tanggal_pemeriksaan, vku.tanggal_verifikasi_kepala_upt, vop.tanggal_diterima_operator_pusat, (vku.tanggal_verifikasi_kepala_upt::date - mp.tanggal_selesai::date) AS durasi_pemeriksaan_ke_verifikasi_upt, (vop.tanggal_diterima_operator_pusat::date - vku.tanggal_verifikasi_kepala_upt::date) AS durasi_verifikasi_upt_ke_operator_pusat FROM public.mv_pemeriksaan mp LEFT JOIN verifikasi_kepala_upt vku ON mp.id = vku.id_pemeriksaan LEFT JOIN verifikasi_operator_pusat vop ON mp.id = vop.id_pemeriksaan WHERE mp.tanggal_selesai IS NOT NULL AND vku.tanggal_verifikasi_kepala_upt IS NOT NULL AND vop.tanggal_diterima_operator_pusat IS NOT NULL ORDER BY mp.nama_upt, mp.nama_sarana;
  ```
- **tampilkan ketepatan waktu pelaporan sipt oleh balai besar pom di bandung dengan menampilkan data tanggal pemeriksaan dan tanggal kirim data sipt ke pusat yang kurang dari 30 hari kerja dan lebih dari 30 hari kerja.**
  ```sql
  WITH waktu AS ( SELECT mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS t3, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 4) AS t4 FROM public.mv_pemeriksaan_log AS mpl GROUP BY mpl.id_pemeriksaan ), kerja AS ( SELECT w.id_pemeriksaan, w.t3, w.t4, ( SELECT COUNT(*) FROM generate_series(w.t3::date, w.t4::date - 1, '1 day') AS d(hari) WHERE EXTRACT(DOW FROM hari) BETWEEN 1 AND 5 -- Senin–Jumat ) AS workdays_between FROM waktu w WHERE w.t3 IS NOT NULL AND w.t4 IS NOT NULL AND w.t4::date > w.t3::date ) SELECT k.id_pemeriksaan, mp.nama_upt, mp.nama_sarana, k.t3 AS tanggal_ka_balai, k.t4 AS tanggal_pusat, k.workdays_between FROM kerja k JOIN public.mv_pemeriksaan mp ON mp.id = k.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%balai besar pom di bandung%' AND k.workdays_between < 30 ORDER BY k.id_pemeriksaan;
  ```
- **tampilkan ketepatan waktu pelaporan sipt oleh balai dengan menampilkan data tanggal pemeriksaan dan tanggal kirim data sipt ke pusat yang kurang dari 30 hari kerja dan lebih dari 30 hari kerja untuk balai pom di jakarta.**
  ```sql
  SELECT tanggal_mulai AS tanggal_pemeriksaan, tanggal_input AS tanggal_kirim_data_sipt_ke_pusat, EXTRACT(DAY FROM (tanggal_input - tanggal_mulai)) AS selisih_hari, CASE WHEN EXTRACT(DAY FROM (tanggal_input - tanggal_mulai)) < 30 THEN 'Kurang dari 30 hari' WHEN EXTRACT(DAY FROM (tanggal_input - tanggal_mulai)) >= 30 THEN 'Lebih dari 30 hari' ELSE 'Tidak Diketahui' END AS kategori_ketepatan_waktu FROM public.mv_pemeriksaan WHERE LOWER(nama_upt) LIKE '%jakarta%';
  ```
- **Tampilkan ketepatan waktu pelaporan SIPT oleh Balai Semarang**  `[no-sql]`
- **Tampilkan ketepatan waktu pelaporan SIPT oleh Balai Surabaya**
  ```sql
  SELECT count(*) FROM vw_pemeriksaan_bcc WHERE lower(nama_balai) LIKE '%surabaya%'
  ```
- **Tampilkan ketepatan waktu pelaporan SIPT oleh Balai Surabaya di tahun 2022-2024**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) BETWEEN 2022 AND 2024 AND lower(nama_balai) LIKE '%surabaya%'
  ```
- **Tampilkan tanggal pemeriksaan dan tanggal kirim data SIPT ke pusat untuk laporan dari Balai Besar POM di Bandung di mana selisih antara tanggal pemeriksaan dan tanggal kirim data SIPT ke pusat kurang dari 30 hari kerja.**
  ```sql
  WITH waktu AS ( SELECT mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 2) AS t2, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 4) AS t4 FROM public.mv_pemeriksaan_log AS mpl GROUP BY mpl.id_pemeriksaan ), kerja AS ( SELECT w.id_pemeriksaan, w.t2, w.t4, ( SELECT COUNT(*) FROM generate_series(w.t2::date, w.t4::date - 1, '1 day') AS d(hari) WHERE EXTRACT(DOW FROM hari) BETWEEN 1 AND 5 -- Senin–Jumat ) AS workdays_between FROM waktu w WHERE w.t2 IS NOT NULL AND w.t4 IS NOT NULL AND w.t4::date > w.t2::date ) SELECT k.id_pemeriksaan, mp.nama_upt, mp.nama_sarana, k.t2 AS tanggal_pemeriksaan, k.t4 AS tanggal_pusat, k.workdays_between FROM kerja k JOIN public.mv_pemeriksaan mp ON mp.id = k.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%balai besar pom di bandung%' AND k.workdays_between < 30 ORDER BY k.id_pemeriksaan;
  ```
- **Tampilkan tanggal pemeriksaan dan tanggal kirim data SIPT ke pusat untuk laporan dari Balai Besar POM di Bandung di mana selisih antara tanggal pemeriksaan dan tanggal kirim data SIPT ke pusat lebih dari 30 hari kerja.**
  ```sql
  WITH waktu AS ( SELECT mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS t3, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 4) AS t4 FROM public.mv_pemeriksaan_log AS mpl GROUP BY mpl.id_pemeriksaan ), kerja AS ( SELECT w.id_pemeriksaan, w.t3, w.t4, ( SELECT COUNT(*) FROM generate_series(w.t3::date, w.t4::date - 1, '1 day') AS d(hari) WHERE EXTRACT(DOW FROM hari) BETWEEN 1 AND 5 -- Senin–Jumat ) AS workdays_between FROM waktu w WHERE w.t3 IS NOT NULL AND w.t4 IS NOT NULL AND w.t4::date > w.t3::date ) SELECT k.id_pemeriksaan, mp.nama_upt, mp.nama_sarana, k.t3 AS tanggal_ka_balai, k.t4 AS tanggal_pusat, k.workdays_between FROM kerja k JOIN public.mv_pemeriksaan mp ON mp.id = k.id_pemeriksaan WHERE k.workdays_between > 30 and lower(mp.nama_upt) LIKE '%balai besar pom di bandung%' ORDER BY k.id_pemeriksaan;
  ```
- **Tampilkan tanggal pemeriksaan dan tanggal kirim data SIPT ke pusat untuk laporan dari Balai Besar POM di Bandung.**
  ```sql
  WITH waktu AS ( SELECT mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS t3, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 4) AS t4 FROM public.mv_pemeriksaan_log AS mpl GROUP BY mpl.id_pemeriksaan ), kerja AS ( SELECT w.id_pemeriksaan, w.t3, w.t4, ( SELECT COUNT(*) FROM generate_series(w.t3::date, w.t4::date - 1, '1 day') AS d(hari) WHERE EXTRACT(DOW FROM hari) BETWEEN 1 AND 5 -- Senin–Jumat ) AS workdays_between FROM waktu w WHERE w.t3 IS NOT NULL AND w.t4 IS NOT NULL AND w.t4::date > w.t3::date ) SELECT k.id_pemeriksaan, mp.nama_upt, mp.nama_sarana, k.t3 AS tanggal_ka_balai, k.t4 AS tanggal_pusat FROM kerja k JOIN public.mv_pemeriksaan mp ON mp.id = k.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%pom di bandung%' ORDER BY k.id_pemeriksaan;
  ```
- **tampilkan temuan produk berdasarkan kategori sarana distribusi yang ada di sipt?**
  ```sql
  SELECT t1.product_name, t1.tp_kategori FROM public.mv_pemeriksaan_temuan AS t1 INNER JOIN public.mv_pemeriksaan AS t2 ON t1.id_pemeriksaan = t2.id WHERE LOWER(t2.jenis_sarana) LIKE '%distribusi%';
  ```
- **tampilkan temuan yang terbanyak di tahun 2025 data SIPT dengan lingkup pangan olahan**  `[no-sql]`
- **Tolong buatkan query untuk: tampilkan ketepatan waktu pelaporan sipt oleh balai besar pom di bandung dengan menampilkan data tanggal pemeriksaan dan tanggal kirim data sipt ke pusat yang kurang dari 30 hari kerja dan lebih dari 30 hari kerja.**
  ```sql
  WITH waktu AS ( SELECT mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS t3, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 4) AS t4 FROM public.mv_pemeriksaan_log AS mpl GROUP BY mpl.id_pemeriksaan ), kerja AS ( SELECT w.id_pemeriksaan, w.t3, w.t4, ( SELECT COUNT(*) FROM generate_series(w.t3::date, w.t4::date - 1, '1 day') AS d(hari) WHERE EXTRACT(DOW FROM hari) BETWEEN 1 AND 5 -- Senin–Jumat ) AS workdays_between FROM waktu w WHERE w.t3 IS NOT NULL AND w.t4 IS NOT NULL AND w.t4::date > w.t3::date ) SELECT k.id_pemeriksaan, mp.nama_upt, mp.nama_sarana, k.t3 AS tanggal_ka_balai, k.t4 AS tanggal_pusat, k.workdays_between FROM kerja k JOIN public.mv_pemeriksaan mp ON mp.id = k.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%balai besar pom di bandung%' ORDER BY k.id_pemeriksaan;
  ```
- **Tolong buatkan query untuk: tampilkan ketepatan waktu pelaporan sipt oleh balai dengan menampilkan data tanggal pemeriksaan dan tanggal kirim data sipt ke pusat yang kurang dari 30 hari kerja dan lebih dari 30 hari kerja untuk balai pom di jakarta.**
  ```sql
  WITH waktu AS ( SELECT mpl.id_pemeriksaan, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 3) AS t3, MIN(mpl.created_at) FILTER (WHERE mpl.urutan_step = 4) AS t4 FROM public.mv_pemeriksaan_log AS mpl GROUP BY mpl.id_pemeriksaan ), kerja AS ( SELECT w.id_pemeriksaan, w.t3, w.t4, ( SELECT COUNT(*) FROM generate_series(w.t3::date, w.t4::date - 1, '1 day') AS d(hari) WHERE EXTRACT(DOW FROM hari) BETWEEN 1 AND 5 -- Senin–Jumat ) AS workdays_between FROM waktu w WHERE w.t3 IS NOT NULL AND w.t4 IS NOT NULL AND w.t4::date > w.t3::date ) SELECT k.id_pemeriksaan, mp.nama_upt, mp.nama_sarana, k.t3 AS tanggal_ka_balai, k.t4 AS tanggal_pusat, k.workdays_between FROM kerja k JOIN public.mv_pemeriksaan mp ON mp.id = k.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%pom di jakarta%' ORDER BY k.id_pemeriksaan;
  ```
- **Tolong buatkan query untuk: tampilkan temuan produk berdasarkan kategori sarana distribusi yang ada di sipt?**
  ```sql
  SELECT mp.komoditi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.nama_sarana) LIKE '%distribusi%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2;
  ```

### forecast — 2 pertanyaan

- **proyeksikan pertumbuhan populasi sarana peredaran yang di periksa upt balai besar pom di bandung dalam kurun waktu 5 tahun terakhir, tampilkan persentase pertambahan sarana peredaran baru yang diperiksa tiap tahunnya dan buat trend, kemudian simulasikan proyeksi pertumbuhan tahun berikutnya berdasarkan rata-rata persentase pertumbuhan sarana peredaran baru.**
  ```sql
  WITH YearlySarana AS ( SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, COUNT(DISTINCT nama_sarana) AS jumlah_sarana_baru FROM public.mv_pemeriksaan WHERE LOWER(nama_upt) LIKE '%balai besar pom di bandung%' AND EXTRACT(YEAR FROM tanggal_mulai) >= EXTRACT(YEAR FROM CURRENT_DATE) - 5 GROUP BY tahun ORDER BY tahun ), GrowthRates AS ( SELECT ys1.tahun, ys1.jumlah_sarana_baru, LAG(ys1.jumlah_sarana_baru, 1, 0) OVER (ORDER BY ys1.tahun) AS jumlah_sarana_sebelumnya, CASE WHEN LAG(ys1.jumlah_sarana_baru, 1, 0) OVER (ORDER BY ys1.tahun) > 0 THEN (CAST(ys1.jumlah_sarana_baru AS NUMERIC) - LAG(ys1.jumlah_sarana_baru, 1, 0) OVER (ORDER BY ys1.tahun)) / LAG(ys1.jumlah_sarana_baru, 1, 0) OVER (ORDER BY ys1.tahun) * 100 ELSE 0 END AS persentase_pertumbuhan FROM YearlySarana ys1 ), AverageGrowth AS ( SELECT AVG(persentase_pertumbuhan) AS rata_rata_pertumbuhan FROM GrowthRates WHERE persentase_pertumbuhan IS NOT NULL AND persentase_pertumbuhan != 0 ), LastYearData AS ( SELECT tahun, jumlah_sarana_baru FROM YearlySarana ORDER BY tahun DESC LIMIT 1 ) SELECT gr.tahun, gr.jumlah_sarana_baru, gr.persentase_pertumbuhan FROM GrowthRates gr UNION ALL SELECT (SELECT tahun FROM LastYearData) + 1 AS tahun_proyeksi, (SELECT jumlah_sarana_baru FROM LastYearData) * (1 + (SELECT rata_rata_pertumbuhan FROM AverageGrowth) / 100) AS proyeksi_jumlah_sarana, (SELECT rata_rata_pertumbuhan FROM AverageGrowth) AS persentase_pertumbuhan_proyeksi;
  ```
- **proyeksikan pertumbuhan populasi sarana peredaran yang di periksa upt balai besar pom di bandung dalam kurun waktu 5 tahun terakhir, tampilkan persentase pertambahan sarana peredaran baru yang diperiksa tiap tahunnya dan buat trend, kemudian simulasikan proyeksi pertumbuhan tahun berikutnya berdasarkan rata-rata persentase pertumbuhan sarana peredaran baru.**
  ```sql
  WITH YearlySarana AS ( SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, COUNT(DISTINCT nama_sarana) AS jumlah_sarana_baru FROM public.mv_pemeriksaan WHERE LOWER(nama_upt) LIKE '%balai besar pom di bandung%' AND EXTRACT(YEAR FROM tanggal_mulai) >= EXTRACT(YEAR FROM CURRENT_DATE) - 5 GROUP BY tahun ORDER BY tahun ), GrowthRates AS ( SELECT ys1.tahun, ys1.jumlah_sarana_baru, LAG(ys1.jumlah_sarana_baru, 1, 0) OVER (ORDER BY ys1.tahun) AS jumlah_sarana_sebelumnya, CASE WHEN LAG(ys1.jumlah_sarana_baru, 1, 0) OVER (ORDER BY ys1.tahun) > 0 THEN (CAST(ys1.jumlah_sarana_baru AS NUMERIC) - LAG(ys1.jumlah_sarana_baru, 1, 0) OVER (ORDER BY ys1.tahun)) / LAG(ys1.jumlah_sarana_baru, 1, 0) OVER (ORDER BY ys1.tahun) * 100 ELSE 0 END AS persentase_pertumbuhan FROM YearlySarana ys1 ), AverageGrowth AS ( SELECT AVG(persentase_pertumbuhan) AS rata_rata_pertumbuhan FROM GrowthRates WHERE persentase_pertumbuhan IS NOT NULL AND persentase_pertumbuhan != 0 ), LastYearData AS ( SELECT tahun, jumlah_sarana_baru FROM YearlySarana ORDER BY tahun DESC LIMIT 1 ) SELECT gr.tahun, gr.jumlah_sarana_baru, gr.persentase_pertumbuhan FROM GrowthRates gr UNION ALL SELECT (SELECT tahun FROM LastYearData) + 1 AS tahun_proyeksi, (SELECT jumlah_sarana_baru FROM LastYearData) * (1 + (SELECT rata_rata_pertumbuhan FROM AverageGrowth) / 100) AS proyeksi_jumlah_sarana, (SELECT rata_rata_pertumbuhan FROM AverageGrowth) AS persentase_pertumbuhan_proyeksi;
  ```

### nilai sarana (only grade) — 6 pertanyaan

- **"tampilkan persentase ketepatan grading hasil pemeriksaan di upt dengan kode upt 'xxxx' di tw 1 2025 (syarat : grading a (mk) jika nilai sarana a dan b; grading b (tmk) jika nilai sarana c; grading c (tmk) jika nilai sarana d) dan tampilkan list hasil pemeriksaan sarana yang tidak tepat gradingnya"**  `[no-sql]`
- **Tampilkan persentase ketepatan grading hasil pemeriksaan di Balai Besar POM di Jakarta di TW 1 2025 Syarat : grading A MK jika nilai sarana A dan B; grading B TMK jika nilai sarana C; grading C TMK jika nilai sarana D dan tampilkan list hasil pemeriksaan sarana yang tidak tepat gradingnya**
  ```sql
  WITH data_grading AS ( SELECT mp.grade, mp.kesimpulan, CASE WHEN UPPER(mp.grade) = 'A' AND UPPER(mp.kesimpulan) = 'MK' THEN 1 WHEN UPPER(mp.grade) = 'B' AND UPPER(mp.kesimpulan) = 'TMK' THEN 1 WHEN UPPER(mp.grade) = 'C' AND UPPER(mp.kesimpulan) = 'TMK' THEN 1 ELSE 0 END AS tepat, mp.nama_sarana FROM mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND EXTRACT(QUARTER FROM mp.tanggal_mulai) = 1 AND mp.grade IS NOT NULL AND LOWER(mp.nama_upt) LIKE '%jakarta%' ) SELECT grade, COUNT(*) AS total_pemeriksaan, SUM(tepat) AS jumlah_tepat, COUNT(*) - SUM(tepat) AS jumlah_tidak_tepat, ROUND((SUM(tepat)::decimal / NULLIF(COUNT(*), 0)) * 100, 2) AS persentase_ketepatan FROM data_grading GROUP BY grade ORDER BY grade;
  ```
- **tampilkan persentase ketepatan grading hasil pemeriksaan di upt balai pom di bogor di tw 1 2025 (syarat : grading a (mk) jika nilai sarana a dan b; grading b (tmk) jika nilai sarana c; grading c (tmk) jika nilai sarana d) dan tampilkan list hasil pemeriksaan sarana yang tidak tepat gradingnya**  `[no-sql]`
- **Tampilkan persentase ketepatan grading hasil pemeriksaan di UPT x di TW 1 2025 Syarat : grading A MK jika nilai sarana A dan B; grading B TMK jika nilai sarana C; grading C TMK jika nilai sarana D dan tampilkan list hasil pemeriksaan sarana yang tidak tepat gradingnya**
  ```sql
  WITH data_grading AS ( SELECT mp.grade, mp.kesimpulan, CASE WHEN UPPER(mp.grade) = 'A' AND UPPER(mp.kesimpulan) = 'MK' THEN 1 WHEN UPPER(mp.grade) IN ('B', 'C') AND UPPER(mp.kesimpulan) = 'TMK' THEN 1 ELSE 0 END AS tepat FROM mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND EXTRACT(QUARTER FROM mp.tanggal_mulai) = 1 AND mp.grade IS NOT NULL AND mp.grade IN ('A','B','C') ) SELECT grade, COUNT(*) AS total_pemeriksaan, SUM(tepat) AS jumlah_tepat, COUNT(*) - SUM(tepat) AS jumlah_tidak_tepat, ROUND((SUM(tepat)::decimal / NULLIF(COUNT(*), 0)) * 100, 2) AS persentase_ketepatan FROM data_grading GROUP BY grade ORDER BY grade;
  ```
- **tampilkan persentase ketepatan tindak lanjut hasil pemeriksaan dari upt dengan nama 'upt x' di tw 1 2025 (syarat : tindak lanjut tepat jika tindak lanjut berupa pembinaan untuk nilai sarana a atau b; tindak lanjut berupa peringatan dan pembinaan jika nilai sarana c atau d) dan tampilkan list hasil pemeriksaan sarana yang tidak tepat tindak lanjutnya.**  `[no-sql]`
- **tampilkan persentase ketepatan tindak lanjut hasil pemeriksaan dari upt dengan nama balai pom di bogor di tw 1 2025 (syarat : tindak lanjut tepat jika tindak lanjut berupa pembinaan untuk nilai sarana a atau b; tindak lanjut berupa peringatan dan pembinaan jika nilai sarana c atau d) dan tampilkan list hasil pemeriksaan sarana yang tidak tepat tindak lanjutnya.**  `[no-sql]`

### notifikasi column missing — 11 pertanyaan

- **"sebutkan riwayat pemeriksaan balai dengan nama x pada tahun y, yang mencakup jumlah sarana distribusi dengan dan tanpa nomor notifikasi (bupn dan importir) yang memenuhi ketentuan dan tidak memenuhi ketentuan, serta jumlah temuan produk dan nilai temuannya dikategorikan berdasarkan bahan berbahaya, tanpa izin edar, kadaluarsa, dan lain-lain?"**  `[no-sql]`
- **"sebutkan riwayat pemeriksaan balai pom surabaya pada tahun 2023 berupa jumlah sarana distribusi pada tahun 2023 yang tidak memiliki nomor notifikasi baik yang memenuhi ketentuan dan tidak memenuhi ketentuan, serta jumlah temuan produk dan nilai temuannnya dikategorikan berdasarkan temuan bko, tanpa izin edar, kadaluarsa, lain-lain?"**
  ```sql
  SELECT SUM(CASE WHEN vw_pemeriksaan_bcc.kesimpulan = 'MK' THEN 1 ELSE 0 END) AS jumlah_sarana_distribusi_memenuhi_ketentuan, SUM(CASE WHEN vw_pemeriksaan_bcc.kesimpulan = 'TMK' THEN 1 ELSE 0 END) AS jumlah_sarana_distribusi_tidak_memenuhi_ketentuan, SUM(CASE WHEN vw_pemeriksaan_bcc.kesimpulan = 'MK' THEN ( CASE WHEN vw_pemeriksaan_bcc.komoditi = 'BKO' THEN 1 ELSE 0 END ) ELSE 0 END) AS jumlah_temuan_bko_memenuhi_ketentuan, SUM(CASE WHEN vw_pemeriksaan_bcc.kesimpulan = 'TMK' THEN ( CASE WHEN vw_pemeriksaan_bcc.komoditi = 'BKO' THEN 1 ELSE 0 END ) ELSE 0 END) AS jumlah_temuan_bko_tidak_memenuhi_ketentuan, SUM(CASE WHEN vw_pemeriksaan_bcc.kesimpulan = 'MK' THEN ( CASE WHEN vw_pemeriksaan_bcc.komoditi = 'Tanpa Izin Edar' THEN 1 ELSE 0 END ) ELSE 0 END) AS jumlah_temuan_tanpa_izin_edar_memenuhi_ketentuan, SUM(CASE WHEN vw_pemeriksaan_bcc.kesimpulan = 'TMK' THEN ( CASE WHEN vw_pemeriksaan_bcc.komoditi = 'Tanpa Izin Edar' THEN 1 ELSE 0 END ) ELSE 0 END) AS jumlah_temuan_tanpa_izin_edar_tidak_memenuhi_ketentuan, SUM(CASE WHEN vw_pemeriksaan_bcc.kesimpulan = 'MK' THEN ( CASE WHEN vw_pemeriksaan_bcc.komoditi = 'Kadaluarsa' THEN 1 ELSE 0 END ) ELSE 0 END) AS jumlah_temuan_kadaluarsa_memenuhi_ketentuan, SUM(CASE WHEN vw_pemeriksaan_bcc.kesimpulan = 'TMK' THEN ( CASE WHEN vw_pemeriksaan_bcc.komoditi = 'Kadaluarsa' THEN 1 ELSE 0 END ) ELSE 0 END) AS jumlah_temuan_kadaluarsa_tidak_memenuhi_ketentuan, SUM(CASE WHEN vw_pemeriksaan_bcc.kesimpulan = 'MK' THEN ( CASE WHEN vw_pemeriksaan_bcc.komoditi = 'Lain-lain' THEN 1 ELSE 0 END ) ELSE 0 END) AS jumlah_temuan_lain_lain_memenuhi_ketentuan, SUM(CASE WHEN vw_pemeriksaan_bcc.kesimpulan = 'TMK' THEN ( CASE WHEN vw_pemeriksaan_bcc.komoditi = 'Lain-lain' THEN 1 ELSE 0 END ) ELSE 0 END) AS jumlah_temuan_lain_lain_tidak_memenuhi_ketentuan FROM public.vw_pemeriksaan_bcc WHERE vw_pemeriksaan_bcc.nama_balai LIKE '%Surabaya%' AND EXTRACT( YEAR FROM vw_pemeriksaan_bcc.tgl_start ) = 2023 AND vw_pemeriksaan_bcc.jenis_sarana LIKE '%distribusi%';
  ```
- **berapa banyak produk yang dinotifikasi oleh PT AlBakri Bros Perfume**
  ```sql
  SELECT COUNT(DISTINCT nama_sarana) FROM public.vw_pemeriksaan_bcc WHERE nama_sarana = 'PT AlBakri Bros Perfume'
  ```
- **berapa banyak produk yang dinotifikasi oleh PT AlBakri Perfume Bros**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE nama_sarana = 'PT AlBakri Perfume Bros';
  ```
- **berapa jumlah kosmetik yang dinotifikasi oleh PT Qiqi Kosmetik Indonesia dan bagaimana status notifikasinya?**  `[no-sql]`
- **berapa produk yang dinotifikasi oleh ALBAKRI PERFUME BROS?**
  ```sql
  SELECT COUNT(DISTINCT nama_sarana) FROM vw_pemeriksaan_bcc WHERE nama_sarana LIKE 'AL BAKRI PERFUME BROS';
  ```
- **Pertanyaan:  Jumlah sarana distribusi pada Balai POM di Jakarta tahun 2025  yang memiliki Nomor Notifikasi baik yang memenuhi ketentuan dan tidak memenuhi ketentuan**
  ```sql
  SELECT COUNT(*) AS jumlah FROM mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM mp.tanggal_selesai) = 2025 AND LOWER(mp.nama_upt) LIKE '%jakarta%' AND LOWER(mp.klasifikasi_distribusi) LIKE '%notifikasi%'
  ```
- **Pertanyaan:  Jumlah sarana distribusi pada Balai POM di Jakarta tahun 2025 yang tidak memiliki Nomor Notifikasi baik yang memenuhi ketentuan dan tidak memenuhi ketentuan**
  ```sql
  SELECT mp.nama_upt, mp.klasifikasi_distribusi, mp.kesimpulan, COUNT(*) AS jumlah FROM mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM mp.tanggal_selesai) = 2025 AND LOWER(mp.nama_upt) LIKE '%jakarta%' AND ( LOWER(mp.klasifikasi_distribusi) NOT LIKE '%notifikasi%' AND LOWER(mp.klasifikasi_distribusi) NOT LIKE '%importir%' ) GROUP BY 1, 2, 3
  ```
- **sebutkan riwayat pemeriksaan balai besar pom di bandung pada tahun 2025, yang mencakup jumlah sarana distribusi dengan dan tanpa nomor notifikasi (bupn dan importir) yang memenuhi ketentuan dan tidak memenuhi ketentuan, serta jumlah temuan produk dan nilai temuannya dikategorikan berdasarkan bahan berbahaya, tanpa izin edar, kadaluarsa, dan lain-lain?**  `[no-sql]`
- **sebutkan riwayat pemeriksaan balai pom surabaya pada tahun 2025 berupa jumlah sarana distribusi pada tahun 2025 yang tidak memiliki nomor notifikasi baik yang memenuhi ketentuan dan tidak memenuhi ketentuan, serta jumlah temuan produk dan nilai temuannnya dikategorikan berdasarkan temuan bko, tanpa izin edar, kadaluarsa, lain-lain?**
  ```sql
  SELECT t.tp_kategori, COUNT(DISTINCT p.nama_sarana) AS jumlah_sarana, SUM(t.tp_jml_temuan) AS jumlah_temuan_produk, SUM(t.tp_harga_total) AS nilai_temuan FROM mv_pemeriksaan p JOIN mv_pemeriksaan_temuan t ON p.id = t.id_pemeriksaan WHERE p.nama_upt = 'BALAI BESAR POM DI SURABAYA' AND EXTRACT(YEAR FROM p.tanggal_mulai) = 2025 AND p.jenis_sarana = 'Distribusi' AND (t.product_register IS NULL OR t.product_register = '') AND p.kesimpulan IN ('MK', 'TMK') GROUP BY t.tp_kategori ORDER BY t.tp_kategori;
  ```
- **Tampilkan total pemeriksaan sarana distribusi dengan klasifikasi importir dan BUPN Badan Usaha/ Usaha Perorangan Pemilik Notifikasi Kosmetik pada tahun 2024**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(jenis_sarana) LIKE '%distribusi%' AND lower(klasifikasi) IN ('importir', 'bupn badan usaha/ usaha perorangan pemilik notifikasi kosmetik');
  ```

### sampling in pengujian DB — 4 pertanyaan

- **"tampilkan profil sampling dan pengujian obat dan makanan selama periode 2025".**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 OR EXTRACT(YEAR FROM tgl_end) = 2025
  ```
- **Berapa jumlah sampel kosmetik yang telah disampling di seluruh Indonesia selama maret 2025?**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND EXTRACT(MONTH FROM tgl_start) = 3 AND lower(komoditi) LIKE '%kosmetik%'
  ```
- **berapakah rata-rata waktu pelaporan hasil sampling (dari tanggal sampling sampai dengan terbit spu) dan pengujian (dari terbit lhu upt penguji sampai pelaporan dikirim ke pusat)?**  `[no-sql]`
- **tampilkan profil sampling dan pengujian obat dan makanan selama periode 2025.**
  ```sql
  SELECT komoditi, COUNT(id) AS jumlah_pemeriksaan FROM public.mv_pemeriksaan WHERE ( komoditi ILIKE '%obat%' OR komoditi ILIKE '%makanan%' OR komoditi ILIKE '%pangan%' ) AND ( EXTRACT( YEAR FROM tanggal_mulai ) = 2025 OR EXTRACT( YEAR FROM tanggal_selesai ) = 2025 ) GROUP BY komoditi;
  ```

## 15.4 Pertanyaan Cross-Domain (81) — Nyasar ke Pemeriksaan

- **[`pengawasan`] "analisis nilai korelasi antara data maturitas industri farmasi dengan kondisi hasil pengawasan rutin dan komprehensif pada periode waktu pengawasan yang terbaru."**
  ```sql
  WITH FilteredData AS ( SELECT nama_sarana, CASE WHEN kesimpulan = 'MK' THEN 1 ELSE 0 END AS memenuhi_ketentuan, CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE 0 END AS tidak_memenuhi_ketentuan FROM public.vw_pemeriksaan_bcc WHERE jenis_sarana = 'Pelayanan' ), SummaryData AS ( SELECT COUNT(nama_sarana) AS total_sarana, AVG(CAST(memenuhi_ketentuan AS NUMERIC)) AS proporsi_memenuhi, AVG(CAST(tidak_memenuhi_ketentuan AS NUMERIC)) AS proporsi_tidak_memenuhi FROM FilteredData ) SELECT ( SELECT proporsi_memenuhi FROM SummaryData ) AS korelasi_maturitas_industri_farmasi_dengan_hasil_pengawasan_rutin_dan_komprehensif;
  ```
- **[`pengawasan`] "analisis profil kepatuhan pelaku usaha untuk sarana produksi, sarana distribusi, pengawasan iklan, dan penandaan dalam bentuk grafik berdasarkan hasil pemeriksaan pada provinsi Jawa Timur**
  ```sql
  SELECT jenis_sarana, SUM(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE 0 END) AS memenuhi_ketentuan, SUM(CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE 0 END) AS tidak_memenuhi_ketentuan, SUM(CASE WHEN kesimpulan = 'TDP' THEN 1 ELSE 0 END) AS tidak_dapat_diperiksa, SUM(CASE WHEN kesimpulan = 'TTP' THEN 1 ELSE 0 END) AS tutup FROM public.vw_pemeriksaan_bcc WHERE provinsi = 'Jawa Timur' GROUP BY jenis_sarana;
  ```
- **[`sertifikasi`] "bagaimana tingkat pemenuhan cpob (memuaskan, baik, cukup, dst) terhadap seluruh fasilitas produksi atau pada fasilitas produksi [nama fasilitas produksi] secara tren berdasarkan region [nama region], korelasi maturitas [tingkat maturitas], dan riwayat inspeksi?"**  `[no-sql]`
- **[`pengawasan`] "bagaimana tren data hasil pengawasan sarana obat tradisional; suplemen kesehatan; obat kuasi (profil hasil pengawasan) di upt balai besar pom di jakarta dalam periode tahun 2025?"**  `[no-sql]`
- **[`pengawasan`] "bagaimana tren data hasil pengawasan sarana obat tradisional; suplemen kesehatan; obat kuasi dalam periode tahun 2025?"**
  ```sql
  SELECT 'Obat Tradisional' AS jenis, COUNT(CASE WHEN komoditi = 'Obat Tradisional' THEN id END) AS jumlah FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) = 2025 UNION ALL SELECT 'Suplemen Kesehatan' AS jenis, COUNT(CASE WHEN komoditi = 'Suplemen Kesehatan' THEN id END) AS jumlah FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) = 2025 UNION ALL SELECT 'Obat Kuasi' AS jenis, COUNT(CASE WHEN komoditi = 'Obat Kuasi' THEN id END) AS jumlah FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) = 2025;
  ```
- **[`pengawasan`] "bagaimana tren data hasil pengawasan sarana produksi kosmetik (profil hasil pengawasan) di upt balai pom di palembang dalam periode tahun 2024?"**  `[no-sql]`
- **[`pengawasan`] "bagaimana tren data hasil pengawasan sarana produksi kosmetik yang memenuhi ketentuan dan tidak memenuhi ketentuan dalam periode tahun 2024?"**
  ```sql
  SELECT COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND jenis_sarana = 'produksi';
  ```
- **[`pengawasan,sertifikasi`] "bagaimana tren data hasil pengawasan sarana produksi kosmetik yang tidak memenuhi ketentuan berdasarkan kategori temuan (tmk tie/cpkb/cpkb habis/tidak memiliki cpkb) dalam periode tahun 2023?"**  `[no-sql]`
- **[`pengawasan`] "menganalisis temuan kritikal sarana distribusi dan pelayanan dengan nama tertentu dalam wilayah dengan nama tertentu berdasarkan hasil pengawasan."**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE jenis_sarana = 'Distribusi' GROUP BY nama_sarana;
  ```
- **[`sertifikasi`] "riwayat kepatuhan cpob dari pt x dalam periode y tahun pengawasan, dengan menampilkan tanggal inspeksi, pelaksana, tindak lanjut dan temuan kritis/mayor secara singkat terkait dengan tindak lanjut."**
  ```sql
  SELECT p.tgl_start AS tanggal_inspeksi, 'Pelaksana Belum Tersedia' AS pelaksana, 'Tindak Lanjut Belum Tersedia' AS tindak_lanjut, 'Temuan Kritis/Mayor Belum Tersedia' AS temuan_kritis_mayor FROM public.vw_pemeriksaan_bcc AS p WHERE p.nama_sarana LIKE '%pt x%' AND EXTRACT( YEAR FROM p.tgl_start ) BETWEEN ( EXTRACT( YEAR FROM CURRENT_DATE ) - 1 ) AND EXTRACT( YEAR FROM CURRENT_DATE ) AND p.kesimpulan = 'MK';
  ```
- **[`pengawasan`] "tampilkan analisis hasil pengawasan berdasarkan produk obat ketamine di sarana distribusi dan pelayanan dalam bentuk grafik untuk jumlah, nama sarana, dan nama upt."**
  ```sql
  SELECT nama_sarana, nama_balai, COUNT(id) AS jumlah FROM public.vw_pemeriksaan_bcc WHERE komoditi = 'Obat' AND jenis_sarana IN ('Distribusi', 'Pelayanan') GROUP BY nama_sarana, nama_balai ORDER BY jumlah DESC;
  ```
- **[`sertifikasi`] "tampilkan tren temuan inspeksi cpob berdasarkan kategori temuan dan tingkat kekritisan temuan dalam periode waktu pengawasan tertentu, dengan menampilkan data dalam bentuk grafik per regional cakupan pengawasan."**
  ```sql
  SELECT p.provinsi, COUNT(CASE WHEN p.kesimpulan = 'TMK' THEN 1 END) AS jumlah_temuan_tmk, COUNT(CASE WHEN p.kesimpulan = 'MK' THEN 1 END) AS jumlah_temuan_mk, COUNT(CASE WHEN p.kesimpulan = 'TDP' THEN 1 END) AS jumlah_temuan_tdp, COUNT(CASE WHEN p.kesimpulan = 'TTP' THEN 1 END) AS jumlah_temuan_ttp FROM public.vw_pemeriksaan_bcc AS p GROUP BY p.provinsi;
  ```
- **[`pengawasan`] 'Tolong buatkan query untuk: 'tampilkan data gap hasil pengawasan penandaan obat antara pusat dan upt untuk periode pengawasan 2025.**
  ```sql
  SELECT EXTRACT(MONTH FROM tanggal_mulai) AS bulan, nama_upt, kesimpulan, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(komoditi) LIKE '%obat%' GROUP BY 1, 2, 3;
  ```
- **[`sertifikasi`] Ambil semua metrik kepatuhan regulasi yang secara spesifik terkait dengan CPOB untuk sarana di Surabaya pada tahun 2024.**  `[no-sql]`
- **[`pengawasan`] analisis nilai korelasi antara data maturitas industri farmasi dengan kondisi hasil pengawasan rutin dan komprehensif pada periode waktu pengawasan yang terbaru.**
  ```sql
  SELECT kesimpulan, COUNT(*) AS jumlah_kasus FROM public.mv_pemeriksaan WHERE jenis_sarana ILIKE '%farmasi%' AND kesimpulan IS NOT NULL AND EXTRACT(YEAR FROM tanggal_selesai) = ( SELECT MAX(EXTRACT(YEAR FROM tanggal_selesai)) FROM public.mv_pemeriksaan WHERE jenis_sarana ILIKE '%farmasi%' AND kesimpulan IS NOT NULL ) GROUP BY kesimpulan;
  ```
- **[`pengawasan`] analisis profil kepatuhan pelaku usaha untuk sarana produksi, sarana distribusi, pengawasan iklan, dan penandaan dalam bentuk grafik berdasarkan hasil pemeriksaan pada provinsi Jawa Timur**
  ```sql
  SELECT kesimpulan, COUNT(nama_sarana) AS jumlah_sarana FROM public.mv_pemeriksaan WHERE provinsi ILIKE 'JAWA TIMUR' AND ( jenis_sarana ILIKE '%produksi%' OR jenis_sarana ILIKE '%distribusi%' ) AND ( tujuan_pemeriksaan ILIKE '%pengawasan iklan%' OR tujuan_pemeriksaan ILIKE '%penandaan%' ) GROUP BY kesimpulan;
  ```
- **[`sertifikasi`] bagaimana tingkat pemenuhan cpob (memuaskan, baik, cukup, dst) terhadap seluruh fasilitas produksi atau pada fasilitas produksi [nama fasilitas produksi] secara tren berdasarkan region [nama region], korelasi maturitas [tingkat maturitas], dan riwayat inspeksi?**  `[no-sql]`
- **[`pengawasan`] bagaimana tren data hasil pengawasan sarana obat tradisional; suplemen kesehatan; obat kuasi (profil hasil pengawasan) di upt balai besar pom di jakarta dalam periode tahun 2025?**  `[no-sql]`
- **[`pengawasan`] Bagaimana tren data hasil pengawasan Sarana Obat Tradisional; Suplemen Kesehatan; Obat Kuasi dalam periode tahun 2023?**
  ```sql
  SELECT EXTRACT(MONTH FROM tgl_start) AS month, COUNT(*) AS total FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2023 GROUP BY month ORDER BY month;
  ```
- **[`pengawasan`] bagaimana tren data hasil pengawasan sarana obat tradisional; suplemen kesehatan; obat kuasi dalam periode tahun 2025?**
  ```sql
  SELECT COUNT(DISTINCT id) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND LOWER(komoditi) IN ('obat tradisional', 'suplemen kesehatan', 'obat kuasi');
  ```
- **[`pengawasan`] bagaimana tren data hasil pengawasan sarana produksi kosmetik (profil hasil pengawasan) di upt balai pom di palembang dalam periode tahun 2024?**  `[no-sql]`
- **[`pengawasan`] Bagaimana tren data hasil pengawasan sarana produksi kosmetik dalam periode tahun 2023?**
  ```sql
  SELECT EXTRACT( MONTH FROM tgl_start ) AS bulan, COUNT(id) AS jumlah_sarana_produksi FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) = 2023 AND jenis_sarana = 'Produksi' GROUP BY bulan ORDER BY bulan;
  ```
- **[`pengawasan`] Bagaimana tren data hasil pengawasan sarana produksi kosmetik dalam periode tahun 2024 ?**
  ```sql
  SELECT EXTRACT( MONTH FROM tgl_start ) AS bulan, COUNT(id) AS jumlah_sarana_produksi FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) = 2024 AND jenis_sarana ILIKE 'produksi' GROUP BY bulan ORDER BY bulan;
  ```
- **[`pengawasan`] Bagaimana tren data hasil pengawasan sarana produksi kosmetik dalam periode tahun 2025 ?**
  ```sql
  SELECT COUNT(CASE WHEN EXTRACT(YEAR FROM tgl_start) = 2025 THEN id END) FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND jenis_sarana = 'Produksi';
  ```
- **[`pengawasan`] Bagaimana tren data hasil pengawasan sarana produksi kosmetik dalam periode tahun 2025?**
  ```sql
  SELECT EXTRACT(MONTH FROM tgl_start) AS month, COUNT(*) AS total FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(jenis_sarana) = 'produksi' GROUP BY month ORDER BY month;
  ```
- **[`pengawasan`] bagaimana tren data hasil pengawasan sarana produksi kosmetik profil hasil pengawasan di upt balai pom di palembang dalam periode tahun 2024?**
  ```sql
  SELECT mp.nama_upt, tanggal_mulai, nama_sarana, jenis_sarana, mpt.product_name, mpt.tp_kategori FROM public.mv_pemeriksaan mp LEFT JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%palembang%' AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2024 AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND lower(mp.komoditi) LIKE '%kosmetik%' AND lower(mp.sarana) LIKE '%produksi%' ORDER BY 1, 2, 3, 4;
  ```
- **[`pengawasan`] bagaimana tren data hasil pengawasan sarana produksi kosmetik yang memenuhi ketentuan dan tidak memenuhi ketentuan dalam periode tahun 2024?**
  ```sql
  SELECT EXTRACT(MONTH FROM tanggal_mulai) AS month, SUM(CASE WHEN kesimpulan = 'MK' THEN 1 ELSE 0 END) AS count_mk, SUM(CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE 0 END) AS count_tmk FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND komoditi = 'KOSMETIK' AND jenis_sarana = 'KOSMETIK (CPKB)' AND (kesimpulan = 'MK' OR kesimpulan = 'TMK') GROUP BY month ORDER BY month;
  ```
- **[`pengawasan`] bagaimana tren data hasil pengawasan sarana produksi kosmetik yang memenuhi ketentuan dan tidak memenuhi ketentuan dalam periode tahun 2025?**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS bulan, kesimpulan, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(komoditi) like '%kosmetik%' AND lower(sarana) like '%produksi%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1,2,3 ORDER BY 1,2,3;
  ```
- **[`pengawasan,sertifikasi`] bagaimana tren data hasil pengawasan sarana produksi kosmetik yang tidak memenuhi ketentuan berdasarkan kategori temuan (tmk tie/cpkb/cpkb habis/tidak memiliki cpkb) dalam periode tahun 2025?**  `[no-sql]`
- **[`pengawasan,sertifikasi`] bagaimana tren data hasil pengawasan sarana produksi kosmetik yang tidak memenuhi ketentuan berdasarkan kategori temuan tmk tie/cpkb/cpkb habis/tidak memiliki cpkb dalam periode tahun 2025?**
  ```sql
  SELECT EXTRACT(MONTH FROM tanggal_mulai) AS bulan, mp.sarana, mp.komoditi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(komoditi) like '%kosmetik%' AND lower(sarana) like '%produksi%' GROUP BY 1, 2, 3, 4;
  ```
- **[`pengawasan`] bagaimana tren data jumlah pemeriksaan sarana obat tradisional; suplemen kesehatan; obat kuasi (profil hasil pengawasan) di upt balai besar pom di jakarta dalam periode tahun 2025?**  `[no-sql]`
- **[`registrasi`] berapa jumlah kosmetik tanpa izin edar hasil pemeriksaan CV Maklonlab Global tahun 2025?**
  ```sql
  SELECT COUNT(*) FROM public.vw_pemeriksaan_bcc WHERE LOWER(nama_sarana) LIKE '%cv maklonlab global%' AND EXTRACT(YEAR FROM tgl_start) = 2025 AND kesimpulan = 'TMK';
  ```
- **[`pengujian`] Berapa jumlah pengujian pada bulan Mei 2025**
  ```sql
  SELECT COUNT(*) AS jumlah_pengujian FROM public.vw_pemeriksaan_bcc WHERE (tgl_start >= '2025-05-01' AND tgl_start < '2025-06-01') OR (tgl_end >= '2025-05-01' AND tgl_end < '2025-06-01');
  ```
- **[`registrasi`] Berapa nilai temuan kosmetik tanpa izin edar di sarana distribusi tahun 2024 balai pom jakarta?**
  ```sql
  SELECT COUNT(CASE WHEN lower(tujuan) LIKE '%tanpa izin edar%' THEN 1 END) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(jenis_sarana) LIKE '%distribusi%' AND lower(komoditi) LIKE '%kosmetik%' AND lower(nama_balai) LIKE '%jakarta%';
  ```
- **[`pengawasan`] berapa total pemeriksaan iklan pada bulan mei 2025?**
  ```sql
  SELECT count(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(MONTH FROM tgl_start) = 5 AND EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(jenis_sarana) LIKE '%iklan%';
  ```
- **[`pengujian`] Cari relasi antara node 'produk' dan 'hasil pengujian' atau 'hasil pemeriksaan'.**
  ```sql
  SELECT komoditi, kesimpulan, COUNT(*) FROM vw_pemeriksaan_bcc GROUP BY komoditi, kesimpulan
  ```
- **[`pengujian`] Identifikasi semua jenis node 'pengujian' atau 'pemeriksaan' dalam knowledge graph.**  `[no-sql]`
- **[`pengawasan`] menganalisis temuan kritikal sarana distribusi dan pelayanan dengan nama tertentu dalam wilayah dengan nama tertentu berdasarkan hasil pengawasan.**
  ```sql
  SELECT mp.nama_sarana, mp.kabupaten, COUNT(mpt.id_pemeriksaan) AS jumlah_temuan_kritikal FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_temuan AS mpt ON mp.id = mpt.id_pemeriksaan WHERE mp.jenis_sarana IN ('distribusi', 'pelayanan') AND mpt.tp_pelanggaran ILIKE 'tidak memenuhi%' GROUP BY mp.nama_sarana, mp.kabupaten ORDER BY jumlah_temuan_kritikal DESC;
  ```
- **[`pengawasan`] Pertanyaan:  'Tampilkan tren hasil pengawasan sarana  distribusi dan pelayanan berdasarkan kolom ketidaksesuaian pada masing-masing aspek pemeriksaan jenis dan jumlah temuan terbanyak
'**
  ```sql
  SELECT tp_pelanggaran, COUNT(*) AS jumlah_temuan FROM public.mv_pemeriksaan_temuan mt JOIN public.mv_pemeriksaan mp ON mt.id_pemeriksaan = mp.id WHERE lower(mp.sarana) LIKE '%distribusi%' OR lower(mp.sarana) LIKE '%pelayanan%' GROUP BY tp_pelanggaran ORDER BY jumlah_temuan DESC;
  ```
- **[`pengawasan`] Pertanyaan:  bagaimana tren data hasil pengawasan sarana obat tradisional; suplemen kesehatan; obat kuasi dalam periode tahun 2025?**
  ```sql
  SELECT EXTRACT(MONTH FROM mp.tanggal_mulai), sarana, komoditi, kesimpulan, count(nama_sarana) FROM public.mv_pemeriksaan mp WHERE (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 GROUP BY 1, 2, 3, 4;
  ```
- **[`pengawasan`] Pertanyaan:  bagaimana tren data hasil pengawasan sarana produksi kosmetik yang memenuhi ketentuan dan tidak memenuhi ketentuan dalam periode tahun 2024?**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS bulan, kesimpulan, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND lower(komoditi) like '%kosmetik%' AND lower(sarana) like '%produksi%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1,2,3 ORDER BY 1,2,3;
  ```
- **[`pengawasan,sertifikasi`] Pertanyaan:  bagaimana tren data hasil pengawasan sarana produksi kosmetik yang tidak memenuhi ketentuan berdasarkan kategori temuan tmk tie/cpkb/cpkb habis/tidak memiliki cpkb dalam periode tahun 2025?**
  ```sql
  SELECT EXTRACT(MONTH FROM tanggal_mulai) AS bulan, mp.nama_sarana, mp.komoditi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(komoditi) like '%kosmetik%' AND lower(nama_sarana) like '%produksi%' AND lower(kesimpulan) = 'tmk' GROUP BY 1, 2, 3, 4;
  ```
- **[`pengujian`] Pertanyaan:  Berapa total sampel yang sudah di periksa untuk pemeriksaan sarana produksi**
  ```sql
  SELECT count(*) FROM public.mv_pemeriksaan WHERE sarana ILIKE '%produksi%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED');
  ```
- **[`sertifikasi`] Pertanyaan:  Berikan temuan inspeksi CPOB berdasarkan tingkat pemenuhan CPOB**
  ```sql
  select mp.tingkat_pemenuhan_cpob, mpt.tp_kategori, mpt.product_name, mpt.tp_harga_total from mv_pemeriksaan mp join mv_pemeriksaan_temuan mpt on mp.id = mpt.id_pemeriksaan where mp.tingkat_pemenuhan_cpob is not null
  ```
- **[`sertifikasi`] Pertanyaan:  Berikan tingkat pemenuhan CPOB terhadap seluruh fasilitas produksi pada tahun 2025**
  ```sql
  select sarana, mp.tingkat_pemenuhan_cpob, count(*) from mv_pemeriksaan mp where extract(year from mp.tanggal_mulai) = 2025 and lower(mp.sarana) like '%produksi%' group by 1, 2 order by 1, 2
  ```
- **[`sertifikasi`] Pertanyaan:  Riwayat kepatuhan CPOB dari Soho Industri Pharmasi dalam periode 2 tahun pengawasan**
  ```sql
  select mp.tanggal_mulai, nama_sarana, kabupaten_kota, mp.tingkat_pemenuhan_cpob from mv_pemeriksaan mp where mp.tingkat_pemenuhan_cpob is not null and status in ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') and lower(nama_sarana) like '%soho industri%' order by 1, 2, 3
  ```
- **[`sertifikasi`] Pertanyaan:  Tampilkan riwayat pemenuhan CPOB untuk harsen laboratories**
  ```sql
  select mp.tanggal_selesai, mp.nama_sarana, mp.tingkat_pemenuhan_cpob from mv_pemeriksaan mp where mp.tingkat_pemenuhan_cpob is not null and lower(mp.nama_sarana) like '%harsen laboratories%' order by 1, 2, 3
  ```
- **[`sertifikasi`] riwayat kepatuhan CPOB dari PT Dexa Medica dalam periode 2024 tahun pengawasan**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(nama_sarana) LIKE '%dexa medica%'
  ```
- **[`sertifikasi`] riwayat kepatuhan cpob dari pt x dalam periode y tahun pengawasan, dengan menampilkan tanggal inspeksi, pelaksana, tindak lanjut dan temuan kritis/mayor secara singkat terkait dengan tindak lanjut.**
  ```sql
  SELECT mp.tanggal_mulai AS "Tanggal Inspeksi", STRING_AGG(DISTINCT mpp.petugas, ', ') AS "Pelaksana", STRING_AGG(DISTINCT mpt.tp_tindakan, ', ') AS "Tindak Lanjut", STRING_AGG(DISTINCT mpt.tp_kategori, ', ') AS "Temuan Kritis/Mayor" FROM public.mv_pemeriksaan mp LEFT JOIN public.mv_pemeriksaan_petugas mpp ON mp.id = mpp.id_pemeriksaan LEFT JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE mp.nama_sarana ILIKE '%PHAROS INDONESIA%' AND mp.tanggal_mulai >= (CURRENT_DATE - INTERVAL '1 year') GROUP BY mp.id, mp.tanggal_mulai ORDER BY mp.tanggal_mulai DESC;
  ```
- **[`sertifikasi`] riwayat kepatuhan CPOB industri farmasi area pengawasan surabaya dalam periode 2024 tahun pengawasan dalam bentuk grafik**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND lower(nama_balai) LIKE '%surabaya%' AND kesimpulan = 'MK'
  ```
- **[`registrasi`] tampilkan 10 list sarana produksi kosmetik yang pernah memproduksi dan mengedarkan kosmetik Tanpa Izin Edar**
  ```sql
  SELECT DISTINCT nama_sarana FROM vw_pemeriksaan_bcc WHERE lower(jenis_sarana) LIKE '%produksi%' AND lower(komoditi) LIKE '%kosmetik%' AND lower(tujuan) LIKE '%tanpa izin edar%' LIMIT 10;
  ```
- **[`pengawasan`] tampilkan analisis hasil pengawasan berdasarkan produk obat ketamine di sarana distribusi dan pelayanan dalam bentuk grafik untuk jumlah, nama sarana, dan nama upt.**
  ```sql
  SELECT mp.nama_sarana, mp.nama_upt, SUM(mpt.tp_jml_temuan) AS total_jumlah_temuan FROM public.mv_pemeriksaan AS mp JOIN public.mv_pemeriksaan_temuan AS mpt ON mp.id = mpt.id_pemeriksaan WHERE LOWER(mpt.product_name) LIKE '%ketamine%' AND LOWER(mp.jenis_sarana) IN ('distribusi', 'pelayanan') GROUP BY mp.nama_sarana, mp.nama_upt ORDER BY total_jumlah_temuan DESC;
  ```
- **[`pengawasan`] Tampilkan data iklan yang dilaporkan MK/TMK dari masing-masing UPT berdasarkan nama produk, jenis pangan, produsen, kabupaten/provinsi produsen, media iklan, jenis pembuat Iklan (pelaku usaha/perorangan) pada**  `[no-sql]`
- **[`pengawasan`] Tampilkan data iklan yang dilaporkan MK/TMK dari masing-masing UPT berdasarkan nama produk, jenis pangan, produsen, kabupaten/provinsi produsen, media iklan, jenis pembuat Iklan (pelaku usaha/perorangan) pada Tahun 2025**  `[no-sql]`
- **[`pengujian`] Tampilkan data UPT yang paling banyak melaporkan hasil Uji TMS pada tahun 2025. Infokan juga  jumlah TMS/MS pengujian pada tahun 2025.**
  ```sql
  SELECT nama_sarana, COUNT(CASE WHEN kesimpulan = 'TMS' THEN 1 END) AS jumlah_tms, COUNT(CASE WHEN kesimpulan = 'MS' THEN 1 END) AS jumlah_ms, COUNT(*) AS total_pengujian FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY nama_sarana ORDER BY jumlah_tms DESC LIMIT 1;
  ```
- **[`pengawasan`] Tampilkan hasil pengawasan sarana produksi kosmetik tahun 2024 berdasarkan proses kontrol kualitas.**
  ```sql
  SELECT mp.nama_sarana, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM mp.tanggal_mulai) = 2024 AND lower(mp.komoditi) LIKE '%kosmetik%' AND lower(mp.jenis_sarana) LIKE '%produksi%' AND mp.status IN ('VERIFY4', 'VERIFY5', 'VERIFY6', 'VERIFY7', 'FINISHED') GROUP BY mp.nama_sarana, mpt.tp_kategori ORDER BY mp.nama_sarana, mpt.tp_kategori;
  ```
- **[`pengawasan`] Tampilkan hasil pengawasan sarana produksi kosmetik tahun 2024 berdasarkan riwayat kepatuhan fasilitas.**
  ```sql
  SELECT riwayat_kepatuhan_fasilitas, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND lower(komoditi) like '%kosmetik%' AND lower(jenis_sarana) like '%produksi%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1 ORDER BY 1;
  ```
- **[`pengawasan`] Tampilkan hasil pengawasan sarana produksi kosmetik tahun 2024 berdasarkan tingkat pelatihan karyawan.**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS bulan, kesimpulan, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND lower(komoditi) like '%kosmetik%' AND lower(nama_sarana) like '%produksi%' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1,2,3 ORDER BY 1,2,3; ```sql Thought: The question asks about hasil pengawasan sarana produksi kosmetik tahun 2024 berdasarkan tingkat pelatihan karyawan. I need to find a column that represents tingkat pelatihan karyawan. I will use DbTablesWithRelevanceScores to find relevant tables. Action: DbTablesWithRelevanceScores Action Input: hasil pengawasan sarana produksi kosmetik tahun 2024 berdasarkan tingkat pelatihan karyawan
  ```
- **[`pengujian`] Tampilkan hasil uji produk untuk PT Wardah di tahun 2024.**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE nama_sarana = 'WARDAH' AND (EXTRACT(YEAR FROM tgl_start) = 2024 OR EXTRACT(YEAR FROM tgl_end) = 2024) AND kesimpulan = 'MK';
  ```
- **[`pengujian`] Tampilkan hasil uji untuk produk PT Wardah di tahun 2024.**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE nama_sarana = 'PT Wardah' AND (EXTRACT(YEAR FROM tgl_start) = 2024 OR EXTRACT(YEAR FROM tgl_end) = 2024);
  ```
- **[`pengujian`] Tampilkan hasil uji untuk produk PT Wardah tahun 2024.**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024;
  ```
- **[`pengujian`] Tampilkan hasil uji untuk produk untuk PT Wardah tahun 2024.**
  ```sql
  SELECT * FROM public.vw_pemeriksaan_bcc WHERE kesimpulan = 'MK' AND nama_sarana ILIKE '%WARD%' AND tgl_start >= '2024-01-01' AND tgl_end <= '2024-12-31';
  ```
- **[`pengawasan`] Tampilkan kesimpulan dan hasil pengawasan bulanan untuk komoditi kosmetika di tahun 2025.**
  ```sql
  SELECT EXTRACT(MONTH FROM tgl_start) AS bulan, kesimpulan, COUNT(*) FROM vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 AND lower(komoditi) LIKE '%kosmetika%' GROUP BY 1, 2 ORDER BY 1, 2;
  ```
- **[`registrasi`] Tampilkan pemeriksaan sarana dengan hasil tidak memenuhi ketentuan tahun 2024 berdasarkan kategori tanpa izin edar.**
  ```sql
  SELECT nama_sarana FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND kesimpulan = 'TMK' AND lower(kategori) LIKE '%tanpa izin edar%';
  ```
- **[`pengawasan`] tampilkan pemeriksaan sarana, pemeriksaan iklan, pemeriksaan penandaan untuk sarana distribusi PT Niaga Warna Persada**
  ```sql
  SELECT * FROM vw_pemeriksaan_bcc WHERE LOWER(nama_sarana) LIKE '%niaga warna persada%' AND lower(jenis_sarana) LIKE '%distribusi%'
  ```
- **[`pengawasan,registrasi`] tampilkan riwayat pemeriksaan untuk sarana distribusi dengan nama Apotek Krisna Farma yang mencakup riwayat pemeriksaan sarana distribusi, riwayat temuan penandaan, riwayat temuan iklan, riwayat temuan mutu, riwayat temuan keamanan, riwayat data importasi (pernah impor dengan ski tertentu, punya atau tidak punya akun ebpom), dan status nomor izin edar yang masih berlaku atas nama sarana distribusi tersebut?**  `[no-sql]`
- **[`pengawasan,registrasi`] tampilkan riwayat pemeriksaan untuk sarana distribusi dengan nama mukomuko yang mencakup riwayat pemeriksaan sarana distribusi, riwayat temuan penandaan, riwayat temuan iklan, riwayat temuan mutu, riwayat temuan keamanan, riwayat data importasi (pernah impor dengan ski tertentu, punya atau tidak punya akun ebpom) dari data ebpom, dan status nomor izin edar yang masih berlaku atas nama sarana distribusi tersebut dari data notifkos?**  `[no-sql]`
- **[`pengawasan,registrasi`] tampilkan riwayat pemeriksaan untuk sarana distribusi dengan nama x yang mencakup riwayat pemeriksaan sarana distribusi, riwayat temuan penandaan, riwayat temuan iklan, riwayat temuan mutu, riwayat temuan keamanan, riwayat data importasi (pernah impor dengan ski tertentu, punya atau tidak punya akun ebpom) dari data ebpom, dan status nomor izin edar yang masih berlaku atas nama sarana distribusi tersebut dari data notifkos?**  `[no-sql]`
- **[`pengawasan,registrasi`] tampilkan riwayat pemeriksaan untuk sarana distribusi dengan nama x yang mencakup riwayat pemeriksaan sarana distribusi, riwayat temuan penandaan, riwayat temuan iklan, riwayat temuan mutu, riwayat temuan keamanan, riwayat data importasi (pernah impor dengan ski tertentu, punya atau tidak punya akun ebpom), dan status nomor izin edar yang masih berlaku atas nama sarana distribusi tersebut?**  `[no-sql]`
- **[`registrasi`] Tampilkan total temuan produk dan total nilai temuan pada kategori Tanpa Izin Edar**
  ```sql
  SELECT count(*) FROM vw_pemeriksaan_bcc WHERE kesimpulan = 'TMK' AND lower(kategori_temuan) LIKE '%tanpa izin edar%'
  ```
- **[`registrasi`] tampilkan total temuan produk dan total nilai temuan pada kategori tanpa izin edar.**
  ```sql
  SELECT COUNT(CASE WHEN kesimpulan = 'TMK' THEN id END) AS total_temuan_produk, SUM(CASE WHEN kesimpulan = 'TMK' THEN 1 ELSE 0 END) AS total_nilai_temuan FROM public.vw_pemeriksaan_bcc;
  ```
- **[`pengawasan`] Tampilkan tren hasil pengawasan sarana  distribusi dan pelayanan berdasarkan kolom ketidaksesuaian pada masing-masing aspek pemeriksaan jenis dan jumlah temuan terbanyak**
  ```sql
  SELECT EXTRACT(YEAR FROM mp.tanggal_mulai) AS tahun, mp.sarana, mpt.tp_kategori, mpt.tp_pelanggaran, COUNT(mpt.tp_jml_temuan) AS jumlah_temuan FROM public.mv_pemeriksaan mp LEFT JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.sarana) LIKE '%distribusi%' OR lower(mp.sarana) LIKE '%pelayanan%' AND mp.status IN ('VERIFY4', 'VERIFY5', 'VERIFY6', 'VERIFY7', 'FINISHED') GROUP BY 1, 2, 3, 4 ORDER BY tahun, sarana, jumlah_temuan DESC;
  ```
- **[`pengawasan`] tampilkan tren hasil pengawasan sarana distribusi dan pelayanan berdasarkan kolom ketidaksesuaian pada masing-masing aspek pemeriksaan (jenis dan jumlah temuan terbanyak) per regional cakupan pengawasan, dengan menampilkan kategori temuan dan tingkat kekritisannya dalam bentuk grafik.**  `[no-sql]`
- **[`sertifikasi`] tampilkan tren temuan inspeksi cpob berdasarkan kategori temuan dan tingkat kekritisan temuan dalam periode waktu pengawasan tertentu, dengan menampilkan data dalam bentuk grafik per regional cakupan pengawasan.**
  ```sql
  SELECT EXTRACT(YEAR FROM p.tanggal_mulai) AS tahun, EXTRACT(MONTH FROM p.tanggal_mulai) AS bulan, p.provinsi, mt.tp_kategori, p.kesimpulan, COUNT(mt.id_pemeriksaan) AS jumlah_temuan FROM public.mv_pemeriksaan AS p JOIN public.mv_pemeriksaan_temuan AS mt ON p.id = mt.id_pemeriksaan WHERE p.jenis_sarana = 'Produksi' AND p.kesimpulan IS NOT NULL AND mt.tp_kategori IS NOT NULL GROUP BY tahun, bulan, p.provinsi, mt.tp_kategori, p.kesimpulan ORDER BY tahun, bulan, p.provinsi, mt.tp_kategori, p.kesimpulan;
  ```
- **[`pengawasan`] Tolong buatkan query untuk: bagaimana tren data hasil pengawasan sarana obat tradisional; suplemen kesehatan; obat kuasi dalam periode tahun 2025?**
  ```sql
  SELECT EXTRACT(MONTH FROM mp.tanggal_mulai), nama_sarana, komoditi, kesimpulan, count(nama_sarana) FROM public.mv_pemeriksaan mp WHERE (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 GROUP BY 1, 2, 3, 4;
  ```
- **[`pengawasan`] Tolong buatkan query untuk: bagaimana tren data hasil pengawasan sarana produksi kosmetik profil hasil pengawasan di upt balai pom di palembang dalam periode tahun 2024?**
  ```sql
  SELECT mp.nama_upt, tanggal_mulai, nama_sarana, jenis_sarana, mpt.product_name, mpt.tp_kategori FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(nama_upt) LIKE '%palembang%' AND EXTRACT(YEAR FROM mp.tanggal_mulai) = 2024 AND mp.status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND lower(mp.komoditi) LIKE '%kosmetik%' AND lower(mp.sarana) LIKE '%produksi%' ORDER BY 1, 2, 3, 4;
  ```
- **[`pengawasan`] Tolong buatkan query untuk: bagaimana tren data hasil pengawasan sarana produksi kosmetik yang memenuhi ketentuan dan tidak memenuhi ketentuan dalam periode tahun 2024?**
  ```sql
  SELECT EXTRACT(YEAR FROM tanggal_mulai) AS tahun, EXTRACT(MONTH FROM tanggal_mulai) AS bulan, kesimpulan, count(*) FROM public.mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND lower(komoditi) like '%kosmetik%' AND lower(jenis_sarana) like '%produksi%' AND kesimpulan IN ('MK', 'TMK') GROUP BY 1,2,3 ORDER BY 1,2,3;
  ```
- **[`pengawasan,sertifikasi`] Tolong buatkan query untuk: bagaimana tren data hasil pengawasan sarana produksi kosmetik yang tidak memenuhi ketentuan berdasarkan kategori temuan tmk tie/cpkb/cpkb habis/tidak memiliki cpkb dalam periode tahun 2025?**
  ```sql
  SELECT EXTRACT(MONTH FROM tanggal_mulai) AS bulan, mp.nama_sarana, mp.komoditi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(komoditi) like '%kosmetik%' AND lower(nama_sarana) like '%produksi%' AND lower(kesimpulan) = 'tmk' GROUP BY 1, 2, 3, 4;
  ```
- **[`registrasi`] Tolong buatkan query untuk: tampilkan total temuan produk dan total nilai temuan pada kategori tanpa izin edar.**
  ```sql
  SELECT tp_kategori, SUM(tp_jml_temuan) AS total_temuan_produk, SUM(tp_harga_total) AS total_nilai_temuan FROM mv_pemeriksaan_temuan WHERE LOWER(tp_kategori) LIKE '%tanpa izin edar%' GROUP BY 1;
  ```
- **[`pengujian`] UPT manakah yang hasil pemeriksaan TMK sarana produksi MD nya paling banyak di tahun 2025? dan tampilkan hasil uji untuk produk untuk PT Wardah tahun 2024**
  ```sql
  WITH Pemeriksaan2025 AS ( SELECT nama_balai, COUNT(CASE WHEN kesimpulan = 'MK' THEN 1 END) AS jumlah_mk FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2025 GROUP BY nama_balai ), MaxPemeriksaan2025 AS ( SELECT nama_balai FROM Pemeriksaan2025 WHERE jumlah_mk = ( SELECT MAX(jumlah_mk) FROM Pemeriksaan2025 ) ), Wardah2024 AS ( SELECT nama_sarana, kesimpulan FROM public.vw_pemeriksaan_bcc WHERE EXTRACT(YEAR FROM tgl_start) = 2024 AND nama_sarana LIKE '%Wardah%' ) SELECT ( SELECT nama_balai FROM MaxPemeriksaan2025 ) AS upt_terbanyak_mk_2025, ( SELECT STRING_AGG(nama_sarana || ': ' || kesimpulan, '; ') FROM Wardah2024 ) AS hasil_uji_wardah_2024;
  ```
- **[`pengujian`] UPT manakah yang hasil pemeriksaan TMK sarana produksi MD nya paling banyak di tahun 2025? Sama  Infokan juga jumlah TMS/MS pengujian pada tahun 2025.**
  ```sql
  SELECT nama_balai, COUNT(CASE WHEN kesimpulan <> 'MK' THEN 1 END) AS jumlah_tms, COUNT(CASE WHEN kesimpulan = 'MK' THEN 1 END) AS jumlah_ms FROM public.vw_pemeriksaan_bcc WHERE EXTRACT( YEAR FROM tgl_start ) = 2025 GROUP BY nama_balai ORDER BY jumlah_tms DESC LIMIT 1;
  ```
