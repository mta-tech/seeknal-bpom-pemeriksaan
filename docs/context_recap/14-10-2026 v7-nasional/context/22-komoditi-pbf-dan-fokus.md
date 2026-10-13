komoditi PBF · NPP · narkotika · psikotropika · prekursor · obat berkontrol · fokus pemeriksaan · NPP dan OOT · CCP · SAS · obat kelola · PBF · IFK · IFP

# Komoditi obat-kelola di sarana distribusi (PBF/IFK/IFP) & fokus pemeriksaan

## Apa yang halaman ini putuskan

Pengelolaan komoditi pada sarana distribusi tersimpan di **dua bridge terpisah**: `bridge_pemeriksaan_komoditi_pbf`
(komoditi yang dikelola) dan `bridge_pemeriksaan_fokus_pbf` (fokus pemeriksaan). Keduanya **grain berbeda**
dari `klasifikasi_id` di `20`: klasifikasi menandai kasus di sarana mana pun; bridge ini hanya milik kasus
ber-form distribusi.

## Tabel keputusan

| Kata dalam pertanyaan | Aksi |
|---|---|
| "PBF/IFK/IFP yang mengelola narkotika/psikotropika/prekursor" | `bridge_pemeriksaan_komoditi_pbf` + kamus `KOMODITI` |
| "fokus pemeriksaan" · "NPP dan OOT" · "CCP" · "SAS" (di distribusi) | `bridge_pemeriksaan_fokus_pbf` + kamus `FOKUS_PEMERIKSAAN` |
| "berapa kasus yang mengelola X" | `COUNT(DISTINCT pemeriksaan_id)` pada bridge |
| "berapa baris komoditi/fokus" | `COUNT(*)` pada bridge |
| "obat berkontrol" tanpa menyebut sarana distribusi | kemungkinan maksudnya kasus ber-`klasifikasi_id` → **lihat** `20` |

**Dua grain NPP — jangan dicampur.** "Kasus ber-komoditi NPP" (klasifikasi, sarana apa pun) dan "kasus
distribusi yang mengelola NPP" (bridge) adalah dua populasi berbeda dengan angka berbeda. Satu jawaban
satu grain; bila keduanya diminta, sajikan dua kolom dan sebut namanya.

## Matriks operasi

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| `komoditi_kode` (text) | nilai dari kamus, bukan ingatan | langsung | `dim_master_data` dengan `type='KOMODITI'` **dan** `master_data_id::text = komoditi_kode` | biasa |
| `fokus_kode` (text) | idem | langsung | `dim_master_data` dengan `type='FOKUS_PEMERIKSAAN'`, cast yang sama | biasa |
| `pemeriksaan_id` | biasa | `COUNT(DISTINCT)` untuk kasus | ke fakta/view, arah dari bridge | biasa |

**Wajib `type`.** `master_data_id` yang sama sah di beberapa kamus; tanpa `type` maknanya bisa berubah
tanpa error. **Kolom `code` kamus bukan kunci** — bridge menyimpan `master_data_id` sebagai teks; join
dengan `code` menghasilkan kosong tanpa pesan.

## Cara mencari

```sql
-- daftar komoditi yang benar-benar dipakai (jangan hafal)
SELECT d.master_data_id, d.name, count(*) AS baris,
       count(DISTINCT b.pemeriksaan_id) AS kasus
FROM public.bridge_pemeriksaan_komoditi_pbf b
JOIN public.dim_master_data d
      ON d.master_data_id::text = b.komoditi_kode AND d.type = 'KOMODITI'
GROUP BY 1, 2 ORDER BY 4 DESC;

-- idem untuk fokus pemeriksaan
SELECT d.master_data_id, d.name, count(DISTINCT b.pemeriksaan_id) AS kasus
FROM public.bridge_pemeriksaan_fokus_pbf b
JOIN public.dim_master_data d
      ON d.master_data_id::text = b.fokus_kode AND d.type = 'FOKUS_PEMERIKSAAN'
GROUP BY 1, 2 ORDER BY 3 DESC;

-- jenis sarana yang benar-benar punya baris bridge (buktikan cakupannya)
SELECT d2.name AS jenis_sarana, count(DISTINCT b.pemeriksaan_id) AS kasus
FROM public.bridge_pemeriksaan_komoditi_pbf b
JOIN public.fact_pemeriksaan f ON f.id = b.pemeriksaan_id
JOIN public.dim_master_data d2 ON d2.master_data_id = f.jenis_id AND d2.type = 'JENIS_SARANA'
GROUP BY 1 ORDER BY 2 DESC;
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| join komoditi kosong / nol | memakai kolom `code` kamus alih-alih `master_data_id::text` | jalankan query pertama di atas |
| kasus dihitung berulang | `COUNT(*)` pada bridge disebut jumlah kasus | `COUNT(DISTINCT pemeriksaan_id)` |
| angka "NPP di distribusi" tertukar "kasus NPP" | dua grain dicampur | putuskan grain dulu (`20` vs halaman ini) |
| baris bridge dianggap milik PBF saja | nama tabel `_pbf` menyesatkan | query cakupan jenis sarana di atas |
| kode komoditi ditulis dari ingatan | nilai `code` kamus dipakai sebagai filter | probe `SELECT DISTINCT` + join kamus |

## Batas & honest gap

- Bridge hanya ada untuk kasus ber-form distribusi; kasus form lain **tidak punya baris** — bukan bukti
  "tidak mengelola".
- Satu kasus bisa memuat beberapa komoditi → penjumlahan per komoditi melebihi jumlah kasus; sebut grain.
- Bridge tidak memuat kuantitas/nilai pengelolaan — hanya relasi kasus ↔ komoditi/fokus.

## Rute

- Komoditi berbasis kasus (`klasifikasi_id`) → **lihat** `20-komoditi.md`
- Temuan produk (BKO, obat keras, bahan berbahaya) → **lihat** `40-temuan-produk.md`
- Kekosongan & bucket → **lihat** `90-kualitas-data.md`
- Zat adiktif & permit impor (tidak ada di sini) → **lihat** `95-batas-domain.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `bridge_pemeriksaan_komoditi_pbf` | `pemeriksaan_id`, `komoditi_kode` | — |
| `bridge_pemeriksaan_fokus_pbf` | `pemeriksaan_id`, `fokus_kode` | — |
| `dim_master_data` | `master_data_id`, `name`, `type` | `KOMODITI`, `FOKUS_PEMERIKSAAN` |
