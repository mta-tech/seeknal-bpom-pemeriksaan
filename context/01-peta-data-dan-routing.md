peta data · routing · bridge · kenapa kosong · tabel mana · varian · flag_varian_datas

# Peta tabel & routing varian

## Apa yang halaman ini putuskan

Tabel/bridge mana yang dibaca untuk satu kasus — diputuskan oleh `fact_pemeriksaan.flag_varian_datas`.

## Tabel keputusan — varian menentukan bridge

| `flag_varian_datas` | Baca bridge | Isi |
|---|---|---|
| `pola1_direct` | `bridge_pemeriksaan_checklist` | klausul bernomor, jawaban campur makna |
| `pola1_nested` | `bridge_pemeriksaan_checklist` | klausul bersarang, jawaban Ya/Tidak + catatan |
| `pola1_observation` | `bridge_pemeriksaan_checklist` | klausul dengan status/severitas |
| `clusterC_skor` | `bridge_pemeriksaan_skor_operasional` | **satu-satunya yang punya kamus aspek** (`area_key`) |
| `clusterC_vaksin` | `bridge_pemeriksaan_vaksin` | 19 `section_key` form vaksin |
| `clusterC_naratif` | `bridge_pemeriksaan_narasi_faskes` | 8 section narasi bebas |
| `pola2_klasifikasi` | `bridge_pemeriksaan_temuan_observasi` | kode observasi + `kriteria` |
| `clusterF_cpkb` | **tidak ada bridge** | hanya header + narasi |
| `lainnya` | **tidak ada bridge** | sangat jarang |

Bridge yang **tidak** ditentukan varian: `bridge_pemeriksaan_temuan` (temuan produk lahir dari flow
hasil & tindak lanjut, bisa ada di varian apa pun); `bridge_pemeriksaan_petugas`;
`fact_pemeriksaan_approval`; `fact_pemeriksaan_narasi`.

## Matriks operasi

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| `flag_varian_datas` | menentukan bridge — **selalu periksa dulu** | untuk audit cakupan | — | — |
| `pemeriksaan_id` (semua bridge) | biasa | biasa | dari fakta, arah aman | — |
| `path` (checklist) | butuh pola/segmen | bertingkat, hati-hati | ke kamus aspek **tidak ada** | — |
| `area_key` (skor) | langsung | langsung | ke `dim_pemeriksaan_aspek.area_key` | — |

## Cara mencari

```sql
-- bridge mana untuk satu kasus
SELECT id, flag_varian_datas FROM public.fact_pemeriksaan WHERE id = :id;

-- sebaran varian pada populasi yang ditanya
SELECT flag_varian_datas, count(*) FROM public.fact_pemeriksaan GROUP BY 1 ORDER BY 2 DESC;

-- cek kasus yang tidak punya baris di bridge mana pun (audit cakupan)
WITH b AS (
  SELECT pemeriksaan_id FROM public.bridge_pemeriksaan_checklist
  UNION SELECT pemeriksaan_id FROM public.bridge_pemeriksaan_skor_operasional
  UNION SELECT pemeriksaan_id FROM public.bridge_pemeriksaan_temuan_observasi
  UNION SELECT pemeriksaan_id FROM public.bridge_pemeriksaan_vaksin
  UNION SELECT pemeriksaan_id FROM public.bridge_pemeriksaan_narasi_faskes
)
SELECT f.flag_varian_datas, count(*) AS kasus, count(*) - count(b.pemeriksaan_id) AS tanpa_bridge
FROM public.fact_pemeriksaan f LEFT JOIN b ON b.pemeriksaan_id = f.id
GROUP BY 1 ORDER BY 3 DESC;
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| hasil **kosong tanpa error** padahal kasusnya ada | membaca bridge yang tidak sesuai varian | periksa `flag_varian_datas` kasus itu |
| angka item jauh lebih kecil dari dugaan | memakai checklist untuk kasus berskor (atau sebaliknya) | bandingkan jumlah baris tiap bridge untuk kasus yang sama |
| kesimpulan "tidak ada data" | populasi memang punya varian tanpa bridge | hitung cakupan seperti query di atas |

**Aturan:** salah tabel → kosong tanpa pesan kesalahan. Satu query kecil untuk memeriksa varian lebih
murah daripada satu jawaban yang salah.

## Batas

- `clusterF_cpkb` dan `lainnya` memang tidak punya bridge detail → nyatakan batasnya, jangan
  menyimpulkan "tidak ada temuan".
- Sebagian kasus tidak punya baris bridge apa pun — **hitung cakupannya** dengan query di atas dan
  sebutkan bila relevan dengan pertanyaan.

## Rute

- Kontrak isi bridge skor → **lihat** `35-kepatuhan-aspek.md`
- Kontrak isi checklist → **lihat** `37-klausul-dan-severity.md`
- Observasi & vaksin → **lihat** `45-observasi-dan-vaksin.md`
- Cakupan kosong → **lihat** `90-kualitas-data.md`
- Daftar kolom satu tabel → `describe_table`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `fact_pemeriksaan` | `id`, `flag_varian_datas` | `pola1_direct`, `pola1_nested`, `pola1_observation`, `clusterC_skor`, `clusterC_vaksin`, `clusterC_naratif`, `pola2_klasifikasi`, `clusterF_cpkb`, `lainnya` |
| `bridge_pemeriksaan_checklist` | `pemeriksaan_id`, `path`, `sumber_pola` | — |
| `bridge_pemeriksaan_skor_operasional` | `pemeriksaan_id`, `area_key` | — |
| `bridge_pemeriksaan_vaksin` | `pemeriksaan_id`, `section_key` | — |
| `bridge_pemeriksaan_narasi_faskes` | `pemeriksaan_id`, `section` | — |
| `bridge_pemeriksaan_temuan_observasi` | `pemeriksaan_id`, `observasi_kode` | — |
