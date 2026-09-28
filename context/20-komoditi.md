komoditi · obat · kosmetik · pangan · obat tradisional · suplemen · narkotika · psikotropika · prekursor · bahan berbahaya

# Komoditi (jenis komoditi)

## Apa yang halaman ini putuskan

Komoditi dipilih user sebagai **Jenis Komoditi**, dan disimpan di `klasifikasi_id` → kamus
`JENIS_KLASIFIKASI`. Ia berbeda dari jenis sarana, dan berbeda dari jenis pangan.

## Tabel keputusan

| Kata dalam pertanyaan | Filter |
|---|---|
| "obat" | nilai obat pada kamus komoditi |
| "kosmetik" · "pangan" · "obat tradisional" · "suplemen" | nilai masing-masing |
| "narkotika" · "psikotropika" · "prekursor" · "bahan berbahaya" | nilai masing-masing |
| "pangan MD" · "pangan IRT" | **bukan** komoditi — itu jenis sarana → `50` |

## Matriks operasi

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| `klasifikasi_id` | butuh kamus + `type='JENIS_KLASIFIKASI'` | butuh kamus yang sama | `dim_master_data` **wajib** dengan `type` | biasa |

**Wajib `type`.** `dim_master_data` memuat puluhan kamus dalam satu tabel; tanpa `type`, join bisa
cocok dengan entri kamus lain dan maknanya berubah tanpa error.

## Cara mencari

```sql
-- daftar komoditi yang benar-benar dipakai
SELECT d.master_data_id, d.name, count(*) AS kasus
FROM public.fact_pemeriksaan f
JOIN public.dim_master_data d ON d.master_data_id = f.klasifikasi_id
  AND d.type = 'JENIS_KLASIFIKASI'
GROUP BY 1, 2 ORDER BY 3 DESC;
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| hasil join kosong | `type` tidak disebut | periksa nilai `type` yang ada di kamus |
| angka aneh pada komoditi tertentu | nilai ditulis dari ingatan | pakai hasil query di atas |

## Batas

- Komoditi dan jenis sarana bisa tampak tumpang tindih di mata user ("kosmetik" adalah keduanya) —
  pilih kolom sesuai **makna** pertanyaan: komoditi yang diawasi → `klasifikasi_id`; jenis fasilitas →
  `jenis_id`.
- Penanda MD/IRT/UMKM **tidak** ada di komoditi → `50`.

## Rute

- Jenis sarana & golongan → **lihat** `10-sarana-dan-fasilitas.md`
- Jenis pangan → **lihat** `50-jenis-pangan.md`
- Label panel komoditi → **lihat** `05-filter-katalog.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `fact_pemeriksaan` | `klasifikasi_id` | — |
| `dim_master_data` | `master_data_id`, `name`, `type` | `JENIS_KLASIFIKASI` |
