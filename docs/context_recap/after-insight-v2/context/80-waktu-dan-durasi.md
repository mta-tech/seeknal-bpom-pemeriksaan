Waktu, periode, dan durasi.

## Memilih kolom tanggal

Tiga kolom, tiga arti — daftar lengkapnya di `00-menghitung.md` §2. Ringkasnya: kegiatan memakai
`tanggal_mulai` (atau `tanggal_selesai` bila pertanyaannya tentang penyelesaian); administrasi
memakai `tanggal_input`.

**Entity dan kolom tanggal adalah satu keputusan** — jangan mengambil dari dua baris berbeda.

## Bentuk filter periode

Pakai **rentang berbatas**: `kolom >= awal AND kolom < akhir_eksklusif`.

Jangan `EXTRACT(YEAR …) = tahun` sebagai penyaring — tidak ada indeks di database ini, dan bentuk
itu memaksa perhitungan per baris pada tabel penuh. `EXTRACT` dan `to_char` hanya untuk **melabeli**
hasil yang sudah dikelompokkan.

| Frasa pengguna | Bentuk |
|---|---|
| tahun X | `>= 'X-01-01' AND < '(X+1)-01-01'` |
| bulan X tahun Y | `>= 'Y-X-01' AND < bulan berikutnya` |
| triwulan I | tiga bulan pertama, rentang berbatas |
| "3 tahun terakhir" | relatif terhadap tanggal hari ini; **nyatakan tanggal acuannya** |
| "tahun ini" / "bulan ini" | periode berjalan — **selalu parsial**, nyatakan |

## Tanggal kotor

Kolom tanggal kegiatan memuat sejumlah nilai yang jelas keliru: tahun jauh di masa lalu dan tahun
di **masa depan** relatif hari ini. Jumlahnya kecil, tetapi:

- tren "sejak tahun paling awal" akan menampilkan ekor panjang yang menyesatkan;
- nilai maksimum kolom tanggal **bukan** penanda kesegaran data.

> Untuk tren, **batasi rentangnya secara eksplisit** ke periode yang masuk akal, dan sebutkan
> bahwa baris di luar rentang dikeluarkan. Untuk mengetahui kesegaran data, pakai `tanggal_input`
> atau kolom `sync`, bukan `tanggal_mulai`.

Sebagian baris juga **tidak punya tanggal kegiatan sama sekali** — lihat `90-kualitas-data.md`.
Baris itu tidak pernah masuk hitungan berbasis periode, dan juga tidak masuk kubus `agg`.

## Periode berjalan selalu parsial

Bulan (dan tahun) yang sedang berlangsung belum lengkap. Setiap tren bulanan **wajib** menyebutnya;
tanpa itu, penurunan di titik terakhir terbaca sebagai penurunan kinerja padahal hanya belum
lengkap.

Hal yang sama berlaku untuk periode yang datanya masih mengalir: bila titik terakhir jauh lebih
rendah dari sebelumnya, periksa dulu apakah itu periode berjalan sebelum menyebutnya penurunan.

## Durasi

Tiga kolom durasi tersedia di tabel fakta: selisih hari antara input dan mulai, input dan selesai,
serta mulai dan selesai. Semuanya dalam hari kalender.

PENTING: Nilai durasi memuat **pencilan ekstrem** yang berasal dari tanggal kotor. Sebelum menyajikan
rata-rata durasi, pakai **median** atau buang pencilan, dan sebutkan perlakuannya. Rata-rata
mentah pada kolom ini tidak stabil.

Durasi antar tahap persetujuan ada di `mv_pemeriksaan_timeline`. Ingat: tabel itu memuat id yang
tidak ada di fakta, dan kolom durasinya kosong pada tahap yang belum tercapai — menghitung
rata-rata tanpa menyaring akan mencampur "cepat" dengan "belum sampai". Lihat
`31-status-dan-alur.md`.


## Kolom tahap di tabel timeline — inilah yang menjawab "tertahan di tahap mana"

Tabel timeline bukan sekadar penyimpan tanggal mulai dan selesai. Ia memuat **tanggal tiap tahap**
dan **kolom selisih antar tahap**:

