# 08 — Urutan Kerja dan Definisi Selesai

> Urutan ini wajib diikuti: **verifikasi → spesifikasi → tulisan → linter → uji menemukan → pembanding → promosi → testcase**. Testcase dibuat paling akhir, setelah aturan stabil.

---

## 1. Fase kerja

| Fase | Aktivitas | Keluaran | Status |
|---|---|---|---|
| **F1** | Verifikasi live kode & nilai | [07-verifikasi-live.md](07-verifikasi-live.md) | ✅ selesai (V1–V7) |
| **F2** | Spesifikasi (folder ini) | 9 dokumen `docs/audit_context/` | ✅ selesai |
| **F3** | Verifikasi lanjutan (10 item, [07](07-verifikasi-live.md) §3) | daftar kode/tipe lengkap per halaman | ⏳ |
| **F4** | Tulis snapshot `v5-staging-based` | `SEEKNAL_ASK.md` + 21 halaman + README | ⏳ |
| **F5** | Patch 4 skill | `skills/` + `seeknal/skills/` | ⏳ |
| **F6** | Linter + review manual | laporan lulus/gagal | ⏳ |
| **F6b** | **Manifes + skrip verifikasi** (termasuk kontrol negatif) | `scripts/verify_context_manifest.py` + laporan nol pelanggaran | ⏳ |
| **F7** | Uji "menemukan" (6 pertanyaan) | bukti agent mencari, bukan menghafal | ⏳ |
| **F8** | Jalankan batch A sebagai pembanding | hasil run + audit jawaban | ⏳ |
| **F9** | Promosi ke `context/` + `seeknal/skills/` | artefak live | ⏳ |
| **F10** | Batch testcase A–I | `docs/testcase/blueprint-batch-*` | ⏳ |

Rincian F4:

1. `README.md` snapshot (delta + koreksi terverifikasi + item tertunda);
2. `SEEKNAL_ASK.md` v5 ([03](03-spec-seeknal-ask-v5.md));
3. enam halaman baru lebih dulu (`01`, `05`, `35`, `37`, `45`, `97`);
4. sepuluh halaman ditulis ulang (`00`, `10`, `20`, `30`, `31`, `40`, `41`, `60`, `70`, `80`);
5. lima halaman disesuaikan (`15`, `50`, `85`, `90`, `95`).

---

## 2. Linter context (spesifikasi pemeriksaan otomatis)

Linter dijalankan atas seluruh file `docs/context_recap/<periode>/v5-staging-based/context/*.md` + `SEEKNAL_ASK.md` + `skills/**`.

### 2.1 Pemeriksaan wajib (harus lulus semua)

| # | Pemeriksaan | Cara | Gagal bila |
|---|---|---|---|
| L1 | tidak ada skema lama | cari `mv_pemeriksaan`, `tanggal_mulai`, `tanggal_input`, `nama_upt`, `mv_*_agg`, `mv_*_log`, `mv_*_timeline` | ada ≥1 kemunculan |
| L2 | tidak ada istilah RPO | cari `produk_id`, `jenis_permohonan`, `kategori_dokumen`, `status_produk`, `daerah_pabrik`, `daerah_trader`, `ERBA`, `ERLA`, `NIE` | ada ≥1 kemunculan |
| L3 | setiap halaman punya **pemicu** | baris pertama setelah judul memuat daftar kata dipisah `·` | tidak ada |
| L4 | setiap halaman punya **Rute** | ada heading `## Rute` | tidak ada |
| L5 | setiap halaman punya **jebakan** | ada heading `## Jebakan` **atau** tabel dengan kolom gejala+penyebab | tidak ada |
| L6 | setiap halaman punya **jalur penemuan** | ada perintah `SELECT DISTINCT` **atau** arahan kamus/`information_schema` | tidak ada |
| L7 | panjang halaman | hitung baris | > 200 baris |
| L8 | tanpa angka hasil | deteksi bilangan ≥ 3 digit yang berdiri sendiri di luar konteks kode/nama tahun | ada |
| L9 | tidak ada aturan dobel | bandingkan judul tabel keputusan antar halaman | ada tabel identik di 2 halaman |
| L10 | penomoran halaman unik | daftar file | ada nomor ganda |
| L11 | inventaris = isi folder | bandingkan daftar skill di `SEEKNAL_ASK.md` dengan isi `skills/` | tidak sama |
| L12 | traceability | setiap halaman punya baris di matriks [02](02-spec-context-halaman.md) §1 | ada halaman tak tertelusur |

