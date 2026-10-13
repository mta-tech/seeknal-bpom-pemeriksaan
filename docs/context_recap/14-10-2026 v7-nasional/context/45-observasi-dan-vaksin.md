observasi · GMP · kriteria · vaksin · imunisasi · narasi · personalia · dokumentasi · gudang

# Observasi GMP, form vaksin, dan narasi

## Apa yang halaman ini putuskan

Tiga sumber kekhasan yang sering disalahartikan sebagai checklist biasa:

1. **observasi GMP** — kode observasi baku + kolom `kriteria` yang artinya belum terkonfirmasi;
2. **form vaksin** — section bertema vaksin tanpa kamus label;
3. **narasi** — teks bebas per bagian; **bukan** item yang bisa dihitung.

## Tabel keputusan

| Kata dalam pertanyaan | Sumber | Catatan |
|---|---|---|
| "observasi" · "GMP" · "kriteria" | `bridge_pemeriksaan_temuan_observasi` | `kriteria` = kode angka, arti belum dikonfirmasi |
| "vaksin" · "imunisasi" · "personil vaksin" | `bridge_pemeriksaan_vaksin` | 19 section, belum punya kamus label aspek |
| "narasi" · "catatan bagian X" · "personalia/dokumentasi/gudang" | `bridge_pemeriksaan_narasi_faskes` | 8 section teks bebas |
| "berapa temuan observasi" | hitung kode observasi, bukan teks | |
| "ringkas isi narasi" | tugas teks + bukti kasus | bukan cacah |

## Matriks operasi

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| `observasi_kode` | butuh kamus `TEMUAN_OBSERVATION` (**cast teks**) | butuh kamus | `dim_master_data` dengan `type` + `::text` | biasa |
| `kriteria` | **jangan** disaring sebelum artinya dikonfirmasi | boleh dikelompokkan sebagai kode mentah | tidak ada kamus | jangan ditafsirkan |
| `section_key` (vaksin) | nilai mentah | kelompokkan apa adanya | belum ada kamus | biasa |
| `section` (narasi) | nilai tetap 8 | langsung | — | **jangan** diperingkat sebagai entitas |

## Cara mencari

```sql
-- observasi: kode mana yang benar-benar dipakai
SELECT o.observasi_kode, d.name, count(*)
FROM public.bridge_pemeriksaan_temuan_observasi o
LEFT JOIN public.dim_master_data d
       ON d.master_data_id::text = o.observasi_kode AND d.type = 'TEMUAN_OBSERVATION'
GROUP BY 1,2 ORDER BY 3 DESC LIMIT 20;

-- vaksin: sebaran section
SELECT section_key, count(*), count(DISTINCT pemeriksaan_id)
FROM public.bridge_pemeriksaan_vaksin GROUP BY 1 ORDER BY 2 DESC;

-- narasi: sebaran bagian
SELECT section, count(*), count(DISTINCT pemeriksaan_id)
FROM public.bridge_pemeriksaan_narasi_faskes GROUP BY 1 ORDER BY 2 DESC;
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| join kode observasi kosong | salah `type`, atau lupa `::text` | periksa kamus `TEMUAN_OBSERVATION` |
| mengartikan `kriteria` sebagai severity | artinya belum dikonfirmasi | sajikan sebagai kode, sebutkan belum dikonfirmasi |
| narasi dihitung sebagai item | teks diperlakukan sebagai klausul | narasi = bahan ringkasan + bukti |
| section vaksin diklaim punya label aspek | belum ada kamusnya | nyatakan |

## Batas

- Observasi hanya pada sebagian varian (routing di `01`).
- Vaksin dan narasi punya tabel sendiri; **bukan** bagian dari aspek pelayanan.
- Ringkasan narasi wajib membawa bukti: id kasus, potongan teks sumber, dan tanggal.

## Rute

- Aspek pelayanan → **lihat** `35-kepatuhan-aspek.md`
- Klausul produksi → **lihat** `37-klausul-dan-severity.md`
- Antibiotik (batas data) → **lihat** `95-batas-domain.md`
- Kode & kamus → **lihat** `05-filter-katalog.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `bridge_pemeriksaan_temuan_observasi` | `pemeriksaan_id`, `urutan`, `observasi_kode`, `kriteria`, `catatan` | — |
| `bridge_pemeriksaan_vaksin` | `pemeriksaan_id`, `section_key`, `opsi`, `jumlah`, `observasi`, `perbaikan`, `intervensi` | — |
| `bridge_pemeriksaan_narasi_faskes` | `pemeriksaan_id`, `section`, `teks` | `profil`, `pengadaan`, `penyimpanan`, `distribusi`, `personalia`, `dokumentasi`, `gudang`, `lain` |
| `dim_master_data` | `master_data_id`, `name`, `type` | `TEMUAN_OBSERVATION` |
