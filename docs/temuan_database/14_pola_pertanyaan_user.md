# 14 — Pola Pertanyaan User (Analisis KAI Text2SQL)

> Analisis **963 pertanyaan natural-language** yang diajukan user ke database `pemeriksaan` melalui sistem KAI text2sql
> (periode Jul 2025 – Apr 2026). Sumber: `data_output/kai_sql_pairs/kai_sql_all.csv`.
> Hanya **pertanyaan** yang dianalisis — SQL KAI tidak divalidasi (lihat [15_mapping_kai_ke_warehouse.md](15_mapping_kai_ke_warehouse.md)).

## 14.1 Sumber & Statistik

| Metrik | Nilai |
|---|---|
| Total SQL generation (runtime) | 11.500 |
| └ untuk DB pemeriksaan | 2.862 |
| Pertanyaan natural-language (`real`) | 3.423 |
| **Pertanyaan real untuk pemeriksaan (unique, dedup)** | **963** |
| └ alias `pemeriksaan` | 539 |
| └ alias `pemeriksaan_all` | 363 |
| └ alias `pemeriksaan_all_v2` | 61 |
| Periode | 2025-07-10 s/d 2026-04-22 |

## 14.2 Klasifikasi Keterjawaban

| Kategori | Jumlah | % | Makna |
|---|---|---|---|
| **✅ Bisa dijawab warehouse** | **811** | 84% | Mapping ke `mv_pemeriksaan*` langsung |
| **🟡 Cross-domain** | 81 | 8% | Rutin ke pemeriksaan tapi sentuh domain lain |
| **🔴 Gap (tidak bisa dijawab)** | 71 | 7% | Kolom/data tidak ada di warehouse |

### Cross-domain (81) — pertanyaan yang "nyasar" ke pemeriksaan
| Domain asal | Jumlah |
|---|---|
| Pengawasan iklan | 56 |
| Sertifikasi (CPOB/CPKB/CPOTB) | 22 |
| Registrasi (NIE/notifikasi) | 22 |
| Pengujian (hasil uji/sampel) | 15 |

### Gap (71) — user TANYA tapi data TIDAK ADA
| Penyebab gap | Jumlah | Detail |
|---|---|---|
| **BUPN** | 18 | Tidak ada kolom BUPN di warehouse |
| **SIPT / waktu pelaporan** | 13 | Tidak ada tanggal kirim SIPT |
| **Notifikasi** | 7 | Tidak ada nomor notifikasi produk |
| Sampling | 3 | Ada di DB `pengujian`, bukan pemeriksaan |
| Forecast/simulasi | 2 | Bukan fungsi SQL analyst |
| Nilai sarana | 2 | Hanya `grade`, tidak ada "nilai" mentah |
| CPOTB | 1 | Ada CPOB/CPKB, bukan CPOTB |

## 14.3 Intent — Apa yang User Mau (707 pertanyaan clean)

| Intent | Count | Contoh khas |
|---|---|---|
| **Detail/list ("tampilkan")** | 505 | "Tampilkan hasil pemeriksaan TMK sarana produksi MD untuk setiap UPT di tahun 2025" |
| **Sarana filter** | 497 | "Sarana produksi apa saja dengan TMK..." / "sarana distribusi..." |
| **Temuan produk** | 187 | "tampilkan jumlah temuan produk sarana distribusi pada tahun 2023" |
| **Verdict TMK** | 166 | "...yang Tidak Memenuhi Ketentuan..." |
| **Verdict MK** | 131 | "...yang Memenuhi Ketentuan..." |
| **Trend** | 107 | "Tunjukan trend jumlah pemeriksaan dalam 5 bulan terakhir" |
| **Count per periode** | 92 | "Berapa total pemeriksaan bulan Juni 2025" |
| **Nilai temuan** | 49 | "jumlah nilai temuan produk... dalam rupiah" |
| **Produk impor** | 45 | "sarana importir apa saja yang pernah diperiksa" |
| **Ranking top** | 44 | "Balai mana yang melakukan pemeriksaan terbanyak" |
| **Chart** | 43 | "...buat dalam bentuk line chart" |
| **Komoditi** | 42 | "pemeriksaan untuk komoditas obat tertinggi" |
| **Jenis sarana** | 37 | "pangan MD / IRT / apotek / toko obat" |
| **Tujuan pemeriksaan** | 33 | "rutin / sertifikasi / kasus / intensifikasi" |
| **Geografis** | 26 | "provinsi / kabupaten / kota" |
| **Perbandingan** | 24 | "januari dibandingkan februari, lebih banyak mana" |
| **Count total** | 15 | "Berapa total jumlah pemeriksaan" |
| **Status** | 13 | "draft / selesai / verifikasi" |
| **Ranking bottom** | 6 | "Balai mana yang paling sedikit" |
| **Grade** | 6 | "grade / grading" |

## 14.4 Bagaimana User Bertanya (pola pembuka)

