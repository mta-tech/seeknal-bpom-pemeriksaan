# Varian `after-insight-v1` — domain `pemeriksaan`

**Dibuat:** 14 Agustus 2026 · **Status:** belum dijalankan terhadap suite.
**Basis:** seluruh temuan di `docs/temuan_database/` — hasil profiling live, eksekusi 213 pair
`context_stores`, dan 27 `SQL Training` dari `BPOM User Relevant Query`.
**Pola penyusunan:** mengikuti `seeknal-bpom-neo/docs/context_recap/after-chart-route/route-context-070826-v6`
— dokumen orkestrator yang **merutekan dan menggerbang**, aturan data dipecah ke halaman topik kecil.

Menggantikan struktur v1 (`predikat.md` + `filter_code_reference.md` + `data_architecture.md`),
bukan menambahinya.

---

## Cara varian ini disusun

```
after-insight-v1/
├── SEEKNAL_ASK.md          orkestrator: PAGE MAP + Gate 0-5
├── seeknal_agent.yml       hanya blok prompt.custom yang diubah dari v1
├── context/                15 halaman topik
│   ├── 00-menghitung.md            WAJIB tiap pertanyaan data
│   ├── 10-sarana-dan-fasilitas.md  `sarana` vs `jenis_sarana`, UPT
│   ├── 11-klasifikasi-distribusi.md BUPN/importir, filter tersembunyi
│   ├── 20-komoditi.md              nilai + jembatan ke target
│   ├── 30-kesimpulan.md            MK/TMK/TDP/TTP + sentinel teks
│   ├── 31-status-dan-alur.md       status, log, batas soal "siapa menyetujui"
│   ├── 40-temuan-produk.md         dua tabel temuan, kategori multi-nilai
│   ├── 41-nilai-dan-negara.md      pembersihan nilai, definisi impor
│   ├── 50-jenis-pangan.md          MD/IRT ada di kolom mana
│   ├── 60-mutu-dan-tindak-lanjut.md grade, kriteria, CPOB, dua kolom tindak lanjut
│   ├── 70-petugas.md               beban kerja, kolom bernama tertukar
│   ├── 80-waktu-dan-durasi.md      tiga kolom tanggal, tanggal kotor, periode parsial
│   ├── 85-target-capaian.md        tiga batas struktural target
│   ├── 90-kualitas-data.md         sentinel, kekosongan bermakna, teks bebas
│   └── 95-batas-domain.md          NOT COVERED + salah rute antar domain
└── skills/
    ├── bpom-analyst/       DITULIS ULANG (v2.0.0)
    ├── visualize-chart/    salinan verbatim dari v1
    ├── bpom-forecaster/    salinan verbatim dari v1
    └── detect-anomaly/     salinan verbatim dari v1
```

**Aturan chart, ekspor S3, forecast, dan anomaly tidak diubah sama sekali.** Ketiga skill itu
disalin byte-identik dari v1, dan blok terkait di `SEEKNAL_ASK.md` Gate 0 & Gate 5 disalin
verbatim. Yang berubah hanya domain bisnisnya.

Pada `seeknal_agent.yml`, hanya `prompt.custom` yang diubah; blok `agent`, `sources`, dan
`agent_harness` byte-identik dengan v1 (terverifikasi lewat diff).

---

## Prinsip yang membedakannya dari v1

**1. Merutekan, bukan menimbun.** v1 menyuruh membaca dua berkas besar setiap turn. v2 membuka
`00-menghitung.md` selalu, lalu hanya halaman yang kondisinya menyala. Membuka halaman gratis;
query yang mahal.

**2. Mengajarkan pemetaan, bukan angka.** Halaman-halaman ini **tidak memuat satu pun cacah baris,
persentase, atau nilai agregat**. Yang diajarkan: konsep pengguna ada di kolom mana, kode filternya
apa bentuknya, istilahnya berarti apa, dan jebakannya di mana. Angka apa pun harus datang dari SQL
turn itu — bukan dari ingatan context.

Alasannya: angka bergeser setiap ETL berjalan. Context yang memuat angka akan menua menjadi salah,
dan lebih buruk lagi — mengundang agent menjawab dari ingatan alih-alih dari query.

