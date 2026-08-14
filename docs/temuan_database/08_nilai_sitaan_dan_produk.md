# 08 — Nilai Sitaan & Produk Teratas

> Analisis finansial temuan produk, nilai sitaan, produk/registrar/negara teratas.

## 8.1 Nilai Sitaan: Bruto vs Bersih

```sql
SELECT 'total_bruto' AS metrik, round(sum(tp_harga_total),0) AS nilai, count(*) AS n
FROM mv_pemeriksaan_temuan WHERE tp_harga_total IS NOT NULL
UNION ALL
SELECT 'minus_INFALGIN', round(sum(tp_harga_total),0), count(*)
FROM mv_pemeriksaan_temuan WHERE tp_harga_total IS NOT NULL AND tp_harga_total < 7000000000000
UNION ALL
SELECT 'bersih_wajar', round(sum(tp_harga_total),0), count(*)
FROM mv_pemeriksaan_temuan WHERE tp_harga_total > 0 AND tp_harga_total < 1000000000;
```

| Metrik | Nilai (Rp) | Record |
|---|---|---|
| **Total bruto (tercemar)** | **7.739.531.958.637** (Rp 7,74 T) | 295.995 |
| Minus 1 record INFALGIN | 662.149.750.237 (Rp 662 M) | 295.994 |
| **Bersih wajar (Rp < 1 M)** | **199.799.719.114** (Rp 199,8 M) | 281.863 |

**1 record INFALGIN = 91% dari total bruto.** Nilai sitaan RIIL ≈ **Rp 200 miliar**, bukan Rp 7,74 triliun.

## 8.2 INFALGIN — Error Pemindahan Kolom

```sql
SELECT product_name, registrar, tp_jml_temuan, round(tp_harga_total,0)
FROM mv_pemeriksaan_temuan WHERE tp_unit_id=263 ORDER BY tp_harga_total DESC LIMIT 5;
```

| Produk | Registrar | tp_jml_temuan | tp_harga_total |
|---|---|---|---|
| INFALGIN | GRAHA FARMA | **20.221.092.024** | **7.077.382.208.400** |
| DANASONE | HEXPHARM JAYA | 4.000 | 640.000.000 |
| TURPAN | CORSA INDUSTRIES | 1.053.000 | 274.833.000 |

`tp_jml_temuan = 20221092024` = **datetime 2022-10-09 20:24 yang terselip di kolom kuantitas**.
Ini BUKAN error harga — ini **error pemindahan kolom** (column misalignment).
8.087 baris dengan `tp_unit_id=263` (obat keras) menyeret rata-rata kuantitas ke 2,5 juta.

## 8.3 Kontaminasi Lainnya

| Anomali | Detail |
|---|---|
| Nilai negatif | 128 record `tp_harga_total < 0` (min -5.360.000) |
| Nilai nol | 13.931 record `tp_harga_total = 0` |
| HTML encoding error | "&AMP;AMP; GLOW WATER CREAM" — 3× @ Rp 36,4 miliar |
| Harga per unit ekstrem | TEH BUBUK Rp 82,5 jt/unit, CASTLE MALTING Rp 69,9 jt/unit (kemungkinan salah unit) |
| `tp_expire` range | 1900-01-01 s/d 2223-08-31 (outlier di kedua ujung) |

## 8.4 Nilai per Kategori Pelanggaran (bersih, < Rp 1 M)

```sql
SELECT tp_kategori, count(*) AS jml,
  round(avg(tp_harga_total),0) AS avg_total,
  sum(tp_harga_total) AS sum_total
FROM mv_pemeriksaan_temuan
WHERE tp_harga_total > 0 AND tp_harga_total < 1000000000
GROUP BY 1 ORDER BY sum_total DESC LIMIT 10;
```

| Kategori | Record | Avg (Rp) | Sum (Rp M) |
|---|---|---|---|
| TIE (Tanpa Izin Edar) | 150.309 | 2.587.410 | 388.911 |
| ED (Kedaluwarsa) | 57.882 | 2.113.378 | 122.327 |
| Lain - Lain | 5.874 | 5.966.641 | 35.048 |
| Substandard/Rusak | 7.689 | 2.409.603 | 18.527 |
| Illegal/TIE | 5.667 | 3.210.495 | 18.194 |
| TMK Label | 3.062 | 5.887.039 | 18.026 |

**TIE (Rp 389 M) = 54% dari nilai total bersih.** Produk impor ilegal bernilai paling besar.
Avg harga ED (Rp 2,1 jt) > TIE (Rp 2,6 jt) — produk kedaluwarsa cenderung barang mahal (obat/suplemen).

