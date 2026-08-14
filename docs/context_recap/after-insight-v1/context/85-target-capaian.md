Target dan capaian — dan tiga batas yang harus disebut setiap kali.

## Tabel

`target_balai` memuat target tahunan per `(nama_balai, komoditi, tahun)`. Kolom targetnya
terpisah per jenis kegiatan.

## Tiga batas struktural

### 1. Hanya satu tahun

Tabel target hanya memuat **satu tahun anggaran**. Periksa dulu tahun apa yang ada
(`SELECT DISTINCT tahun FROM target_balai`) sebelum menjanjikan capaian.

> Untuk realisasi di tahun yang **tidak ada targetnya**, ada dua jawaban jujur: sajikan realisasi
> **tanpa** persentase capaian, atau bandingkan terhadap target tahun yang tersedia **sambil
> menyatakan bahwa tahunnya berbeda**. Diam-diam memakai target tahun lain sebagai pembanding
> adalah kesalahan.

### 2. Tidak ada target untuk semua rantai sarana

Kolom target sarana hanya tersedia untuk **sebagian** nilai `sarana`. Periksa daftar kolomnya
lebih dulu:

```sql
SELECT column_name FROM information_schema.columns
WHERE table_schema='public' AND table_name='target_balai' AND column_name LIKE 'target%';
```

> Pertanyaan "tabel balai + target + realisasi dikelompokkan berdasarkan sarana" **hanya bisa
> dijawab untuk rantai yang punya kolom targetnya**. Memakai target rantai lain sebagai pengganti
> menghasilkan capaian yang keliru. Sebutkan rantai mana yang tidak punya target — itu jawaban
> yang benar, bukan "datanya tidak ada".

### 3. Beberapa unit tidak punya target sama sekali

Unit pusat (direktorat) dan sebagian loka baru tidak ada di tabel target. Laporkan terpisah
sebagai "target belum ditetapkan"; jangan menghitung capaian nol untuk mereka.

## Dua kunci join yang harus benar

**Nama balai.** Tabel fakta menulis `nama_upt` dengan huruf besar, tabel target menulis
`nama_balai` dengan huruf campuran. **Join persis akan gagal.** Selalu normalisasi kedua sisi:
`lower(trim(...)) = lower(trim(...))`.

**Komoditi.** Jangan join `komoditi` mentah. Pakai kolom jembatan
`mapping_komoditi_target_balai` — lihat `20-komoditi.md`. Memakai kolom mentah membuat banyak
pasangan balai×komoditi kehilangan targetnya tanpa error.

## Bentuk jawaban

Capaian = realisasi ÷ target. Sebelum menyajikannya:

1. sebutkan **tahun target** yang dipakai;
2. sebutkan **rantai sarana** mana yang tercakup;
3. keluarkan unit pusat dan akun uji dari agregat nasional;
4. bila periodenya berjalan, sebutkan bahwa realisasinya belum lengkap.

Empat butir itu bukan hiasan — tanpanya, angka capaian terbaca sebagai penilaian kinerja yang
tidak sepadan.

## Cakupan wilayah

`coverage_balai` memuat wilayah kerja balai (kabupaten/kota yang menjadi tanggung jawabnya).
Dipakai untuk pertanyaan "berapa persen wilayah kerja yang tersentuh" — pembilangnya dari lokasi
sarana di fakta (`kabupaten_kota`), penyebutnya dari tabel ini.

Perhatikan: jumlah balai di `coverage_balai` dan di fakta **tidak sama**. Balai yang ada di
cakupan tetapi tidak punya pemeriksaan pada periode itu harus tampil sebagai nol, bukan hilang —
pakai LEFT JOIN dari sisi cakupan.

## Rute

- Menyebut komoditi → **seberang** `20-komoditi.md`.
- Menyebut UPT/balai → **seberang** `10-sarana-dan-fasilitas.md`.
- Menyebut periode → **seberang** `80-waktu-dan-durasi.md`.
