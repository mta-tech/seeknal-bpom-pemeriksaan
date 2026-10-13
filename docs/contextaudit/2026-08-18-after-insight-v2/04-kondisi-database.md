# Kondisi database `pemeriksaan` — profil terukur, 18 Agustus 2026

Seluruh angka di halaman ini dihasilkan dengan menjalankan query ke database melalui tunnel `localhost:5533` pada 18 Agustus 2026. Halaman ini menjawab: *seperti apa sebenarnya datanya*, sebelum bicara benar-salah jawaban agent.

## 1. Tabel dan ukurannya

| Tabel | Baris |
|---|---:|
| `mv_pemeriksaan_log` | 1.312.259 |
| `mv_pemeriksaan_petugas` | 582.211 |
| `mv_pemeriksaan_agg` | 367.048 |
| `mv_pemeriksaan_temuan` | 297.058 |
| `mv_pemeriksaan_timeline` | 288.335 |
| `mv_pemeriksaan` | 257.607 |
| `mv_pemeriksaan_jenis_pangan` | 67.223 |
| `mv_kriteria_pemeriksaan` | 5.892 |
| `coverage_balai` | 668 |
| `target_balai` | 532 |
| `mv_pemeriksaan_kategori_temuan` | 0 |

**Indeks:** *tidak ada indeks sama sekali*.
Tanpa indeks, setiap `WHERE` menjadi pemindaian penuh — inilah alasan aturan "jangan `EXTRACT(YEAR ...)` di `WHERE`" muncul di context.

## 2. Grain tabel fakta

```sql
SELECT count(*), count(DISTINCT id) FROM mv_pemeriksaan;   -- 257.607 | 257.607
```

**`id` unik penuh** — `COUNT(*)` dan `COUNT(DISTINCT id)` selalu sama, sehingga pilihan entity pada tabel fakta tidak dapat mengubah angka.

## 3. Rentang waktu dan penanda kosong

| Ukuran | Nilai |
|---|---|
| Kolom tanggal kanonik | `tanggal_mulai` |
| Paling awal | 0004-02-21 |
| Paling akhir | 2027-07-27 |
| Kosong (`NULL`) | 947 |
| Bernilai `1970-01-01` (epoch) | 4 |
| **Bertanggal di masa depan** | 1 |
| `max(sync)` (kesegaran data) | 2026-08-18 05:48:07.253021 |

> 1 baris bertanggal setelah hari ini. `max(tanggal_mulai)` karena itu **bukan** penanda kesegaran data; pakai `sync`.

## 4. Profil setiap kolom tabel fakta

Kolom `kosong` menghitung string kosong/hanya spasi (untuk teks) atau `1970-01-01` (untuk tanggal). Kolom `spasi ujung` menghitung nilai teks yang tidak sama dengan versi `btrim()`-nya — sumber klasik filter kesamaan persis yang gagal senyap.

