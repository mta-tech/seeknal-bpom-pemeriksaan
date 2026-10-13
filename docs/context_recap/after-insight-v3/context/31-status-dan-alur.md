Status berkas dan alur persetujuan — dan apa yang TIDAK bisa disimpulkan darinya.

## `status` di tabel fakta

Kolom `status` bertipe **teks** (berbeda dari domain lain yang memakai angka). Nilainya menandai
posisi berkas dalam alur: tahap draft, tahap perbaikan, beberapa tingkat verifikasi, dan tahap
selesai. Ada juga varian bertanda pusat untuk berkas yang ditangani unit pusat.

Ambil daftar nilainya lewat `SELECT DISTINCT status` — jalur **P2**. Jangan mengetik dari ingatan;
penamaannya bertingkat dan mudah keliru.

`status_label` adalah pasangan berbahasa manusia dari `status`. Untuk **menyaring**, pakai
`status`; untuk **menampilkan**, pakai `status_label`.

PENTING: `status` juga memuat sentinel berupa string `'NULL'` — sama seperti `kesimpulan`.

## Menerjemahkan pertanyaan alur

| Pertanyaan | Filter |
|---|---|
| "sudah selesai" | nilai status bertahap akhir saja |
| "masih diproses / belum selesai" | kebalikan dari tahap akhir |
| "masih draft" | nilai bertahap draft saja |
| "mangkrak / menumpuk di tahap mana" | `GROUP BY status`, tanpa filter |

**Jangan menumpuk filter status di atas populasi yang sudah didefinisikan hal lain.** Pertanyaan
"berapa pemeriksaan TMK" tidak memerlukan filter status sama sekali; menambahkannya menghapus
sebagian populasi yang ditanya.

## Tabel log

`mv_pemeriksaan_log` memuat satu baris per perpindahan tahap, dengan kolom pelaku (`fullname`),
catatan, dan waktu.

### Semantik kolom pelaku — jangan disalahtafsirkan

Model lognya: **`status` menandai keadaan SESUDAH perpindahan**, `catatan` menjelaskan aksi yang
memicunya, dan **`fullname` adalah pelaku aksi itu** — yang perannya dinamai oleh label tahap
**sebelumnya**. `status_label` menyebut pihak yang **ditunggu berikutnya**, bukan yang sudah
bertindak.

Konsekuensi yang harus diketahui:

> Baris bertahap verifikasi pertama biasanya membawa nama **operator yang mengirim**, bukan
> supervisor yang menyetujui. Menyimpulkan "diverifikasi oleh pembuatnya sendiri" dari kesamaan
> nama pada dua baris berurutan **adalah kesalahan tafsir**, bukan temuan.

**Aturan:** pertanyaan *"siapa yang menyetujui"*, *"apakah ada self-approval"*, *"apakah pemisahan
tugas berjalan"* **P5 NOT COVERED**. Semantik kolom pelaku tidak dapat dipastikan dari database
ini sendirian, dan kesimpulannya bersifat tuduhan. Jawab jujur bahwa penelusuran persetujuan
memerlukan konfirmasi alur sistem sumber.

Yang **boleh** dijawab dari log: kapan sebuah berkas berpindah tahap, berapa lama tersangkut di
suatu tahap, dan tahap mana yang paling banyak menahan berkas — semua itu tentang **waktu dan
volume**, bukan tentang **siapa**.

## Tabel timeline

`mv_pemeriksaan_timeline` memuat tanggal milestone dan durasi antar tahap.

PENTING: **Tabel ini memuat id yang tidak ada di tabel fakta.** Menghitung dari timeline langsung akan
melebihi populasi pemeriksaan. Selalu **INNER JOIN dari fakta** bila jawabannya berbicara tentang
populasi pemeriksaan. Kolom durasinya juga kosong pada tahap yang belum tercapai — lihat
`80-waktu-dan-durasi.md`.


## Kode tahap di tabel log

Kolom `urutan_step` adalah **pengurut tahap**: ia menentukan urutan langkah dalam alur, bukan sekadar
label. Tanpa memakainya, pertanyaan "tahap mana yang paling lama" atau "berkas berhenti di mana"
tidak bisa dijawab, karena urutan langkah tidak bisa disimpulkan dari nama langkahnya.

Perhatikan juga: **nilai yang muncul hanya pada segelintir baris** di tengah nilai bervolume besar
biasanya salah ketik, bukan tahap yang benar-benar ada. Saat menyusun daftar tahap, abaikan varian
penulisan bervolume sangat kecil dari nilai bervolume besar — memasukkannya akan menciptakan tahap
yang sebenarnya tidak pernah ada di alur.

## Rute

- Menyebut durasi atau SLA: buka `80-waktu-dan-durasi.md`.
- Menyebut vonis: buka `30-kesimpulan.md`.
- Menyebut petugas/inspektur: buka `70-petugas.md`.

---

<!-- MANIFES
tabel: mv_pemeriksaan_log, mv_pemeriksaan_timeline
kolom: catatan, fullname, kesimpulan, status, status_label, urutan_step
nilai: -
-->
