# 10 — Blueprint User: NPPZA, Ekspor-Impor & Pengawasan Keamanan Mutu

> Blueprint kebutuhan informasi untuk topik **Pengawasan Keamanan Mutu** dan **Ekspor Impor Obat, Narkotika, Psikotropika, Prekursor, dan Zat Adiktif (NPPZA)** pada domain **Pemeriksaan Sarana**.
>
> **Verifikasi**: seluruh angka di dokumen ini diverifikasi langsung ke `staging` via `pemeriksaan_reader` pada **13 Oktober 2026**. Angka adalah snapshot — regenerasi dengan query yang sama sebelum dipakai untuk keputusan.
>
> **Revisi 13 Okt 2026 (audit ulang)**: §4.1 ditambahkan — variasi nilai & kunci yang belum terpetakan (alias kode, kunci join `master_data_id`, JSON-string `jenis_obat`, prefiks narasi); guard G4 & G8 dikoreksi. **Reverifikasi POV kedua (13 Okt 2026)**: V1–V3, V6–V9 tepat; V4 & V5 dikoreksi (elemen null 35 bukan 45 · `506` = 17 bukan 14 · total bucket V5 ±730/0,23% — `699` berada di dalam rentang 677–714). **Revisi ekspektasi**: setiap use case kini memuat blok **Ekspektasi jawaban** (bentuk output + bahasa aman) — fokus pada variasi data yang belum terpetakan, bukan isian kosong.
>
> **Pesan utama**: tidak ada modul "Ekspor-Impor" ataupun "Pengawasan Keamanan Mutu" di SIPT. Kamus `MODUL` hanya memuat 5 nilai: Pemeriksaan Sarana · Sampling · Iklan · Penandaan · Pengujian. Data NPPZA hidup **tersebar di dalam domain Pemeriksaan Sarana** (jalur terkuat: pemeriksaan PBF/IFK/IFP), dan sebagian kebutuhan (permit impor, zat adiktif terstruktur) **memang tidak ada** — jawab lewat protokol NOT COVERED (`context/95-batas-domain.md`).

---

## 1. Ringkasan kesiapan per kebutuhan

| # | Kebutuhan informasi | Verdict | Jalur data utama |
|---|---|---|---|
| A1 | Tren pengawasan NPP per tahun | ✅ siap (2 grain, jangan dicampur) | `klasifikasi_id` + `bridge_pemeriksaan_komoditi_pbf` |
| A2 | Hotspot balai/wilayah NPP | ✅ siap | `fact → dim_balai` |
| A3 | Jenis sarana pengelola NPP | ✅ siap | `klasifikasi_id × jenis_id` |
| A4 | Faskes yang mengelola prekursor | ⚠️ siap dengan batas | `fact_pemeriksaan_profil_faskes.prekursor` |
| A5 | Komoditi obat-kelola di PBF | ✅ siap | `bridge_pemeriksaan_komoditi_pbf` + `FOKUS_PEMERIKSAAN` |
| A6 | Temuan BKO / obat keras / bahan berbahaya | ⚠️ siap dengan guard | `bridge_pemeriksaan_temuan` (jsonb + kode raw) |
| A7 | Zat adiktif terstruktur; CAPA "Re-Ekspor" | ❌ tidak bisa | hanya narasi; CAPA re-ekspor 2/260.886 |
| B1 | Sarana importir yang diperiksa | ⚠️ terbatas | `dim_sarana.nama_sarana` (teks bebas) |
| B2 | Temuan produk impor per negara asal | ⚠️ siap dengan normalisasi | `bridge_pemeriksaan_temuan.negara` |
| B3 | Produk impor via NIE `ML` | ⚠️ proxy, belum final | `dim_produk.nomor_registrasi` |
| B4 | Data permit/awal impor (RPO/ERBA-ERLA) | ❌ sistem lain | tidak tersambung ke staging ini |
| C1 | TMS Keamanan, Mutu & Gizi Pangan | ⚠️ siap parsial | `kategori_kode` raw 220131–220133 |
| C2 | Profil manajemen mutu pabrik pangan | ✅ siap | `fact_pemeriksaan_profil_pangan_md` |
| C3 | Istilah "PKM" | ⚠️ wajib klarifikasi | `PKM` = Puskesmas, bukan keamanan mutu |

