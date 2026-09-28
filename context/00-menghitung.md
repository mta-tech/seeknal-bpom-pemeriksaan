pemeriksaan · inspeksi · sarana · temuan · petugas · berapa · jumlah · periode · tanggal

# Cara menghitung — entity, grain, tanggal, eksklusi

Berlaku untuk **setiap** pertanyaan data di domain ini.

## Apa yang halaman ini putuskan

Apa yang dihitung (entity), seberapa halus (grain), kolom tanggal mana yang dipakai, dan baris mana
yang wajib dibuang — sebelum satu baris SQL ditulis.

## Tabel keputusan — kata pertanyaan menentukan entity

| Kata dalam pertanyaan | Entity | Tanggal kanonik |
|---|---|---|
| pemeriksaan · inspeksi · kunjungan · kegiatan | `COUNT(DISTINCT fact_pemeriksaan.id)` | `tgl_start` |
| sarana · fasilitas · pabrik · apotek · toko (sebagai objek) | `COUNT(DISTINCT sarana_id)` | `tgl_start` |
| temuan produk — **kasus terdampak** | `COUNT(DISTINCT pemeriksaan_id)` | `tgl_start` |
| temuan produk — **baris/entri** | `COUNT(*)` pada bridge temuan | `tgl_start` |
| penugasan petugas | `COUNT(*)` pada bridge petugas | `tgl_start` |
| item/klausul tidak sesuai (produksi) | `COUNT(*)` pada bridge checklist | dari kasus induk |

**Entity ≠ sarana.** Satu sarana bisa diperiksa berkali-kali; "berapa sarana yang diperiksa" berbeda
dari "berapa pemeriksaan". Bila pertanyaannya tidak jelas → Gate 1.

## Matriks operasi — kolom yang sering salah dipakai

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| `id` | biasa | biasa | kunci ke seluruh bridge (`pemeriksaan_id`) | biasa |
| `sarana_id` | biasa | `COUNT(DISTINCT)` untuk sarana unik | ke `dim_sarana.sarana_id` | biasa |
| `tgl_start` | **rentang berbatas**, bukan `EXTRACT` | `date_trunc` boleh untuk melabeli hasil | — | biasa |
| `jenis_id` | butuh kamus + `type` | butuh kamus + `type` | `dim_master_data` dengan `type='JENIS_SARANA'` | biasa |
| `is_data_uji` | **eksklusi wajib** saat membahas kegiatan nyata | biasa | — | — |
| `flag_varian_datas` | penentu bridge | bermanfaat untuk audit cakupan | — | — |

## Cara mencari bila nilainya tidak stabil

```sql
-- 1. pastikan rentang tanggal yang benar-benar terisi
SELECT min(tgl_start), max(tgl_start), count(*) FILTER (WHERE tgl_start IS NULL)
FROM public.fact_pemeriksaan;

-- 2. nilai yang dipakai untuk menyaring (jangan hafal)
SELECT DISTINCT jenis_id FROM public.fact_pemeriksaan ORDER BY 1;
```

## Eksklusi wajib

| Apa | Aturan | Alasan |
|---|---|---|
| data uji | `is_data_uji IS NOT TRUE` | bukan kegiatan nyata |
| unit pusat pada hitungan per-balai | tidak dibuang sebagai baris, tapi **dibedakan** dari balai wilayah | pusat tidak punya wilayah kerja |
| baris temuan yang diklaim final | `is_kasus_draft = false` | angka final |

### Uji satu kalimat sebelum menambah `WHERE` apa pun

> **Apakah baris yang dibuang klausa ini bisa menjadi jawaban yang benar?**
> **Bisa → itu PENYEMPITAN**, dan penyempitan hanya sah bila pertanyaan memintanya.
> **Tidak bisa → itu EKSKLUSI**, dan boleh selalu.

Kolom yang kosong **tidak lolos** uji ini: baris berkolom kosong tetap pemeriksaan sungguhan dan ikut
dihitung, kecuali pertanyaannya memang tentang kolom itu.

## Bentuk angka

- **Angka utama dari query globalnya sendiri**, bukan penjumlahan partisi.
- Setelah join ke bridge, penjumlahan per kelompok bisa melebihi total — satu pemeriksaan muncul di
  beberapa kelompok.
- Satu statement per panggilan, tanpa `;`.
- Scope yang sudah disetujui harus **terlihat di SQL**, bukan hanya di kalimat jawaban.

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| angka ±2× lipat | `COUNT(*)` setelah join ke bridge, lalu disebut jumlah pemeriksaan | pakai `COUNT(DISTINCT` pada id fakta |
| total tidak sama dengan penjumlahan bagian | bagian dihitung dari query berbeda / pengelompokan ganda | hitung ulang angka utama dari query globalnya sendiri |
| hasil kosong padahal kasusnya ada | membaca bridge yang salah varian | periksa `flag_varian_datas` (`01`) |
| filter periode menghilangkan banyak baris | memakai `EXTRACT` di `WHERE`, atau kolom administrasi alih-alih kolom kegiatan | pakai rentang berbatas pada kolom kegiatan |
| populasi menyusut tanpa diminta | menambahkan penjaga keterisian kolom yang tidak diminta pertanyaan | terapkan uji penyempitan vs eksklusi di atas |

## Batas & honest gap

- Sebagian kasus tidak punya tanggal kegiatan → tidak pernah masuk hitungan berbasis periode;
  **hitung keterisiannya** dan sebutkan bila pertanyaannya tentang total populasi.
- Satu kasus bertanggal jauh ke depan (jadwal terjadwal) itu **valid**, bukan data kotor.

## Rute

- Butuh tahu tabel/bridge mana → **lihat** `01-peta-data-dan-routing.md`
- Menyentuh kekosongan kolom → **lihat** `90-kualitas-data.md`
- Entity berupa aspek/klausul → **lihat** `35` / `37`
- Entity berupa produk → **lihat** `40`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `fact_pemeriksaan` | `id`, `sarana_id`, `jenis_id`, `tgl_start`, `tgl_end`, `is_data_uji`, `flag_varian_datas` | — |
| `bridge_pemeriksaan_temuan` | `pemeriksaan_id`, `is_kasus_draft` | — |
| `bridge_pemeriksaan_petugas` | `pemeriksaan_id` | — |
