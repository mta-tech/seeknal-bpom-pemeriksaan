# 04 — Kamus Unique Value (Semua Nilai Kategorikal + Distribusi)

> Daftar lengkap nilai + distribusi untuk semua kolom kategorikal yang terverifikasi dari query.
> Gunakan ini sebagai cheat-sheet untuk filter — jangan probe `SELECT DISTINCT` setiap turn.

## 4.1 `sarana` (3 nilai + 1 NULL)

| Nilai | Count | % |
|---|---|---|
| DISTRIBUSI | 141.477 | 55,0% |
| PELAYANAN | 72.638 | 28,2% |
| PRODUKSI | 43.340 | 16,8% |
| (NULL) | 1 | 0,0004% |

## 4.2 `komoditi` (13 nilai)

| Nilai (UPPER CASE) | Count | % | Mapping ke target |
|---|---|---|---|
| PRODUK PANGAN | 107.236 | 41,7% | PRODUK PANGAN |
| OBAT | 82.845 | 32,2% | OBAT |
| KOSMETIK | 39.313 | 15,3% | KOSMETIKA |
| OBAT TRADISIONAL | 19.925 | 7,7% | OBAT TRADISIONAL (OT) |
| SUPLEMEN KESEHATAN | 7.124 | 2,8% | SUPLEMEN KESEHATAN |
| NARKOTIKA | 273 | 0,1% | OBAT |
| PSIKOTROPIKA | 252 | 0,1% | OBAT |
| OBAT OBAT TERTENTU | 176 | 0,1% | OBAT |
| PREKURSOR | 117 | 0,05% | OBAT |
| BAHAN BERBAHAYA | 108 | 0,04% | OBAT KUASI |
| PRODUK BIOLOGI DAN SARANA KHUSUS | 55 | 0,02% | OBAT |
| BAHAN BAKU OBAT | 17 | 0,01% | OBAT |
| BAHAN OBAT | 11 | 0,004% | OBAT |

**Aturan**: filter pakai `komoditi = 'OBAT'` (exact UPPER). Join ke target pakai `mapping_komoditi_target_balai`.
"Semua obat" = OBAT + NARKOTIKA + PSIKOTROPIKA + OBAT OBAT TERTENTU + PREKURSOR + PRODUK BIOLOGI + BAHAN BAKU OBAT + BAHAN OBAT.

## 4.2B — Istilah yang User KAI Pakai tapi TIDAK ADA di Warehouse (gap)

| Istilah | Pertanyaan user | Status di warehouse |
|---|---|---|
| **BUPN** | 18 ("sarana BUPN apa saja...") | 🔴 Tidak ada kolom. Mungkin = `klasifikasi_sarana`/`legal`? Perlu investigasi |
| **SIPT** | 13 ("ketepatan waktu pelaporan SIPT") | 🔴 Tidak ada. Proxy = `day_input_mulai` |
| **Nomor notifikasi** | 7 ("tidak memiliki nomor notifikasi") | 🔴 Tidak ada. Ada di DB `penandaan`/`rpo_v2` |
| **Sampling** | 3 ("jumlah sampel yang disampling") | 🔴 Ada di DB `pengujian`, bukan pemeriksaan |
| **Nilai sarana** (mentah) | 2 ("grading A jika nilai sarana A dan B") | 🟡 Hanya `grade` final, tidak ada nilai mentah |
| **CPOTB** | 1 | 🟡 Ada CPOB/CPKB, bukan CPOTB |

Lihat [12_belum_ditemukan_dan_eksternal.md](12_belum_ditemukan_dan_eksternal.md) §12.2B untuk detail.

## 4.3 `kesimpulan` (6 nilai)

