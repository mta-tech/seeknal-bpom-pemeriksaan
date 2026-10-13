TIE · tanpa izin edar · kedaluwarsa · rusak · substandard · BKO · obat keras · palsu · sitaan · dimusnahkan · diamankan · temuan produk · kategori temuan

# Temuan produk

## Apa yang halaman ini putuskan

Temuan produk hidup di `bridge_pemeriksaan_temuan`. Halaman ini memutuskan **grain mana yang dihitung**,
karena empat angka berbeda bisa dihasilkan dari tabel yang sama.

## Empat grain — pilih satu, jangan dicampur

| Yang ditanya | Hitungan |
|---|---|
| berapa **kasus/pemeriksaan** yang menemukan produk bermasalah | `COUNT(DISTINCT pemeriksaan_id)` |
| berapa **baris/entri** temuan | `COUNT(*)` |
| berapa **fisik produk** (kuantitas) | agregasi kolom kuantitas |
| berapa **nilai ekonomi** | agregasi kolom nilai |

Menyebut "jumlah temuan" tanpa grain → Gate 1.

## Tabel keputusan

| Kata dalam pertanyaan | Aksi |
|---|---|
| "TIE" · "tanpa izin edar" | kategori TIE |
| "kedaluwarsa" · "ED" | kategori kedaluwarsa |
| "rusak" · "substandard" | perlu keputusan penggabungan — lihat Jebakan |
| "BKO" · "obat keras" · "palsu" · "bahan berbahaya" | kategori masing-masing |
| "paling banyak" | `COUNT(DISTINCT pemeriksaan_id)` lalu urutkan |
| "berapa kali keputusan" | grain baris |

## Matriks operasi

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| `kategori_kode` (jsonb array) | **expand dulu** | expand lalu kelompokkan | kamus lewat **teks**: `master_data_id::text = elemen` | normalisasi/bucket dulu |
| `tindakan_kode` (jsonb array) | expand dulu | expand lalu kelompokkan | idem | biasa |
| `tp_product_id` | — | — | `dim_produk.produk_id` | biasa |
| `is_kasus_draft` | **buang** bila angka diklaim final | — | — | — |
| `jumlah_temuan` · `harga_total` | jangan jadi penyaring | jangan | — | pakai guard kualitas (`41`) |

## Cara mencari

```sql
-- nilai kategori yang benar-benar dipakai, dan mana yang TIDAK ada di kamus
SELECT e.kode,
       COALESCE(d.name, '(tidak di kamus)') AS nama,
       count(*) AS baris
FROM public.bridge_pemeriksaan_temuan t
CROSS JOIN LATERAL jsonb_array_elements_text(t.kategori_kode) e(kode)
LEFT JOIN public.dim_master_data d
       ON d.master_data_id::text = e.kode AND d.type = 'KATEGORI_TEMUAN_PRODUK'
GROUP BY 1, 2 ORDER BY 3 DESC;

-- sebaran grain
SELECT count(*) AS baris,
       count(DISTINCT pemeriksaan_id) AS kasus,
       count(DISTINCT (pemeriksaan_id, tp_product_id)) AS pasangan_unik
FROM public.bridge_pemeriksaan_temuan WHERE is_kasus_draft = false;
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| kategori kosong / nol | array tidak di-expand, atau join tanpa cast teks | bandingkan `jsonb_array_elements_text` + `::text` |
| angka kategori lebih kecil dari kenyataan | kode tidak ada di kamus → dibuang oleh INNER JOIN | pakai `LEFT JOIN` + bucket "(tidak di kamus)" |
| satu makna terpecah | ada beberapa kode untuk makna serupa di kamus | periksa daftar kamus & kode yang dipakai |
| angka draft ikut terhitung | `is_kasus_draft` tidak disaring | saring bila angka diklaim final |
| kategori berlabel aneh / ganda-makna | ada **alias/varian ketik** dari kode kamus, dan **kode yang tertukar tempat** (kode tindakan muncul di `kategori_kode`, sebaliknya di `tindakan_kode`) | jalankan query "nilai kategori" di atas; kanonikkan alias ke kode kamus sebelum agregasi; yang tak berkamus masuk bucket eksplisit dan **sebut jumlahnya** — jangan dibuang diam-diam |
| "jumlah temuan" raksasa | itu **kuantitas**, bukan jumlah kasus | tegaskan grain |

## Batas

- Kode kategori di data **lebih banyak** daripada di kamus, dan sebagian kamus tidak dipakai → jangan
  mengklaim seluruh kategori terpetakan.
- Istilah **"keamanan mutu"** pada produk = kelompok kode TMS Keamanan-Mutu-Gizi Pangan + bahan
  berbahaya (`220001`, `220131`–`220133`) — ketersediaannya baru pada periode terbaru; cek sebaran
  tahunnya dulu sebelum menarik tren (naik/turun bisa efek ketersediaan kode, bukan kejadian).
- `tp_asset` adalah id eksternal; tidak ada tabel targetnya → jangan dibangunkan lookup.
- Angka kuantitas/nilai punya nilai besar yang sah → `41`.

## Rute

- Nilai & kuantitas → **lihat** `41-nilai-dan-negara.md`
- Kategori sebagai dimensi panel → **lihat** `05-filter-katalog.md`
- Grain & eksklusi → **lihat** `00-menghitung.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `bridge_pemeriksaan_temuan` | `id`, `pemeriksaan_id`, `tp_product_id`, `kategori_kode`, `tindakan_kode`, `is_kasus_draft`, `jumlah_temuan`, `harga_total`, `tp_asset` | — |
| `dim_master_data` | `master_data_id`, `name`, `type` | `KATEGORI_TEMUAN_PRODUK`, `TL_PRODUK_TEMUAN` |
| `dim_produk` | `produk_id`, `nama_produk`, `nomor_registrasi` | — |
