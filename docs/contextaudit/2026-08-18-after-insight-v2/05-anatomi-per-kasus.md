# Anatomi per kasus gagal — PEMERIKSAAN SARANA

Setiap kasus dibedah dengan empat sudut: **apa yang ditanya**, **apa yang dituntut GT** (beserta SQL GT-nya yang dijalankan ULANG ke database 18 Agustus 2026), **apa yang dikerjakan agent**, dan **mengapa dicatat gagal**. Tidak ada angka yang disalin tanpa dijalankan ulang.

Jumlah kasus: **15**.

---

## `TC-PMR-RANK-SARANA-01`

**Pertanyaan:** sarana apa yang paling banyak pada pemeriksaan?

**Catatan:** agent meminta klarifikasi; jawaban yang dinilai adalah jawaban setelah harness memilih opsi secara otomatis (`[AUTO]`).

| Sudut | Isi |
|---|---|
| GT `assert_any_of` | `[['141.509']]` |
| GT `assert_contains` | `['DISTRIBUSI']` |
| SQL GT | `SELECT sarana, COUNT(*) AS jumlah FROM mv_pemeriksaan WHERE sarana IS NOT NULL AND btrim(sarana) <> '' GROUP BY 1 ORDER BY 2 DESC LIMIT 5` |
| Hasil SQL GT **hari ini** | `DISTRIBUSI|141559 ⏎ PELAYANAN|72680 ⏎ PRODUKSI|43367` |
| SQL agent (terakhir) | `SELECT COUNT(*) AS total_pemeriksaan FROM warehouse.public.mv_pemeriksaan` |
| Jumlah SQL agent | 2 |
| Jawaban agent | **Jenis sarana paling banyak diperiksa** (dari total 257.607 pemeriksaan): ⏎  ⏎ - **PANGAN** — 61.576 pemeriksaan (23,9%) ⏎ - **KOSMETIK** — 36.738 (14,3%) ⏎ - **APOTEK** — 27.521 (10,7%) ⏎ - **PANGAN MD** — 26.321 (10,2%) ⏎ - **PUSAT KESEHATAN MASYARAKAT (PKM)** — 19.762 (7,7%) ⏎ - **OBAT TRADISIONAL** — 16.930 (6,6%) ⏎ - **PANGAN IRT (CPPB - IRT)** — 10.285 (4,0%) ⏎ - **BALAI PENGOBATAN / KLINIK** — 10.178 (4,0%) ⏎ - **INTENSIFIKASI PENGAWASAN … |
| Pesan gagal | `missing: 'DISTRIBUSI'; no assert_any_of group matched (tol=5.0%)` |

## `TC-PMR-RIWAYAT-SARANA-11`

**Pertanyaan:** Sarana Importir apa saja yang pernah diperiksa?

| Sudut | Isi |
|---|---|
| GT `assert_any_of` | `[['ABAD DUA SATU MAKMUR']]` |
| GT `assert_contains` | `['ABAD DUA SATU MAKMUR']` |
| SQL GT | `select distinct(nama_sarana), klasifikasi_distribusi from mv_pemeriksaan mp where lower(mp.klasifikasi_distribusi) like '%importir%'` |
| Hasil SQL GT **hari ini** | `ABAD DUA SATU MAKMUR|IMPORTIR OBAT TRADISIONAL DAN / ATAU SUPLEMEN MAKANAN ⏎ ABADI BERKILAU TECH|IMPORTIR KOSMETIKA ⏎ ABBOTT INDONESIA|IMPORTIR OBAT TRADISIONAL DAN / ATAU SUPLEMEN MAKANAN ⏎ ABHIPRAYA SATWIKA AHARA|IMPORTIR KOSMETIKA ⏎ ABILL INDONESIA JAYA|IMPORTIR KOSMETIKA ⏎ ACCELERATING BUSINESS …` |
| SQL agent (terakhir) | `SELECT klasifikasi_distribusi, COUNT(DISTINCT nama_sarana) AS jumlah_sarana, COUNT(*) AS jumlah_pemeriksaan FROM warehouse.public.mv_pemeriksaan WHERE klasifikasi_distribusi IN ('IMPORTIR KOSMETIKA', 'IMPORTIR OBAT TRADISIONAL DAN / ATAU SUPLEMEN MAKANAN') AND nama_sarana IS NOT NULL AND TRIM(nama_sarana) != '' GROUP BY 1 ORDER BY 2 DESC` |
| Jumlah SQL agent | 4 |
| Jawaban agent | **1.247 sarana importir** pernah diperiksa dalam **1.877 pemeriksaan** di seluruh Indonesia. ⏎  ⏎ **Rincian per jenis importir:** ⏎ - **Importir Kosmetika**: 1.125 sarana (1.601 pemeriksaan) ⏎ - **Importir Obat Tradisional dan/atau Suplemen Makanan**: 166 sarana (276 pemeriksaan) ⏎  ⏎ **Contoh sarana importir yang pernah diperiksa:** ⏎ - ABBOTT INDONESIA ⏎ - BAYER ⏎ - HERBALIFE INDONESIA ⏎ - JOHNSON & JOHNSON INDONESIA ⏎ - KAO INDONESIA DISTRIBUT… |
| Pesan gagal | `missing: 'ABAD DUA SATU MAKMUR'; no assert_any_of group matched (tol=5.0%)` |

