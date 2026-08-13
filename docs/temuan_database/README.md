# Temuan Database Pemeriksaan BPOM — Dokumentasi Data Understanding

> **Snapshot verifikasi**: `sync = 2026-08-12 05:56:33` (full-reload ETL).
> **Koneksi**: `postgresql://postgres@localhost:5533/pemeriksaan` (via SSH tunnel srv29-tunnel).
> **Metode**: 60+ query SELECT nyata terhadap database live, bukan asumsi.
> **Status**: Dokumen temuan independen — TIDAK mengubah `context/` yang ada.

## Tentang Dokumentasi Ini

Dokumen ini adalah hasil **deep-dive data understanding** terhadap warehouse `pemeriksaan` BPOM.
Setiap angka berasal dari query SQL yang dijalankan langsung terhadap database (bukan estimasi).
Tujuannya: memetakan kondisi data secara menyeluruh — struktur, isi, kualitas, relasi, anomali —
agar siapa pun yang menganalisis database ini punya landasan faktual yang terverifikasi.

## Peta Navigasi

| File | Isi |
|---|---|
| [01_arsitektur_dan_struktur.md](01_arsitektur_dan_struktur.md) | 2 schema, 19 tabel, zero constraint, public vs dimension, sync pattern |
| [02_pemetaan_tabel_per_tabel.md](02_pemetaan_tabel_per_tabel.md) | Grain, kardinalitas, coverage, ERD logis, fan-out trap |
| [03_data_dictionary_lengkap.md](03_data_dictionary_lengkap.md) | Semua kolom semua tabel — null rate, unique count, tipe, makna |
| [04_kamus_unique_value.md](04_kamus_unique_value.md) | Daftar nilai + distribusi untuk semua kolom kategorikal |
| [05_workflow_dan_bottleneck.md](05_workflow_dan_bottleneck.md) | State machine, funnel, durasi per transisi, bottleneck pusat |
| [06_korelasi_dan_peta_risiko.md](06_korelasi_dan_peta_risiko.md) | Grade↔temuan, hotspot RUTIN, residivis, tren tahunan |
| [07_target_dan_capaian.md](07_target_dan_capaian.md) | Target vs realisasi 2024 per komoditi |
| [08_nilai_sitaan_dan_produk.md](08_nilai_sitaan_dan_produk.md) | Nilai sitaan bersih, produk teratas, negara asal |
| [09_performa_balai_dan_petugas.md](09_performa_balai_dan_petugas.md) | Ranking balai, distribusi petugas, jenis_id |
| [10_agg_dan_integritas_etr.md](10_agg_dan_integritas_etr.md) | agg fan-out 2×, sync full-reload, implikasi ETL |
| [11_kualitas_data_dan_anomali.md](11_kualitas_data_dan_anomali.md) | Cacat, vonis per anomali, outlier, structural vs missing NULL |
| [12_belum_ditemukan_dan_eksternal.md](12_belum_ditemukan_dan_eksternal.md) | 10 pertanyaan tim sumber + 7 gap baru dari user KAI, 3 lapis ketidaklengkapan |
| [13_koreksi_hipotesis.md](13_koreksi_hipotesis.md) | Hipotesis terbantahkan vs terkonfirmasi + pelajaran metodologi |
| [14_pola_pertanyaan_user.md](14_pola_pertanyaan_user.md) | **963 pertanyaan user KAI** — intent, frasa waktu, verdict, gap |
| [15_mapping_kai_ke_warehouse.md](15_mapping_kai_ke_warehouse.md) | Mapping kolom KAI→warehouse + katalog SQL pair per intent |
| [lampiran_sql_playbook.md](lampiran_sql_playbook.md) | Semua query investigasi siap re-run, dikelompokkan per tema |

## Ringkasan Eksekutif (10 temuan kunci)

1. **19 tabel, zero constraint, zero index.** Semua query = full sequential scan. Prefix `mv_` menipu —
   semua tabel fisik (`relkind='r'`), bukan materialized view.

2. **`dimension` BUKAN mirror `public`.** Dimension adalah proyeksi dimensi murni (18 kolom, tanpa id/tanggal/measures).
   `dimension.mv_pemeriksaan_timeline` (18 baris, 1 kolom) = tabel referensi kode status workflow, bukan timeline.

3. **Sync = full-reload.** Semua 257.456 record punya timestamp identik (2026-08-12 05:56:33).
   Kolom `sync` tidak berguna untuk change detection (CDC).

4. **Grade↔temuan berkorelasi KUAT** (bukan independen seperti dugaan): Grade A 6,2% punya temuan,
   Grade C 49,6% — beda 8× lipat. Korelasi monoton A < B < C.

5. **Bottleneck di pipeline pusat, bukan "direktur 91 hari".** VERIFY4→VERIFY7 total ~67 hari median.
   64,4% inspeksi mangkrak di VERIFY4 (Operator Pusat). Hanya 11,2% mencapai FINISHED.

6. **`mv_pemeriksaan_agg` fan-out 2× — tidak boleh di-SUM langsung.** `sum(jumlah_pemeriksaan)` = 513.026
   vs fact 257.456. Dashboard yang baca agg bisa menampilkan angka 2× lipat.

7. **Nilai sitaan RIIL Rp 199,8 M, bukan Rp 7,74 T.** Satu record INFALGIN (datetime terselip di kolom
   kuantitas) menyumbang 91% dari total bruto. Tanpa pembersihan, angka finansial tak bisa dipakai.

8. **Hotspot #1 (kontrol RUTIN) = PANGAN IRT.** 59-79% TMK konsisten di hampir semua provinsi.
   Bukan Jamu seperti dugaan awal tanpa kontrol tujuan.

9. **TMK turun 37%→24% (2020→2024) lalu naik ke 32% (2025-26).** Tren positif 4 tahun terhenti.
   PANGAN IRT adalah kontributor utama lompatan 2025.

10. **943 record NULL tanggal BUKAN batch migrasi** — tersebar di id 284–289.133, 2020-2026, 84 balai.
    Ini NULL operasional (inspeksi dibuat tapi tak dimulai), bukan kohort yang bisa dibuang.

## Cara Membaca

- **01-04** = peta struktural (apa yang ADA di database).
- **05-09** = analisis bisnis (apa yang DATA ini CERITAKAN).
- **10-11** = kualitas & integritas (apa yang BERMASALAH).
- **12-13** = gap & pembelajaran (apa yang TIDAK diketahui + koreksi).
- **14-15** = perspektif USER (963 pertanyaan KAI) + mapping ke warehouse.
- **lampiran** = SQL siap pakai.

## Dataset KAI (sumber file 14-15)

Analisis pertanyaan user berbasis log sistem KAI text2sql (`data_output/kai_sql_pairs/kai_sql_all.csv`):
11.500 SQL generation (9.491 valid), 1.808 pasangan bersih, DB `pemeriksaan` = #2.
**963 pertanyaan real unik** → 811 ✅ bisa dijawab / 71 🔴 gap / 81 ⚠️ cross-domain.

## Konvensi

- Semua angka diberi sumber SQL (dalam `[bracket]` atau rujukan ke lampiran).
- `✅` = terkonfirmasi oleh query. `❌` = hipotesis terbantahkan. `🆕` = temuan baru.
- Tanggal verifikasi: **2026-08-13** (sesi analisis ini). Data bisa berubah saat ETL refresh.
