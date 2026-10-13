# Alur Entri Pemeriksaan Sarana — Dokumentasi Lengkap per Flow, dengan Kondisi Database

> **Tujuan**: dokumentasi alur entri **Pemeriksaan Sarana** SIPT 3.0 yang **lengkap dan berurutan per flow** — dari Entri Baru sampai Direktur — di mana setiap langkah dilengkapi **kondisi database**: isian itu disimpan di tabel/kolom apa, dan seperti apa isi nyatanya di `sipt_sync` (10.59.2.29:5432, verifikasi 16 Sep 2026).
>
> Sumber: KB resmi (buku pemeriksaan-sarana-d34: halaman "Alur Pemeriksaan Sarana" + "Operator - Pemeriksaan Sarana Rutin"), PDF `Panduan_Penggunaan_Aplikasi_SIPT_2025.pdf` BAB III hal. 9–34, aplikasi dev `sipt.pom.go.id/dev/entri/pemeriksaan*`, dan query langsung ke `sipt_sync`. 27 screenshot asli form tersimpan di `kb_pelayanan/`.
>
> Untuk kebutuhan analitik (Q1–Q9), lihat dokumen terpisah: [pertanyaan-analitik.md](pertanyaan-analitik.md). Dokumen ini murni alur + arah data.

---

## FLOW 1 — Entri Baru Data Pemeriksaan Sarana

**Langkah user**: Login Operator → menu **Entri** → submenu **Pemeriksaan Sarana** → **Entri Baru** → halaman "Tambah Baru Pemeriksaan Sarana".

### 1.1 Form Tambah Baru (satu halaman, sebelum wizard)

| Urutan | Field (tampil di form) | Sifat | Diisi bagaimana |
|---|---|---|---|
| 1 | Jenis Sarana `*` | dropdown master | memilih 1 dari ±32 jenis (Apotek, PBF, Pangan, PKM, Klinik, Toko Obat, Sarana Produksi Obat, OT, Kosmetik, …) |
| 2 | Jenis Komoditi `*` | dropdown master | Obat, OT, Suplemen, Kosmetik, Produk Pangan, Bahan Berbahaya, … |
| 3 | Versi Formulir Pemeriksaan | dropdown (opsional) | versi 1–10 |
| 4 | Provinsi, Kabupaten/Kota | dropdown berantai | mengikuti lokasi sarana |
| 5 | Nama Sarana `*` | **search master** (ketik → pilih; "Apabila Nama Sarana tidak tersedia, silahkan cek data master") | 1 dari master fasilitas |
| 6 | Nomor Surat Tugas `*` | free text | format resmi `PW.02.02.31B.08.26.1402` (banyak juga nilai bebas) |
| 7 | Tanggal Surat Tugas `*` | date | — |
| 8 | Unit / Balai Besar / Balai / Loka `*` | dropdown (±60 unit: BB POM per kota, Loka POM per kabupaten, direktorat pusat, Balai Pengujian) | bisa multi |
| 9 | Petugas `*` | **multi-select chip** (1–5 pemeriksa) | — |

Tombol **Proses** (+ popup konfirmasi Ya) → masuk wizard.

### 1.2 Kondisi database setelah FLOW 1

Dua baris langsung lahir:

- **`trx_pemeriksaan`** (header) — 290.203 baris total, **259.348 aktif**.
- **`trx_pemeriksaan_detail`** (surat tugas) — 307.482 baris, terhubung `pemeriksaan_id`.

Contoh nyata (kasus **id 291155**, status `DRAFT`):

| Kolom | Nilai nyata |
|---|---|
| `trx_pemeriksaan.jenis_id` | `15` (→ master: jenis sarana; top sebaran: Pangan 61.831 · Kosmetik 36.999 · **Apotek 27.696** · Pangan MD 26.521 · PKM 19.860 · OT 17.260 · Klinik 10.258 · PBF 6.934) |
| `klasifikasi_id` | `464` (Obat/OT/… per kamus; sebaran: Pangan 107.780 · Obat 83.444 · Kosmetik 39.609 · OT 20.282) |
| `form_version_id` | **kosong** — hanya 29% kasus yang mengisi (v9 30.342 · v10 13.407 · v4 12.043 …) |
| `tgl_start/tgl_end` | `2026-08-20` (⚠️ ada ±15 baris ekstrem 1922–2028) |
| `entri_balai_id` | `29` (BB POM Bandung → `ms_balai.regional_name` = "Semarang/Medan/Surabaya/…" terisi 99,6%) |
| `detail.nomorsurat` | `PW.02.02.31B.08.26.1402` — **100% terisi** |
| `detail.tgl_surat` | `2026-08-14` — **100% terisi** |
| `detail.balai_id` | `["29"]` — **array JSON string** |
| `detail.petugas_id` | `["2018","7732","493"]` — array 1–5; sebaran: 2 petugas 236.777 kasus · 3 petugas 31.091 · 1 · 4 · 5 |