---

## 2. Peta lokasi data (hasil verifikasi live 13 Okt 2026)

### 2.1 Jejak NPPZA dan volumenya

| Lokasi | Grain | Volume terverifikasi |
|---|---|---:|
| `fact_pemeriksaan.klasifikasi_id` → `JENIS_KLASIFIKASI` | 1 kasus | Narkotika **273** · Psikotropika **255** · Obat Tertentu 176 · Prekursor **119** · Bahan Berbahaya 108 |
| `bridge_pemeriksaan_komoditi_pbf.komoditi_kode` → `KOMODITI` | 1 komoditi dikelola per kasus PBF/IFK/IFP | Psikotropika (829) **4.588** · Prekursor (831) **4.198** · Narkotika (827) **2.004** · OOT (828) 4.671 · Obat (123) 7.903 · Obat Lainnya (830) 5.733 · CCP (826) 5.121 · SAS 745 · Bahan Obat 181 |
| `bridge_pemeriksaan_fokus_pbf.fokus_kode` → `FOKUS_PEMERIKSAAN` | 1 fokus per kasus | **"NPP dan OOT" 5.070** · Obat 9.351 · CCP 4.654 · SAS 798 · Bahan Obat 406 |
| `fact_pemeriksaan_profil_faskes.prekursor` | 1 profil per kasus faskes | `t` **5.094** · `f` 1.616 · NULL 66.653 — **hanya form Toko Obat** |
| `fact_pemeriksaan_profil_faskes.jenis_obat` | TEXT berisi JSON-array `'["223","229",…]'` — parse dulu; nilai = `master_data_id` `JENIS_OBAT_KELOLA` | kode 223 Narkotika · 226 Psikotropika · 229 Prekursor · 224 Antibiotika · 227 Obat Lain · 228 Vaksin · 225 OOT · 231 CCP Lain |
| `fact_pemeriksaan_narasi.teks` | 1 potongan narasi | menyebut `narkotik/psikotrop/prekursor/zat adiktif`: **53.785** (catatan_balai 23.893 · hasil_balai 21.431 · TL detil 3.198 · analisa 1.640 · rekomendasi 528) |
| `bridge_pemeriksaan_temuan.kategori_kode` (raw) | 1 temuan produk | BKO `499` **18.875** (termasuk combo `["499","506"]` 7.851) · Obat Keras `211214` **22.475** · Bahan berbahaya `220131/2/3` **2.346** · Diversi `760` 1.910 · Illegal/TIE `757` 9.213 |
| `dim_master_data` (kamus pendukung) | kamus | `KOMODITI` 16/18/20 · `JENIS_OBAT_KELOLA` JBK01/04/07 · `JENIS_KLASIFIKASI` 005/PSI19/009 · `KRITERIA_RISIKO` 3h ("Narkotik, Psikotropik, Prekursor… rawan didiversikan") & 3i ("Obat Impor") · label CAPA "…Re-Ekspor" |

### 2.2 Jejak ekspor-impor

| Lokasi | Kondisi |
|---|---|
| `dim_sarana.nama_sarana` | 116 nama memuat `ekspor/impor/narkotik/BNN` — teks bebas, **bukan atribut resmi importir**; tidak ada kolom klasifikasi distribusi di staging (ada di `profil_sarana_json`, belum dikamus) |
| `bridge_pemeriksaan_temuan.negara` | asal produk temuan: Indonesia ±201 rb · sentinel `-` **54.428** · kosong/NULL **6.333** · China/Cina/CHINA ±18 rb · Malaysia 8.762 · Thailand 2.732 · Korea 1.614 · USA 1.016 — **ejaan tidak dinormalisasi di DB** |
| `dim_produk.nomor_registrasi` | prefix `ML` = impor / `MD` = lokal — proxy, konvensi belum dikonfirmasi BPOM |
| Kamus `TL_PRODUK_TEMUAN` | ada tindakan "Dikembalikan kepada produsen / importir" (33,8 rb di sumber) |
| CAPA/Saran/BA | `tl_capa::text ILIKE '%ekspor%'` = **2 baris** dari 260.886 — praktis tidak dipakai |

