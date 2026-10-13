prekursor · jenis obat kelola · profil faskes · profil apotek · profil puskesmas · profil toko obat · manfaat IT · resep · personel faskes

# Profil terstruktur sarana pelayanan (faskes) per kasus

## Apa yang halaman ini putuskan

Sebagian kasus pelayanan menyimpan profil terstruktur di `fact_pemeriksaan_profil_faskes` — satu baris
per kasus yang ber-form profil. Halaman ini memutuskan cara membaca kolom `prekursor` dan `jenis_obat`
(dua kolom yang paling sering disalahbaca) serta personelnya. **Makna kosong ditentukan cakupan form**:
kolom yang tidak dimuat form tidak boleh dibaca sebagai "tidak ada".

## Tabel keputusan

| Kata dalam pertanyaan | Aksi |
|---|---|
| "sarana mengelola prekursor?" | `prekursor = 't'` — **text `'t'/'f'`, bukan boolean** |
| "obat apa yang dikelola" (narkotika/psikotropika/prekursor/antibiotik/vaksin/…) | parse `jenis_obat`, lalu join kamus `JENIS_OBAT_KELOLA` |
| "personel yang terlibat" | `bridge_pemeriksaan_personel_faskes` (`peran`) |
| "akreditasi" · "manfaat IT" · "resep" · "TTK" | kolom profil masing-masing |
| profil untuk sarana non-pelayanan | tidak ada barisnya → **lihat** `90` (bukan "tidak mengelola") |

**Cakupan form menentukan makna kosong.** `prekursor` hanya diisi oleh form tertentu (Toko Obat); pada
jenis sarana lain kolom itu kosong karena **form tidak memuatnya**. Selalu tampilkan sebaran per jenis
sarana beserta cakupannya sebelum menyimpulkan apa pun.

## Matriks operasi

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| `prekursor` | `= 't'` (bandingkan teks) | kelompokkan `'t' / 'f' / kosong` **bersama** cakupan formnya | dari profil ke fakta | sebut cakupan |
| `jenis_obat` (TEXT ber-JSON) | parse `::jsonb` dulu | `jsonb_array_elements_text` per kode | `dim_master_data` `type='JENIS_OBAT_KELOLA'`, `master_data_id::text = kode` | biasa |
| `jenis_id` | filter jenis sarana | sebaran profil per jenis | kamus `JENIS_SARANA` | biasa |
| `peran` (bridge personel) | teks; normalisasi ejaan dulu | bedakan `COUNT(*)` baris vs `COUNT(DISTINCT pemeriksaan_id)` kasus | — | normalisasi dulu |

## Cara mencari

```sql
-- sebaran prekursor + cakupannya per jenis sarana (jangan hafal)
SELECT d.name AS jenis_sarana, COALESCE(pf.prekursor,'(kosong)') AS prekursor, count(*)
FROM public.fact_pemeriksaan_profil_faskes pf
LEFT JOIN public.dim_master_data d
       ON d.master_data_id = pf.jenis_id AND d.type = 'JENIS_SARANA'
GROUP BY 1, 2 ORDER BY 1, 3 DESC;

-- daftar kode obat-kelola yang benar-benar dipakai
SELECT d.master_data_id, d.name, count(*) AS kasus
FROM public.fact_pemeriksaan_profil_faskes pf,
     LATERAL jsonb_array_elements_text(pf.jenis_obat::jsonb) j(kode)
JOIN public.dim_master_data d
      ON d.master_data_id::text = j.kode AND d.type = 'JENIS_OBAT_KELOLA'
GROUP BY 1, 2 ORDER BY 3 DESC;

-- keterisian profil per jenis sarana
SELECT d.name, count(*) AS profil
FROM public.fact_pemeriksaan_profil_faskes pf
LEFT JOIN public.dim_master_data d
       ON d.master_data_id = pf.jenis_id AND d.type = 'JENIS_SARANA'
GROUP BY 1 ORDER BY 2 DESC;
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| filter `prekursor = true` gagal atau kosong | kolom bertipe text `'t'/'f'` | bandingkan sebagai teks |
| "Apotek tidak mengelola prekursor" | kolom kosong pada form itu dibaca sebagai penolakan | lihat sebaran per jenis di atas |
| filter `jenis_obat` tanpa hasil | string JSON tidak di-parse | `::jsonb` + `jsonb_array_elements_text` |
| kode obat-kelola tak ketemu | join tanpa cast teks / tanpa `type` | pola join di atas |
| "berapa sarana" dijawab dari tabel profil | profil adalah data kasus | `COUNT(DISTINCT sarana_id)` dari fakta |

## Batas & honest gap

- Profil hanya ada untuk varian form pelayanan tertentu; kasus lain tidak punya baris profil — sebut
  cakupan, jangan menyimpulkan populasi dari yang punya profil saja.
- `jenis_obat` menyatakan **obat yang dikelola/dijual sarana**, bukan temuan pelanggaran.
- Karantina: jangan menyimpulkan "mengelola X" dari nama sarana atau dari kolom lain yang mirip.

## Rute

- Jenis sarana & golongan → **lihat** `10-sarana-dan-fasilitas.md`
- Komoditi kasus (`klasifikasi_id`) → **lihat** `20-komoditi.md`; bridge distribusi → **lihat** `22`
- Narasi faskes & vaksin → **lihat** `45-observasi-dan-vaksin.md`
- Kekosongan & cakupan → **lihat** `90-kualitas-data.md`
- Ambiguitas "PKM" → **lihat** `97-glossary-istilah-user.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `fact_pemeriksaan_profil_faskes` | `pemeriksaan_id`, `jenis_id`, `jenis_sarana_json`, `prekursor`, `jenis_obat`, `manfaat_it`, `resep`, `akreditasi` | — |
| `bridge_pemeriksaan_personel_faskes` | `pemeriksaan_id`, `urutan`, `peran` | — |
| `dim_master_data` | `master_data_id`, `name`, `type` | `JENIS_SARANA`, `JENIS_OBAT_KELOLA` |