| Kolom | Tipe | NULL | kosong/epoch | % tak terpakai | distinct | spasi ujung / masa depan | panjang maks |
|---|---|---:|---:|---:|---:|---:|---:|
| `id` | bigint | 0 | 0 | 0.0 % | 257.607 | 0 | — |
| `nama_upt` | text | 0 | 0 | 0.0 % | 91 | 1.428 | 51 |
| `nama_sarana` | text | 0 | 157 | 0.1 % | 130.554 | 18.827 | 214 |
| `alamat` | text | 0 | 0 | 0.0 % | 159.007 | 352 | 669 |
| `provinsi` | text | 18 | 18 | 0.0 % | 34 | 0 | 25 |
| `kabupaten_kota` | text | 18 | 18 | 0.0 % | 514 | 0 | 36 |
| `tanggal_input` | date | 0 | 0 | 0.0 % | 2.337 | 0 | — |
| `tanggal_mulai` | date | 947 | 4 | 0.4 % | 2.205 | 1 | — |
| `tanggal_selesai` | date | 947 | 0 | 0.4 % | 2.402 | 5 | — |
| `day_input_mulai` | bigint | 947 | 0 | 0.4 % | 762 | 0 | — |
| `day_input_selesai` | bigint | 947 | 0 | 0.4 % | 854 | 0 | — |
| `day_mulai_selesai` | bigint | 947 | 0 | 0.4 % | 401 | 0 | — |
| `sarana` | text | 1 | 1 | 0.0 % | 3 | 0 | 10 |
| `jenis_sarana` | text | 0 | 0 | 0.0 % | 24 | 0 | 49 |
| `legal` | text | 23 | 23 | 0.0 % | 51 | 0 | 58 |
| `tujuan_pemeriksaan` | text | 947 | 947 | 0.7 % | 36 | 0 | 41 |
| `komoditi` | text | 0 | 0 | 0.0 % | 13 | 0 | 32 |
| `mapping_komoditi_target_balai` | text | 0 | 0 | 0.0 % | 6 | 0 | 21 |
| `klasifikasi_distribusi` | text | 197.652 | 197.652 | 153.5 % | 22 | 0 | 79 |
| `klasifikasi_sarana` | text | 196.197 | 196.197 | 152.3 % | 4 | 0 | 34 |
| `kesimpulan` | text | 0 | 0 | 0.0 % | 6 | 0 | 4 |
| `status` | text | 0 | 0 | 0.0 % | 17 | 0 | 18 |
| `status_label` | text | 114 | 114 | 0.1 % | 15 | 0 | 51 |
| `tx_critical_issue` | integer | 202.393 | 0 | 78.6 % | 16 | 0 | — |
| `tx_major_issue` | integer | 190.982 | 0 | 74.1 % | 45 | 0 | — |
| `tx_minor_issue` | integer | 190.398 | 0 | 73.9 % | 42 | 0 | — |
| `grade` | text | 213.459 | 213.459 | 165.7 % | 4 | 0 | 3 |
| `hp_followup_name` | text | 256.821 | 256.821 | 199.4 % | 20 | 0 | 86 |
| `tingkat_pemenuhan_cpob` | text | 256.746 | 256.746 | 199.3 % | 4 | 0 | 9 |
| `sync` | timestamp without time zone | 0 | 0 | 0.0 % | 1 | 0 | — |

## 5. Sebaran nilai kolom berkardinalitas rendah

Kolom-kolom inilah yang dipakai testcase sebagai filter. Nilai ditampilkan **apa adanya**, termasuk penanda sentinel dan perbedaan kapitalisasi.

**`sarana`** (3 nilai)

| Nilai | Baris |
|---|---:|
| `DISTRIBUSI` | 141.559 |
| `PELAYANAN` | 72.680 |
| `PRODUKSI` | 43.367 |
| `∅ (kosong)` | 1 |

**`jenis_sarana`** (24 nilai)

| Nilai | Baris |
|---|---:|
| `PANGAN` | 61.576 |
| `KOSMETIK` | 36.738 |
| `APOTEK` | 27.521 |
| `PANGAN MD` | 26.321 |
| `PUSAT KESEHATAN MASYARAKAT (PKM)` | 19.762 |
| `OBAT TRADISIONAL` | 16.930 |
| `PANGAN IRT (CPPB - IRT)` | 10.285 |
| `BALAI PENGOBATAN / KLINIK` | 10.178 |
| `INTENSIFIKASI PENGAWASAN KHUSUS` | 9.061 |
| `SUPLEMEN KESEHATAN` | 7.100 |
| `TOKO OBAT` | 6.894 |
| `PBF` | 6.874 |
| `INSTALLASI FARMASI RUMAH SAKIT SWASTA` | 4.528 |
| `INSTALLASI FARMASI RUMAH SAKIT PEMERINTAH` | 3.786 |
| `INSTALASI FARMASI PEMERINTAH KOTA/KABUPATEN (IFK)` | 3.117 |
| `OBAT TRADISIONAL (CPOTB)` | 2.919 |
| `KOSMETIK (CPKB)` | 2.597 |
| `SARANA PRODUKSI OBAT` | 907 |
| `INSTALASI FARMASI PEMERINTAH PROVINSI (IFP)` | 339 |
| `BAHAN BERBAHAYA` | 108 |
| `PANGAN UMKM MENUJU MD` | 52 |
| `KANTOR KESEHATAN PELABUHAN (KKP)` | 11 |
| `PANGAN MD (OLD)` | 2 |
| `DARING` | 1 |