### 2.3 Jejak "keamanan mutu"

| Lokasi | Kondisi |
|---|---|
| `KATEGORI_TEMUAN_PRODUK` kode 25 / raw 220131–220133 | "TMS Persyaratan Keamanan, Mutu, Dan Gizi Pangan" + bahan berbahaya — ±2.350 temuan, **baru muncul sejak 2024** |
| `fact_pemeriksaan_profil_pangan_md` | `manajemen_mutu`, `dokumen_mutu`, `tinjauan_berkala` — profil sistem mutu pabrik pangan MD |
| `fact_pemeriksaan_narasi` | menyebut "keamanan mutu": 570 baris (hasil_balai 342 · catatan_balai 222) |
| `JENIS_SARANA 03PKM` | **Puskesmas** (19.897 profil / 19.944 kasus) — bukan "Pengawasan Keamanan Mutu" |

---

## 3. Use case — format sama dengan blueprint 07

### Case A1 — Tren pengawasan NPP per tahun

**Pertanyaan natural**

> Bagaimana tren pengawasan narkotika/psikotropika/prekursor lima tahun terakhir?

**Maksud bisnis** — menilai intensitas pengawasan obat berkontrol naik/turun; dasar alokasi target tahunan.

**Data**

```text
Jalur 1 (kasus komoditi NPP): fact_pemeriksaan.klasifikasi_id → JENIS_KLASIFIKASI
Jalur 2 (pengelolaan di PBF): bridge_pemeriksaan_komoditi_pbf / fokus_pbf → fact → dim_date
```

**Kondisi data (verified)** — dua grain, dua cerita:

| Tahun | Kasus komoditi NPP (PBF) | Kasus fokus "NPP dan OOT" |
|---|---:|---:|
| 2020 | 778 | 516 |
| 2021 | 786 | 519 |
| 2022 | 1.005 | 704 |
| 2023 | 1.042 | 830 |
| 2024 | **1.171** | **965** |
| 2025 | 1.061 | 949 |
| 2026 (YTD) | 644 | 585 |

Intensitas pengawasan NPP di PBF **naik 2020→2024 lalu plateau**, sementara kasus komoditi NPP di sarana pelayanan (klasifikasi) justru menurun (110 narkotika 2020 → 8 pada 2026 YTD).

**Ekspektasi jawaban** — dua panel terpisah, satu angka per jalur:

| Tahun | Jalur (klasifikasi / PBF) | Kasus | Catatan lingkup |
|---|---|---|---|

- Bahasa aman: **"kasus pemeriksaan dengan komoditi narkotika/psikotropika/prekursor"** — bukan "kasus narkotika" (kasus menyorot sarana pemeriksaan, bukan barang sitaan).
- YTD selalu disebut; tren tidak boleh mencampur dua jalur dalam satu angka.
- Bila user minta "semua narkotika", klarifikasi jalur mana (kasus komoditi vs pengelolaan PBF) — Gate.

**Batas**

- jangan gabungkan dua jalur di satu angka;
- ada tanggal kotor **2018–2019 dan 2027** (min `tgl_start` 2018-01-11, max 2027-07-27) — filter rentang wajib;
- YTD 2026 = parsial, sebutkan.

---

### Case A2 — Hotspot balai NPP

**Pertanyaan natural**

> Balai mana yang paling banyak menangani kasus narkotika/psikotropika/prekursor?

**Data** — `fact_pemeriksaan` (klasifikasi NPP) → `dim_balai`.

**Kondisi (verified)** — ✅ siap:

| Balai | Kasus NPP |
|---|---:|
| **BALAI POM DI JAMBI** | **229** |
| BB POM MAKASSAR | 77 |
| BB POM MANADO | 52 |
| Loka POM Kota Tanjung Pinang | 33 |
| BB POM DENPASAR | 23 |
| BB POM BANDUNG | 21 |

**Ekspektasi jawaban**

| Balai | Regional | Kasus NPP | Porsi |

