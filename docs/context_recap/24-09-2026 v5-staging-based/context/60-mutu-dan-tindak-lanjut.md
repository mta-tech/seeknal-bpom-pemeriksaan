grade · mutu · CAPA · tindak lanjut · sanksi · pembinaan · teguran · rekomendasi · temuan kritis · mayor · minor · CPOB

# Mutu & tindak lanjut

## Apa yang halaman ini putuskan

Tingkat mutu, ringkasan kekritisan per kasus, dan tindak lanjut. Ketiganya berada di tempat berbeda dan
**tidak boleh disamakan** dengan kategori temuan produk.

## Tabel keputusan

| Kata dalam pertanyaan | Sumber |
|---|---|
| "grade A/B/C" | `fact_pemeriksaan.grade` (subset jenis sarana) |
| "berapa temuan Major/Kritis" (per kasus) | counter kekritisan + level kesimpulan |
| "berapa klausul Kritis" (per klausul) | `nilai_aspek` → `37` |
| "tindak lanjut" · "CAPA" | kolom CAPA (teks) + tabel narasi |
| "sanksi" · "pembinaan" · "teguran" · "rekomendasi" | saran TL + narasi rekomendasi |
| "tindakan terhadap produk" (dimusnahkan/ditarik) | `tindakan_kode` pada temuan produk → `40` |
| "tingkat pemenuhan CPOB" | kelompok kode kesimpulan → `30` |

## Matriks operasi

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| `grade` | hanya untuk jenis sarana yang dinilai dengan grade | kelompok sebaran (termasuk kategori kosong) | — | biasa |
| counter kekritisan | **sebut cakupan** (tidak semua kasus punya) | boleh | — | biasa |
| `level_kesimpulan` | nilai teks tetap | boleh | — | bahasa asosiasi |
| saran tindak lanjut (jsonb array) | **merujuk >1 kamus** → jangan filter satu `type` | tampilkan `type` sebagai hasil | `dim_master_data` tanpa filter type | normalisasi dulu |
| CAPA | teks bebas → jangan disaring sebagai kode | lewat pengelompokan topik teks | — | bukan entitas |

## Cara mencari

```sql
-- sebaran grade (termasuk kosong = bukan jenis yang dinilai dengan grade)
SELECT COALESCE(grade,'(kosong)') AS grade, count(*) FROM public.fact_pemeriksaan GROUP BY 1 ORDER BY 2 DESC;

-- seberapa luas kekritisan per kasus tersedia?
SELECT count(*) AS kasus,
       count(*) FILTER (WHERE level_kesimpulan IS NOT NULL) AS ada_level,
       count(*) FILTER (WHERE kritis_count IS NOT NULL) AS ada_counter
FROM public.fact_pemeriksaan;

-- saran TL merujuk kamus mana saja? (buktikan)
SELECT d.type, count(*)
FROM public.fact_pemeriksaan f, LATERAL jsonb_array_elements_text(f.tl_saran) k(x)
JOIN public.dim_master_data d ON d.master_data_id::text = k.x
GROUP BY 1 ORDER BY 2 DESC;
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| "tingkat mutu seluruh sarana" terlihat lengkap | grade tidak berlaku untuk semua jenis sarana | sebutkan cakupannya |
| angka Major/Kritis dibandingkan dengan jumlah klausul | dua grain berbeda dicampur | pisahkan per kasus vs per klausul |
| tindak lanjut sebagian hilang | filter satu `type` pada kolom multi-kamus | jalankan query sebaran `type` |
| CAPA diklaim sebagai kategori | CAPA teks bebas, tidak terkamusk | sajikan sebagai teks/topik |

## Batas

- Kekritisan **tidak merata** antar jenis sarana → selalu sebutkan cakupan sebelum menyajikan peringkat.
- Hubungan antara severitas dan tindak lanjut bersifat **asosiasi**, bukan sebab-akibat.
- Riwayat perubahan keputusan tidak tersimpan → jangan menjanjikan rekonstruksi.

## Rute

- Severitas per klausul → **lihat** `37-klausul-dan-severity.md`
- Kesimpulan & CPOB → **lihat** `30-kesimpulan.md`
- Tindakan produk → **lihat** `40-temuan-produk.md`
- Narasi & ringkasan teks → **lihat** `45-observasi-dan-vaksin.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `fact_pemeriksaan` | `grade`, `kritis_count`, `major_count`, `minor_count`, `level_kesimpulan`, `tl_capa`, `tl_saran`, `tl_saran_pusat` | — |
| `fact_pemeriksaan_narasi` | `pemeriksaan_id`, `jenis_narasi`, `teks` | `catatan_balai`, `tindak_lanjut_detil`, `hasil_balai`, `hasil_pusat`, `catatan_pusat`, `rekomendasi`, `analisa`, `detail_tmk`, `tindak_lanjut_detil_pusat` |
| `dim_master_data` | `master_data_id`, `type`, `name` | — |
