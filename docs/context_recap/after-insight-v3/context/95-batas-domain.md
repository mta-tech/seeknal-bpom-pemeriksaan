Batas domain — apa yang TIDAK ada di database ini, dan bagaimana menjawabnya.

## Empat domain BPOM yang terpisah

| Domain | Isi | Database |
|---|---|---|
| **pemeriksaan** (di sini) | inspeksi ke sarana/fasilitas | domain ini |
| pengujian | sampling dan hasil uji laboratorium | database terpisah |
| pengawasan | pengawasan iklan | database terpisah |
| penandaan | pengawasan label/penandaan produk | database terpisah |

Keempatnya **tidak tersambung** di sini. Pertanyaan yang jatuh ke domain lain harus dijawab jujur,
bukan dijawab dengan kolom terdekat yang namanya mirip.

## Istilah yang menandai pertanyaan salah rute

| Istilah pengguna | Domain sebenarnya | Kenapa mudah tertukar |
|---|---|---|
| **MS / TMS**, "hasil uji", "parameter uji", "sampel", "LHU" | pengujian | domain ini memakai MK/TMK, bukan MS/TMS |
| **iklan**, "media", "lokasi iklan", "klausul pelanggaran" | pengawasan | — |
| **label / penandaan produk**, "kesimpulan balai vs pusat" | penandaan | domain ini juga punya kata "kesimpulan" |
| **izin edar / NIE / registrasi produk** | sistem registrasi | domain ini merekam sarana, bukan produk terdaftar |

> Bila pertanyaannya memakai istilah di atas, jawab: **konsep itu tidak direkam di database
> pemeriksaan**, lalu sebutkan domain mana yang menanganinya. Jangan memakai
> `kesimpulan`/`tp_kategori` sebagai pengganti hasil uji.

Cara memastikan dengan cepat bila ragu: periksa daftar kolom tabel
(`information_schema.columns`). Bila tidak ada kolom yang memuat konsepnya, itu **P5 NOT COVERED**.

## Konsep yang ditanyakan pengguna tetapi tidak ada di sini

| Diminta | Status | Kenapa |
|---|---|---|
| **nilai sarana A/B/C/D** (masukan grading) | tidak ada | hanya `grade` sebagai keluaran — `60-mutu-dan-tindak-lanjut.md` |
| **berita acara / dokumen unggahan** | tidak ada | lampiran tidak masuk warehouse |
| **sertifikat** (CPOB/CDOB dan masa berlakunya) | tidak ada | ada di sistem sertifikasi terpisah |
| **kualifikasi / kompetensi inspektur** | tidak ada | `70-petugas.md` hanya merekam penugasan |
| **siapa yang menyetujui** | tidak dapat dipastikan | semantik pelaku di log ambigu — `31-status-dan-alur.md` |
| **isian formulir per klausul/aspek** (pengadaan, penyimpanan, dst.) | tidak ada | hanya ringkasannya yang masuk warehouse |
| **data importasi / rekam jejak impor** | tidak ada | sistem lain |
| **status izin edar sarana** | tidak ada | sistem lain |

## Cara menjawab NOT COVERED

Tiga kalimat, tidak lebih:

1. sebut **apa yang ditanyakan** dan bahwa konsepnya tidak direkam di database ini;
2. sebut **di mana kemungkinan besar konsep itu berada** (domain/sistem lain), bila diketahui;
3. tawarkan **hal terdekat yang benar-benar bisa dijawab**, dan sebutkan bedanya.

Yang **tidak boleh**: menjawab dengan kolom yang namanya mirip lalu berharap pembaca memahami
bedanya. Query semacam itu jalan, hasilnya rapi, dan pembaca tidak punya cara tahu bahwa yang
ditampilkan bukan yang ditanyakan.

## Rute

- Kembali ke peta halaman `SEEKNAL_ASK.md`.
- Menyentuh kekosongan kolom: buka `90-kualitas-data.md`.

---

<!-- MANIFES
tabel: -
kolom: grade, kesimpulan, tp_kategori
nilai: -
-->
