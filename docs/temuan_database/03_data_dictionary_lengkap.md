# 03 — Data Dictionary Lengkap (Semua Kolom, Null Rate, Unique Count)

> Semua kolom semua tabel, dikelompokkan per klaster semantik.
> Null rate dan unique count diverifikasi langsung dari database (snapshot 2026-08-13).

## 3.1 `mv_pemeriksaan` (31 kolom — FACT UTAMA)

### Klaster A — IDENTITAS

| # | Kolom | Tipe | Null % | Unique | Catatan |
|---|---|---|---|---|---|
| 1 | `id` | bigint | 0% | 257.456 | PK empirik. `COUNT(*)` = `COUNT(DISTINCT id)`. |
| 2 | `nama_upt` | text | 0% | 91 | 3 tingkat org: Balai Besar, Balai, Loka + 6 Direktorat + 2 DEMO |
| 3 | `nama_sarana` | text | 0% | 130.501 | Free-text. Normalisasi: 126.142 (hanya -4.361). |
| 4 | `alamat` | text | 0% | 158.935 | > nama_sarana → inkonsisten (ditulis ulang tiap inspeksi). |
| 5 | `provinsi` | text | 0,007% | 34 | 18 baris NULL. |
| 6 | `kabupaten_kota` | text | 0,007% | 514 | 18 baris NULL. |

### Klaster B — WAKTU (6 kolom, saling terhitung)

| # | Kolom | Tipe | Null % | Unique | Catatan |
|---|---|---|---|---|---|
| 7 | `tanggal_input` | date | 0% | 2.331 | Kapan data dimasukkan ke sistem. |
| 8 | `tanggal_mulai` | date | 0,4% | 2.201 | Kapan inspeksi dilakukan. **DEFAULT kolom tanggal.** 943 NULL. |
| 9 | `tanggal_selesai` | date | 0,4% | 2.401 | 943 NULL (sama kohort). |
| 10 | `day_input_mulai` | bigint | 0,4% | 762 | = mulai − input. Median 9 hari. **Max 736.685** (outlier). |
| 11 | `day_input_selesai` | bigint | 0,4% | 854 | = selesai − input. Outlier parah. |
| 12 | `day_mulai_selesai` | bigint | 0,4% | 401 | = selesai − mulai. Durasi inspeksi. Max 34.706. |

**Rantai sebab-akibat:** Error tanggal_mulai (0004, 1922, 1970) → day_input_mulai meledak (736.685) →
agg avg_day_* tercemar → dashboard salah. Bersihkan di hulu (fact) otomatis memperbaiki hilir.

### Klaster C — KLASIFIKASI SARANA (4 kolom hierarkis)

| # | Kolom | Tipe | Null % | Unique | Catatan |
|---|---|---|---|---|---|
| 13 | `sarana` | text | 0,0004% | 3 | DISTRIBUSI (55%), PELAYANAN (28%), PRODUKSI (17%). |
| 14 | `jenis_sarana` | text | 0% | 24 | PANGAN (24%), KOSMETIK (14%), APOTEK (11%), PKM (8%)... |
| 15 | `legal` | text | 0,009% | 51 | Campur bentuk hukum (PT, CV) + tipe outlet (TOKO, KIOS). |
| 16 | `klasifikasi_sarana` | text | 76,7% | 22 | **Structural NULL**: hanya untuk DISTRIBUSI (RITEL MODERN/TRADISIONAL/GUDANG). |
| 17 | `klasifikasi_distribusi` | text | 76,7% | 22 | Sama — kondisional pada sarana=DISTRIBUSI. |

### Klaster D — KLASIFIKASI PRODUK & TUJUAN

| # | Kolom | Tipe | Null % | Unique | Catatan |
|---|---|---|---|---|---|
| 18 | `komoditi` | text | 0% | 13 | UPPER CASE. PRODUK PANGAN (42%), OBAT (32%), KOSMETIK (15%)... |
| 19 | `mapping_komoditi_target_balai` | text | 0% | 6 | Bridge ke target_balai. OBAT, KOSMETIKA, PRODUK PANGAN, dll. |
| 20 | `tujuan_pemeriksaan` | text | 0,4% | 36 | PEMERIKSAAN RUTIN (78%), INTENSIFIKASI, KASUS, SERTIFIKASI... |

### Klaster E — HASIL

| # | Kolom | Tipe | Null % | Unique | Catatan |
|---|---|---|---|---|---|
| 21 | `kesimpulan` | text | 0% | 6 | MK (69%), TMK (29%), TTP, TDP, TMBB, NULL. |
| 22 | `status` | text | 0% | 17 | VERIFY4 (64%), VERIFY5 (18%), FINISHED (11%)... |
| 23 | `status_label` | text | 0,04% | 15 | Label resmi untuk status. 114 baris NULL. |
| 24 | `grade` | text | **82,9%** | 4 | A (24.618), B (9.747), C (9.682), N/A (65). **Structural NULL**: hanya RUTIN/INTENSIFIKASI. |