> Jebakan teknis: `balai_id`/`petugas_id` adalah **string JSON array**, bukan angka — join wajib di-parse dulu.

---

## FLOW 2 — Pemeriksaan Sarana (Sesuai Jenis Sarana) — wizard 2 langkah

**Langkah user** (dari draft, menu aksi → *Edit Data Pemeriksaan* / lanjut setelah Entri Baru):

**Langkah 1 — Informasi Umum Sarana**: terisi **otomatis dari Master Sarana** (nama, alamat, NIE/sipa, pemilik, masa berlaku). KB menegaskan: perubahan di sini *hanya data transaksi*, tidak mengubah master.

**Langkah 2 — Informasi Pemeriksaan**:

| Field | Keterangan | Ke database |
|---|---|---|
| Tanggal Pemeriksaan | range (mulai–selesai) | `trx_pemeriksaan.tgl_start/tgl_end` |
| Tujuan Pemeriksaan | dropdown: **Pemeriksaan Rutin** / Kasus | `tujuan_id` (kamus `TUJUAN_PEMERIKSAAN`) |
| **Popup "Apakah ada kasus?"** | **YA** → wajib isi form temuan produk; **TIDAK** → lanjut tanpa temuan | menentukan ada-tidaknya baris di `trx_pemeriksaan_temuan` |
| Bertemu Dengan, Metode Inspeksi, Nomor Inspeksi, Referensi | kontekstual | `metode_inspeksi` (kamus: **On-site inspection 4.009 · Remote 54 · Hybrid 38** — hanya 1,6% kasus yang mengisi); sisanya masuk `datas` |
| Informasi Petugas Pemeriksa (rekap) | read-only | dari `trx_pemeriksaan_detail` |

Proses → konfirmasi Ya.

---

## FLOW 3 — Inspeksi Pemeriksaan Sarana (wizard 8 langkah — satu langkah per aspek)

> Varian **Sarana Pelayanan** (Apotek, PBF, Toko Obat, Klinik, PKM, dll). Varian Produksi beda — lihat FLOW 3B.

| Langkah | Tab/section di layar | Yang diisi petugas | Ke database (`datas`, section `tx_*`) |
|---|---|---|---|
| 1 | Informasi (rekap) | read-only: info umum + pemeriksaan + petugas | — (sudah di header/detail) |
| 2 | **Pengadaan** | pertanyaan per item + **aturan kondisional**: jawab "Sebagian Besar/Sebagian Kecil/Tidak" pada pengadaan obat → wajib sebutkan **sumber pengadaan** & **pihak pengadaan**; kaitan produk ilegal | `tx_pengadaan_obat/_drugs/_apj/_arsip` |
| 3 | **Penerimaan** | pertanyaan per item | `tx_penerimaan_obat/_param` |
| 4 | **Penyimpanan** | pertanyaan per item | `tx_penyimpanan_obat/_drugs/_ccp/_psiko/_rusak/_investigasi/_opname_*` |
| 5 | **Pendistribusian** | pertanyaan per item | `tx_distribusi` |
| 6 | **Penyerahan** | pertanyaan per item (termasuk antibiotik tanpa resep, KIE) | `tx_penyerahan_*` (±14 varian section) |
| 7 | **Pengembalian, Pencatatan dan Pelaporan** | pertanyaan per item (retur, SIPNAP, mutasi) | `tx_pengembalian_mutasi/_retur/_sipnap`, `tx_pencatatan_mutasi_antibiotika` |
| 8 | **Pemusnahan** | pertanyaan per item | `tx_pemusnahan_obat/_drugs` |

Tiap langkah ditutup tombol **Selanjutnya**; langkah terakhir **Proses** + konfirmasi Ya.

### Kondisi database per langkah — bentuk isian nyata

Setiap section punya pola nilai yang sama — **pertanyaan berkode Inggris + skor** (contoh nyata section `tx_pengadaan_obat` Apotek, 500 kasus terakhir):