- Top 5–10 balai + total keseluruhan; regional diambil dari `dim_balai.regional`.
- Bila satu balai mendominasi >30%, lampirkan cek `kasus_id` (satu operasi besar ≠ hotspot distributif).
- Bahasa aman: "balai dengan penanganan kasus NPP terbanyak" — bukan "wilayah rawan narkotika".

**Batas** — Jambi mendominasi jauh; cek apakah itu efek satu operasi/kasus besar (group by `kasus_id` bila perlu) sebelum menyimparkan "hotspot".

---

### Case A3 — Jenis sarana tempat NPP ditemukan

**Data** — `klasifikasi_id × jenis_id → JENIS_SARANA`.

**Kondisi (verified)** — ✅ siap: Apotek 294 · PKM 141 · Toko Obat 68 (Prekursor 64) · RS Swasta 56 · RS Pemerintah 40 · Klinik 56. Pola: **sarana pelayanan**, bukan jalur impor/ekspor.

**Ekspektasi jawaban**

| Jenis sarana | Kasus | Porsi |

- Sertakan total 647 kasus dan catatan: **klasifikasi kasus = jenis obat yang ditemukan/diawasi di sarana**, bukan profil izin sarana.
- Bahasa aman: "obat berkontrol ditemukan di sarana pelayanan (Apotek/PKM/RS/Klinik)" — bukan "jalur impor NPP".

**Batas** — jumlah kecil (647 kasus total); persentase tanpa konteks menyesatkan.

---

### Case A4 — Faskes yang mengelola prekursor

**Pertanyaan natural**

> Berapa banyak fasilitas yang mengelola prekursor?

**Data** — `fact_pemeriksaan_profil_faskes.prekursor`.

**Kondisi (verified)** — ⚠️ siap dengan 3 batas:

1. kolom bertipe **text `'t'/'f'`**, bukan boolean — query wajib `prekursor = 't'`;
2. hanya terisi untuk form **Toko Obat: 5.094 dari 6.964 (73%)**; Apotek/PKM/Klinik/RS = 0 — itu **tidak diisi oleh form**, bukan bukti "tidak mengelola";
3. NULL 66.653 = kasus tanpa profil faskes (varian form berbeda).

**Bentuk output yang benar**

> "5.094 pemeriksaan Toko Obat mencatat sarana mengelola prekursor (73% dari 6.964 Toko Obat yang punya profil). Kolom ini tidak tersedia untuk jenis sarana lain."

---

### Case A5 — Komoditi obat-kelola yang diperiksa di PBF

**Data** — `bridge_pemeriksaan_komoditi_pbf.komoditi_kode` → kamus `KOMODITI` (kode 826–831, 123); `bridge_pemeriksaan_fokus_pbf.fokus_kode` → `FOKUS_PEMERIKSAAN`.

**Kondisi (verified)** — ✅ siap. Catatan cakupan: meski bernama `_pbf`, tabel mencakup **PBF + IFK + IFP** (form sama).

**Ekspektasi jawaban**

| Komoditi (label kamus `KOMODITI`) | Baris (komoditi×kasus) | Kasus unik | Fokus dominan |

- Label komoditi dari kamus via `master_data_id` (Psikotropika/Prekursor/Narkotika/OOT/…); jumlah baris + kasus unik disebut keduanya (grain berbeda, G7).
- Tambahkan konteks fokus "NPP dan OOT" (5.070 kasus); cakupan selalu disebut: **PBF + IFK + IFP**.
- Bahasa aman: "kasus pemeriksaan yang memuat komoditi psikotropika" — bukan "X kasus psikotropika".

**Batas**

- grain = baris komoditi × kasus (1 kasus bisa memuat banyak komoditi) — sebutkan "kasus dengan komoditi X", bukan "X kasus";
- cakupan kasus per tahun lihat Case A1.

---

### Case A6 — Temuan BKO / Obat Keras / Bahan Berbahaya

**Pertanyaan natural**

> Bagaimana tren temuan BKO dan obat keras, dan apa tindakannya?

**Data** — `bridge_pemeriksaan_temuan` expand `kategori_kode` (jsonb) → raw `499`/`211214`/`220131–133`; tindakan via `tindakan_kode` (`669` pemusnahan, `665` dikembalikan, `672` pengamanan…).

