# 05 — Workflow & Bottleneck (State Machine, Funnel, Durasi)

> Rekonstruksi lengkap alur workflow BPOM pemeriksaan dari data log + timeline.
> Semua durasi dihitung dari `mv_pemeriksaan_log.created_at` (lebih reliable dari timeline yang tercemar outlier).

## 5.1 Tiga Jalur Workflow Paralel

Dari analisis status di log, terdapat **3 jalur paralel** dengan label resmi terverifikasi:

```
JALUR DAERAH (99% volume):
  DRAFT [Operator - Draft]
    → VERIFY1 [Supervisor - Verifikasi]           (opsional: VERIFY2 [Supervisor 2])
    → VERIFY3 [Kepala Balai/Loka - Verifikasi]
    → VERIFY4 [Operator Pusat - Verifikasi]       ← batas daerah/pusat
        ↓ revisi: DRAFT_REVISE [Operator - Perbaikan] → kembali ke VERIFY1

JALUR PUSAT LANJUTAN (dari VERIFY4):
  VERIFY4 → VERIFY5 [Supervisor Pusat]
         → VERIFY6 [Supervisor 2 Pusat]           (bisa skip: VERIFY5 → VERIFY7)
         → VERIFY7 [Direktur - Verifikasi]
         → FINISHED [Selesai]
        ↓ revisi: VERIFY7 → DRAFT_REVISE (109,9 hari median!)

JALUR PUSAT MURNI (1% volume — inspeksi oleh direktorat):
  DRAFT_PUSAT [Pemeriksaan Pusat - Operator Pusat - Draft]
    → VERIFY_P1 [Supervisor Pusat - Verifikasi]
    → VERIFY_P2 [Supervisor 2 Pusat - Verifikasi]   (bisa: DRAFT_PUSAT_REVISE)
    → VERIFY_P3 [Direktur - Verifikasi]
    → FINISHED_PUSAT
```

## 5.2 Funnel Penyelesaian (Status Terakhir per Inspeksi)

```sql
-- Status terakhir setiap inspeksi (dari log, presisi):
WITH last_status AS (
  SELECT DISTINCT ON (id_pemeriksaan) id_pemeriksaan, status, status_label
  FROM mv_pemeriksaan_log
  ORDER BY id_pemeriksaan, urutan_step DESC, created_at DESC
)
SELECT status, status_label, count(*) FROM last_status GROUP BY 1,2 ORDER BY 3 DESC;
```

| Status terakhir | Label | Jumlah | % | Interpretasi |
|---|---|---|---|---|
| **VERIFY4** | Operator Pusat | **165.891** | **64,4%** | 🔴 STUCK — mangkrak di pusat |
| VERIFY5 | Supervisor Pusat | 46.327 | 18,0% | 🟡 Dalam proses pusat |
| FINISHED | Selesai | 28.863 | 11,2% | 🟢 Tuntas |
| DRAFT_REVISE | Perbaikan | 5.111 | 2,0% | 🟡 Dikembalikan |
| VERIFY7 | Direktur | 4.737 | 1,8% | 🟡 Menunggu direktur |
| DRAFT | Draft | 3.167 | 1,2% | 🟡 Belum diajukan |
| VERIFY6 | Supervisor 2 Pusat | ~1.500 | ~0,6% | |
| DRAFT_PUSAT | | ~500 | ~0,2% | |
| (lainnya) | | < 1% | |

**Temuan kunci**: **64,4% seluruh inspeksi nasional terhenti di VERIFY4** (Operator Pusat Jakarta).
Hanya **11,2% yang benar-benar FINISHED**. 88,8% masih dalam proses atau terhenti.

## 5.3 Durasi per Transisi (median, dari log)

```sql
-- Hitung durasi antar transisi dari log:
WITH step_dur AS (
  SELECT id_pemeriksaan, status, created_at,
    lag(created_at) OVER w AS prev_ts,
    lag(status) OVER w AS prev_status
  FROM mv_pemeriksaan_log WHERE created_at > '2000-01-01'
  WINDOW w AS (PARTITION BY id_pemeriksaan ORDER BY urutan_step, created_at)
)
SELECT prev_status || ' → ' || status AS transisi, count(*) AS jml,
  round(percentile_cont(0.5) WITHIN GROUP (ORDER BY EXTRACT(epoch FROM created_at-prev_ts)/86400),1) AS median_hari,
  round(avg(EXTRACT(epoch FROM created_at-prev_ts)/86400),1) AS avg_hari
FROM step_dur WHERE prev_ts IS NOT NULL AND created_at > prev_ts
GROUP BY 1 HAVING count(*) >= 100 ORDER BY median_hari DESC;
```

