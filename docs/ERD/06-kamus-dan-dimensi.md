# 06 — Kamus & Dimensi

> Semua arti kode ada di sini. Tanpa kamus, `jenis_id = 16` tidak berarti apa-apa.
>
> Verifikasi: 22 Sep 2026.

---

## 1. `dim_master_data` — 1.999 kode, **72 tipe kamus** dalam satu tabel

Satu tabel menyimpan semua dropdown aplikasi, dibedakan kolom `type`. Karena itu **setiap join wajib menyebut `type`** ([03-aturan-join.md](03-aturan-join.md) Pola 1).

Tipe yang dipakai domain pemeriksaan:

| `type` | Kode | Dipakai untuk |
|---|---:|---|
| `BENTUK_SEDIAAN` | 142 | `fact_pemeriksaan.sediaan_kode` (jarang terisi) |
| `SAMPEL_UNIT` | 82 | `unit_id`, `unit_kode` |
| `TUJUAN_PEMERIKSAAN` | 48 | `tujuan_id` (Rutin / Kasus) |
| `SARAN_TINDAK_LANJUT` | 35 | `tl_saran_pusat` (99,8% murni), sebagian `tl_saran` |
| `JENIS_SARANA` | 32 | `jenis_id`, `dim_sarana.type_id` |
| `KATEGORI_TEMUAN_PRODUK` | 28 | `bridge_pemeriksaan_temuan.kategori_kode` |
| `TL_DISTRIBUSI` | 23 | `tl_saran` |
| `KOMODITI` | 17 | `bridge_pemeriksaan_komoditi_pbf.komoditi_kode` |
| `TEMUAN_OBSERVATION` | 17 | `bridge_pemeriksaan_temuan_observasi.observasi_kode` |
| `TL_PRODUK_TEMUAN` | 15 | `bridge_pemeriksaan_temuan.tindakan_kode` |
| `JENIS_KLASIFIKASI` | 15 | `klasifikasi_id` (jenis komoditi) |
| `ASPEK_KTL` | 10 | `dim_pemeriksaan_aspek.aspek_ktl_kode` |
| `STATUS_SARANA` | 7 | `dim_sarana.status_sarana`, `fact_pemeriksaan.status_ss` |
| `JENIS_KASUS` | 5 | `kasus_id` |
| `FOKUS_PEMERIKSAAN` | 5 | `bridge_pemeriksaan_fokus_pbf.fokus_kode` |
| `CLASS_SARANA` | 4 | `klasifikasi_sarana_kode` (khusus Pangan) |
| `METODE_INSPEKSI` | 3 | `metode_inspeksi` |

Tipe terbesar keseluruhan: `TUJUAN_SAMPLING` 465 · `JENIS_PANGAN_68` 235 · `JENIS_PANGAN` 227 · `BENTUK_SEDIAAN` 142 · `KATEGORI_PANGAN` 127 — tiga yang pertama milik domain lain (pengujian/pangan), bukan pemeriksaan.