## 8.5 Top 15 Produk Paling Sering Ditemukan

| Produk | Temuan | Total Unit | Total Nilai (Rp) |
|---|---|---|---|
| KRIMER KENTAL MANIS | 2.217 | 15.532 | 3.805.340.939 |
| MONTALIN | 1.261 | 38.870 | 641.568.840 |
| TAWON LIAR | 908 | 37.400 | 355.774.404 |
| AFRICA BLACK ANT | 653 | 6.582 | 100.937.961 |
| SUSU STERIL | 641 | 1.959 | 21.264.137 |
| PI KANG SHUANG | 639 | 10.479 | 132.643.844 |
| URAT MADU | 619 | 6.349 | 90.328.900 |
| URAT MADU BLACK | 599 | 7.018 | 95.528.375 |
| WAN TONG | 548 | 10.940 | 136.304.300 |

**Pola**: Produk jamu/potensi (MONTALIN, TAWON LIAR, AFRICA BLACK ANT, URAT MADU) mendominasi.
Ini produk BKO (jamu dioplos bahan kimia obat) — Mayoritas dari impor ilegal China.

## 8.6 Top 15 Registrar (Pemilik Produk)

| Registrar | Temuan |
|---|---|
| (kosong/"-") | 43.229 |
| PT NESTLE INDONESIA | 2.152 |
| CHINA | 2.020 |
| PT. HEINZ ABC INDONESIA | 1.917 |
| PJ AIR MADU | 1.713 |
| PT INDOLAKTO | 1.707 |
| P.T. FRISIAN FLAG INDONESIA | 1.603 |
| MALAYSIA | 1.542 |
| PJ AIR MADU MAGELANG | 1.465 |

**Catatan**: "CHINA" dan "MALAYSIA" sebagai registrar = produk impor tanpa registrar formal Indonesia.
PT NESTLE, HEINZ ABC, INDOLAKTO = brand besar yang produknya sering kena TIE/ED.

## 8.7 Top 15 Negara Asal Produk

| Negara | Temuan | Total Nilai (Rp) |
|---|---|---|
| INDONESIA | 190.735 | 7.509.861.114.427 |
| CHINA | 16.681 | 21.007.773.474 |
| MALAYSIA | 9.132 | 45.329.640.396 |
| THAILAND | 2.940 | 1.362.451.495 |
| KOREA | 1.827 | 4.041.921.813 |
| CINA (= China varian) | 1.649 | 7.837.766.418 |
| USA | 1.028 | 5.464.200.070 |
| TIONGKOK (= China varian) | 566 | — |
| PRC (= China varian) | 396 | — |

**⚠️ 1.299 "negara" berbeda.** China ditulis 4+ cara: CHINA + CINA + TIONGKOK + PRC = 19.292 total.
"-" sebagai negara: 53.063 baris. Normalisasi WAJIB sebelum analisis negara asal.

## 8.8 Kolom Mati Sejati

| Kolom | Null % | Record terisi | Vonis |
|---|---|---|---|
| `tp_pelanggaran` | 99,996% | 12 | **Mati sejati** — kolom sejenis (tp_kategori) terisi penuh |
| `tp_netto` | 99,998% | 5 | **Mati sejati** — tidak ada alasan struktural |

Isi `tp_pelanggaran` yang ada (12 record): "ED", "Expired", "Kadaluarsa", "TIE", "menjual kosmetik yang TIE".
Ini duplikasi `tp_kategori` — kolom ini tak pernah dipakai secara serius.

---

## 8.x `tp_negara` — kolom teks bebas 1.299 nilai, dan kenapa "temuan impor" selalu salah

Pertanyaan *"tampilkan negara-negara dengan temuan impor pada tahun X"* muncul berulang di log KAI
dan menjadi `BPOM User Relevant Query` #113. SQL resminya memakai satu baris filter:

```sql
WHERE lower(mpt.tp_negara) != 'indonesia'
```

### Yang sebenarnya ada di kolom itu (live 2026-08-13, 296.987 baris)

```sql
SELECT CASE
         WHEN lower(tp_negara)='indonesia'            THEN 'indonesia'
         WHEN tp_negara IN ('-','','--')              THEN 'SENTINEL'
         WHEN lower(tp_negara) IN ('lokal','local')   THEN 'lokal'
         WHEN tp_negara IS NULL                       THEN 'NULL'
         ELSE 'negara lain' END AS grup,
       count(*) AS baris, count(DISTINCT tp_negara) AS nilai,
       round(sum(tp_harga_total)/1e9,2) AS miliar
FROM mv_pemeriksaan_temuan GROUP BY 1 ORDER BY 2 DESC;
```

