# 06 — Korelasi & Peta Risiko (Cross-Table Insights)

> Analisis lintas-tabel dan lintas-dimensi: grade↔temuan, hotspot RUTIN, residivis, tren.

## 6.1 Grade ↔ Temuan Produk: Korelasi KUAT (membantah hipotesis independensi)

**❌ Hipotesis lama**: "Grade (kepatuhan sarana) dan temuan (produk ilegal) adalah dua sistem penilaian independen."

**✅ Fakta terverifikasi**: Korelasi monoton sempurna A < B < C.

```sql
SELECT p.grade,
  count(DISTINCT p.id) AS jml_inspeksi,
  count(DISTINCT t.id_pemeriksaan) AS punya_temuan,
  round(100.0*count(DISTINCT t.id_pemeriksaan)/count(DISTINCT p.id),1) AS pct_bertemuan,
  round(avg(sub.n_temuan),1) AS avg_temuan,
  round(avg(p.tx_critical_issue+p.tx_major_issue+p.tx_minor_issue),1) AS avg_issue_total
FROM mv_pemeriksaan p
LEFT JOIN (SELECT DISTINCT id_pemeriksaan FROM mv_pemeriksaan_temuan) t ON t.id_pemeriksaan=p.id
LEFT JOIN (SELECT id_pemeriksaan, count(*) n_temuan FROM mv_pemeriksaan_temuan GROUP BY 1) sub ON sub.id_pemeriksaan=p.id
WHERE p.grade IN ('A','B','C') GROUP BY p.grade ORDER BY p.grade;
```

| Grade | % Punya Temuan | Avg Temuan/Inspeksi | Avg Issue Total |
|---|---|---|---|
| **A** | **6,2%** | 4,1 | 2,5 |
| **B** | **14,0%** | 4,7 | 7,0 |
| **C** | **49,6%** | 7,3 | 10,9 |

**Grade C (sarana buruk) 8× lebih sering punya produk ilegal dari Grade A.**
Korelasi monoton: makin buruk manajemen sarana, makin banyak produk ilegal.
**Implikasi bisnis**: Kedua dimensi BISA digabung jadi satu skor risiko gabungan.

## 6.2 Kesimpulan ↔ Punya Temuan

| Kesimpulan | % Punya Temuan |
|---|---|
| TMK | 37,5% |
| MK | 2,3% |
| TDP | 2,2% |
| NULL | 1,9% |
| TTP | **0,3%** ← lebih rendah dari MK! |
| TMBB | 0,0% |

**🆕 TTP/TDP BUKAN tentang pelanggaran produk.** TTP (1.540 kasus) hanya 0,3% punya temuan produk.
Profil: tersebar di 7 komoditi, avg issue 0,7. Ini **kode administratif/perizinan**, bukan temuan pidana produk.

## 6.3 Dualitas Sistem: Kriteria CPOB vs Grade — ZERO Overlap

```sql
SELECT k.tx_criteria, p.grade, count(*)
FROM mv_kriteria_pemeriksaan k
JOIN mv_pemeriksaan p ON p.id=k.pemeriksaan_id
WHERE p.grade IN ('A','B','C') GROUP BY 1,2;
-- Hasil: 0 rows
```

**902 inspeksi dengan kriteria CPOB** dan **44.047 inspeksi ber-grade** → **0 overlap**.
- Sertifikasi CPOB/CPKB → punya kriteria, **tidak** ber-grade.
- Rutin/intensifikasi → ber-grade, **tidak** punya kriteria checklist.

Dua jalur penilaian benar-benar terpisah total.

## 6.4 Peta Risiko Multidimensi (Kontrol RUTIN)

Setelah kontrol tujuan (hanya PEMERIKSAAN RUTIN, agar mengukur kepatuhan riil bukan efek penargetan):