**Soft-delete**: 1.994 aktif + 5 `dihapus_di_sumber = true` (Aturan #19).

### Golongan Sardis/Saryan pada `JENIS_SARANA`

| `parent_name` | Jumlah kode | Arti |
|---|---:|---|
| `Produksi` | 8 | Saryan — pabrik (Pangan MD, OT/CPOTB, Kosmetik/CPKB, Sarana Produksi Obat, Suplemen manufaktur) |
| `Distribusi` | 11 | Sardis — PBF, IFK, IFP, Pangan, Kosmetik, OT, Suplemen (peredaran) |
| `Pelayanan` | 7 | Saryan — Apotek, PKM, Klinik, Toko Obat, IFRS swasta/pemerintah |
| *(tanpa parent)* | 4 | tidak masuk 3 golongan |
| `Tidak Berizin` (id 223445) | 2 | golongan terpisah |

Pemetaan jenis sarana ↔ kasus (25 jenis di `fact_pemeriksaan`):

| Jenis sarana | Kasus | | Jenis sarana | Kasus |
|---|---:|---|---|---:|
| Pangan | 61.831 | | Suplemen Kesehatan (17) | 6.899 |
| Kosmetik | 36.999 | | IFRS Swasta (106) | 4.556 |
| Apotek | 27.696 | | IFRS Pemerintah (748) | 3.809 |
| Pangan MD | 26.521 | | IFK (747) | 3.148 |
| PKM | 19.860 | | OT (CPOTB) (4) | 2.937 |
| Obat Tradisional | 17.260 | | Kosmetik (CPKB) (7) | 2.610 |
| Pangan IRT | 10.313 | | Sarana Produksi Obat (8) | 915 |
| Klinik | 10.258 | | IFP (12) | 339 |
| Intensifikasi Pengawasan Khusus | 9.061 | | Suplemen (9) | 285 |
| Toko Obat | 6.943 | | Bahan Berbahaya | 108 |
| PBF | 6.934 | | UMKM → MD / KKP / Daring / MD old | 52 / 11 / 1 / 2 |

---

## 2. `dim_pemeriksaan_aspek` — 47 baris: satu-satunya kamus aspek

Grain: 1 baris = 1 `area_key` mentah dari form. Kolom: `area_key` (PK) · `aspek_ktl_kode` · `aspek_ktl_nama` · `aspek_label` · `status_kamus`.

| `status_kamus` | Jumlah | Arti |
|---|---:|---|
| `resmi` | 40 | punya padanan di kamus resmi BPOM |
| `belum_ada_di_kamus` | 7 | belum ada di `ASPEK_KTL` — pakai `aspek_label` |

**Tujuh yang belum ada di kamus**: `tx_penerimaan_obat`, `tx_penerimaan_param` (Penerimaan) · `tx_pengembalian_mutasi`, `tx_pengembalian_retur`, `tx_pengembalian_sipnap` (Pengembalian) · `tx_efek_samping_sas`, `tx_pencantuman_kode_sas` (SAS).

Saat menampilkan label, selalu:

```sql
COALESCE(a.aspek_ktl_nama, a.aspek_label) AS aspek
```

Kalau tidak, Penerimaan dan Pengembalian hilang dari hasil — padahal keduanya aspek bervolume besar.

### Kamus resmi `ASPEK_KTL` (10 entri)

| id | code | nama |
|---|---|---|
| 476 | 01 | Label |
| 477 | 02 | Pemusnahan |
| 478 | 03 | Pencatatan dan Pelaporan |
| 479 | 04 | Pengadaan |
| 480 | 05 | **Penyaluran** (= "Pendistribusian" di form) |
| 481 | 06 | Penyerahan |
| 482 | 07 | Penyimpanan |
| 483 | 08 | Perizinan |
| 484 | 09 | Personalia |
| 485 | 10 | Produksi |

⚠️ **Penerimaan dan Pengembalian tidak ada di kamus resmi**, padahal form menanyakannya. Ini butuh konfirmasi BPOM.

### Volume per aspek (jalur `bridge_pemeriksaan_skor_operasional`, tanpa data uji)

| Aspek | Item | Kasus | status kamus |
|---|---:|---:|---|
| Penyerahan | 503.545 | 63.845 | resmi |
| Penyimpanan | 360.852 | 63.845 | resmi |
| Pengadaan | 230.935 | 63.845 | resmi |
| Pengembalian | 146.945 | 63.845 | belum_ada_di_kamus |
| Penerimaan | 127.690 | 63.845 | belum_ada_di_kamus |
| Pemusnahan | 103.245 | 63.845 | resmi |
| Pencatatan dan Pelaporan | 28.665 | 25.808 | resmi |
| Penyaluran | 13.547 | 5.811 | resmi |
| Efek Samping (SAS) | 2.885 | 2.885 | belum_ada_di_kamus |
| Pencantuman Kode (SAS) | 2.885 | 2.885 | belum_ada_di_kamus |

---

## 3. `dim_pemeriksaan_kesimpulan` — 14 baris, 3 kelompok

| Kelompok | `id` | `sumber` | Isi | Pemakaian |
|---|---|---|---|---|
| Umum | 1–5 | `vocab_umum` | MK (1) · TMK (2) · TTP (3) · TDP (4) · TMBB (5) | `kesimpulan_balai_id` / `kesimpulan_pusat_id` |
| CPOB | 791–794 | `dim_master_data (CPOB_FULLFILLMENT)` | Memuaskan · Baik · Cukup · Kurang | khusus `jenis_id`=8 |
| Vaksin | 795–799 | `vocab_umum`, `dugaan_belum_konfirmasi` | TMS Mayor 1 · TMS Mayor 2 · MS · TMS Kritikal · TMS Mayor 3 | **hanya** lewat `vaksin_kesimpulan_id` |

**Pemakaian nyata:**

| Kode | Sebagai kesimpulan balai | Sebagai kesimpulan pusat |
|---|---:|---:|
| MK | 177.944 | 45.599 |
| TMK | 76.090 | 17.669 |
| TTP | 1.557 | 324 |
| TDP | 794 | 156 |
| TMBB | 18 | — |
| *(NULL)* | 2.299 | 195.600 |
| 791 Memuaskan / 792 Baik / 793 Cukup / 794 Kurang | 76 / 345 / 118 / 107 (balai **atau** pusat) | |

Catatan penting:
- Kesimpulan pusat mayoritas NULL (75,4%) — **review Pusat memang parsial**, jangan dibaca sebagai "belum diproses".
- `keterangan` masih NULL untuk TTP/TDP/TMBB dan kelima kode vaksin.
- Untuk `jenis_id`=8, `kesimpulan_balai_id` memuat **dua taksonomi sekaligus** (vonis kasus MK/TMK/TTP dan tingkat pemenuhan CPOB) — pisahkan sebelum membuat rekap.
- `vaksin_kesimpulan_id` terisi di **1.979** kasus; 1.976 di antaranya terisi bersamaan dengan `kesimpulan_balai_id` (Aturan #20).

---

## 4. `dim_status_code` — 35 baris, 16 domain pemeriksaan

| `domain` | Jumlah | Isi |
|---|---:|---|
| `pemeriksaan` | 16 | DRAFT · DRAFT_REVISE · DRAFT_PUSAT · DRAFT_PUSAT_REVISE · VERIFY1–VERIFY7 · VERIFY_P1–P3 · FINISHED · FINISHED_PUSAT |
| `pengawasan` | 19 | kode angka `0`–`7`, `8`, `9`, `990`–`997`, `999` |

⚠️ **`status_label` kosong di seluruh 35 baris.** Tabel ini hanya menyimpan kode; label harus diambil dari luar.

Distribusi kasus per status:

| Status | Kasus | Porsi | Arti alur |
|---|---:|---:|---|
| VERIFY4 | 167.116 | 64,4% | macet di Operator Pusat |
| VERIFY5 | 46.619 | 18,0% | di Supervisor Pusat |
| FINISHED | 29.042 | 11,2% | selesai |
| DRAFT_REVISE | 5.108 | 2,0% | dikembalikan |
| VERIFY7 | 4.784 | 1,8% | |
| DRAFT | 3.297 | 1,3% | belum dikirim |
| VERIFY6 | 1.008 | 0,4% | |
| VERIFY1 | 640 | 0,2% | |
| VERIFY2 / DRAFT_PUSAT / VERIFY_P1 / FINISHED_PUSAT / VERIFY_P3 / VERIFY3 / DRAFT_PUSAT_REVISE / VERIFY_P2 / NULL | 1.734 | 0,7% | sisanya |

Alur resminya: `draft` → `step_verify1..7` → `finished`, dengan jalur Pusat opsional `draft_pusat` → `step_verify_p1..p3` → `finished_pusat`.

---

## 5. `dim_balai` — 108 baris, sumber breakdown regional

| `regional` | `regional_name` | Jumlah balai |
|---:|---|---:|
| 0 | `-` | 1 |
| 0 | Jakarta | 2 |
| 1 | Medan | 14 |
| 2 | Pekanbaru | 11 |
| 3 | **Jakarta** | 2 |
| 3 | **Semarang** | 14 |
| 4 | Samarinda | 11 |
| 5 | Makassar | 8 |
| 6 | Manado | 7 |
| 7 | Surabaya | 13 |
| 8 | Jayapura | 5 |
| *(NULL)* | *(NULL)* | 20 |

⚠️ **Kode `regional` tidak konsisten** — kode `3` dipakai untuk dua nama berbeda (Jakarta & Semarang), kode `0` juga. **Selalu pakai `regional_name`.**

Distribusi kasus per regional: Semarang 60.504 · Medan 40.315 · Surabaya 36.953 · Pekanbaru 35.999 · Makassar 27.533 · Samarinda 24.483 · Manado 17.264 · Jayapura 15.240 · (tanpa regional) 1.057. **Hanya 8 regional** — bukan 34 provinsi.

`dim_balai` juga memuat `target_sampling` dan `target_sarana` — dasar perbandingan target vs realisasi.

---

## 6. Dimensi lain

### `dim_sarana` — 441.821 baris, 24 kolom

440.192 aktif · 1.629 bertanda `dihapus_di_sumber = true`. Semua baris dibawa (Aturan #19), jadi jumlahnya utuh termasuk yang sudah di-soft-delete.
**Status**: `aktif = true` 440.093+1.628 · `aktif = false` 100.

| Uji | Hasil |
|---|---|
| Sarana yang belum pernah diperiksa | 271.262 |
| Orphan `sarana_id` dari fact | **0** |
| `provinsi_id` tak ketemu di `dim_provinsi` | 231 |
| `kabupaten_id` tak ketemu di `dim_kabupaten` | 950 |

Memuat banyak ID silang sistem lain yang artinya belum digali: `id_pelaku_usaha`, `legal_id`, `idcdob`, `kode_satu_sehat`, `id_siptlama`, `plant`. ⚠️ `legal_id` merujuk **dua** kamus (Pola 4).

### `dim_produk` — 176.879 baris, 17 kolom

Dim **bersama lintas domain** (Aturan #10) — gabungan referensi dari Pengawasan dan Pemeriksaan.
`is_imported` = `false` untuk **semua** baris → tidak informatif. 56.754 produk belum pernah jadi temuan. Orphan dari `bridge_pemeriksaan_temuan.tp_product_id`: **15**.
Kolom berguna: `nomor_registrasi` (NIE, prefix `MD`/`ML`/`NA`/`TR`/`DK`/`LK`/…), `nama_produk`, `pendaftar`, `produsen`, `kategori`, `kemasan`, `golongan`, `tgl_terbit`, `tgl_kadaluarsa`.

### `dim_user` — 13.322 baris, 11 kolom

`fullname` (nama inspektur & verifikator), `username`, `email`, `balai_id`, `roles_id`, `group_id`, `active`, `kode_sarana`, `last_login`, `is_core`.
⚠️ `balai_id = 0` untuk **4.570** user — itu **penanda user tanpa balai** (mis. user pusat), bukan join rusak.
Orphan dari `bridge_pemeriksaan_petugas.user_id`: **13 user** (169 baris) — jumlahnya kecil dan tidak mengganggu agregat.

### `dim_date` — 7.670 baris

`date_key` (PK, date) · `tahun` · `bulan` · `nama_bulan` · `tanggal` · `kuartal` · `minggu_ke` · `hari_ke_iso` · `nama_hari` · `is_weekend` · `bulan_tahun` · `awal_bulan` · `akhir_bulan`. Rentang mulai **2015-01-01**.
⚠️ Kolom tanggalnya bernama **`date_key`**, bukan `full_date`/`calendar_date`.

### `dim_provinsi` (44) & `dim_kabupaten` (664)

Dimensi wilayah. Wilayah sarana diambil dari `dim_sarana.provinsi_id`/`kabupaten_id`, bukan dari `fact_pemeriksaan`.
