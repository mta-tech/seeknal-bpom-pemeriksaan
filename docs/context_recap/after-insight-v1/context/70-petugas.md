Petugas pemeriksa — beban kerja dan penugasan.

## Tabel

`mv_pemeriksaan_petugas` menempel ke fakta lewat `id_pemeriksaan`. **Satu pemeriksaan lazimnya
punya lebih dari satu petugas**, jadi tabel ini jauh lebih panjang daripada tabel fakta.

| Kolom | Isi |
|---|---|
| `petugas`, `petugas_id` | identitas pemeriksa |
| `nomorsurat`, `tgl_surat` | surat tugas |
| `daftar_balai_pemeriksa` | balai pelaksana |
| `komoditi`, `tujuan`, `klasifikasi`, `jenis_id` | konteks penugasan |

## ⚠️ Kolom `komoditi` di tabel ini berbeda artinya

Di tabel fakta, `komoditi` berarti **jenis produk**. Di tabel petugas, kolom bernama `komoditi`
berisi **jenis fasilitas** — sejajar dengan `jenis_sarana` di fakta, bukan dengan `komoditi`.

> Pilih tabel berdasarkan subjek pertanyaan, jangan berdasarkan kolom yang kebetulan bernama sama.
> Bila pertanyaannya tentang komoditi produk, ambil dari fakta lewat join, bukan dari kolom
> bernama sama di tabel ini.

Kolom `klasifikasi` di tabel petugas justru yang sejajar dengan `komoditi` di fakta. Penamaannya
tertukar dibanding tabel fakta — periksa isinya sebelum memakai (jalur **P2**).

## Menghitung beban kerja

| Pertanyaan | Bentuk |
|---|---|
| berapa pemeriksaan per petugas | `GROUP BY petugas`, `COUNT(DISTINCT id_pemeriksaan)` |
| petugas per balai | `GROUP BY daftar_balai_pemeriksa, petugas` |
| penugasan per tujuan | `GROUP BY tujuan` |

**Jangan** menghitung "jumlah pemeriksaan" dari tabel ini dengan `COUNT(*)` — hasilnya cacah
penugasan, bukan pemeriksaan. Untuk cacah pemeriksaan, `COUNT(DISTINCT id_pemeriksaan)`.

`tgl_surat` adalah tanggal surat tugas, **bukan** tanggal pemeriksaan. Untuk periode kegiatan,
join ke fakta dan pakai kolom tanggal di sana (`00-menghitung.md` §2).

## Yang TIDAK bisa dijawab dari tabel ini

Kualifikasi, kompetensi, jenjang, atau "maturitas" inspektur **tidak ada** di database ini. Tabel
ini hanya merekam siapa ditugaskan ke pemeriksaan mana. Pertanyaan tentang kualifikasi →
**P5 NOT COVERED**.

Demikian pula pertanyaan *"siapa yang menyetujui"* — itu soal alur, dan semantik pelakunya tidak
dapat dipastikan; lihat `31-status-dan-alur.md`.

## Rute

- Menyebut alur persetujuan → **seberang** `31-status-dan-alur.md`.
- Menyebut balai/UPT → **seberang** `10-sarana-dan-fasilitas.md`.
