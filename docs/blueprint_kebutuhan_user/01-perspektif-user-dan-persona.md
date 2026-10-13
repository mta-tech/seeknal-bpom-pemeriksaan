# 01 — Perspektif User dan Persona

> Fokus file ini bukan tabel database, tetapi **siapa user-nya, apa pekerjaan mereka, keputusan apa yang dibuat, dan informasi seperti apa yang dibutuhkan**.

---

## 1. Perspektif user dalam satu paragraf

Tim Wasdis membutuhkan cara untuk menelusuri seluruh siklus pemeriksaan—mulai dari objek dan petugas pemeriksa, kondisi lapangan, ketidaksesuaian, tingkat risiko, kesimpulan, rekomendasi, sampai evaluasi UPT dan Pusat—kemudian mengubahnya menjadi laporan dan insight yang dapat ditanyakan menggunakan bahasa kerja sehari-hari. Kebutuhan pelaporan berubah menurut stakeholder, periode, komoditi, wilayah, dan isu seperti penyimpanan atau antibiotik. Tantangannya bukan sekadar menemukan tabel, tetapi memahami bahwa setiap jenis sarana memakai bentuk form, grain, dan definisi temuan yang berbeda.

Dengan kata lain, user tidak hanya meminta:

> “Tolong tampilkan data.”

Mereka membutuhkan:

> “Tolong pahami proses pemeriksaannya, jelaskan kondisi yang ditemukan, hubungkan tingkat risikonya dengan tindak lanjut, dan sajikan dalam bentuk yang sesuai untuk saya.”

---

## 2. Persona 1 — Petugas / Operator UPT

### Pekerjaan yang dilakukan

- membuat entri pemeriksaan;
- memilih sarana, jenis sarana, komoditi, Balai, periode, dan petugas;
- mengisi checklist atau skor aspek;
- menulis catatan observasi;
- memasukkan temuan produk;
- memberi kesimpulan dan rekomendasi awal;
- mengunggah identitas dokumen tindak lanjut;
- mengirim kasus ke tahap verifikasi.

### Pertanyaan yang mereka butuhkan

- Kasus apa yang masih draft atau dikembalikan?
- Sarana mana yang harus ditindaklanjuti?
- Apa temuan utama pada sarana ini?
- Apa rekomendasi sebelumnya?
- Apakah sarana ini pernah memiliki temuan yang sama?
- Apakah tindak lanjut/CAPA sudah lengkap?
- Kasus mana yang belum bergerak ke tahap berikutnya?

### Keputusan yang ingin dibuat

- apakah data sudah cukup untuk dikirim;
- apakah ketidaksesuaian sudah dijelaskan dengan benar;
- tindak lanjut apa yang harus dilakukan;
- kasus mana yang perlu diprioritaskan.

### Bentuk output yang berguna

- daftar operasional per kasus;
- status dan tindak lanjut;
- ringkasan temuan satu sarana;
- riwayat pemeriksaan sarana;
- checklist kelengkapan entry.

### Batas data yang perlu diketahui

- edit menimpa nilai lama; tidak ada version history;
- isi file lampiran tidak ada di database, hanya ID;
- status TTE tidak direkam sebagai field;
- bentuk form berbeda menurut jenis sarana.

---

## 3. Persona 2 — Supervisor / Kepala Balai

### Pekerjaan yang dilakukan

- memverifikasi hasil pemeriksaan;
- mengecek kesesuaian observasi, severity, kesimpulan, dan rekomendasi;
- meminta revisi jika hasil belum memadai;
- memfinalkan hasil Balai;
- memantau beban kasus dan produktivitas UPT.

### Pertanyaan yang mereka butuhkan

- Apakah kesimpulan TMK didukung oleh temuan yang cukup?
- Apakah severity yang diberikan konsisten dengan kondisi lapangan?
- Kasus apa yang paling lama belum selesai?
- Siapa petugas yang menangani jenis sarana tertentu?
- Temuan apa yang dominan di wilayah kerja kami?
- Sarana mana yang mengalami ketidaksesuaian berulang?
- Rekomendasi apa yang paling sering diberikan?

### Keputusan yang ingin dibuat

- menerima atau mengembalikan hasil operator;
- menentukan prioritas pembinaan;
- membagi penugasan inspektur;
- menentukan fokus pemeriksaan berikutnya;
- menilai kebutuhan eskalasi ke Pusat.

### Bentuk output yang berguna

- dashboard status kasus;
- daftar kasus berisiko tinggi;
- tren aspek/klausul per UPT;
- matriks petugas × jenis sarana;
- daftar sarana berulang;
- ringkasan rekomendasi dan CAPA.

### Batas data yang perlu diketahui

- jumlah penugasan tidak sama dengan jumlah pemeriksaan;
- data dapat menunjukkan eksposur petugas, bukan kompetensi formal;
- “wilayah” harus dibedakan antara UPT pelaksana dan lokasi sarana;
- satu metrik temuan tidak berlaku untuk seluruh varian form.

---

## 4. Persona 3 — Evaluator Pusat

### Pekerjaan yang dilakukan

- mengevaluasi hasil final Balai;
- menilai apakah severity, kesimpulan, dan rekomendasi proporsional;
- membandingkan pola antar-UPT;
- memberi koreksi atau justifikasi Pusat;
- memantau konsistensi penerapan kebijakan.

### Pertanyaan yang mereka butuhkan

