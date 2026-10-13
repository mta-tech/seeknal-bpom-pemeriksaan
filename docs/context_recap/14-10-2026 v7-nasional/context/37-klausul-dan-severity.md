klausul · tidak sesuai · minor · major · kritis · kritikal · serius · severity · checklist · aspek tidak sesuai

# Klausul & tingkat keparahan (varian produksi)

## Apa yang halaman ini putuskan

Untuk varian produksi, item checklist tersimpan di `bridge_pemeriksaan_checklist`: `path` (jejak
pertanyaan), `nilai_aspek` (jawaban), `catatan`. **`nilai_aspek` memuat empat makna berbeda**, dan
severitasnya **tidak tersedia untuk semua jenis sarana**.

## Tabel keputusan

| Kata dalam pertanyaan | Filter |
|---|---|
| "klausul tidak sesuai" · "tidak sesuai" · "tidak dipenuhi" | nilai `Tidak` |
| "minor" · "major" · "kritis" · "kritikal" · "serius" | nilai severitas yang sesuai |
| "OK" · "sesuai" | nilai konformitas |
| "paling sering tidak sesuai" | kelompokkan per `path`/segmen, hitung `Tidak`, **sebut cakupannya** |
| "severitas seluruh sarana" | **tidak bisa** — severitas tidak merata → sebutkan batas |

## Empat makna dalam satu kolom

| Kelompok | Nilai | Dipakai untuk |
|---|---|---|
| konformitas | `OK` · `Ya` · `Tidak` · `Tidak Berlaku` | cacah sesuai/tidak |
| grade | `B` · `T` · `C` · `K` | kelompok penilaian huruf |
| severitas | `Minor` · `Major` · `Kritis` · `Serius` · `Kritikal` | tingkat keparahan |
| status | `Lanjut` | status tindakan |

**Jangan** memakai satu filter untuk semua makna, dan **jangan** menganggap semua nilai adalah severity.

## Matriks operasi

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| `nilai_aspek` | pilih **kelompok** nilai sesuai maksud pertanyaan | pisahkan kelompok dulu | tidak ada kamus seragam | sebutkan cakupan |
| `path` | pola/segmen string; **tidak semua path punya nama aspek** | potong segmen — hati-hati, maknanya tidak seragam | ke kamus aspek **tidak ada** | sebutkan bila perkiraan |
| `sumber_pola` | menyaring varian | audit cakupan | — | — |
| `catatan` | teks bebas | tidak untuk cacah | — | — |

## Cara mencari

```sql
-- seluruh nilai yang benar-benar ada (jangan hafal)
SELECT COALESCE(NULLIF(btrim(nilai_aspek),''),'(kosong)') AS nilai, count(*)
FROM public.bridge_pemeriksaan_checklist GROUP BY 1 ORDER BY 2 DESC;

-- sebaran varian
SELECT sumber_pola, count(*), count(DISTINCT pemeriksaan_id)
FROM public.bridge_pemeriksaan_checklist GROUP BY 1 ORDER BY 2 DESC;

-- apakah severitas tersedia untuk jenis sarana tertentu?
SELECT d.name AS jenis_sarana,
       count(*) FILTER (WHERE b.nilai_aspek IN ('Minor','Major','Kritis','Serius','Kritikal')) AS ada_severitas,
       count(*) AS total_item
FROM public.bridge_pemeriksaan_checklist b
JOIN public.fact_pemeriksaan f ON f.id = b.pemeriksaan_id
JOIN public.dim_master_data d ON d.master_data_id = f.jenis_id AND d.type = 'JENIS_SARANA'
GROUP BY 1 ORDER BY 2 DESC;
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| "severitas seluruh sarana" terlihat lengkap | mencampur jenis sarana yang punya dan tidak punya severitas | jalankan query cakupan di atas |
| peringkat aspek terlihat masuk akal tapi salah | memotong `path` dan menganggap segmennya nama aspek | periksa contoh `path` nyata lebih dulu |
| angka klausul membengkak | menjumlahkan pelayanan (skor) dengan produksi (klausul) | pisahkan — satuan berbeda |

## Batas

- Severitas per klausul **tidak merata** antar jenis sarana; sebagian jenis tidak punya sama sekali →
  sebutkan cakupannya sebelum menyajikan angka.
- Sebagian kasus tidak punya baris checklist → lihat cakupan di `01`.
- Narasi (`catatan`) **bukan** item yang bisa dihitung.

## Rute

- Kepatuhan aspek (pelayanan) → **lihat** `35-kepatuhan-aspek.md`
- Observasi & vaksin → **lihat** `45-observasi-dan-vaksin.md`
- Grade & tindak lanjut → **lihat** `60-mutu-dan-tindak-lanjut.md`
- Routing varian → **lihat** `01-peta-data-dan-routing.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `bridge_pemeriksaan_checklist` | `pemeriksaan_id`, `path`, `nilai_aspek`, `catatan`, `sumber_pola`, `conformity` | `OK`, `Ya`, `Tidak`, `Tidak Berlaku`, `Minor`, `Major`, `Kritis`, `Serius`, `Kritikal`, `Lanjut`, `B`, `T`, `C`, `K` |
| `fact_pemeriksaan` | `id`, `jenis_id` | — |
| `dim_master_data` | `master_data_id`, `name` | `JENIS_SARANA` |