**Kondisi (verified)** — ⚠️ siap dengan guard:

| Tahun | BKO `499` | Obat Keras `211214` | Bahan berbahaya `220131–3` |
|---|---:|---:|---:|
| 2020 | 151 | 1.170 | 0 |
| 2022 | 531 | 3.282 | 0 |
| 2024 | 3.232 | 1.950 | 72 |
| 2025 | **9.327** | **8.317** | 1.639 |
| 2026 YTD | 3.341 | 3.557 | 1.009 |

Spike 2025 ekstrem (BKO 4× lipat) — **verifikasi dulu** apakah efek operasi nyata, perubahan form, atau draft (`is_kasus_draft`) — sebelum dinarati sebagai kenaikan.

**Ekspektasi jawaban** — dua panel, dengan bucket variasi §4.1 tampil sebagai kolom sendiri:

Panel tren:

| Tahun | BKO | Obat Keras | Bahan berbahaya | Tidak terklasifikasi (V1–V3) | Tanpa kategori (V4) |

Panel tindakan (expand `tindakan_kode`, bucket V5 terpisah — tidak dijumlah ke tindakan sah):

| Tindakan (label kamus via `master_data_id`) | Baris | Kasus |

- Bahasa aman: sebut spike 2025 dengan status verifikasinya ("menunggu verifikasi operasi vs form vs draft"), dan sebut grain (baris temuan, bukan kasus).
- Baris multi-kategori (`["499","506"]`) dihitung di kedua kategori, bukan dua kali di total baris — sebutkan.

**Batas**

- **angka selalu dari kode raw; label dari kamus via `master_data_id`** (bukan kolom `code` yang berisi kanonik 1–28): `d.type='KATEGORI_TEMUAN_PRODUK' AND d.master_data_id::text = kode_raw` — terverifikasi melabeli 15 kode terbanyak; residu **444 elemen (0,14% dari 321.257)** dipetakan lewat §4.1 (alias typo, kode tindakan nyasar, kode di luar kamus, kosong);
- expand jsonb dulu; `["499","506"]` adalah satu baris dua kategori — jangan dijumlah keduanya ke "total baris";
- selalu filter `is_kasus_draft = false` untuk angka final;
- bahan berbahaya baru ada sejak 2024 — bukan penurunan, tapi perubahan ketersediaan kode.

---

### Case A7 — Zat adiktif & CAPA Re-Ekspor

**Pertanyaan natural**

> Berapa kasus terkait zat adiktif? Berapa tindak lanjut re-ekspor?

**Kondisi (verified)** — ❌ **NOT COVERED**:

- tidak ada kolom/kamus/nilai "zat adiktif" — hanya kemunculan teks di narasi (bukan kategori terstruktur; cari dengan prefiks, lihat §4.1 V9);
- CAPA/Saran/BA memuat "ekspor" hanya di **2 dari 260.886** kasus.

**Jawaban yang benar** (protokol 3 kalimat): konsep tidak direkam terstruktur di database ini; tindak lanjut ekspor/Re-Ekspor praktis tidak dipakai di SIPT; terdekat yang bisa dijawab = narasi teks (evidence, pencarian prefiks `adiktif%`) atau kategori temuan Diversi/Penyalahgunaan (1.910 temuan).

---

### Case B1 — Sarana importir yang diperiksa

**Kondisi (verified)** — ⚠️ terbatas: 116 nama sarana memuat `importir/ekspor/impor/BNN`, tersebar di Klinik (39), Pangan (10), Kosmetik (9), dll. **Tidak ada kolom klasifikasi distribusi** di staging (`klasifikasi_distribusi` hanya ada di tabel legacy luar-scope) → identifikasi importir via teks nama = **proxy, bukan atribut resmi**.

**Ekspektasi jawaban**

| Sarana | Pemeriksaan | Basis identifikasi (teks nama) |

- Disclaimer wajib satu kalimat: "identifikasi berbasis pencocokan teks nama sarana, bukan atribut izin importir resmi".
- Bahasa aman: "sarana yang namanya memuat 'importir'" — bukan "sarana importir terdaftar".

---

### Case B2 — Temuan produk impor per negara

