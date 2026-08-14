Kualitas data — sentinel, kekosongan yang bermakna, dan cara menyebutnya.

## 1. Sentinel: kosong tidak selalu berarti NULL

Database ini memakai beberapa bentuk penanda kosong, dan bentuknya **berbeda per kolom**:

| Bentuk | Di mana lazimnya |
|---|---|
| **SQL NULL** | kolom tanggal, kolom numerik, sebagian kolom teks |
| **string `'NULL'` (empat huruf)** | kolom vonis dan kolom status |
| **tanda hubung** | kolom teks isian bebas |
| **string kosong** | sebagian kolom teks |

> Karena itu `WHERE kolom IS NULL` **tidak cukup**. Untuk kolom vonis dan status, sentinel-nya
> berupa teks; `IS NULL` di sana mengembalikan nol baris dan menyembunyikan populasinya.

Cara aman sebelum memakai kolom sebagai penyaring: lihat daftar nilainya lebih dulu (jalur **P2**)
dan kenali bentuk kosongnya. Domain lain memakai ejaan sentinel yang berbeda — jangan menyalin
aturan dari sana (`95-batas-domain.md`).

## 2. Kekosongan yang berkorelasi dengan makna = FILTER TERSEMBUNYI

Kolom yang kosongnya **tidak acak** bukan cacat data — ia menandai sebuah kelompok. Menyaring
"yang terisi" pada kolom seperti itu **diam-diam memfilter kelompok tersebut**, tanpa error dan
tanpa jejak di kalimat jawaban.

Yang terbukti berperilaku begitu di domain ini:

| Kolom | Kosongnya berarti |
|---|---|
| `klasifikasi_distribusi` | bukan sarana distribusi pada komoditi yang memakai skema notifikasi |
| `klasifikasi_sarana` | tidak relevan bagi jenis sarana itu |
| `grade` | bukan jenis sarana yang dinilai dengan grade |
| `tingkat_pemenuhan_cpob` | bukan pemeriksaan berskema CPOB |
| `hp_followup_name` | bukan pemeriksaan berskema sertifikasi |
| `tx_*_issue` | formulir pemeriksaannya tidak memakai skema kritis/mayor/minor |

**Cara mengenalinya sebelum memakai kolom apa pun sebagai penjaga:** tanyakan **apa arti
kosongnya**. Bila kosong berarti "tidak berlaku bagi kelompok X" — bukan "datanya belum diisi" —
maka menyaringnya membuang kelompok X. Bila perlu diperiksa, **silangkan keterisiannya** dengan
kolom yang mendefinisikan kelompok itu (`GROUP BY sarana, komoditi` dengan `count(kolom)`), jangan
dihitung sendirian.

## 3. Kolom yang praktis kosong seluruhnya

Dua kolom di tabel temuan (`tp_pelanggaran`, `tp_netto`) terdaftar di dokumentasi lama seolah
punya himpunan nilai, tetapi di database ini **tidak terisi**. Memfilternya mengembalikan nol
baris tanpa error. Jangan dipakai.

**Pelajaran umumnya:** daftar nilai di dokumentasi lama adalah **sampel**, bukan bukti bahwa
kolomnya terisi. Sebelum memakai kolom yang belum pernah dipakai, periksa keterisiannya.

## 4. Baris tanpa tanggal kegiatan

Sebagian baris tidak punya tanggal mulai maupun selesai; hampir semuanya berstatus draft —
pemeriksaan yang dibuat tetapi belum dijalankan. Konsekuensinya:

- baris itu **tidak pernah** masuk hitungan berbasis periode;
- baris itu juga **tidak masuk** kubus `agg`, sehingga total dari kubus selalu sedikit di bawah
  total fakta.

Bukan kohort yang harus dibuang, tetapi harus **disebut** bila pertanyaannya tentang total populasi.

## 5. Teks bebas: satu entitas, banyak penulisan

