Tujuan pemeriksaan — alasan sebuah inspeksi dilakukan, dan kolom mirip yang menjebak.

## Kolomnya

`tujuan_pemeriksaan` di `mv_pemeriksaan`. Ini dimensi yang menjawab **mengapa** sebuah pemeriksaan
terjadi — berbeda dari `jenis_sarana` (diperiksa di mana) dan `komoditi` (memeriksa apa).

Kubus agregasi `mv_pemeriksaan_agg` memuat kolom bernama sama dengan makna sama.

## Ada tiga kolom lain bernama mirip — hanya satu yang benar untuk menghitung pemeriksaan

Ini jebakan utama halaman ini, dan ia sangat mudah kena karena namanya cocok.

| Tabel | Kolom | Satu barisnya mewakili apa | Aman untuk menghitung pemeriksaan? |
|---|---|---|---|
| `mv_pemeriksaan` | `tujuan_pemeriksaan` | satu pemeriksaan | YA — **ini yang benar** |
| `mv_pemeriksaan_agg` | `tujuan_pemeriksaan` | satu sel kubus | hanya dengan aturan kubus di `00-menghitung.md` |
| `mv_pemeriksaan_petugas` | `tujuan` | satu **penugasan petugas** | tidak, tidak |
| `mv_kriteria_pemeriksaan` | `tujuan` | satu item checklist audit | tidak, tidak |

Tabel petugas memuat **beberapa baris per pemeriksaan**, karena satu pemeriksaan dikerjakan lebih
dari satu petugas. `GROUP BY tujuan` di sana menghitung **penugasan**, bukan pemeriksaan — angkanya
akan lebih besar dari kenyataan, dan besarnya tidak akan terlihat aneh.

> **Aturan:** pertanyaan "pemeriksaan per tujuan", "berapa pemeriksaan rutin", "pemeriksaan dalam
> rangka X" **selalu** dijawab dari `mv_pemeriksaan.tujuan_pemeriksaan`. Kolom `tujuan` di tabel
> petugas hanya dipakai bila pertanyaannya memang tentang **penugasan petugas** — lihat
> `70-petugas.md`.

## Bentuk nilainya

Nilai ditulis **huruf besar semua**, berupa frasa, dan sebagian memuat tanda baca (`/`, `-`).
Contoh bentuknya: `PEMERIKSAAN RUTIN`, `IDUL FITRI`, `SERTIFIKASI CDOB`,
`RENCANA AKSI / INTENSIFIKASI PENGAWASAN`, `KASUS/ TINDAK LANJUT`.

Perhatikan `KASUS/ TINDAK LANJUT` — ada spasi **sesudah** garis miring tetapi tidak sebelumnya.
Penulisan seperti ini tidak bisa ditebak; ambil nilainya lewat probe, jangan diketik dari ingatan.

## Cara membaca isinya — enam keluarga

Nilai-nilainya tidak acak. Mengenali keluarganya membantu memetakan pertanyaan pengguna ke filter
yang benar, dan menjelaskan mengapa dua nilai yang berbeda kadang harus digabung.

| Keluarga | Apa yang dimaksud | Bentuk nilainya |
|---|---|---|
| **Rutin** | inspeksi terjadwal, bukan karena pemicu | nilai bertuliskan rutin |
| **Kampanye musiman** | intensifikasi menjelang hari besar | nama hari besar keagamaan sebagai nilai — Idul Fitri, Natal dan tahun baru, Idul Adha, Imlek, dan sebutan hari besar lainnya |
| **Sertifikasi** | inspeksi untuk menerbitkan atau memperpanjang sertifikat | memuat kata sertifikasi, kadang dengan nama standar (CPOB, CDOB, CPKB) atau tahapannya (pra, re-) |
| **Intensifikasi tematik** | fokus pada satu isu | memuat kata intensifikasi diikuti temanya |
| **Kasus dan tindak lanjut** | dipicu temuan atau laporan sebelumnya | memuat kata kasus, tindak lanjut, atau verifikasi CAPA |
| **Operasi gabungan & lainnya** | kegiatan lintas instansi dan sisanya | singkatan operasi gabungan, surveilans, pemusnahan, asistensi |

> **Aturan:** pertanyaan pengguna hampir selalu menyebut **keluarga**, bukan nilai persis —
> "pemeriksaan menjelang lebaran", "inspeksi rutin", "pemeriksaan sertifikasi". Karena satu keluarga
> berisi beberapa nilai, filter dengan kesamaan persis **akan kehilangan sebagian**.
>
> Pola kerjanya: ambil daftar nilai lebih dulu (jalur **P2**), kenali mana saja yang masuk keluarga
> yang diminta, lalu filter dengan himpunan nilai persis itu — bukan dengan satu nilai, dan bukan
> dengan pencarian kata bebas.

Untuk keluarga sertifikasi dan intensifikasi, pencarian pola awalan bisa dipakai karena katanya
konsisten di depan. Untuk keluarga kampanye musiman **tidak bisa** — nama hari besar tidak punya
kata bersama, jadi himpunannya harus disebut satu per satu.

## Kolom ini kosong pada sebagian berkas

Sebagian baris tidak punya tujuan terisi, dan itu **bukan acak**: baris tanpa tujuan hampir
seluruhnya adalah berkas yang masih berstatus draft — pemeriksaannya belum dicatat, jadi belum ada
tujuannya. Kaitannya dengan tanggal kosong dijelaskan di `90-kualitas-data.md`.

> **Aturan:** kekosongan di kolom ini adalah **keadaan alur kerja**, bukan kategori "lain-lain".
> Jangan menampilkannya sebagai salah satu tujuan dalam peringkat; sebutkan terpisah bila relevan.

## Menyilangkan tujuan dengan kesimpulan

Sah, dengan satu syarat: bandingkan hanya antar tujuan yang **populasinya sebanding**. Sebagian
tujuan sangat jarang dipakai, dan proporsi dari populasi kecil terlihat ekstrem tanpa berarti.

## Rute

- Menyebut jenis sarana atau balai: buka `10-sarana-dan-fasilitas.md`.
- Menyebut petugas atau penugasan: buka `70-petugas.md`.
- Menyebut kesimpulan MK/TMK: buka `30-kesimpulan.md`.
- Menyebut periode atau tren: buka `80-waktu-dan-durasi.md`.

---

<!-- MANIFES
tabel: mv_kriteria_pemeriksaan, mv_pemeriksaan, mv_pemeriksaan_agg, mv_pemeriksaan_petugas
kolom: jenis_sarana, komoditi, tujuan, tujuan_pemeriksaan
nilai: IDUL FITRI, KASUS/ TINDAK LANJUT, PEMERIKSAAN RUTIN, RENCANA AKSI / INTENSIFIKASI PENGAWASAN, SERTIFIKASI CDOB
-->
