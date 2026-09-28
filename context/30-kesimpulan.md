MK · TMK · TTP · TDP · TMBB · memenuhi ketentuan · tidak memenuhi · kesimpulan · tingkat pemenuhan CPOB

# Kesimpulan kasus

## Apa yang halaman ini putuskan

Kesimpulan adalah **foreign key**, bukan teks: `kesimpulan_balai_id` / `kesimpulan_pusat_id` →
`dim_pemeriksaan_kesimpulan`. Kolom teks kesimpulan tidak ada lagi.

## Tabel keputusan

| Kata dalam pertanyaan | Filter |
|---|---|
| "MK" · "memenuhi ketentuan" | kode MK |
| "TMK" · "tidak memenuhi ketentuan" | kode TMK |
| "TTP" · "TDP" · "TMBB" | kode masing-masing |
| "tingkat pemenuhan CPOB" · "memuaskan/baik/cukup/kurang" | **kelompok kode CPOB** pada kolom yang sama |
| "kesimpulan pusat" · "evaluasi pusat" | `kesimpulan_pusat_id` |
| "penilaian vaksin" · "MS/TMS" | `vaksin_kesimpulan_id` |

## Satu kolom, tiga taksonomi

`kesimpulan_balai_id` memuat **tiga kelompok** yang tidak boleh dicampur:

| Kelompok | Isi | Catatan |
|---|---|---|
| umum | MK · TMK · TTP · TDP · TMBB | vonis kasus |
| CPOB | memuaskan · baik · cukup · kurang | tingkat pemenuhan, untuk sebagian jenis sarana |
| vaksin | MS · TMS Mayor 1–3 · TMS Kritikal | hanya lewat `vaksin_kesimpulan_id` |

Untuk rekap, **pisahkan kelompoknya lebih dulu** — kalau tidak, dua taksonomi tercampur dalam satu
daftar.

## Matriks operasi

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| `kesimpulan_balai_id` | kelompok kode + `type` tak berlaku (ini dim sendiri) | pisahkan taksonomi | `dim_pemeriksaan_kesimpulan.id` | biasa |
| `kesimpulan_pusat_id` | **review pusat parsial** — NULL berarti tidak direview, bukan "belum diproses" | sebutkan cakupannya | idem | sebutkan cakupan |
| `vaksin_kesimpulan_id` | hanya untuk kasus form vaksin | biasa | idem | — |

## Cara mencari

```sql
-- seluruh isi kamus kesimpulan
SELECT id, kode, keterangan, status, sumber FROM public.dim_pemeriksaan_kesimpulan ORDER BY id;

-- kode kesimpulan mana yang BENAR-BENAR dipakai (termasuk kelompok CPOB & vaksin)
SELECT d.kode, count(*) AS kasus
FROM public.fact_pemeriksaan f
JOIN public.dim_pemeriksaan_kesimpulan d ON d.id = f.kesimpulan_balai_id
GROUP BY 1 ORDER BY 2 DESC;

-- keterisian kesimpulan: balai vs pusat
SELECT count(*) AS kasus, count(kesimpulan_balai_id) AS ada_balai, count(kesimpulan_pusat_id) AS ada_pusat
FROM public.fact_pemeriksaan;
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| rekap kesimpulan bercampur dua taksonomi | kelompok CPOB disamakan dengan vonis | pisahkan berdasarkan `sumber`/kelompok kode |
| "pusat belum memproses semua kasus" | NULL dibaca sebagai pekerjaan tertunda | review pusat memang parsial — sebutkan |
| angka MK+TMK < total | sebagian kasus belum berkesimpulan | hitung keterisian |

## Batas

- Kasus tanpa kesimpulan tetap pemeriksaan sah → jangan dibuang tanpa alasan.
- `keterangan` pada sebagian kode masih kosong → bila user menanyakan arti, katakan belum terkonfirmasi.
- Tidak boleh menyimpulkan kualitas sarana dari kesimpulan saja tanpa menyebut cakupannya.

## Rute

- Status & alur → **lihat** `31-status-dan-alur.md`
- Grade & tindak lanjut → **lihat** `60-mutu-dan-tindak-lanjut.md`
- Tingkat pemenuhan sebagai label panel → **lihat** `05-filter-katalog.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `fact_pemeriksaan` | `kesimpulan_balai_id`, `kesimpulan_pusat_id`, `vaksin_kesimpulan_id` | — |
| `dim_pemeriksaan_kesimpulan` | `id`, `kode`, `keterangan`, `status`, `sumber` | `MK`, `TMK`, `TTP`, `TDP`, `TMBB` |