| Nilai | Count | % | Arti |
|---|---|---|---|
| MK | ~176.778 | ~69% | Memenuhi Kondisi (patuh) |
| TMK | ~75.386 | ~29% | Tidak Memenuhi Kondisi (bandel) |
| TTP | 1.540 | 0,6% | Kode administratif (BUKAN pidana produk — hanya 0,3% punya temuan) |
| TDP | 790 | 0,3% | Kode administratif |
| TMBB | 18 | 0,007% | Khusus BAHAN BERBAHAYA |
| NULL | 2.944 | 1,1% | Belum ada kesimpulan |

**"Bermasalah"** = TMK + TTP + TDP + TMBB.
**⚠️ TTP/TDP BUKAN pelanggaran produk**: TTP hanya 0,3% punya temuan (lebih rendah dari MK 2,3%).
Ini kode administratif/perizinan.

**⚠️ Mapping full-text ↔ kode** (dari 963 pertanyaan user KAI — user pakai BANYAK varian):
| User bilang | Kode DB | Count pertanyaan |
|---|---|---|
| "Memenuhi Ketentuan" / "sesuai" | `MK` | 131 |
| "Tidak Memenuhi Ketentuan" / "TMS" / "tidak sesuai" | `TMK` | 166 |
| "MK"/"TMK" (kode langsung) | `MK`/`TMK` | banyak |

Sistem wajib menerjemahkan full-text → kode sebelum query.

## 4.4 `status` (17 nilai) — Workflow Pipeline

| Kode | Label (verified) | Count di fact (status terakhir) | % |
|---|---|---|---|
| VERIFY4 | Operator Pusat - Verifikasi | **165.891** | **64,4%** |
| VERIFY5 | Supervisor Pusat - Verifikasi | 46.327 | 18,0% |
| FINISHED | Selesai | 28.863 | 11,2% |
| DRAFT_REVISE | Operator - Perbaikan | 5.111 | 2,0% |
| VERIFY7 | Direktur - Verifikasi | 4.737 | 1,8% |
| DRAFT | Operator - Draft | 3.167 | 1,2% |
| VERIFY6 | Supervisor 2 Pusat - Verifikasi | ~1.500 | ~0,6% |
| DRAFT_PUSAT | Pemeriksaan Pusat - Draft | ~500 | ~0,2% |
| (lainnya) | | < 1% each | |

**"Selesai"** = `status IN ('FINISHED', 'FINISHED_PUSAT')`.
**"Dalam proses"** = `status NOT IN ('FINISHED', 'FINISHED_PUSAT')`.
**"Draft"** = `status IN ('DRAFT', 'DRAFT_REVISE', 'DRAFT_PUSAT', 'DRAFT_PUSAT_REVISE')`.

## 4.5 `grade` (4 nilai + NULL)

| Nilai | Count | % dari non-NULL | % dari total |
|---|---|---|---|
| A | 24.618 | 56,0% | 9,6% |
| B | 9.747 | 22,2% | 3,8% |
| C | 9.682 | 22,0% | 3,8% |
| N/A | 65 | 0,1% | 0,03% |
| NULL | 213.344 | — | **82,9%** |

Grade hanya untuk RUTIN/INTENSIFIKASI. Sertifikasi TIDAK ber-grade.
**83% NULL = structural**, bukan missing.

## 4.6 `tujuan_pemeriksaan` (36 nilai — top 12)

| Nilai | Count | % | TMK % |
|---|---|---|---|
| PEMERIKSAAN RUTIN | 200.604 | 78% | 29,4% |
| INTENSIFIKASI PENGAWASAN PANGAN | 16.231 | 6% | 28,7% |
| INTENSIFIKASI VAKSIN | 7.696 | 3% | 9,7% |
| RENCANA AKSI / INTENSIFIKASI PENGAWASAN | 7.005 | 3% | **53,1%** |
| SERTIFIKASI | 5.327 | 2% | 26,8% |
| NATAL DAN TAHUN BARU | 4.847 | 2% | 29,1% |
| IDUL FITRI | 3.925 | 2% | 35,6% |
| SURVEILANS SMKPO | 3.337 | 1% | 25,9% |
| KASUS | 2.471 | 1% | 38,6% |
| PERMINTAAN REGISTRASI | 1.173 | 0,5% | — |
| SERTIFIKASI CDOB | 1.113 | 0,4% | 30,7% |
| (NULL) | 942 | 0,4% | — |

