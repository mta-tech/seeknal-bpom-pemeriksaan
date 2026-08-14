Klasifikasi sarana distribusi — BUPN, importir, dan kategori peredaran.

## Kolom

`klasifikasi_distribusi` memuat peran sarana dalam rantai peredaran. Nilainya berupa label panjang
huruf besar, antara lain badan usaha/usaha perorangan pemilik notifikasi kosmetik, importir
kosmetika, importir obat tradisional dan/atau suplemen makanan, distributor, sub distributor,
agen, grosir, pengecer, toko kosmetik/swalayan, toko obat/swalayan, depot jamu, klinik kecantikan,
salon/spa, stokist MLM, penjualan melalui media elektronik, dan lain-lain.

Karena labelnya panjang dan berubah-ubah, **jangan mengetiknya dari ingatan**. Ambil daftar
nilainya lebih dulu (`SELECT DISTINCT klasifikasi_distribusi …`), lalu pilih nilai persis — ini
jalur **P2** pada Gate 2.

## Terjemahan istilah pengguna

| Istilah pengguna | Cara mengikat |
|---|---|
| **BUPN** | Badan Usaha Pemilik Notifikasi — cari nilai yang memuat kata *notifikasi* |
| **importir** | cari nilai yang memuat kata *importir*; ada lebih dari satu (kosmetika, dan OT/suplemen) — sertakan semuanya kecuali pertanyaannya menyebut salah satu |
| **non-notif / selain BUPN** | kebalikan dari nilai bernotifikasi, **di dalam populasi yang kolomnya terisi** |
| **ritel modern / tradisional / gudang** | itu `klasifikasi_sarana`, bukan `klasifikasi_distribusi` — kolom berbeda |

## ⚠️ Kolom ini adalah FILTER TERSEMBUNYI

Keterisiannya **tidak acak**. Kolom ini praktis hanya diisi untuk **sarana distribusi pada
sebagian komoditi** (kosmetik, obat tradisional, suplemen kesehatan). Untuk sarana pelayanan,
sarana produksi, dan komoditi lain, kolom ini kosong seluruhnya.

Akibatnya:

> `WHERE klasifikasi_distribusi IS NOT NULL` **identik dengan** "sarana distribusi kosmetik / obat
> tradisional / suplemen saja" — itu penyempitan populasi, bukan pembersihan data.

**Aturan:** setiap jawaban yang memakai kolom ini **wajib menyebut cakupannya** — bahwa
pertanyaannya hanya berlaku pada sarana distribusi komoditi tertentu. Menyajikannya sebagai angka
nasional membuat pembaca mengira seluruh pemeriksaan tercakup.

Cara memeriksanya sebelum memakai: silangkan keterisian kolom ini dengan `sarana` dan `komoditi`
(`GROUP BY sarana, komoditi` dengan `count(klasifikasi_distribusi)`), lalu sebutkan hasilnya.

## Temuan produk per kategori sarana distribusi

Pertanyaan "temuan produk berdasarkan kategori sarana distribusi" menggabungkan kolom ini dengan
tabel temuan. Ingat dua hal: join ke tabel temuan **melipatgandakan** baris induk
(`00-menghitung.md` §1), dan nilai temuan perlu pembersihan (`41-nilai-dan-negara.md`).

## Rute

- Kembali ke konsep sarana → **naik** ke `10-sarana-dan-fasilitas.md`.
- Menyentuh temuan atau nilainya → **seberang** `40-temuan-produk.md`.
- Mempertanyakan arti kekosongan kolom → **seberang** `90-kualitas-data.md`.
