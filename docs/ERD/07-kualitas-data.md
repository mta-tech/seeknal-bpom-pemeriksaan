# 07 — Kualitas Data & Batas Pemakaian

> Ringkasnya: kolom mana yang lengkap, mana yang kosong permanen (aplikasi memang tidak mengisinya), mana yang bisa diperbaiki, dan apa yang perlu dikonfirmasi ke pemilik data.
>
> Semua angka = kondisi `staging` per **22 Sep 2026**.

---

## 1. Yang sudah lengkap (jangan diutak-atik)

| Item | Nilai |
|---|---:|
| Header kasus (`fact_pemeriksaan`) | 259.348 |
| `id` unik | 259.348 = 259.348 (tanpa duplikat) |
| `dim_sarana` | 441.821 |
| `dim_master_data` | 1.999 |
| `dim_provinsi` / `dim_kabupaten` | 44 / 664 |
| Grade terisi | 44.400 |
| Orphan `sarana_id` · `balai_id` · `jenis_id` · `status_id` · `kesimpulan_balai_id` | **0** semua |
| Orphan bridge → fact | 0 |

---

## 2. Kosong permanen — aplikasi tidak pernah mengisinya

Kolom ini tidak akan bertambah isinya karena aplikasi memang tidak pernah mengisinya:

| Kolom | Kosong | Keterangan |
|---|---:|---|
| `bridge_pemeriksaan_petugas.user_id` | 169 baris (13 user) | 13 user itu tidak ada padanannya di `dim_user` |
| `bridge_pemeriksaan_temuan.tp_product_id` | 15 | produk tidak ada di `dim_produk` |
| `fact_pemeriksaan_approval.created_by` | 713 | user tidak ada di `dim_user` |
| `dim_sarana.provinsi_id` | 231 | kode wilayah tidak ada di `dim_provinsi` |
| `dim_sarana.kabupaten_id` | 950 | kode wilayah tidak ada di `dim_kabupaten` |
| `bridge_pemeriksaan_temuan_observasi.observasi_kode` | 295 | nilainya memang NULL |
| `kategori_kode` tak ketemu kamus | 444 baris | termasuk elemen `[null]` di dalam array |
| `fact_pemeriksaan.kesimpulan_pusat_id` | 195.600 | review Pusat memang parsial, bukan "belum diproses" |
| `dim_status_code.status_label` | 35 dari 35 | label tidak pernah diisi |

---

## 3. Bisa dilengkapi — datanya ada, belum terbaca di `staging`

| Yang belum lengkap | Kondisi sekarang | Yang dibutuhkan |
|---|---:|---|
| `tx_fast_moving_antibiotika` | 25.780 kasus tanpa label aspek | pemetaan section → aspek (isinya terstruktur: nama zat aktif, jumlah penjualan) |
| Nama section yang belum masuk kamus aspek | 47 dipetakan dari **108** section pelayanan | pemetaan 61 section sisanya |
| Kasus `pola1_direct` tanpa baris checklist | 10.211 | penyelidikan per kasus |
| `clusterF_cpkb` (`jenis_id`=7) | 2.610 kasus tanpa bridge sama sekali | tabel bridge baru |
| Kasus `pola1_observation` tanpa baris | 1.665 | penyelidikan per kasus |
| Kasus `clusterC_skor` tanpa baris | 398 | penyelidikan per kasus |
| Kasus `clusterC_naratif` tanpa baris | 145 | penyelidikan per kasus |
| `pola1_nested` / `pola2_klasifikasi` / `lainnya` tanpa baris | 254 / 115 / 14 | penyelidikan per kasus |
| Tingkat pemenuhan CPOB (`kesimpulan_balai_id` 791–794) | 646 kasus | dicatat lebih banyak di aplikasi (876) → kurang 230 |

**Total kasus tanpa baris bridge apa pun: 15.412 (5,9%)** — rincian per flag ada di [04-routing-bridge.md](04-routing-bridge.md) §3.

---

## 4. Kekritisan: kondisi sekarang

| Jalur | Kondisi |
|---|---|
| Per **kasus** (`kritis_count`/`major_count`/`minor_count`) | **10.736 kasus** terisi |
| Per **kasus** (`level_kesimpulan`) | **9.064 kasus** — nilai: Major · Baik · N/A · Minor · Kritikal |
| Per **klausul** (dari `bridge_pemeriksaan_checklist.nilai_aspek`) | **604.842 item** |

Sebaran per jenis sarana (per klausul):

| Jenis sarana | Item ber-severity | Total item |
|---|---:|---:|
| Pangan MD | 319.196 | 2.408.942 |
| Pangan | 219.845 | 2.921.028 |
| Pangan IRT | 35.143 | 379.327 |
| PBF | 29.473 | 111.508 |
| IFK | 22.258 | 83.831 |
| IFP | 1.997 | 8.578 |
| UMKM / Intensifikasi | 313 / 16 | 3.060 / 1.214 |
| **Kosmetik · Obat Tradisional · Suplemen · Bahan Berbahaya** | **0** | 807.482 · 397.464 · 264.317 · 1.414 |

Jadi: kekritisan **tersedia** untuk sebagian jenis sarana saja. Untuk Kosmetik/OT/Suplemen, satu-satunya angka kekritisan yang ada adalah per kasus — dan itu pun hanya untuk 10.736 kasus dari 259.348.

---

