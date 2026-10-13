# 03 — Kebutuhan Informasi dan Pertanyaan User

> File ini menyusun **question-space** berdasarkan pekerjaan dan keputusan user—bukan berdasarkan 256 prompt generated.

---

## 1. Tujuh kelas kebutuhan informasi

### Kelas 1 — Monitoring kegiatan

User ingin tahu:

- apa yang sudah diperiksa;
- siapa yang memeriksa;
- kapan dan di mana;
- jenis sarana/komoditi apa;
- statusnya sudah sampai mana.

Contoh pertanyaan natural:

- Berapa pemeriksaan bulan ini?
- Sarana apa saja yang diperiksa oleh UPT kami?
- Kasus apa yang masih draft atau direvisi?
- Siapa petugas yang menangani kasus tertentu?
- Pemeriksaan apa yang belum selesai?

Bentuk output:

- angka agregat + daftar kasus;
- breakdown Balai/jenis sarana/periode;
- status workflow.

### Kelas 2 — Penilaian kepatuhan

User ingin tahu:

- aspek/klausul apa yang sesuai atau tidak;
- di mana ketidaksesuaian paling banyak;
- apakah kondisi membaik atau memburuk.

Contoh:

- Bagaimana tren ketidaksesuaian Penyimpanan?
- Aspek apa yang paling bermasalah pada Apotek?
- Klausul gudang apa yang paling sering tidak sesuai?
- UPT mana yang paling sering menemukan masalah Pengadaan?

Bentuk output:

- panel kepatuhan pelayanan;
- panel klausul produksi;
- kasus/item/persentase secara terpisah.

### Kelas 3 — Penilaian risiko

User ingin tahu:

- berapa Minor/Major/Kritis;
- sarana mana yang berulang kali kritis;
- bagaimana hubungan severity dengan MK/TMK/grade.

Contoh:

- Berapa temuan Major dan Kritis tahun ini?
- Sarana apa yang punya temuan kritikal berulang?
- Apakah kasus Major lebih sering berakhir TMK?
- Jenis sarana mana yang paling berisiko?

Bentuk output:

- severity per kasus;
- severity per klausul;
- breakdown jenis sarana/UPT/periode;
- evidence kasus.

### Kelas 4 — Respons dan tindak lanjut

User ingin tahu:

- tindak lanjut apa yang diberikan;
- apakah CAPA selesai;
- apakah tindakan proporsional terhadap temuan.

Contoh:

- Apa tindak lanjut dominan untuk kasus TMK?
- Apakah semua kasus Kritis sudah ditindaklanjuti?
- Kasus apa yang CAPA-nya belum selesai?
- Kapan pembinaan, teguran, penarikan, atau pencabutan direkomendasikan?

Bentuk output:

- severity × rekomendasi;
- daftar CAPA;
- kasus yang belum selesai;
- narasi tindak lanjut.

### Kelas 5 — Evaluasi keputusan UPT vs Pusat

User ingin tahu:

- apakah keputusan Balai konsisten;
- apakah Pusat mengubah kesimpulan/rekomendasi;
- di mana bottleneck/revisi paling banyak.

Contoh:

- Berapa kasus yang kesimpulan Balai dan Pusatnya berbeda?
- UPT mana yang paling sering direvisi?
- Apakah kasus dengan severity serupa mendapat tindakan serupa?
- Berapa lama kasus bergerak dari Balai ke Pusat?

Bentuk output:

- perbandingan kesimpulan;
- funnel approval;
- durasi tahap;
- daftar kasus koreksi.

### Kelas 6 — Analisis pola dan isu tematik

User ingin tahu:

- tren/hotspot;
- temuan berulang;
- pola regional;
- isu khusus seperti antibiotik.

Contoh:

- Apa temuan utama bulan ini?
- Regional mana paling banyak menemukan produk TIE?
- Sarana mana yang mengulang ketidaksesuaian yang sama?
- Antibiotik apa yang paling banyak dijual tanpa resep?
- Bagaimana tren pelaporan antibiotik antar-UPT?

Bentuk output:

- tren;
- hotspot map/table;
- daftar repeat offender;
- laporan tematik.

### Kelas 7 — Komunikasi, narasi, dan report

User ingin:

- merapikan free text;
- merangkum temuan;
- membuat report sesuai audiens;
- tetap dapat menelusuri bukti.

Contoh:

- Ringkas catatan pemeriksaan ini.
- Kelompokkan alasan TMK yang paling sering muncul.
- Buat laporan satu halaman untuk pimpinan.
- Tampilkan bukti kasus untuk insight ini.

Bentuk output:

- summary;
- cluster topik;
- tabel + chart + narasi;
- evidence appendix.

---

## 2. Sembilan pertanyaan analitik awal sebagai fondasi

### Q1–Q7 — Tren temuan per aspek

1. Pengadaan
2. Penerimaan
3. Penyimpanan
4. Penyerahan
5. Pengembalian
6. Pencatatan dan Pelaporan
7. Pemusnahan

User sebenarnya ingin mengetahui:

```text
periode
× aspek
× jenis sarana
× jumlah kasus
× jumlah item
× ketidaksesuaian
× tingkat kepatuhan
× wilayah/UPT
```

Namun statusnya berbeda:

