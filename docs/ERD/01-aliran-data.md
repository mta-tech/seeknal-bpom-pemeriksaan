# 01 — Dari Entri User ke Kondisi Data di `staging`

> File ini memetakan: **petugas mengisi apa di aplikasi → mendarat di tabel/kolom mana di `staging` → isinya apa → untuk insight apa**.
>
> Semua angka di bawah adalah kondisi nyata `staging` per **22 Sep 2026**. Tidak ada penjelasan alur sistem di luar `staging`.

---

## 1. Tujuh flow entri, dan jejaknya di `staging`

| Flow | Yang dilakukan user | Jejak utama di `staging` |
|---|---|---|
| 1 | Entri Baru (jenis sarana, komoditi, sarana, surat tugas, balai, petugas) | `fact_pemeriksaan` + `bridge_pemeriksaan_petugas` |
| 2 | Wizard informasi pemeriksaan (tanggal, tujuan, ada kasus?, metode) | `fact_pemeriksaan` |
| 3 | Inspeksi varian pelayanan (8 langkah, satu per aspek) | `bridge_pemeriksaan_skor_operasional` |
| 3B | Inspeksi varian produksi (klausul Ya/Tidak) | `bridge_pemeriksaan_checklist` (+ `_temuan_observasi`, `_vaksin`, `_narasi_faskes`) |
| 4 | Hasil inspeksi, temuan produk, kesimpulan, tindak lanjut | `fact_pemeriksaan` + `bridge_pemeriksaan_temuan` + `fact_pemeriksaan_narasi` |
| 5 | Edit (menimpa nilai lama) | `fact_pemeriksaan.updated_at` |
| 6–7 | Kirim & verifikasi berjenjang 6 tingkat | `fact_pemeriksaan.status_id` + `fact_pemeriksaan_approval` |

Satu catatan struktural yang penting: **JSON mentah isian form tidak disimpan di `staging`**. Yang ada hanyalah hasil pecahannya di tabel bridge, ditambah satu kolom jsonb cadangan (`fact_pemeriksaan.profil_sarana_json`, terisi 71,9%). Jadi semuanya harus dibaca dari tabel yang sudah tertata, bukan dengan membedah JSON.

---

## 2. FLOW 1 — Entri Baru

