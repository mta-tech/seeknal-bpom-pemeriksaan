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

## ⚠️ Tanggal kotor

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

⚠️ Nilai durasi memuat **pencilan ekstrem** yang berasal dari tanggal kotor. Sebelum menyajikan
rata-rata durasi, pakai **median** atau buang pencilan, dan sebutkan perlakuannya. Rata-rata
mentah pada kolom ini tidak stabil.

Durasi antar tahap persetujuan ada di `mv_pemeriksaan_timeline`. Ingat: tabel itu memuat id yang
tidak ada di fakta, dan kolom durasinya kosong pada tahap yang belum tercapai — menghitung
rata-rata tanpa menyaring akan mencampur "cepat" dengan "belum sampai". Lihat
`31-status-dan-alur.md`.

## Rute

- Menyebut target/capaian per periode → **seberang** `85-target-capaian.md`.
- Menyebut alur/tahapan → **seberang** `31-status-dan-alur.md`.
- Menyebut baris tanpa tanggal → **seberang** `90-kualitas-data.md`.
