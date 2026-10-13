# Crosscheck testcase vs database LIVE — PEMERIKSAAN SARANA

**Tanggal:** 19 Agustus 2026 · **Populasi:** 256 testcase — 100% isi `docs/testcase/`, bukan sampel.

**Metode:** SQL yang tertulis di `note` tiap testcase dijalankan ULANG ke database live lewat tunnel `localhost:5533`. Pipeline-nya sendiri diaudit lebih dulu — lihat `07-metodologi-dan-self-audit.md`.

---

## 1. Dua sumbu yang harus dipisah

Laporan versi pertama saya mencampur dua hal berbeda dan karenanya salah. Yang benar:

| Sumbu | Pertanyaan | Hasil |
|---|---|---|
| **1 — Keterjawaban** | Apakah database bisa menjawab pertanyaan testcase ini? | **256/256 = 100% BISA** |
| **2 — Mutu penulisan assert** | Apakah `assert_any_of`/`assert_contains`-nya ditulis dengan benar? | 251/256 baik, **5 cacat** |

> **Tidak ada satu pun testcase di repo ini yang "halu".** Seluruh 256 SQL GT tereksekusi tanpa error dan mengembalikan data yang konsisten dengan yang dicatat `note`-nya. Yang bermasalah semata **cara assert-nya ditulis** — dan itu ada di berkas YAML, bukan di database.

## 2. 5 cacat penulisan assert (Sumbu 2)

### Assert bertentangan dengan `note`-nya sendiri — 3 kasus

| Skenario | Verifikasi database & sifat cacatnya |
|---|---|
| `TC-PMR-TARGET-CAPAIAN-01` | `note` mencatat **33.365**, DB hari ini **33.358** (drift 0,02%). Tapi `assert_any_of` menuntut jawaban memuat 'tidak ada'/'tidak ditemukan'/'kosong'. Assert bertentangan dengan notenya sendiri. |
| `TC-PMR-TREN-HASIL-PEMERIKSAAN-02` | `note` mencatat **8.062**, DB hari ini **8.062** (cocok persis). Assert tetap menuntut 'tidak ada'. |
| `TC-PMR-VONIS-MK-TMK-03` | `note` mencatat **466** (BBPOM Surabaya), DB hari ini **466** (cocok persis). Assert tetap menuntut 'tidak ada'. |

### Assert "baris teratas" dari query tanpa `ORDER BY` — 1 kasus

| Skenario | Verifikasi database & sifat cacatnya |
|---|---|
| `TC-PMR-RIWAYAT-SARANA-03` | Cacah baris terverifikasi: note **214.166** vs DB **214.308** (drift 0,07%). Tapi assert menuntut `'INDAH FARMA  '` sebagai *baris teratas* dari query **tanpa `ORDER BY`** — urutan ditentukan urutan fisik Postgres, tidak reproducible. |

### Angka assert menua melewati toleransi 5% — 1 kasus

| Skenario | Verifikasi database & sifat cacatnya |
|---|---|
| `TC-PMR-DRAFT-1` | 947 → **948** (+0,1%, wajar). Ada isu terpisah: token kedua ditulis `'draft|belum'` — sintaks OR pipe hanya didukung `assert_contains`, **tidak** oleh `assert_any_of`, jadi dicocokkan sebagai literal. |

## 3. 1 testcase yang SEMPAT saya tuduh cacat — ternyata sah

Ini testcase **perilaku**: assert-nya tekstual dan menilai apakah agent mengakui keterbatasan data. Pemeriksa mekanis saya tidak bisa menilainya (ia membandingkan teks ke hasil SQL, bukan ke jawaban agent). Premis tiap-tiap testcase saya verifikasi manual ke database — **semuanya terbukti benar**:

| Skenario | Bukti dari database |
|---|---|
| `TC-PMR-KATEGORI-BEKU-1` | Premis TERBUKTI: `max(sync)` tabel kategori temuan = **2025-11-12**, tabel induk = **2026-08-18** — data kategori memang tertinggal 9 bulan. Assert tekstual ('tidak lengkap'/'ETL'/dst) menilai *pengakuan keterbatasan* di jawaban agent, bukan angka. |

## 4. Implikasi untuk context v3

Perbaiki **berkas testcase** lebih dulu, sebelum dipakai menilai context v3. Kalau tidak, context yang menjawab BENAR justru tercatat FAIL:

1. **3 assert kontradiktif** — ganti `'tidak ada'` dengan angka yang sudah tercatat di `note`-nya sendiri: `TC-PMR-TARGET-CAPAIAN-01`, `TC-PMR-TREN-HASIL-PEMERIKSAAN-02`, `TC-PMR-VONIS-MK-TMK-03`.
2. **1 assert non-deterministik** — tambahkan `ORDER BY` eksplisit di SQL GT, atau ganti assert "baris teratas" jadi cacah baris: `TC-PMR-RIWAYAT-SARANA-03`.
3. **1 assert kedaluwarsa** — perbarui angkanya, atau longgarkan toleransi khusus untuk metrik tahap-alur yang memang bergerak harian: `TC-PMR-DRAFT-1`.