| Key | Nilai yang muncul | Arti |
|---|---|---|
| `opsi` | `"yes"` 410 · `"mostly"` 46 · `"rarely"` 11 · `"no"` 10 · `"illegal"` 3 | padanan layar: Sesuai ("Ya") / Sebagian Besar / Sebagian Kecil / **Tidak** / **Ilegal** |
| `n` | 300 / 150 / 75 / 0 | skor mentah (n = 3× skor) |
| `fp` | `3` | faktor pembobot |
| `score` | **100 / 50 / 25 / 0** | skor akhir per item (yes=100, mostly=50, rarely=25, no/illegal=0) |
| `other` | `{"apotek":"on"}` 58 · `{"pm":"on"}` · `{"to":"on"}` | sub-jenis sarana yang diperiksa (apotek/praktik mandiri/toko obat) |

Contoh section `tx_penyimpanan_obat` (kasus nyata id 291156): `wadah:"on", bentuk:"on", sentuh:"on", sistem:"on", jaminan:"on", kondisi:"on", kontaminasi:"on", n:"262.50", fp:"3", score:"262.5"`.

Kondisi volume: dari 27.528 datas Apotek aktif, **27.387 (99,5%) tersimpan terstruktur seperti ini**; sisanya **141 kasus berupa paste dokumen Word mentah** (HTML `MsoNormal`, satu section pernah 264.736 karakter) — isian naratif murni. Secara lintas jenis: 6.731 datas (dari 247.244) mengandung paste HTML.

> Varian lama/non-pelayanan memakai key berbeda (`administrasi`, `gudang`, `sanitasi`, item `a1..aN`, `l1..l4`) — 77.862 datas memuat pola `{"aspect":"Ya/Tidak","note":"…"}`. Contoh potongan mentah nyata:
> `administrasi.distribusi.a1 = {"aspect":"Ya","note":"izin usaha"}` · `a2 = {"aspect":"Ya","note":"memiliki faktur"}` · `a3 = {"aspect":"Ya","note":"tidak mengeluarkan bon penjualan"}` · `a4 = {"aspect":"Tidak","note":"tidak ada pencatatan"}` · `penyimpanan.gudang.a1..a3 (note null), a3.p1 (sub-item bersarang)`.
>
> **Konsekuensi**: satu kolom `datas`, banyak skema — akses programatik wajib unescape 2× `(datas::jsonb #>> '{}')::jsonb` dan routing per jenis sarana.

## FLOW 3B — Inspeksi varian Sarana Produksi (PDF BAB III; Sarana Produksi Obat/OT/Kosmetik/Pangan)

| Langkah | Isi | Ke database |
|---|---|---|
| 1 Pemeriksaan (info) | rekap info + petugas | header/detail |
| 2 **Observasi** | SEMUA aspek dalam 1 langkah: kolom hasil per klausul + catatan + **upload PDF ≤5MB** (BAP, Agenda Inspeksi, Daftar Dokumen, Rencana Inspeksi, …) | `datas` section per aspek, item `a1..aN` `{"aspect":"Ya/Tidak","note"}`; file = ID di `datas.*.file` (kolom `attachment` header 0 semua) |
| 3 **Daftar Temuan** | counter **Temuan Gross / Major / Minor** + Rekomendasi + Kesimpulan | counter → `result.hp_level {major, minor, critical, conclusion}` (terisi ±9 rb+ — hanya form ini); rekomendasi/kesimpulan → `datas`/`result` |
| 4 **Tingkat Pemenuhan CPOB** | dropdown Tingkat Pemenuhan + Tindak Lanjut Hasil Inspeksi + Kriteria | `datas` section cpob (1.186) + `result.hp_pemenuhan` (870) |

## FLOW 4 — Hasil Inspeksi + Melengkapi Surat Tindak Lanjut

**Langkah user** (setelah Proses inspeksi): wizard Hasil Inspeksi 3 langkah:
1. *Info Pemeriksaan* — boleh ubah tanggal.
2. *Temuan Produk* — tombol **Tambah** per produk bermasalah (boleh dilewati jika tidak ada).
3. *Kesimpulan dan Tindak Lanjut* — form: **Hasil Kesimpulan, Hasil Temuan, Catatan Hasil Pemeriksaan, Tindak Lanjut, Detil Tindak Lanjut, Upload Surat TL, Upload Berita Acara** (PDF maks 5MB) → **Simpan** + Ya.

