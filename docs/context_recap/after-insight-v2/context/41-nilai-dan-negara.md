Nilai temuan dan negara asal — dua kolom yang tidak bisa dipakai mentah.

## Nilai temuan — WAJIB dibersihkan sebelum dijumlahkan

Kolom `tp_harga` (satuan) dan `tp_harga_total` (nilai keseluruhan) di `mv_pemeriksaan_temuan`
memuat **pencilan ekstrem** dari salah input: sebagian baris menaruh sesuatu yang jelas bukan
kuantitas di `tp_jml_temuan` (misalnya rangkaian angka berpola tanggal), lalu dikalikan harga
sehingga totalnya meledak.

Satu baris seperti itu bisa **mendominasi seluruh jumlah nasional**. Menjumlahkan kolom ini apa
adanya menghasilkan angka yang salah besaran, bukan sekadar sedikit meleset.

> **Aturan:** setiap penjumlahan nilai temuan menyaring pencilan lebih dulu — buang baris yang
> `tp_jml_temuan`-nya di luar batas wajar sebagai kuantitas, dan baris yang `tp_harga_total`-nya
> di luar batas wajar sebagai nilai satu temuan. **Sebutkan di jawaban** bahwa pencilan dibuang
> dan berapa banyak barisnya.

Cara menemukan ambangnya: urutkan `tp_harga_total` menurun dan lihat di mana deretnya patah;
lakukan hal sama untuk `tp_jml_temuan`. Jangan memakai ambang dari ingatan — ETL menambah baris
tiap hari.

Jangan pernah menyajikan angka finansial tanpa menyebut pembersihannya. Pembaca tidak punya cara
tahu bahwa satu baris salah input menggeser totalnya.

## `tp_negara` — teks bebas, bukan kode

Kolom ini diisi bebas oleh petugas. Akibatnya:

| Masalah | Bentuknya |
|---|---|
| **Banyak ejaan untuk negara yang sama** | huruf besar/kecil/campur untuk nama yang sama |
| **Nama alternatif** | satu negara punya dua nama resmi berbeda dalam bahasa Indonesia |
| **Bukan negara** | sebagian baris berisi nama perusahaan lengkap dengan alamat |
| **Sentinel** | tanda hubung dan string kosong |
| **Penanda domestik non-negara** | kata yang berarti "lokal", dengan berbagai ejaan |

### Jangan pakai "bukan Indonesia" sebagai definisi impor

Filter `lower(tp_negara) <> 'indonesia'` **ikut menarik**:

- baris bersentinel (tanda hubung / kosong) — asalnya **tidak tercatat**, bukan impor;
- baris berpenanda **lokal** — justru domestik.

Keduanya bisa berjumlah besar dan membuat "temuan impor" jauh melebihi kenyataan.

> **Definisi yang benar:**
> **domestik** = nilai yang berarti Indonesia (semua ejaannya) **atau** berarti lokal (semua
> ejaannya) · **tidak tercatat** = sentinel dan NULL · **impor** = sisanya.

Laporkan porsi "tidak tercatat" sebagai kelompok tersendiri — tanpa itu, peringkat impor terlihat
lebih lengkap daripada kenyataannya.

### Sebelum memeringkat negara: normalisasi

Peringkat "negara asal terbanyak" **tidak sahih** tanpa menggabungkan ejaan. Minimal:

1. samakan huruf besar-kecil (`lower(trim(tp_negara))`);
2. gabungkan nama alternatif untuk negara yang sama;
3. keluarkan baris yang isinya nama perusahaan.

Cara menemukan varian: ambil daftar nilai terurut cacah menurun dan periksa manual — jalur **P3**.
Sebutkan di jawaban bahwa varian digabungkan.

## Frasa "tidak diketahui" adalah sentinel, bukan negara

Kolom negara diisi bebas, dan sebagian isinya bukan nama negara melainkan pernyataan bahwa
negaranya tidak diketahui. Frasa itu ditulis dalam beberapa bentuk: berbeda kapitalisasi, dan
berbeda pilihan kata — ada yang memakai kata "diketahui", ada "mencantumkan", ada "tercantum",
ada "ada keterangan".

Karena jumlahnya besar, frasa ini akan menempati peringkat atas seolah sebuah negara.

Aturan: sebelum memeringkat negara, kumpulkan dulu daftar nilainya, kenali seluruh anggota keluarga
"tidak diketahui", lalu keluarkan mereka dari peringkat dan laporkan porsinya terpisah. Jangan
mengandalkan satu ejaan saja.

Sebagian nilai juga berisi nama perusahaan atau kota, bukan negara. Kolom ini tidak bisa dipakai
untuk peringkat negara tanpa normalisasi eksplisit.

## Rute

- Kembali ke konsep temuan: buka `40-temuan-produk.md`.
- Menyebut kualitas data secara umum: buka `90-kualitas-data.md`.

---

<!-- MANIFES
tabel: mv_pemeriksaan_temuan
kolom: tp_harga, tp_harga_total, tp_jml_temuan, tp_negara
nilai: -
-->
