# 11 — Kualitas Data & Anomali

> Vonis per anomali: ERROR (data rusak), VALID (fenomena nyata), SUSPICIOUS (perlu investigasi).
> Setiap vonis disertai bukti dari query.

## 11.1 Tabel Vonis Anomali

### Outlier Tanggal

| Anomali | Vonis | Detail | Filter |
|---|---|---|---|
| tanggal_mulai = 0004-02-21 | 🔴 ERROR | Mustahil; typo tahun. id=36925. | `tanggal_mulai >= '2015-01-01'` |
| tanggal_mulai = 0020-12-03 | 🔴 ERROR | Mustahil. id=26813 (Cargill). | sama |
| tanggal_mulai = 1922-1928 | 🔴 ERROR | 9 record. Kemungkinan typo 2022-2028. | sama |
| tanggal_mulai = 1970-01-01 | 🔴 ERROR | Unix epoch default (NULL → 0). | sama |
| tanggal_mulai = 2027 (future) | 🟠 SUSPICIOUS | Bisa typo, bisa jadwal rencana. | `tanggal_mulai <= CURRENT_DATE` |

**Konsekuensi berantai**: Error tanggal_mulai → `day_input_mulai` meledak (max 736.685 hari = 2018 tahun)
→ `agg.avg_day_*` tercemar → dashboard menampilkan durasi tidak masuk akal.
**Bersihkan di hulu (fact), otomatis memperbaiki hilir.**

### Durasi Ekstrem

| Anomali | Vonis | Detail |
|---|---|---|
| `day_input_mulai` max 736.685 | 🔴 ERROR | Konsekuensi tanggal error. Jangan dipakai untuk filtering. |
| `day_mulai_selesai` max 34.706 | 🔴 ERROR | ~95 tahun. Tidak valid. |
| `mulai_kabalai` max 526.265 (timeline) | 🔴 ERROR | ~1441 tahun. Outlier tanggal. |
| `kabalai_direktur` max 996 (timeline) | 🟠 OUTLIER | ~2,7 tahun. Mungkin valid (kasus ekstrem). |

### Nilai Negatif

| Anomali | Vonis | Detail |
|---|---|---|
| `tp_jml_temuan` min -196 | 🔴 ERROR | Jumlah tidak bisa negatif. Kemungkinan record koreksi tak berlabel. |
| `tp_harga_total` min -5.360.000 | 🔴 ERROR | Harga tidak bisa negatif. |

### Data DEMO/Test

| Anomali | Vonis | Count | Filter |
|---|---|---|---|
| nama_upt = 'DEMO BALAI BESAR' | 🟠 TEST | 3 | `nama_upt NOT IN ('DEMO BALAI BESAR','DEMO TIPE A')` |
| nama_upt = 'DEMO TIPE A' | 🟠 TEST | 90 | sama |

**Total 93 baris test** yang harus diexclude dari semua analisis.

## 11.2 943 Record NULL Tanggal — Vonis: OPERASIONAL TERSEBAR

```sql
SELECT min(id), max(id), max(id)-min(id) AS span,
  count(DISTINCT date_trunc('day',sync)) AS batch_sync,
  min(tanggal_input), max(tanggal_input),
  count(DISTINCT status), count(DISTINCT nama_upt)
FROM mv_pemeriksaan WHERE tanggal_mulai IS NULL AND tujuan_pemeriksaan IS NULL;
-- id: 284 → 289.133 (span 288.849 — nyaris penuh!)
-- tanggal_input: 2020-03-16 → 2026-08-11 (6+ tahun)
-- status: 5 variasi
-- nama_upt: 84 balai
```

**❌ Hipotesis lama**: "942 record NULL = satu batch migrasi lama."
**✅ Vonis**: **TERBANTAHKAN.** Ini NULL operasional tersebar — inspeksi yang dibuat (tanggal_input ada)
tapi tidak pernah dimulai (tanggal_mulai/selesai/day_*/tujuan semua NULL serentak).
Tersebar di seluruh rentang id, 6+ tahun, 84 balai, 5 status.

**Pola polymorfit**: tanggal_mulai + tanggal_selesai + day_* + tujuan_pemeriksaan SEMUA NULL bersamaan.
Tapi tanggal_input terisi (0 NULL). Artinya record dibuat di sistem tapi inspeksi tidak jalan.

**Implikasi**: Tidak bisa dibuang begitu saja — perlu investigasi mengapa inspeksi tidak dimulai.

## 11.3 30.699 Orphan Timeline — Vonis: DRAFT BATAL (dengan catatan)

```sql
SELECT t.status, count(*) AS jml, count(*) FILTER(WHERE t.tgl_end IS NULL) AS belum_selesai
FROM mv_pemeriksaan_timeline t
WHERE NOT EXISTS (SELECT 1 FROM mv_pemeriksaan p WHERE p.id = t.id_pemeriksaan)
GROUP BY 1 ORDER BY jml DESC;
```

| Status orphan | Count | tgl_end NULL | Vonis |
|---|---|---|---|
| **DRAFT** | **29.874** | 13.548 | ✅ Aman — draft dibatalkan, tak ter-cascade delete |
| DRAFT_PUSAT | 450 | 195 | ✅ Aman |
| DRAFT_REVISE | 319 | 0 | ✅ Aman |
| VERIFY1 | 28 | 0 | 🟠 Sedikit mencurigakan |
| VERIFY4 | 18 | 0 | 🟠 |
| VERIFY3 | 5 | 0 | 🟠 |
| **FINISHED** | **3** | 0 | **🔴 MENCURIGAKAN** — inspeksi selesai tapi fact hilang! |
| VERIFY5 | 2 | 0 | 🔴 |
| VERIFY7 | 1 | 0 | 🔴 |

