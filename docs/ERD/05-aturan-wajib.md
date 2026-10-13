# 05 — Aturan Wajib Sebelum Menulis Query

> 22 aturan, disusun dari pengalaman salah-query berulang. Nomor aturan **tidak berubah** supaya referensi "Aturan #N" di dokumen lain tetap valid.
>
> Kalau hanya punya waktu membaca satu bagian: baca **Aturan #1, #3, #5, #6, #11**.

---

## A. Kesimpulan & status

**Aturan #1 — Kesimpulan itu FK, bukan teks.**
`fact_pemeriksaan.kesimpulan_balai_id` / `kesimpulan_pusat_id` (integer) **wajib JOIN** ke `dim_pemeriksaan_kesimpulan`. Tidak ada kolom teks langsung — `kesimpulan_balai_kode` sudah di-drop.

**Aturan #3 — Status kasus itu domain-specific.**
`fact_pemeriksaan.status_id` → `dim_status_code`, **wajib filter `domain='pemeriksaan'`**. Tabel yang sama dipakai pengawasan (`domain='pengawasan'`); kode `status_code`-nya sama-sama teks tapi ruang nilai `id` berbeda.
⚠️ `dim_status_code.status_label` **kosong untuk semua 35 baris** — label harus diambil dari luar tabel.

**Aturan #20 — Kesimpulan umum dan kesimpulan vaksin itu independen, bisa terisi bersamaan.**
`kesimpulan_balai_id` (MK/TMK/TTP/TDP/TMBB, atau 4 kode CPOB untuk `jenis_id`=8) dan `vaksin_kesimpulan_id` (MS/TMS Mayor 1–3/TMS Kritikal) **bukan alternatif saling eksklusif**. Terverifikasi: 1.976 dari 1.979 kasus vaksin punya keduanya terisi — dua representasi penilaian berbeda untuk satu kasus. Jangan asumsikan salah satunya cukup.

---

## B. Join

**Aturan #2 — Sarana wajib JOIN.** `sarana_id` cuma angka; nama/alamat/NIB ada di `dim_sarana`.

**Aturan #14 — `penelusuran_id` menyeberangi 2 type kamus** (`PENELUSURAN` dan `TL_PENELUSURAN`). Jangan filter satu `type`.

**Aturan #19 — Soft-delete di-flag, BUKAN di-exclude.**
`dim_sarana.dihapus_di_sumber` dan `dim_master_data.dihapus_di_sumber` — kedua dim memuat **semua** baris, termasuk yang sudah di-soft-delete di aplikasi, dengan penanda boolean. Ini disengaja supaya tidak ada orphan FK dari fact/bridge yang masih merujuk baris tersebut.

| Tabel | `dihapus_di_sumber = false` | `= true` | Total |
|---|---:|---:|---:|
| `dim_master_data` | 1.994 | 5 | 1.999 |
| `dim_sarana` | 440.192 | 1.629 | 441.821 |

Mau mengecualikan yang terhapus? tulis eksplisit `WHERE dihapus_di_sumber IS NOT TRUE`. Tanpa filter, semua baris tetap muncul — itu keputusan desain, bukan bug.

Detail lengkap 4 pola join + peta kolom→kamus ada di [03-aturan-join.md](03-aturan-join.md).

---

## C. Draft & data uji

**Aturan #4 — Filter kasus draft kalau butuh angka final.**
`bridge_pemeriksaan_temuan.is_kasus_draft` — 6.464 baris (2,1%) berasal dari kasus berstatus `DRAFT`/`DRAFT_REVISE`/`DRAFT_PUSAT`. Pakai `WHERE is_kasus_draft = false`.

**Aturan #13 — `is_data_uji` menandai data uji.** 72 `true`, 29 `NULL`, sisanya `false`. Exclude dengan `WHERE is_data_uji IS NOT TRUE`.

---

## D. Grain & routing bridge

**Aturan #5 — `bridge_pemeriksaan_checklist` BUKAN 1 baris per kasus.**
Grain-nya 1 baris = 1 item checklist: **7.388.165 baris** untuk 97.567 kasus. Join ke fact tanpa filter tambahan = fan-out besar (rata-rata ~76 baris/kasus).

**Aturan #6 — Routing wajib pakai `flag_varian_datas`.** Lihat [04-routing-bridge.md](04-routing-bridge.md). Salah tabel → hasil kosong tanpa error.

**Aturan #15 — Cluster F (CPKB) & "lainnya" belum ada bridge detail.**
`jenis_id`=7 (Kosmetik CPKB, 2.610 kasus) dan `jenis_id` 211265/223447 (14 kasus) — hanya header + narasi/approval, **tidak ada** detail per klausul.

