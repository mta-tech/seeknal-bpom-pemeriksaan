# 02 — Proses Bisnis dan Entry User

> File ini menjelaskan **apa yang user lakukan di setiap tahap, data apa yang terbentuk, makna bisnisnya, insight yang dimungkinkan, dan batas datanya**.

---

## 1. Rantai bisnis pemeriksaan

```text
Objek/sarana
→ standar atau SOP
→ kondisi nyata di lapangan
→ observasi / ketidaksesuaian
→ tingkat keparahan
→ kesimpulan kasus
→ rekomendasi dan tindak lanjut
→ verifikasi UPT
→ evaluasi Pusat
→ laporan dan keputusan
```

Satu pemeriksaan tidak sama dengan satu baris detail:

```text
1 pemeriksaan
├── 1 sarana
├── 1 balai
├── 1 periode
├── N petugas
├── N item skor/checklist
├── N temuan produk
├── N narasi
└── N event approval
```

Pusatnya adalah `fact_pemeriksaan`: 1 baris = 1 kasus. Detailnya berada di fact/bridge lain.

---

## 2. FLOW 1 — Entri Baru

### User melakukan

- memilih jenis sarana dan komoditi;
- memilih nama sarana;
- menentukan Balai/UPT;
- memasukkan nomor dan tanggal surat tugas;
- memilih petugas pemeriksa;
- menentukan versi formulir bila tersedia.

### Data yang terbentuk

| Entry user | Data `staging` | Makna bisnis |
|---|---|---|
| Jenis sarana | `fact_pemeriksaan.jenis_id` → `JENIS_SARANA` | jenis objek yang diperiksa |
| Komoditi | `klasifikasi_id` → `JENIS_KLASIFIKASI` | kelompok produk/domain |
| Sarana | `sarana_id` → `dim_sarana` | identitas dan lokasi objek |
| Balai/UPT | `balai_id` → `dim_balai` | pelaksana pemeriksaan |
| Surat tugas | `no_surat`, `tgl_surat` | dasar administratif |
| Petugas | `bridge_pemeriksaan_petugas` | siapa yang terlibat |
| Versi form | `form_version_id` | versi formulir, tetapi hanya ±29% terisi |

### Insight yang dimungkinkan

- jumlah pemeriksaan per Balai/periode;
- pemeriksaan per jenis sarana/komoditi;
- beban penugasan petugas;
- persebaran lokasi sarana;
- pengalaman petugas menurut jenis sarana.

### Batas data

- satu kasus dapat memiliki banyak petugas;
- `COUNT(*)` pada bridge petugas = jumlah penugasan, bukan jumlah pemeriksaan;
- versi form terlalu tipis untuk dijadikan routing utama;
- “wilayah Balai” berbeda dari lokasi fisik sarana.

---

## 3. FLOW 2 — Informasi Pemeriksaan

### User melakukan

- memilih tanggal mulai dan selesai;
- memilih tujuan pemeriksaan;
- menjawab apakah ada kasus/temuan produk;
- memilih metode inspeksi bila digunakan.

### Data yang terbentuk

| Entry user | Data `staging` | Kondisi |
|---|---|---|
| Tanggal | `tgl_start`, `tgl_end` | 99,6% terisi |
| Tujuan | `tujuan_id` | 99,6% terisi |
| Ada kasus/produk bermasalah | hadir/tidaknya `bridge_pemeriksaan_temuan` | 31.959 kasus punya temuan produk |
| Metode inspeksi | `metode_inspeksi` | hanya ±1,6% terisi |

### Insight yang dimungkinkan

- tren pemeriksaan;
- pemeriksaan rutin vs intensifikasi/kasus;
- produktivitas per periode;
- proporsi kasus dengan temuan produk.

### Batas data

- metode inspeksi tidak representatif untuk seluruh populasi;
- tanggal kosong pada 963 kasus;
- pertanyaan “ada temuan?” tidak menjelaskan jenis temuan—bisa berbeda dari temuan checklist.

---

## 4. FLOW 3 — Inspeksi Varian Pelayanan

### User melakukan

Untuk Apotek, PKM, Klinik, Toko Obat, dan Rumah Sakit, user mengisi aspek:

