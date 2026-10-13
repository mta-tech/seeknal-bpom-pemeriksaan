# 07 — Use Case dan Bentuk Output

> Setiap use case menjelaskan **pertanyaan user → maksud bisnis → data → interpretasi → output → batas jawaban**.

---

## Case 1 — Kepala Balai: tren ketidaksesuaian Penyimpanan

### Pertanyaan natural

> Bagaimana tren ketidaksesuaian Penyimpanan selama 2024–2025?

### Maksud bisnis

- apakah masalah penyimpanan membaik atau memburuk;
- jenis sarana mana yang paling bermasalah;
- apa tema ketidaksesuaiannya;
- apa yang harus diprioritaskan.

### Langkah interpretasi

1. Klarifikasi/populasi: pelayanan, produksi, atau keduanya?
2. Jangan gabungkan satuannya.
3. Pelayanan → rule skor per `area_key` Penyimpanan.
4. Produksi → checklist path Penyimpanan + nilai Tidak/severity.
5. Narasi → topik masalah dengan evidence.

### Data

```text
Pelayanan: bridge_pemeriksaan_skor_operasional
Produksi: bridge_pemeriksaan_checklist
Konteks: fact_pemeriksaan + jenis sarana + Balai
Narasi: catatan checklist / fact_pemeriksaan_narasi
```

### Output yang direkomendasikan

**Panel A — Pelayanan**

| Tahun | Jenis sarana | Kasus | Item dinilai | Proporsi tidak sesuai |

**Panel B — Produksi**

| Tahun | Jenis sarana | Klausul | Tidak sesuai | Minor | Major | Kritis |

**Panel C — Tema narasi**

| Topik | Kasus | Evidence contoh | Severity dominan |

### Batas

- tidak semua jenis sarana punya severity;
- `opsi='no'` tidak boleh dipakai global;
- narasi tidak boleh dihitung sebagai klausul.

---

## Case 2 — Tim kompetensi: eksposur inspektur

### Pertanyaan natural

> Siapa inspektur yang paling banyak menangani sarana distribusi obat, dan jenis sarana apa yang sering mereka periksa?

### Maksud bisnis

- melihat distribusi penugasan;
- mengetahui eksposur/pengalaman;
- merencanakan pembinaan atau rotasi.

### Data

```text
bridge_pemeriksaan_petugas
→ fact_pemeriksaan
→ dim_user
→ JENIS_SARANA / komoditi / Balai
```

### Kontrak metrik

```text
Jumlah kasus = COUNT(DISTINCT pemeriksaan_id)
Jumlah penugasan = COUNT(*) bridge petugas
```

### Output

| Inspektur | Golongan | Jenis sarana | Komoditi | Kasus unik | Penugasan | Balai |

### Bahasa yang aman

> “Inspektur X memiliki eksposur penugasan tertinggi pada…”

Bukan:

> “Inspektur X paling kompeten.”

### Batas

- tidak ada data sertifikasi/kompetensi formal;
- `urutan` petugas bukan bukti peran keputusan;
- kompleksitas kasus perlu konteks severity.

---

## Case 3 — Pusat: kategori temuan dominan per regional

### Pertanyaan natural

> Kategori temuan produk apa yang paling dominan di setiap regional?

### Maksud bisnis

- menentukan fokus regional;
- melihat hotspot produk TIE/rusak/kedaluwarsa;
- menyusun prioritas pengawasan.

### Data

```text
bridge_pemeriksaan_temuan
→ fact_pemeriksaan
→ dim_balai.regional_name
→ expand kategori_kode
→ KATEGORI_TEMUAN_PRODUK
```

### Output

| Regional | Kategori | Kasus terdampak | Baris temuan | Porsi regional |

### Batas

- regional Balai ≠ lokasi sarana;
- kasus/baris/kuantitas berbeda;
- draft harus dikeluarkan;
- kategori yang tidak match kamus perlu bucket “tidak terpetakan”.

---

## Case 4 — Evaluator Pusat: severity vs rekomendasi UPT

### Pertanyaan natural

> Apakah rekomendasi yang diberikan UPT sudah proporsional dengan tingkat temuan?

### Maksud bisnis

- menjaga konsistensi keputusan;
- menemukan kasus yang terlalu ringan/keras;
- menyelaraskan standar antar-UPT.

### Data

```text
Severity kasus/klausul
+ kesimpulan Balai
+ tl_saran/CAPA/narasi rekomendasi
+ kesimpulan/TL Pusat
+ approval
```

### Langkah analisis

1. Sepakati matriks severity→tindakan yang diharapkan.
2. Ambil kasus dengan severity dan rekomendasi terisi.
3. Bandingkan dengan keputusan Pusat bila ada.
4. Flag outlier, jangan langsung menyatakan salah.
5. Sertakan evidence kasus.

### Output

| Pemeriksaan | Severity | Kesimpulan Balai | Rekomendasi UPT | Evaluasi Pusat | Status | Evidence |

