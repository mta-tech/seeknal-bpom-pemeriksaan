label panel · filter · legal · klasifikasi · status label · tingkat pemenuhan cpob · target · tanggal · wilayah

# Katalog filter panel → kolom, atau honest gap

## Apa yang halaman ini putuskan

User memilih filter dari **panel**, bukan dari nama kolom. Halaman ini memetakan setiap label panel ke
kolom/kode yang benar — atau menyatakan bahwa label itu **tidak punya kolom**.

## Tabel keputusan — dimensi panel

| Label panel | Kolom / keputusan | Status |
|---|---|---|
| Jenis sarana | `jenis_id` → kamus `JENIS_SARANA`; golongan lewat `parent_name` | ada |
| Jenis komoditi | `klasifikasi_id` → kamus `JENIS_KLASIFIKASI` (wajib `type`) | ada |
| Tanggal | `tgl_start` · `tgl_end` · `created_at` · `updated_at` | ada (4 label → 4 kolom) |
| Kesimpulan | `kesimpulan_balai_id` / `kesimpulan_pusat_id` → `dim_pemeriksaan_kesimpulan` | ada |
| Tingkat pemenuhan CPOB | **kelompok kode** pada `kesimpulan_balai_id`, bukan kolom | ada sebagai kode |
| Grade | `grade` | ada (subset jenis sarana) |
| Tujuan pemeriksaan | `tujuan_id` → kamus | ada |
| Petugas / inspektur | `bridge_pemeriksaan_petugas` → `dim_user` | ada |
| Unit / Balai | `balai_id` → `dim_balai` | ada (pelaksana, bukan lokasi objek) |
| Regional | `dim_balai.regional_name` | ada — **jangan** kolom `regional` |
| Provinsi / Kabupaten | `dim_sarana.provinsi_id` / `kabupaten_id` | ada (lokasi objek) |
| Legal | `dim_sarana.legal_id` | ⚠️ **merujuk 2 kamus** |
| Klasifikasi sarana | `klasifikasi_sarana_kode` → `CLASS_SARANA` | ⚠️ khusus Pangan |
| Status label | `dim_status_code` | ❌ **labelnya kosong seluruhnya** |
| Target / capaian | `dim_balai.target_sampling` · `target_sarana` | ada (terisi penuh) |
| **Klasifikasi distribusi** | — | ❌ **tidak ada kolom** |
| Aspek / skor | `area_key` → `dim_pemeriksaan_aspek` | ⚠️ hanya varian pelayanan |
| Klausul / severitas | `path` + `nilai_aspek` | ⚠️ parsial |
| Observasi / GMP | `bridge_pemeriksaan_temuan_observasi` | ⚠️ sebagian |
| Vaksin | `bridge_pemeriksaan_vaksin.section_key` | ⚠️ belum punya kamus label |

## Cara mencari bila label tidak jelas

```sql
-- 1. cari kolomnya lebih dulu — jangan menebak dari nama label
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND (column_name ILIKE '%<kata>%' OR column_name ILIKE '%<sinonim>%')
ORDER BY 1, 2;

-- 2. kolom ada? cek keterisiannya sebelum dipakai sebagai penyaring
SELECT count(*) AS total, count(<kolom>) AS terisi FROM public.<tabel>;

-- 3. kolom tidak ada -> P5 honest gap. JANGAN pakai kolom "yang mirip namanya".
```

## Matriks operasi

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| `legal_id` | **jangan filter satu `type`** | tampilkan `type` sebagai kolom hasil | `dim_master_data` tanpa filter type | biasa |
| `status_label` | tidak bisa dipakai (kosong) | tidak bisa | `dim_status_code` | tidak bisa |
| `target_sampling`/`target_sarana` | biasa | biasa | dari `dim_balai` | biasa |
| `klasifikasi_sarana_kode` | sebutkan cakupannya (Pangan) | batasi ke jenis sarana terkait | kamus `CLASS_SARANA` | sebutkan cakupan |

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| angka "klasifikasi distribusi" muncul rapi | tersambung ke `distribusi_provinsi_kode` (itu **tujuan distribusi pabrik Pangan MD**) | periksa nama tabel & konteksnya; baca kolom aslinya |
| "belum punya status label" = seluruh populasi | `status_label` memang kosong | hitung keterisian kolomnya |
| filter legal menghilangkan sebagian besar baris | `legal_id` merujuk 2 kamus | hitung sebaran `type` |

## Batas & honest gap

- **Klasifikasi distribusi**: tidak direkam di database ini → nyatakan; tawarkan hal terdekat yang
  benar-benar bisa dijawab, dan sebutkan bedanya.
- **Status label**: hanya kode status yang tersedia; label tahap tidak ada di data.
- **Panel tidak menang atas kanon**: bila label panel berbeda dari bacaan kanonik, pakai kanon dan
  sebutkan bedanya.

## Rute

- Dimensi sarana → **lihat** `10-sarana-dan-fasilitas.md`
- Komoditi → **lihat** `20-komoditi.md`
- Kesimpulan & CPOB → **lihat** `30-kesimpulan.md`
- Status → **lihat** `31-status-dan-alur.md`
- Aspek → **lihat** `35-kepatuhan-aspek.md`; klausul → **lihat** `37-klausul-dan-severity.md`
- Target → **lihat** `85-target-capaian.md`
- Label tanpa kolom → **lihat** `95-batas-domain.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `information_schema.columns` | `table_name`, `column_name`, `data_type` | — |
| `dim_sarana` | `legal_id`, `provinsi_id`, `kabupaten_id` | — |
| `dim_status_code` | `status_code`, `status_label` | — |
| `dim_balai` | `regional_name`, `target_sampling`, `target_sarana` | — |
| `fact_pemeriksaan` | `klasifikasi_sarana_kode`, `jenis_id`, `klasifikasi_id` | — |
| `fact_pemeriksaan_profil_pangan_md` | `distribusi_provinsi_kode` | — |
