# 02 — Pemetaan Tabel Per Tabel (Grain, Kardinalitas, Coverage)

> Setiap tabel dipetakan: grain (1 baris = apa), rasio ke fact, coverage, peran arsitektural.

## 2.1 Analisis Grain (Kardinalitas)

| Tabel | Grain (1 baris = ) | Rasio ke fact | Sifat | Verified |
|---|---|---|---|---|
| `mv_pemeriksaan` | 1 inspeksi | 1× | **ANCHOR** | 257.456 baris, id unik |
| `mv_pemeriksaan_timeline` | 1 inspeksi | ~1,12× (orphan) | 1:1 (harusnya) | 288.157 baris, 30.699 orphan |
| `mv_pemeriksaan_log` | 1 langkah workflow | **5,09×** | 1:N fan-out | 1.311.757 baris |
| `mv_pemeriksaan_petugas` | 1 penugasan orang | **2,26×** | 1:N fan-out | 581.864 baris |
| `mv_pemeriksaan_temuan` | 1 produk sitaan | 1,15× (12,6% coverage) | 1:N sparse | 296.981 baris, 32.503 id punya temuan |
| `mv_pemeriksaan_kategori_temuan` | 1 kategori-per-produk | 0,94× | 1:N exploded | 241.609 baris |
| `mv_pemeriksaan_jenis_pangan` | 1 jenis-per-pangan | 0,19× | 1:N exploded, kondisional | 48.511 baris |
| `mv_kriteria_pemeriksaan` | 1 item checklist audit | 0,023× | 1:N sangat sparse | 5.892 baris, 902 id |
| `mv_pemeriksaan_agg` | 1 kombinasi dimensi×periode | **1,42×** | rollup fan-out | 366.800 baris |

### ⚠️ Fan-Out Trap (bahaya terbesar)

Jika seorang analis melakukan JOIN banyak tabel sekaligus tanpa agregasi awal:

```
fact JOIN _log JOIN _petugas JOIN _temuan
= 1 × 5,09 × 2,26 × 1,15 = ~13 baris per inspeksi
```

Semua `COUNT(*)` dan `SUM()` jadi **salah berlipat**. ERD ini WAJIB dibaca sebagai bintang dengan cabang
terpisah yang **tidak boleh di-join bersamaan tanpa agregasi dulu**.

## 2.2 Tabel per Tabel — Detail

### `mv_pemeriksaan` — FACT UTAMA

- **Grain**: 1 baris = 1 inspeksi sarana.
- **PK empirik**: `id` (bigint, 257.456 unik, 0 null). `COUNT(*)` = `COUNT(DISTINCT id)` di tabel ini.
- **31 kolom** dalam 6 klaster semantik (lihat [03_data_dictionary_lengkap.md](03_data_dictionary_lengkap.md)).
- **Coverage**: 100% tabel anak punya parent di sini (kecuali 30.699 orphan timeline).
- **Catatan**: `nama_sarana` (130.501 unik) lebih banyak dari yang diharapkan — entity resolution sarana
  masih kabur (normalisasi hanya mengurangi 4.361 nilai).

### `mv_pemeriksaan_log` — Mesin Waktu Proses

- **Grain**: 1 baris = 1 transisi status (1 langkah workflow).
- **FK**: `id_pemeriksaan` → fact.id. `id_steps` (1.311.693 distinct = 99,995% unik → PK natural empirik).
- **Rasio**: 5,09 baris per inspeksi (p50=4, max=75 langkah).
- **64 baris corrupt**: `id_steps` + `status` + `created_at` semua NULL bersamaan.
- **Kolom kaya**: `catatan` (free-text, 82% terisi), `fullname` (2.063 aktor verifikator).
- **Penting**: `fullname` di log = **verifikator/approver** (orang yang approve status),
  BERBEDA dari `petugas` di tabel petugas (= **pemeriksa lapangan**). Dua populasi orang berbeda.

### `mv_pemeriksaan_petugas` — Tim Lapangan