**Aturan #16 — `bridge_pemeriksaan_komoditi_pbf` / `_fokus_pbf` bukan cuma PBF.** Cakupannya 3 `jenis_id`: PBF (14), IFK (747), IFP (12) — berbagi bentuk form yang sama.

---

## E. Kamus & aspek

**Aturan #7 — Label aspek di `dim_pemeriksaan_aspek` campuran resmi/tidak.**
`status_kamus`: `'resmi'` (40 baris) vs `'belum_ada_di_kamus'` (7 baris). Selalu tampilkan dengan `COALESCE(aspek_ktl_nama, aspek_label)`.

> ⚠️ **Koreksi 22 Sep 2026**: deskripsi lama menyebut `belum_ada_di_kamus` sebagai "minoritas kecil". Yang benar: Penerimaan (127.702 item) dan Pengembalian (146.958 item) adalah **dua dari empat aspek bervolume terbesar**, tapi namanya tidak ada di kamus resmi `ASPEK_KTL` (10 entri).

**Aturan #8 — Kode temuan (sebagian) sudah dikanonikalisasi.**
`bridge_pemeriksaan_temuan.kategori_kode` / `tindakan_kode` — kode lama sudah digabung ke kode kanonik. Jangan berharap kode lama masih muncul di data.

> ⚠️ **Koreksi 22 Sep 2026**: klaim ini benar untuk **data**, tapi kamusnya masih menyimpan duplikat. Dari 28 kode `KATEGORI_TEMUAN_PRODUK`:
> - **4 kode TIE** — hanya `506` yang dipakai (173.769 baris); `757 Illegal/TIE`, `211213 TIE`, `211239 TIE` = **0 baris**
> - **3 kode Kedaluwarsa** — hanya `840` yang dipakai (64.276); `855` dan `501` = 0 baris
> - **2 kode Rusak — keduanya dipakai**: `856 Rusak` (10.440) + `759 Substandard/Rusak` (9.179)
> - **3 kode bahan berbahaya — semuanya dipakai**: `220132` (1.412) + `220131` (871) + `220133` (445)
> - 6 kode kamus tidak dipakai sama sekali
>
> Artinya: angka TIE dan Kedaluwarsa **tidak** terpecah seperti dugaan awal; yang benar-benar perlu digabung hanya Rusak (2 kode) dan bahan berbahaya (3 kode). Plus 444 baris dengan kategori tak ketemu di kamus.

**Aturan #17 — Kolom array/jsonb di `fact_pemeriksaan`.** `tl_saran`, `tl_saran_pusat`, `sediaan_kode`, `jenis_pangan_kode` bertipe jsonb array — pakai `->>0` untuk elemen pertama atau `jsonb_array_elements_text` untuk expand semua.

> ⚠️ **Koreksi 22 Sep 2026**: kalimat lama "nyaris selalu berisi 1 elemen (>90%)" **tidak berlaku untuk `sediaan_kode`** — kolom itu **99,7% NULL** (hanya 860 baris terisi). Yang terisi justru `tl_saran` (83,1%) dan `tl_saran_pusat` (21,4%).

---

## F. Kolom jsonb & kolom cadangan

**Aturan #11 — `profil_sarana_json` sudah punya tabel turunannya; pakai itu, jangan parsing ulang kolom ini.** Membaca tabel terstruktur selalu lebih cepat dan lebih benar.

| `jenis_id` | Kolom `profil_sarana_json` | Wajib pakai |
|---|---|---|
| 16 / 14 / 747 / 12 | **sengaja di-NULL-kan** | `klasifikasi_sarana_kode` (16) · `bridge_pemeriksaan_komoditi_pbf` / `_fokus_pbf` (14/747/12) |
| 5 (Pangan MD) | masih terisi (cadangan) | `fact_pemeriksaan_profil_pangan_md` + `bridge_pemeriksaan_sertifikat_pangan_md` |
| 109/107/108/106/105/748 (faskes) | masih terisi (cadangan) | `fact_pemeriksaan_profil_faskes` + `bridge_pemeriksaan_personel_faskes` |
| lainnya | jarang terisi | belum ada tabel turunan — parsing langsung boleh |

**Aturan #22 — `tp_asset` referensi eksternal belum teridentifikasi, JANGAN dibuatkan dim.**
`bridge_pemeriksaan_temuan.tp_asset` (59.215 dari 303.521 baris terisi) diduga ID lampiran/foto temuan, tapi tidak ada tabel file/attachment apa pun di `staging` yang bisa dikonfirmasi sebagai targetnya. Biarkan sebagai id mentah.

