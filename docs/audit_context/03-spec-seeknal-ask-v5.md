# 03 — Spesifikasi `SEEKNAL_ASK.md` v5

> `SEEKNAL_ASK.md` adalah **orchestrator**: ia merutekan dan menggerbang, **tidak memuat aturan data**. Aturan hidup di halaman `context/`; penegakan hidup di `skills/`.
>
> Yang baru di v5: blok **Canonical Rules** yang diletakkan sebelum gerbang dan **menang** atas halaman bila berbeda.

---

## 1. Kerangka dokumen

| # | Bagian | Isi | Perubahan dari v3 |
|---|---|---|---|
| 1 | Kepala | peran, prinsip "jawaban dari SQL bukan memori", lingkup tabel | ditambah daftar tabel eksplisit |
| 2 | Lingkup & tabel terlarang | 27 tabel boleh dibaca; 26 tabel pengawasan terlarang | **baru**, eksplisit |
| 3 | Tabel skill | `bpom-analyst` · `visualize-chart` · `bpom-forecaster` · `detect-anomaly` | tidak berubah strukturnya |
| 4 | **Canonical Rules** | 5 blok keputusan (§2 di bawah) | **baru** |
| 5 | Page Map | konsep + trigger words → halaman (+ `05-filter-katalog` untuk label panel) | diganti ke konsep `staging` |
| 6 | Gate 0 CLASSIFY | pemecahan "temuan" jadi tiga jalur | ditambah sub-routing |
| 7 | Gate 1 CLARIFY | hemat: pakai default lalu sebutkan asumsi; daftar wajib-tanya | isi daftar diganti |
| 8 | Gate 2 RESOLVE | P1–P5; P2 wajib `type`; panel label tanpa kolom = P5 | P5 diperluas |
| 9 | Gate 3 COMMIT | intent · entity · tanggal · count_col · codes · tables · filters · **varian** · **aspek_route** · shape | dua field baru |
| 10 | Gate 4 EXECUTE | budget langkah logis; stop rules; larangan menuning filter | ditambah larangan |
| 11 | Gate 5 VERIFY | tabel check 10 baris versi pemeriksaan | isinya diganti |
| 12 | Follow-up | warisi jawaban, turunkan ulang metode; kasus dua panel | ditambah satu aturan |
| 13 | Closing sequence | satu chart + satu CSV | tidak berubah |

---

## 2. Blok Canonical Rules (isi konkret)

### 2.1 Entity · tanggal · hitungan — dari SATU baris keputusan

| Kata dalam pertanyaan | Entity | Tanggal |
|---|---|---|
| pemeriksaan · inspeksi | `COUNT(DISTINCT fact_pemeriksaan.id)` | `tgl_start` |
| sarana (unik) | `COUNT(DISTINCT sarana_id)` | `tgl_start` |
| temuan produk — **kasus** | `COUNT(DISTINCT pemeriksaan_id)` | `tgl_start` |
| temuan produk — **baris** | `COUNT(*)` | `tgl_start` |
| penugasan petugas | `COUNT(*)` pada bridge petugas | `tgl_start` |

Entity dan kolom tanggal dipilih dari satu baris — tidak dicampur.

### 2.2 Branch filter dari kata pertanyaan

| Kata / maksud | Aksi |
|---|---|
| "selesai" | status akhir: `FINISHED` + `FINISHED_PUSAT` |
| "dalam proses" / "belum selesai" | bukan kelompok selesai dan bukan kelompok draft |
| "draft" | kelompok draft (`DRAFT`, `DRAFT_REVISE`, `DRAFT_PUSAT`, `DRAFT_PUSAT_REVISE`) |
| "MK" / "memenuhi ketentuan" | `kesimpulan_balai_id` → kode MK |
| "TMK" / "tidak memenuhi" | kode TMK |
| "pendistribusian" | label resmi kamus adalah **Penyaluran** |
| **"temuan"** | **tiga jalur**: aspek (pelayanan) · klausul (produksi) · produk — wajib dipilih, jika ragu klarifikasi |
| "kritis / Major / Minor" | per **kasus** (counter/`level_kesimpulan`) **atau** per **klausul** (`nilai_aspek`) — sebutkan coverage |
| "produksi / distribusi / pelayanan" | golongan pada kamus `JENIS_SARANA` lewat `parent_name` |
| "sudah di-TTE" | **tidak tersedia** → `95-batas-domain` |

### 2.3 Tanggal

| Kolom | Arti | Dipakai untuk |
|---|---|---|
| `tgl_start` | pemeriksaan dimulai | default periode & tren |
| `tgl_end` | selesai | pertanyaan penyelesaian |
| `created_at` / `updated_at` | administrasi | kesegaran data & perubahan terakhir |

### 2.4 Wilayah — tiga makna berbeda

| Bahasa | Kolom |
|---|---|
| "oleh BBPOM Bandung" | `fact_pemeriksaan.balai_id` → `dim_balai` |
| "Regional Semarang" | `dim_balai.regional_name` (jangan kolom `regional`) |
| "sarana di Jawa Barat / Bandung" | `dim_sarana.provinsi_id` / `kabupaten_id` |
| "wilayah kerja UPT" | perlu definisi cakupan → bila tidak tersedia: P5 |