### Klaster F — TINDAK LANJUT & ISSUE

| # | Kolom | Tipe | Null % | Unique | Catatan |
|---|---|---|---|---|---|
| 25 | `tx_critical_issue` | integer | 78,6% | 16 | Checklist audit. Max 17. |
| 26 | `tx_major_issue` | integer | 74,1% | 45 | Max 44. |
| 27 | `tx_minor_issue` | integer | 73,9% | 42 | Max 41. |
| 28 | `tl_saran_names` | text[] (array) | 17,1% | 195 | Pembinaan (133k), Peringatan (66k), Peringatan Keras (25k)... |
| 29 | `hp_followup_name` | text | **99,7%** | 20 | Hanya kasus hukum lanjutan. Structural NULL. |
| 30 | `tingkat_pemenuhan_cpob` | text | **99,7%** | 4 | Hanya industri obat CPOB. Structural NULL. |

## 3.2 `mv_pemeriksaan_log` (11 kolom)

| Kolom | Tipe | Null % | Unique | Catatan |
|---|---|---|---|---|
| `id_pemeriksaan` | bigint | 0% | 257.456 | FK ke fact. |
| `id_steps` | bigint | 0,005% | 1.311.693 | PK natural empirik (99,995% unik). 64 baris NULL. |
| `status` | text | 0,005% | 16 | Kode workflow (DRAFT, VERIFY1-7, FINISHED...). 64 baris NULL. |
| `status_label` | text | 0,014% | 15 | Label resmi. |
| `fullname` | text | 0,059% | 2.063 | Verifikator/approver (BUKAN petugas lapangan). |
| `nama_balai` | text | 0,062% | 92 | |
| `catatan` | text | 17,7% | 207.850 | Free-text. Sumber NLP (alasan revisi). |
| `urutan_step` | integer | 0% | 75 | 1-75. Bukan sequence — bisa melompat/berulang. |
| `created_at` | timestamp | 0,005% | 2.332 | Waktu transisi. 64 baris NULL (= baris corrupt). |
| `trx_steps` | text | — | — | Transaction step identifier. |
| `sync` | timestamp | 0% | 1 | Full-reload timestamp. |

## 3.3 `mv_pemeriksaan_petugas` (11 kolom)

| Kolom | Tipe | Null % | Unique | Catatan |
|---|---|---|---|---|
| `id_pemeriksaan` | bigint | 0% | 257.456 | FK ke fact. |
| `petugas_id` | bigint | 0,037% | 2.997 | Unique petugas. 216 baris NULL. |
| `petugas` | text | — | ~2.969 | Nama petugas. |
| `jenis_id` | integer | 0% | 25 | Kode peran. 16 (140k), 13 (81k), 109 (60k)... 3 kode 6-digit tak dikenal. |
| `komoditi` | text | 0% | 24 | ⚠️ **Jenis sarana, BUKAN produk!** APOTEK, PBF, PKM... |
| `tujuan` | text | 0,3% | 36 | |
| `klasifikasi` | text | 0% | 13 | |
| `nomorsurat` | text | 0,005% | 110.581 | Nomor surat tugas. |
| `tgl_surat` | date | 0,005% | 2.304 | |
| `daftar_balai_pemeriksa` | text | 0,005% | 98 | |

## 3.4 `mv_pemeriksaan_temuan` (18 kolom)

| Kolom | Tipe | Null % | Unique | Catatan |
|---|---|---|---|---|
| `id_pemeriksaan` | bigint | 0% | 32.503 | FK ke fact. Hanya 12,6% inspeksi. |
| `product_register` | text | 0,02% | 25.552 | Nomor registrasi produk. |
| `product_name` | text | 0,01% | 25.552 | Nama produk. |
| `product_brands` | text | — | — | Merk. |
| `registrar` | text | — | — | Pemilik/pendaftar produk. |
| `tp_bets` | text | 47,1% | 50.818 | Batch/expire. Banyak placeholder. |
| `tp_negara` | text | 2,0% | **1.299** | ⚠️ Perlu normalisasi (China = 4+ varian). |
| `tp_pelanggaran` | text | **99,996%** | 7 | **Kolom mati sejati.** Hanya 12 record terisi. |
| `tp_netto` | text | **99,998%** | — | **Kolom mati sejati.** Hanya 5 record terisi. |
| `tp_expire` | date | 61,6% | 4.186 | Expire date produk. |
| `tp_jml_temuan` | bigint | 0,27% | 1.224 | Jumlah unit. ⚠️ Min -196 (negatif), 1 record = 20 miliar (datetime terselip). |
| `tp_unit_id` | bigint | 0% | 92 | Kode satuan. 281 (70k), 241 (48k)... 11 kode 6-digit tak dikenal. |
| `tp_harga` | numeric(38,9) | 0,33% | 4.145 | Harga per unit. |
| `tp_harga_total` | numeric(38,9) | 0,33% | 8.526 | Total nilai. ⚠️ Terkontaminasi outlier (lihat [08](08_nilai_sitaan_dan_produk.md)). |
| `tp_tindakan` | text | — | 126 | Pemusnahan (61%), Dikembalikan (11%), Pengamanan (10%)... |
| `tp_kategori` | text | — | 106 | TIE (52%), ED (20%), Obat Keras (7%)... Banyak sinonim. |
| `tp_keterangan` | text | — | — | Keterangan bebas. |
| `sync` | timestamp | 0% | 1 | |