| Bentuk kolom | Contoh namanya | Isinya |
|---|---|---|
| Tanggal tahap | `tanggal_kirim_kabalai`, `tanggal_kirim_direktur` | kapan berkas dikirim ke tahap berikutnya |
| Selisih antar tahap | `mulai_kabalai`, `kabalai_direktur` | jarak antar dua tahap |

> PENTING: **Kolom bernama seperti selisih belum tentu berisi jumlah hari.** Sebagian di antaranya hanya
> punya sedikit kemungkinan nilai — itu **penanda**, bukan durasi. Sebelum memakai kolom selisih
> untuk menghitung rata-rata lama proses, **periksa dulu sebaran nilainya**. Kalau nilainya hanya
> beberapa kemungkinan, ia menandai terjadi/tidaknya sesuatu, dan merata-ratakannya tidak berarti.

**Kekosongan di kolom tahap bersifat deterministik.** Berkas yang tidak pernah naik ke suatu tahap
memang tidak punya tanggal untuk tahap itu — bukan data yang hilang, melainkan tahap yang belum
terjadi.

> **Aturan:** rata-rata lama tahap **hanya dihitung dari berkas yang benar-benar melewati tahap
> itu**. Menyertakan baris kosong akan menurunkan rata-rata secara keliru. Dan karena porsi berkas
> yang mencapai tahap akhir jauh lebih kecil daripada yang mencapai tahap awal, **sebutkan populasi
> mana yang dihitung** di kalimat jawaban.
>
> Pertanyaan "di tahap mana berkas paling lama tertahan" dijawab dengan membandingkan antar tahap
> **pada populasi yang sama** — yaitu berkas yang melewati semua tahap yang dibandingkan.

## Kolom selisih hari sudah dihitung di tabel fakta

`mv_pemeriksaan` memuat `day_input_mulai`, `day_input_selesai`, dan `day_mulai_selesai` — selisih
hari antar tanggal, sudah dihitung saat ETL.

Untuk pertanyaan "berapa lama", kolom ini lebih murah daripada mengurangkan tanggal sendiri, dan
hasilnya konsisten karena semua baris memakai definisi yang sama.

Aturan: sebelum memakainya, periksa keterisiannya. Baris yang tanggalnya kosong juga kosong di
kolom selisih, dan rata-rata yang menyertakan baris kosong akan salah. Bila hasilnya berbeda dari
pengurangan tanggal manual, yang dipakai adalah kolom ini, dan sebutkan basisnya.

`mv_pemeriksaan_timeline` juga punya `tgl_start` dan `tgl_end` — tanggal batas versi timeline,
terpisah dari kolom tanggal di tabel fakta. Keduanya tidak selalu sama; pilih menurut apakah
pertanyaannya soal kegiatan atau soal perjalanan berkas.

## Memastikan rentang tanggal sebelum menjawab

Sebelum menjawab pertanyaan periode, pastikan dulu rentang yang benar-benar tersedia:
`SELECT min(tanggal_mulai), max(tanggal_mulai) FROM mv_pemeriksaan`.

Dua hal yang muncul dari situ dan keduanya perlu ditangani:

- Nilai terjauh bisa berupa tanggal rusak, bukan tanggal sebenarnya. Batasi ke rentang operasional
  sebelum menyebut "paling awal".
- Baris tanpa tanggal kegiatan tidak akan muncul di filter periode mana pun. Bila pertanyaannya
  tentang berkas yang masuk, kolom tanggal yang dipakai berbeda.

## Rute

- Menyebut target/capaian per periode: buka `85-target-capaian.md`.
- Menyebut alur/tahapan: buka `31-status-dan-alur.md`.
- Menyebut baris tanpa tanggal: buka `90-kualitas-data.md`.

---

<!-- MANIFES
tabel: mv_pemeriksaan, mv_pemeriksaan_timeline
kolom: day_input_mulai, day_input_selesai, day_mulai_selesai, kabalai_direktur, mulai_kabalai, sync, tanggal_input, tanggal_kirim_direktur, tanggal_kirim_kabalai, tanggal_mulai, tanggal_selesai, tgl_end, tgl_start
nilai: -
-->