**Data** — `bridge_pemeriksaan_temuan.negara`.

**Kondisi (verified)** — ⚠️ siap dengan normalisasi wajib:

- varian ejaan satu makna: `China / china / CHINA / Cina`, `Indonesia / indonesia / INDONESIA`;
- sentinel `-` = **54.428 baris tidak tercatat** + kosong/NULL **6.333** — kelompokkan sendiri, **jangan masuk "impor"**;
- definisi aman: `lokal` = Indonesia (semua ejaan) · `tidak tercatat` = sentinel + NULL · `impor` = sisanya; laporkan porsi "tidak tercatat".

**Ekspektasi jawaban** — tabel wajib menampilkan 3 kelompok G8 bersebelahan:

| Kelompok | Temuan | Catatan |
|---|---:|---|
| Lokal (Indonesia, semua ejaan) | ±201 rb | — |
| **Tidak tercatat (`-`, NULL, kosong)** | **54.428 + 6.333** | **selalu tampil** |
| Impor (sisanya, dinormalisasi) | China ±18 rb · Malaysia 8.762 · Thailand 2.732 · Korea 1.614 · USA 1.016 | ejaan digabung |

- Tanpa kolom "tidak tercatat", peringkat impor terlihat melebih-lebihkan — itu kesalahan jawaban, bukan selera format.

---

### Case B3 — Produk impor via NIE

**Kondisi** — ⚠️ proxy: `dim_produk.nomor_registrasi` prefix `ML` (impor) / `MD` (lokal), konvensi belum dikonfirmasi BPOM; `dim_produk.is_imported` **selalu FALSE — jangan dipakai**.

**Ekspektasi jawaban**

| Produk | NIE | Prefix | Asal (negara_pabrik bila ada) |

- Disclaimer wajib: "asal produk diperkirakan dari prefix NIE (ML=impor, MD=lokal); konvensi belum dikonfirmasi BPOM; kolom `is_imported` tidak reliabel (selalu FALSE)".
- Bahasa aman: "produk dengan NIE prefix ML" — bukan "produk impor terverifikasi".

---

### Case B4 — Data permit/awal impor obat (RPO/ERBA/ERLA)

**Kondisi** — ❌ **sistem lain**: repositori ERBA/ERLA yang ada hanya mencakup **registrasi pangan** (`t_produk_3_erba`, `t_btp_3_erla`, …); untuk obat-NPP belum ada sumber yang tersambung ke staging.

**Ekspektasi jawaban** — protokol NOT COVERED 3 kalimat: (1) data permit/awal impor obat-NPP tidak direkam di database ini; (2) kemungkinan besar berada di sistem terpisah (pipeline RPO/ERBA obat — belum tersambung); (3) terdekat yang bisa dijawab dari staging: temuan produk impor via `negara` (Case B2) atau NIE prefix (Case B3), dengan bedanya disebut.

---

### Case C1 — TMS Keamanan, Mutu & Gizi Pangan

**Kondisi** — ⚠️ siap parsial: raw `220131` (665) + `220132` (1.311) + `220133` (370) = ±2.350 temuan, **baru muncul 2024** (bukan tren turun sebelumnya). Kategori kanonik 25 di kamus staging ada, tapi kode raw di data tidak match kamus — pakai raw.

**Ekspektasi jawaban**

| Tahun | Temuan TMS Keamanan, Mutu & Gizi Pangan | Kasus |

- Nama kategori ditulis **lengkap**: "TMS Persyaratan Keamanan, Mutu, dan Gizi Pangan".
- Wajib sebut: kategori baru dipakai sejak 2024 — tahun sebelumnya **bukan nol pelanggaran**, melainkan kode belum tersedia di form.

---

### Case C2 — Profil manajemen mutu pabrik pangan

**Data** — `fact_pemeriksaan_profil_pangan_md`: `manajemen_mutu`, `dokumen_mutu`, `tinjauan_berkala`, `proses_pengolahan`, plus identitas pabrik (`nib`, `nie`, alamat, skala_usaha). ✅ siap; cakupan = kasus Pangan MD yang punya profil.

**Ekspektasi jawaban**