**3. Kekosongan diperlakukan sebagai makna, bukan cacat.** Beberapa kolom di domain ini kosong
secara **deterministik** untuk kelompok tertentu. Menyaring "yang terisi" pada kolom seperti itu
adalah penyempitan populasi yang tidak diminta. `90-kualitas-data.md` mendaftarnya dan memberi cara
mengenali pola itu pada kolom baru.

**4. Batas domain ditulis eksplisit.** `95-batas-domain.md` mendaftar konsep yang **tidak ada** di
sini beserta domain yang menanganinya, supaya pertanyaan salah rute dijawab jujur — bukan dijawab
dengan kolom terdekat yang namanya mirip.

---

## Temuan yang menjadi alasan tiap halaman

| Halaman | Temuan yang mendasarinya |
|---|---|
| `10-sarana-dan-fasilitas` | Kolom rantai pengawasan berpindah nama antar generasi skema; aturan warisan masih menunjuk kolom lama. Pair historis yang memakainya mengembalikan nol baris tanpa error |
| `11-klasifikasi-distribusi` | Keterisian kolom terbukti terkunci pada irisan sarana×komoditi tertentu — `IS NOT NULL` di sana setara memfilter kelompok |
| `20-komoditi` | Join ke tabel target lewat kolom mentah kehilangan banyak pasangan; kolom jembatan wajib. Ejaan komoditi berbeda dari tiga domain lain |
| `30-kesimpulan` | Sentinel berupa teks empat huruf; dua kode berarti "pemeriksaan tidak terjadi" dan mencemari denominator kepatuhan |
| `31-status-dan-alur` | Semantik kolom pelaku di log terbukti ambigu — kesimpulan "self-approve" dari sana terbantah setelah diuji |
| `40-temuan-produk` | Kolom kategori hadir di dua tabel dengan bentuk berbeda; dua kolom yang terdaftar di dokumentasi lama ternyata kosong |
| `41-nilai-dan-negara` | Pencilan salah input mendominasi jumlah nilai; definisi impor "bukan Indonesia" menarik sentinel dan penanda lokal |
| `50-jenis-pangan` | Penanda MD/IRT ada di kolom jenis fasilitas, bukan komoditi — penyebab tunggal sekelompok pair gagal |
| `60-mutu-dan-tindak-lanjut` | `grade` terkunci satu jenis sarana; kolom cacah isu bukan jenis isu; dua kolom tindak lanjut berbeda cakupan |
| `70-petugas` | Kolom bernama sama dengan tabel fakta membawa konsep berbeda |
| `80-waktu-dan-durasi` | Tanggal kotor termasuk tanggal masa depan; sebagian baris tanpa tanggal dan tidak masuk kubus |
| `85-target-capaian` | Target hanya satu tahun, tidak mencakup semua rantai sarana, dan nama balai beda kapitalisasi |
| `90-kualitas-data` | Empat bentuk sentinel berbeda; enam kolom dengan kekosongan deterministik; teks bebas bervarian |
| `95-batas-domain` | Pertanyaan pengguna terbukti salah rute antar domain; beberapa konsep diminta berulang tetapi kolomnya tidak ada |

---

## Yang wajib diperiksa saat pilot

| Metrik | Gerbang |
|---|---|
| PASS suite yang ada | **tidak turun** |
| Jawaban pada skenario yang sudah benar | **nol yang bergerak** |
| SQL per turn | **tidak naik** — v2 memindahkan biaya dari query ke pembacaan halaman |
| Pertanyaan yang seharusnya NOT COVERED | dijawab jujur, **bukan** dengan kolom terdekat |
| Jawaban yang memakai kolom berketerisian rendah | **menyebut cakupannya** |

⚠️ Dua hal yang tidak akan tertangkap suite mana pun: apakah cakupan benar-benar disebut di
kalimat jawaban, dan apakah kolom yang dipilih benar secara makna ketika dua kolom sama-sama
menghasilkan angka yang masuk akal. Keduanya perlu pembacaan manual atas jawaban.
