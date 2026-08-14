# Test case — domain `pemeriksaan`

**Dibuat:** 14 Agustus 2026 · **Total:** 256 test dalam 18 folder.
**Skema berkas:** mengikuti pola UAT `seeknal-bpom-neo/seeknal/tests/v1/singleturn/UAT-v2-compact`.

## Tujuan

Mengevaluasi apakah agent mampu menjawab **dengan membaca context dan skill** yang ada — bukan
menebak. Angka pada `assert_any_of` seluruhnya diambil dari eksekusi SQL langsung ke database
domain ini pada tanggal verifikasi, bukan ditulis tangan.

## Dua kelas test

**Kelas A — regresi.** Diambil dari SQL pair sistem lama yang sudah terbukti jalan, SQL-nya
dijalankan ulang untuk mendapat nilai assert. Tugasnya membuktikan context baru **tidak merusak**
jawaban yang selama ini benar. Folder bernomor 11 ke atas.

**Kelas B — diskriminasi.** Ditulis dari temuan audit, menyasar aturan yang versi context sekarang
belum atau salah mengajarkan. Ciri khasnya: versi lama gagal, versi baru harus lolos. Folder
berawalan `0x-B-`.

Kelas A saja tidak cukup: pemetaan menunjukkan SQL pair nyaris tidak menyentuh target/capaian,
kode tahap log, sentinel, maupun kolom tahap timeline — persis yang diperbaiki versi baru. Tanpa
kelas B, seluruh test akan lolos di kedua versi dan tidak membuktikan apa pun.

## Semantik assert

| Kunci | Arti |
|---|---|
| `assert_contains` | semua token wajib muncul (DAN). Token bertanda `\|` = daftar sinonim, cukup salah satu |
| `assert_any_of` | daftar grup; lolos bila **minimal satu grup** cocok penuh |
| `tolerance_pct` | hanya berlaku untuk token numerik di `assert_any_of`. `0` = cocok persis |

Angka tidak pernah ditaruh di `assert_contains` karena di sana toleransi tidak berlaku.

Beberapa test sengaja **tanpa angka**: yang diuji apakah agent menyatakan keterbatasan data dengan
benar. Perilaku itu tidak menua ketika data bertambah.

## Isi `note`

Tiap `note` memuat SQL yang menghasilkan angka assert, kode filter beserta tabel dan kolomnya,
sebab jebakannya, dan — untuk kelas B — apa yang membuat versi lama gagal.

## Folder

| Folder | Kelas | Test | Menguji |
|---|---|--:|---|
| `01-aturan-baru-balai-dan-draft` | A | 15 | Cacah pemeriksaan untuk satu balai pada satu tahun; menguji normalisasi nama balai dan fi... |
| `02-bulan-dan-balai` | A | 15 | Cacah pemeriksaan untuk satu balai pada satu tahun; menguji normalisasi nama balai dan fi... |
| `03-jenis-sarana-dan-jenissar` | A | 15 | Cacah pemeriksaan untuk satu nilai `grade`; menguji pemetaan istilah ke kode filter yang ... |
| `04-kesimpula-dan-jenissar` | A | 15 | Silang `jenis_sarana` dengan periode; menguji kelengkapan filter dari pertanyaan majemuk. |
| `05-klasifikasi-distribusi-dan-klasifikasi-saran` | A | 14 | Cacah pemeriksaan untuk satu nilai `kesimpulan`; menguji pemetaan istilah ke kode filter ... |
| `06-komoditi-dan-kom-kosmetik` | A | 14 | Silang komoditi dengan periode; menguji apakah kedua komponen pertanyaan masuk ke filter. |
| `07-komoditi-dan-kosong-grade` | A | 14 | Cacah pemeriksaan untuk satu nilai `komoditi`; menguji pemetaan istilah ke kode filter ya... |
| `08-lainnya-dan-legal` | A | 14 | Keterisian `klasifikasi_sarana`; menguji penanganan penanda kosong yang lebih dari satu b... |
| `09-mapping-komoditi-target-balai-dan-legal` | A | 14 | Cacah pemeriksaan untuk satu nilai `legal`; menguji pemetaan istilah ke kode filter yang ... |
| `10-riwayat-sarana-dan-rank-jenis-sarana` | A | 14 | Peringkat nilai `jenis_sarana`; menguji pengeluaran penanda kosong dari peringkat. |
| `11-sarana-distribusi-dan-sarana` | A | 14 | Regresi dari pertanyaan nyata sistem lama; angka diverifikasi ulang ke database. |
| `12-sarana-distribusi-dan-sarana-produksi` | A | 14 | Regresi dari pertanyaan nyata sistem lama; angka diverifikasi ulang ke database. |
| `13-sarana-tutup-dan-sarana-produksi` | A | 14 | Regresi dari pertanyaan nyata sistem lama; angka diverifikasi ulang ke database. |
| `14-status-label-dan-tahun` | A | 14 | Cacah pemeriksaan untuk satu nilai `status_label`; menguji pemetaan istilah ke kode filte... |
| `15-temuan-produk-dan-target-capaian` | A | 14 | Regresi dari pertanyaan nyata sistem lama; angka diverifikasi ulang ke database. |
| `16-tren-hasil-pemeriksaan-dan-tingkat-pemenuhan` | A | 14 | Regresi dari pertanyaan nyata sistem lama; angka diverifikasi ulang ke database. |
| `17-tujuan-pemeriksaan-dan-vonis-mk-tmk` | A | 14 | Regresi dari pertanyaan nyata sistem lama; angka diverifikasi ulang ke database. |
| `18-x-dan-wilayah-persebaran` | A | 14 | Regresi dari pertanyaan nyata sistem lama; angka diverifikasi ulang ke database. |

## Catatan pemeliharaan

Angka kelas A akan bergeser seiring ETL. `verification_date` menandai kapan diverifikasi;
`tolerance_pct` menyerap pergeseran wajar. Bila sebuah test gagal, periksa dulu apakah datanya
yang bergerak atau jawabannya yang salah — jangan langsung menurunkan toleransi.