- **Grain**: 1 baris = 1 penugasan petugas ke inspeksi.
- **FK**: `id_pemeriksaan` → fact.id. `petugas_id` (2.997 distinct).
- **Rasio**: 2,26 petugas per inspeksi (p50=2, max=48). 75,7% inspeksi punya tepat 2 petugas.
- **`jenis_id`** (25 kode): kode peran petugas. Dominan: 16 (140k), 13 (81k), 109 (60k).
  **3 kode 6-digit** (211265=26, 211337=2, 223447=2) = kode tak dikenal, kemungkinan ID bocor dari tabel lain.
- **⚠️ Jebakan**: `komoditi` di tabel ini = **jenis sarana/penugasan** (APOTEK, PBF, PKM),
  BUKAN jenis produk (OBAT, PANGAN). Nama kolom sama, makna beda dari fact.
- **`nomorsurat`** (110.581 distinct) = nomor surat tugas.

### `mv_pemeriksaan_temuan` — Barang Bukti Fisik

- **Grain**: 1 baris = 1 produk yang ditemukan/disita.
- **FK**: `id_pemeriksaan` → fact.id. Hanya **32.503 inspeksi (12,6%)** punya temuan — wajar (MK tidak punya temuan).
- **Rasio**: rata-rata 9,1 produk per inspeksi bertemuan.
- **Kolom kunci**: `product_name` (25.552 distinct), `registrar`, `tp_negara` (1.299 distinct — perlu normalisasi),
  `tp_kategori` (106 nilai, banyak sinonim), `tp_harga_total` (tercemar outlier — lihat [08](08_nilai_sitaan_dan_produk.md)).
- **Kolom mati sejati**: `tp_pelanggaran` (99,996% null, hanya 12 record terisi) dan
  `tp_netto` (99,998% null, hanya 5 record terisi). Tidak ada alasan struktural — kolom sejenis
  (`tp_kategori`, `tp_tindakan`) terisi penuh di tabel yang sama.
- **`tp_expire`** (date): 61,6% null (wajar — tidak semua produk punya expire date, mis. kosmetik TIE).
- **`tp_bets`**: 50.818 distinct — nomor batch/expire. 47% terisi (banyak placeholder: "-", "tidak ada", "N/A").

### `mv_pemeriksaan_timeline` — Stopwatch Antar-Tahap

- **Grain**: 1 baris = 1 inspeksi (1:1 dengan fact, seharusnya).
- **FK**: `id_pemeriksaan` → fact.id. **30.699 orphan** (id tidak ada di fact) — lihat [11](11_kualitas_data_dan_anomali.md).
- **Kolom durasi** (semua dalam HARI):
  - `mulai_kabalai`: dari mulai sampai kirim ke kepala balai. Median ~8 hari, **max 526.265** (outlier).
  - `kabalai_direktur`: kepala balai ke direktur. Median ~82 hari, max 996.
  - `direktur_pusat`: direktur ke pusat. Median 0, max 1. **⚠️ Trap**: 254.391 baris NULL —
    `direktur_pusat = 0` TIDAK berarti cepat, tapi `tanggal_kirim_pusat` belum terisi.
- **Penting**: timeline data tercemar outlier tanggal (lihat [11](11_kualitas_data_dan_anomali.md)).
  Hitung durasi dari **log** (lebih reliable) daripada timeline.

### `mv_pemeriksaan_agg` — Rollup Pre-Computed

- **Grain**: 1 baris = 1 kombinasi (periode_type, tanggal, UPT, provinsi, kabupaten, sarana, jenis_sarana,
  legal, tujuan, komoditi, kesimpulan, status).
- **`periode_type`**: `day` (202.104 baris) + `month` (164.696 baris).
- **⚠️ FAN-OUT 2×**: `sum(jumlah_pemeriksaan)` = 513.026 ≈ **2× fact** (257.456). Lihat [10](10_agg_dan_integritas_etr.md).
- **TIDAK boleh di-SUM langsung** untuk total inspeksi. Hanya aman untuk `sum(jumlah_sarana_unik)` atau `avg_*`.

### `mv_pemeriksaan_jenis_pangan` — Rincian Pangan

- **Grain**: 1 baris = 1 jenis pangan per inspeksi (exploded array).
- **Coverage**: 48.511 baris dari ~18,8% inspeksi (hanya komoditi PRODUK PANGAN).
- **Kondisional**: kolom ini HANYA berlaku untuk pangan. NULL di non-pangan = structural, bukan missing.

