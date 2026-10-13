# Rincian kegagalan — pemeriksaan · varian `after-insight-v2` · 18 Agustus 2026

Sumber: `seeknal/tests/outputs/2026-08-18/*/variant_compare_results_*.json` (kolom `failures`, `sqls`, `answer`).
Tabel dibangkitkan langsung dari berkas hasil, bukan diketik ulang.

| Kelas | Jumlah |
|---|---:|
| teks+angka | 7 |
| teks/nama saja | 4 |
| angka | 3 |
| 0-SQL | 1 |
| **TOTAL** | **15** |

| Skenario | Kelas | AUTO-klarifikasi | #SQL | GT (assert_any_of) | Pesan gagal |
|---|---|:--:|--:|---|---|
| `TC-PMR-RANK-SARANA-01` | teks+angka | ya | 2 | 141.509 | missing: 'DISTRIBUSI'; no assert_any_of group matched (tol=5.0%) |
| `TC-PMR-RIWAYAT-SARANA-11` | teks+angka | - | 4 | ABAD DUA SATU MAKMUR | missing: 'ABAD DUA SATU MAKMUR'; no assert_any_of group matched (tol=5.0%) |
| `TC-PMR-SARANA-DISTRIBUSI-06` | teks+angka | - | 3 | KOSMETIK | missing: 'KOSMETIK'; no assert_any_of group matched (tol=5.0%) |
| `TC-PMR-SARANA-DISTRIBUSI-09` | teks+angka | - | 3 | 23 | missing: 'BAHAN BERBAHAYA'; no assert_any_of group matched (tol=5.0%) |
| `TC-PMR-SARANA-DISTRIBUSI-11` | teks/nama saja | - | 4 | 2 | missing: 'BALAI BESAR POM DI JAKARTA' |
| `TC-PMR-SARANA-TUTUP-06` | teks+angka | - | 2 | KOTA JAKARTA UTARA | missing: 'KOTA JAKARTA UTARA'; no assert_any_of group matched (tol=5.0%) |
| `TC-PMR-TARGET-CAPAIAN-02` | angka | - | 5 | 284 | no assert_any_of group matched (tol=5.0%) |
| `TC-PMR-TEMUAN-PRODUK-01` | 0-SQL | - | 0 | APOTEK EKA FARMA   | missing: 'APOTEK EKA FARMA  '; no assert_any_of group matched (tol=5.0%) |
| `TC-PMR-TEMUAN-PRODUK-03` | teks+angka | - | 8 | BUSANA INDAH | missing: 'BUSANA INDAH'; no assert_any_of group matched (tol=5.0%) |
| `TC-PMR-TREN-HASIL-PEMERIKSAAN-02` | angka | - | 2 | tidak ada / tidak ditemukan / kosong | no assert_any_of group matched (tol=5.0%) |
| `TC-PMR-TREN-HASIL-PEMERIKSAAN-06` | teks/nama saja | - | 2 | 1 | missing: '2024-05' |
| `TC-PMR-TREN-HASIL-PEMERIKSAAN-07` | teks/nama saja | - | 6 | 2 | missing: '2025-06' |
| `TC-PMR-VONIS-MK-TMK-01` | angka | - | 3 | 455 / tidak ada / tidak ditemukan / koso | no assert_any_of group matched (tol=5.0%) |
| `TC-PMR-VONIS-MK-TMK-04` | teks/nama saja | - | 3 | 3.323 | missing: 'BALAI BESAR POM DI BANDUNG' |
| `TC-PMR-VONIS-MK-TMK-05` | teks+angka | - | 5 | ED (Expire Date / Kedaluwarsa) | missing: 'ED (Expire Date / Kedaluwarsa)'; no assert_any_of group matched (tol=5.0%) |