| Pabrik | Skala usaha | Manajemen mutu | Dokumen mutu | Tinjauan berkala |

- Sebut cakupan (kasus Pangan MD dengan profil vs total kasus Pangan MD) sebelum menyimpulkan persentase.
- Bahasa aman: "pabrik pangan MD yang tercatat menerapkan manajemen mutu" — bukan "pabrik bersertifikat mutu".

---

### Case C3 — Istilah "PKM"

**Kondisi** — ⚠️ wajib klarifikasi (Gate): user bisa bermaksud **Puskesmas** (`JENIS_SARANA 03PKM`, 19.944 kasus) atau **Pengawasan Keamanan Mutu** (tidak ada sebagai modul).

**Ekspektasi jawaban** — klarifikasi melalui tool `ask_clarification`/`ask_user` (bukan teks jawaban), satu pertanyaan: *"PKM yang dimaksud Puskesmas (jenis sarana kesehatan) atau pengawasan keamanan mutu?"* Bila maksudnya keamanan mutu → jawab lewat Case C1/C2 dengan batas yang disebut.

---

## 4. Aturan guard wajib (agregat semua case)

| # | Guard | Alasan (terverifikasi) |
|---|---|---|
| G1 | Filter `tgl_start BETWEEN 2020-01-01 AND <hari ini>` (atau sebut rentang) | tanggal kotor 2018–2019 dan 2027 ada di data |
| G2 | `is_kasus_draft = false` untuk angka temuan final | draft ikut terhitung bila tidak disaring |
| G3 | Expand `jsonb_array_elements_text` sebelum join/agregasi kategori & tindakan temuan | `kategori_kode` array; baris multi-kategori |
| G4 | Angka kategori dari kode raw; label via kamus **`master_data_id`** (bukan kolom `code` 1–28); alias & residu wajib dipetakan per §4.1 | kolom `code` kamus ≠ kode raw data (506/…); join `master_data_id::text = kode_raw` terbukti bekerja; residu 444/321.257 elemen |
| G5 | Wajib `type` saat join `dim_master_data` | puluhan kamus dalam satu tabel |
| G6 | `prekursor`/kolom flag faskes = text `'t'/'f'`, dan hanya berisi untuk Toko Obat | bukan boolean; cakupan form |
| G7 | Sebutkan grain: kasus (`COUNT(DISTINCT pemeriksaan_id)`) vs baris (`COUNT(*)`) vs kuantitas vs nilai | empat angka berbeda dari tabel yang sama |
| G8 | Normalisasi `negara` + kelompok "tidak tercatat" terpisah | sentinel `-` 54.428 · kosong/NULL 6.333 · ejaan ganda (`Indonesia/indonesia/INDONESIA` · `China/china/Cina`) |
| G9 | Kode komoditi PBF (826–831, 123) memakai kamus `KOMODITI`; kode fokus (1–5 via master_data_id 507–510, 211636) memakai `FOKUS_PEMERIKSAAN` | dua kamus berbeda, jangan tertukar |
| G10 | Bridge `_pbf` mencakup PBF + IFK + IFP | form sama, nama tabel menyesatkan |

### 4.1 Variasi nilai & kunci yang wajib dipetakan (terverifikasi live 13 Okt 2026)

Nilai **menyimpang sudah ada di data** — bukan kolom kosong, bukan "belum diisi". Variasi ini muncul tepat di jalur pertanyaan user (A4 · A6 · A7 · B2 · C1); setiap variasi punya perlakuan tetap, dan bila tidak dipetakan angka jawaban salah diam-diam.