**Mayoritas (30.643 dari 30.699) = draft yang dibatalkan** — aman diabaikan.
**6 record mencurigakan** (3 FINISHED + 2 VERIFY5 + 1 VERIFY7) = inspeksi yang sudah maju jauh
tapi fact-nya hilang. Kecil tapi menunjukkan bug penghapusan yang tidak ter-cascade (buktikan absennya FK).

**Filter orphan**: `WHERE EXISTS (SELECT 1 FROM mv_pemeriksaan p WHERE p.id = t.id_pemeriksaan)`.

## 11.4 Kontaminasi Nilai Sitaan

| Anomali | Vonis | Detail |
|---|---|---|
| INFALGIN Rp 7,08 T | 🔴 ERROR | `tp_jml_temuan=20221092024` (datetime terselip). 91% dari total bruto. |
| "&AMP;AMP; GLOW WATER CREAM" 3× | 🔴 ERROR | HTML encoding error di nama + nilai Rp 36,4 M × 3. |
| TEH BUBUK Rp 82,5 jt/unit | 🟠 OUTLIER | Kemungkinan salah unit (bukan per pcs). |
| tp_harga_total negatif (128) | 🔴 ERROR | Lihat §11.1. |

**Nilai bersih setelah pembersihan**: Rp 199,8 M (bukan Rp 7,74 T). Lihat [08](08_nilai_sitaan_dan_produk.md).

## 11.5 Kode Tak Dikenal

| Kolom | Kode | Count | Vonis |
|---|---|---|---|
| `jenis_id` (petugas) | 211265 | 26 | 🟠 ID 6-digit, bukan FK petugas (max <100k) |
| `jenis_id` | 211337 | 2 | 🟠 |
| `jenis_id` | 223447 | 2 | 🟠 |
| `tp_unit_id` (temuan) | 211214-220008 | 11 nilai | 🟠 Kode 6-digit, tak berkamus |

Range ID (211214-223447) overlap antara jenis_id dan tp_unit_id → kemungkinan dari tabel referensi
yang sama yang tidak ada di DB ini. Perlu konfirmasi tim sumber.

## 11.6 Sinonim & Inkonsistensi Label

| Kolom | Varian | Count | Solusi |
|---|---|---|---|
| tp_kategori | "TIE (Tanpa Izin Edar)" vs "TIE" | 154.143 vs 30 | Satukan |
| tp_kategori | "ED (Expire Date...)" vs "Kedaluwarsa" | 58.731 vs 3.799 | Satukan |
| tp_kategori | "Rusak" vs "Substandard/Rusak" | 10.265 vs 8.968 | Tinjau overlap |
| tp_tindakan | "Pemusnahan" vs "Dimusnahkan" | 180.046 vs 16.511 | Satukan |
| tp_tindakan | "Pengaminan" vs "Diamankan" | 28.989 vs 11.064 | Satukan |
| tp_negara | CHINA/CINA/TIONGKOK/PRC | 4+ varian | Normalisasi |
| komoditi | "KOSMETIK" (fact) vs "Kosmetika" (target) | — | Pakai `mapping_komoditi_target_balai` |

## 11.7 Structural NULL (BUKAN cacat)

Kolom-kolom berikut punya NULL rate tinggi tetapi **bukan data hilang** — kolom kondisional:

| Kolom | Null % | Berlaku hanya untuk |
|---|---|---|
| grade | 82,9% | RUTIN/INTENSIFIKASI (bukan sertifikasi) |
| klasifikasi_sarana | 76,7% | sarana=DISTRIBUSI |
| tx_*_issue | 74-79% | inspeksi dengan checklist audit |
| tingkat_pemenuhan_cpob | 99,7% | industri obat CPOB |
| hp_followup_name | 99,7% | kasus hukum lanjutan |
| mv_kriteria coverage | 99,65% | sertifikasi CPKB/CPOB |
| jenis_pangan coverage | 81,2% | komoditi PRODUK PANGAN |

**~70% "NULL" di warehouse ini adalah structural.** Bukan kualitas buruk — memang tidak berlaku.

## 11.8 Case-Mismatch Join (jebakan integrasi)

| Sambungan | Masalah | Solusi |
|---|---|---|
| fact.kabupaten ↔ coverage.kabupaten | UPPER vs Title Case | `lower()` kedua sisi |
| fact.komoditi ↔ target.komoditi | "KOSMETIK" vs "Kosmetika" | `mapping_komoditi_target_balai` |
| fact.nama_upt ↔ target.nama_balai | 15 unmatched (Loka/Direktorat/Demo) | roll-up + filter |

## 11.9 Ringkasan: Sehat vs Kondisional vs Cacat

| Aspek | ✅ Sehat | 🟡 Kondisional (bukan cacat) | 🔴 Cacat sejati |
|---|---|---|---|
| Struktur | grain jelas, 1 anchor | prefix mv_ (fisik, bukan matview) | 0 PK/FK/index |
| Identitas | id unik | 3 tingkat org di nama_upt | alamat tak konsisten, DEMO data |
| Waktu | tanggal_input lengkap | median durasi wajar | 14+ tanggal mustahil, day_* meledak |
| Klasifikasi | hierarki sarana logis | 76% klasifikasi null (struktural) | legal campur 2 konsep |
| Hasil | piramida sanksi sehat | 83% grade null (struktural) | grade di IN_PROGRESS ambigu |
| Relasi | fact→log/petugas 100% | temuan/kriteria sparse (wajar) | 30.699 orphan, case-mismatch |
| Value | kesimpulan/status terstandar | — | sinonim, TIE ganda |
| Angka | issue counts wajar | 0 bermakna di target | jml_temuan & harga negatif, INFALGIN |