| Pembuka | Count | Karakter |
|---|---|---|
| **"tampilkan"/"tunjukkan"** | **262** | Dominan — user mau MELIHAT data (list/detail), bukan hanya angka |
| "berapa" | 82 | Counting |
| "tolong" | 68 | Permintaan sopan |
| "sarana..." (mulai dari entity) | 45 | Topik dulu, baru pertanyaan |
| "berikan" | 30 | |
| "bagaimana" | 28 | Analitis (tren/kondisi) |
| "upt..." | 17 | Mulai dari entitas organisasi |

**Insight**: User BPOM lebih banyak minta **"tampilkan"** (show/list) daripada **"berapa"** (count).

## 14.5 Frasa Waktu

| Frasa | Count | Mapping |
|---|---|---|
| **"tahun 2025"** | **233** | `tanggal_mulai >= '2025-01-01' AND < '2026-01-01'` |
| "periode" | 132 | ⚠️ Ambigu — perlu Gate 1 klarifikasi |
| "tahun 2024" | 98 | |
| "bulan juni/juli" | 49 | |
| "N bulan terakhir" | 11 | `>= CURRENT_DATE - INTERVAL 'N months'` |
| "triwulan/quarter/TW" | 16 | Q1-Q4 |

## 14.6 Verdict: User Pakai DUA Bentuk

User memakai **kode** DAN **full-text** bergantian:
- Kode: "MK", "TMK"
- Full-text: "Memenuhi Ketentuan", "Tidak Memenuhi Ketentuan"
- Varian: "TMS" (Tidak Memenuhi Syarat), "tidak sesuai"

Warehouse menyimpan kode (`kesimpulan = 'MK'`/`'TMK'`). Sistem wajib menerjemahkan full-text → kode.

## 14.7 Sarana & Merk yang Dicari User (free-text lookup)

| Merk/Sarana | Frekuensi | Pola pertanyaan |
|---|---|---|
| Alfamart | 4 | "riwayat pemeriksaan sarana alfamart tahun 2024" |
| Kimia Farma | 2 | "riwayat pemeriksaan sarana apotek kimia farma" |
| Maha Siri Jaya | 2 | |
| PT Wardah | 3 | "hasil uji produk PT Wardah" (cross-domain pengujian) |
| Nida Food | 1 | "riwayat pemeriksaan sarana produksi 'nida food'" |
| CIPTA ANUGERAH BAKTI MANDIRI | 1 | |
| Siloam | 1 | |

**Pola khas**: "riwayat pemeriksaan sarana [NAMA] dalam periode [TAHUN]" → `ILIKE '%nama%'` di `nama_sarana`.

## 14.8 Pertanyaan Kompleks (133 pertanyaan >120 char)

User mengharapkan jawaban yang lebih kaya dari counting sederhana:

| Ekspektasi | Contoh |
|---|---|
| **Grading custom logic** | "grading A MK jika nilai sarana A dan B; grading B TMK jika nilai C" |
| **SLA compliance** | "tepat waktu jika pelaporan max tgl 15 bulan berikutnya" |
| **Multi-dimensional breakdown** | "sarana distribusi... MK dan TMK... jumlah temuan... nilai... BKO/TIE/kadaluarsa" |
| **Justifikasi ketidaksesuaian** | "daftar justifikasi atas ketidaksesuaian" |
| **Proyeksi/forecast** | "simulasikan proyeksi tahun berikutnya" |
| **Cross-check realisasi** | "crosscheck realisasi lain yang tidak sesuai" |

## 14.9 Temuan Korelasi Kunci

### A. Dokumentasi teknis saya OVER-DOCUMENT area yang user TIDAK tanyakan
- `jenis_id` petugas (25 kode): **0 pertanyaan**
- `tp_unit_id` (92 satuan): **0 pertanyaan**
- `tp_bets` (batch): **0 pertanyaan**
- Workflow bottleneck V4-V7: **< 5 pertanyaan**
- agg fan-out 2×: **0 pertanyaan** (internal-only)
- Kriteria CPOB severity: **0 pertanyaan**

### B. User EXPECTS informasi yang TIDAK ADA di database
- **BUPN** (18 pertanyaan) — tidak ada kolom. Mungkin = `klasifikasi_sarana` atau `legal`? Perlu investigasi.
- **SIPT/SLA pelaporan** (13) — user mau cek "tanggal kirim SIPT vs pemeriksaan". `day_input_mulai` = proxy terbaik.
- **Nomor notifikasi** (7) — ada di DB `penandaan`/`rpo_v2`, bukan pemeriksaan.

### C. BEDA NAMA KOLOM — jebakan kritis
SQL KAI pakai view `vw_pemeriksaan_bcc` yang me-rename kolom. Lihat [15_mapping_kai_ke_warehouse.md](15_mapping_kai_ke_warehouse.md) §15.1.

## 14.10 Rekomendasi Prioritas