### Status kesiapan

**Butuh keputusan bisnis**: rule proporsionalitas resmi belum terdokumentasi.

### Batas

- review Pusat parsial;
- edit menimpa nilai lama;
- severity belum universal;
- asosiasi bukan kausalitas.

---

## Case 5 — Pimpinan: laporan bulanan nasional

### Pertanyaan natural

> Apa kondisi utama pemeriksaan bulan ini dan apa yang perlu diprioritaskan?

### Isi report

1. volume kasus dan coverage;
2. MK/TMK dan severity;
3. hotspot regional/jenis sarana;
4. kategori temuan produk dominan;
5. backlog workflow;
6. kasus kritis belum selesai;
7. rekomendasi berbasis pola;
8. batas data.

### Bentuk output

```text
Ringkasan 5 poin
+ 4–6 chart utama
+ tabel hotspot
+ daftar kasus prioritas
+ evidence appendix
```

### Prinsip

- tidak membanjiri pimpinan dengan detail klausul;
- setiap rekomendasi punya dasar;
- perubahan dibanding periode sebelumnya memakai metrik yang sama;
- coverage dinyatakan.

---

## Case 6 — Tim antibiotik: penyerahan tanpa resep

### Pertanyaan natural

> Antibiotik apa yang paling banyak dijual tanpa resep, di sarana mana, dan apakah pencatatannya sesuai?

### Data yang dibutuhkan

- nama zat aktif;
- jumlah penjualan;
- jumlah tanpa resep;
- satuan;
- pihak penyerah;
- penerima/KIE;
- pencatatan mutasi;
- jenis sarana/Balai/periode;
- temuan dan tindak lanjut.

### Kondisi

- sekitar 25.780 kasus memiliki detail `tx_fast_moving_antibiotika` pada entry form;
- data zat aktif/volume belum menjadi bridge khusus di `staging`;
- sebagian kepatuhan antibiotik sudah ada di Penyerahan/Pencatatan.

### Output ideal

| Zat aktif | Sarana | UPT | Penjualan | Tanpa resep | Proporsi | Kepatuhan pencatatan | TL |

### Status

**Belum siap penuh**. Perlu bridge antibiotik khusus.

---

## Case 7 — Analis: temuan berulang pada sarana yang sama

### Pertanyaan natural

> Sarana mana yang mengalami ketidaksesuaian yang sama berulang kali, dan apakah tindak lanjut sebelumnya efektif?

### Maksud bisnis

- menemukan repeat offender;
- menilai efektivitas pembinaan/CAPA;
- menentukan inspeksi berbasis risiko.

### Data

```text
sarana_id
+ beberapa pemeriksaan sepanjang waktu
+ aspek/klausul/kategori temuan
+ severity
+ TL/CAPA
+ kesimpulan
```

### Output

| Sarana | Temuan/topik | Jumlah kejadian | Periode | Severity terakhir | TL sebelumnya | Kondisi terakhir |

### Batas

- istilah “temuan sama” perlu normalisasi kode/topik;
- edit history tidak tersedia;
- efektivitas diukur dari pemeriksaan berikutnya, bukan perubahan internal satu kasus.

---

## Case 8 — AI: free text menjadi insight dengan bukti

### Pertanyaan natural

> Ringkas alasan TMK dan kelompokkan masalah yang paling sering muncul.

### Proses

```text
narasi/catatan
→ bersihkan HTML/karakter
→ klasifikasi topik
→ ringkas per kasus
→ hubungkan severity/kesimpulan/TL
→ agregasi topik
→ evidence drill-down
```

### Output

| Topik | Kasus | Severity dominan | Rekomendasi dominan | Evidence contoh |

Contoh evidence:

| Pemeriksaan | Potongan teks | Sarana | UPT | Tanggal |

### Aturan

- satu insight selalu punya sumber;
- confidence/status review dicatat;
- tidak mengarang severity;
- narasi bukan otomatis satu item temuan.

---

## Case 9 — Operasional: backlog verifikasi

### Pertanyaan natural

> Kasus apa yang paling lama tertahan dan berada di tahap mana?

### Data

- status kasus;
- event approval;
- waktu event;
- Balai/jenis sarana;
- severity/kesimpulan bila ada.

### Output

| Tahap | Kasus | Median usia | Kasus tertua | UPT dominan |

Drill-down:

| Pemeriksaan | Sarana | UPT | Tahap | Hari tertahan | Severity | TL |

### Nilai bisnis

- mengurangi backlog;
- prioritas kasus berisiko;
- menemukan bottleneck proses.

---

## 10. Template use case baru

```markdown
## Case — [nama]

### Persona
### Pertanyaan natural
### Keputusan yang ingin dibuat
### Intent
### Entity/grain
### Scope
### Data route
### Metric contract
### Bentuk output
### Coverage
### Batas/anti-trap
### Evidence yang wajib
### Status kesiapan
```
