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


## Tabel target memuat TUJUH kolom target — hanya sebagian milik domain ini

Ini penyebab kesalahan yang paling mudah terjadi di halaman ini, karena semua kolomnya bernama
mirip dan semuanya berisi angka yang masuk akal.

`target_balai` melayani beberapa kegiatan pengawasan sekaligus. Kolom targetnya:
`target_penandaan`, `target_pengawasan`, `target_pengujian`, `target_pengujian_pangan`,
`target_pengujian_pangan_fortifikasi`, `target_sarana_distribusi`, `target_sarana_produksi`.

**Untuk domain ini yang dipakai adalah `target_sarana_produksi` dan `target_sarana_distribusi`.** Dua kolom, bukan satu: pilih sesuai rantai yang ditanya — sarana produksi atau sarana distribusi. Bila pertanyaannya tidak menyebut rantai, tanyakan lebih dulu; menjumlahkan keduanya hanya benar bila pertanyaannya memang total sarana.

> **Aturan:** kolom target dipilih berdasarkan **kegiatan yang ditanya**, bukan berdasarkan angka
> mana yang terlihat wajar. Kolom milik kegiatan lain **tidak boleh dipakai di sini** meskipun
> terisi — angkanya nyata, tetapi menjawab pertanyaan yang berbeda.

## Grain tabel target: satu baris = satu balai × satu komoditi × satu tahun

Bukan satu baris per balai. Setiap balai punya beberapa baris, satu untuk tiap komoditi.

Konsekuensinya:

| Yang ingin dijawab | Yang harus dilakukan |
|---|---|
| Target satu balai untuk satu komoditi | ambil barisnya langsung |
| Target satu balai keseluruhan | jumlahkan seluruh komoditinya |
| Target nasional | jumlahkan seluruh balai **dan** seluruh komoditi |
| Membandingkan dengan capaian per komoditi | agregasi capaian juga harus per komoditi |

> **Aturan:** menjumlahkan kolom target tanpa menyadari grain-nya akan **melipatgandakan** hasilnya
> sebanyak jumlah komoditi. Selalu tentukan lebih dulu apakah pertanyaannya per komoditi atau
> gabungan, lalu samakan tingkat agregasi kedua sisi — target dan capaian.

## Tabel target tidak mencakup semua tahun

Kolom `tahun` di tabel ini **tidak berisi seluruh tahun operasional**. Jangan berasumsi tahun yang
diminta pengguna tersedia.

> **Aturan:** sebelum menjawab pertanyaan capaian, **periksa dulu tahun apa saja yang ada** di
> tabel target. Bila tahun yang diminta tidak ada, jawab bahwa pembandingnya tidak tersedia untuk
> tahun itu — **jangan** menjawab capaian nol, dan **jangan** diam-diam memakai tahun lain sebagai
> pengganti.
>
> Ini pemeriksaan, bukan fakta yang dihafal: isi tabel bisa bertambah kapan saja, jadi periksa
> setiap kali alih-alih mengandalkan apa yang pernah benar.

## Rute

- Menyebut komoditi: buka `20-komoditi.md`.
- Menyebut UPT/balai: buka `10-sarana-dan-fasilitas.md`.
- Menyebut periode: buka `80-waktu-dan-durasi.md`.

---

<!-- MANIFES
tabel: coverage_balai, target_balai
kolom: kabupaten_kota, komoditi, mapping_komoditi_target_balai, nama_balai, nama_upt, sarana, tahun, target_penandaan, target_pengawasan, target_pengujian, target_pengujian_pangan, target_pengujian_pangan_fortifikasi, target_sarana_distribusi, target_sarana_produksi
nilai: -
-->