| Yang diisi user | Mendarat di | Isi | Insight |
|---|---|---|---|
| Jenis sarana | `fact_pemeriksaan.jenis_id` → `dim_master_data` (`JENIS_SARANA`) | 25 jenis terpakai dari 32 kode kamus | dasar pemecahan **Sardis/Saryan** (golongan `Produksi`/`Distribusi`/`Pelayanan`) |
| Jenis komoditi | `klasifikasi_id` → `JENIS_KLASIFIKASI` | 15 kode | profil komoditi yang diawasi |
| Versi formulir | `form_version_id` | ⚠️ terisi 29,4% | tidak bisa diandalkan untuk routing |
| Nama sarana | `sarana_id` → `dim_sarana` | 441.821 sarana | siapa yang diperiksa; wilayah & identitas legal |
| Nomor & tanggal surat tugas | `no_surat` / `tgl_surat` | 100% terisi | penelusuran dokumen; sudah diambil dari surat tugas terbaru per kasus (Aturan #18) |
| Unit/balai | `balai_id` → `dim_balai` | 108 balai, 8 regional | dasar **breakdown regional** |
| Petugas 1–5 orang | `bridge_pemeriksaan_petugas` | 553.380 baris, 2.975 inspektur | beban & komposisi tim inspektur |

Kondisi tim: **2 petugas = 204.171 kasus** · 1 orang 17.173 · 3 orang 26.455 · 4 orang 9.809 · 5 orang 1.285 · 6–12 orang 421. Jadi "jumlah pemeriksaan" dan "jumlah penugasan" adalah dua angka berbeda.

## 3. FLOW 2 — Wizard informasi pemeriksaan

| Yang diisi user | Mendarat di | Kondisi di `staging` |
|---|---|---|
| Tanggal mulai–selesai | `tgl_start` / `tgl_end` | 99,6% terisi (963 kasus kosong) |
| Tujuan (Rutin/Kasus) | `tujuan_id` | 99,6% terisi |
| Popup "Apakah ada kasus?" | menentukan ada/tidaknya baris di `bridge_pemeriksaan_temuan` | 31.959 kasus punya temuan |
| Metode inspeksi | `metode_inspeksi` | ⚠️ **1,6%** (4.101 kasus) — terlalu tipis untuk dianalisis |

## 4. FLOW 3 — Inspeksi varian pelayanan (per aspek)

| Yang diisi user | Mendarat di | Isi | Insight |
|---|---|---|---|
| Jawaban per item: Ya / Sebagian Besar / Sebagian Kecil / Tidak / Ilegal + skor | `bridge_pemeriksaan_skor_operasional` | 1.521.315 baris untuk 63.851 kasus; kolom `opsi`, `n`, `fp`, `score` | **kepatuhan per aspek** |
| Aspeknya sendiri | `area_key` → `dim_pemeriksaan_aspek` | 47 `area_key`, join 100% kena | satu-satunya jalur dengan label aspek resmi |
| Rekap skor kasus | `datas.tx_total_n` / `tx_total_fp` | angka per kasus | skor total |

Cakupan: Apotek 26.611 · PKM 13.122 · Klinik 9.991 · Toko Obat 6.765 · IFRS Swasta 4.040 · IFRS Pemerintah 3.322.

⚠️ Dua jebakan yang sudah terbukti di data:
- `opsi` **tidak selalu** yes/no — bisa berisi jabatan (`apoteker`, `ttk`), nama pihak, atau JSON-string (`{"mutasi":"mostly"}`). Memakai `opsi='no'` sebagai penanda temuan membuat sebagian aspek otomatis bernilai 0.
- `score` mencampur skala item (0/25/50/75/100) dengan nilai akumulasi (>100). Nilai >100 muncul di Penyimpanan 116.978 baris, Penyerahan 63.700, Penerimaan 49.261, Pemusnahan 10.523.

## 5. FLOW 3B — Inspeksi varian produksi (klausul)

| Yang diisi user | Mendarat di | Isi | Insight |
|---|---|---|---|
| Klausul bernomor (`a1`, `a2`, …) dengan jawaban & catatan | `bridge_pemeriksaan_checklist` | 7.388.165 baris; `path`, `nilai_aspek`, `catatan` | **cacah klausul tidak sesuai**; severity untuk sebagian jenis |
| Observasi GMP | `bridge_pemeriksaan_temuan_observasi` | 27.418 baris; `observasi_kode` (kamus baku) + `kriteria` (angka 1–4) | temuan per kode observasi |
| Form vaksin (19 section) | `bridge_pemeriksaan_vaksin` | 145.540 baris / 7.660 kasus; `opsi` 88% · `perbaikan` 84% · `observasi` 70% · `jumlah` 10% | kepatuhan program vaksin |
| Form naratif (8 section) | `bridge_pemeriksaan_narasi_faskes` | 6.930 baris / 1.182 kasus | narasi inspektur — bahan analisis teks, bukan cacah |
| Profil faskes & personel | `fact_pemeriksaan_profil_faskes`, `bridge_pemeriksaan_personel_faskes` | 72.890 & 131.898 baris | kapasitas sarana & komposisi tenaga |
| Profil pabrik Pangan MD + sertifikat | `fact_pemeriksaan_profil_pangan_md`, `bridge_pemeriksaan_sertifikat_pangan_md` | 26.281 & 23.404 baris | skala usaha, kapasitas, sertifikasi |

Nilai `nilai_aspek` **berbeda arti per varian** — kolom yang sama memuat konformitas (OK / Tidak Berlaku), grade (B / T / C / K), dan severity (Minor / Major / Kritis / Serius / Kritikal). Rinciannya di [04-routing-bridge.md](04-routing-bridge.md) §6.

## 6. FLOW 4 — Hasil inspeksi & tindak lanjut

| Yang diisi user | Mendarat di | Kondisi di `staging` | Insight |
|---|---|---|---|
| Kesimpulan kasus | `kesimpulan_balai_id` → `dim_pemeriksaan_kesimpulan` | MK 177.944 · TMK 76.090 · TTP 1.557 · TDP 794 · kosong 2.299 | vonis sarana |
| Grade (produksi) | `grade` | 44.400 terisi (A 24.777 · B 9.819 · C 9.739 · N/A 65) | kualitas sarana produksi |
| Counter kekritisan | `kritis_count` / `major_count` / `minor_count` / `level_kesimpulan` | 10.736 / 9.064 kasus | kekritisan temuan per kasus |
| Tingkat pemenuhan CPOB | `kesimpulan_balai_id` id 791–794 | 646 kasus (Memuaskan 76 · Baik 345 · Cukup 118 · Kurang 107) | khusus Sarana Produksi Obat |
| Daftar temuan produk | `bridge_pemeriksaan_temuan` | 303.521 baris · 31.959 kasus · 6.464 baris draft | **temuan produk terbanyak**, nilai sitaan |
| Catatan, hasil, TL, rekomendasi | `fact_pemeriksaan_narasi` | 525.894 baris, 9 jenis | analisis kualitatif |
| CAPA | `tl_capa` | 19.299 (7,4%) — teks bebas, tidak terkamusk | tindak lanjut korektif |
| Lampiran | `tl_attachment` (29,3%) · `tl_ba` (38,2%) | hanya **ID** dokumen, bukan isi file | jejak dokumen |

## 7. FLOW 5–7 — Edit, kirim, verifikasi berjenjang

Edit menimpa nilai lama — **tidak ada riwayat perubahan**. Jejak waktu hanya `updated_at`/`updated_by`, terisi di **seluruh 259.348 kasus** dan bergerak sampai 2026-09-14.

Kondisi alur verifikasi adalah temuan operasional terbesar di domain ini:

| Status | Kasus | Porsi | Arti |
|---|---:|---:|---|
| VERIFY4 | 167.116 | 64,4% | **macet di Operator Pusat** |
| VERIFY5 | 46.619 | 18,0% | di Supervisor Pusat |
| FINISHED | 29.042 | 11,2% | selesai |
| DRAFT_REVISE | 5.108 | 2,0% | dikembalikan |
| VERIFY7 | 4.784 | 1,8% | |
| DRAFT | 3.297 | 1,3% | belum dikirim |
| sisanya (VERIFY6 · VERIFY1 · VERIFY2 · jalur Pusat · NULL) | 3.382 | 1,3% | |

Hampir dua dari tiga kasus berhenti di satu titik, dan hanya 11,2% selesai. Ini bukan masalah data, tapi masalah alur kerja.

---

## 8. Kondisi keterisian kolom `fact_pemeriksaan` (259.348 kasus)

Diurutkan dari yang paling kosong — berguna untuk tahu kolom mana yang jangan diandalkan:

| Kolom | Terisi | Porsi |
|---|---:|---:|
| `tl_ba_pusat` | 105 | 0,04% |
| `tl_attachment_pusat` | 141 | 0,05% |
| `sediaan_kode` | 860 | 0,3% |
| `unit_id` | 1.529 | 0,6% |
| `penelusuran_id` | 1.931 | 0,7% |
| `kasus_id` | 1.946 | 0,8% |
| `vaksin_kesimpulan_id` | 1.979 | 0,8% |
| `vaksin_bersama_rutin` | 2.045 | 0,8% |
| `metode_inspeksi` | 4.101 | 1,6% |
| `vaksin_status_capa` | 7.660 | 3,0% |
| `minor_count` / `level_kesimpulan` / `kritis_count` / `major_count` | 9.017 / 9.064 / 10.081 / 10.913 | 3,5–4,2% |
| `tl_capa` | 19.299 | 7,4% |
| `grade` | 44.400 | 17,1% |
| `jenis_pangan_kode` | 48.729 | 18,8% |
| `tl_saran_pusat` | 55.575 | 21,4% |
| `klasifikasi_sarana_kode` | 61.669 | 23,8% |
| `kesimpulan_pusat_id` | 63.748 | 24,6% |
| `tl_attachment` / `form_version_id` | 76.018 / 76.273 | 29,3–29,4% |
| `status_ss` | 84.020 | 32,4% |
| `tl_ba` | 99.018 | 38,2% |
| `profil_sarana_json` | 186.372 | 71,9% |
| `tl_saran` | 215.398 | 83,1% |
| `kesimpulan_balai_id` | 257.049 | 99,1% |
| `tgl_start` / `tgl_end` / `tujuan_id` | 258.385 / 258.390 / 258.401 | 99,6% |
| `id` · `sarana_id` · `balai_id` · `jenis_id` · `klasifikasi_id` · `created_at` · `created_by` · `flag_varian_datas` · `updated_at` · `updated_by` | 259.348 | 100% |

---

## 9. Rantai lengkap satu kasus (contoh id 287342)

| Tabel | Baris | Isi |
|---|---:|---|
| `fact_pemeriksaan` | 1 | flag `clusterC_skor` |
| `bridge_pemeriksaan_petugas` | 2 | Apoteker (urutan 1) + TTK (urutan 2) |
| `bridge_pemeriksaan_skor_operasional` | 22 | nilai per aspek |
| `bridge_pemeriksaan_checklist` | 0 | memang bukan varian checklist |
| `bridge_pemeriksaan_temuan` | 0 | tidak ada temuan produk |
| `fact_pemeriksaan_approval` | 5 | jejak disposisi |
| `fact_pemeriksaan_narasi` | 6 | catatan & hasil |

Query "cek semua bridge satu kasus" ada di [04-routing-bridge.md](04-routing-bridge.md) §5.

---

## 10. Yang tidak tersedia di `staging` (jangan dicari)

| Apa | Kondisi |
|---|---|
| JSON mentah isian form (`datas`) | tidak disimpan — hanya hasil pecahannya di bridge. Contoh bentuk aslinya ada di [08-contoh-datas.md](08-contoh-datas.md) |
| Isi file lampiran | hanya ID dokumen (`tl_attachment`, `tl_ba`) |
| Status TTE | tidak ada kolomnya |
| Riwayat perubahan kasus | tidak ada versioning |
| Detail checklist untuk Kosmetik CPKB (`jenis_id`=7, 2.610 kasus) dan `lainnya` (14 kasus) | tidak ada tabel bridge-nya |
| Kekritisan per klausul untuk Kosmetik / Obat Tradisional / Suplemen | tidak ada satu pun item ber-severity |
| Metode remote vs on-site untuk 98,4% kasus | terisi 1,6% saja |
| Status label kasus (mis. "macet di Operator Pusat") | `dim_status_code.status_label` kosong untuk seluruh 35 baris |
