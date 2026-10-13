nilai temuan · harga · rupiah · kerugian · nilai ekonomi · negara · impor · asal · lokal · luar negeri

# Nilai ekonomi & asal produk

## Apa yang halaman ini putuskan

Dua kolom di bridge temuan menyimpan angka besar yang **tidak boleh dipakai mentah**, dan satu kolom
menyimpan asal produk yang sering disalahartikan.

## Tabel keputusan

| Kata dalam pertanyaan | Aksi |
|---|---|
| "nilai temuan" · "kerugian" · "rupiah" | agregasi kolom nilai, **dengan guard kualitas** |
| "jumlah fisik" · "banyaknya produk" | agregasi kolom kuantitas |
| "negara asal" · "impor" · "lokal" | kolom negara pada bridge temuan |
| "produk impor" | pakai kolom negara / penanda asal — **bukan** tebakan dari nama |

## Matriks operasi

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| `jumlah_temuan` | hanya penyaring bila memang diminta | boleh, dengan catatan kualitas | — | **sebut outlier** |
| `harga_total` | jangan jadi penyaring | boleh | — | **sebut outlier** |
| `negara` | normalisasi ejaan + kenali sentinel | gabungkan varian ejaan | — | periksa puncak daftar untuk sentinel |
| `tgl_expire` | tanggal masa depan **wajar** | — | — | — |

## Cara mencari — pemeriksaan kualitas sebelum menyajikan angka

```sql
-- statistik kualitas kolom angka
SELECT count(*) AS baris,
       min(jumlah_temuan), max(jumlah_temuan),
       count(*) FILTER (WHERE jumlah_temuan IS NULL) AS kosong
FROM public.bridge_pemeriksaan_temuan;

-- daftar "negara" yang muncul (termasuk sentinel berbentuk kata)
SELECT COALESCE(negara,'(kosong)') AS negara, count(*)
FROM public.bridge_pemeriksaan_temuan GROUP BY 1 ORDER BY 2 DESC LIMIT 20;
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| total nilai tidak masuk akal | satu/beberapa nilai sangat besar ikut terjumlah | tampilkan median + jumlah baris, atau batasi nilai |
| negara "tidak diketahui" menempati puncak | sentinel berupa kata dianggap negara | periksa daftar nilai sebelum memeringkat |
| satu negara terpecah banyak baris | varian ejaan/kapitalisasi | normalisasi |
| nilai negatif | cacat data | cek `min` dan sebutkan bila ada |

## Batas

- Nilai besar yang **sah** tetap ikut terjumlah; menyajikan `SUM` mentah tanpa catatan menyesatkan.
- Sebagian baris tidak mengisi nilai/kuantitas → sebutkan cakupannya.
- Tanggal kedaluwarsa boleh jatuh di masa depan — itu normal.

## Rute

- Kategori & grain temuan → **lihat** `40-temuan-produk.md`
- Kualitas data & sentinel → **lihat** `90-kualitas-data.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `bridge_pemeriksaan_temuan` | `jumlah_temuan`, `harga`, `harga_total`, `netto`, `negara`, `tgl_expire` | — |
| `dim_produk` | `produk_id`, `is_imported` | — |