Kolom teks bebas di domain ini: `nama_sarana` dan `nama_upt` di tabel fakta; `product_name`,
`product_brands`, `registrar`, `tp_negara`, `tp_keterangan` di tabel temuan; `petugas` di tabel
petugas. Satu entitas yang sama muncul dengan beberapa penulisan (huruf besar-kecil, spasi ganda,
prefiks badan usaha ikut/tidak, kadang alamat ikut tertulis di dalam nama).

> PENTING: **Penamaan kolom tidak konsisten antar tabel.** Tabel fakta memakai bahasa Indonesia
> (`nama_sarana`, `nama_upt`), sedangkan tabel temuan memakai bahasa Inggris (`product_name`,
> `product_register`, `product_brands`). Tidak ada kolom bernama `nama_produk` di database ini —
> menebak nama kolom dari pola tabel fakta akan menghasilkan SQL yang gagal. Bila ragu, ambil
> daftar kolomnya lebih dulu, jangan menebak.

> Peringkat berdasarkan kolom teks bebas **tidak sahih tanpa normalisasi**. Bila memeringkat,
> sebutkan bahwa varian penulisan digabungkan — atau bahwa tidak digabungkan.

Pola kerjanya: `ILIKE` **sekali** untuk menemukan varian (jalur **P3**), lalu hitung dengan
himpunan nilai persis.

Perhatikan juga bahwa kolom teks bebas bisa memuat **sentinel berbentuk kalimat** (frasa yang
artinya "tidak ada data"). Ia akan tampil di puncak peringkat seolah entitas nyata. Periksa
puncak daftar sebelum menyajikannya.

### Nama petugas — kembaran karena gelar

`petugas` menyimpan nama beserta gelar, dan cara menulis gelar tidak seragam: tanda titik
ada/tidak, spasi sesudah koma ada/tidak, gelar disingkat atau dipanjangkan, kadang ada spasi di
depan nama. Akibatnya satu orang tersimpan sebagai beberapa entri berbeda.

> **Aturan:** peringkat "petugas paling produktif" atau "siapa paling sering" **tidak sahih** dari
> kolom ini apa adanya — satu orang terpecah, dan yang penulisannya paling konsisten menang.
> Normalisasi dulu, dan sebutkan keterbatasan itu di kalimat jawaban.

### Nama balai punya spasi tersembunyi di ujung

Sebagian nilai nama balai tersimpan dengan **spasi menempel di belakang**. Karena spasi itu
konsisten di semua tabel yang memuat nama balai, join antar tabel tetap jalan — yang gagal adalah
**filter kesamaan persis**.

Menulis `nama_upt = 'BALAI POM DI …'` dengan nama yang disalin dari dokumen atau dari ingatan akan
mengembalikan **nol baris, tanpa pesan kesalahan** — seolah balai itu tidak punya data.

> **Aturan:** filter kesamaan persis pada nama balai wajib lewat `trim()` di kedua sisi, atau
> memakai nilai hasil probe `SELECT DISTINCT` **apa adanya** termasuk spasinya. Jangan pernah
> mengetik nama balai dari ingatan.

## 6. Menyebutkan cakupan di jawaban

Bila kolom yang dipakai punya keterisian rendah pada populasi yang ditanya, **sebutkan porsinya
sebelum menyajikan peringkat atau persentase**. Tanpa itu, pembaca mengira jawabannya mencakup
seluruh populasi.

Kalimatnya cukup satu baris, misalnya: *"dihitung atas pemeriksaan yang kolom ini terisi; sebagian
besar pemeriksaan tidak memakai skema ini."*

## Rute

- Kembali ke aturan hitung: buka `00-menghitung.md`.
- Menyebut batas domain: buka `95-batas-domain.md`.

---

<!-- MANIFES
tabel: -
kolom: grade, hp_followup_name, klasifikasi_distribusi, klasifikasi_sarana, nama_sarana, nama_upt, petugas, product_brands, product_name, product_register, registrar, tingkat_pemenuhan_cpob, tp_keterangan, tp_negara, tp_netto, tp_pelanggaran
nilai: -
-->