**`komoditi`** (13 nilai)

| Nilai | Baris |
|---|---:|
| `PRODUK PANGAN` | 107.297 |
| `OBAT` | 82.896 |
| `KOSMETIK` | 39.336 |
| `OBAT TRADISIONAL` | 19.934 |
| `SUPLEMEN KESEHATAN` | 7.134 |
| `NARKOTIKA` | 273 |
| `PSIKOTROPIKA` | 252 |
| `OBAT OBAT TERTENTU` | 176 |
| `PREKURSOR` | 118 |
| `BAHAN BERBAHAYA` | 108 |
| `PRODUK BIOLOGI DAN SARANA KHUSUS` | 55 |
| `BAHAN BAKU OBAT` | 17 |
| `BAHAN OBAT` | 11 |

**`mapping_komoditi_target_balai`** (6 nilai)

| Nilai | Baris |
|---|---:|
| `PRODUK PANGAN` | 107.297 |
| `OBAT` | 83.798 |
| `KOSMETIKA` | 39.336 |
| `OBAT TRADISIONAL (OT)` | 19.934 |
| `SUPLEMEN KESEHATAN` | 7.134 |
| `OBAT KUASI` | 108 |

**`klasifikasi_distribusi`** (22 nilai)

| Nilai | Baris |
|---|---:|
| `∅ (kosong)` | 197.652 |
| `TOKO KOSMETIK / SWALAYAN / PENGECER` | 18.031 |
| `DEPOT JAMU / PENGECER` | 12.184 |
| `PENGECER` | 6.702 |
| `LAIN-LAIN` | 4.578 |
| `TOKO OBAT / SWALAYAN` | 4.514 |
| `KLINIK KECANTIKAN / SALON / SPA` | 4.045 |
| `DISTRIBUTOR` | 2.908 |
| `BADAN USAHA/USAHA PERORANGAN PEMILIK NOTIFIKASI KOSMETIK` | 1.705 |
| `IMPORTIR KOSMETIKA` | 1.601 |
| `AGEN` | 1.197 |
| `STOKIST MLM` | 863 |
| `KLINIK KECANTIKAN` | 699 |
| `SALON/SPA` | 318 |
| `IMPORTIR OBAT TRADISIONAL DAN / ATAU SUPLEMEN MAKANAN` | 276 |
| `PENGOBATAN TRADISIONAL ATAU ALTERNATIF` | 150 |
| `GROSIR` | 39 |
| `SUB DISTRIBUTOR ATAU SUB AGEN` | 38 |
| `APOTEK/INSTALASI FARMASI` | 35 |
| `PENJUALAN LANGSUNG SATU/MULTI TINGKAT (MLM)` | 26 |
| `PENJUALAN OBAT TRADISIONAL DAN / ATAU SUPLEMEN MAKANAN MELALUI MEDIA ELEKTRONIK` | 22 |
| `PENJUALAN KOSMETIK MELALUI MEDIA ELEKTRONIK` | 15 |
| `BADAN USAHA` | 9 |

**`klasifikasi_sarana`** (4 nilai)

| Nilai | Baris |
|---|---:|
| `∅ (kosong)` | 196.197 |
| `SARANA RITEL MODERN` | 30.099 |
| `SARANA RITEL TRADISIONAL` | 24.318 |
| `SARANA GUDANG IMPORTIR/DISTRIBUTOR` | 6.941 |
| `SARANA GUDANG E-COMMERCE` | 52 |

**`kesimpulan`** (6 nilai)

| Nilai | Baris |
|---|---:|
| `MK` | 176.883 |
| `TMK` | 75.425 |
| `NULL` | 2.945 |
| `TTP` | 1.544 |
| `TDP` | 792 |
| `TMBB` | 18 |

**`status`** (17 nilai)