| Transisi | Volume | Median (hari) | Avg (hari) | Interpretasi |
|---|---|---|---|---|
| VERIFY7 → DRAFT_REVISE | 130 | **109,9** | 148,6 | Direktur kembalikan → sangat lambat |
| VERIFY6 → VERIFY7 | 25.053 | 20,9 | 41,3 | Supervisor 2 → Direktur |
| VERIFY7 → FINISHED | 28.925 | 19,0 | 97,2 | Direktur → Selesai |
| VERIFY4 → VERIFY5 | 81.026 | **18,3** | 63,5 | Operator → Supervisor Pusat |
| VERIFY5 → VERIFY6 | 26.081 | 13,2 | 50,9 | Supervisor → Supervisor 2 |
| VERIFY4 → DRAFT_REVISE | 6.364 | 9,9 | 48,1 | Operator kembalikan |
| DRAFT_REVISE → VERIFY5 | 292 | 8,3 | 11,5 | |
| VERIFY1 → VERIFY2 | 40.137 | 4,8 | 17,1 | (opsional) |
| VERIFY5 → VERIFY7 | 8.741 | 4,5 | 57,9 | Skip VERIFY6 |
| VERIFY1 → VERIFY3 | 216.116 | **2,2** | 8,7 | Daerah cepat |
| VERIFY3 → VERIFY4 | 253.297 | **1,5** | 8,6 | Handoff ke pusat, cepat |
| DRAFT → VERIFY1 | 253.300 | **0,1** | 9,6 | Operator → Supervisor, instan |

### Interpretasi bottleneck

**Daerah cepat, pusat lambat.** Tahap daerah (DRAFT → VERIFY1 → VERIFY3 → VERIFY4) hanya butuh
**0,1–2,2 hari per tahap** (total ~4 hari). Handoff ke pusat (VERIFY3 → VERIFY4) juga cepat (1,5 hari).

**Pipeline pusat (VERIFY4 → FINISHED) = ~67 hari kumulatif median:**
- VERIFY4 → VERIFY5: 18,3 hari
- VERIFY5 → VERIFY6: 13,2 hari
- VERIFY6 → VERIFY7: 20,9 hari
- VERIFY7 → FINISHED: 19,0 hari

Setiap tahap pusat memakan **13–21 hari**. Total melalui 4 tahap pusat = **~67 hari**.
Ini adalah bottleneck institusional, bukan satu titik.

**❌ KOREKSI**: Hipotesis awal "bottleneck di kabalai→direktur = 91 hari" (dari timeline data)
**TERBANTAHKAN** karena timeline tercemar outlier tanggal. Durasi nyata dari log jauh lebih dapat dipercaya.

## 5.4 Efek Revisi (DRAFT_REVISE)

- **12,4% inspeksi** kena DRAFT_REVISE minimal sekali (38.708 baris di log).
- Revisi butuh **9,9 hari median** (VERIFY4 → DRAFT_REVISE), 2× lebih lama dari draft awal.
- **Loop status**: VERIFY1 → VERIFY1 (3.551 kali) — reviewer yang sama/berbeda mereview ulang tanpa maju.
- Kombinasi revisi + loop + VERIFY2 opsional = ekor distribusi 21+ langkah (24 inspeksi ekstrem).
- **VERIFY7 → DRAFT_REVISE = 109,9 hari** — saat Direktur mengembalikan, butuh ~110 hari untuk revisi!
  (Hanya 130 kasus, tapi extremely slow.)

## 5.5 Drop-off per Tahap (funnel absolut)

Dari `count(status)` di log (bukan status terakhir, melainkan berapa yang PERNAH sampai):

