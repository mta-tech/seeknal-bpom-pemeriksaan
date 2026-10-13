tujuan pemeriksaan · rutin · kasus · intensifikasi · sertifikasi · hari besar · surveilans

# Tujuan pemeriksaan

## Apa yang halaman ini putuskan

`tujuan_id` adalah **tujuan pemeriksaan** (kenapa sarana diperiksa). Ia berbeda dari tujuan
penugasan yang bisa muncul di konteks petugas.

## Tabel keputusan

| Kata dalam pertanyaan | Filter |
|---|---|
| "rutin" · "pemeriksaan rutin" | `tujuan_id` = nilai rutin dari kamus |
| "kasus" · "penindakan" · "berdasarkan kasus" | nilai kasus |
| "intensifikasi" · "pengawasan khusus" | nilai intensifikasi |
| "sertifikasi" | nilai sertifikasi |
| "natal" · "tahun baru" · "idul fitri" · "hari besar" | nilai kampanye musiman |
| tidak menyebut tujuan | **tanpa filter `tujuan_id`** |

## Matriks operasi

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| `tujuan_id` | butuh kamus + `type='TUJUAN_PEMERIKSAAN'` | butuh kamus yang sama | `dim_master_data` dengan `type` | biasa |

## Cara mencari

```sql
-- daftar tujuan yang benar-benar terpakai (jangan hafal)
SELECT d.master_data_id, d.name, count(*) AS kasus
FROM public.fact_pemeriksaan f
JOIN public.dim_master_data d ON d.master_data_id = f.tujuan_id
  AND d.type = 'TUJUAN_PEMERIKSAAN'
GROUP BY 1, 2 ORDER BY 3 DESC;
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| filter tujuan mengembalikan nol | nilai ditulis dari ingatan, bukan dari kamus | jalankan query di atas |
| angka tujuan tidak menjumlah populasi | sebagian kasus tidak mengisi tujuan | hitung keterisian `tujuan_id` |

## Batas

- Sebagian kecil kasus tidak mengisi `tujuan_id` → tidak akan muncul di hitungan per tujuan.
- Jangan menumpuk filter tujuan di atas populasi yang sudah didefinisikan hal lain.

## Rute

- Status & alur → **lihat** `31-status-dan-alur.md`
- Kesimpulan → **lihat** `30-kesimpulan.md`
- Periode & tren → **lihat** `80-waktu-dan-durasi.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `fact_pemeriksaan` | `tujuan_id` | — |
| `dim_master_data` | `master_data_id`, `name` | `TUJUAN_PEMERIKSAAN` |