- Apakah kesimpulan Balai dan Pusat berbeda?
- UPT mana yang paling sering mendapat revisi?
- Apakah kasus dengan severity serupa mendapat tindak lanjut serupa?
- Rekomendasi keras paling sering diberikan untuk kondisi apa?
- Di tahap mana kasus paling banyak tertahan?
- Berapa lama kasus bergerak dari Balai ke Pusat?
- Apa pola nasional untuk isu tertentu, misalnya penyimpanan atau antibiotik?

### Keputusan yang ingin dibuat

- mempertahankan atau mengoreksi kesimpulan Balai;
- menyelaraskan standar antar-UPT;
- menentukan isu prioritas nasional;
- meminta perbaikan kualitas entry/data;
- memberi arahan kebijakan.

### Bentuk output yang berguna

- perbandingan Balai vs Pusat;
- distribusi revisi antar-UPT;
- matriks severity × rekomendasi;
- funnel workflow;
- laporan hotspot nasional;
- daftar kasus bukti (evidence cases).

### Batas data yang perlu diketahui

- review Pusat memang parsial; `kesimpulan_pusat_id` mayoritas NULL;
- edit menimpa nilai lama, sehingga semua versi keputusan tidak dapat direkonstruksi;
- hubungan severity→rekomendasi tersedia di level kasus, belum selalu di level klausul;
- hubungan yang terlihat adalah asosiasi, bukan otomatis sebab-akibat.

---

## 5. Persona 4 — Pimpinan

### Pekerjaan yang dilakukan

- membaca ringkasan kondisi nasional/organisasi;
- menentukan prioritas dan kebijakan;
- meminta analisis isu tertentu;
- membandingkan kondisi antar-periode dan wilayah;
- memantau penyelesaian kasus berisiko.

### Pertanyaan yang mereka butuhkan

- Apa temuan utama periode ini?
- Apakah kondisi membaik atau memburuk?
- Regional/UPT mana yang paling berisiko?
- Apa kasus kritis yang belum selesai?
- Apa isu yang memerlukan kebijakan atau pembinaan?
- Apa perubahan dibanding periode sebelumnya?
- Apa rekomendasi berbasis data?

### Keputusan yang ingin dibuat

- fokus pengawasan;
- prioritas sumber daya;
- arahan pembinaan;
- eskalasi isu;
- kebijakan lintas wilayah/komoditi.

### Bentuk output yang berguna

- satu halaman ringkasan;
- chart tren;
- hotspot;
- daftar isu prioritas;
- rekomendasi dan dasar buktinya;
- lampiran evidence jika perlu audit.

### Batas data yang perlu diketahui

- angka nasional harus menyebut grain dan coverage;
- pelayanan dan produksi tidak boleh digabung mentah;
- beberapa aspek hanya tersedia pada subset jenis sarana;
- free-text insight harus membawa bukti kasus.

---

## 6. Persona 5 — Analis / Tim Data / Pengembang AI

### Pekerjaan yang dilakukan

- menerjemahkan bahasa user menjadi konsep bisnis;
- menentukan grain dan metrik;
- memilih fact/bridge/dim;
- menerapkan aturan join dan routing;
- memvalidasi coverage dan kualitas;
- menyajikan jawaban dengan disclaimer yang tepat;
- membangun context, skill, dan testcase.

### Pertanyaan yang harus dijawab sebelum query

1. Apa intent user?
2. Apa entitas dan grain yang dihitung?
3. Jenis sarana/populasinya apa?
4. Varian form mana yang relevan?
5. Definisi metriknya apa?
6. Tabel bridge mana yang benar?
7. Apakah data mencakup seluruh populasi?
8. Apa bentuk output yang diharapkan?
9. Bukti apa yang harus disertakan?

### Tanggung jawab utama

- tidak memakai nama kolom sebagai pengganti definisi bisnis;
- tidak menganggap `no`, `score`, atau “temuan” punya satu arti global;
- tidak mengubah korelasi menjadi klaim sebab-akibat;
- tidak mengarang data yang tidak tersedia;
- menjaga setiap insight tetap dapat diaudit.

---

## 7. Hubungan antar-persona

```text
Petugas UPT
  entry observasi/temuan/rekomendasi
        ↓
Supervisor / Kepala Balai
  verifikasi dan finalisasi awal
        ↓
Evaluator Pusat
  cek konsistensi dan evaluasi
        ↓
Pimpinan
  menerima ringkasan dan mengambil keputusan

Analis / Data / AI
  menjadi jembatan bahasa dan data di seluruh tahapan
```

Satu dataset yang sama menghasilkan output berbeda:

| Persona | Detail yang dibutuhkan |
|---|---|
| Operator | per kasus dan per field |
| Supervisor | per kasus + pembanding UPT |
| Pusat | antar-UPT + konsistensi keputusan |
| Pimpinan | agregat, tren, hotspot, rekomendasi |
| Data/AI | grain, route, rule, coverage, evidence |

---

## 8. Narasi kebutuhan utama

> User membutuhkan sistem yang memahami proses pemeriksaan, bukan sekadar nama tabel. Sistem harus dapat menghubungkan kondisi lapangan dengan severity, kesimpulan, rekomendasi, workflow, dan laporan; memahami istilah kerja user; memilih data yang sesuai dengan jenis form; serta menjelaskan batas data dan bukti asalnya.
