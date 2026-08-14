Komoditi — apa yang diawasi, dan jembatannya ke tabel target.

## Kolom `komoditi`

Berisi jenis produk yang diawasi pada pemeriksaan itu. Nilainya huruf besar dan mencakup obat,
kosmetik, produk pangan, obat tradisional, suplemen kesehatan, serta beberapa golongan khusus
(narkotika, psikotropika, prekursor, obat-obat tertentu, bahan baku obat, bahan obat, bahan
berbahaya, produk biologi dan sarana khusus).

Ambil daftar nilainya bila pertanyaannya menyebut komoditi yang tidak Anda kenali — jalur **P2**.

## ⚠️ Ejaan berbeda dari domain lain

Domain ini memakai **`KOSMETIK`** (tanpa akhiran A) dan **`OBAT TRADISIONAL`** (tanpa `(OT)`),
sedangkan domain pengujian, pengawasan, dan penandaan memakai `KOSMETIKA` dan
`OBAT TRADISIONAL (OT)`. **Jangan menyalin daftar komoditi antar domain** — nilainya tidak cocok
dan filternya akan mengembalikan nol baris.

## Istilah pengguna yang ambigu

| Istilah | Kemungkinan | Tindakan |
|---|---|---|
| **"obat"** | hanya `OBAT`, atau seluruh keluarga obat (termasuk tradisional, narkotika, psikotropika, prekursor, obat-obat tertentu) | **tanya di Gate 1** |
| **"obat-obatan"** | idem | tanya |
| **"makanan" / "pangan"** | `PRODUK PANGAN` | biasanya tunggal, aman |
| **"obat kuasi"** | **tidak ada** sebagai nilai `komoditi` di domain ini | lihat di bawah |

## Jembatan ke tabel target

`komoditi` **tidak sama** dengan komoditi pada `target_balai`. Ada kolom jembatan khusus,
`mapping_komoditi_target_balai`, yang mengelompokkan nilai-nilai `komoditi` ke kelompok yang
dipakai tabel target.

> **Setiap join ke `target_balai` memakai `mapping_komoditi_target_balai`, tidak pernah
> `komoditi` mentah.** Memakai `komoditi` membuat sebagian besar pasangan balai×komoditi
> kehilangan target — tanpa error, hanya menghilang.

Peta pengelompokannya bisa dilihat langsung:
`SELECT DISTINCT komoditi, mapping_komoditi_target_balai FROM mv_pemeriksaan`.

Dua hal yang perlu diketahui dari peta itu:

1. Beberapa golongan obat khusus dikelompokkan menjadi satu kelompok obat.
2. **`OBAT KUASI` pada sisi target berasal dari komoditi `BAHAN BERBAHAYA`** — pemetaan yang
   janggal secara istilah. Bila pertanyaan menyebut Obat Kuasi, jawab lewat kolom jembatan dan
   **sebutkan** bahwa realisasinya berasal dari komoditi bahan berbahaya. Jangan mencari nilai
   `OBAT KUASI` di kolom `komoditi` — tidak ada.

Sebaliknya, `target_balai` memuat satu komoditi (rokok) yang **tidak pernah muncul** di pemeriksaan
sarana; itu bukan kesalahan, memang tidak ada pemeriksaan sarana untuk komoditi itu.

## Kolom bernama `komoditi` di tabel lain

`mv_pemeriksaan_petugas` juga punya kolom bernama `komoditi`, tetapi isinya **jenis fasilitas**
(sejajar `jenis_sarana` di tabel fakta), bukan jenis produk. Pilih tabel berdasarkan subjek
pertanyaan, jangan berdasarkan kolom yang kebetulan bernama sama.

## Rute

- Menyentuh target atau capaian → **seberang** `85-target-capaian.md`.
- Menyebut MD / IRT / jenis pangan → **seberang** `50-jenis-pangan.md`.
- Menyebut rantai sarana → **seberang** `10-sarana-dan-fasilitas.md`.