## `TC-PMR-SARANA-DISTRIBUSI-06`

**Pertanyaan:** tampilkan jumlah nilai temuan produk sarana distribusi pada tahun 2025?

| Sudut | Isi |
|---|---|
| GT `assert_any_of` | `[['KOSMETIK']]` |
| GT `assert_contains` | `['KOSMETIK']` |
| SQL GT | `SELECT mp.komoditi, mpt.tp_kategori, sum(mpt.tp_harga_total) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND lower(sarana) LIKE '%distribusi%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2` |
| Hasil SQL GT **hari ini** | `KOSMETIK|ED (Expire Date / Kedaluwarsa)|111946036239.000000000 ⏎ KOSMETIK|ED (Expire Date / Kedaluwarsa), Lain - Lain|2424000.000000000 ⏎ KOSMETIK|Kedaluwarsa|36000.000000000 ⏎ KOSMETIK|Kedaluwarsa, Temuan Obat Keras|142000.000000000 ⏎ KOSMETIK|Lain - Lain|3946391780.000000000 ⏎ KOSMETIK|Mengandung …` |
| SQL agent (terakhir) | `SELECT COUNT(*) AS total_temuan_tanpa_filter, COUNT(*) FILTER (WHERE tp_jml_temuan <= 500 AND tp_harga_total <= 10000000) AS temuan_setelah_filter_pencilan, SUM(tp_harga_total) AS total_nilai_sebelum_filter, SUM(tp_harga_total) FILTER (WHERE tp_jml_temuan <= 500 AND tp_harga_total <= 10000000) AS total_nilai_setelah_filter FROM warehouse.public.mv_pemeriksaan_temuan t JOIN warehouse.public.mv_pemeriksaan p ON t.id_pe…` |
| Jumlah SQL agent | 3 |
| Jawaban agent | **Total nilai temuan produk sarana distribusi tahun 2025: Rp 21,26 miliar** dari 82.230 temuan. ⏎  ⏎ Angka ini sudah dibersihkan dari pencilan ekstrem — 1.152 temuan (1,4% dari total 83.382 temuan) dibuang karena `tp_jml_temuan` > 500 atau `tp_harga_total` > Rp 10 juta. Tanpa pembersihan, totalnya mencapai Rp 322 miliar (satu baris salah input bisa mendominasi seluruh jumlah). ⏎  ⏎ **Catatan:** ⏎ - Tahun 2025 masih berjalan, data belum lengkap ⏎ … |
| Pesan gagal | `missing: 'KOSMETIK'; no assert_any_of group matched (tol=5.0%)` |

## `TC-PMR-SARANA-DISTRIBUSI-09`

**Pertanyaan:** tampilkan temuan produk berdasarkan kategori sarana distribusi yang ada di sipt?

| Sudut | Isi |
|---|---|
| GT `assert_any_of` | `[['23']]` |
| GT `assert_contains` | `['BAHAN BERBAHAYA']` |
| SQL GT | `SELECT mp.komoditi, mpt.tp_kategori, count(*) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(sarana) LIKE '%distribusi%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') GROUP BY 1, 2` |
| Hasil SQL GT **hari ini** | `BAHAN BERBAHAYA||23 ⏎ KOSMETIK|BKO|27 ⏎ KOSMETIK|BKO, TIE (Tanpa Izin Edar)|3 ⏎ KOSMETIK|ED (Expire Date / Kedaluwarsa)|19449 ⏎ KOSMETIK|ED (Expire Date / Kedaluwarsa), Lain - Lain|41 ⏎ KOSMETIK|Farmasetik|25 ⏎ KOSMETIK|Illegal/TIE|173 ⏎ KOSMETIK|Kedaluwarsa|2 ⏎ KOSMETIK|Kedaluwarsa, Temuan Obat Ker…` |
| SQL agent (terakhir) | `SELECT COUNT(*) AS total_temuan FROM warehouse.public.mv_pemeriksaan mp JOIN warehouse.public.mv_pemeriksaan_temuan mt ON mt.id_pemeriksaan = mp.id WHERE UPPER(TRIM(CAST(sarana AS VARCHAR))) = 'DISTRIBUSI' AND NULLIF(TRIM(CAST(klasifikasi_distribusi AS VARCHAR)), '') IS NOT NULL` |
| Jumlah SQL agent | 3 |
| Jawaban agent | ### Temuan Produk per Kategori Sarana Distribusi (SIPT) ⏎  ⏎ **Total: 183.128 temuan produk** pada sarana distribusi yang kolom klasifikasi distribusinya terisi. ⏎  ⏎ | Kategori | Jumlah Temuan | ⏎ |---|---| ⏎ | Depot Jamu / Pengecer | 60.524 | ⏎ | Pengecer | 45.317 | ⏎ | Toko Kosmetik / Swalayan / Pengecer | 43.967 | ⏎ | Klinik Kecantikan / Salon / Spa | 7.047 | ⏎ | Distributor | 4.980 | ⏎ | Lain-lain | 4.803 | ⏎ | Toko Obat / Swalayan | 4.501 |… |
| Pesan gagal | `missing: 'BAHAN BERBAHAYA'; no assert_any_of group matched (tol=5.0%)` |