| Aspek | Kebutuhan | Kondisi |
|---|---|---|
| Pengadaan | tren kepatuhan/ketidaksesuaian | siap untuk pelayanan dengan rule per `area_key` |
| Penerimaan | siapa/proses penerimaan + kepatuhan | data bercampur; definisi temuan perlu keputusan |
| Penyimpanan | kepatuhan pelayanan + klausul produksi | paling kaya, tetapi dua satuan harus dipisah |
| Penyerahan | kepatuhan, termasuk antibiotik | siap parsial; `opsi` bercampur jabatan/prosedur |
| Pengembalian | prosedur mutasi/retur | data ada, definisi temuan belum jelas |
| Pencatatan/Pelaporan | kepatuhan pencatatan | siap sebagian, termasuk konteks antibiotik |
| Pemusnahan | kepatuhan/prosedur pemusnahan | banyak N/A/yes; indikator temuan belum jelas |

Bentuk output yang direkomendasikan:

- **Panel A**: pelayanan—skor/persentase kepatuhan;
- **Panel B**: produksi—cacah klausul tidak sesuai/severity;
- jangan dijumlahkan menjadi satu total temuan.

### Q8 — Inspektur × jenis fasilitas

Kebutuhan:

- jumlah kasus per inspektur;
- pengalaman menurut jenis sarana/komoditi;
- distribusi penugasan;
- eksposur produksi/distribusi/pelayanan.

Batas:

- dapat menunjukkan eksposur penugasan;
- tidak cukup untuk menilai kompetensi formal/performa tanpa data sertifikasi/peran.

### Q9 — Jenis temuan, kekritisan, regional

Tiga pertanyaan berbeda:

1. **Kategori temuan produk** — kasus, baris produk, kuantitas, nilai ekonomi harus dipisahkan.
2. **Kekritisan** — per kasus dan per klausul adalah grain berbeda.
3. **Regional** — Balai pelaksana berbeda dari lokasi fisik sarana.

---

## 3. Pertanyaan tambahan yang muncul dari diskusi user

### Observasi/temuan

- Masalah penyimpanan apa yang paling sering ditemukan?
- SOP apa yang paling sering tidak dijalankan?
- Apa alasan TMK yang paling sering muncul?
- Temuan apa yang terus berulang pada sarana yang sama?

### Severity dan keputusan

- Apakah severity sejalan dengan rekomendasi?
- Apakah kasus Kritis mendapat tindak lanjut yang lebih keras?
- Apakah keputusan Balai dan Pusat konsisten?
- UPT mana yang paling sering mendapat koreksi?

### Workflow

- Kasus apa yang tertahan di Pusat?
- Berapa lama setiap tahap verifikasi?
- Di tahap mana backlog paling besar?

### Antibiotik

- Antibiotik apa yang paling banyak dijual tanpa resep?
- Sarana mana dengan proporsi penjualan tanpa resep tertinggi?
- Apakah pencatatan/pelaporan antibiotik dipenuhi?
- Apa tindak lanjut untuk ketidaksesuaian antibiotik?

### Free text

- Ringkas catatan panjang menjadi temuan utama.
- Kelompokkan topik masalah.
- Hubungkan narasi dengan severity, kesimpulan, dan rekomendasi.
- Tampilkan bukti teks asli dari setiap insight.

### Reporting

- Apa temuan utama bulan ini?
- Apa perubahan dari periode sebelumnya?
- Apa isu prioritas untuk pimpinan?
- Apa rekomendasi kebijakan berdasarkan data?

---

## 4. Pertanyaan yang harus diklarifikasi sebelum query

| Bahasa user | Klarifikasi yang diperlukan |
|---|---|
| “temuan” | checklist, observasi, produk bermasalah, atau alasan TMK? |
| “wilayah” | Balai pelaksana, regional Balai, atau lokasi sarana? |
| “jumlah” | kasus, sarana unik, item, produk, kuantitas, atau penugasan? |
| “tren” | tren kasus, item tidak sesuai, persentase kepatuhan, atau TMK? |
| “kritis” | level kasus atau severity per klausul? |
| “tindak lanjut” | saran, CAPA, tindakan produk, narasi, atau approval? |
| “selesai” | FINISHED, FINISHED_PUSAT, atau tahapan tertentu? |
| “inspektur terbaik” | volume penugasan, eksposur, atau kompetensi formal? |

---

## 5. Template dokumentasi kebutuhan per pertanyaan

Setiap pertanyaan baru sebaiknya dicatat dengan format:

| Elemen | Isi |
|---|---|
| Pertanyaan natural/verbatim | bahasa user |
| Persona | siapa yang bertanya |
| Tujuan keputusan | keputusan apa yang hendak dibuat |
| Intent | monitoring/kepatuhan/risiko/TL/evaluasi/pola/report |
| Entitas | pemeriksaan/sarana/petugas/item/temuan produk |
| Grain | apa yang dihitung |
| Scope | periode/UPT/lokasi/jenis sarana/komoditi |
| Metric | definisi angka |
| Data route | fact/bridge/dim |
| Status | ready/rule/decision/unavailable |
| Bentuk output | angka/tabel/chart/narasi/evidence |
| Batas | coverage, kualitas, disclaimer |

---

## 6. Yang bukan sumber kebutuhan

256 prompt di `docs/testcase/` adalah corpus generated/historis. Ia dapat membantu:

- regresi teknis;
- melihat variasi istilah;
- menemukan anti-trap.

Tetapi tidak boleh digunakan untuk menyimpulkan:

- frekuensi pertanyaan user;
- prioritas bisnis;
- ekspektasi stakeholder;
- definisi metrik;
- daftar kebutuhan final.

Question-space utama harus berasal dari persona, pekerjaan, keputusan, sembilan pertanyaan fondasi, dan diskusi user yang didokumentasikan di blueprint ini.