1. **Investigasi BUPN** — 18 pertanyaan user menunggu. Cek `klasifikasi_sarana`/`legal`/`klasifikasi_distribusi`.
2. **Panduan entity resolution sarana** — "riwayat pemeriksaan sarana [NAMA]" adalah pattern umum (15+ pertanyaan).
3. **Mapping full-text ↔ kode** — user pakai "Memenuhi Ketentuan", "TMS", "Tidak Sesuai", bukan cuma MK/TMK.
4. **Clarifikasi "periode"** — 132 pertanyaan pakai kata ambigu "periode".
5. **Bab SQL kanonik** — 11 intent butuh template SQL siap pakai (lihat [15_mapping_kai_ke_warehouse.md](15_mapping_kai_ke_warehouse.md)).

---

## Batch pertanyaan tambahan — diuji ke DB live 2026-08-14

Sepuluh pertanyaan baru dari pengguna, dipetakan ke kolom lalu dijalankan.

| Pertanyaan | Pemetaan | Catatan hasil |
|---|---|---|
| Inspeksi RUTIN MK/TMK per periode 2025 | `tujuan_pemeriksaan='PEMERIKSAAN RUTIN'` + `kesimpulan` + bulan `tanggal_mulai` | jalan; MK dan TMK naik seiring bulan |
| Total pemeriksaan Agustus 2025 | rentang `tanggal_mulai` | jalan |
| **"Penurunan drastis pada Oktober 2025"** | uji klaim | ⛔ **KLAIM SALAH** — lihat di bawah |
| Pemeriksaan **MD** 2025 status TMK | `jenis_sarana LIKE '%MD%'`, **bukan** `komoditi` | jalan; satu-satunya nilai yang cocok `PANGAN MD` |
| **Top 5 Balai** | ambigu — "top" berdasar apa? | dijawab dengan cacah pemeriksaan; **perlu klarifikasi** |
| Line chart komoditas OBAT 2025 | `komoditi='OBAT'` (bukan keluarga obat) | jalan |
| Kepatuhan CPOB produksi obat 2024 Surabaya | `tingkat_pemenuhan_cpob` | jalan, tapi **populasinya sangat tipis** |
| **Tabel balai + target + pemeriksaan per sarana 2025** | `target_balai` | ⛔ **tidak lengkap** — lihat di bawah |
| Analisa total per bulan 2025 | bulan `tanggal_mulai` | jalan; **bulan berjalan parsial** |

### ⛔ Klaim "penurunan drastis Oktober 2025" terbantah

```sql
SELECT to_char(tanggal_mulai,'YYYY-MM') AS bln, count(*) AS n FROM mv_pemeriksaan
WHERE tanggal_mulai >= '2025-01-01' AND tanggal_mulai < '2026-01-01' GROUP BY 1 ORDER BY 1;
```

Bentuk kurvanya: naik dari Januari sampai puncak di Mei, landai Juni–September, **Oktober justru
naik lagi**, baru turun di November dan tajam di Desember.

Jadi bulan yang benar-benar turun adalah **November dan Desember**, bukan Oktober. Kalimat
*"mengalami penurunan drastis pada Oktober 2025, menandai tren penurunan signifikan"* adalah
**kesimpulan yang tidak didukung data** — kemungkinan besar keluaran AI yang lolos tanpa
verifikasi, lalu ditanyakan balik sebagai fakta.

**Aturan yang harus masuk skill:** pernyataan tren dari turn sebelumnya **tidak boleh diwarisi
sebagai fakta**; hitung ulang dari SQL turn ini.

### ⛔ `target_balai` tidak punya target untuk sarana PELAYANAN

```sql
SELECT string_agg(column_name, ', ' ORDER BY ordinal_position) FROM information_schema.columns
WHERE table_schema='public' AND table_name='target_balai' AND column_name LIKE 'target%';
--  target_penandaan, target_pengawasan, target_pengujian, target_pengujian_pangan,
--  target_pengujian_pangan_fortifikasi, target_sarana_distribusi, target_sarana_produksi
```

Ada target untuk **distribusi** dan **produksi**, **tidak ada** untuk **pelayanan** — padahal
`mv_pemeriksaan.sarana` punya tiga nilai. Pertanyaan "tabel balai + total target + total
pemeriksaan dikelompokkan berdasarkan sarana" karena itu **hanya bisa dijawab untuk dua dari tiga
sarana**. Menjawabnya untuk ketiganya (dengan memakai target distribusi bagi pelayanan) menghasilkan
capaian yang keliru.

Perhatikan juga pernyataan pengguna *"Saat ini tidak ada data yang tersedia untuk ditampilkan…"* —
itu **tidak benar**: datanya ada, yang tidak ada adalah **target pelayanan**. Jawaban yang tepat
menyebut batas itu, bukan menyatakan datanya kosong.

### Catatan cakupan waktu

```sql
SELECT max(tanggal_mulai), max(tanggal_input),
       count(*) FILTER (WHERE tanggal_mulai >= date_trunc('month', CURRENT_DATE)) AS bulan_berjalan
FROM mv_pemeriksaan;
```

`tanggal_input` mencapai hari ini, sementara `tanggal_mulai` memuat tanggal **di masa depan** —
gejala salah input yang sudah dicatat di `11_kualitas_data_dan_anomali.md`. Bulan berjalan selalu
**parsial**; sebutkan itu pada setiap jawaban tren bulanan.