## `TC-PMR-SARANA-DISTRIBUSI-11`

**Pertanyaan:** Jumlah sarana distribusi pada Balai POM di Jakarta tahun 2025 yang tidak memiliki Nomor Notifikasi baik yang memenuhi ketentuan dan tidak memenuhi ketentuan

| Sudut | Isi |
|---|---|
| GT `assert_any_of` | `[['2']]` |
| GT `assert_contains` | `['BALAI BESAR POM DI JAKARTA']` |
| SQL GT | `SELECT mp.nama_upt, mp.klasifikasi_distribusi, mp.kesimpulan, COUNT(*) AS jumlah FROM mv_pemeriksaan mp WHERE EXTRACT(YEAR FROM mp.tanggal_selesai) = 2025 AND LOWER(mp.nama_upt) LIKE '%jakarta%' AND ( LOWER(mp.klasifikasi_distribusi) NOT LIKE '%notifikasi%' OR LOWER(mp.klasifikasi_distribusi) NOT LIKE '%importir%' ) GROUP BY 1, 2, 3` |
| Hasil SQL GT **hari ini** | `BALAI BESAR POM DI JAKARTA|AGEN|MK|2 ⏎ BALAI BESAR POM DI JAKARTA|APOTEK/INSTALASI FARMASI|MK|5 ⏎ BALAI BESAR POM DI JAKARTA|BADAN USAHA|TMK|1 ⏎ BALAI BESAR POM DI JAKARTA|BADAN USAHA/USAHA PERORANGAN PEMILIK NOTIFIKASI KOSMETIK|MK|19 ⏎ BALAI BESAR POM DI JAKARTA|BADAN USAHA/USAHA PERORANGAN PEMILIK…` |
| SQL agent (terakhir) | `SELECT kesimpulan, COUNT(DISTINCT nama_sarana) AS jumlah_sarana FROM warehouse.public.mv_pemeriksaan WHERE TRIM(nama_upt) = 'BALAI BESAR POM DI JAKARTA' AND sarana = 'DISTRIBUSI' AND tanggal_mulai >= '2025-01-01' AND tanggal_mulai < '2026-01-01' AND klasifikasi_distribusi IS NOT NULL AND klasifikasi_distribusi NOT ILIKE '%NOTIFIKASI%' AND kesimpulan IN ('MK', 'TMK') GROUP BY kesimpulan ORDER BY kesimpulan` |
| Jumlah SQL agent | 4 |
| Jawaban agent | **311 sarana distribusi** di Balai Besar POM Jakarta tahun 2025 yang tidak memiliki Nomor Notifikasi (non-BUPN) dengan kesimpulan MK atau TMK. ⏎  ⏎ Rincian berdasarkan kesimpulan: ⏎ - **MK (Memenuhi Ketentuan)**: 250 sarana ⏎ - **TMK (Tidak Memenuhi Ketentuan)**: 72 sarana ⏎  ⏎ Catatan: ⏎ - Jumlah rincian (322) melebihi total karena sebagian sarana memiliki lebih dari satu pemeriksaan dengan kesimpulan berbeda (MK dan TMK) sepanjang tahun 2025 ⏎ … |
| Pesan gagal | `missing: 'BALAI BESAR POM DI JAKARTA'` |

## `TC-PMR-SARANA-TUTUP-06`

**Pertanyaan:** berapa total sarana yang tutup dan/atau tidak berproduksi saat diperiksa di tahun 2024 di wilayah kerja jakarta utara?