## 3.5 `mv_pemeriksaan_timeline` (11 kolom)

| Kolom | Tipe | Null % | Unique | Catatan |
|---|---|---|---|---|
| `id_pemeriksaan` | bigint | 0% | 257.458 | 30.699 orphan (id tak ada di fact). |
| `tgl_start` | date | 5,1% | 2.268 | |
| `tgl_end` | date | 5,1% | 2.431 | |
| `tanggal_kirim_kabalai` | date | 13,5% | 2.110 | |
| `tanggal_kirim_direktur` | date | 88,3% | 377 | |
| `tanggal_kirim_pusat` | date | — | — | |
| `status` | bigint | 0% | 18 | Kode status (0, 1-7, 990-999). |
| `mulai_kabalai` | integer | 13,5% | 656 | Hari. Max 526.265 (outlier). |
| `kabalai_direktur` | integer | **88,3%** | 797 | Hari. 254.391 NULL. |
| `direktur_pusat` | integer | — | — | Hari. Trap: 0 ≠ cepat (tanggal belum terisi). |

## 3.6 Tabel Lainnya (ringkas)

### `mv_pemeriksaan_agg` (26 kolom)
Lihat [10_agg_dan_integritas_etr.md](10_agg_dan_integritas_etr.md) untuk detail fan-out.

### `mv_pemeriksaan_jenis_pangan` (4 kolom)
`id_pemeriksaan`, `jenis_pangan_name`, + 2 kolom metadata. 48.511 baris, ~18,8% inspeksi.

### `mv_pemeriksaan_kategori_temuan` (4 kolom)
`id_pemeriksaan`, `tp_kategori`, + 2 kolom. 241.609 baris, 49 nilai bersih.

### `mv_kriteria_pemeriksaan` (12 kolom)
`pemeriksaan_id` (bukan `id_pemeriksaan`!), `nama_sarana`, `klasifikasi`, `tujuan`, `kabupaten`,
`nama_balai`, `tgl_start`, `tgl_end`, `criteria_index`, `tx_criteria` (1-4), `tx_criteria_desc`. 5.892 baris.

### `coverage_balai` (5 kolom)
`id_balai` (88), `nama_balai`, `id_kabupaten` (514), `kabupaten_kota`, `sync`.

### `target_balai` (12 kolom)
`id`, `nama_balai` (76), `komoditi` (7, Title Case), `tahun` (hanya 2024),
`target_penandaan`, `target_pengawasan`, `target_pengujian`, `target_pengujian_pangan`,
`target_pengujian_pangan_fortifikasi`, `target_sarana_distribusi`, `target_sarana_produksi`, `sync`.

## 3.7 Prinsip Kunci: Structural NULL vs Missing NULL

Salah satu temuan terpenting dari analisis kolom:

| Kolom | Null % | Vonis | Alasan |
|---|---|---|---|
| `grade` | 82,9% | **Structural** | Hanya RUTIN/INTENSIFIKASI. Sertifikasi tak ber-grade. |
| `klasifikasi_sarana` | 76,7% | **Structural** | Hanya sarana=DISTRIBUSI. |
| `tingkat_pemenuhan_cpob` | 99,7% | **Structural** | Hanya industri obat CPOB. |
| `hp_followup_name` | 99,7% | **Structural** | Hanya kasus hukum lanjutan. |
| `tx_*_issue` | 74-79% | **Structural** | Hanya inspeksi dengan checklist audit. |
| `mv_kriteria_pemeriksaan` coverage | 99,65% | **Structural** | Hanya sertifikasi CPKB/CPOB. |
| `jenis_pangan` coverage | 81,2% | **Structural** | Hanya komoditi PRODUK PANGAN. |
| `tp_pelanggaran` | 99,996% | **❌ Missing sejati** | Kolom sejenis terisi → tidak ada alasan struktural. |
| `tp_netto` | 99,998% | **❌ Missing sejati** | Sama. |
| `tanggal_mulai` (943 baris) | 0,4% | **Operasional** | Inspeksi dibuat tapi tak dimulai. Tersebar, bukan batch. |

**Prinsip**: ~70% "NULL/kekosongan" di warehouse ini adalah **structural** (kolom kondisional yang memang
tidak berlaku untuk baris itu). Cacat sejati terbatas pada: outlier tanggal, nilai negatif, orphan timeline,
case-mismatch join, sinonim label, kolom mati (`tp_pelanggaran`/`tp_netto`), dan data DEMO.
