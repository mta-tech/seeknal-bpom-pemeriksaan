# 06 — Kontrak Metrik dan Aturan Jawaban

> Kontrak metrik adalah jembatan bisnis–teknis: **apa yang dihitung, pada grain apa, dari data mana, dengan filter apa, dan batas interpretasinya apa**.

---

## 1. Urutan wajib sebelum membuat query

```text
1. Tentukan intent
2. Tentukan entity dan grain
3. Tentukan scope/populasi
4. Tentukan varian form
5. Pilih definisi metrik
6. Pilih fact/bridge/dim
7. Terapkan filter wajib
8. Validasi coverage & kualitas
9. Pilih bentuk output
10. Sertakan evidence & batas jawaban
```

Query pendek tetap salah bila grain atau definisinya salah.

---

## 2. Kontrak metrik inti

| Konsep | Definisi aman | Data | Filter/rule | Jangan dilakukan |
|---|---|---|---|---|
| Jumlah pemeriksaan | kasus unik | `fact_pemeriksaan` | `COUNT(DISTINCT id)` | menghitung dari baris bridge |
| Sarana unik | objek sarana unik | fact + `dim_sarana` | `COUNT(DISTINCT sarana_id)` | menyamakan dengan kasus |
| Penugasan petugas | satu petugas×kasus | bridge petugas | `COUNT(*)` | menyebutnya jumlah pemeriksaan |
| Kasus per inspektur | kasus unik per user | bridge petugas | `COUNT(DISTINCT pemeriksaan_id)` | menilai kompetensi formal |
| Kepatuhan pelayanan | rule per `area_key` | bridge skor | normalisasi opsi/score per field | global `opsi='no'` atau `AVG(score)` |
| Klausul tidak sesuai | item `Tidak` | bridge checklist | route varian + nilai sesuai intent | campur dengan skor pelayanan |
| Severity kasus | counter/level kasus | fact | coverage subset | menyebut mewakili seluruh kasus |
| Severity klausul | item Minor/Major/Kritis/Serius/Kritikal | checklist | jenis sarana tertentu | gabung dengan counter kasus |
| Temuan produk—kasus | kasus terdampak | bridge temuan | `COUNT(DISTINCT pemeriksaan_id)`, draft=false | menyebut jumlah fisik produk |
| Temuan produk—baris | entry produk | bridge temuan | `COUNT(*)` | menyebut jumlah kasus |
| Temuan produk—kuantitas | jumlah fisik | `SUM(jumlah_temuan)` | quality guard/outlier note | memakai mentah tanpa disclaimer |
| Nilai ekonomi | harga total | `SUM(harga_total)` | quality guard | menganggap seluruh nilai comparable |
| Regional | kelompok Balai | `regional_name` | jangan kode `regional` | menyebut lokasi sarana |
| Lokasi sarana | provinsi/kabupaten objek | `dim_sarana` | join wilayah | menyebut UPT pelaksana |
| MK/TMK | kesimpulan kasus | dim kesimpulan | FK join | menyamakan dengan severity |
| Grade | klasifikasi produksi | `grade` | subset produksi | menyebut semua sarana |
| Workflow selesai | status akhir | status code | definisikan FINISHED/FINISHED_PUSAT | hanya satu kode tanpa scope |
| Kasus komoditi NPP | kasus ber-klasifikasi NPP | `fact_pemeriksaan.klasifikasi_id` → `JENIS_KLASIFIKASI` | wajib `type`; rentang tanggal eksplisit | mencampur dengan grain distribusi |
| Kasus distribusi yang mengelola komoditi X | kasus unik pada bridge | `bridge_pemeriksaan_komoditi_pbf` / `fokus_pbf` | join `master_data_id::text` + `type`; `COUNT(DISTINCT pemeriksaan_id)` | menganggap hanya PBF; menjumlah antar grain |
| Temuan obat keras / BKO | baris/kasus kategori kode raw | `bridge_pemeriksaan_temuan.kategori_kode` | expand jsonb; kanonik alias; bucket residu; draft=false | join kamus via `code`; membuang residu diam-diam |
| Asal produk (lokal/impor) | tiga bucket | `bridge_pemeriksaan_temuan.negara` | normalisasi ejaan; sentinel/kosong = "tidak tercatat" | memasukkan sentinel ke impor |
| Produk impor (proxy penanda izin edar) | prefix `ML`/`MD` | `dim_produk.nomor_registrasi` | cek keterisian; disclaimer di jawaban | memakai `is_imported` |

---

## 3. Kontrak “temuan” per bentuk data

Tidak ada satu definisi global.

| Bentuk | Definisi yang dapat digunakan | Catatan |
|---|---|---|
| Skor pelayanan | rule per `area_key`: opsi/subfield/score | wajib data dictionary per area |
| Checklist Ya/Tidak | `nilai_aspek='Tidak'` | cacah item, bukan kasus |
| Checklist severity | nilai severity | pisahkan Minor/Major/Kritis |
| Observasi GMP | satu baris observasi + kode | `kriteria` belum terkonfirmasi |
| Temuan produk | satu baris produk bermasalah | kategori berupa array |
| Narasi | hasil klasifikasi NLP | harus evidence-backed |

### Kenapa `opsi='no'` tidak global

Contoh satu form dapat memiliki:

```text
opsi=no, score=0      → mungkin tidak sesuai
opsi=no, score=100    → jawaban faktual, bukan temuan
opsi=apoteker         → peran penyerah
opsi={"mutasi":"mostly"} → object prosedur
```