| Sudut | Isi |
|---|---|
| GT `assert_any_of` | `[['KOTA JAKARTA UTARA']]` |
| GT `assert_contains` | `['KOTA JAKARTA UTARA']` |
| SQL GT | `SELECT kabupaten_kota, nama_sarana, tanggal_mulai, kesimpulan FROM public.mv_pemeriksaan WHERE kesimpulan = 'TTP' AND lower(sarana) LIKE '%produksi%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND lower(kabupaten_kota) ILIKE '%jakarta utara%'` |
| Hasil SQL GT **hari ini** | `KOTA JAKARTA UTARA|SARI BUNGA ALAM SEJATI  PT|2024-02-16|TTP ⏎ KOTA JAKARTA UTARA|LAUTAN UTAMA|2024-10-24|TTP ⏎ KOTA JAKARTA UTARA|TAUTO KEDUNG RASA|2024-07-25|TTP` |
| SQL agent (terakhir) | `SELECT COUNT(DISTINCT nama_sarana) AS total_sarana, COUNT(DISTINCT CASE WHEN kesimpulan = 'TTP' THEN nama_sarana END) AS sarana_tutup, COUNT(DISTINCT CASE WHEN kesimpulan = 'TDP' THEN nama_sarana END) AS sarana_tidak_dapat_diperiksa FROM warehouse.public.mv_pemeriksaan WHERE kabupaten_kota = 'KOTA JAKARTA UTARA' AND kesimpulan IN ('TTP', 'TDP') AND tanggal_mulai >= '2024-01-01' AND tanggal_mulai < '2025-01-01'` |
| Jumlah SQL agent | 2 |
| Jawaban agent | **Total 15 sarana unik** di wilayah kerja Jakarta Utara yang tutup dan/atau tidak dapat diperiksa saat diperiksa tahun 2024. ⏎  ⏎ Rincian: ⏎ - **7 sarana** dengan kesimpulan **TTP (Tutup)** — sarana tutup saat didatangi ⏎ - **8 sarana** dengan kesimpulan **TDP (Tidak Dapat Diperiksa)** — sarana tidak dapat diperiksa ⏎  ⏎ Kedua kode ini menandakan pemeriksaan tidak jadi dilakukan, bukan vonis kepatuhan. Angka ini dihitung dari sarana unik (COUNT D… |
| Pesan gagal | `missing: 'KOTA JAKARTA UTARA'; no assert_any_of group matched (tol=5.0%)` |

## `TC-PMR-TARGET-CAPAIAN-02`

**Pertanyaan:** Tampilkan data realisasi inspeksi pada tahun 2025 yang dilaksanakan oleh pusat maupun UPT secara mandiri

| Sudut | Isi |
|---|---|
| GT `assert_any_of` | `[['284']]` |
| GT `assert_contains` | `['BALAI BESAR POM DI BANDA ACEH']` |
| SQL GT | `select mp.nama_upt, sarana, mp.komoditi, count(*) from mv_pemeriksaan mp where extract(year from mp.tanggal_mulai) = 2025 group by 1, 2, 3 order by 1, 3, 3` |
| Hasil SQL GT **hari ini** | `BALAI BESAR POM DI BANDA ACEH|DISTRIBUSI|KOSMETIK|284 ⏎ BALAI BESAR POM DI BANDA ACEH|PRODUKSI|KOSMETIK|4 ⏎ BALAI BESAR POM DI BANDA ACEH|DISTRIBUSI|OBAT|26 ⏎ BALAI BESAR POM DI BANDA ACEH|PELAYANAN|OBAT|221 ⏎ BALAI BESAR POM DI BANDA ACEH|DISTRIBUSI|OBAT TRADISIONAL|67 ⏎ BALAI BESAR POM DI BANDA AC…` |
| SQL agent (terakhir) | `SELECT nama_upt, COUNT(*) AS jumlah_pemeriksaan FROM warehouse.public.mv_pemeriksaan WHERE tanggal_mulai >= '2025-01-01' AND tanggal_mulai < '2026-01-01' AND nama_upt NOT LIKE 'DIREKTORAT%' GROUP BY nama_upt ORDER BY jumlah_pemeriksaan DESC` |
| Jumlah SQL agent | 5 |
| Jawaban agent | ## Realisasi Inspeksi 2025 — Pusat & UPT ⏎  ⏎ **Total nasional: 33.360 pemeriksaan** (s/d Agustus 2025 — periode berjalan, belum lengkap). ⏎  ⏎ ### Ringkasan Pusat vs UPT ⏎  ⏎ | Level | Jumlah | % | ⏎ |---|---|---| ⏎ | **UPT** (25 Balai Besar/Balai + 51 Loka) | 33.197 | 99,5% | ⏎ | **Pusat** (5 Direktorat) | 163 | 0,5% | ⏎  ⏎ ### Pusat — per Direktorat ⏎  ⏎ | Direktorat | Pemeriksaan | ⏎ |---|---| ⏎ | Direktorat Pengawasan Kosmetik | 94 | ⏎ | Dir… |
| Pesan gagal | `no assert_any_of group matched (tol=5.0%)` |

## `TC-PMR-TEMUAN-PRODUK-01`

**Pertanyaan:** sarana obat tradisional; suplemen kesehatan; obat kuasi apa saja yang pernah memproduksi dan mengedarkan obat tradisional; suplemen kesehatan; obat kuasi tie dalam periode tahun 2025?

| Sudut | Isi |
|---|---|
| GT `assert_any_of` | `[['APOTEK EKA FARMA  ']]` |
| GT `assert_contains` | `['APOTEK EKA FARMA  ']` |
| SQL GT | `SELECT mp.nama_sarana, mpt.product_name, mp.sarana, mp.komoditi, mpt.tp_kategori FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND (lower(komoditi) LIKE '%obat%' OR lower(komoditi) LIKE '%obat tradisional%' OR lower(komoditi) LIKE '%suplemen kesehatan%') AND lower(tp_kategori) LIKE '%tie%'` |
| Hasil SQL GT **hari ini** | `ROBEMA|CLARIDERM|PELAYANAN|OBAT|Illegal/TIE ⏎ H SYAHRUDIN|TABLET ORANGE|PELAYANAN|OBAT|Illegal/TIE ⏎ H SYAHRUDIN|ZINC|PELAYANAN|OBAT|Illegal/TIE ⏎ H SYAHRUDIN|POT PUTIH|PELAYANAN|OBAT|Illegal/TIE ⏎ H SYAHRUDIN|KAPLET BIRU|PELAYANAN|OBAT|Illegal/TIE ⏎ H SYAHRUDIN|KAPLET HIJAU|PELAYANAN|OBAT|Illegal/T…` |
| SQL agent | **tidak menjalankan SQL sama sekali** |
| Jawaban agent | Saya perlu memahami pertanyaan Anda terlebih dahulu. ⏎  ⏎ **Gate 1 — Klarifikasi:** ⏎  ⏎ Pertanyaan Anda menyebutkan "obat kuasi" sebagai komoditi, tetapi berdasarkan dokumentasi domain, **OBAT KUASI tidak ada sebagai nilai kolom `komoditi`**. Nilai tersebut berasal dari komoditi `BAHAN BERBAHAYA` melalui mapping target balai. ⏎  ⏎ Apakah yang Anda maksud adalah: ⏎ - Sarana yang memproduksi dan mengedarkan **OBAT TRADISIONAL**, **SUPLEMEN KESEHAT… |
| Pesan gagal | `missing: 'APOTEK EKA FARMA  '; no assert_any_of group matched (tol=5.0%)` |

## `TC-PMR-TEMUAN-PRODUK-03`

**Pertanyaan:** tampilkan negara-negara dengan temuan impor pada tahun 2025?

| Sudut | Isi |
|---|---|
| GT `assert_any_of` | `[['BUSANA INDAH']]` |
| GT `assert_contains` | `['BUSANA INDAH']` |
| SQL GT | `SELECT nama_sarana, tanggal_mulai, mpt.product_name, mpt.tp_negara, mpt.tp_kategori FROM public.mv_pemeriksaan mp JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mpt.tp_negara) NOT LIKE '%indonesia%'` |
| Hasil SQL GT **hari ini** | `BUSANA INDAH|2020-02-11|HAJAR JAHANAM  MESIR.|-|TIE (Tanpa Izin Edar) ⏎ BUSANA INDAH|2020-02-11|OTEM.|-|TIE (Tanpa Izin Edar) ⏎ SUMBER KULIT   PT MARINA LOMBOK MANDIRI|2020-02-12|MUSTARD ( CLASSIC YELLOW MUSTARD )|Amerika Serikat|ED (Expire Date / Kedaluwarsa) ⏎ MUTIARA|2020-03-05|PIL TUPAI|Malaysia…` |
| SQL agent (terakhir) | `SELECT LOWER(TRIM(t.tp_negara)) AS negara_raw, COUNT(*) AS jml FROM warehouse.public.mv_pemeriksaan_temuan t JOIN warehouse.public.mv_pemeriksaan p ON t.id_pemeriksaan = p.id WHERE p.tanggal_mulai >= '2025-01-01' AND p.tanggal_mulai < '2026-01-01' AND NULLIF(TRIM(CAST(t.tp_negara AS VARCHAR)), '') IS NOT NULL AND LOWER(TRIM(t.tp_negara)) NOT IN ('indonesia','indoensia','indoneisa','indoneaia','indinesia','indonesai',…` |
| Jumlah SQL agent | 8 |
| Jawaban agent | **China mendominasi** temuan produk impor tahun 2025 dengan ~7.600 temuan (51%), diikuti Malaysia (~3.300, 23%) dan Thailand (~1.100). Tiga negara ini menyumbang ~77% dari seluruh temuan impor. ⏎  ⏎ Sebanyak **28 negara** teridentifikasi sebagai asal produk temuan impor. Selengkap pada tabel di atas. ⏎  ⏎ **Keterbatasan data:** ⏎ - Kolom `tp_negara` berteks bebas — normalisasi telah menggabungkan varian ejaan (China/Cina/Tiongkok/PRC/RRC, dll.) ⏎… |
| Pesan gagal | `missing: 'BUSANA INDAH'; no assert_any_of group matched (tol=5.0%)` |

## `TC-PMR-TREN-HASIL-PEMERIKSAAN-02`

**Pertanyaan:** bagaimana tren data hasil pengawasan sarana produksi kosmetik yang memenuhi ketentuan dan tidak memenuhi ketentuan dalam periode tahun 2024?

| Sudut | Isi |
|---|---|
| GT `assert_any_of` | `[['tidak ada'], ['tidak ditemukan'], ['kosong']]` |
| GT `assert_contains` | `[]` |
| SQL GT | `SELECT COUNT(*) FROM mv_pemeriksaan WHERE EXTRACT(YEAR FROM tanggal_mulai) = 2024 AND lower(sarana) = 'produksi'` |
| Hasil SQL GT **hari ini** | `8062` |
| SQL agent (terakhir) | `SELECT EXTRACT(MONTH FROM tanggal_mulai) AS bulan, kesimpulan, COUNT(*) AS jumlah_pemeriksaan FROM warehouse.public.mv_pemeriksaan WHERE sarana = 'PRODUKSI' AND komoditi = 'KOSMETIK' AND kesimpulan IN ('MK', 'TMK') AND tanggal_mulai >= '2024-01-01' AND tanggal_mulai < '2025-01-01' GROUP BY 1, 2 ORDER BY 1, 2` |
| Jumlah SQL agent | 2 |
| Jawaban agent | **Tren Hasil Pengawasan Sarana Produksi Kosmetik Tahun 2024** ⏎  ⏎ Sepanjang tahun 2024, tercatat **471 pemeriksaan** sarana produksi kosmetik yang memiliki kesimpulan MK (Memenuhi Ketentuan) atau TMK (Tidak Memenuhi Ketentuan). ⏎  ⏎ **Distribusi hasil:** ⏎ - **MK (Memenuhi Ketentuan): 296 pemeriksaan** (62,9%) ⏎ - **TMK (Tidak Memenuhi Ketentuan): 175 pemeriksaan** (37,1%) ⏎  ⏎ **Pola tren bulanan:** ⏎  ⏎ Pemeriksaan MK mencapai puncak pada **Ju… |
| Pesan gagal | `no assert_any_of group matched (tol=5.0%)` |

## `TC-PMR-TREN-HASIL-PEMERIKSAAN-06`

**Pertanyaan:** Tampilkan tren audit komprehensif berdasarkan tingkat kritikalitas untuk tahun 2024

| Sudut | Isi |
|---|---|
| GT `assert_any_of` | `[['1']]` |
| GT `assert_contains` | `['2024-05']` |
| SQL GT | `SELECT TO_CHAR(mkp.tgl_end, 'YYYY-MM') AS bulan_tahun, mkp.tx_criteria AS tingkat_kritikalitas, COUNT(*) AS jumlah_audit FROM mv_kriteria_pemeriksaan mkp WHERE LOWER(mkp.tujuan) LIKE '%komprehensif%' AND EXTRACT(YEAR FROM mkp.tgl_end) = 2024 GROUP BY TO_CHAR(mkp.tgl_end, 'YYYY-MM'), mkp.tx_criteria ORDER BY bulan_tahun, tingkat_kritikalitas` |
| Hasil SQL GT **hari ini** | `2024-05|1|1 ⏎ 2024-05|2|3 ⏎ 2024-05|3|3 ⏎ 2024-06|1|1 ⏎ 2024-06|2|2 ⏎ 2024-09|2|4 ⏎ 2024-09|3|10` |
| SQL agent (terakhir) | `SELECT to_char(date_trunc('month', tanggal_mulai), 'YYYY-MM') AS bulan, COUNT(*) AS jumlah_pemeriksaan, SUM(COALESCE(tx_critical_issue, 0)) AS total_kritis, SUM(COALESCE(tx_major_issue, 0)) AS total_mayor, SUM(COALESCE(tx_minor_issue, 0)) AS total_minor, COUNT(tx_critical_issue) AS terisi_kritis, COUNT(tx_major_issue) AS terisi_mayor, COUNT(tx_minor_issue) AS terisi_minor FROM warehouse.public.mv_pemeriksaan WHERE ta…` |
| Jumlah SQL agent | 2 |
| Jawaban agent | ## Tren Audit Berdasarkan Tingkat Kritikalitas — Tahun 2024 ⏎  ⏎ **Interpretasi:** Tren bulanan jumlah temuan berdasarkan tingkat kritikalitas (kritis, mayor, minor) dari seluruh pemeriksaan sarana yang dimulai pada tahun 2024. ⏎  ⏎ ### Angka Utama 2024 ⏎  ⏎ | Tingkat | Total Temuan | ⏎ |---|---| ⏎ | **Kritis** | 2.093 | ⏎ | **Mayor** | 32.232 | ⏎ | **Minor** | 53.733 | ⏎ | **Total** | **88.058** | ⏎  ⏎ Total pemeriksaan tahun 2024: **48.006 peme… |
| Pesan gagal | `missing: '2024-05'` |

## `TC-PMR-TREN-HASIL-PEMERIKSAAN-07`

**Pertanyaan:** Trend hasil pemeriksaan sarana produksi MD untuk jenis pangan AMDK di UPT Bogor (tahun 2025)

| Sudut | Isi |
|---|---|
| GT `assert_any_of` | `[['2']]` |
| GT `assert_contains` | `['2025-06']` |
| SQL GT | `WITH pemeriksaan_amdk AS ( SELECT mp.id, mp.tanggal_mulai, TO_CHAR(mp.tanggal_mulai, 'YYYY-MM') AS bulan_tahun, mp.nama_upt FROM mv_pemeriksaan mp JOIN mv_pemeriksaan_jenis_pangan mpjp ON mp.id = mpjp.id_pemeriksaan WHERE EXTRACT(YEAR FROM mp.tanggal_mulai) = 2025 AND LOWER(mp.nama_upt) LIKE '%bogor%' AND LOWER(mpjp.jenis_pangan_name) LIKE '%air minum dalam kemasan%' and mp.sarana = 'PRODUKSI' ) SELECT pa.bulan_tahun…` |
| Hasil SQL GT **hari ini** | `2025-06|2 ⏎ 2025-07|3 ⏎ 2025-08|2 ⏎ 2025-10|1 ⏎ 2025-11|3` |
| SQL agent (terakhir) | `SELECT COUNT(DISTINCT mp.id) AS total_pemeriksaan, COUNT(DISTINCT mp.nama_sarana) AS total_sarana_unik FROM warehouse.public.mv_pemeriksaan mp LEFT JOIN warehouse.public.mv_pemeriksaan_jenis_pangan jp ON jp.id_pemeriksaan = mp.id WHERE mp.sarana = 'PRODUKSI' AND mp.jenis_sarana LIKE '%MD%' AND jp.jenis_pangan_name = 'Air Minum Dalam Kemasan' AND mp.nama_upt = 'BALAI POM DI BOGOR' AND mp.tanggal_mulai >= '2025-01-01' …` |
| Jumlah SQL agent | 6 |
| Jawaban agent | **Trend Hasil Pemeriksaan Sarana Produksi MD — Jenis Pangan AMDK di Balai POM di Bogor, 2025** ⏎  ⏎ **Total 2025**: 11 pemeriksaan pada 10 sarana unik. ⏎  ⏎ **Rincian per bulan (kesimpulan)**: ⏎  ⏎ | Periode | MK | TMK | TDP | TTP | Total | ⏎ |---------|----|----|-----|-----|-------| ⏎ | Juni 2025 | 1 | 1 | - | - | 2 | ⏎ | Juli 2025 | - | 1 | 1 | 1 | 3 | ⏎ | Agustus 2025 | 2 | - | - | - | 2 | ⏎ | Oktober 2025 | 1 | - | - | - | 1 | ⏎ | November 20… |
| Pesan gagal | `missing: '2025-06'` |

## `TC-PMR-VONIS-MK-TMK-01`

**Pertanyaan:** tampilkan jumlah sarana yang tidak memenuhi ketentuan di wilayah upt surabaya dan pada tahun 2025

| Sudut | Isi |
|---|---|
| GT `assert_any_of` | `[['455'], ['tidak ada'], ['tidak ditemukan'], ['kosong']]` |
| GT `assert_contains` | `['BALAI BESAR POM DI SURABAYA']` |
| SQL GT | `SELECT nama_upt, count(*) FROM mv_pemeriksaan vpb WHERE lower(nama_upt) LIKE '%surabaya%' AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 AND kesimpulan LIKE 'TMK' GROUP BY 1` |
| Hasil SQL GT **hari ini** | `BALAI BESAR POM DI SURABAYA|455` |
| SQL agent (terakhir) | `SELECT to_char(date_trunc('month', tanggal_mulai), 'YYYY-MM') AS bulan, COUNT(DISTINCT nama_sarana) AS jumlah_sarana_tmk FROM warehouse.public.mv_pemeriksaan WHERE kesimpulan = 'TMK' AND nama_upt = 'BALAI BESAR POM DI SURABAYA' AND tanggal_mulai >= '2025-01-01' AND tanggal_mulai < '2026-01-01' GROUP BY 1 ORDER BY 1` |
| Jumlah SQL agent | 3 |
| Jawaban agent | **Jumlah sarana yang Tidak Memenuhi Ketentuan (TMK) di wilayah Balai Besar POM di Surabaya pada tahun 2025: 443 sarana unik.** ⏎  ⏎ - **Entity**: sarana unik (`COUNT(DISTINCT nama_sarana)`) ⏎ - **Filter**: `kesimpulan = 'TMK'`, `nama_upt = 'BALAI BESAR POM DI SURABAYA'`, `tanggal_mulai` dalam rentang 2025 ⏎ - **Sumber**: `warehouse.public.mv_pemeriksaan` ⏎  ⏎ **Distribusi bulanan** (puncak di Agustus & Oktober, terendah di Desember): ⏎  ⏎ | Bulan… |
| Pesan gagal | `no assert_any_of group matched (tol=5.0%)` |

## `TC-PMR-VONIS-MK-TMK-04`

**Pertanyaan:** upt mana saja yang paling banyak melaporkan hasil pemeriksaan sarana yang tmk?

| Sudut | Isi |
|---|---|
| GT `assert_any_of` | `[['3.323']]` |
| GT `assert_contains` | `['BALAI BESAR POM DI BANDUNG']` |
| SQL GT | `SELECT nama_upt, COUNT(*) as jumlah_pemeriksaan FROM mv_pemeriksaan WHERE kesimpulan = 'TMK' GROUP BY nama_upt ORDER BY count(*) desc limit 5` |
| Hasil SQL GT **hari ini** | `BALAI BESAR POM DI BANDUNG|3324 ⏎ BALAI BESAR POM DI SURABAYA|3217 ⏎ BALAI BESAR POM DI JAKARTA|2752 ⏎ BALAI BESAR POM DI SEMARANG|2741 ⏎ BALAI BESAR POM DI BANDAR LAMPUNG|2565` |
| SQL agent (terakhir) | `SELECT COUNT(*) AS total_tmk, COUNT(DISTINCT nama_upt) AS jumlah_upt FROM warehouse.public.mv_pemeriksaan WHERE kesimpulan = 'TMK' AND nama_upt NOT ILIKE '%DIREKTORAT%' AND nama_upt NOT ILIKE '%DEMO%'` |
| Jumlah SQL agent | 3 |
| Jawaban agent | **Total 75.194 pemeriksaan TMK** dari **83 UPT** (balai/loka) di seluruh Indonesia, tanpa batasan waktu. Direktorat dan akun demo sudah dikeluarkan. ⏎  ⏎ **10 UPT dengan pemeriksaan TMK terbanyak:** ⏎  ⏎ | # | UPT | Jumlah TMK | ⏎ |---|---|---| ⏎ | 1 | BBPOM Bandung | 3.324 | ⏎ | 2 | BBPOM Surabaya | 3.217 | ⏎ | 3 | BBPOM Jakarta | 2.752 | ⏎ | 4 | BBPOM Semarang | 2.741 | ⏎ | 5 | BBPOM Bandar Lampung | 2.565 | ⏎ | 6 | BBPOM Medan | 2.212 | ⏎ | 7 … |
| Pesan gagal | `missing: 'BALAI BESAR POM DI BANDUNG'` |

## `TC-PMR-VONIS-MK-TMK-05`

**Pertanyaan:** tampilkan total nilai keekonomian produk tmk (tie, rusak kedaluwarsa) di balai pom di batam pada tahun 2025.

| Sudut | Isi |
|---|---|
| GT `assert_any_of` | `[['ED (Expire Date / Kedaluwarsa)']]` |
| GT `assert_contains` | `['ED (Expire Date / Kedaluwarsa)']` |
| SQL GT | `SELECT mpt.tp_kategori, sum(mpt.tp_harga_total) FROM public.mv_pemeriksaan mp LEFT OUTER JOIN public.mv_pemeriksaan_temuan mpt ON mp.id = mpt.id_pemeriksaan WHERE lower(mp.nama_upt) LIKE '%pom di batam%' AND lower(kesimpulan) = 'tmk' AND status IN ('VERIFY4', 'VERIFY5','VERIFY6','VERIFY7','FINISHED') AND EXTRACT(YEAR FROM tanggal_mulai) = 2025 GROUP BY 1` |
| Hasil SQL GT **hari ini** | `ED (Expire Date / Kedaluwarsa)|24071500.000000000 ⏎ Illegal/TIE|430000.000000000 ⏎ Kedaluwarsa|240000.000000000 ⏎ Lain - Lain|6480000.000000000 ⏎ Mengandung bahan berbahaya/bahan dilarang (berdasarkan SE)|1010000.000000000 ⏎ Palsu|108000.000000000 ⏎ Rusak|461000.000000000 ⏎ TIE (Tanpa Izin Edar)|627…` |
| SQL agent (terakhir) | `SELECT CASE WHEN tp_kategori ILIKE '%TIE%' OR tp_kategori ILIKE '%izin edar%' THEN 'TIE (Tanpa Izin Edar)' WHEN tp_kategori ILIKE '%kedaluwarsa%' OR tp_kategori ILIKE '%expire%' THEN 'ED (Kedaluwarsa)' WHEN tp_kategori ILIKE '%rusak%' THEN 'Rusak/Substandard' ELSE 'Lainnya' END AS kategori_utama, SUM(tp_harga_total) AS nilai, COUNT(*) AS jumlah_produk FROM warehouse.public.mv_pemeriksaan_temuan t JOIN warehouse.publi…` |
| Jumlah SQL agent | 5 |
| Jawaban agent | **Total nilai keekonomian produk temuan (TIE, kedaluwarsa, rusak) di Balai POM di Batam tahun 2025:** ⏎  ⏎ ### **Rp 690.382.500** ⏎  ⏎ - **2.229 produk temuan** dari **73 pemeriksaan** ⏎  ⏎ **Rincian per kategori:** ⏎  ⏎ | Kategori | Nilai | Jumlah Produk | ⏎ |---|---|---| ⏎ | TIE (Tanpa Izin Edar) | Rp 665.610.000 | 2.036 | ⏎ | ED (Kedaluwarsa) | Rp 24.311.500 | 175 | ⏎ | Rusak/Substandard | Rp 461.000 | 18 | ⏎  ⏎ **Catatan:** ⏎ - TIE mendominas… |
| Pesan gagal | `missing: 'ED (Expire Date / Kedaluwarsa)'; no assert_any_of group matched (tol=5.0%)` |