```sql
SELECT provinsi, komoditi, jenis_sarana, count(*) AS total,
  count(*) FILTER(WHERE kesimpulan='TMK') AS tmk,
  round(100.0*count(*) FILTER(WHERE kesimpulan='TMK')/count(*),0) AS pct_tmk
FROM mv_pemeriksaan
WHERE kesimpulan IN ('MK','TMK') AND tujuan_pemeriksaan = 'PEMERIKSAAN RUTIN'
GROUP BY provinsi, komoditi, jenis_sarana HAVING count(*) >= 200
ORDER BY pct_tmk DESC LIMIT 20;
```

| Hotspot (≥200 inspeksi RUTIN) | % TMK |
|---|---|
| Sumut × Pangan × **PANGAN IRT** | **79%** |
| Riau × Pangan × PANGAN IRT | 74% |
| Jatim × Pangan × PANGAN IRT | 74% |
| Jabar × Pangan × PANGAN IRT | 74% |
| Banten × Pangan × PANGAN IRT | 74% |
| Bali × Pangan × PANGAN IRT | 73% |
| Kalbar × Pangan × PANGAN IRT | 72% |
| Lampung × Pangan × PANGAN IRT | 68% |
| Riau × Obat × TOKO OBAT | 67% |
| Jateng × Pangan × PANGAN IRT | 66% |
| Sumut × Obat × APOTEK | 64% |

**🆕 PANGAN IRT (Industri Rumah Tangga) = hotspot #1 nasional.** 59-79% TMK konsisten di hampir SEMUA provinsi.
Ini sektor paling bermasalah yang tersebar merata — bukan Jamu (yang muncul tinggi TANPA kontrol tujuan).

### Tren PANGAN IRT per Tahun

| Tahun | Total IRT | TMK % |
|---|---|---|
| 2020 | 1.601 | 69% |
| 2021 | 1.984 | 61% |
| 2022 | 2.159 | 56% |
| 2023 | 1.926 | 44% |
| 2024 | 1.644 | **38%** (terbaik) |
| 2025 | 567 | **71%** 🔴 |
| 2026 | 224 | **78%** 🔴 |

Pola sama dengan TMK nasional: membaik 2020→2024, lalu melonjak 2025-2026.
PANGAN IRT adalah kontributor utama lompatan TMK 2025.

## 6.5 TMK Rate per Dimensi Tunggal

### per komoditi
| Komoditi | TMK % |
|---|---|
| BAHAN OBAT | 54,5% |
| PREKURSOR | 41,9% |
| NARKOTIKA | 35,4% |
| PSIKOTROPIKA | 33,9% |
| OBAT TRADISIONAL | 32,5% |
| OBAT | 30,7% |
| KOSMETIK | 30,3% |
| PRODUK PANGAN | 30,2% |
| SUPLEMEN KESEHATAN | ~15% |

### per jenis_sarana (top bermasalah)
| Jenis Sarana | TMK % |
|---|---|
| PANGAN IRT (CPPB - IRT) | **54,9%** |
| TOKO OBAT | 43,2% |
| APOTEK | 38,5% |
| BALAI PENGOBATAN/KLINIK | 35,5% |

### per legal (bentuk usaha)
| Legal | TMK % |
|---|---|
| DEPOT JAMU / TOKO JAMU | **57,8%** |
| PIRT | 55,1% |
| STAND / LOS / GEROBAK | 49,4% |
| UD | 40,1% |
| CV | 37,8% |
| TOKO OBAT | 37,7% |

### per provinsi (top & bottom 5)
| Provinsi | TMK % |
|---|---|
| JAWA TIMUR | 37,3% (tertinggi) |
| GORONTALO | ~35% |
| JAWA TENGAH | 30,0% |
| JAWA BARAT | 28,7% |
| ... | ... |
| ACEH | 21,0% |
| DKI JAKARTA | **21,5%** (terendah) |

**Gradien regional 16 poin persen** (Jatim 37% vs Jakarta 21%). Bisa berarti standar pemeriksaan berbeda
atau kepatuhan riil berbeda — tidak bisa dibedakan tanpa data lebih lanjut.

