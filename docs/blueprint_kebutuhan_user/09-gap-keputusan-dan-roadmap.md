# 09 — Gap, Keputusan, dan Roadmap

> Pisahkan tiga hal: **keputusan bisnis**, **perbaikan data**, dan **perbaikan agent/context/testcase**. Jangan menyelesaikan keputusan bisnis dengan asumsi teknis.

---

## 1. Keputusan bisnis yang harus disepakati

### D1 — Definisi temuan per varian

Perlu ditetapkan:

- rule per `area_key` pelayanan;
- kapan score dianggap tidak sesuai;
- arti opsi per field;
- cara membaca JSON opsi;
- hubungan klausul Tidak dan severity.

Output: **metric dictionary per area_key/form**.

### D2 — Definisi tren

Pilih/nyatakan:

- jumlah kasus;
- jumlah item tidak sesuai;
- proporsi ketidaksesuaian;
- skor kepatuhan;
- proporsi TMK;
- sarana unik bermasalah.

Output: contract tren per intent.

### D3 — Pelayanan vs produksi

Rekomendasi:

- jangan dijumlahkan mentah;
- tampilkan dua panel berdampingan;
- sediakan narasi perbandingan, bukan total gabungan.

### D4 — Penerimaan, Pengembalian, Pemusnahan

Tentukan:

- indikator ketidaksesuaian;
- field mana yang factual vs compliance;
- apakah Penerimaan/Pengembalian masuk kamus resmi;
- bagaimana N/A diperlakukan.

### D5 — Wilayah

Tentukan istilah standar:

- UPT/Balai pelaksana;
- regional Balai;
- lokasi sarana;
- wilayah kerja administratif.

### D6 — Severity → rekomendasi

Butuh matriks bisnis:

| Severity/kondisi | Rekomendasi yang wajar | Pengecualian |

Tanpa ini, sistem hanya dapat menunjukkan asosiasi, bukan menilai proporsionalitas.

### D7 — Arti kode khusus

- `kriteria` 1–4 pada observasi;
- TTP/TDP/TMBB;
- MS/TMS Mayor 1–3/TMS Kritikal vaksin;
- istilah/singkatan internal seperti PMR/Wasdis.

---

## 2. Perbaikan data

### P1 — Bridge antibiotik

Prioritas tinggi karena:

- disebut eksplisit user;
- ±25.780 kasus mempunyai detail;
- zat aktif dan volume belum queryable di `staging`.

Usulan:

```text
bridge_pemeriksaan_antibiotika
├── pemeriksaan_id
├── urutan
├── nama_zat_aktif
├── jumlah_penjualan
├── satuan_penjualan
├── jumlah_tanpa_resep
└── satuan_tanpa_resep
```

### P2 — Metric dictionary / area contract

Buat tabel/dokumen:

| area_key | pertanyaan form | vocab | tipe data | skala | definisi temuan | aspek |

Ini lebih penting daripada menambah query baru.

### P3 — Mapping section → aspek

- 108 section pelayanan;
- 47 sudah dipetakan;
- `tx_fast_moving_antibiotika` dan section lain perlu keputusan mapping;
- naratif harus ditandai sebagai teks, bukan item.

### P4 — Detail CPKB

- 2.610 kasus `clusterF_cpkb` tanpa bridge;
- perlu tabel detail atau keputusan bahwa hanya header/narasi yang tersedia.

### P5 — Label status dan kode khusus

- isi `status_label` atau buat semantic mapping;
- konfirmasi kode observasi/kesimpulan vaksin.

### P6 — Normalisasi free text

- pembersihan HTML/karakter;
- penyimpanan teks bersih;
- klasifikasi topik;
- evidence model;
- human review untuk label penting.

### P7 — Evidence store untuk AI

Simpan:

- label AI;
- sumber tabel/kolom;
- pemeriksaan_id;
- potongan teks;
- model/version;
- confidence;
- review status.

### P8 — Coverage gap bridge

Investigasi:

- 10.211 pola1_direct kosong;
- 1.665 pola1_observation;
- 398 clusterC_skor;
- 145 clusterC_naratif;
- 254 pola1_nested;
- 115 pola2;
- 14 lainnya.

---

## 3. Perbaikan agent/context/skill

### A1 — Semantic glossary

Context harus mengajarkan:

- istilah user;
- definisi bisnis;
- grain;
- ambiguities;
- clarification policy.

### A2 — Intent/grain router

Sebelum SQL:

```text
intent → entity → grain → scope → metric → route
```

### A3 — Varian-aware data routing

Gunakan:

- jenis sarana;
- `flag_varian_datas`;
- bentuk output per varian.

### A4 — Metric contracts

Context/skill tidak boleh mengajarkan formula global `opsi='no'`, score rata-rata mentah, atau total temuan tunggal.