**Insight**: RENCANA AKSI punya TMK rate tertinggi (53%) — memang inspeksi follow-up dari kecurigaan.
RUTIN = baseline kepatuhan populasi (~29%).

## 4.7 `jenis_sarana` (24 nilai — top 12)

| Nilai | Count | % |
|---|---|---|
| PANGAN | 61.539 | 23,9% |
| KOSMETIK | 36.719 | 14,3% |
| APOTEK | 27.503 | 10,7% |
| PANGAN MD | 26.300 | 10,2% |
| PUSAT KESEHATAN MASYARAKAT (PKM) | 19.753 | 7,7% |
| OBAT TRADISIONAL | 16.923 | 6,6% |
| PANGAN IRT (CPPB - IRT) | 10.282 | 4,0% |
| BALAI PENGOBATAN / KLINIK | 10.167 | 3,9% |
| INTENSIFIKASI PENGAWASAN KHUSUS | 9.061 | 3,5% |
| TOKO OBAT | ~8.700 | ~3,4% |
| RUMAH SAKIT | ~5.000 | ~1,9% |
| SWALAYAN | ~4.500 | ~1,7% |

## 4.8 `tl_saran_names` (array — 10 nilai utama saat di-unnest)

| Saran (tindak lanjut) | Count |
|---|---|
| Pembinaan | 133.434 |
| Peringatan | 65.628 |
| Peringatan Keras | 24.922 |
| N/A | 3.080 |
| Penghentian Sementara Kegiatan | 1.849 |
| Pembinaan Teknis | 1.470 |
| Lain-lain | 810 |
| Pencabutan Izin | 355 |
| Pengamanan | 350 |
| Produk Dimusnahkan | 92 |

**Piramida penegakan**: mayoritas dibina (133k), sedikit dihukum berat. Rasio Pencabutan : Pembinaan ≈ 1 : 376.

## 4.9 `tp_kategori` (106 nilai mentah — top 12)

| Kategori | Count | % |
|---|---|---|
| TIE (Tanpa Izin Edar) | 154.143 | 51,9% |
| ED (Expire Date / Kedaluwarsa) | 58.731 | 19,8% |
| Temuan Obat Keras | 21.776 | 7,3% |
| Rusak | 10.265 | 3,5% |
| BKO | 9.784 | 3,3% |
| Substandard/Rusak | 8.968 | 3,0% |
| BKO, TIE (Tanpa Izin Edar) | 6.810 | 2,3% |
| Illegal/TIE | 6.283 | 2,1% |
| Lain - Lain | 6.193 | 2,1% |
| Kedaluwarsa | 3.799 | 1,3% |
| TMK Label | 3.147 | 1,1% |

**⚠️ Sinonim teridentifikasi** (perlu standardisasi):
- "ED (Expire Date / Kedaluwarsa)" (58.731) vs "Kedaluwarsa" (3.799) → gabung
- "Rusak" (10.265) vs "Substandard/Rusak" (8.968) → overlap
- "TIE" muncul dalam 6+ varian (standalone, BKO+TIE, Illegal/TIE, dst.)

## 4.10 `tp_tindakan` (126 nilai — top 10)

| Tindakan | Count | % |
|---|---|---|
| Pemusnahan | 180.046 | 60,7% |
| Dikembalikan kepada produsen / importir | 33.036 | 11,1% |
| Pengamanan | 28.989 | 9,8% |
| Dimusnahkan | 16.511 | 5,6% |
| Diamankan | 11.064 | 3,7% |
| Pendataan | 9.164 | 3,1% |
| Penarikan | 4.444 | 1,5% |
| Pemusnahan, Pendataan | 2.157 | 0,7% |
| Dikembalikan..., Pendataan | 1.755 | 0,6% |

