inspektur · petugas · pemeriksa · beban kerja · jam terbang · tim pemeriksa

# Petugas & inspektur

## Apa yang halaman ini putuskan

Siapa yang terlibat dalam pemeriksaan, dan **apa yang boleh disimpulkan** dari data itu.

## Tabel keputusan

| Kata dalam pertanyaan | Aksi |
|---|---|
| "berapa pemeriksaan oleh X" | `COUNT(DISTINCT pemeriksaan_id)` pada bridge petugas |
| "berapa penugasan" | `COUNT(*)` pada bridge petugas |
| "beban kerja" | jumlah kasus per petugas, **sebut jenis sarana** supaya adil dibandingkan |
| "jam terbang" · "pengalaman" | eksposur penugasan per jenis sarana/golongan |
| "paling kompeten" · "inspektur terbaik" | **tidak tersedia** → butuh klarifikasi: volume atau eksposur |

## Matriks operasi

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| `user_id` | biasa | `COUNT(DISTINCT pemeriksaan_id)` per user | `dim_user.user_id` | sebut jenis sarana pembanding |
| `urutan` | urutan dalam tim, **bukan** peran keputusan | boleh untuk komposisi tim | — | jangan dijadikan hierarki |
| `fullname` | teks bebas → normalisasi bila mengelompokkan | normalisasi dulu | dari `dim_user` | peringkat tanpa normalisasi tidak sahih |
| `balai_id` (di user) | 0 = penanda tanpa balai | — | — | — |

## Cara mencari

```sql
-- petugas terbanyak (kasus unik, bukan baris)
SELECT u.fullname, count(DISTINCT p.pemeriksaan_id) AS kasus
FROM public.bridge_pemeriksaan_petugas p
JOIN public.dim_user u ON u.user_id = p.user_id
GROUP BY 1 ORDER BY 2 DESC LIMIT 10;

-- eksposur per jenis sarana (untuk pertanyaan kompetensi)
SELECT u.fullname, d.name AS jenis_sarana, count(DISTINCT p.pemeriksaan_id) AS kasus
FROM public.bridge_pemeriksaan_petugas p
JOIN public.fact_pemeriksaan f ON f.id = p.pemeriksaan_id
JOIN public.dim_user u ON u.user_id = p.user_id
LEFT JOIN public.dim_master_data d ON d.master_data_id = f.jenis_id AND d.type = 'JENIS_SARANA'
GROUP BY 1,2 ORDER BY 3 DESC LIMIT 20;

-- komposisi tim per kasus
SELECT n_petugas, count(*) FROM (
  SELECT pemeriksaan_id, count(*) AS n_petugas
  FROM public.bridge_pemeriksaan_petugas GROUP BY 1) x
GROUP BY 1 ORDER BY 1;
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| angka petugas ±2× angka pemeriksaan | `COUNT(*)` pada bridge disebut jumlah pemeriksaan | pakai `COUNT(DISTINCT pemeriksaan_id)` |
| sebagian petugas tanpa nama | `user_id` tidak ada di `dim_user` | hitung orphan; sebutkan bila kecil |
| peringkat petugas terpecah | penulisan nama berbeda | normalisasi |

## Batas

- Data **tidak** memuat kompetensi, sertifikasi, atau peran keputusan → jangan menyimpulkan kualitas.
- `urutan` bukan hierarki peran.
- Perbandingan beban kerja antar petugas harus mempertimbangkan jenis sarana yang ditangani.

## Rute

- Jenis sarana & golongan → **lihat** `10-sarana-dan-fasilitas.md`
- Wilayah & balai → **lihat** `05-filter-katalog.md`
- Ambiguitas "inspektur terbaik" → **lihat** `97-glossary-istilah-user.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `bridge_pemeriksaan_petugas` | `pemeriksaan_id`, `user_id`, `urutan` | — |
| `dim_user` | `user_id`, `fullname`, `username`, `balai_id` | — |
| `fact_pemeriksaan` | `id`, `jenis_id` | — |