Pembuatan surat TL juga bisa lewat draft (rujuk panduan CAPA).

**Kondisi database** — semuanya di kolom JSON `result` (stabil, terisi 99,2% kasus):

| Key | Field form | Kondisi & contoh isi nyata |
|---|---|---|
| `hp_kesimpulan` | Hasil Kesimpulan | 262.182 (89%) — nilai unik teramati: **`MK`** (Memenuhi, 1.931 dari sampel) · **`TMK`** (1.038) · **`TTP`** 20 · **`TDP`** 9 · teks bebas seperti *"tidak ada temuan produk"*, *"Tidak ditemukan produk kosmetik TIE, rusak dan kadaluarsa"* |
| `hp_hasil` | Hasil Temuan | ±16 rb — teks bebas |
| `hp_grade` | Grade (produksi) | **A** 24.777 · **B** 9.819 · **C** 9.739 (C = hanya TMK) |
| `hp_level` | counter temuan (produksi) | `{major, minor, critical, conclusion}` |
| `hp_catatan` | Catatan Hasil Pemeriksaan | 246.734 — contoh: *"Tidak ditemukan pada pajangan kosmetik Tanpa Izin Edar (TIE), rusak dan Kedaluarsa"* |
| `tl_detil` | Detil Tindak Lanjut | 196.361 — contoh: `Pembinaan`, `Pembinaan Teknis` |
| `tl_saran` | Saran TL | 171.549 |
| `tl_ba` | Upload Berita Acara | 163.244 (file ID) |
| `tl_attachment` | Upload Surat TL | 165.066 (file ID) — kolom `attachment` header kosong semua, file hidup di sini |
| `tl_capa` | CAPA (via modul Tindak Lanjut) | 62.097 |
| `tl_ba_pusat`, `tl_attachment_pusat`, `hp_catatan_pusat` | versi pusat | 68.774 / 66.074 / 68.774 |

## FLOW 5 — Edit Data Pemeriksaan Sarana

**Langkah user**: halaman **Draft Pemeriksaan** → centang data → ikon aksi → **Edit Data Pemeriksaan** → wizard terbuka pada langkah terakhir → ubah → **Proses**. Menu aksi lain di draft: *Edit Data Sarana* (mengubah data master sarana dari draft!), *Aksi Telaah Ulang*, *Data Temuan Produk*, *Proses Data Pemeriksaan*, *Cetak Inspeksi*.

**Kondisi database**: edit = update baris yang sama (`trx_pemeriksaan`, `datas`, `result`); tidak ada versioning — nilai lama tertimpa. `updated_at/updated_by` berubah. Kasus yang dikembalikan verifikator muncul sebagai `status = DRAFT_REVISE` (**5.108 kasus**).

## FLOW 6 — Kirim Data

**Langkah user**: halaman **Draft Pemeriksaan** → centang → ikon aksi → **Kirim Data** → popup konfirmasi Ya. Sebelum kirim ada form **Disposisi ke: "Supervisor - Verifikasi"** + **Komentar**.

**Kondisi database**: dua kejadian sekaligus —
1. `trx_pemeriksaan.status` berubah `DRAFT` → `VERIFY1`.
2. Satu baris baru di **`trx_pemeriksaan_approval`** (1.352.827 event total): contoh nyata kasus 291155 → `act_steps=DRAFT, to_steps=step_verify1, notes="Entri Draft Pemeriksaan Sarana Obat Trad…"`, `created_at=2026-09-14 08:31`.

## FLOW 7 — Verifikasi berjenjang (3.2 Supervisor → 3.3 Kepala Balai/Loka → 3.4 Operator Pusat → 3.5 Supervisor Pusat → 3.6 Direktur)

