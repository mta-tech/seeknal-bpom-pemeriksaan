Temuan produk — apa yang ditemukan saat pemeriksaan, dan tindakannya.

## Dua tabel, dua bentuk

| Tabel | Grain | Pakai untuk |
|---|---|---|
| `mv_pemeriksaan_temuan` | satu baris per produk temuan | rincian produk, nilai, negara, tindakan |
| `mv_pemeriksaan_kategori_temuan` | satu baris per kategori temuan | **menghitung per kategori** |

Keduanya menempel ke fakta lewat `id_pemeriksaan`.

PENTING: **Kolom `tp_kategori` ada di kedua tabel dengan bentuk berbeda.** Di tabel temuan, satu baris
bisa memuat **beberapa kategori tergabung dalam satu teks berkoma**. Di tabel kategori_temuan,
kategori sudah dipecah menjadi nilai tunggal per baris.

> Untuk pertanyaan **"kategori temuan apa yang paling banyak"**, pakai
> `mv_pemeriksaan_kategori_temuan`. Memakai `tp_kategori` di tabel temuan memecah satu kategori
> menjadi banyak kombinasi berkoma dan merusak peringkat.

Tabel kategori_temuan pun masih menyisakan sedikit nilai berkoma; bila peringkatnya harus rapi,
sebutkan bahwa sebagian kecil nilai masih gabungan.

## Kategori temuan — istilah pengguna

Nilai kategorinya berupa label panjang. Ambil daftarnya lebih dulu (jalur **P2**), lalu ikat:

| Istilah pengguna | Cara mengikat |
|---|---|
| **TIE** / tanpa izin edar / ilegal | cari nilai yang memuat *TIE* atau *izin edar* — ada lebih dari satu penulisan |
| **kedaluwarsa** / ED / expired | cari nilai yang memuat *kedaluwarsa* atau *expire* — ada beberapa varian ejaan |
| **bahan berbahaya** / BKO | cari nilai yang memuat *bahan berbahaya*, *dilarang*, atau *BKO* — beberapa nilai berbeda menunjuk konsep yang sama |
| **rusak / substandard** | cari nilai yang memuat *rusak* |
| **lain-lain** | ada beberapa penulisan berbeda (*Lain - Lain*, *Lain-lain*) — sertakan semuanya |

**Selalu perlakukan ini sebagai keluarga nilai, bukan satu nilai.** Ejaan bervariasi (spasi,
tanda hubung, huruf besar-kecil), dan memilih satu penulisan saja melewatkan sebagian populasi.

## Tindakan atas produk

`tp_tindakan` memuat tindakan yang diambil (pemusnahan, pengamanan, dikembalikan ke
produsen/importir, penarikan, pendataan, dan lain-lain). Kolom ini juga **bisa memuat beberapa
tindakan berkoma** dalam satu baris — perlakukan seperti `tp_kategori`.

Pertanyaan "produk kategori X tetapi tidak dimusnahkan/diamankan" memerlukan kombinasi kategori
dan tindakan; keduanya multi-nilai, jadi pakai pencocokan pola, bukan kesamaan persis.

## Kolom lain di tabel temuan

| Kolom | Isi | Catatan |
|---|---|---|
| `product_name`, `product_register`, `product_brands` | identitas produk | teks bebas |
| `registrar` | pendaftar produk | teks bebas, keterisian tidak penuh |
| `tp_negara` | negara asal | **teks bebas** — lihat `41-nilai-dan-negara.md` |
| `tp_jml_temuan`, `tp_harga`, `tp_harga_total` | kuantitas dan nilai | **tercemar** — lihat `41-nilai-dan-negara.md` |
| `tp_expire` | tanggal kedaluwarsa produk | keterisian sebagian |
| `tp_pelanggaran`, `tp_netto` | **praktis kosong seluruhnya** | jangan dipakai sebagai penyaring |

PENTING: Dua kolom terakhir terdaftar di dokumentasi lama seolah punya kategori nilai. Di database ini
keduanya kosong. Memfilternya menghasilkan nol baris tanpa error.

## Hubungan dengan vonis

Hanya sebagian pemeriksaan menghasilkan temuan. `INNER JOIN` ke tabel temuan **menjatuhkan
mayoritas pemeriksaan** — untuk pertanyaan populasi, LEFT JOIN dari fakta. Dan seperti dicatat di
`30-kesimpulan.md`, temuan dan vonis `TMK` adalah dua hal berbeda.

## Tabel kategori tidak selalu sejalan dengan tabel temuan

`mv_pemeriksaan_kategori_temuan` adalah bentuk terurai dari kategori temuan. ETL-nya **tidak
berjalan seiring** dengan tabel temuan induknya: untuk periode terbaru, banyak temuan tidak punya
baris kategori sama sekali.

Akibatnya pertanyaan "kategori temuan terbanyak" untuk periode berjalan bisa mengembalikan nyaris
tidak ada apa-apa, dan perbandingan antar tahun akan menampilkan penurunan tajam yang sebenarnya
berasal dari ETL, bukan dari kegiatan.

Aturan: sebelum memakai tabel ini untuk periode mana pun, hitung dulu berapa temuan pada periode
itu yang punya baris kategori. Bila porsinya kecil, jawab sebagai keterbatasan data, bukan sebagai
penurunan. Alternatifnya, ambil kategori dari kolom array di tabel temuan induk dan normalisasi
sendiri.

## Rute

- Menyebut nilai rupiah atau negara asal: buka `41-nilai-dan-negara.md`.
- Menyebut kategori sarana distribusi: buka `11-klasifikasi-distribusi.md`.
- Menyebut vonis sarana: buka `30-kesimpulan.md`.

---

<!-- MANIFES
tabel: mv_pemeriksaan_kategori_temuan, mv_pemeriksaan_temuan
kolom: id_pemeriksaan, product_brands, product_name, product_register, registrar, tp_expire, tp_harga, tp_harga_total, tp_jml_temuan, tp_kategori, tp_negara, tp_netto, tp_pelanggaran, tp_tindakan
nilai: TMK
-->
