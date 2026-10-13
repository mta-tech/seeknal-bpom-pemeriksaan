target · capaian · realisasi · pencapaian · persentase capaian · target sampling · target sarana

# Target & capaian

## Apa yang halaman ini putuskan

Target tersedia di **`dim_balai`** (per balai), bukan di tabel fakta. Halaman ini memutuskan grain dan
cara menyajikannya dibanding realisasi.

## Tabel keputusan

| Kata dalam pertanyaan | Sumber |
|---|---|
| "target pemeriksaan nasional" | jumlah target seluruh balai — **hati-hati grain** |
| "target balai X" | baris balai itu |
| "realisasi" · "capaian" | hitungan kasus dari fakta |
| "persentase capaian" | realisasi ÷ target, **per balai**, sebutkan pembilang & penyebut |
| "target sarana" vs "target sampling" | **dua kolom berbeda** — tanyakan/pilih sesuai maksud |

## Matriks operasi

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| `target_sampling` | per balai | langsung | dari `dim_balai` | sebutkan satuan |
| `target_sarana` | per balai | langsung | dari `dim_balai` | sebutkan satuan |
| realisasi (kasus) | periode + eksklusi | per balai | dari fakta ke `dim_balai` | biasa |

## Cara mencari

```sql
-- ketersediaan target per balai
SELECT count(*) AS balai, count(target_sampling) AS ada_sampling, count(target_sarana) AS ada_sarana
FROM public.dim_balai;

-- target vs realisasi per balai (contoh; periode sesuai pertanyaan)
SELECT b.nama_balai, b.target_sarana,
       count(DISTINCT f.id) AS realisasi
FROM public.dim_balai b
LEFT JOIN public.fact_pemeriksaan f
       ON f.balai_id = b.balai_id AND f.tgl_start >= DATE '2025-01-01' AND f.tgl_start < DATE '2026-01-01'
GROUP BY 1,2 ORDER BY 3 DESC;
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| total target membengkak | menjumlahkan baris yang grain-nya bukan per balai-periode | periksa grain sebelum menjumlahkan |
| persentase > 100% terlihat aneh | pembilang dan penyebut beda cakupan (mis. realisasi lintas periode) | samakan periode & cakupan, sebutkan keduanya |
| target "nasional" dobel | unit pusat ikut dijumlahkan | bedakan unit pusat dari balai wilayah |

## Batas

- Target hanya tersedia **per balai**; memecahnya per jenis sarana tidak didukung data.
- Bila pertanyaan menuntut grain yang tidak tersedia → nyatakan batasnya, jangan membagi rata.
- Realisasi harus memakai eksklusi data uji (`00`).

## Rute

- Wilayah & balai → **lihat** `10-sarana-dan-fasilitas.md`
- Periode → **lihat** `80-waktu-dan-durasi.md`
- Label panel target → **lihat** `05-filter-katalog.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `dim_balai` | `balai_id`, `nama_balai`, `target_sampling`, `target_sarana`, `regional_name` | — |
| `fact_pemeriksaan` | `id`, `balai_id`, `tgl_start`, `is_data_uji` | — |
