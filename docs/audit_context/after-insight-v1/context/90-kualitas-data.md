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

`nama_sarana`, `nama_produk`, `registrar`, `tp_negara` diisi bebas. Satu entitas yang sama muncul
dengan beberapa penulisan (huruf besar-kecil, spasi ganda, prefiks badan usaha ikut/tidak,
kadang alamat ikut tertulis di dalam nama).

> Peringkat berdasarkan kolom teks bebas **tidak sahih tanpa normalisasi**. Bila memeringkat,
> sebutkan bahwa varian penulisan digabungkan — atau bahwa tidak digabungkan.

Pola kerjanya: `ILIKE` **sekali** untuk menemukan varian (jalur **P3**), lalu hitung dengan
himpunan nilai persis.

Perhatikan juga bahwa kolom teks bebas bisa memuat **sentinel berbentuk kalimat** (frasa yang
artinya "tidak ada data"). Ia akan tampil di puncak peringkat seolah entitas nyata. Periksa
puncak daftar sebelum menyajikannya.

## 6. Menyebutkan cakupan di jawaban

Bila kolom yang dipakai punya keterisian rendah pada populasi yang ditanya, **sebutkan porsinya
sebelum menyajikan peringkat atau persentase**. Tanpa itu, pembaca mengira jawabannya mencakup
seluruh populasi.

Kalimatnya cukup satu baris, misalnya: *"dihitung atas pemeriksaan yang kolom ini terisi; sebagian
besar pemeriksaan tidak memakai skema ini."*

## Rute

- Kembali ke aturan hitung → **naik** ke `00-menghitung.md`.
- Menyebut batas domain → **seberang** `95-batas-domain.md`.