### `mv_pemeriksaan_kategori_temuan` — Versi Bersih Temuan

- **Grain**: 1 baris = 1 kategori per produk temuan (exploded array).
- **49 nilai** (vs 106 di `mv_pemeriksaan_temuan.tp_kategori` mentah).
- **Normalisasi setengah jalan**: masih ada varian sisa ("TIE (Tanpa Izin Edar)" 128.666 vs "TIE" 30).

### `mv_kriteria_pemeriksaan` — Checklist CPOB/CPKB

- **Grain**: 1 baris = 1 item checklist audit.
- **FK**: `pemeriksaan_id` (bukan `id_pemeriksaan` — inkonsistensi!).
- **Coverage**: 5.892 baris dari **902 inspeksi (0,35%)** — hanya sarana produksi obat yang disertifikasi.
- **`tx_criteria`** (severity 1-4): 1=critical (294), 2=major (2.620), 3=minor (2.635), 4=observation (49).
- **`tx_criteria_desc`**: narasi temuan, menyebut "temuan berulang dari inspeksi sebelumnya."
- **🆕 ZERO overlap dengan grade**: 0 inspeksi punya KEDUA kriteria checklist DAN grade.
  Sertifikasi (CPOB) tidak ber-grade; rutin tidak punya kriteria. Dua sistem benar-benar terpisah.

### `coverage_balai` — Peta Yurisdiksi

- **Grain**: 1 baris = 1 mapping balai → kabupaten.
- **668 baris**: 84 balai × rata-rata ~8 kabupaten.
- **514 kabupaten** terdaftar. **1 belum diinspeksi**: Kabupaten Intan Jaya (LOKA POM Mimika) — kendala geografis.
- **Tabel paling sehat**: 0 null, 0 duplikat, natural key (`id_balai`, `id_kabupaten`) unik.

### `target_balai` — Kontrak Kinerja 2024

- **Grain**: 1 baris = 1 (balai, komoditi, tahun).
- **532 baris**: 76 balai × 7 komoditi × **1 tahun** (hanya 2024).
- **7 komoditi**: Kosmetika, Obat, Obat Kuasi, Obat Tradisional, Produk Pangan, Rokok, Suplemen Kesehatan.
- **15 nama_balai unmatched** ke fact: 6 Direktorat (central office), 2 DEMO (test), 7 Loka (sub-balai).
- **Perlu roll-up Loka → Balai induk** untuk pencapaian target akurat.

## 2.3 Coverage Inspeksi per Tabel Anak

```sql
-- Jumlah inspeksi (distinct id) yang punya data di tiap tabel anak:
mv_pemeriksaan_log:           257.456  (100%)
mv_pemeriksaan_petugas:       257.456  (100%)
mv_pemeriksaan_temuan:         32.503  (12,6%)
mv_pemeriksaan_timeline:      257.458  (100% + 30.699 orphan)
mv_kriteria_pemeriksaan:         902  (0,35%)
mv_pemeriksaan_jenis_pangan:   48.511  (18,8%)
```

## 2.4 Tiga Subgraf Tersembunyi

Warehouse ini sebenarnya **3 subgraf** yang berpotongan di `mv_pemeriksaan.id`:

```
SUBGRAF 1: PROSES ADMINISTRASI          SUBGRAF 2: HASIL PENGAWASAN PRODUK     SUBGRAF 3: KEPATUHAN SARANA
  fact ─── _log ─── _timeline             fact ─── _temuan ─── _kategori          fact ─── _kriteria
    └── _petugas                                    └── _jenis_pangan                    └── (grade, tx_issue, cpob di fact)
  "seberapa cepat & siapa?"              "produk apa yang ilegal?"               "seberapa patuh sarananya?"
```

**Implikasi:**
- Pertanyaan "apakah sarana grade C punya lebih banyak temuan TIE?" hanya bisa dijawab **lewat fact** sebagai
  perantara (Subgraf 3 → fact → Subgraf 2). Tidak ada relasi langsung kriteria → temuan.
- `id` adalah **satu-satunya jembatan** antar-subgraf. Integritasnya (tanpa PK/FK) menentukan
  kualitas seluruh kemampuan analitik lintas-subgraf.