| Tingkat | Menu di aplikasi | Yang dilakukan & diisi | Ke database |
|---|---|---|---|
| **3.2 Supervisor Balai** | Entri > Pemeriksaan Sarana > **Diterima Supervisor** | filter (jenis sarana/komoditi/tujuan) → pilih data → **Proses Data Pemeriksaan** → lengkapi Langkah 4: *Hasil Kesimpulan, Tindak Lanjut, Hasil Temuan, Detil TL, Catatan Hasil Pemeriksaan, File BA* → Langkah 5 disposisi: **Kepala Balai** atau **Revisi ke Operator** + **Komentar Pemeriksaan** + **Komentar Surat Tindak Lanjut** | hasil → `result.hp_*/tl_*`; komentar → `approval.notes` & **`notes_tl`**; status → `VERIFY2`; revisi → `DRAFT_REVISE` |
| **3.3 Kepala Balai / Loka** | **Diterima Kepala Balai** | ceklist → **Generate TTE** (bisa multiple; popup "Perizinan*", checkbox pernyataan) → data dapat label **"Selesai TTE"** → **Download Surat Tindak Lanjut** → Proses → disposisi **Operator Pusat** + komentar | status → `VERIFY3`; komentar → `notes`; ⚠️ **TTE tidak tersimpan sebagai data** — hanya status dokumen di daftar |
| **3.4 Operator Pusat** | **Diterima Operator Pusat** | filter (balai, jenis sarana, komoditi, tujuan) → ceklist → Proses → **Justifikasi Pusat** (Langkah 5: Hasil Kesimpulan, Saran TL, Hasil Temuan, Detil TL, Catatan, File BA) → disposisi **Supervisor Pusat** + komentar | → `result.hp_kesimpulan_pusat/hp_hasil_pusat/tl_detil_pusat/tl_ba_pusat/tl_attachment_pusat/hp_catatan_pusat` (68.774 kasus versi pusat); status → `VERIFY4` |
| **3.5 Supervisor Pusat** | **Diterima Supervisor Pusat** | verifikasi → disposisi **Direktur** + komentar | status → `VERIFY5`; komentar → `notes` |
| **3.6 Direktur** | **Diterima Direktur** | verifikasi → pilih **Selesai** (+ Revisi ke Operator bila koreksi) | status → **`FINISHED`** (29.042) / `FINISHED_PUSAT` (113) |

**Kondisi database alur verifikasi** (angka nyata):

- Status kasus aktif: `VERIFY4` **167.116 (64% — bottleneck di Operator Pusat)** · VERIFY5 46.619 · FINISHED 29.042 · DRAFT_REVISE 5.108 · VERIFY7 4.784 · DRAFT 3.297 · VERIFY6 1.008 · VERIFY1 640 · VERIFY2 619 · DRAFT_PUSAT 464 · VERIFY_P1 351 · FINISHED_PUSAT 113.
- Log `to_steps` (disposisi): `step_verify2` 333.448 · `step_verify1` 288.774 · `step_verify3` 259.070 · `step_verify4` 255.730 · `step_verify5` 82.927 · `draft_revise` 39.529 · `step_verify7` 34.818 · `finished` 29.598 · `step_verify6` 26.614 · `step_verify_p1` 1.420 · p2 571 · p3 142 · `finished_pusat` 113 · `draft_pusat_revise` 44.
- Isi `notes` yang nyata (top frekuensi): *"Verifikasi Supervisor Pemdik Satu"* 102.708 · *"Verifikasi Supervisor Pemdik Dua"* 23.586 · *"Verifikasi Supervisor Pemdik Satu Tipe-A Tipe-B Loka"* 18.908 · *"Ditolak Supervisor Pemdik Satu"* 6.161 · *"Mohon koreksi, terima kasih"* 2.936 — dari sini label role verifikator (Pemdik Satu/Dua) mulai terbaca, walau pemetaan resmi `VERIFY1..7`→role belum ada di database.
- Wujud di aplikasi dev (user operator): bucket **Draft 294** baris · **Terkirim 10.197** (kolom Hasil Balai + Hasil Pusat) · **Ditolak 31** · **Selesai 0** (kasus selesai keluar dari bucket operator).

---

### Lampiran: peta cepat flow → tabel

| Flow | Tabel yang tertulis |
|---|---|
| Entri Baru | `trx_pemeriksaan` + `trx_pemeriksaan_detail` |
| Wizard pemeriksaan & inspeksi (semua langkah) | `trx_pemeriksaan.datas` (JSON) |
| Temuan produk | `trx_pemeriksaan_temuan` (→ `ms_product`) |
| Hasil inspeksi, kesimpulan, TL, CAPA | `trx_pemeriksaan.result` (JSON) |
| Kirim/verifikasi/revisi | `trx_pemeriksaan.status` + `trx_pemeriksaan_approval` |
| Kamus dropdown | `ms_master_data`, `ms_balai`, `ms_product` |

*Angka & contoh nilai = hasil query `sipt_sync` 16 Sep 2026. Detail per kolom: [pemetaan-form-ke-database.md](pemetaan-form-ke-database.md); kamus kondisi penuh: [../ERD/02-katalog-tabel.md](../ERD/02-katalog-tabel.md).*
