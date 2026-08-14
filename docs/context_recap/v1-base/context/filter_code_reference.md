#VERIFIED CODE ANCHORS — STATUS, KESIMPULAN, GRADE, KOMODITI, SARANA, TUJUAN, DAN DOMAIN LAINNYA#

Codes listed here are VERIFIED anchors — use them directly, no re-probing. Codes NOT listed here
still exist: the database is the broadest catalog, this file is only the shortcut.
On conflict, this file wins ONLY where a row explicitly says so; everywhere else, query the database.

This file stores structure only — columns, codes, scope rules. Every number in an answer comes
from SQL executed this turn. Query only these tables: `mv_pemeriksaan`, `mv_pemeriksaan_log`,
`mv_pemeriksaan_petugas`, `mv_pemeriksaan_temuan`, `mv_pemeriksaan_timeline`,
`mv_pemeriksaan_jenis_pangan`, `mv_pemeriksaan_kategori_temuan`, `mv_kriteria_pemeriksaan`,
`coverage_balai`, `target_balai`.

## 0. Choosing the resolution path

| Case | Path |
|---|---|
| Concept exactly matches an anchor below | use the anchor directly |
| Same FAMILY as an anchor, code not listed | query `SELECT DISTINCT <col> FROM <table>` |
| User term is a LABEL, not a code | scoped ILIKE is correct: lock the category first, then filter inside it |
| Free text (nama_balai, nama_sarana) | `ILIKE` to discover, then `=` to count |
| More than one plausible column | ask the user — never pick silently |