Jadi kontrak perlu dibuat per `area_key`:

| area_key | pertanyaan bisnis | vocab | skala | definisi temuan |

Tanpa kontrak itu, Q1–Q7 belum boleh dianggap satu formula universal.

---

## 4. Kontrak tren

Kata “tren” wajib menyebut metrik:

| Tren | Numerator/metric | Denominator | Makna |
|---|---|---|---|
| Tren volume pemeriksaan | kasus | — | aktivitas |
| Tren item tidak sesuai | item | — | beban temuan, sensitif volume inspeksi |
| Tren proporsi tidak sesuai | item tidak sesuai | semua item relevan | kualitas/kepatuhan |
| Tren TMK | kasus TMK | kasus dengan kesimpulan | outcome kasus |
| Tren sarana unik bermasalah | sarana unik | sarana diperiksa | cakupan objek |
| Tren severity | item/kasus severity | coverage relevan | risiko |

Jawaban harus mengatakan metrik mana yang digunakan. Default yang aman untuk aspek:

- pelayanan: proporsi/score kepatuhan;
- produksi: jumlah dan proporsi klausul tidak sesuai;
- tampilkan terpisah.

---

## 5. Kontrak wilayah

| Bahasa | Route | Output |
|---|---|---|
| “oleh BBPOM Bandung” | `balai_id` | UPT pelaksana |
| “Regional Semarang” | `regional_name` | kelompok regional |
| “sarana di Jawa Barat” | provinsi sarana | lokasi objek |
| “kabupaten Bandung” | kabupaten sarana | lokasi objek |
| “wilayah kerja UPT Bandung” | perlu definisi cakupan administratif | klarifikasi/lookup tambahan |

Jika bahasa user hanya “di Bandung”, sistem harus klarifikasi.

---

## 6. Kontrak inspektur

Yang dapat diukur:

- volume penugasan;
- kasus unik;
- jenis sarana/komoditi yang ditangani;
- wilayah/Balai;
- eksposur terhadap kasus severity tertentu.

Yang tidak dapat disimpulkan langsung:

- kompetensi formal;
- kualitas individu;
- produktivitas bersih tanpa memperhitungkan kompleksitas;
- siapa pengambil keputusan akhir.

Bahasa jawaban:

> “Inspektur X memiliki eksposur penugasan tertinggi pada jenis sarana Y.”

Bukan:

> “Inspektur X paling kompeten.”

---

## 7. Kontrak keputusan Balai vs Pusat

Dapat dianalisis:

- perbedaan kesimpulan Balai/Pusat jika keduanya terisi;
- narasi/TL Balai vs Pusat;
- event approval dan durasi;
- revisi dan status akhir.

Tidak dapat direkonstruksi penuh:

- setiap versi nilai sebelum/sesudah edit;
- alasan perubahan bila tidak ditulis di narasi/notes;
- review Pusat untuk kasus yang memang tidak direview.

Coverage review Pusat harus disebut karena `kesimpulan_pusat_id` parsial.

---

## 8. Kontrak free text / AI insight

Setiap hasil klasifikasi/ringkasan harus menyimpan:

| Field evidence | Wajib |
|---|---|
| `pemeriksaan_id` | ya |
| sumber teks/jenis narasi | ya |
| potongan bukti asli | ya |
| tanggal | ya |
| sarana dan UPT | ya |
| severity/kesimpulan terkait | bila tersedia |
| label hasil AI | ya |
| confidence/status review | ya |

AI boleh:

- membersihkan;
- merangkum;
- mengelompokkan topik;
- menunjukkan pola;
- menghubungkan data dalam kasus yang sama.

AI tidak boleh:

- mengarang severity yang tidak ada;
- mengubah narasi menjadi fakta tanpa evidence;
- menyatakan sebab-akibat dari korelasi;
- menghitung satu narasi sebagai satu klausul tanpa definisi.

---

## 9. Kontrak output

### Angka tunggal

Wajib menyebut:

- entity/grain;
- periode;
- scope;
- filter utama;
- coverage jika parsial.

### Tabel

Wajib:

- kolom label jelas;
- unit/grain jelas;
- sorting sesuai intent;
- limit/total jika daftar panjang.

### Chart

Wajib:

- metrik dan denominator;
- periode;
- kategori konsisten;
- tidak mencampur dua satuan.

### Narasi insight

Wajib:

- fakta utama;
- konteks;
- batas data;
- evidence atau jalur drill-down;
- bahasa korelasi.

---

## 10. Validasi sebelum jawaban dikirim

Checklist:

- [ ] intent sudah jelas;
- [ ] grain benar;
- [ ] route bridge sesuai flag/varian;
- [ ] join memakai type/cast/expand yang benar;
- [ ] data uji/draft difilter bila angka final;
- [ ] coverage dinyatakan;
- [ ] pelayanan vs produksi tidak digabung mentah;
- [ ] regional vs lokasi dibedakan;
- [ ] bukti disertakan untuk NLP;
- [ ] tidak ada klaim kausal tanpa dasar;
- [ ] honest gap dinyatakan bila data tidak tersedia.

---

## 11. Referensi aturan teknis

- [Aturan join](../ERD/03-aturan-join.md)
- [Routing bridge](../ERD/04-routing-bridge.md)
- [Aturan wajib](../ERD/05-aturan-wajib.md)
- [Kualitas data](../ERD/07-kualitas-data.md)
