status · draft · verifikasi · selesai · macet · antrian · bottleneck · belum selesai · tahap

# Status berkas & alur

## Apa yang halaman ini putuskan

Status kasus adalah kode teks di `dim_status_code`, **wajib disaring dengan `domain='pemeriksaan'`** —
tabel yang sama dipakai domain lain dengan ruang nilai berbeda.

## Tabel keputusan

| Kata dalam pertanyaan | Filter |
|---|---|
| "draft" · "belum dikirim" | kelompok draft |
| "dikirim" · "masuk verifikasi" | kelompok verifikasi |
| "selesai" | kelompok final — **dua kode**: jalur balai dan jalur pusat |
| "dalam proses" · "belum selesai" | bukan kelompok final dan bukan kelompok draft |
| "macet" · "menumpuk" · "bottleneck" | **`GROUP BY status` tanpa filter** — pertanyaannya memang tentang sebaran |
| "siapa yang menyetujui" · "self-approval" | **tidak dapat dipastikan** → P5 |

## Matriks operasi

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| `status_id` | kelompok kode dari kamus + `domain` | butuh kamus | `dim_status_code.id` **dan** `domain='pemeriksaan'` | sebaran lebih bermakna daripada peringkat |
| `status_code` (di tabel approval) | join pakai **teks**, bukan id | biasa | `dim_status_code.status_code` | — |
| `status_label` | **tidak bisa dipakai** (kosong) | tidak bisa | — | — |

## Cara mencari

```sql
-- daftar status pemeriksaan (jangan hafal; catat bahwa labelnya kosong)
SELECT id, status_code, status_label FROM public.dim_status_code
WHERE domain = 'pemeriksaan' ORDER BY id;

-- sebaran kasus per status
SELECT s.status_code, count(*) AS kasus
FROM public.fact_pemeriksaan f
JOIN public.dim_status_code s ON s.id = f.status_id AND s.domain = 'pemeriksaan'
GROUP BY 1 ORDER BY 2 DESC;

-- jejak perpindahan tahap + durasi (dari approval)
SELECT act_steps, to_steps, count(*), min(created_at), max(created_at)
FROM public.fact_pemeriksaan_approval GROUP BY 1,2 ORDER BY 3 DESC LIMIT 20;
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| angka status kosong | `domain` tidak disebut → id bentrok dengan domain lain | sebut `domain='pemeriksaan'` |
| label tahap tidak muncul | `status_label` kosong seluruhnya | pakai `status_code`, sebutkan label tidak tersedia |
| "berapa TMK yang selesai" kehilangan populasi | menumpuk filter status di atas populasi yang sudah didefinisikan | pertanyaan TMK tidak butuh filter status kecuali diminta |
| menyimpulkan siapa menyetujui | semantik pelaku tidak dapat dipastikan | nyatakan P5 |

## Batas

- Kata "selesai" mencakup **dua** jalur final; menyebut satu saja akan mengurangi angka.
- Tabel approval menjelaskan **perpindahan dan waktu**, bukan siapa yang memutuskan.
- Riwayat perubahan isi kasus tidak tersimpan (edit menimpa) → jangan menjanjikan rekonstruksi.

## Rute

- Durasi & lama tertahan → **lihat** `80-waktu-dan-durasi.md`
- Kesimpulan → **lihat** `30-kesimpulan.md`
- Status sebagai label panel → **lihat** `05-filter-katalog.md`
- Batas domain (TTE, siapa menyetujui) → **lihat** `95-batas-domain.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `dim_status_code` | `id`, `status_code`, `status_label`, `domain` | `pemeriksaan` |
| `fact_pemeriksaan` | `status_id` | — |
| `fact_pemeriksaan_approval` | `act_steps`, `to_steps`, `status`, `created_at`, `notes` | — |