**Code values do NOT collide across columns** in this database (unlike neo's registration domain).
Each column has its own namespace. But `komoditi` MEANS different things in different tables
(product category in fact, facility type in petugas) — pick the column by meaning.

**Close the code set — finding ONE code is not the end.**

Resolution feels finished the moment a code matches the user's word. It is not. A business
concept is a *set* of codes far more often than it is a single one. Resolution ends only when
this question has an answer: *is there another code that also belongs to the concept?*

## 1. Counting entity

| Question subject | Count |
|---|---|
| Pemeriksaan / inspeksi / total | `COUNT(DISTINCT id)` |
| Temuan / produk ditemukan | `COUNT(DISTINCT id_pemeriksaan)` on `mv_pemeriksaan_temuan` |
| Petugas | `COUNT(DISTINCT petugas_id)` on `mv_pemeriksaan_petugas` |
| Langkah workflow | `COUNT(DISTINCT id_steps)` on `mv_pemeriksaan_log` |
| Balai | `COUNT(DISTINCT nama_upt)` on `mv_pemeriksaan` |

- `COUNT(*)` on `mv_pemeriksaan` is safe (no versioning), but `COUNT(DISTINCT id)` is preferred
  for clarity and consistency.
- Never `COUNT(*)` on child tables to count pemeriksaan — use `COUNT(DISTINCT id_pemeriksaan)`.

## 2. Status codes — workflow pipeline

| Stage | Status Codes | Label |
|---|---|---|
| Draft | `DRAFT`, `DRAFT_PUSAT` | Operator membuat draft |
| Revise | `DRAFT_REVISE`, `DRAFT_PUSAT_REVISE` | Operator merevisi |
| Verifikasi 1 | `VERIFY1` | Supervisor Balai |
| Verifikasi 2 | `VERIFY2` | Supervisor 2 Balai |
| Kepala Balai | `VERIFY3` | Kepala Balai/Loka |
| Operator Pusat | `VERIFY4` | Operator Pusat Jakarta |
| Supervisor Pusat | `VERIFY5` | Supervisor Pusat |
| Supervisor 2 Pusat | `VERIFY6` | Supervisor 2 Pusat |
| Direktur | `VERIFY7` | Direktur |
| Verifikasi Pusat 1 | `VERIFY_P1` | Supervisor Pusat (pemeriksaan pusat) |
| Verifikasi Pusat 2 | `VERIFY_P2` | Supervisor 2 Pusat (pemeriksaan pusat) |
| Verifikasi Pusat 3 | `VERIFY_P3` | Direktur (pemeriksaan pusat) |
| Selesai | `FINISHED`, `FINISHED_PUSAT` | Pemeriksaan selesai |

Rules:
- "Sedang diproses" = semua status selain FINISHED/FINISHED_PUSAT
- "Draft" = DRAFT + DRAFT_REVISE + DRAFT_PUSAT + DRAFT_PUSAT_REVISE
- "Selesai" = FINISHED + FINISHED_PUSAT
- "Dalam verifikasi" = VERIFY1 + VERIFY2 + VERIFY3 + VERIFY4 + VERIFY5 + VERIFY6 + VERIFY7
- Pemeriksaan pusat (jalur P): DRAFT_PUSAT -> VERIFY_P1 -> VERIFY_P2 -> VERIFY_P3 -> FINISHED_PUSAT
- DRAFT_REVISE = pemeriksaan dikembalikan ke operator untuk perbaikan

## 3. Kesimpulan (inspection result)

| Code | Label | Meaning |
|---|---|---|
| `MK` | Memenuhi Kondisi | Sarana MEMENUHI semua syarat. 176.766 (69%). |
| `TMK` | Tidak Memenuhi Kondisi | Sarana TIDAK memenuhi syarat. 75.377 (29%). |
| `TTP` | Temuan Tindak Pidana | Ada pelanggaran hukum. 1.541 (0,6%). |
| `TDP` | Temuan Dasar Pelanggaran | Pelanggaran mendasar. 789 (0,3%). |
| `TMBB` | Tidak Memenuhi Batas Bahan | Di atas batas bahan berbahaya. 18 (hanya BAHAN BERBAHAYA). |
| `NULL` | Belum ada kesimpulan | 2.943 (1,1%). |

Rules:
- "Bermasalah" = TMK + TTP + TDP + TMBB (semua yang bukan MK)
- "Memenuhi" = MK saja
- "Tidak memenuhi" = TMK saja
- TMBB hanya muncul untuk komoditi BAHAN BERBAHAYA
- Kesimpulan NULL = pemeriksaan masih dalam proses atau belum diisi

## 4. Grade

| Code | Label | Meaning |
|---|---|---|
| `A` | Grade A | Terbaik. 24.618. |
| `B` | Grade B | Cukup. 9.745. |
| `C` | Grade C | Terburuk. 9.682. |
| `N/A` | Tidak Dinilai | 65. |
| `NULL` | Belum dinilai | 213.324 (83%). |

Rules:
- Grade HANYA diisi untuk pemeriksaan tertentu (rutin, intensifikasi)
- Sertifikasi (CPOB/CPKB) TIDAK punya grade
- Grade muncul saat IN_PROGRESS, bukan hanya FINISHED
- 83% pemeriksaan tidak punya grade — jangan anggap NULL = grade terburuk

## 5. Komoditi (product category)

| Code (fact) | Mapping (target) | Count |
|---|---|---|
| `PRODUK PANGAN` | PRODUK PANGAN | 107.224 (42%) |
| `OBAT` | OBAT | 82.838 (32%) |
| `KOSMETIK` | KOSMETIKA | 39.313 (15%) |
| `OBAT TRADISIONAL` | OBAT TRADISIONAL (OT) | 19.925 (8%) |
| `SUPLEMEN KESEHATAN` | SUPLEMEN KESEHATAN | 7.124 (3%) |
| `NARKOTIKA` | OBAT | 273 |
| `PSIKOTROPIKA` | OBAT | 252 |
| `OBAT OBAT TERTENTU` | OBAT | 176 |
| `PREKURSOR` | OBAT | 118 |
| `BAHAN BERBAHAYA` | OBAT KUASI | 108 |
| `PRODUK BIOLOGI DAN SARANA KHUSUS` | OBAT | 55 |
| `BAHAN BAKU OBAT` | OBAT | 17 |
| `BAHAN OBAT` | OBAT | 11 |

Rules:
- Gunakan `komoditi` di `mv_pemeriksaan` (UPPER CASE) untuk filter
- Gunakan `mapping_komoditi_target_balai` untuk join ke `target_balai`
- NARKOTIKA, PSIKOTROPIKA, OBAT OBAT TERTENTU, PREKURSOR, PRODUK BIOLOGI, BAHAN BAKU OBAT, BAHAN OBAT -> mapping ke OBAT
- BAHAN BERBAHAYA -> mapping ke OBAT KUASI
- KOSMETIK -> mapping ke KOSMETIKA (note: beda ejaan!)

## 6. Sarana (facility type)

| Code | Label | Count |
|---|---|---|
| `DISTRIBUSI` | Sarana Distribusi | 141.469 (55%) |
| `PELAYANAN` | Sarana Pelayanan | 72.633 (28%) |
| `PRODUKSI` | Sarana Produksi | 43.331 (17%) |

Rules:
- DISTRIBUSI = toko, swalayan, distributor, gudang
- PELAYANAN = apotek, klinik, rumah sakit, PKM
- PRODUKSI = pabrik obat, pabrik kosmetik, industri pangan
- PRODUKSI punya TMK rate tertinggi (36,7%)
- NULL (1 baris) = data tidak lengkap

## 7. Tujuan Pemeriksaan (inspection purpose)

| Code | Label | Count | TMK Rate |
|---|---|---|---|
| `PEMERIKSAAN RUTIN` | Inspeksi Berkala | 200.592 (78%) | 29,4% |
| `INTENSIFIKASI PENGAWASAN PANGAN` | Intensifikasi Pangan | 16.231 (6%) | 28,7% |
| `INTENSIFIKASI VAKSIN` | Intensifikasi Vaksin | 7.696 (3%) | 9,7% |
| `RENCANA AKSI / INTENSIFIKASI PENGAWASAN` | Rencana Aksi | 7.005 (3%) | 53,1% |
| `SERTIFIKASI` | Sertifikasi CPOB/CPKB | 5.323 (2%) | 26,8% |
| `NATAL DAN TAHUN BARU` | Operasi Nataru | 4.847 | 29,1% |
| `IDUL FITRI` | Operasi Lanjut | 3.925 | 35,6% |
| `SURVEILANS SMKPO` | Surveilans | 3.336 | 25,9% |
| `KASUS` | Investigasi Kasus | 2.471 | 38,6% |
| `PERMINTAAN REGISTRASI` | Permintaan | 1.173 | — |
| `SERTIFIKASI CDOB` | Sertifikasi CDOB | 1.113 | 30,7% |
| NULL | Belum diisi | 942 | — |

Rules:
- 36 tujuan total. Top 11 di atas = 99% data.
- RENCANA AKSI punya TMK rate tertinggi (53,1%) — memang inspeksi follow-up
- KASUS juga tinggi (38,6%) — investigasi atas laporan
- INTENSIFIKASI VAKSIN rendah (9,7%) — vaksin sudah highly regulated
- NULL = pemeriksaan belum lengkap (sama dengan tanggal_mulai NULL)

## 8. Issue counts (tx_critical/major/minor)

- Hanya 20,2% pemeriksaan punya semua kolom issues terisi
- 27,7% punya minimal satu kolom issues
- Issues berasal dari checklist audit (kriteria), BUKAN dari temuan produk
- Issues dan temuan adalah DIMENSI BERBEDA dari hasil inspeksi

| Kolom | Not-null | Max | Mean |
|---|---|---|---|
| `tx_critical_issue` | 55.165 (21%) | 17 | ~0,4 |
| `tx_major_issue` | 66.560 (26%) | 44 | ~0,5 |
| `tx_minor_issue` | 67.142 (26%) | 41 | ~0,7 |

## 9. Temuan (product findings)

**tp_kategori** — top violation types:

| Kategori | Count | Pct |
|---|---|---|
| TIE (Tanpa Izin Edar) | 154.115 | 51,9% |
| ED (Expire Date / Kedaluwarsa) | 58.730 | 19,8% |
| Temuan Obat Keras | 21.774 | 7,3% |
| Rusak | 10.265 | 3,5% |
| BKO (Bahan Kimia Obat) | 9.784 | 3,3% |
| Substandard/Rusak | 8.967 | 3,0% |
| BKO, TIE | 6.810 | 2,3% |
| Illegal/TIE | 6.280 | 2,1% |
| Lain - Lain | 6.193 | 2,1% |
| Kedaluwarsa | 3.799 | 1,3% |
| TMK Label | 3.147 | 1,1% |

Multi-value: "BKO, TIE" = produk punya 2 pelanggaran. `mv_pemeriksaan_kategori_temuan` adalah
exploded version (49 kategori bersih).

**tp_tindakan** — what happens to found products:

| Tindakan | Count | Pct |
|---|---|---|
| Pemusnahan | 180.016 | 60,6% |
| Dikembalikan kepada produsen/importir | 33.036 | 11,1% |
| Pengamanan | 28.989 | 9,8% |
| Dimusnahkan | 16.508 | 5,6% |
| Diamankan | 11.064 | 3,7% |
| Pendataan | 9.162 | 3,1% |
| Penarikan | 4.444 | 1,5% |

Sinonim: "Pemusnahan" = "Dimusnahkan", "Pengamanan" = "Diamankan".

**tp_pelanggaran**: 99,996% NULL — kolom mati, jangan pakai.
**tp_netto**: 99,998% NULL — kolom mati, jangan pakai.

## 10. Jenis Pangan (food type — exploded array)

Top jenis pangan per TMK rate:

| Jenis | Count | TMK Rate |
|---|---|---|
| Garam | 944 | 45,4% |
| Air Minum Dalam Kemasan | 3.611 | 39,3% |
| Pangan Olahan Daging/Ikan/Unggas | 1.625 | 29,2% |
| Produk Bakeri | 1.039 | 29,5% |
| Lemak dan Minyak Nabati | 1.028 | 28,5% |
| Kopi | 764 | 26,2% |
| Gula dan Pemanis | 527 | 24,5% |
| Dry Food | 29.504 | 22,0% |
| Frozen | 8.605 | 21,7% |
| Chill | 8.411 | 21,2% |

Garam dan AMDK punya TMK rate tertinggi.

## 11. Kategori Temuan (cleaned, 49 values)

`mv_pemeriksaan_kategori_temuan.tp_kategori` adalah versi bersih dari `mv_pemeriksaan_temuan.tp_kategori`.
Multi-value strings dipecah menjadi baris terpisah. 49 nilai (vs 106 di temuan).

Masih ada inkonsistensi:
- "TIE (Tanpa Izin Edar)" (128.666) vs "TIE" (30) — seharusnya disatukan
- "Rusak" vs "Substandard/Rusak" — overlap
- "Mengandung bahan berbahaya/bahan dilarang (berdasarkan SE)" vs "(daftar PW)" vs "dilarang." — varian

## 12. Coverage Balai

- 88 balai, 514 kabupaten, 668 mapping rows
- 1 kabupaten belum diinspeksi: Kabupaten Intan Jaya (LOKA POM DI KABUPATEN MIMIKA)
- Top balai by kabupaten: Surabaya (38), Semarang (35), Bandung (27), Medan (26), Jayapura (22)
- Format: Title Case ("Kabupaten Aceh Barat")

## 13. Target Balai

- 532 rows = 76 balai × 7 komoditi
- Tahun 2024 ONLY — tidak ada data historis target
- 7 komoditi: Kosmetika, Obat, Obat Kuasi, Obat Tradisional (OT), Produk Pangan, Rokok, Suplemen Kesehatan
- Target: penandaan, pengawasan, pengujian, pengujian_pangan, pengujian_pangan_fortifikasi, sarana_distribusi, sarana_produksi
- 15 nama_upt unmatched: 6 DIREKTORAT (central office), 2 DEMO (test data), 7 LOKA POM (sub-balai)

## 14. Workflow Log

- Avg 5,09 langkah per pemeriksaan (p50=4, max=75)
- 78,7% punya 4-6 langkah (jalur normal)
- 12,4% pernah masuk DRAFT_REVISE (revisi)
- Avg waktu DRAFT ke FINISHED: 307 hari (p50=212 hari)
- 64 baris corrupt (null id_steps + status + created_at)

## 15. Timeline

- mulai_kabalai: avg 49 hari, p50=22, max 526.265 (outlier)
- kabalai_direktur: avg 122 hari, p50=82, max 996
- 33.756 pemeriksaan sudah sampai direktur
- 30.699 orphan records (12%)