| Nilai | Baris |
|---|---:|
| `VERIFY4` | 165.946 |
| `VERIFY5` | 46.305 |
| `FINISHED` | 28.863 |
| `DRAFT_REVISE` | 5.099 |
| `VERIFY7` | 4.775 |
| `DRAFT` | 3.285 |
| `VERIFY6` | 1.008 |
| `VERIFY1` | 635 |
| `VERIFY2` | 619 |
| `DRAFT_PUSAT` | 461 |
| `VERIFY_P1` | 346 |
| `FINISHED_PUSAT` | 113 |
| `VERIFY_P3` | 85 |
| `VERIFY3` | 46 |
| `DRAFT_PUSAT_REVISE` | 13 |
| `VERIFY_P2` | 7 |
| `NULL` | 1 |

**`status_label`** (15 nilai)

| Nilai | Baris |
|---|---:|
| `OPERATOR PUSAT - VERIFIKASI` | 165.946 |
| `SUPERVISOR PUSAT - VERIFIKASI` | 46.305 |
| `SELESAI` | 28.863 |
| `OPERATOR - PERBAIKAN` | 5.099 |
| `DIREKTUR - VERIFIKASI` | 4.775 |
| `OPERATOR - DRAFT` | 3.285 |
| `SUPERVISOR 2 PUSAT - VERIFIKASI` | 1.008 |
| `SUPERVISOR - VERIFIKASI` | 635 |
| `SUPERVISOR 2 - VERIFIKASI` | 619 |
| `PEMERIKSAAN PUSAT - OPERATOR PUSAT - DRAFT` | 461 |
| `PEMERIKSAAN PUSAT - SUPERVISOR PUSAT - VERIFIKASI` | 346 |
| `∅ (kosong)` | 114 |
| `PEMERIKSAAN PUSAT - DIREKTUR - VERIFIKASI` | 85 |
| `KEPALA BALAI / LOKA - VERIFIKASI` | 46 |
| `PEMERIKSAAN PUSAT - OPERATOR PUSAT - PERBAIKAN` | 13 |
| `PEMERIKSAAN PUSAT - SUPERVISOR 2 PUSAT - VERIFIKASI` | 7 |

**`grade`** (4 nilai)

| Nilai | Baris |
|---|---:|
| `∅ (kosong)` | 213.459 |
| `A` | 24.645 |
| `B` | 9.752 |
| `C` | 9.686 |
| `N/A` | 65 |

**`hp_followup_name`** (20 nilai)

| Nilai | Baris |
|---|---:|
| `∅ (kosong)` | 256.821 |
| `Pembinaan` | 242 |
| `Peringatan Keras` | 119 |
| `Peringatan` | 112 |
| `Perintah Perbaikan` | 99 |
| `N/A` | 60 |
| `Perbaikan Hasil Inspeksi` | 49 |
| `Produk Dimusnahkan` | 35 |
| `Permintaan CAPA` | 20 |
| `Penghentian Sementara Kegiatan` | 16 |
| `Rekomendasi Peringatan Keras` | 16 |
| `Rekomendasi Penghentian Sementara Kegiatan` | 5 |
| `Rekomendasi Perbaikan` | 4 |
| `Rekomendasi Peringatan` | 2 |
| `Rekomendasi Penarikan dan/atau Perintah Pemusnahan atau Pengiriman Kembali / Re-Ekspor` | 1 |
| `Rekomendasi Pencabutan Izin/Perizinan Berusaha` | 1 |
| `Rekomendasi Pencabutan Sertifikat Cara Pembuatan Obat yang Baik` | 1 |
| `Produk Diamankan` | 1 |
| `Pencabutan Sertifikat CDOB` | 1 |
| `Pencabutan Izin/Perizinan Berusaha` | 1 |
| `Rekomendasi larangan produksi dan/atau mengedarkan untuk sementara waktu` | 1 |

**`tingkat_pemenuhan_cpob`** (4 nilai)

| Nilai | Baris |
|---|---:|
| `∅ (kosong)` | 256.746 |
| `Baik` | 425 |
| `Cukup` | 176 |
| `Kurang` | 175 |
| `Memuaskan` | 85 |