**Sinonim**: "Pemusnahan" = "Dimusnahkan" (65k+17k = 82k total). "Pengamanan" = "Diamankan".

## 4.11 `tp_negara` (1.299 nilai — top 15)

| Negara (upper trim) | Count |
|---|---|
| INDONESIA | 190.735 |
| CHINA | 16.681 |
| MALAYSIA | 9.132 |
| THAILAND | 2.940 |
| KOREA | 1.827 |
| CINA | 1.649 |
| USA | 1.028 |
| LOKAL | 842 |
| IND | 688 |
| INDIA | 560 |
| TIONGKOK | 566 |
| PRC | 396 |
| JEPANG | 396 |
| VIETNAM | 390 |
| FILIPINA | 385 |

**⚠️ 1.299 "negara" berbeda.** Inkonsistensi parah:
- China = CHINA (16.681) + CINA (1.649) + TIONGKOK (566) + PRC (396) = 19.292 total
- "-" sebagai negara: 53.063 baris (data hilang tersamar)
- IND (688) ambigu: India atau Indonesia?
- LOKAL (842) vs INDONESIA (190.735): konsep sama, label beda

## 4.12 `jenis_id` petugas (25 kode — semua)

| jenis_id | Count |
|---|---|
| 16 | 140.617 |
| 13 | 81.763 |
| 109 | 60.104 |
| 5 | 59.742 |
| 107 | 43.471 |
| 15 | 39.043 |
| 108 | 22.450 |
| 18 | 22.448 |
| 10 | 22.134 |
| 14 | 15.750 |
| 105 | 14.847 |
| 17 | 14.406 |
| 106 | 10.349 |
| 748 | 8.737 |
| 747 | 7.127 |
| 4 | 7.018 |
| 7 | 6.032 |
| 8 | 3.570 |
| 9 | 1.073 |
| 12 | 804 |
| 11 | 215 |
| 6 | 134 |
| **211265** | **26** |
| **211337** | **2** |
| **223447** | **2** |

**3 kode 6-digit** (211265, 211337, 223447) = kode tak dikenal. Bukan FK petugas_id (max petugas_id < 100.000).
Kemungkinan ID dari tabel referensi yang tidak ada di DB ini. Perlu konfirmasi tim sumber.

## 4.13 `tp_unit_id` (92 nilai — top 15)

| tp_unit_id | Count | Avg tp_jml_temuan |
|---|---|---|
| 281 | 70.350 | 199,86 |
| 241 | 48.105 | 33,24 |
| 282 | 37.607 | 35,23 |
| 258 | 31.753 | 80,84 |
| 295 | 15.495 | 22,75 |
| 297 | 14.174 | 41,35 |
| 291 | 11.299 | 37,59 |
| 276 | 10.267 | 54,90 |
| 285 | 10.172 | 41,81 |
| 261 | 10.152 | 13,79 |
| **263** | **8.087** | **2.500.771** ← outlier (INFALGIN datetime terselip) |
| 254 | 4.130 | 54,52 |

**11 kode 6-digit** (211214-220008): kode tak dikenal. Perlu kamus satuan dari tim sumber.

## 4.14 Komoditi di `target_balai` (7 nilai — Title Case)

| Nilai | vs fact komoditi |
|---|---|
| Kosmetika | KOSMETIK (beda ejaan!) |
| Obat | OBAT |
| Obat Kuasi | BAHAN BERBAHAYA |
| Obat Tradisional (OT) | OBAT TRADISIONAL |
| Produk Pangan | PRODUK PANGAN |
| Rokok | (tidak ada di fact!) |
| Suplemen Kesehatan | SUPLEMEN KESEHATAN |

**⚠️ Selalu pakai `mapping_komoditi_target_balai` sebagai bridge key.** Jangan join `komoditi` langsung.
