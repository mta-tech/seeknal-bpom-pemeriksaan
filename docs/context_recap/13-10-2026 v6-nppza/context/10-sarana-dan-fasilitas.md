apotek · PBF · pangan · pangan MD · IRT · UMKM · toko obat · PKM · klinik · rumah sakit · sarana produksi · sarana distribusi · sarana pelayanan · balai · regional · wilayah

# Sarana, golongan, dan wilayah

## Apa yang halaman ini putuskan

Jenis sarana versus golongannya, identitas sarana, dan **wilayah mana** yang dimaksud pertanyaan.

## Tabel keputusan

| Kata dalam pertanyaan | Kolom / keputusan |
|---|---|
| apotek · PBF · toko obat · pangan · pangan MD · pangan IRT · kosmetik · obat tradisional · suplemen · klinik · PKM · rumah sakit | `jenis_id` → kamus `JENIS_SARANA` |
| "sarana produksi" · "sarana distribusi" · "sarana pelayanan" | **golongan**, bukan jenis: `parent_name` pada kamus `JENIS_SARANA` |
| nama sarana / pabrik / perusahaan tertentu | `sarana_id` → `dim_sarana.nama_sarana` (teks bebas → P3 probe) |
| "oleh BBPOM X" / "UPT X" | `balai_id` → `dim_balai.nama_balai` |
| "Regional X" | `dim_balai.regional_name` |
| "sarana di provinsi/kabupaten X" | `dim_sarana.provinsi_id` / `kabupaten_id` |
| "wilayah kerja UPT X" | **perlu definisi cakupan** → bila tidak tersedia: P5 |

## Tiga makna "wilayah" (jangan dicampur)

| Bahasa user | Arti | Kolom |
|---|---|---|
| oleh BBPOM Bandung | **pelaksana** pemeriksaan | `fact_pemeriksaan.balai_id` |
| Regional Semarang | kelompok operasional balai | `dim_balai.regional_name` |
| sarana di Bandung | **lokasi objek** | `dim_sarana.kabupaten_id` / `provinsi_id` |

Pertanyaan "temuan di Bandung" bisa berarti dua hal berbeda → Gate 1.

## Cara mencari

```sql
-- daftar jenis sarana + golongannya (jangan hafal)
SELECT master_data_id, name, parent_id, parent_name
FROM public.dim_master_data WHERE type = 'JENIS_SARANA' ORDER BY 1;

-- sebaran regional (pakai nama, bukan kode)
SELECT regional_name, count(*) FROM public.dim_balai GROUP BY 1 ORDER BY 2 DESC;

-- cari sarana berdasarkan nama (P3): ILIKE sekali untuk menemukan varian
SELECT sarana_id, nama_sarana FROM public.dim_sarana
WHERE nama_sarana ILIKE '%<kata>%' LIMIT 20;
```

## Matriks operasi

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| `nama_sarana` | teks bebas → probe dulu, lalu `=` pada nilai temuan | normalisasi sebelum dikelompokkan | ke `fact_pemeriksaan.sarana_id` | **peringkat tanpa normalisasi tidak sahih** |
| `regional_name` | langsung | langsung | dari `dim_balai` | pakai nama, bukan kode |
| `regional` (kode) | **jangan** | jangan | jangan | jangan — kode tidak konsisten |
| `parent_name` | filter golongan | grup utama | dari kamus jenis sarana | biasa |
| `dihapus_di_sumber` | flag, bukan eksklusi otomatis | — | — | — |

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| "sarana produksi" tidak mengembalikan apa pun | memfilternya di kolom jenis | itu golongan (`parent_name`), bukan jenis — pindah kolom |
| peringkat balai terlihat acak | memakai kolom `regional` (kode) | pakai `regional_name` |
| peringkat sarana terpecah | satu entitas punya beberapa penulisan | normalisasi; sebutkan bila tidak digabung |
| nama balai tidak ketemu | perbedaan spasi/kapitalisasi pada filter kesamaan | probe dulu, lalu saring dengan nilai hasil probe |

## Batas

- `dim_sarana` memuat baris soft-delete (`dihapus_di_sumber`); default: **tetap ikut**, kecuali
  pertanyaannya tentang sarana aktif.
- `provinsi_id`/`kabupaten_id` sebagian tidak ketemu kamus wilayah — nyatakan bila relevan.
- Jumlah jenis sarana yang benar-benar terpakai lebih sedikit dari isi kamus → jangan menyimpulkan
  "semua jenis" dari daftar kamus.

## Rute

- Komoditi → **lihat** `20-komoditi.md`
- Jenis pangan (MD/IRT/UMKM) → **lihat** `50-jenis-pangan.md`
- Target → **lihat** `85-target-capaian.md`
- Label panel sarana → **lihat** `05-filter-katalog.md`
- Kekosongan & soft-delete → **lihat** `90-kualitas-data.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `dim_sarana` | `sarana_id`, `nama_sarana`, `type_id`, `provinsi_id`, `kabupaten_id`, `dihapus_di_sumber` | — |
| `dim_balai` | `balai_id`, `nama_balai`, `regional_name`, `regional` | — |
| `dim_master_data` | `master_data_id`, `name`, `parent_id`, `parent_name` | `JENIS_SARANA` |
| `fact_pemeriksaan` | `sarana_id`, `balai_id`, `jenis_id` | — |
