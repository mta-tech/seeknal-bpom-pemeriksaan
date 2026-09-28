jenis pangan · MD · IRT · PIRT · UMKM · AMDK · kategori pangan · pangan MD

# Jenis pangan & penanda MD/IRT

## Apa yang halaman ini putuskan

Penanda seperti **MD, IRT, UMKM, AMDK** hidup di dimensi **jenis sarana** atau di kolom khusus pangan —
bukan di komoditi. Dan kolom daftar pangan bisa merujuk **lebih dari satu kamus**.

## Tabel keputusan

| Kata dalam pertanyaan | Filter |
|---|---|
| "pangan MD" | jenis sarana yang memuat penanda MD |
| "pangan IRT" · "PIRT" · "UMKM" | jenis sarana yang memuat penanda IRT/UMKM |
| "AMDK" | jenis pangan spesifik, bukan jenis sarana |
| "jenis pangan" (daftar) | kolom daftar pangan pada kasus |
| "skala usaha" · "kapasitas pabrik" | tabel profil Pangan MD (satelit), bukan kolom fakta |
| "sertifikat" (SNI/HACCP/Halal/ISO) | bridge sertifikat Pangan MD |

## Matriks operasi

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| daftar pangan (jsonb array) | expand dulu | expand lalu kelompokkan | **bisa merujuk >1 kamus** → jangan filter satu `type`; tampilkan `type` sebagai hasil | normalisasi dulu |
| `klasifikasi_sarana_kode` | sebutkan cakupannya (khusus Pangan) | batasi ke jenis sarana terkait | kamus `CLASS_SARANA` | sebutkan cakupan |
| `jenis_id` untuk MD/IRT | jenis sarana, bukan komoditi | butuh kamus + `type` | `dim_master_data` | biasa |

## Cara mencari

```sql
-- penanda MD/IRT hidup di mana? periksa jenis sarana
SELECT master_data_id, name, parent_name FROM public.dim_master_data
WHERE type = 'JENIS_SARANA' AND (name ILIKE '%MD%' OR name ILIKE '%IRT%' OR name ILIKE '%UMKM%')
ORDER BY 1;

-- daftar pangan merujuk kamus mana saja? (buktikan, jangan asumsikan)
SELECT d.type, count(*)
FROM public.fact_pemeriksaan f,
     LATERAL jsonb_array_elements_text(f.jenis_pangan_kode) k(x)
JOIN public.dim_master_data d ON d.master_data_id::text = k.x
GROUP BY 1 ORDER BY 2 DESC;
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| "pangan MD" tidak kena | dicari di kolom komoditi | pindah ke jenis sarana |
| daftar pangan sebagian hilang | difilter ke satu `type` kamus | jalankan query sebaran `type` di atas |
| klasifikasi sarana diklaim berlaku semua | hanya relevan untuk sebagian jenis sarana | sebutkan cakupannya |

## Batas

- Kolom daftar pangan sering kosong pada populasi yang tidak relevan → sebutkan keterisiannya.
- Profil pabrik (skala usaha, kapasitas) ada di tabel satelit, bukan di fakta.

## Rute

- Jenis sarana & golongan → **lihat** `10-sarana-dan-fasilitas.md`
- Komoditi → **lihat** `20-komoditi.md`
- Kualitas & keterisian → **lihat** `90-kualitas-data.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `fact_pemeriksaan` | `jenis_pangan_kode`, `klasifikasi_sarana_kode`, `jenis_id` | — |
| `dim_master_data` | `master_data_id`, `name`, `parent_name`, `type` | `JENIS_SARANA`, `CLASS_SARANA` |
| `fact_pemeriksaan_profil_pangan_md` | `pemeriksaan_id`, `skala_usaha`, `jumlah_karyawan` | — |
| `bridge_pemeriksaan_sertifikat_pangan_md` | `pemeriksaan_id`, `jenis`, `nomor`, `lembaga` | — |