### A5 — Clarification policy

Wajib klarifikasi untuk:

- temuan;
- wilayah;
- tren;
- kritis;
- tindak lanjut;
- inspektur terbaik.

### A6 — Evidence-first answer

Untuk free text/insight:

- summary;
- evidence cases;
- coverage;
- confidence/status.

### A7 — Output template per persona

- operator: detail kasus;
- Balai: kasus+tren;
- Pusat: perbandingan+konsistensi;
- pimpinan: ringkasan+prioritas.

### A8 — Honest gap

Agent harus menyatakan:

- data tidak tersedia;
- coverage parsial;
- keputusan bisnis belum ada;
- alternatif data terdekat.

---

## 4. Perbaikan testcase

### T1 — Audit 256 testcase lama

Klasifikasikan:

- relevant;
- needs rewrite;
- duplicate;
- obsolete;
- out-of-domain;
- generated-only.

### T2 — Bangun question-space baru

Mulai dari tujuh kebutuhan dan sembilan use-case, bukan nama kolom atau SQL pair lama.

### T3 — Batch kecil

8–16 testcase per tema:

1. monitoring;
2. kepatuhan;
3. risiko;
4. tindak lanjut;
5. evaluasi keputusan;
6. pola/regional;
7. antibiotik;
8. free text.

### T4 — Positive + anti-trap

Satu rule minimal:

- satu testcase benar;
- satu testcase yang mengekspos salah-grain/salah-route/salah-interpretasi.

### T5 — Evidence & coverage asserts

Testcase harus menguji:

- evidence trace;
- coverage statement;
- clarification;
- honest gap;
- forbidden causal claim.

---

## 5. Roadmap prioritas

### Fase 1 — Sepakati makna

1. semantic glossary;
2. metric contracts;
3. definisi wilayah;
4. severity→recommendation matrix;
5. status kesiapan tiap kebutuhan.

**Output**: file 05/06 blueprint disetujui stakeholder.

### Fase 2 — Tutup gap data prioritas

1. bridge antibiotik;
2. area contract;
3. section mapping;
4. CPKB detail;
5. label kode/status;
6. evidence store.

### Fase 3 — Update context/skill

1. routing intent/grain;
2. semantic glossary;
3. clarification policy;
4. metric rules;
5. persona output;
6. evidence/honest-gap.

### Fase 4 — Testcase batch kecil

1. buat satu batch;
2. review stakeholder;
3. validasi SQL/live data;
4. jalankan;
5. audit jawaban;
6. baru perluas.

### Fase 5 — Audit corpus lama

- pertahankan yang relevan;
- rewrite yang masih dibutuhkan;
- tandai obsolete, jangan menjadikannya gate;
- dokumentasikan coverage baru.

---

## 6. Prioritas berbasis dampak

| Prioritas | Item | Dampak |
|---:|---|---|
| 1 | metric contract per area | mencegah jawaban salah pada Q1–Q7 |
| 2 | semantic glossary & clarification | mencegah salah intent/grain |
| 3 | bridge antibiotik | menutup kebutuhan eksplisit user |
| 4 | evidence-first NLP | mengubah free text menjadi insight yang bisa diaudit |
| 5 | decision consistency Balai–Pusat | kebutuhan evaluasi utama Pusat |
| 6 | testcase blueprint baru | menjaga perubahan tidak kembali ke pola generated |
| 7 | CPKB/coverage bridge | memperluas cakupan |

---

## 7. Keputusan yang perlu dibawa ke stakeholder berikutnya

1. Apa definisi “temuan” untuk setiap aspek/form?
2. Metrik tren default apa yang diinginkan per persona?
3. Apakah pelayanan dan produksi harus selalu dipisah?
4. Definisi “wilayah kerja” yang resmi apa?
5. Apa matriks severity→tindak lanjut yang diharapkan?
6. Apakah Penerimaan/Pengembalian menjadi aspek resmi?
7. Apa output minimum laporan antibiotik?
8. Apakah insight AI perlu human approval sebelum masuk report?
9. Evidence apa yang wajib ditampilkan ke pimpinan vs analis?
10. Testcase lama mana yang masih dianggap business-critical?

---

## 8. Definition of done blueprint ke implementasi

- [ ] semantic glossary disetujui;
- [ ] metric contracts disetujui;
- [ ] prioritas gap data dipilih;
- [ ] context/skill mengacu blueprint;
- [ ] testcase baru punya persona/grain/metric/route/evidence;
- [ ] corpus lama diaudit relevansinya;
- [ ] jawaban AI menyatakan coverage & batas;
- [ ] free-text insight evidence-backed;
- [ ] laporan berbeda sesuai persona;
- [ ] perubahan terdokumentasi dan dapat ditelusuri.