| # | Kolom | Variasi di data | Perlakuan | Dampak bila diabaikan |
|---|---|---|---|---|
| V1 | `kategori_kode` | alias typo `21214` (134 elemen) ≈ `211214`; `211215` (1) | kanonikkan ke kode kamus sebelum agregasi | under-count "Temuan Obat Keras" ±134 |
| V2 | `kategori_kode` | kode **tindakan** nyasar ke kategori: `762` (54) · `669` (37) · `665` (4) · `670` (4) · `672` (2) | bucket "kode tindakan salah tempat" — jangan dijumlah ke kategori | kategori palsu, angka bengkak tanpa makna |
| V3 | `kategori_kode` | kode di luar kamus: `449` (60) · `507` (11) · `560` (6) · `508–518` (44) · `1`/`131` (2 masing-masing) · `1001`/`814`/`5606` (1 masing-masing) | bucket "tidak terklasifikasi" + sebut jumlahnya | volume hilang senyap |
| V4 | `kategori_kode` | elemen `null` (35) · baris tanpa array (30) · string kosong **0** | bucket "tanpa kategori" | — |
| V5 | `tindakan_kode` | kode kategori nyasar ke tindakan: `506` (17) · `759` (2) · `840` (1); kode di luar kamus: `699` (196) · `258` (56) · `166` (52) · rentang `677–714` (344 — **termasuk `699` 196, jangan dobel hitung**); elemen `null` (65) · string kosong (0) | bucket "tindakan tak terklasifikasi" — total ±730 elemen (0,23% dari 322.482) | distribusi tindakan salah |
| V6 | `negara` | ejaan huruf (`Indonesia/indonesia/INDONESIA` · `China/china/Cina`), sentinel `-`, kosong/NULL | 3 kelompok G8 (lokal / tidak tercatat / impor) | salah klasifikasi impor |
| V7 | `profil_faskes.jenis_obat` | TEXT ber-JSON `'["223",…]'` — bukan jsonb/array asli | parse dulu; kode = `master_data_id` `JENIS_OBAT_KELOLA` | filter NPP gagal senyap (0 baris) |
| V8 | kunci join kamus (semua bridge) | `klasifikasi_id` · `komoditi_kode` · `fokus_kode` · `kategori_kode` · `tindakan_kode` menyimpan **`master_data_id` sebagai teks**; kolom `code`/kanonik kamus bukan kunci | join via `master_data_id`; `type` wajib (G5) | join kosong — mis. `005`/`PSI19`/`009` (komoditi NPP) tidak pernah ada di data |
| V9 | `narasi.teks` | ejaan tidak seragam: `narkotik` 28.944 vs `narkotika` 26.991 baris; `psikotrop` 40.167 vs `psikotropika` 37.347 | pencarian wajib **prefiks** (`narkotik%`, `psikotrop%`, `prekursor%`, `adiktif%`) | kehilangan 7–8% bukti narasi |

---

## 5. Ringkasan kondisi → keputusan siap/jumlah

- **Siap tanpa syarat**: A1 (per jalur), A2, A3, A5, C2.
- **Siap dengan guard**: A4, A6, B2, B3, C1.
- **Terbatas/proxy**: B1 (teks nama sarana).
- **Tidak tersedia — jawab NOT COVERED**: A7 (zat adiktif terstruktur, Re-Ekspor sebagai metrik), B4 (permit impor obat; sistem lain).
- **Risiko salah baca istilah**: C3 ("PKM").

### Catatan context (untuk pengelola agent)

Halaman context aktif saat ini sudah mengajarkan routing umum (`20-komoditi`, `40-temuan-produk`, `41-nilai-dan-negara`, `95-batas-domain`), tetapi **belum** memuat: decode `bridge_pemeriksaan_komoditi_pbf`/`fokus_pbf`, kolom `profil_faskes.prekursor`/`jenis_obat` (termasuk parse JSON-string), guard G1/G4/G6/G9/G10, tabel variasi §4.1 (alias kode, kunci join `master_data_id`, prefiks narasi), blok **Ekspektasi jawaban** per use case (§3), dan istilah NPPZA/keamanan-mutu/PKM. Blueprint ini menjadi sumber bahan halaman context berikutnya.

**Adopsi (13 Okt 2026)**: seluruh butir di atas telah ditulis ke snapshot `context_recap/13-10-2026 v6-nppza/` — halaman baru `22-komoditi-pbf-dan-fokus.md` & `25-profil-sarana-faskes.md`, revisi `20/40/41/60/80/95/97`, PAGE MAP & skill `bpom-analyst`. Menunggu linter/UAT lalu promosi; context hidup belum berubah. Angka-angka blueprint §4.1 sengaja **tidak** disalin ke context (aturan tanpa-angka-hasil) — context mengajarkan jalur penemuannya.