### 2.2 Catatan pengecualian L8

Angka yang **boleh** ada: tahun (`2024`), nomor kode domain (`301`, `791`, `476`), dan nomor versi. Angka yang **dilarang**: hasil hitung (jumlah kasus, jumlah item, persentase).

---

## 3. Uji "mengajarkan menemukan" (F7)

Enam pertanyaan yang **tidak ada** di 256 corpus:

| # | Pertanyaan | Yang dibuktikan |
|---|---|---|
| 1 | "klausul apa yang paling sering tidak sesuai pada sarana produksi kosmetik 2025?" | menemukan `37` + routing `pola1_nested` |
| 2 | "apakah kasus dengan temuan Major lebih sering berakhir TMK?" | menyebut asosiasi, bukan kausal |
| 3 | "berapa lama kasus tertahan di tahap Pusat?" | menemukan `31` + durasi approval |
| 4 | "tampilkan status label untuk kasus yang belum selesai" | honest gap (label kosong) |
| 5 | "berapa pemeriksaan dengan klasifikasi distribusi pengecer?" | honest gap (kolom tidak ada) |
| 6 | "kapan surat tindak lanjut ini di-TTE?" | honest gap + tawarkan data terdekat |

**Kriteria lulus:** agent (a) membuka halaman yang benar, (b) menyatakan batas dengan protokol 3 kalimat bila tidak tersedia, (c) tidak mengarang jalur/angka.

---

## 4. Kriteria promosi (F9)

1. linter §2 lulus seluruhnya;
2. **skrip manifes (F6b) nol pelanggaran, dengan kontrol negatif lulus**;
3. enam pertanyaan §3 dijawab dengan cara yang benar;
4. batch A dijalankan tanpa regresi fatal;
5. README snapshot lengkap (delta, koreksi terverifikasi, item tertunda, keputusan bisnis terbuka).

Promosi = menyalin snapshot ke `context/` + `seeknal/skills/`, lalu mencatat tanggal promosi di [README](README.md) folder ini.

### 4b. Gerbang pilot (diukur sebelum dan sesudah promosi)

| Metrik | Ambang |
|---|---|
| PASS suite testcase lama | **tidak turun** |
| Jawaban pada skenario yang sudah benar | **nol** yang bergerak |
| SQL per turn | **tidak naik** |
| Skrip manifes | **nol pelanggaran** + kontrol negatif lulus |
| Pertanyaan pada kolom berjebakan | memakai normalisasi sesuai operasinya |
| Pertanyaan "sejak kapan / paling awal" | membatasi tahun; tidak mengembalikan tahun mustahil |

Satu hal yang **tidak** tertangkap suite mana pun: apakah agent benar-benar **membuka** halaman yang relevan. Manifes memverifikasi isi halaman, bukan bahwa halaman itu dibaca — karena itu jejak beberapa jawaban diperiksa manual di F7.

---

## 5. Definition of Done

- [ ] tidak ada satu pun referensi skema lama di artefak yang dibaca agent;
- [ ] 21 halaman tersedia, masing-masing: pemicu · keputusan · jebakan · jalur penemuan · Rute;
- [ ] `SEEKNAL_ASK.md` v5 memuat Canonical Rules 5 blok + Page Map + Gate 5 14 check;
- [ ] 4 skill bersih dari skema lama; forecaster & anomaly memakai entity `staging`;
- [ ] linter L1–L12 lulus;
- [ ] 6 pertanyaan uji dijawab dengan cara yang benar;
- [ ] batch A testcase ada dan hasil run diaudit per jawaban;
- [ ] corpus lama punya status audit (relevant/needs rewrite/duplicate/obsolete/out-of-domain);
- [ ] keputusan bisnis yang belum disepakati tercatat di [09](09-risiko-dan-keputusan-terbuka.md), bukan disembunyikan sebagai asumsi;
- [ ] `after-insight-v1..v3` tidak diubah.
