# 03 — Aturan Join

> Enam pola join berlaku di domain ini. Masing-masing punya alasan, dan kalau salah pola hasilnya **kosong tanpa pesan error** — inilah sumber kesalahan paling sering.
>
> Verifikasi: 22 Sep 2026.

---

## Pola 1 — Angka ke kamus: **wajib sebut `type`**

```sql
LEFT JOIN public.dim_master_data m
       ON m.master_data_id = f.jenis_id
      AND m.type = 'JENIS_SARANA'
```

`dim_master_data` adalah satu tabel berisi **72 kamus** sekaligus. `master_data_id` bisa cocok dengan entri kamus mana pun. Tanpa `type`, join-nya jalan tapi maknanya tidak jelas.

Dipakai di: `jenis_id`, `tujuan_id`, `klasifikasi_id`, `metode_inspeksi`, `kasus_id`, `unit_id`, `klasifikasi_produk_kode`, `unit_kode`, `dim_sarana.type_id`, `dim_sarana.status_sarana`, `fact_pemeriksaan.status_ss`.

## Pola 2 — Kolom teks berisi angka: **wajib `::text`**

```sql
LEFT JOIN public.dim_master_data m
       ON m.master_data_id::text = o.observasi_kode
      AND m.type = 'TEMUAN_OBSERVATION'
```

`observasi_kode` bertipe teks sementara `master_data_id` bertipe bigint. Tanpa cast, join gagal — dan gagalnya senyap.

Dipakai di: `observasi_kode`, `komoditi_kode`, `fokus_kode`, `aspek_ktl_kode`, dan semua elemen jsonb array (`kategori_kode`, `tindakan_kode`).

## Pola 3 — Kolom array: **expand dulu**

```sql
CROSS JOIN LATERAL jsonb_array_elements_text(t.kategori_kode) AS e(kode)
LEFT JOIN public.dim_master_data m
       ON m.master_data_id::text = e.kode
      AND m.type = 'KATEGORI_TEMUAN_PRODUK'
```

Contoh: `kategori_kode` bisa berisi `["499","506"]` — satu produk kena dua kategori sekaligus. Array harus dipecah jadi baris dulu.

⚠️ Ada `[null]` di dalam array (81 baris) — parser harus menangani `null`, bukan hanya string kosong.

## Pola 4 — Satu kolom merujuk **beberapa** kamus (paling berbahaya)

Tiga kolom terverifikasi seperti ini:

| Kolom | Kamus yang dirujuk | Kalau salah filter |
|---|---|---|
| `dim_sarana.legal_id` | `BENTUK_PERUSAHAAN` 241.769 + `JENIS_SARANA` 169.067 + tanpa match 29.356 | kehilangan 45% baris |
| `fact_pemeriksaan.tl_saran` | **7 kamus**; `SARAN_TINDAK_LANJUT` hanya 116.831 (51%) | hanya benar 51% |
| `fact_pemeriksaan.jenis_pangan_kode` | `PRODUK_PANGAN` 46.521 + `JENIS_PANGAN_68` 20.915 | kehilangan 31% |
| `fact_pemeriksaan.penelusuran_id` | `PENELUSURAN` **atau** `TL_PENELUSURAN` | Aturan #14 |

Pembanding yang berguna: `tl_saran_pusat` di sebelah `tl_saran` justru **hampir murni satu kamus** (56.362 dari 56.502 elemen = 99,8% `SARAN_TINDAK_LANJUT`).

Cara aman untuk kolom semacam ini — jangan filter `type`, tapi tampilkan `type` sebagai kolom hasil:

```sql
SELECT m.type, count(*)
FROM public.fact_pemeriksaan f,
     LATERAL jsonb_array_elements_text(f.tl_saran) k(x)
JOIN public.dim_master_data m ON m.master_data_id::text = k.x
GROUP BY 1 ORDER BY 2 DESC;
```

## Pola 5 — Join ke tabel dimensi khusus

```sql
JOIN public.dim_pemeriksaan_kesimpulan k ON k.id = f.kesimpulan_balai_id
JOIN public.dim_pemeriksaan_aspek      a ON a.area_key = s.area_key
JOIN public.dim_status_code            c ON c.id = f.status_id AND c.domain = 'pemeriksaan'
```

Untuk tabel **approval** join-nya berbeda — pakai kolom teks, bukan id:

```sql
JOIN public.dim_status_code c ON c.status_code = a.status AND c.domain = 'pemeriksaan'
```

Konsepnya sama (status kasus), tapi di `fact_pemeriksaan` join ke `id`, di `fact_pemeriksaan_approval` join ke `status_code`. **Ini mudah tertukar.** Keduanya sudah diuji: `fact` → 0 orphan (1 baris `status_id` NULL, bukan orphan), `approval` → 0 orphan.

## Pola 6 — Join ke fact: **hitung dulu barisnya**

```sql
JOIN public.fact_pemeriksaan f ON f.id = b.pemeriksaan_id
```

Menggabungkan fact dengan bridge menambah jumlah baris:

| Pertanyaan | Tabel yang benar | Hasil |
|---|---|---|
| "berapa pemeriksaan?" | `fact_pemeriksaan` | 259.348 |
| "berapa penugasan petugas?" | `bridge_pemeriksaan_petugas` | 553.380 (~2× karena satu kasus ~2 petugas) |

Rata-rata baris bridge per kasus: checklist ~76 (pada kasus yang punya), skor ~24, approval ~5, petugas ~2, temuan ~9,5.

---

## Peta lengkap: kolom mana join ke `type` mana

| Kolom | Ada di tabel | `type` di `dim_master_data` | Catatan |
|---|---|---|---|
| `jenis_id` | `fact_pemeriksaan` | `JENIS_SARANA` | jenis sarana |
| `tujuan_id` | `fact_pemeriksaan` | `TUJUAN_PEMERIKSAAN` | |
| `klasifikasi_id` | `fact_pemeriksaan` | `JENIS_KLASIFIKASI` | |
| `metode_inspeksi` | `fact_pemeriksaan` | `METODE_INSPEKSI` | jarang terisi |
| `kasus_id` | `fact_pemeriksaan` | `JENIS_KASUS` | jarang |
| `unit_id` | `fact_pemeriksaan` | `SAMPEL_UNIT` | jarang |
| `penelusuran_id` | `fact_pemeriksaan` | `PENELUSURAN` **atau** `TL_PENELUSURAN` | 2 kemungkinan (Aturan #14) |
| `status_ss` | `fact_pemeriksaan` | `STATUS_SARANA` | snapshot status sarana saat diperiksa |
| `sediaan_kode` | `fact_pemeriksaan` | `BENTUK_SEDIAAN` | jsonb array, 0,3% terisi |
| `klasifikasi_sarana_kode` | `fact_pemeriksaan` | `CLASS_SARANA` | khusus Pangan, teks langsung |
| `type_id` | `dim_sarana` | `JENIS_SARANA` | kamus sama dengan `fact.jenis_id` |
| `status_sarana` | `dim_sarana` | `STATUS_SARANA` | statis/terkini |
| `aspek_ktl_kode` | `dim_pemeriksaan_aspek` | `ASPEK_KTL` | NULL kalau belum ada di kamus (Aturan #7) |
| `kategori_kode` | `bridge_pemeriksaan_temuan` | `KATEGORI_TEMUAN_PRODUK` | jsonb array |
| `tindakan_kode` | `bridge_pemeriksaan_temuan` | `TL_PRODUK_TEMUAN` | jsonb array |
| `klasifikasi_produk_kode` | `bridge_pemeriksaan_temuan` | `KLASIFIKASI_PRODUK` | Lokal/Impor |
| `unit_kode` | `bridge_pemeriksaan_temuan` | `SAMPEL_UNIT` | |
| `observasi_kode` | `bridge_pemeriksaan_temuan_observasi` | `TEMUAN_OBSERVATION` | wajib `::text` |
| `komoditi_kode` | `bridge_pemeriksaan_komoditi_pbf` | `KOMODITI` | wajib `::text` |
| `fokus_kode` | `bridge_pemeriksaan_fokus_pbf` | `FOKUS_PEMERIKSAAN` | wajib `::text` |
| `legal_id` | `dim_sarana` | `BENTUK_PERUSAHAAN` **+** `JENIS_SARANA` | kolom multi-kamus |
| `jenis_pangan_kode` | `fact_pemeriksaan` | `PRODUK_PANGAN` **+** `JENIS_PANGAN_68` | kolom multi-kamus |
| `tl_saran` | `fact_pemeriksaan` | **7 kamus** | kolom multi-kamus |
| `tl_saran_pusat` | `fact_pemeriksaan` | `SARAN_TINDAK_LANJUT` | 99,8% murni |
| `status` | `fact_pemeriksaan_approval` | `domain='pemeriksaan'` (join ke `status_code`) | Aturan #3 |

**Pengecualian penting**: `kesimpulan_balai_id`, `kesimpulan_pusat_id`, dan `vaksin_kesimpulan_id` **bukan** join langsung ke `dim_master_data` — ketiganya ke `dim_pemeriksaan_kesimpulan` (Aturan #1, #20). Empat baris di dalamnya (khusus `jenis_id`=8) aslinya berasal dari `dim_master_data` type `CPOB_FULLFILLMENT`, tapi sudah dibungkus supaya kolom kesimpulan tetap satu target join untuk semua kasus.

---

## Tiga kesalahan yang paling sering terjadi

| Gejala | Penyebab | Perbaikan |
|---|---|---|
| Hasil kosong tanpa error | `type` tidak disebut, atau lupa `::text`, atau baca bridge yang salah untuk flag kasus itu | Pola 1/2 + [04-routing-bridge.md](04-routing-bridge.md) |
| Angka ~2× lipat | `count(*)` setelah join ke bridge | pakai `count(DISTINCT f.id)` |
| Sebagian baris hilang tanpa peringatan | filter satu `type` pada kolom multi-kamus | Pola 4 |

```sql
-- versi aman untuk "berapa pemeriksaan yang punya temuan"
SELECT count(DISTINCT t.pemeriksaan_id) FROM public.bridge_pemeriksaan_temuan t;
-- bukan: SELECT count(*) ...
```
