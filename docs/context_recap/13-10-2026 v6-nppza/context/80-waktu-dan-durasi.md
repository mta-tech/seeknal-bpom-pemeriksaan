tahun · bulan · triwulan · periode · tren · durasi · lama · berapa hari · sejak · paling awal · terakhir

# Waktu, periode, dan durasi

## Apa yang halaman ini putuskan

Kolom tanggal mana yang dipakai, bagaimana menyaring periode, dan kapan sebuah tren **tidak boleh**
disimpulkan.

## Tabel keputusan

| Kata dalam pertanyaan | Kolom | Catatan |
|---|---|---|
| kegiatan · diperiksa · periode · tren | `tgl_start` | default |
| selesai · berapa lama | `tgl_end` | penyelesaian |
| dilaporkan · diinput · administrasi | `created_at` / `updated_at` | bukan kegiatan |
| lama tertahan di tahap X | dari tabel approval (`created_at` per perpindahan) | bukan dari fakta |
| "paling awal" · "sejak kapan" | lihat Jebakan — butuh penjaga | — |

**Entity dan kolom tanggal adalah satu keputusan.** Menghitung pemeriksaan lalu menyaringnya dengan
kolom administrasi mencampur dua peristiwa.

## Matriks operasi

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| `tgl_start` | **rentang berbatas** (`>= awal AND < akhir`), bukan `EXTRACT` | `date_trunc` untuk melabeli hasil | — | biasa |
| `tgl_end` | rentang | boleh | — | biasa |
| `created_at` / `updated_at` | rentang (administrasi) | boleh | — | memeringkat "terbaru" pakai `updated_at` |
| `created_at` (approval) | rentang | boleh | dari fakta | durasi antar tahap |

## Cara mencari

```sql
-- rentang nyata + kekosongan
SELECT min(tgl_start), max(tgl_start), count(*) FILTER (WHERE tgl_start IS NULL) FROM public.fact_pemeriksaan;

-- sebaran per tahun (jangan pakai EXTRACT di WHERE)
SELECT date_trunc('year', tgl_start) AS thn, count(*)
FROM public.fact_pemeriksaan WHERE tgl_start IS NOT NULL GROUP BY 1 ORDER BY 1;

-- durasi perpindahan tahap
SELECT act_steps, to_steps, percentile_cont(0.5) WITHIN GROUP (ORDER BY created_at) 
FROM public.fact_pemeriksaan_approval GROUP BY 1,2 LIMIT 10;
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| "paling awal" mengembalikan tahun tidak masuk akal | ada nilai tanggal rusak/terjadwal | batasi ke rentang operasional; sebutkan bila membatasi |
| tren naik/turun menyesatkan | periode pembanding tidak lengkap (periode berjalan) | sebutkan periode berjalan bersifat parsial |
| filter periode kosong | memakai `EXTRACT` di `WHERE` | ganti ke rentang berbatas |
| durasi kosong untuk tahap tertentu | tahap belum tercapai | sebutkan, bukan dianggap nol |

## Batas

- Periode berjalan selalu parsial → wajib disebut.
- Sebagian kasus tanpa tanggal kegiatan tidak masuk hitungan periode.
- Tanggal jadwal ke depan itu **valid** (bukan data kotor).
- Nilai `tgl_start` **di luar rentang operasional** (sebelum 2020, dan jauh di masa depan) ada di data →
  setiap hitung periode wajib memakai rentang eksplisit (`>= DATE '2020-01-01' AND < batas atas`);
  jangan mengandalkan `min`/`max` kolom untuk menentukan filter.

## Rute

- Status & tahap alur → **lihat** `31-status-dan-alur.md`
- Entity & eksklusi → **lihat** `00-menghitung.md`
- Target vs realisasi per periode → **lihat** `85-target-capaian.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `fact_pemeriksaan` | `tgl_start`, `tgl_end`, `created_at`, `updated_at` | — |
| `fact_pemeriksaan_approval` | `created_at`, `act_steps`, `to_steps` | — |