- Pengadaan;
- Penerimaan;
- Penyimpanan;
- Penyaluran/Pendistribusian;
- Penyerahan;
- Pengembalian;
- Pencatatan dan Pelaporan;
- Pemusnahan.

### Data yang terbentuk

```text
bridge_pemeriksaan_skor_operasional
├── area_key
├── opsi
├── n
├── fp
└── score
        │
        └── dim_pemeriksaan_aspek
```

Cakupan: sekitar 1,52 juta baris untuk 63,8 ribu kasus.

### Variasi nyata

`opsi` dapat berisi:

```text
yes / no / mostly / rarely / N/A
apoteker / ttk / Apoteker atau TTK
{"mutasi":"yes"}
```

`score` dapat berupa:

```text
0 / 25 / 50 / 75 / 100
atau nilai akumulasi >100
```

### Makna bisnis

- sebagian field menyatakan kepatuhan;
- sebagian field menyatakan orang/peran;
- sebagian field menyimpan pilihan prosedur;
- sebagian field merupakan object terstruktur.

### Insight yang dimungkinkan

- kepatuhan per aspek;
- tren item tidak sesuai;
- perbandingan antar-jenis sarana/UPT;
- area yang memerlukan pembinaan.

### Batas data

- `opsi='no'` tidak boleh menjadi definisi temuan global;
- score tidak boleh dirata-rata mentah tanpa memahami skala;
- Penerimaan/Pengembalian belum memiliki label resmi di `ASPEK_KTL`;
- definisi temuan harus dibuat per `area_key`.

---

## 5. FLOW 3B — Inspeksi Varian Produksi

### User melakukan

Pada sarana produksi, user mengisi klausul bertingkat, misalnya:

```text
Penyimpanan
└── Gudang
    └── A3
        └── P1
            ├── Tidak
            ├── catatan: monitoring suhu tidak tersedia
            └── severity: Major
```

### Data yang terbentuk

```text
bridge_pemeriksaan_checklist
├── path
├── nilai_aspek
├── catatan
└── conformity
```

Cakupan: sekitar 7,39 juta item checklist.

### Variasi `nilai_aspek`

```text
Ya / Tidak
OK / Tidak Berlaku
B / T / C / K
Minor / Major / Kritis / Serius / Kritikal
Lanjut
```

Satu kolom mencampur:

- hasil kepatuhan;
- grade/kode penilaian;
- severity;
- status tindak lanjut.

### Insight yang dimungkinkan

- jumlah klausul tidak sesuai;
- severity per jenis sarana;
- catatan pelanggaran;
- temuan berulang pada sarana yang sama;
- pola aspek tertentu jika `path` dapat dipetakan.

### Batas data

- tidak semua `path` bisa dipetakan ke aspek resmi;
- severity per klausul tidak tersedia untuk semua jenis sarana;
- data pelayanan dan produksi berbeda satuan dan tidak boleh dijumlahkan mentah;
- 2.610 kasus Kosmetik CPKB belum memiliki bridge detail.

---

## 6. Varian Khusus dalam FLOW 3B

### Observasi GMP

```text
bridge_pemeriksaan_temuan_observasi
├── observasi_kode
├── kriteria
└── catatan
```

- kode observasi dapat diterjemahkan;
- `kriteria` masih berupa angka 1–4 yang artinya belum dikonfirmasi.

### Vaksin

```text
bridge_pemeriksaan_vaksin
├── section_key
├── opsi
├── jumlah
├── observasi
├── perbaikan
└── intervensi
```

- 19 section vaksin;
- cukup kaya untuk analisis program vaksin;
- belum memiliki kamus label aspek formal.

### Narasi Faskes

```text
bridge_pemeriksaan_narasi_faskes
├── section
└── teks
```

Section: profil, personalia, pengadaan, penyimpanan, distribusi, dokumentasi, gudang, lain.

- cocok untuk NLP/ringkasan;
- tidak dapat langsung dihitung sebagai item ketidaksesuaian.

### Profil Pangan MD/Faskes

- profil sarana, skala usaha, personel, sertifikat, kapasitas;
- mendukung konteks kasus dan segmentasi sarana.

---

## 7. FLOW 4 — Hasil Inspeksi dan Tindak Lanjut

### User melakukan