## 5. Perubahan kondisi 21 Sep 2026 (kolom & tabel yang baru muncul)

| Hal | Sebelum | Sekarang |
|---|---|---|
| Varian vaksin | 0 baris | **7.660 kasus · 145.540 baris** (`bridge_pemeriksaan_vaksin`) |
| Form naratif faskes | 0 baris | **1.182 kasus · 6.930 baris** (`bridge_pemeriksaan_narasi_faskes`) |
| Kekritisan per kasus | 609 kasus | **10.736 counter + 9.064 `level_kesimpulan`** |
| `dim_pemeriksaan_kesimpulan` | 9 baris | **14 baris** (5 kode vaksin) |
| `dim_sarana` | 440.192 | **441.821** |
| `dim_master_data` | 1.994 | **1.999** |
| `flag_varian_datas` | 7 nilai | **9 nilai** |
| Kolom baru | — | `status_ss` (84.020) · `tp_asset` (59.215) · `updated_at`/`updated_by` (259.348) · `level_kesimpulan` · `vaksin_kesimpulan_id` · `vaksin_bersama_rutin` · `vaksin_status_capa` |
| Gap `clusterC_skor` | 9.271 kasus kosong | **398** |
| Outlier `jumlah_temuan` | maks 20,2 miliar · 137 negatif | **maks 7,7 juta · 0 negatif** |
| Duplikat temuan same-moment | 1.166 | dihapus (Aturan #21) |

Tabel `dim_sarana` dan `dim_master_data` sekarang memuat **semua** baris — termasuk yang sudah di-soft-delete — dengan penanda `dihapus_di_sumber` (Aturan #19).

---

## 6. Cacat kecil yang diketahui (tidak menghalangi)

| Cacat | Skala | Bisa dibersihkan? |
|---|---:|---|
| `bridge_pemeriksaan_checklist.conformity` masih mengandung HTML | 760 dari 95.773 baris terisi | bisa |
| `bridge_pemeriksaan_checklist.catatan` sisa HTML | 1.570 dari 7.388.165 | bisa (diabaikan) |
| `[null]` di dalam array `kategori_kode`/`tindakan_kode` | 81 baris | parser perlu menangani `null` |
| `kategori_kode`/`tindakan_kode` kadang tertukar | mis. kode tindakan `762` tersimpan di kolom kategori | kondisi sumber |
| `dim_balai.regional` kode 3 dipakai dua nama | Jakarta (2 balai) & Semarang (14 balai) | pakai `regional_name` |
| `dim_status_code.status_label` kosong | 35 baris | bisa diisi |
| `jumlah_temuan` nilai besar yang sah tetap terjumlah | kisaran 100 ribu–7,7 juta | jangan pakai `sum()` mentah |
| 6 kode `KATEGORI_TEMUAN_PRODUK` tidak pernah dipakai | termasuk 3 kode TIE duplikat & 2 kode Kedaluwarsa | bisa digabung di kamus |
| `dim_produk.is_imported` | `false` di seluruh 176.879 baris | tidak informatif |

---

## 7. Di luar domain ini

| Apa | Alasan |
|---|---|
| 26 tabel `fact_pengawasan*`, `bridge_pengawasan_*`, `dim_pengawasan_*` | milik domain pengawasan — namanya terlihat di katalog, `SELECT` ditolak |
| Kamus `JENIS_PANGAN` (id 211236) | type ini tidak pernah dirujuk pemeriksaan (0 baris) |
| Kamus `TUJUAN_SAMPLING` (id 223492) | milik domain pengujian |

---

## 8. Checklist konfirmasi ke pemilik data

| # | Hal | Yang perlu dikonfirmasi |
|---|---|---|
| C1 | `jenis_pangan_kode` merujuk 2 kamus (`PRODUK_PANGAN` + `JENIS_PANGAN_68`) | memang desainnya begitu? |
| C2 | `tl_saran` merujuk 7 kamus; `tl_saran_pusat` 99,8% satu kamus | memang begitu? perlu didokumentasikan |
| C3 | `dim_sarana.legal_id` merujuk 2 kamus | idem |
| C4 | `tx_fast_moving_antibiotika` (25.780 kasus) belum punya label aspek | sengaja dikecualikan atau terlewat? |
| C5 | 6 kode kategori temuan tidak pernah dipakai | boleh dibersihkan? |
| C6 | 444 baris temuan dengan kategori tak ketemu kamus | perlu pemetaan? |
| C7 | `dim_balai.regional` kode 3 untuk dua nama | mana yang benar? |
| C8 | Penerimaan & Pengembalian tidak ada di kamus resmi `ASPEK_KTL` | perlu ditambahkan? |
| C9 | Arti `kriteria` 1–4 di `temuan_observasi` | kaitannya dengan `KRITERIA_RISIKO`? |
| C10 | Arti kode vaksin (MS, TMS Mayor 1–3, TMS Kritikal) | kriteria pembedanya? |
| C11 | `tp_asset` 59.215 terisi, target tidak ditemukan | merujuk ke sistem mana? |
| C12 | Tingkat pemenuhan CPOB 646 kasus (aplikasi mencatat 876) | kenapa ada yang tidak terbaca? |
| C13 | `dim_status_code.status_label` kosong semua | perlu diisi? |
| C14 | Detail checklist untuk Kosmetik CPKB (2.610 kasus) tidak ada | memang belum dibuatkan bridge-nya? |