### 2.5 Aturan tingkat satu

1. Setiap join ke kamus **wajib menyebut `type`** (72 tipe kamus dalam satu tabel `dim_master_data`).
2. Kolom teks yang isinya angka wajib `::text` saat join.
3. Kolom array jsonb wajib di-`jsonb_array_elements_text` sebelum di-join.
4. Label aspek selalu `COALESCE(aspek_ktl_nama, aspek_label)`.
5. Nilai teks dinormalkan sebelum dikelompokkan (spasi tepi, spasi ganda, beda kapitalisasi).

---

## 3. Perubahan Page Map

Baris baru yang wajib ada:

| Pertanyaan menyebut | Buka |
|---|---|
| **label panel apa pun** (klasifikasi, legal, status label, tingkat pemenuhan CPOB, target, tanggal, wilayah) | `05-filter-katalog.md` + halaman pemilik |
| aspek / skor / kepatuhan pelayanan | `35-kepatuhan-aspek.md` |
| klausul / tidak sesuai / severity | `37-klausul-dan-severity.md` |
| observasi / GMP / vaksin / narasi | `45-observasi-dan-vaksin.md` |
| "temuan" (tanpa objek jelas) | `97-glossary-istilah-user.md` → lalu `35`/`37`/`40` |
| perhitungan apa pun | `00-menghitung.md` + `01-peta-data-dan-routing.md` |

Baris lama yang **dibuang**: apa pun yang menyebut `mv_*`, `nama_upt`, `jenis_sarana` versi rantai, `agg`, `timeline`.

---

## 4. Perubahan per gerbang

| Gerbang | Perubahan konkret |
|---|---|
| Gate 0 | sebelum `bpom-analyst`, bila pertanyaan memuat "temuan", tentukan dulu objeknya (aspek/klausul/produk) atau simpan sebagai kandidat klarifikasi untuk Gate 1 |
| Gate 1 | default hemat dipertahankan; daftar **wajib tanya** versi pemeriksaan: objek temuan · makna wilayah · metrik tren · tingkat kritis · jenis tindak lanjut · arti "inspektur terbaik" |
| Gate 2 | P1–P5; **P2 wajib `type`**; **P5 diperluas**: label panel tanpa kolom (mis. klasifikasi distribusi, status label) = P5, bukan tebakan kolom terdekat |
| Gate 3 | tambah `varian=<flag_varian_datas>` dan `aspek_route=<skor|klausul|observasi|produk|tidak ada>` |
| Gate 4 | larangan eksplisit menuning filter; stop bila dua probe tidak mengubah rencana |
| Gate 5 | tabel check: (1) `00` dibaca · (2) entity+tanggal satu baris · (3) status sesuai kata kerja · (4) filter kesimpulan hanya bila ditanya · (5) setiap `WHERE` tertelusur ke kata pertanyaan · (6) eksklusi diterapkan · (7) scope terlihat di SQL · (8) himpunan kode = keputusan Gate 3 · (9) angka utama dari query globalnya sendiri · (10) **dua panel pelayanan vs produksi tidak dijumlahkan** · (11) **coverage severity disebut** · (12) **label aspek `COALESCE`** · (13) regional ≠ lokasi sarana · (14) korelasi bukan kausal |
| Follow-up | tambah: bila giliran sebelumnya menjawab satu panel, jangan diam-diam menggabungkan panel |

---

## 5. Guard lintas domain

Ditulis di kepala dokumen dan ditegakkan linter:

- istilah yang **dilarang**: `produk_id`, `jenis_permohonan`, `kategori_dokumen`, `status_produk`, `daerah_pabrik`, `daerah_trader`, `ERBA`, `ERLA`, `NIE`;
- tabel terlarang: 26 tabel domain pengawasan (namanya terlihat di katalog, `SELECT` ditolak);
- pertanyaan domain lain (pengawasan/penandaan/pengujian/registrasi) → jalur `95-batas-domain.md`, bukan kolom terdekat.

---

## 6. Yang TIDAK berubah

- struktur gerbang 0–5 dan sifatnya blocking;
- jalur P1–P5 sebagai kerangka resolusi;
- stop rules dan query ledger;
- kontrak jawaban (interpretasi kanonik → angka utama → rincian);
- closing pair: satu `visualize_chart` + satu `upload_to_s3`;
- aturan follow-up "warisi jawaban, turunkan ulang metode".

---

## 7. Kriteria lulus orchestrator

- [ ] tidak ada nama tabel/kolom lama;
- [ ] tidak ada istilah RPO;
- [ ] Canonical Rules lengkap 5 blok;
- [ ] Page Map memuat 21 halaman + baris label panel;
- [ ] setiap gerbang menyebut perubahan versi ini;
- [ ] Gate 5 memuat 14 check;
- [ ] panjang dokumen tetap muat dalam satu baca (`read_max_lines: 500`).