- memberi kesimpulan MK/TMK/TTP/TDP;
- memberi grade;
- mencatat Minor/Major/Kritis;
- memasukkan temuan produk;
- memberi rekomendasi/tindak lanjut/CAPA;
- menulis catatan dan analisis;
- mengunggah identitas lampiran.

### Data yang terbentuk

| Entry user | Data `staging` | Makna |
|---|---|---|
| Kesimpulan | `kesimpulan_balai_id` | vonis kasus |
| Grade | `grade` | kualitas sarana produksi |
| Severity | `kritis_count`, `major_count`, `minor_count`, `level_kesimpulan` | risiko per kasus |
| Temuan produk | `bridge_pemeriksaan_temuan` | produk/kategori/tindakan/kuantitas/nilai |
| Narasi | `fact_pemeriksaan_narasi` | alasan, hasil, rekomendasi, analisis |
| CAPA | `tl_capa` | tindak lanjut korektif, teks bebas |
| Lampiran | `tl_attachment`, `tl_ba` | hanya ID file |

### Insight yang dimungkinkan

- proporsi MK/TMK;
- kasus kritis;
- kategori produk bermasalah;
- rekomendasi dominan;
- hubungan severity dan tindak lanjut;
- alasan TMK dari narasi;
- kasus yang belum menyelesaikan CAPA.

### Batas data

- severity dan rekomendasi belum selalu terhubung sampai level klausul;
- jumlah produk, baris temuan, kasus, dan nilai ekonomi adalah grain berbeda;
- kuantitas/nilai sangat besar perlu rule kualitas;
- isi lampiran tidak tersedia;
- narasi perlu NLP dan evidence trace.

---

## 8. FLOW 5 — Edit

### User melakukan

- memperbaiki data atau hasil setelah revisi.

### Kondisi data

- perubahan memperbarui kasus yang sama;
- `updated_at`/`updated_by` tersedia;
- nilai lama tidak tersimpan sebagai version history.

### Dampak kebutuhan

Bisa:

- mengetahui kapan terakhir diubah;
- mengetahui siapa terakhir mengubah.

Tidak bisa:

- melihat isi sebelum dan sesudah edit;
- merekonstruksi seluruh perubahan keputusan.

---

## 9. FLOW 6–7 — Kirim dan Verifikasi

### User melakukan

```text
Operator UPT
→ Supervisor
→ Kepala Balai
→ Operator Pusat
→ Supervisor Pusat
→ Direktur
```

### Data yang terbentuk

- status terakhir di `fact_pemeriksaan.status_id`;
- jejak event di `fact_pemeriksaan_approval`;
- catatan verifikator di `notes`/`notes_tl`;
- kesimpulan/tindak lanjut Balai dan Pusat.

### Insight yang dimungkinkan

- funnel workflow;
- bottleneck;
- durasi antar-tahap;
- kasus yang direvisi;
- perbedaan hasil Balai dan Pusat;
- konsistensi rekomendasi antar-UPT.

### Kondisi nyata

- VERIFY4 mendominasi sekitar 64%;
- FINISHED sekitar 11%;
- menunjukkan bottleneck besar pada jalur verifikasi Pusat.

### Batas data

- review Pusat parsial;
- status TTE tidak tersedia;
- edit dapat menghapus jejak nilai keputusan sebelumnya;
- event approval menjelaskan perpindahan, tidak selalu isi keputusan sebelum/sesudah.

---

## 10. Dari entry menjadi laporan

```text
Entry user
→ data operasional
→ semantic/metric rules
→ agregasi/analisis
→ validasi coverage
→ output sesuai persona
```

Contoh:

| Entry | Kebutuhan laporan |
|---|---|
| Checklist Penyimpanan | tren ketidaksesuaian penyimpanan |
| Severity | kasus kritis & tindak lanjut |
| Petugas | eksposur penugasan inspektur |
| Temuan produk | kategori dominan & nilai ekonomi |
| Approval | bottleneck & revisi |
| Narasi | alasan TMK & topik masalah |
| Data antibiotik | volume tanpa resep & kepatuhan pencatatan |

Data tidak otomatis menjadi laporan. Ia membutuhkan definisi bisnis, grain, route, dan bentuk output yang disepakati.