| Grup | Baris | Nilai unik | Nilai temuan (Rp M) |
|---|--:|--:|--:|
| **indonesia** | 190.740 | **9** | 7.509,86 |
| **SENTINEL** (`'-'`, `''`) | **53.130** | 2 | 53,87 |
| **negara lain** (impor sebenarnya) | **46.236** | **1.285** | **159,59** |
| NULL | 6.039 | — | 11,76 |
| **lokal** | 842 | **3** | 4,44 |

**Filter `<> 'indonesia'` mengembalikan 106.247 baris** (SENTINEL + negara lain + lokal), padahal
yang benar-benar impor hanya **46.236**. Sentinel `'-'` sendirian menyumbang 53.130 baris — lebih
banyak daripada seluruh temuan impor sejati.

### Sembilan ejaan "Indonesia" dan tiga ejaan "lokal"

| Ejaan | Baris | | Ejaan | Baris |
|---|--:|---|---|--:|
| `Indonesia` | 167.319 | | `lokal` | 534 |
| `indonesia` | 13.507 | | `Lokal` | 279 |
| `INDONESIA` | 9.611 | | `LOKAL` | 29 |
| `iNDONESIA` | 224 | | | |
| `INdonesia` | 75 | | | |
| `InDONESIA` · `IndonesIa` · `IndonesiA` · `indonesiA` | 1 masing-masing | | | |

`lower(tp_negara)='indonesia'` sudah menangkap kesembilan ejaan — tetapi **`lokal` (842 baris)
lolos** dan terhitung sebagai impor.

### Satu negara, banyak penulisan — peringkat "negara asal" tidak sahih tanpa normalisasi

```sql
SELECT tp_negara, count(*) FROM mv_pemeriksaan_temuan
WHERE lower(tp_negara) LIKE '%china%' OR lower(tp_negara) LIKE '%korea%'
   OR lower(tp_negara) LIKE '%tiongkok%' GROUP BY 1 ORDER BY 2 DESC;
```

| Penulisan | Baris | | Penulisan | Baris |
|---|--:|---|---|--:|
| `China` | 14.103 | | `Korea` | 1.479 |
| `china` | 1.861 | | `korea` | 278 |
| `CHINA` | 698 | | `Korea Selatan` | 246 |
| `Tiongkok` | 348 | | `KOREA` | 66 |
| `tiongkok` | 201 | | | |
| `TIONGKOK` | 17 | | | |
| `Made in China` | 31 | | | |
| `Xingfu Biotechnology (Guangdong) Co., Ltd. (China)` | 53 | | | |

**Tiongkok = China.** Digabung, RRT menjadi **17.312 baris**; terpecah, `China` tampil 14.103 dan
`Tiongkok` tidak masuk lima besar. Kolom ini juga menampung **nama perusahaan** (`Xingfu
Biotechnology…`), bukan hanya negara.

### Aturan yang harus dipakai

1. **Domestik** = `lower(tp_negara) IN ('indonesia','lokal','local')`.
2. **Sentinel** = `tp_negara IN ('-','','--') OR tp_negara IS NULL` → **bukan impor**, laporkan
   sebagai "asal tidak tercatat" (59.169 baris = 19,9%).
3. **Impor** = sisanya (46.236 baris), dan **wajib dinormalisasi** minimal untuk China/Tiongkok
   dan Korea/Korea Selatan sebelum diperingkat.
4. Sebutkan bahwa 19,9% temuan tidak punya asal tercatat — tanpa itu, peringkat impor terlihat
   lebih lengkap daripada kenyataannya.

## 8.y 946 baris tanpa tanggal = draft, bukan kohort migrasi

`11_kualitas_data_dan_anomali.md` §11.2 menyimpulkan NULL tanggal bersifat operasional. Rincian
statusnya memperkuat itu:

```sql
SELECT status, count(*) FROM mv_pemeriksaan WHERE tanggal_mulai IS NULL GROUP BY 1 ORDER BY 2 DESC;
--  DRAFT 800 · DRAFT_PUSAT 131 · VERIFY4 12 · DRAFT_REVISE 2 · VERIFY2 1
```

**931 dari 946 (98,4%) berstatus draft** — inspeksi yang dibuat tetapi belum dijalankan. Hanya 15
baris yang sudah masuk alur verifikasi tanpa tanggal, dan itu yang layak disebut anomali.
Konsekuensi teknis: baris-baris ini **tidak pernah masuk `mv_pemeriksaan_agg`** (agg berjumlah
256.536 = 257.482 − 946), sehingga total dari agg selalu kurang 946 dari total fakta.