| Tahap | Count di log | vs DRAFT |
|---|---|---|
| DRAFT | 256.467 | 100% (start) |
| VERIFY1 | 290.533 | 113% (lebih banyak karena revisi!) |
| VERIFY3 | 256.852 | 100% |
| VERIFY4 | 253.891 | 99% — hampir semua sampai pusat |
| VERIFY5 | 82.405 | **32%** — drop 68%! |
| VERIFY6 | 26.595 | 10% |
| VERIFY7 | 34.582 | 13% (beberapa skip V6) |
| FINISHED | 29.414 | **11,5%** |

**Titik jatuh**: VERIFY4 → VERIFY5. Dari 253.891 yang sampai VERIFY4, hanya 82.405 (32%) lanjut ke VERIFY5.
**171.486 inspeksi terhenti permanen di VERIFY4.**

## 5.6 Workflow Pusat Murni (Jalur P)

| Tahap | Count di log |
|---|---|
| DRAFT_PUSAT | 953 |
| VERIFY_P1 | 526 |
| VERIFY_P2 | 32 |
| VERIFY_P3 | 137 |
| FINISHED_PUSAT | 113 |

Volume sangat kecil (~0,4% dari total). Jalur ini untuk inspeksi yang langsung dilakukan oleh direktorat pusat.

## 5.7 Seasonality (Musiman)

TMK rate per bulan (kontrol RUTIN, lintas tahun):

| Bulan | Total | TMK % |
|---|---|---|
| 1 (Jan) | 11.522 | 29,8% |
| 2 (Feb) | 20.685 | **32,9%** (tertinggi) |
| 3 (Mar) | 22.942 | 29,7% |
| 4 (Apr) | 22.085 | 30,0% |
| 5 (Mei) | 21.682 | 29,7% |
| 6 (Jun) | 25.146 | 29,8% |
| 7 (Jul) | 23.170 | 31,5% |
| 8 (Agu) | 21.639 | 31,8% |
| 9 (Sep) | 22.220 | 29,7% |
| 10 (Okt) | 22.537 | 29,9% |
| 11 (Nov) | 20.896 | **27,2%** (terendah) |
| 12 (Des) | 22.962 | 29,8% |

Variasi musiman relatif kecil (27–33%). Februari tertinggi, November terendah.

## 5.8 Trend TMK Tahunan (paling penting)

| Tahun | Inspeksi | TMK % | Tren |
|---|---|---|---|
| 2020 | 29.761 | **37,1%** | 🔴 Tertinggi (mungkin COVID era) |
| 2021 | 40.308 | 29,4% | ⬇️ Membaik |
| 2022 | 46.293 | 30,5% | → Stabil |
| 2023 | 45.831 | 25,9% | ⬇️ Membaik |
| 2024 | 48.006 | **24,1%** | 🟢 Terbaik (4 tahun menurun) |
| 2025 | 33.365 | **32,1%** | 🔴 LOMPAT naik! |
| 2026 | 12.865 | **32,8%** | 🔴 Tetap tinggi |

**Pola**: TMK turun konsisten 2020→2024 (37%→24%), lalu **melonjak ke 32% di 2025-2026**.
Pertanyaan bisnis kritis: Apa yang berubah di 2025? (Perubahan standar? Kebijakan? Atau kepatuhan riil menurun?)
PANGAN IRT adalah kontributor utama lompatan ini (lihat [06](06_korelasi_dan_peta_risiko.md)).

---

## ⚠️ Status penyaluran ke `context/` — kolom tahap timeline: BELUM

Diverifikasi 14 Agustus 2026 terhadap warehouse dan terhadap `context/80-waktu-dan-durasi.md`.

Halaman itu menyebut nama tabel `mv_pemeriksaan_timeline` tanpa menyebut kolom tahapnya — `tanggal_kirim_kabalai`, `tanggal_kirim_direktur`, `mulai_kabalai`, `kabalai_direktur`. Padahal justru kolom itulah yang menjawab "berkas tertahan di tahap mana", dan SQL sistem lama memakainya. Kekosongannya deterministik: berkas yang tidak pernah naik ke suatu tahap memang tidak punya tanggalnya, jadi rata-rata yang menyertakan baris kosong akan salah. Kolom `urutan_step` di tabel log juga tidak disebut sama sekali.

Pengukuran cakupan lengkapnya di dokumen `cakupan_context_vs_database` di direktori ini.