## 6.6 Residivis Sarana — Dua Tipe Berlawanan

### Industri besar patuh (rutin diinspeksi, selalu bersih)
| Sarana | Inspeksi | TMK % |
|---|---|---|
| BINTANG TOEDJOE | 43 | **0%** |
| STERLING PRODUCTS INDONESIA | 37 | 0% |
| GURIHCLOUD SUKSES PERKASA | 28 | 0% |
| SOHO INDUSTRI PHARMASI | 24 | 4% |

### Ritel kecil bandel (berulang kena, tetap bandel)
| Sarana | Inspeksi | TMK % |
|---|---|---|
| KIMIA FARMA APOTEK (Batam) | 19 | **63%** |
| SAHABAT (Mimika) | 19 | 47% |
| BERKAH (Gorontalo) | 22 | 23% |
| KUNING INDAH (Jember) | 13 | **92%** |
| JADI JAYA (Tanjungbalai) | 11 | 91% |

### 100% TMK (≥8 inspeksi, selalu gagal)
| Sarana | Inspeksi | Komoditi |
|---|---|---|
| BUNGA MASAMBA CV (Palopo) | 8 | PRODUK PANGAN |
| IFK KABUPATEN BIMA | 8 | OBAT |
| **MUSTIKA RATU TBK** (Jakarta) | 8 | OBAT TRADISIONAL, SUPLEMEN |

**MUSTIKA RATU TBK** menonjol — brand nasional terkenal, 8 inspeksi 2020-2025 SEMUA TMK (7 OT + 1 suplemen).
Tidak ada grade/issue → kemungkinan inspeksi kasus/intensifikasi. Anomali yang layak audit khusus.

## 6.7 Efektivitas Penargetan (RUTIN vs TARGETED)

```sql
SELECT CASE WHEN tujuan_pemeriksaan ILIKE '%RUTIN%' THEN 'RUTIN'
            WHEN tujuan ILIKE '%KASUS%' OR '%INTENSIFIKASI%' OR '%RENCANA AKSI%' THEN 'TARGETED'
            ELSE 'LAINNYA' END,
  count(*), count(*) FILTER(WHERE kesimpulan='TMK'), round(100.0*.../...);
```

| Tipe | Total | TMK % |
|---|---|---|
| RUTIN | 197.383 | 29,9% |
| TARGETED | 33.686 | 30,3% |
| LAINNYA | 21.095 | 29,0% |

**Insight**: TMK rate TARGETED (30,3%) hanya sedikit lebih tinggi dari RUTIN (29,9%).
Selisih kecil ini mengejutkan — penargetan BPOM tidak terlalu efektif dalam menangkap pelanggar.
(Namun jika dilihat per sub-tujuan: RENCANA AKSI 53%, KASUS 39% — penargetan spesifik memang lebih tinggi.)

## 6.8 Profil Pelanggaran per Komoditi

Dari `tp_kategori` di tabel temuan:

| Pelanggaran | % dari semua temuan | Komoditi dominan |
|---|---|---|
| TIE (Tanpa Izin Edar) | 51,9% | PANGAN & KOSMETIK (impor ilegal) |
| ED (Kedaluwarsa) | 19,8% | OBAT (apotek/toko obat) |
| Temuan Obat Keras | 7,3% | OBAT (dijual tanpa resep) |
| Rusak/Substandard | 6,5% | PANGAN |
| BKO (Bahan Kimia Obat) | 3,3% | OBAT TRADISIONAL & KOSMETIK (dioplos) |

**Pola bisnis**:
- Kosmetik & Pangan → TIE (produk impor ilegal tanpa izin BPOM)
- Obat → Kedaluwarsa + obat keras liar
- Jamu/OT & Kosmetik → BKO (dicampur bahan kimia berbahaya)
- **BKO+TIE** (6.810 kasus) = produk paling berbahaya: ilegal DAN dioplos
