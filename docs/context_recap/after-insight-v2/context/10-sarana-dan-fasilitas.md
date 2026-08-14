Sarana — rantai pengawasan, jenis fasilitas, bentuk badan usaha, dan UPT pemeriksa.

## Dua kolom bernama mirip, dua konsep berbeda

Ini kesalahan paling mahal di domain ini. Query-nya jalan tanpa error dan mengembalikan nol baris.

| Kolom | Konsep | Isi |
|---|---|---|
| `sarana` | **rantai pengawasan** — tiga nilai | `DISTRIBUSI`, `PELAYANAN`, `PRODUKSI` |
| `jenis_sarana` | **jenis fasilitas** — puluhan nilai | `APOTEK`, `PBF`, `TOKO OBAT`, `PANGAN`, `PANGAN MD`, `PANGAN IRT (CPPB - IRT)`, `KOSMETIK`, `PUSAT KESEHATAN MASYARAKAT (PKM)`, dan seterusnya |

**"Sarana produksi", "sarana distribusi", "sarana pelayanan" kolom `sarana`.**
**"Apotek", "PBF", "pangan MD", "toko obat" kolom `jenis_sarana`.**

Skema lama sistem ini menaruh konsep rantai di kolom bernama `jenis_sarana`. Kamus istilah dan
aturan warisan yang menyebut *"produksi ada di kolom jenis_sarana"* mengacu ke skema lama dan
**sudah tidak berlaku**. Bila menemukan aturan lama seperti itu, abaikan; pakai `sarana`.

Nilai `sarana` ditulis huruf besar. Bandingkan dengan nilai persis, atau bungkus kedua sisi dengan
`lower()` — jangan mencampur (`lower(sarana) = 'PRODUKSI'` selalu salah).

## Menggabungkan keduanya

Banyak pertanyaan memerlukan dua-duanya sekaligus:

| Pertanyaan | Filter |
|---|---|
| sarana **produksi MD** | `sarana = 'PRODUKSI'` **AND** `jenis_sarana LIKE '%MD%'` |
| sarana **distribusi kosmetik** | `sarana = 'DISTRIBUSI'` **AND** `komoditi = 'KOSMETIK'` |
| **apotek** | `jenis_sarana = 'APOTEK'` (rantainya menyusul sendiri) |
| sarana **produksi obat** | `sarana = 'PRODUKSI'` **AND** `komoditi = 'OBAT'` |

Penanda **MD / IRT / UMKM** hidup di `jenis_sarana`, **bukan** di `komoditi`. Detail di
`50-jenis-pangan.md`.

## `legal` — bentuk badan usaha atau tempat

Kolom terpisah berisi bentuk hukum/tempat usaha (`PT`, `CV`, `UD`, `TOKO`, `APOTEK`,
`SWALAYAN / MINI MARKET / SUPER MARKET`, `KIOS / WARUNG`, dan lain-lain). Beberapa nilainya
**bertumpang tindih** dengan `jenis_sarana` (`APOTEK` dan `TOKO OBAT` muncul di kedua kolom) —
pilih berdasarkan makna pertanyaan: bentuk usaha `legal`, jenis fasilitas yang diawasi
`jenis_sarana`.

`legal` punya nilai sentinel berupa tanda hubung. Lihat `90-kualitas-data.md`.

## `klasifikasi_sarana` — bentuk fisik ritel/gudang

Kolom terpisah lagi, berisi klasifikasi seperti ritel modern, ritel tradisional, gudang
importir/distributor, gudang e-commerce. **Keterisiannya kondisional** — hanya relevan untuk
sebagian populasi distribusi. Sebelum memakainya sebagai penyaring, baca
`11-klasifikasi-distribusi.md` dan `90-kualitas-data.md`.

## UPT / balai pemeriksa

`nama_upt` adalah unit yang melakukan pemeriksaan. Istilah pengguna "UPT", "balai", "loka", "BPOM
di kota X" semuanya menunjuk kolom ini.

Tiga bentuk nilai yang harus dibedakan:

| Bentuk | Contoh pola | Perlakuan |
|---|---|---|
| Balai / Balai Besar | `BALAI BESAR POM DI …`, `BALAI POM DI …` | unit wilayah normal |
| Loka | `LOKA POM DI KAB…` / `LOKA POM DI KOTA…` | unit wilayah normal |
| **Direktorat** | `DIREKTORAT PENGAWASAN …` | **unit pusat** — bukan balai, tidak punya wilayah kerja maupun target |
| **Akun uji** | nama bergaya demo/percobaan | **buang** dari semua hitungan |

Peringkat "balai mana yang paling banyak" harus mengeluarkan direktorat dan akun uji, atau
menyebutkannya terpisah. Lihat `00-menghitung.md` §3.

Penulisan `nama_upt` di tabel fakta memakai **huruf besar**, sedangkan tabel target memakai
huruf campuran — konsekuensinya ada di `85-target-capaian.md`.

Wilayah kerja balai (kabupaten/kota mana saja yang menjadi tanggung jawabnya) ada di
`coverage_balai`. Itu **bukan** lokasi sarana; lokasi sarana ada di `provinsi` dan
`kabupaten_kota` pada tabel fakta.

## Wilayah di tabel kriteria berbeda dari tabel fakta

`mv_kriteria_pemeriksaan.kabupaten` menulis nama lengkap berawalan (`Kabupaten …`), sedangkan
kolom wilayah di tabel fakta memakai bentuk lain. Keduanya **tidak bisa dijoin langsung**.

Tabel kriteria hanya mencakup sebagian kecil pemeriksaan, jadi wilayah dari sana **bukan** wakil
populasi. Untuk pertanyaan wilayah, pakai kolom di tabel fakta.

## Cara memperoleh nilai `legal`

`legal` menyimpan bentuk legalitas sarana. Nilainya banyak dan penulisannya tidak bisa ditebak dari
istilah pengguna — pengguna menyebut "berizin", "punya NIB", "PIRT", sedangkan kolomnya memakai
bentuk sendiri.

Cara kerjanya, bukan hafalan:

1. Ambil daftar nilainya lebih dulu — `SELECT DISTINCT legal FROM mv_pemeriksaan` (jalur P2).
2. Kenali nilai mana yang masuk keluarga yang diminta pengguna.
3. Filter dengan himpunan nilai persis itu, disalin apa adanya dari hasil probe.

Jangan mengetik nilai dari ingatan dan jangan memakai pencarian kata bebas: sebagian nilai memuat
kata yang sama dengan nilai lain, sehingga pola kata akan menarik kelompok yang tidak diminta.

## Rute

- Pertanyaan menyebut BUPN, importir, notifikasi, ritel: buka `11-klasifikasi-distribusi.md`.
- Menyebut MD, IRT, AMDK, jenis pangan: buka `50-jenis-pangan.md`.
- Menyebut komoditi: buka `20-komoditi.md`.
- Menyebut target atau capaian: buka `85-target-capaian.md`.

---

<!-- MANIFES
tabel: coverage_balai, mv_kriteria_pemeriksaan
kolom: jenis_sarana, kabupaten, kabupaten_kota, klasifikasi_sarana, komoditi, legal, nama_upt, provinsi, sarana
nilai: APOTEK, DISTRIBUSI, KIOS / WARUNG, KOSMETIK, PANGAN, PANGAN IRT (CPPB - IRT), PANGAN MD, PBF, PELAYANAN, PRODUKSI, PUSAT KESEHATAN MASYARAKAT (PKM), SWALAYAN / MINI MARKET / SUPER MARKET, TOKO, TOKO OBAT
-->
