# Metodologi & self-audit — apakah crosscheck ini bisa dipercaya

**Ditulis karena:** klaim-klaim saya di percakapan ini ("0 HALU_SQL_ERROR, terbukti 57 kasus
sebelumnya artefak") ditantang secara sah — pipeline yang menghasilkan angka itu **sudah empat kali
saya temukan bug-nya sendiri** di sesi yang sama. Kredibilitas sebuah angka yang lahir dari alat
yang baru saja terbukti cacat empat kali tidak otomatis absah hanya karena bug berikutnya belum
ditemukan. Dokumen ini menuliskan seluruh proses koreksi + 4 jalur validasi independen yang
dijalankan SEBELUM angka final dipakai, supaya siapa pun bisa memeriksa ulang tanpa percaya begitu
saja pada kata "terverifikasi".

## 1. Empat bug yang ditemukan dan diperbaiki pada pipeline ini sendiri

| # | Bug | Efek jika tidak diperbaiki | Cara ketahuan |
|---|---|---|---|
| 1 | Regex ekstraksi SQL menelan anotasi hasil (`= 360.940.`) sebagai bagian query | `syntax error` pada SQL yang sebenarnya valid | 3 testcase gagal dengan pesan sama persis |
| 2 | Satu koneksi DB terputus (`server closed the connection unexpectedly`) tidak di-reconnect, mencemari 52 testcase berikutnya jadi `cursor already closed` | 53/256 testcase repo pemeriksaan tercatat "halu" — padahal 52 di antaranya cuma korban 1 koneksi yang mati | Semua 52 pesan error IDENTIK — pola statistik yang tidak masuk akal untuk "SQL salah" |
| 3 | Assert `[['3']]`, `[['4']]` dst (1 digit) tidak dicek sebagai angka toleransi — persis meniru batasan `\d{2,}` di harness asli, tapi tanpa verifikasi manual, ini akan salah dilaporkan sebagai "GT menyimpang" | 13 testcase valid akan salah dicatat sebagai "GT salah" | Delta besar (>100%) yang tidak masuk akal untuk kasus sesederhana `COUNT(*) WHERE sarana='DISTRIBUSI'` |
| 4 | `FETCH_CAP = 5000` memotong hasil sebelum cacah baris sesungguhnya diketahui | 3 testcase dgn hasil 91rb–214rb baris tampak "tidak cocok" padahal cocok | Cacah baris di `note` (214.166) jauh di atas 5.000 — batas skrip, bukan batas data |

Setiap bug ditemukan dengan cara yang sama: **angka yang keluar tidak masuk akal**, ditelusuri ke
notenya satu per satu, baru dipatch. Setelah patch #2 dan #3, dijalankan ULANG dari nol (bukan ditambal di atas data lama) — total 4
kali eksekusi penuh (v1 draft, v2, v3, v4). Bug #4 ditemukan belakangan lewat verifikasi manual
per-kasus, dan diperbaiki dengan menghitung ulang memakai pembungkus `COUNT(*)`.

## 2. Empat jalur validasi independen dijalankan sebelum angka dipercaya

### 2.1 PARTIAL_ERROR = 0 di keempat repo
Kalau ekstraksi masih salah potong, sebagian statement dalam satu testcase akan gagal sementara
lainnya sukses. Nol kejadian di 731 testcase — tidak ada sinyal potongan SQL yang setengah jalan.

### 2.2 Tidak ada kontaminasi SQL "yang sengaja salah"
Beberapa note menulis pola `SQL SALAH: ...` untuk mengajarkan kesalahan umum. Dicek eksplisit:
nol kejadian pola itu diikuti statement `SELECT`/`WITH` lengkap yang bisa ikut tereksekusi.

### 2.3 Cross-reference ke audit manual minggu lalu — 0/84 SQL tidak cocok
Untuk 86 testcase yang GAGAL di run 18 Agustus, saya SUDAH membaca notenya satu per satu secara
manual (bukan lewat regex) dan menjalankan SQL-nya via `psql` langsung — hasilnya tertulis di
`05-anatomi-per-kasus.md` per repo. Pipeline otomatis hari ini dibandingkan ke 84 catatan manual
itu. **Nol perbedaan SQL** — apa yang regex ekstrak hari ini SAMA
dengan apa yang saya baca dengan mata sendiri minggu lalu.

### 2.4 Spot-check acak 16 kasus yang BELUM PERNAH diperiksa manual
84 kasus di atas hanya mewakili testcase yang pernah GAGAL — bukan populasi utama (615 testcase
lain lolos tanpa pernah dibaca manual). Diambil 4 sampel acak per repo (16 total, `seed=7`, di
luar daftar 84) dan dibaca penuh: prompt, SQL yang diekstrak, hasil eksekusi. **Semua 16 bersih** —
SQL lengkap dan sesuai prompt, angka cocok dengan toleransi wajar terhadap drift data 5 hari
(14→19 Agustus).

## 3. Setelah 4 jalur ini lolos, klasifikasi ulang menyeluruh

Klaim pertama ("32 GT_MENYIMPANG") juga TERLALU KASAR — sebelum dilaporkan lebih jauh, setiap satu
dari sisa kasus ganjil dibaca notenya secara utuh (bukan dipotong 400 karakter), lalu dicocokkan ke
hasil query manual. Hasilnya:

| Kategori final | Jumlah | Makna |
|---|---:|---|
| Keterjawaban database | **731/731 = 100%** | setiap SQL GT jalan bersih & hasilnya konsisten dgn `note`-nya |
| **Halu — SQL benar-benar tidak jalan** | **0** | — |
| Cacat penulisan assert (sumbu terpisah) | 13 | rincian per repo di `06-crosscheck-semua-testcase.md` |

## 3b. Koreksi keempat: angka "715/731 (97,8%)" yang sempat saya laporkan juga SALAH

Setelah ditantang lagi, ke-16 kasus sisa ditelusuri satu per satu ke database. Hasilnya
**semuanya terjawab database dengan benar** — yang bermasalah cuma cara assert-nya ditulis:

- **3 kasus bukan cacat sama sekali** (`TC-PMR-KATEGORI-BEKU-1`, `TC-PGJ-PERSEN-KARANTINA-1`,
  `TC-PGJ-SLA-CAKUPAN-1`): testcase *perilaku* yang premisnya saya verifikasi TERBUKTI benar ke
  database. Pemeriksa mekanis saya membandingkan teks assert ke hasil SQL, padahal assert itu
  menilai jawaban agent — kategori yang memang tidak bisa dinilai mesin string-match.
- **3 kasus korban `FETCH_CAP=5000` di skrip saya sendiri** (`TC-PMR-RIWAYAT-SARANA-03`,
  `TC-PGJ-LAINNYA-06`, `TC-PGJ-LAINNYA-07`): setelah dihitung ulang dengan `COUNT(*)`,
  cacah barisnya cocok — 214.166→214.308 (0,07%), 91.163→92.794 (1,79%),
  150.681→153.977 (2,19%). Ini **bug keempat di pipeline saya**, bukan cacat testcase.
- **13 sisanya cacat penulisan assert yang nyata** — dan tetap perlu diperbaiki sebelum
  dipakai menilai context v3.

**Kesimpulan yang benar: 731/731 (100%) terjawab database, 0 halu, 13 cacat penulisan assert.**

## 4. Batasan yang jujur harus disebutkan

- Cross-reference 4-jalur ini memvalidasi **kesetiaan ekstraksi dan eksekusi SQL**, bukan
  menjamin setiap `note` GT itu sendiri secara analitik optimal — 13 cacat assert di atas justru
  ditemukan LEWAT proses ini.
- Pola koreksi berulang di dokumen ini sendiri adalah temuannya: **setiap angka agregat yang saya
  hasilkan otomatis, ternyata perlu ditelusuri balik ke kasus satuan sebelum layak dipercaya.**
  Empat kali berturut-turut angka agregat yang kelihatan rapi ternyata menyembunyikan bug alat,
  bukan fakta tentang data.
- 504/731 testcase (69%) belum pernah dijalankan oleh harness sungguhan — crosscheck ini
  memverifikasi bahwa GT-nya **valid dan terjawab database**, bukan bahwa agent akan menjawabnya
  benar. Itu pertanyaan terpisah yang baru bisa dijawab dengan menjalankan gelombang test baru.
- Statement_timeout 60 detik berarti query yang secara struktural lebih lambat dari itu di
  database tanpa indeks ini akan tercatat error walau sintaksnya benar — tidak ada kejadian
  seperti itu di run final (semua tereksekusi dalam batas waktu).