---

## G. Kebersihan teks & tanggal

**Aturan #9 — HTML sudah di-strip** di `fact_pemeriksaan_narasi.teks`, `fact_pemeriksaan_approval.notes`/`notes_tl`, `bridge_pemeriksaan_checklist.catatan`, `bridge_pemeriksaan_temuan_observasi.catatan`. Sisa kecil di checklist bisa diabaikan.

> ⚠️ **Belum dibersihkan**: `bridge_pemeriksaan_checklist.conformity` masih berisi HTML (`<p class="MsoNoSpacing" ...>`). Padahal kolom itu justru satu-satunya tempat tingkat keparahan per klausul tercatat di varian observasi.

**Aturan #12 — `tgl_start`/`tgl_end` sudah divalidasi** dari outlier tahun mustahil (mis. tahun 4). Tapi tanggal jauh di masa depan itu **valid** (jadwal terjadwal) — hanya 1 kasus bertanggal 2027.

---

## H. Petugas & surat

**Aturan #18 — `bridge_pemeriksaan_petugas` & `no_surat`/`tgl_surat` sudah diambil dari detail TERBARU per kasus.**
Satu kasus bisa punya lebih dari satu surat tugas akibat revisi; yang tersimpan di `staging` adalah baris dengan `updated_at` terbaru. Jadi hitung petugas dari tabel ini (bukan dari catatan surat), dan jangan berharap menemukan surat versi lama.

---

## I. Kebersihan isi temuan

**Aturan #21 — `bridge_pemeriksaan_temuan` sudah dibersihkan (21 Sep 2026), tapi TIDAK agresif.** Cek konteks sebelum menganggap nilai besar sebagai error.

| Aspek | Sebelum | Sekarang (verifikasi 22 Sep) |
|---|---|---|
| Baris | 304.687 | **303.521** |
| `jumlah_temuan` minimum | −196 | **1** |
| Maksimum | 20.221.092.024 | **7.700.000** |
| Nilai negatif | 137 | **0** |
| Duplikat same-moment | 1.166 dihapus | — |

- Outlier ekstrem (20,2 miliar — 99,86% dari total) dan 137 nilai negatif di-NULL-kan (927 baris `jumlah_temuan` NULL).
- Nilai besar lain (100 ribu – 7,7 juta) **sengaja dibiarkan**: semuanya aritmatika-konsisten (`harga_total = harga × jumlah_temuan` persis) dan sebagian punya justifikasi di `keterangan`. **Jangan pakai ambang angka murni untuk menyatakan error** — cek `keterangan` dulu.
- Duplikat dengan konten identik tapi `created_at` **berbeda** sengaja dibiarkan (kemungkinan temuan sama ditemukan lagi di kunjungan berikutnya). Jangan dedup hanya berdasar kesamaan konten.

---

## J. Aturan praktis menulis query (ringkasan cepat)

1. **Tentukan dulu tingkat hitungannya.** "Berapa pemeriksaan" (259.348) ≠ "berapa penugasan petugas" (553.380).
2. **Cek `flag_varian_datas` sebelum menyentuh checklist.**
3. **Selalu sebut `type`** saat join `dim_master_data` — kecuali 3 kolom multi-kamus di Pola 4.
4. **Cast `::text`** untuk `observasi_kode`, `komoditi_kode`, `fokus_kode`, dan semua elemen array.
5. **Filter data uji dan draft** kalau mau angka final: `is_data_uji IS NOT TRUE`, `is_kasus_draft = false`.
6. **Pakai `COALESCE` untuk label aspek** — kalau tidak, Penerimaan & Pengembalian (volume terbesar ke-2 dan ke-4) hilang dari hasil.
7. **Jangan pakai `sum(jumlah_temuan)` mentah** — nilai besar yang sah tetap ikut terjumlah; pakai median atau batasi nilainya.
8. **Pakai `regional_name`, jangan `regional`** — kode regional tidak konsisten (kode 3 dipakai 2 nama berbeda).
9. **Batasi baris checklist** kalau menampilkan per kasus — bisa ratusan baris per kasus.

---

## Angka baseline yang sering dipakai

| Item | Nilai |
|---|---:|
| Kasus pemeriksaan (aktif) | 259.348 |
| Kasus data uji | 72 (29 NULL) |
| Baris temuan draft | 6.464 |
| `dim_sarana` (termasuk soft-delete) | 441.821 |
| `dim_master_data` (termasuk soft-delete) | 1.999 |
| Grade terisi | 44.400 (A 24.777 · B 9.819 · C 9.739 · N/A 65) |
| Kasus tanpa `tgl_start` | 963 |
