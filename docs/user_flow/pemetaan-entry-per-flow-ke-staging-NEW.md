# Pemeriksaan Sarana — Kondisi Data di `staging`

## Data yang belum sinkron

Ini daftar lengkap data yang ada di `sipt_sync` tapi tidak ikut terbawa ke `staging`. Semuanya sudah diverifikasi dengan membandingkan langsung kedua database.

| # | Data | Sumber di `sipt_sync` | Punya di sumber | Punya di staging | Selisih |
|---|---|---|---|---|---|
| 1 | Section varian vaksin | `trx_pemeriksaan.datas`, key berakhiran `_vaksin_` | 7.697 kasus | 0 baris | **7.697** |
| 2 | Kekritisan per kasus | `trx_pemeriksaan.result` key `hp_level` | 9.100 kasus | 609 | **8.491** |
| 3 | Tingkat pemenuhan CPOB | `trx_pemeriksaan.result` key `hp_pemenuhan` | 876 kasus | 646 | **230** |
| 4 | Nama section aspek | `trx_pemeriksaan.datas`, key `tx_*` | 89 nama | 47 nama | **42** |
| 5 | Kasus dengan data standar | `trx_pemeriksaan.datas` | 1.183 kasus | 0 baris | **1.183** |
| 6 | Kamus `JENIS_SARANA` | `ms_master_data` | 32 entri | 30 entri | **2** |
| 7 | Kamus `TL_DISTRIBUSI` | `ms_master_data` | 23 entri | 22 entri | **1** |
| 8 | Sarana | `trx_sarana` | 441.821 | 440.192 | **1.629** |
| 9 | `status_ss` | `trx_pemeriksaan.status_ss` | 84.020 terisi | kolomnya tidak ada | **84.020** |
| 10 | `tp_asset` | `trx_pemeriksaan_temuan.tp_asset` | 59.708 terisi | kolomnya tidak ada | **59.708** |
| 11 | `updated_at`, `updated_by` | `trx_pemeriksaan` | 259.348 terisi | kolomnya tidak ada | **259.348** |

Nomor 1 sampai 8 sudah dipastikan perlu dikerjakan. Nomor 9 sampai 11 adalah kolom yang tidak punya padanan sama sekali di `staging` — perlu keputusan dulu apakah memang mau dibawa, karena tiga kolom itu tidak dipakai oleh pertanyaan analitik mana pun saat ini.

Akibat tiap kekurangan ke jawaban user:

| # | Kalau tidak diperbaiki |
|---|---|
| 1, 5 | jawaban "tren temuan per aspek" kurang 8.876 kasus (7.693 vaksin + 1.183 data standar) |
| 2 | pertanyaan tingkat kekritisan hampir tidak bisa dijawab, hanya 609 kasus dari 9.100 |
| 3 | pertanyaan tingkat pemenuhan CPOB kurang 230 kasus |
| 4 | 42 jenis pertanyaan checklist tidak bisa dikelompokkan per aspek resmi |
| 6, 7 | 2 kasus pemeriksaan kehilangan nama jenis sarana |
| 8 | 63 kasus kehilangan nama dan alamat sarana yang diperiksa |

Urutan pengerjaan yang disarankan:

| Prioritas | Yang dikerjakan | Ukuran |
|---|---|---|
| P1 | Petakan section vaksin (`tx_*_vaksin_*`) ke kamus aspek, lalu backfill | 7.693 kasus |
| P2 | Backfill kekritisan `hp_level` | 8.491 kasus |
| P3 | Petakan 42 nama section yang belum masuk kamus aspek (termasuk `tx_personalia`) | 42 nama |
| P4 | Backfill kasus dengan data standar | 1.183 kasus |
| P5 | Tambah 3 entri kamus yang dipakai pemeriksaan | 3 baris |
| P6 | Sinkron 1.629 sarana | 1.629 baris |
| P7 | Backfill tingkat pemenuhan CPOB | 230 kasus |
| P8 | Putuskan apakah `status_ss`, `tp_asset`, `updated_at/by` perlu dibawa | 3 kolom |

Dampaknya ke cakupan jawaban: sekarang 63.851 kasus (24,6%). Setelah P1 dan P4 dikerjakan naik jadi 72.727 (28,0%). Sisanya 395 kasus memang belum punya data karena masih berstatus draft.

> **Catatan 21 Sep 2026 (malam)**: sebagian besar poin di atas sudah dikerjakan tim data. Status terbaru ada di bagian **"Status setelah perbaikan"** di bawah.

---

## Status setelah perbaikan

Tim data sudah mengerjakan sebagian besar temuan. Berikut hasil verifikasi ulang ke database pada 21 September 2026.

### Yang sudah diperbaiki

| Poin | Sebelum | Sekarang | Cara verifikasi |
|---|---|---|---|
| P1 varian vaksin | 0 baris | **7.697 kasus, 145.540 baris** | tabel baru `bridge_pemeriksaan_vaksin` |
| P2 kekritisan | 609 kasus | **10.935 counter + 9.064 `level_kesimpulan`** | sumber punya 9.100 |
| P5 kamus | 1.994 entri | **1.999 entri** (= sumber) | ternyata soft-delete, lihat catatan di bawah |
| P6 sarana | 440.192 | **441.821** (= sumber) | idem |
| P8 kolom hilang | tidak ada kolomnya | **`status_ss`, `tp_asset`, `updated_at`, `updated_by` sudah dibawa** | 84.020 / 59.215 / 259.348 terisi |
| Orphan `jenis_id` | 2 | **0** | |
| Orphan `sarana_id` | 87 | **0** | |
| Outlier `jumlah_temuan` | maks 20,2 miliar, 137 negatif | **maks 7,7 juta, 0 negatif** | Aturan #21 ERD v3 |
| Duplikat temuan | 91.697 | **90.531** (berkurang 1.166) | hanya yang `created_at` identik yang dihapus |

Tabel dan kolom baru yang muncul:

| Yang baru | Keterangan |
|---|---|
| `bridge_pemeriksaan_vaksin` | 19 `section_key` vaksin, 145.540 baris untuk 7.660 kasus |
| `bridge_pemeriksaan_narasi_faskes` | 8 `section` naratif, 6.930 baris untuk 1.182 kasus |
| `dim_pemeriksaan_kesimpulan` | 9 → **14 baris** (5 kode vaksin: MS, TMS Mayor 1–3, TMS Kritikal) |
| `dihapus_di_sumber` | kolom baru di `dim_sarana` dan `dim_master_data` — lihat catatan |
| `level_kesimpulan`, `vaksin_kesimpulan_id`, `vaksin_bersama_rutin`, `vaksin_status_capa` | kolom baru di `fact_pemeriksaan` |
| `flag_varian_datas` | 7 → **9 nilai** (`clusterC_vaksin` 7.697, `clusterC_naratif` 1.182) |

### Catatan: dua temuan lama ternyata soft-delete, bukan hilang

Dua hal yang sebelumnya dilaporkan "hilang karena ekstraksi" ternyata **keputusan desain**, bukan bug. Ternyata baris-baris itu memang ada di sumber, tapi sudah `deleted_at IS NOT NULL` dan dikecualikan oleh filter ekstraksi.

| Laporan lama | Kenyataan |
|---|---|
| 5 entri kamus hilang | 1.994 aktif + **5 soft-delete** = 1.999 |
| 1.629 sarana hilang | 440.192 aktif + **1.629 soft-delete** = 441.821 |

Sekarang kedua dim dibuat **exact match** dengan sumber, dan baris soft-delete ditandai `dihapus_di_sumber = true` (Aturan #19 di ERD v3). Jadi tidak ada data yang benar-benar hilang — hanya definisi "aktif" yang berubah.

```sql
SELECT dihapus_di_sumber, count(*) FROM dim_master_data GROUP BY 1;
-- f 1994 | t 5

SELECT dihapus_di_sumber, count(*) FROM dim_sarana GROUP BY 1;
-- f 440192 | t 1629
```

### Yang masih terbuka

| # | Data | Sumber | Staging | Selisih |
|---|---|---|---|---|
| 1 | **42 nama section belum masuk kamus aspek** | 89 nama | 47 nama | **42** |
| 2 | Kasus `pola1_direct` tanpa baris checklist | — | 10.211 kosong | **10.211** |
| 3 | `clusterF_cpkb` | — | 2.610 kosong | **2.610** (memang belum ada bridge) |
| 4 | Kasus `pola1_observation` tanpa baris | — | 1.665 kosong | **1.665** |
| 5 | Kasus `clusterC_skor` tanpa baris | — | 398 kosong | **398** |
| 6 | Kasus `clusterC_naratif` tanpa baris | — | 145 kosong | **145** |
| 7 | `pola1_nested` / `pola2_klasifikasi` / `lainnya` | — | 254 / 115 / 14 | **383** |
| 8 | `petugas.user_id` orphan | 0 ada di `tb_users` | 169 | kondisi sumber |
| 9 | `temuan.tp_product_id` orphan | 0 ada di `ms_product` | 15 | kondisi sumber |

**Poin 1 masih menjadi yang paling layak dikerjakan.** `dim_pemeriksaan_aspek` masih 47 baris (40 resmi + 7 belum dikamus), dan section ini masih nol baris di semua bridge:

```sql
-- masih kosong di skor_operasional
SELECT count(*) FROM bridge_pemeriksaan_skor_operasional
WHERE area_key IN ('tx_personalia','tx_distribusi','tx_pengadaan',
                   'tx_penyimpanan','tx_gudang','tx_fast_moving_antibiotika');
-- 0

-- masih tidak ada di kamus
SELECT count(*) FROM dim_pemeriksaan_aspek
WHERE area_key IN ('tx_personalia','tx_distribusi','tx_pengadaan',
                   'tx_penyimpanan','tx_gudang');
-- 0
```

Catatan: section vaksin dan naratif **sudah tertangani**, tapi lewat tabel sendiri (`bridge_pemeriksaan_vaksin` dan `bridge_pemeriksaan_narasi_faskes`), bukan lewat `dim_pemeriksaan_aspek`. Jadi bridge-nya ada, tapi label aspek resminya belum.

**Poin 2 sampai 7 sebagian sudah membaik.** Gap `clusterC_skor` turun dari 9.271 menjadi 398, dan sebarannya kini merata antar tahun — tidak lagi menumpuk di 2021:

```sql
WITH b AS (SELECT DISTINCT pemeriksaan_id FROM bridge_pemeriksaan_skor_operasional)
SELECT extract(year FROM f.tgl_start)::int thn,
       count(*) - count(b.pemeriksaan_id) kosong
FROM fact_pemeriksaan f LEFT JOIN b ON b.pemeriksaan_id = f.id
WHERE f.flag_varian_datas = 'clusterC_skor'
GROUP BY 1 HAVING count(*) - count(b.pemeriksaan_id) > 0 ORDER BY 1;
```

| Tahun | Kosong |
|---:|---:|
| 2020 | 23 |
| 2021 | 30 |
| 2022 | 26 |
| 2023 | 38 |
| 2024 | 14 |
| 2025 | 16 |
| 2026 | 25 |
| tanpa tanggal | 226 |

226 kasus tanpa `tgl_start` (masih draft) menyumbang lebih dari separuh sisa. Sisanya tersebar tipis.

### Cakupan jawaban setelah perbaikan

```sql
WITH b AS (
  SELECT pemeriksaan_id FROM bridge_pemeriksaan_checklist
  UNION SELECT pemeriksaan_id FROM bridge_pemeriksaan_skor_operasional
  UNION SELECT pemeriksaan_id FROM bridge_pemeriksaan_temuan_observasi
  UNION SELECT pemeriksaan_id FROM bridge_pemeriksaan_vaksin
  UNION SELECT pemeriksaan_id FROM bridge_pemeriksaan_narasi_faskes
)
SELECT f.flag_varian_datas, count(*) kasus,
       count(b.pemeriksaan_id) punya_bridge,
       count(*) - count(b.pemeriksaan_id) masih_kosong
FROM fact_pemeriksaan f LEFT JOIN b ON b.pemeriksaan_id = f.id
GROUP BY 1 ORDER BY 4 DESC;
```

| flag | Kasus | Punya bridge | Masih kosong |
|---|---:|---:|---:|
| pola1_direct | 107.778 | 97.567 | 10.211 |
| clusterF_cpkb | 2.610 | 0 | 2.610 |
| pola1_observation | 10.421 | 8.756 | 1.665 |
| clusterC_skor | 64.243 | 63.845 | 398 |
| pola1_nested | 61.266 | 61.012 | 254 |
| clusterC_naratif | 1.182 | 1.037 | 145 |
| pola2_klasifikasi | 4.137 | 4.022 | 115 |
| lainnya | 14 | 0 | 14 |
| **clusterC_vaksin** | **7.697** | **7.697** | **0** |

Kasus tanpa bridge turun dari 24.140 menjadi **15.412**.

### Satu hal yang perlu diperjelas di ERD v3

ERD v3 §2 masih menulis status role begini:

> *"(Status: pembuatan role masih terblokir, akun kerja tidak punya privilege `CREATEROLE` — menunggu DBA menjalankan `CREATE ROLE` yang sudah disiapkan.)"*

Status itu sudah tidak berlaku. Role `pemeriksaan_reader` sudah dibuat dan aktif, dengan akses SELECT ke 27 tabel (19 tabel pemeriksaan + 8 dim general).

```sql
SELECT count(*) FROM information_schema.role_table_grants
WHERE grantee='pemeriksaan_reader' AND privilege_type='SELECT';
-- 27
```

---

## Yang sudah dicek dan bukan tugas pipeline

Empat hal ini tidak bisa dilengkapi, karena aplikasi SIPT-nya memang tidak pernah merekam. Sudah diverifikasi satu per satu ke sumber:

| Apa | Alasan |
|---|---|
| Aspek distribusi untuk sekitar 186.226 kasus produksi/kosmetik/pangan | formulir SIPT memakai checklist CPOB, bukan aspek distribusi |
| Penerimaan dan Pengembalian di kamus resmi | tidak ada di `ASPEK_KTL` BPOM (10 entri) |
| Status TTE | tidak pernah direkam sebagai data |
| Kekritisan per klausul | tidak pernah dicatat aplikasi |

Dan dua entri kamus yang sering disebut hilang bukan milik pemeriksaan:

| Entri | Alasan |
|---|---|
| `JENIS_PANGAN` ID 211236 | `JENIS_PANGAN` tidak pernah dirujuk pemeriksaan |
| `TUJUAN_SAMPLING` ID 223492 | milik domain pengujian |

---

Dokumen ini menjawab satu pertanyaan: **apakah semua data dari aplikasi SIPT sudah terbawa utuh ke database `staging`, atau ada yang hilang di tengah jalan?**

Cara menjawabnya bukan dengan membaca kode pipeline, tapi dengan membandingkan langsung dua database: sumber aslinya (`sipt_sync`) dan hasil ekstraksinya (`staging`). Kalau sebuah nilai kosong di `staging`, kita cek apakah nilai itu memang kosong di sumber, atau sebenarnya ada tapi tidak ikut terbawa.

Menggantikan `pemetaan-entry-per-flow-ke-staging.md` (versi lama = rencana sebelum ekstraksi) — file itu sudah **dihapus 22 Sep 2026** karena tidak lagi relevan dan memuat kredensial internal.

Verifikasi: 21 September 2026.

## Koneksi database

Query di dokumen ini dijalankan ke dua database:

| Keperluan | Variabel | Database |
|---|---|---|
| Baca hasil ekstraksi | `$STAGING_URL` | `staging`, schema `public` |
| Baca data mentah | `$SIPT_SYNC_URL` | `sipt_sync` |

Kredensialnya dikelola tim dan didokumentasikan terpisah di folder `credentials/` (butuh akses internal). Dokumen ini sengaja hanya memakai nama variabel supaya aman dibagikan ke tim mana pun tanpa perlu menyensor.

```bash
psql "$STAGING_URL"   -c "SELECT count(*) FROM fact_pemeriksaan;"
psql "$SIPT_SYNC_URL" -c "SELECT count(*) FROM trx_pemeriksaan;"
```

---

## Jawaban singkat

Data pemeriksaan **sebagian besar sudah terbawa**, tapi belum utuh. Yang perlu dipahami: nilai kosong di `staging` ada **dua jenis** yang berbeda, dan keduanya harus dipisahkan sebelum dianggap masalah.

**Jenis pertama — memang kosong di sumber.** Aplikasi SIPT-nya sendiri tidak pernah mengisi data itu. Contohnya: 169 petugas yang `user_id`-nya tidak terdaftar di tabel user, atau 295 baris observasi yang kodenya memang kosong. Ini bukan kesalahan pipeline, dan tidak bisa diperbaiki dari sisi ekstraksi.

**Jenis kedua — ada di sumber tapi tidak ikut terbawa.** Ini yang perlu diperbaiki. Contoh paling jelas: 7.693 kasus pemeriksaan yang di sumber punya data lengkap, tapi di `staging` nol baris.

Ringkasannya:

| Kondisi | Jumlah | Bisa diperbaiki? |
|---|---:|---|
| Sudah benar | — | — |
| Kosong karena sumber memang begitu | beragam | Tidak |
| Hilang karena ekstraksi | 6 kelompok | Ya |

Yang **sudah** benar dan tidak perlu diutak-atik:

| Item | Sumber | Staging | Status |
|---|---:|---:|---|
| Header kasus | 259.348 | 259.348 | utuh |
| Grade A/B/C | 44.401 | 44.400 | 99,998% |
| Provinsi | 44 | 44 | utuh |
| Kabupaten | 664 | 664 | utuh |
| Bridge ke fact | — | — | 0 orphan |
| Sisa kode temuan lama | — | 0 | bersih |

```sql
-- header kasus
SELECT count(*) FROM fact_pemeriksaan;                            -- 259348

-- grade
SELECT count(grade) FROM fact_pemeriksaan;                        -- 44400
SELECT grade, count(*) FROM fact_pemeriksaan
WHERE grade IS NOT NULL GROUP BY 1 ORDER BY 2 DESC;
-- A 24777 | B 9819 | C 9739 | N/A 65

-- provinsi & kabupaten
SELECT (SELECT count(*) FROM dim_provinsi) provinsi,
       (SELECT count(*) FROM dim_kabupaten) kabupaten;            -- 44 | 664

-- bridge ke fact: hitung baris bridge yang pemeriksaan_id-nya tidak ada di fact
SELECT count(*) FROM bridge_pemeriksaan_temuan t
LEFT JOIN fact_pemeriksaan f ON f.id = t.pemeriksaan_id
WHERE f.id IS NULL;                                               -- 0
```

Yang **hilang karena ekstraksi**:

| # | Yang hilang | Skala | Artinya bagi user |
|---|---|---:|---|
| 1 | Entri kamus (yang dipakai pemeriksaan) | 3 entri | 2 kasus kehilangan nama jenis sarana |
| 2 | Sarana | 1.629 | 63 kasus kehilangan nama & alamat sarana |
| 3 | Kasus varian vaksin | 7.693 | jawaban tren per aspek tidak mencakup kasus vaksin |
| 4 | Kasus dengan data standar | 1.183 | jawaban tren per aspek kurang 1.183 kasus |
| 5 | Kekritisan `hp_level` | 8.491 | pertanyaan tingkat kekritisan hampir tidak bisa dijawab |
| 6 | Tingkat pemenuhan CPOB | 230 | pertanyaan CPOB kurang akurat |

---

## Batas pembahasan

Audit ini **hanya** membahas domain **Pemeriksaan**. SIPT sebenarnya punya empat domain yang dipisah di pipeline:

```
sipt_sync (34 tabel)
   ├── PEMERIKSAAN  → trx_pemeriksaan, _detail, _temuan, _approval     ← dokumen ini
   ├── PENGAWASAN   → trx_pengawasan, _otsk, _kosmetik, _pangan, _obat_kuasi, _approval
   ├── PENANDAAN    → trx_penandaan, _penilaian_kos/_obat_kuasi/_otsk/_otskok/_pangan
   └── PENGUJIAN    → trx_sampling, _approval, _lhu_kesimpulan, _spk_parameter
```

Kenapa ini penting? Karena **`dim_master_data` itu kamus bersama**. Satu tabel kamus dipakai keempat domain, dibedakan kolom `type`. Jadi kalau ada entri kamus yang hilang, belum tentu itu masalah pemeriksaan — harus dicek dulu apakah type-nya benar-benar dipakai pemeriksaan. Tanpa memisahkan scope, audit akan melaporkan temuan palsu.

Setelah ekstraksi, `staging` memuat:

| Kelompok | Jumlah | Contoh |
|---|---:|---|
| Tabel khusus pemeriksaan | 17 | `fact_pemeriksaan`, `bridge_pemeriksaan_*`, `dim_sarana`, `dim_pemeriksaan_*` |
| Dim general (dipakai bersama) | 8 | `dim_balai`, `dim_master_data`, `dim_produk`, `dim_user`, dll |
| Tabel khusus pengawasan | 26 | `fact_pengawasan`, `bridge_pengawasan_*`, `dim_pengawasan_*` |

Role baca `pemeriksaan_reader` hanya dapat 25 tabel (17 + 8), tidak bisa melihat tabel pengawasan.

```sql
-- tabel khusus pemeriksaan (16 ber-nama *pemeriksaan* + dim_sarana)
SELECT relname FROM pg_class
WHERE relnamespace='public'::regnamespace AND relkind='r'
  AND relname LIKE '%pemeriksaan%'
UNION SELECT 'dim_sarana';

-- tabel khusus pengawasan (25 ber-nama *pengawasan* + dim_kesimpulan_penilaian)
SELECT relname FROM pg_class
WHERE relnamespace='public'::regnamespace AND relkind='r'
  AND relname LIKE '%pengawasan%'
UNION SELECT 'dim_kesimpulan_penilaian';

-- pastikan dim_sarana memang tidak dipakai domain pengawasan
SELECT table_name, column_name FROM information_schema.columns
WHERE table_schema='public' AND table_name LIKE '%pengawasan%'
  AND column_name LIKE '%sarana%';
-- kosong: dim_sarana memang milik pemeriksaan saja
```

---

## Bagaimana data mengalir

```
Aplikasi SIPT 3.0 (dipakai petugas)
        │  simpan
        ▼
PostgreSQL produksi SIPT
        │  sync Airbyte
        ▼
sipt_sync                      ← sumber mentah, 34 tabel, 4 domain
        │  pipeline ekstraksi   (dipecah per domain)
        ▼
staging                        ← ditata jadi fact / dim / bridge
        │  GRANT SELECT
        ▼
pemeriksaan_reader             ← 25 tabel, read-only
```

Tabel sumber yang dipakai domain pemeriksaan — hanya 7 dari 34:

| Tabel sumber | Baris | Jadi apa di staging |
|---|---:|---|
| `trx_pemeriksaan` | 259.348 aktif | `fact_pemeriksaan` |
| `trx_pemeriksaan_detail` | 307.482 | `no_surat`, `tgl_surat`, `bridge_pemeriksaan_petugas` |
| `trx_pemeriksaan_temuan` | 308.295 | `bridge_pemeriksaan_temuan` |
| `trx_pemeriksaan_approval` | 1.352.827 | `fact_pemeriksaan_approval` |
| `trx_sarana` | **441.821** | `dim_sarana` → 441.821 (exact match sejak 21 Sep 2026) |
| `ms_master_data` | **1.999** | `dim_master_data` → 1.999 (exact match sejak 21 Sep 2026) |
| `ms_balai`, `ms_provinsi`, `ms_kabupaten`, `ms_product`, `tb_users` | — | `dim_balai`, `dim_provinsi`, `dim_kabupaten`, `dim_produk`, `dim_user` |

Isi `staging` untuk domain pemeriksaan (19 tabel, kondisi 21 Sep 2026):

| Tabel | Baris |
|---|---:|
| `bridge_pemeriksaan_checklist` | 7.388.165 |
| `bridge_pemeriksaan_skor_operasional` | 1.521.315 |
| `fact_pemeriksaan_approval` | 1.320.680 |
| `bridge_pemeriksaan_petugas` | 553.380 |
| `fact_pemeriksaan_narasi` | 525.894 |
| `dim_sarana` | 441.821 |
| `bridge_pemeriksaan_temuan` | 303.521 |
| `fact_pemeriksaan` | 259.348 |
| `bridge_pemeriksaan_vaksin` | 145.540 |
| `bridge_pemeriksaan_personel_faskes` | 131.898 |
| `fact_pemeriksaan_profil_faskes` | 72.890 |
| `bridge_pemeriksaan_komoditi_pbf` | 34.833 |
| `bridge_pemeriksaan_temuan_observasi` | 27.418 |
| `fact_pemeriksaan_profil_pangan_md` | 26.281 |
| `bridge_pemeriksaan_sertifikat_pangan_md` | 23.404 |
| `bridge_pemeriksaan_fokus_pbf` | 20.117 |
| `bridge_pemeriksaan_narasi_faskes` | 6.930 |
| `dim_master_data` | 1.999 |
| `dim_pemeriksaan_aspek` | 47 |
| `dim_pemeriksaan_kesimpulan` | 14 |

```sql
SELECT 'bridge_pemeriksaan_checklist' t, count(*) FROM bridge_pemeriksaan_checklist
UNION ALL SELECT 'bridge_pemeriksaan_skor_operasional', count(*) FROM bridge_pemeriksaan_skor_operasional
UNION ALL SELECT 'fact_pemeriksaan_approval',           count(*) FROM fact_pemeriksaan_approval
UNION ALL SELECT 'bridge_pemeriksaan_petugas',          count(*) FROM bridge_pemeriksaan_petugas
UNION ALL SELECT 'fact_pemeriksaan_narasi',             count(*) FROM fact_pemeriksaan_narasi
UNION ALL SELECT 'dim_sarana',                          count(*) FROM dim_sarana
UNION ALL SELECT 'fact_pemeriksaan',                    count(*) FROM fact_pemeriksaan
UNION ALL SELECT 'bridge_pemeriksaan_temuan',           count(*) FROM bridge_pemeriksaan_temuan
UNION ALL SELECT 'dim_pemeriksaan_aspek',               count(*) FROM dim_pemeriksaan_aspek
UNION ALL SELECT 'dim_pemeriksaan_kesimpulan',          count(*) FROM dim_pemeriksaan_kesimpulan
ORDER BY 2 DESC;

-- sumber, sebagai pembanding
SELECT count(*) FROM trx_pemeriksaan WHERE deleted_at IS NULL;   -- 259348
SELECT count(*) FROM trx_pemeriksaan_detail;                     -- 307482
SELECT count(*) FROM trx_pemeriksaan_temuan;                     -- 308295
SELECT count(*) FROM trx_pemeriksaan_approval;                   -- 1352827
SELECT count(*) FROM trx_sarana;                                 -- 441821
SELECT count(*) FROM ms_master_data;                             -- 1999
```

---

## Dua jenis kekosongan

Cara memisahkannya sederhana: ambil nilai yang kosong di `staging`, lalu tanyakan ke sumber apakah nilai itu ada di sana.

### Kosong karena sumber memang begitu

| Kolom | Kosong | Hasil cek ke sumber | Kesimpulan |
|---|---:|---|---|
| `bridge_pemeriksaan_petugas.user_id` | 169 | 0 dari 13 user_id ada di `tb_users` | sumber |
| `bridge_pemeriksaan_temuan.tp_product_id` | 15 | 0 ada di `ms_product` | sumber |
| `fact_pemeriksaan_approval.created_by` | 713 | 0 ada di `tb_users` | sumber |
| `dim_sarana.provinsi_id` | 229 | 0 ada di `ms_provinsi` | sumber |
| `dim_sarana.kabupaten_id` | 950 | 0 ada di `ms_kabupaten` | sumber |
| `temuan_observasi.observasi_kode` | 295 | 295 NULL, 0 orphan nyata | sumber |
| `fact_pemeriksaan.grade` | 214.948 | sumber `hp_grade` 44.401 → staging 44.400 | sudah penuh |
| `fact_pemeriksaan.kesimpulan_pusat_id` | 195.600 | Review Pusat memang parsial | memang begitu |
| `kategori_kode` | 410 kode lintas-kamus | kode ada di sumber, di `type` lain | sumber |
| `tindakan_kode` | 610 kode lintas-kamus | kode ada di sumber, di `type` lain | sumber |

Contoh cara kerjanya — kasus petugas:

```sql
-- 1. hitung orphan di staging
SELECT count(*) FILTER (WHERE u.user_id IS NULL) orphan
FROM bridge_pemeriksaan_petugas p
LEFT JOIN dim_user u ON u.user_id = p.user_id;
-- 169

-- 2. ambil user_id yang orphan
SELECT string_agg(DISTINCT p.user_id::text, ',')
FROM bridge_pemeriksaan_petugas p
LEFT JOIN dim_user u ON u.user_id = p.user_id
WHERE u.user_id IS NULL;

-- 3. cek ke sumber (ganti nilai IN dengan hasil langkah 2)
SELECT count(*) FROM tb_users
WHERE user_id IN (14,1845,1905,2477,3000,3007,3289,3340,3354,3388,512,7181,7199);
-- 0  → petugas itu memang tidak terdaftar di sumber
```

Pola yang sama untuk kolom lain:

```sql
-- temuan.tp_product_id
SELECT count(*) FILTER (WHERE d.produk_id IS NULL)
FROM bridge_pemeriksaan_temuan t
LEFT JOIN dim_produk d ON d.produk_id = t.tp_product_id;
-- 15

-- approval.created_by
SELECT count(*) FILTER (WHERE u.user_id IS NULL)
FROM fact_pemeriksaan_approval a
LEFT JOIN dim_user u ON u.user_id = a.created_by;
-- 713

-- dim_sarana.provinsi_id (hitung hanya yang tidak null)
SELECT count(*) FILTER (WHERE p.provinsi_id IS NULL)
FROM dim_sarana s
LEFT JOIN dim_provinsi p ON p.provinsi_id = s.provinsi_id
WHERE s.provinsi_id IS NOT NULL;
-- 229

-- dim_sarana.kabupaten_id
SELECT count(*) FILTER (WHERE k.kabupaten_id IS NULL)
FROM dim_sarana s
LEFT JOIN dim_kabupaten k ON k.kabupaten_id = s.kabupaten_id
WHERE s.kabupaten_id IS NOT NULL;
-- 950

-- observasi_kode: pisahkan NULL dari orphan nyata
SELECT count(*) FILTER (WHERE o.observasi_kode IS NULL) kosong,
       count(*) FILTER (WHERE o.observasi_kode IS NOT NULL
                          AND m.master_data_id IS NULL) orphan_nyata
FROM bridge_pemeriksaan_temuan_observasi o
LEFT JOIN dim_master_data m
       ON m.master_data_id::text = o.observasi_kode
      AND m.type = 'TEMUAN_OBSERVATION';
-- 295 kosong | 0 orphan
```

### Hilang karena ekstraksi

#### Entri kamus hilang

`dim_master_data` adalah tabel kamus yang menyimpan semua daftar pilihan dropdown di aplikasi: jenis sarana, jenis komoditi, kategori temuan, aspek, dan seterusnya. Kalau satu entri hilang di sini, semua baris yang merujuk entri itu kehilangan namanya.

```sql
SELECT count(*) FROM ms_master_data;     -- sumber  : 1999
SELECT count(*) FROM dim_master_data;    -- staging : 1994
```

Cek per entri:

```sql
-- jalankan di kedua database, bandingkan
SELECT count(*) FROM ms_master_data
 WHERE type='JENIS_SARANA' AND id=211337;               -- sumber  : 1
SELECT count(*) FROM dim_master_data
 WHERE type='JENIS_SARANA' AND master_data_id=211337;   -- staging : 0
```

Selengkapnya:

| Type | ID | Nama | Dipakai pemeriksaan? |
|---|---|---|---|
| JENIS_SARANA | 211337 | Pangan MD (old) | Ya |
| JENIS_SARANA | 211626 | Pangan (old) | Ya |
| TL_DISTRIBUSI | 211308 | Penghentian Sementara Kegiatan | Ya |
| JENIS_PANGAN | 211236 | Surat Peringatan | Tidak |
| TUJUAN_SAMPLING | 223492 | Sarana Tidak Berizin | Tidak |

Dua entri terakhir bukan milik pemeriksaan. Buktinya:

```sql
-- JENIS_PANGAN tidak pernah dirujuk pemeriksaan
SELECT count(*) FROM fact_pemeriksaan f
JOIN dim_master_data m ON m.master_data_id::text = f.jenis_pangan_kode::text
                      AND m.type = 'JENIS_PANGAN'
WHERE f.jenis_pangan_kode IS NOT NULL;      -- 0

-- TUJUAN_SAMPLING juga tidak
SELECT count(*) FROM fact_pemeriksaan f
JOIN dim_master_data m ON m.master_data_id = f.tujuan_id
                      AND m.type = 'TUJUAN_SAMPLING';   -- 0
```

Type yang benar-benar dipakai pemeriksaan:

```sql
SELECT 'JENIS_SARANA'       t, count(*) FROM fact_pemeriksaan f JOIN dim_master_data m ON m.master_data_id=f.jenis_id AND m.type='JENIS_SARANA'
UNION ALL SELECT 'TUJUAN_PEMERIKSAAN', count(*) FROM fact_pemeriksaan f JOIN dim_master_data m ON m.master_data_id=f.tujuan_id AND m.type='TUJUAN_PEMERIKSAAN'
UNION ALL SELECT 'JENIS_KLASIFIKASI',  count(*) FROM fact_pemeriksaan f JOIN dim_master_data m ON m.master_data_id=f.klasifikasi_id AND m.type='JENIS_KLASIFIKASI'
UNION ALL SELECT 'TL_DISTRIBUSI',      count(*) FROM fact_pemeriksaan f, LATERAL jsonb_array_elements_text(f.tl_saran) k(x) JOIN dim_master_data m ON m.master_data_id::text=k.x AND m.type='TL_DISTRIBUSI';
-- 259346 | 258401 | 259348 | 11783
```

#### Sarana tidak tersinkron

```sql
SELECT count(*) FROM trx_sarana;    -- sumber  : 441821
SELECT count(*) FROM dim_sarana;    -- staging : 440192
```

Selisih 1.629 sarana. Dari 87 kasus yang `sarana_id`-nya tidak ketemu, 63 di antaranya sebenarnya ada di sumber:

```sql
-- 1. ambil sarana_id yang orphan di staging
SELECT string_agg(DISTINCT f.sarana_id::text, ',')
FROM fact_pemeriksaan f
LEFT JOIN dim_sarana s ON s.sarana_id = f.sarana_id
WHERE s.sarana_id IS NULL;

-- 2. cek ke sumber
SELECT count(*) FROM trx_sarana WHERE id IN (<hasil langkah 1>);
-- 63 dari 87 ada di sumber
```

Dampaknya: 63 kasus pemeriksaan kehilangan nama dan alamat sarana yang diperiksa, padahal datanya tersedia.

#### Gap aspek pelayanan — penyebab utamanya varian vaksin

> **Sudah diperbaiki.** Bagian ini menjelaskan asal gap 9.271 kasus pelayanan yang dulu kosong. Setelah tim data memetakan varian vaksin ke `bridge_pemeriksaan_vaksin`, gap `clusterC_skor` turun dari 9.271 menjadi 398. Angka di bawah adalah kondisi sebelum perbaikan, disimpan sebagai catatan asal masalah.

Dari 9.271 kasus pelayanan yang kosong di staging, penyebabnya dipecah lewat perbandingan dengan sumber. Hasilnya bukan backfill tahun lama, melainkan section varian vaksin yang belum dipetakan.

```sql
-- langkah 1: ambil ID kasus yang kosong di staging
SELECT string_agg(f.id::text, ',') AS ids
FROM fact_pemeriksaan f
LEFT JOIN (SELECT DISTINCT pemeriksaan_id FROM bridge_pemeriksaan_skor_operasional) s
       ON s.pemeriksaan_id = f.id
WHERE f.flag_varian_datas = 'clusterC_skor' AND s.pemeriksaan_id IS NULL;

-- langkah 2: jalankan di sumber, pecah penyebabnya (ganti <ids>)
SELECT count(*)                                                       total,
       count(*) FILTER (WHERE datas IS NULL)                          tak_ada_datas,
       count(*) FILTER (WHERE datas::text LIKE '%_vaksin_%')          varian_vaksin,
       count(*) FILTER (WHERE datas IS NOT NULL
                          AND datas::text NOT LIKE '%_vaksin_%')     gap_murni
FROM trx_pemeriksaan WHERE id IN (<ids>);
-- 9271 | 395 | 7693 | 1183
```

Hasilnya:

| Penyebab | Kasus | Porsi | Sifat |
|---|---:|---:|---|
| Varian vaksin | 7.693 | 83,0% | form vaksin belum dipetakan |
| Data standar belum diekstrak | 1.183 | 12,8% | backfill belum tuntas |
| Datas NULL (masih DRAFT) | 395 | 4,3% | wajar |

Sebaran per tahun:

```sql
SELECT extract(year FROM tgl_start)::int thn,
       count(*) FILTER (WHERE datas::text LIKE '%_vaksin_%') varian_vaksin,
       count(*) FILTER (WHERE datas IS NOT NULL
                          AND datas::text NOT LIKE '%_vaksin_%') gap_murni,
       count(*) FILTER (WHERE datas IS NULL) kosong
FROM trx_pemeriksaan WHERE id IN (<ids>)
GROUP BY 1 ORDER BY 1;
```

| Tahun | Varian vaksin | Gap murni | Kosong |
|---:|---:|---:|---:|
| 2020 | 1 | 78 | 23 |
| 2021 | 5.363 | 177 | 28 |
| 2022 | 1.852 | 414 | 26 |
| 2023 | 425 | 153 | 38 |
| 2024 | 49 | 149 | 14 |
| 2025 | 1 | 139 | 15 |
| 2026 | 2 | 73 | 25 |
| tanpa tanggal | 0 | 0 | 226 |

**Kenapa bisa terjadi?** Formulir pemeriksaan pelayanan punya satu varian khusus untuk program vaksin. Section-nya diberi akhiran `_vaksin_`:

```
tx_pengadaan_vaksin_1 .. _4
tx_penyimpanan_vaksin_1 .. _8
tx_pemusnahan_vaksin_1 .. _2
tx_personil_vaksin_1 .. _3
tx_lainnya_vaksin_1 .. _2
```

Kamus aspek (`dim_pemeriksaan_aspek`) hanya memuat 47 nama section versi standar, tidak memuat nama berakhiran `_vaksin_`. Akibatnya saat parsing, semua section vaksin dilewati dan kasus itu masuk sebagai kasus kosong.

```sql
-- sumber: berapa kasus pakai varian vaksin
SELECT count(*) FROM trx_pemeriksaan
WHERE deleted_at IS NULL AND datas IS NOT NULL
  AND jenis_id IN (109,107,108,105,106,748)
  AND datas::text LIKE '%_vaksin_%';                  -- 7697

-- staging: cek 5 kasus contoh, semuanya 0 baris
SELECT f.id,
       (SELECT count(*) FROM bridge_pemeriksaan_skor_operasional s
        WHERE s.pemeriksaan_id = f.id) baris_skor
FROM fact_pemeriksaan f
WHERE f.id IN (247853,229048,222173,207531,202509);
```

#### Kekritisan dan CPOB belum tersinkron

```sql
-- sumber: berapa kasus punya hp_level (kekritisan)
SELECT count(*) FILTER (WHERE j ? 'hp_level') AS hp_level
FROM (SELECT (result::jsonb #>> '{}')::jsonb j FROM trx_pemeriksaan
      WHERE deleted_at IS NULL AND result IS NOT NULL) r;
-- 9100

-- staging: berapa kasus yang counternya terisi
SELECT count(*) FILTER (WHERE kritis_count IS NOT NULL
                           OR major_count IS NOT NULL
                           OR minor_count IS NOT NULL) AS counter
FROM fact_pemeriksaan;
-- 609

-- sumber vs staging untuk tingkat pemenuhan CPOB
SELECT count(*) FILTER (WHERE j ? 'hp_pemenuhan') FROM (
  SELECT (result::jsonb #>> '{}')::jsonb j FROM trx_pemeriksaan
  WHERE deleted_at IS NULL AND result IS NOT NULL) r;
-- sumber 876

SELECT count(*) FROM fact_pemeriksaan
WHERE kesimpulan_balai_id IN (791,792,793,794);
-- staging 646
```

Tingkat CPOB kehilangan 230 kasus. Yang lebih serius: kekritisan kehilangan 8.491 kasus, atau 93%.

---

## Alur entri user

Bagian ini menjelaskan apa yang petugas lakukan di aplikasi, dan data itu mendarat di tabel mana.

### FLOW 1 — Entri Baru

Petugas memilih jenis sarana, komoditi, versi formulir, provinsi/kabupaten, nama sarana, mengisi nomor dan tanggal surat tugas, memilih unit/balai, lalu memilih petugas (bisa 1 sampai 5 orang). Setelah klik Proses:

```
   ├─► fact_pemeriksaan            (jenis_id, klasifikasi_id, tujuan_id,
   │                                sarana_id, balai_id, tgl_start, tgl_end)
   ├─► fact_pemeriksaan            (no_surat, tgl_surat)
   │      diambil dari baris trx_pemeriksaan_detail terbaru,
   │      karena satu kasus bisa punya lebih dari satu surat tugas bila direvisi
   └─► bridge_pemeriksaan_petugas  (N baris, satu per petugas)
```

Sebaran jumlah petugas per kasus — ini penting karena menentukan cara menghitung:

```sql
SELECT n, count(*) kasus FROM (
  SELECT pemeriksaan_id, count(*) n
  FROM bridge_pemeriksaan_petugas GROUP BY 1
) x GROUP BY 1 ORDER BY 1;
```

| Petugas | Kasus |
|---:|---:|
| 1 | 17.173 |
| 2 | 204.171 |
| 3 | 26.455 |
| 4 | 9.809 |
| 5 | 1.285 |
| 6–12 | 421 |

Paling umum 2 orang, sesuai SOP pemeriksaan. Artinya kalau menghitung "berapa pemeriksaan", jangan pakai tabel petugas — hasilnya akan sekitar dua kali lipat.

### FLOW 2 — Wizard Pemeriksaan

Petugas mengisi tanggal pemeriksaan, tujuan (Rutin/Kasus), menjawab popup "Apakah ada kasus?", dan memilih metode inspeksi. Semua masuk ke `fact_pemeriksaan` langsung, tidak ada tabel terpisah.

```sql
SELECT count(*) total, count(metode_inspeksi) terisi
FROM fact_pemeriksaan;
-- 259348 | 4101 (1,6%)
```

Metode inspeksi hampir tidak pernah diisi. Kalau ada pertanyaan soal remote vs on-site, datanya terlalu tipis untuk diandalkan.

### FLOW 3 — Inspeksi varian pelayanan

Delapan langkah, satu langkah per aspek: Pengadaan, Penerimaan, Penyimpanan, Pendistribusian, Penyerahan, Pengembalian+Pencatatan, Pemusnahan.

Petugas menjawab tiap pertanyaan dengan pilihan: Ya / Sebagian Besar / Sebagian Kecil / Tidak / Ilegal. Jawaban itu tersimpan dengan skor.

```
jawaban skor → datas {"tx_pengadaan_obat":{"opsi":"yes","n":"300","fp":"3","score":"100"}}
   → flag_varian_datas = clusterC_skor (64.243 kasus)
   → bridge_pemeriksaan_skor_operasional
   → dim_pemeriksaan_aspek
```

### FLOW 3B — Inspeksi varian produksi

Varian ini beda. Semua aspek diisi dalam satu langkah, bentuknya klausul bernomor (`a1`, `a2`, …) dengan jawaban Ya/Tidak plus catatan.

```
klausul → datas {"tx_pemeriksaan":{"penyimpanan":{"gudang":{"a3":{"p1":{...}}}}}}
   ├─ pola1_direct / pola1_nested / pola1_observation (179.465)
   │     → bridge_pemeriksaan_checklist
   └─ pola2_klasifikasi (4.137)
         → bridge_pemeriksaan_temuan_observasi
```

### FLOW 4 — Hasil inspeksi dan tindak lanjut

Petugas mengisi kesimpulan, grade, daftar temuan produk, catatan, dan tindak lanjut.

```
   ├─► fact_pemeriksaan            (grade, counter, tl_capa, tl_attachment,
   │                                tl_ba, tl_saran, kesimpulan_balai_id)
   ├─► bridge_pemeriksaan_temuan
   └─► fact_pemeriksaan_narasi     (9 jenis_narasi)
```

```sql
SELECT jenis_narasi, count(*) FROM fact_pemeriksaan_narasi
GROUP BY 1 ORDER BY 2 DESC;
```

| jenis_narasi | Baris |
|---|---:|
| catatan_balai | 189.159 |
| tindak_lanjut_detil | 125.998 |
| hasil_balai | 117.461 |
| tindak_lanjut_detil_pusat | 34.524 |
| hasil_pusat | 23.464 |
| catatan_pusat | 15.872 |
| rekomendasi | 7.782 |
| analisa | 6.835 |
| detail_tmk | 4.799 |

Catatan teks dipisah ke tabel sendiri karena isinya panjang. Kalau ditaruh di tabel utama, tabelnya jadi berat.

### FLOW 5 — Edit

Update di tempat, tidak ada versioning. Kolom `updated_at` dan `updated_by` tidak diekstrak, jadi di `staging` tidak ada jejak kapan sebuah kasus terakhir diubah.

### FLOW 6 — Kirim

Petugas klik Kirim, dan dua hal terjadi sekaligus: `status_id` berubah dari DRAFT ke VERIFY1, dan satu baris masuk ke `fact_pemeriksaan_approval`.

### FLOW 7 — Verifikasi berjenjang

Enam tingkat: Operator → Supervisor Balai → Kepala Balai → Operator Pusat → Supervisor Pusat → Direktur. Tiap tingkat menambah satu baris approval dan menggeser status.

```sql
SELECT sc.status_code, count(*) kasus
FROM fact_pemeriksaan f
JOIN dim_status_code sc ON sc.id = f.status_id AND sc.domain = 'pemeriksaan'
GROUP BY 1 ORDER BY 2 DESC;
```

| Status | Kasus | Porsi | Arti |
|---|---:|---:|---|
| VERIFY4 | 167.116 | 64,4% | macet di Operator Pusat |
| VERIFY5 | 46.619 | 18,0% | di Supervisor Pusat |
| FINISHED | 29.042 | 11,2% | selesai |
| DRAFT_REVISE | 5.108 | 2,0% | dikembalikan |
| VERIFY7 | 4.784 | 1,8% | |
| DRAFT | 3.297 | 1,3% | belum dikirim |
| VERIFY6 | 1.008 | 0,4% | |
| VERIFY1 | 640 | 0,2% | |

Hampir dua pertiga kasus berhenti di Operator Pusat. Ini temuan operasional yang penting: bukan masalah data, tapi masalah alur kerja.

---

## Bridge

### Kenapa ada tabel bridge

Bayangkan satu pemeriksaan dikerjakan dua petugas. Kalau kedua nama petugas ditaruh di satu baris pemeriksaan, bentuknya jadi:

```
Kasus #123 | Petugas 1: Budi | Petugas 2: Siti
```

Ini masih muat. Tapi bagaimana kalau satu kasus punya 9 temuan produk, 166 item checklist, dan 5 event approval? Tidak mungkin dimasukkan ke satu baris.

Jalan keluarnya: pisahkan. Tabel utama menyimpan kasusnya, tabel bridge menyimpan detailnya satu per baris.

```
fact_pemeriksaan          1 baris = 1 kasus        → 259.348
bridge_pemeriksaan_petugas 1 baris = 1 petugas      → 553.380
bridge_pemeriksaan_temuan  1 baris = 1 temuan       → 303.521
bridge_pemeriksaan_checklist 1 baris = 1 item       → 7.388.165
```

Bridge itu seperti jembatan: menyambungkan data pemeriksaan dengan data dimensi.

```
Data Pemeriksaan
       │
       ▼
   BRIDGE
   │    │
   ▼    ▼
dim_user   dim_produk
```

Contohnya, kasus 287342 dikerjakan Apoteker dan TTK:

```sql
SELECT u.fullname, p.urutan
FROM bridge_pemeriksaan_petugas p
JOIN dim_user u ON u.user_id = p.user_id
WHERE p.pemeriksaan_id = 287342
ORDER BY p.urutan;
-- urutan 1: Apoteker | urutan 2: TTK
```

### Kenapa bridge-nya banyak

Karena isian wizard disimpan di satu kolom JSON bernama `datas`, dan bentuk JSON-nya berbeda-beda tergantung jenis sarana. Satu kolom, banyak bentuk. Jadi saat ekstraksi, kolom itu dipecah ke beberapa tabel sesuai bentuknya.

Untuk tahu kasus tertentu masuk tabel mana, lihat `flag_varian_datas`:

```sql
SELECT flag_varian_datas, count(*),
       round(100.0*count(*)/sum(count(*)) OVER (), 1) pct
FROM fact_pemeriksaan GROUP BY 1 ORDER BY 2 DESC;
```

| flag_varian_datas | Kasus | Porsi | Baca bridge mana |
|---|---:|---:|---|
| pola1_direct | 107.778 | 41,6% | bridge_pemeriksaan_checklist |
| clusterC_skor | 64.243 | 24,8% | bridge_pemeriksaan_skor_operasional |
| pola1_nested | 61.266 | 23,6% | bridge_pemeriksaan_checklist |
| pola1_observation | 10.421 | 4,0% | bridge_pemeriksaan_checklist |
| clusterC_vaksin | 7.697 | 3,0% | bridge_pemeriksaan_vaksin |
| pola2_klasifikasi | 4.137 | 1,6% | bridge_pemeriksaan_temuan_observasi |
| clusterF_cpkb | 2.610 | 1,0% | belum ada bridge |
| clusterC_naratif | 1.182 | 0,5% | bridge_pemeriksaan_narasi_faskes |
| lainnya | 14 | 0,0% | belum ada bridge |

**Ini jebakan nomor satu di domain ini.** Kalau flag-nya `clusterC_skor` tapi yang dibaca `bridge_pemeriksaan_checklist`, hasilnya kosong — dan tidak ada pesan error. Orang akan menyimpulkan "tidak ada data" padahal salah tabel.

### Coverage nyata

```sql
WITH b AS (
  SELECT pemeriksaan_id FROM bridge_pemeriksaan_checklist
  UNION SELECT pemeriksaan_id FROM bridge_pemeriksaan_skor_operasional
  UNION SELECT pemeriksaan_id FROM bridge_pemeriksaan_temuan_observasi
  UNION SELECT pemeriksaan_id FROM bridge_pemeriksaan_vaksin
  UNION SELECT pemeriksaan_id FROM bridge_pemeriksaan_narasi_faskes
)
SELECT f.flag_varian_datas, count(*) kasus,
       count(b.pemeriksaan_id) punya_bridge,
       count(*) - count(b.pemeriksaan_id) tanpa_bridge
FROM fact_pemeriksaan f LEFT JOIN b ON b.pemeriksaan_id = f.id
GROUP BY 1 ORDER BY 4 DESC;
```

| flag | Kasus | Punya bridge | Tanpa bridge | % gap |
|---|---:|---:|---:|---:|
| pola1_direct | 107.778 | 97.567 | 10.211 | 9,5% |
| clusterF_cpkb | 2.610 | 0 | 2.610 | 100% |
| pola1_observation | 10.421 | 8.756 | 1.665 | 16,0% |
| clusterC_skor | 64.243 | 63.845 | 398 | 0,6% |
| pola1_nested | 61.266 | 61.012 | 254 | 0,4% |
| clusterC_naratif | 1.182 | 1.037 | 145 | 12,3% |
| pola2_klasifikasi | 4.137 | 4.022 | 115 | 2,8% |
| lainnya | 14 | 0 | 14 | 100% |
| clusterC_vaksin | 7.697 | 7.697 | 0 | 0% |

Kasus tanpa baris bridge turun dari 24.140 menjadi **15.412**. Penurunan terbesar dari `clusterC_vaksin` (7.697 kasus, sebelumnya nol baris) dan `clusterC_skor` (9.271 → 398).

Sisa yang belum tertutup: `pola1_direct` 10.211, `clusterF_cpkb` 2.610 (memang belum ada bridge), `pola1_observation` 1.665, dan sisanya kecil-kecil.

### Daftar bridge dan cara query-nya

**1. bridge_pemeriksaan_petugas** — siapa saja yang memeriksa

```sql
SELECT u.fullname, p.urutan
FROM bridge_pemeriksaan_petugas p
JOIN dim_user u ON u.user_id = p.user_id
WHERE p.pemeriksaan_id = 287342
ORDER BY p.urutan;
```

**2. bridge_pemeriksaan_temuan** — produk apa saja yang bermasalah

```sql
SELECT d.nama_produk, t.kategori_kode, t.tindakan_kode,
       t.jumlah_temuan, t.harga_total, t.is_kasus_draft
FROM bridge_pemeriksaan_temuan t
LEFT JOIN dim_produk d ON d.produk_id = t.tp_product_id
WHERE t.pemeriksaan_id = 286734;
```

**3. bridge_pemeriksaan_checklist** — item pemeriksaan per klausul

Ini bridge terbesar. Satu kasus bisa punya ratusan baris:

```sql
SELECT pemeriksaan_id, count(*) FROM bridge_pemeriksaan_checklist
GROUP BY 1 ORDER BY 2 DESC LIMIT 3;
-- 34235 | 166
-- 15805 | 166
-- 52364 | 166
```

```sql
SELECT path, nilai_aspek, catatan
FROM bridge_pemeriksaan_checklist
WHERE pemeriksaan_id = 192906
ORDER BY path;
```

**4. bridge_pemeriksaan_temuan_observasi** — temuan GMP per kode observasi

```sql
SELECT o.urutan, m.name AS observasi, o.kriteria, o.catatan
FROM bridge_pemeriksaan_temuan_observasi o
LEFT JOIN dim_master_data m
       ON m.master_data_id::text = o.observasi_kode
      AND m.type = 'TEMUAN_OBSERVATION'
WHERE o.pemeriksaan_id = 98016
ORDER BY o.urutan;
```

**5. bridge_pemeriksaan_skor_operasional** — nilai per aspek

```sql
SELECT a.area_key, COALESCE(a.aspek_ktl_nama, a.aspek_label) aspek,
       s.opsi, s.n, s.fp, s.score
FROM bridge_pemeriksaan_skor_operasional s
JOIN dim_pemeriksaan_aspek a ON a.area_key = s.area_key
WHERE s.pemeriksaan_id = 97747
ORDER BY a.area_key;
```

**6. bridge_pemeriksaan_komoditi_pbf** — komoditi yang diperiksa

```sql
SELECT m.name AS komoditi
FROM bridge_pemeriksaan_komoditi_pbf b
JOIN dim_master_data m
       ON m.master_data_id::text = b.komoditi_kode
      AND m.type = 'KOMODITI'
WHERE b.pemeriksaan_id = :id;
```

Meski namanya "pbf", cakupannya tiga jenis sarana: PBF, IFK, dan IFP. Ketiganya memakai bentuk formulir yang sama.

**7. bridge_pemeriksaan_fokus_pbf** — fokus pemeriksaan

```sql
SELECT m.name AS fokus
FROM bridge_pemeriksaan_fokus_pbf b
JOIN dim_master_data m
       ON m.master_data_id::text = b.fokus_kode
      AND m.type = 'FOKUS_PEMERIKSAAN'
WHERE b.pemeriksaan_id = :id;
```

**8. bridge_pemeriksaan_sertifikat_pangan_md** — sertifikat yang dimiliki sarana

```sql
SELECT urutan, jenis, jenis_lainnya, nomor, lembaga, expired
FROM bridge_pemeriksaan_sertifikat_pangan_md
WHERE pemeriksaan_id = :id
ORDER BY urutan;
```

**9. bridge_pemeriksaan_personel_faskes** — peran personel di fasilitas kesehatan

```sql
SELECT urutan, peran
FROM bridge_pemeriksaan_personel_faskes
WHERE pemeriksaan_id = 287342
ORDER BY urutan;
```

**10. bridge_pemeriksaan_vaksin** — isian form vaksin per section (baru, 145.540 baris)

```sql
SELECT section_key, opsi, jumlah, observasi, perbaikan, intervensi
FROM bridge_pemeriksaan_vaksin
WHERE pemeriksaan_id = :id
ORDER BY section_key;
```

Cakupan: `flag_varian_datas = 'clusterC_vaksin'` (7.697 kasus, dominan PKM). Isinya 19 `section_key`, semuanya berakhiran `_vaksin_`. `section_key` belum punya kamus, jadi masih teks mentah.

**11. bridge_pemeriksaan_narasi_faskes** — narasi per section (baru, 6.930 baris)

```sql
SELECT section, teks
FROM bridge_pemeriksaan_narasi_faskes
WHERE pemeriksaan_id = :id
ORDER BY section;
```

Cakupan: `flag_varian_datas = 'clusterC_naratif'` (1.182 kasus, dominan Apotek). Isinya 8 `section` tetap: `profil`, `pengadaan`, `penyimpanan`, `distribusi`, `personalia`, `dokumentasi`, `gudang`, `lain`. Bentuknya narasi bebas, bukan checklist berkode.

**12 dan 13. Dua tabel satelit**

Keduanya mirip bridge tapi sebenarnya 1:1 dengan kasus, bukan 1:N. Isinya profil sarana.

```sql
SELECT pimpinan, skala_usaha, jumlah_karyawan, proses_pengolahan
FROM fact_pemeriksaan_profil_pangan_md
WHERE pemeriksaan_id = :id;

SELECT jenis_id, penanggungjawab, ap_oprs, resep
FROM fact_pemeriksaan_profil_faskes
WHERE pemeriksaan_id = :id;
```

Catatan: kolom di tabel profil faskes tidak seragam antar jenis sarana. Kolom `akreditasi` hanya berisi untuk Apotek, `penanggungjawab` hanya untuk PKM, `layanan` hanya untuk Klinik. Kolom lain pasti NULL. Jadi cek `jenis_id` dulu sebelum memakai.

### Cek semua bridge satu kasus

```sql
SELECT f.id,
       (SELECT count(*) FROM bridge_pemeriksaan_checklist        WHERE pemeriksaan_id=f.id) checklist,
       (SELECT count(*) FROM bridge_pemeriksaan_skor_operasional WHERE pemeriksaan_id=f.id) skor,
       (SELECT count(*) FROM bridge_pemeriksaan_temuan           WHERE pemeriksaan_id=f.id) temuan,
       (SELECT count(*) FROM bridge_pemeriksaan_petugas          WHERE pemeriksaan_id=f.id) petugas,
       (SELECT count(*) FROM fact_pemeriksaan_approval           WHERE pemeriksaan_id=f.id) approval,
       (SELECT count(*) FROM fact_pemeriksaan_narasi             WHERE pemeriksaan_id=f.id) narasi
FROM fact_pemeriksaan f
WHERE f.id = 287342;
-- checklist 0 | skor 22 | temuan 0 | petugas 2 | approval 5 | narasi 6
```

Query ini berguna saat menyelidiki satu kasus: langsung kelihatan kasus itu datanya ada di bridge mana.

---

## Aturan join

Enam pola join berlaku di domain ini. Masing-masing punya alasan.

**Pola 1 — angka biasa ke kamus, wajib sebutkan type**

```sql
LEFT JOIN dim_master_data m
       ON m.master_data_id = f.jenis_id
      AND m.type = 'JENIS_SARANA'
```

Kenapa `type` wajib? Karena `dim_master_data` itu satu tabel besar berisi puluhan kamus. Kolom `master_data_id` bisa cocok dengan entri dari kamus mana pun. Tanpa `type`, join-nya jalan tapi maknanya tidak jelas.

Dipakai di: `jenis_id`, `tujuan_id`, `klasifikasi_id`, `metode_inspeksi`, `kasus_id`, `unit_id`, `unit_kode`, `klasifikasi_produk_kode`.

**Pola 2 — kolom teks berisi angka, wajib di-cast**

```sql
LEFT JOIN dim_master_data m
       ON m.master_data_id::text = o.observasi_kode
      AND m.type = 'TEMUAN_OBSERVATION'
```

`observasi_kode` bertipe teks, sementara `master_data_id` bertipe angka. Tanpa `::text`, join gagal — dan gagalnya tanpa pesan error, hasilnya cuma kosong.

Dipakai di: `observasi_kode`, `komoditi_kode`, `fokus_kode`.

**Pola 3 — kolom array, harus di-expand dulu**

```sql
CROSS JOIN LATERAL jsonb_array_elements_text(t.kategori_kode) AS k(kode)
LEFT JOIN dim_master_data m
       ON m.master_data_id::text = k.kode
      AND m.type = 'KATEGORI_TEMUAN_PRODUK'
```

Sebagian kolom menyimpan daftar, bukan satu nilai. Contoh `kategori_kode` bisa berisi `["499","506"]` — produk itu kena dua kategori sekaligus. Untuk menjangkaunya, array harus dipecah dulu jadi baris.

**Pola 4 — satu kolom merujuk beberapa kamus**

Ini yang paling berbahaya. Tiga kolom terverifikasi seperti ini:

```sql
-- jenis_pangan_kode: 2 kamus
SELECT 'PRODUK_PANGAN' t, count(*) FROM fact_pemeriksaan f,
  LATERAL jsonb_array_elements_text(f.jenis_pangan_kode) k(x)
  JOIN dim_master_data m ON m.master_data_id::text=k.x AND m.type='PRODUK_PANGAN'
UNION ALL
SELECT 'JENIS_PANGAN_68', count(*) FROM fact_pemeriksaan f,
  LATERAL jsonb_array_elements_text(f.jenis_pangan_kode) k(x)
  JOIN dim_master_data m ON m.master_data_id::text=k.x AND m.type='JENIS_PANGAN_68';
-- 46521 | 20915

-- tl_saran: 7 kamus
SELECT m.type, count(*) FROM fact_pemeriksaan f,
  LATERAL jsonb_array_elements_text(f.tl_saran) k(x)
  JOIN dim_master_data m ON m.master_data_id::text=k.x
GROUP BY 1 ORDER BY 2 DESC;

-- legal_id: 2 kamus
SELECT m.type, count(*) FROM dim_sarana s
JOIN dim_master_data m ON m.master_data_id = s.legal_id
WHERE s.legal_id IS NOT NULL GROUP BY 1 ORDER BY 2 DESC;
-- BENTUK_PERUSAHAAN 241769 | JENIS_SARANA 169067
```

| Kolom | Kamus yang dirujuk | Kalau salah filter |
|---|---|---|
| `dim_sarana.legal_id` | BENTUK_PERUSAHAAN 241.769 + JENIS_SARANA 169.067 + tanpa match 29.356 | kehilangan 45% baris |
| `fact_pemeriksaan.tl_saran` | 7 kamus, SARAN_TINDAK_LANJUT hanya 116.831 (51%) | hanya benar 51% |
| `fact_pemeriksaan.jenis_pangan_kode` | PRODUK_PANGAN 46.521 + JENIS_PANGAN_68 20.915 | kehilangan 31% |
| `fact_pemeriksaan.penelusuran_id` | PENELUSURAN atau TL_PENELUSURAN | sudah didokumentasikan |

Masalahnya sama dengan pola 1, tapi lebih parah: kalau kita filter satu `type` saja, sebagian baris hilang tanpa peringatan.

**Pola 5 — join ke tabel dimensi khusus**

```sql
JOIN dim_pemeriksaan_kesimpulan k ON k.id = f.kesimpulan_balai_id
JOIN dim_pemeriksaan_aspek      a ON a.area_key = s.area_key
JOIN dim_status_code            c ON c.id = f.status_id AND c.domain = 'pemeriksaan'
```

Khusus tabel approval, join-nya berbeda — pakai kolom teks, bukan id:

```sql
SELECT a.act_steps, a.to_steps, a.status, s.status_label, a.notes, a.created_at
FROM fact_pemeriksaan_approval a
JOIN dim_status_code s ON s.status_code = a.status AND s.domain = 'pemeriksaan'
WHERE a.pemeriksaan_id = 291155
ORDER BY a.id;
```

Konsepnya sama (status kasus), tapi di tabel fact join ke `id`, di tabel approval join ke `status_code`. Ini mudah tertukar.

**Pola 6 — join ke tabel fact, hati-hati jumlah baris**

```sql
JOIN fact_pemeriksaan f ON f.id = b.pemeriksaan_id
```

Selalu ingat: menggabungkan fact dengan bridge akan menambah jumlah baris. 259.348 kasus menjadi 553.380 baris kalau di-join dengan petugas.

---

## Kamus dan aspek

### Kelengkapan kamus

```sql
SELECT count(*) FROM ms_master_data;     -- 1999
SELECT count(*) FROM dim_master_data;    -- 1994
```

5 entri hilang. Tiga di antaranya dipakai pemeriksaan, dua tidak.

### Kenapa Penerimaan dan Pengembalian "belum ada di kamus"

Ini pertanyaan yang sering membingungkan, jadi dijelaskan bertahap.

**Langkah 1.** Kamus resmi BPOM untuk aspek, namanya `ASPEK_KTL`, hanya berisi 10 entri:

```sql
SELECT id, code, name FROM ms_master_data WHERE type='ASPEK_KTL' ORDER BY id;
```

| id | code | nama |
|---|---|---|
| 476 | 01 | Label |
| 477 | 02 | Pemusnahan |
| 478 | 03 | Pencatatan dan Pelaporan |
| 479 | 04 | Pengadaan |
| 480 | 05 | Penyaluran |
| 481 | 06 | Penyerahan |
| 482 | 07 | Penyimpanan |
| 483 | 08 | Perizinan |
| 484 | 09 | Personalia |
| 485 | 10 | Produksi |

**Langkah 2.** Penerimaan dan Pengembalian tidak ada di situ. Pencarian ke seluruh kamus:

```sql
SELECT type, id, name FROM ms_master_data
WHERE lower(name) ~ '(penerimaan|pengembalian)';
-- kosong
```

**Langkah 3.** Tapi formulir pemeriksaan tetap punya kedua aspek itu. Namanya muncul sebagai section di JSON: `tx_penerimaan_obat`, `tx_penerimaan_param`, `tx_pengembalian_mutasi`, `tx_pengembalian_retur`, `tx_pengembalian_sipnap`.

**Langkah 4.** Karena itu, saat ekstraksi dibuatlah tabel `dim_pemeriksaan_aspek` yang memetakan nama section formulir ke label aspek. Hasilnya 47 baris: 40 berstatus `resmi` (ada padanannya di kamus BPOM) dan 7 berstatus `belum_ada_di_kamus`.

```sql
SELECT area_key, aspek_ktl_nama, aspek_label, status_kamus
FROM dim_pemeriksaan_aspek
WHERE status_kamus = 'belum_ada_di_kamus'
ORDER BY area_key;
```

**Langkah 5.** Konsekuensinya, saat menampilkan label aspek harus begini:

```sql
SELECT COALESCE(a.aspek_ktl_nama, a.aspek_label) AS aspek
FROM bridge_pemeriksaan_skor_operasional s
JOIN dim_pemeriksaan_aspek a ON a.area_key = s.area_key;
```

Kalau tidak pakai COALESCE, Penerimaan (127.702 item) dan Pengembalian (146.958 item) — dua aspek dengan volume terbesar — akan hilang dari hasil.

Kesimpulannya: ini bukan masalah data hilang. Datanya ada, hanya saja kamus resminya memang belum punya nama untuk kedua aspek itu. Yang perlu dilakukan adalah konfirmasi ke BPOM.

### Aspek yang ada di kamus tapi tidak muncul

| Aspek | Di kamus ASPEK_KTL | Muncul di dim_pemeriksaan_aspek | Volume |
|---|---|---|---|
| Penyaluran | ya | ya | 13.547 item |
| Personalia | ya | tidak | — |
| Produksi | ya | tidak | — |

Penyaluran di kamus sama dengan Pendistribusian di formulir. Jadi ketika tim bertanya "tren aspek pendistribusian", jawabannya ada di bawah label "Penyaluran".

### Section formulir yang tidak dipetakan

Ini yang perlu ditindaklanjuti lebih dulu.

Dari sumber, ada 89 nama section `tx_*` di formulir pelayanan. Yang masuk ke `dim_pemeriksaan_aspek` hanya 47.

```sql
-- nama section di sumber (sampel 20.000 kasus pelayanan)
WITH d AS (
  SELECT (datas::jsonb #>> '{}')::jsonb j FROM trx_pemeriksaan
  WHERE deleted_at IS NULL AND datas IS NOT NULL
    AND jenis_id IN (109,107,108,105,106,748) LIMIT 20000
)
SELECT DISTINCT k FROM d, LATERAL jsonb_object_keys(j) k
WHERE k LIKE 'tx\_%' AND k NOT LIKE 'tx\_point%' ORDER BY 1;
-- 89 nama

SELECT area_key FROM dim_pemeriksaan_aspek ORDER BY 1;   -- 47 nama
```

Dari 42 nama yang tidak masuk, sebagian memang bukan aspek dan wajar dikecualikan:

```
tx_total_fp, tx_total_n, tx_file_bap, tx_file_laporan, tx_kritis, tx_major,
tx_minor, tx_kesimpulan, tx_profil, tx_status_capa, tx_dokumentasi, tx_lain_pemeriksaan
```

Tapi sisanya seharusnya jadi aspek:

```
tx_personalia                    ← "Personalia" ada di kamus resmi ASPEK_KTL
tx_distribusi                    ← "Penyaluran"
tx_pengadaan                     versi polos
tx_penyimpanan                   versi polos
tx_gudang
tx_fast_moving_antibiotika       ← "Penyerahan"
tx_penyerahan_antibiotika_tanpa_resep_kepada
tx_penyerahan_antibiotika_tanpa_resep_kepada_terbanyak
tx_penyerahan_antibiotika_tanpa_resep_kie
tx_penyerahan_antibiotika_tanpa_resep_oleh
tx_pengadaan_vaksin_1..4         ← varian vaksin
tx_penyimpanan_vaksin_1..8
tx_pemusnahan_vaksin_1..2
tx_personil_vaksin_1..3
tx_lainnya_vaksin_1..2
```

Perhatikan `tx_personalia`. Aspek Personalia **ada di kamus resmi BPOM** (kode 09) **dan** ada section-nya di formulir, tapi tidak dipetakan ke dim. Ini yang paling jelas perlu diperbaiki.

Yang penting: section-section ini benar-benar dibuang saat parsing, bukan hanya kamusnya yang kurang. Buktinya:

```sql
-- dim dan bridge konsisten: 47 area_key dipakai penuh
SELECT count(DISTINCT area_key) FROM bridge_pemeriksaan_skor_operasional;   -- 47

-- tapi section ini tidak pernah masuk sama sekali
SELECT DISTINCT area_key FROM bridge_pemeriksaan_skor_operasional
WHERE area_key IN ('tx_personalia','tx_distribusi','tx_pengadaan',
                   'tx_penyimpanan','tx_gudang');
-- kosong
```

### Definisi "temuan" berbeda per varian

Ini belum diputuskan siapa pun, dan perlu keputusan sebelum dashboard dibuat.

```
Varian pelayanan (skor)   — 63.851 kasus
   temuan = jawaban bukan "yes", atau skor di bawah 100
   satuannya skor/persen kepatuhan
   ada di bridge_pemeriksaan_skor_operasional  (punya kamus aspek)

Varian produksi (klausul) — 179.465 kasus
   temuan = jawaban "Tidak"
   satuannya jumlah klausul
   ada di bridge_pemeriksaan_checklist          (tanpa kamus aspek)
```

Kedua varian ini tidak bisa digabung dalam satu grafik, karena satuannya berbeda. Satu menyatakan persentase, satunya menyatakan cacah.

---

## Kenapa aspek hanya mencakup pelayanan

### Varian produksi memang tidak punya aspek itu

Formulir produksi memakai kosakata yang sama sekali berbeda. Ini top-level key `datas` untuk varian produksi:

```sql
WITH d AS (
  SELECT (datas::jsonb #>> '{}')::jsonb j FROM trx_pemeriksaan
  WHERE deleted_at IS NULL AND datas IS NOT NULL
    AND jenis_id IN (4,5,7,8,9,10) LIMIT 3000
)
SELECT k, count(*) FROM d, LATERAL jsonb_object_keys(j) k
GROUP BY 1 ORDER BY 2 DESC LIMIT 25;
```

Hasilnya `tx_kritis`, `tx_major`, `tx_minor`, `tx_rating`, `tx_grading`, `tx_score`, lalu puluhan `tx_pointV2`, `tx_pointD4`, `tx_pointC2` dan seterusnya.

Itu **titik checklist CPOB** (A sampai Z), bukan aspek distribusi. Ukurannya:

```sql
WITH d AS (
  SELECT (datas::jsonb #>> '{}')::jsonb j FROM trx_pemeriksaan
  WHERE deleted_at IS NULL AND datas IS NOT NULL
    AND jenis_id IN (4,5,7,8,9,10,13,15,16,17)
)
SELECT count(*) total,
       count(*) FILTER (WHERE j::text LIKE '%tx_pengadaan%')   ada_pengadaan,
       count(*) FILTER (WHERE j::text LIKE '%tx_penyimpanan%') ada_penyimpanan,
       count(*) FILTER (WHERE j::text LIKE '%tx_point%')       ada_point_cpob
FROM d;
-- 165081 | 17 | 10270 | 63785
```

Dari 165.081 kasus non-pelayanan, hanya 17 yang punya section pengadaan. Sarana produksi, kosmetik, dan pangan memang tidak diperiksa dengan aspek Pengadaan/Penerimaan/Penyerahan — mereka diperiksa dengan checklist CPOB (bangunan, sanitasi, peralatan, higiene).

**Jadi ini bukan masalah ekstraksi.** Bahkan kalau pipeline diperbaiki total, aspek distribusi untuk sarana produksi tetap tidak akan ada, karena formulirnya tidak menanyakan itu.

### Varian pelayanan: datanya ada, cuma belum diekstrak

```sql
-- sumber
SELECT count(*) FROM trx_pemeriksaan
WHERE deleted_at IS NULL AND datas IS NOT NULL
  AND jenis_id IN (109,107,108,105,106,748);
-- 72727

-- staging
SELECT count(DISTINCT pemeriksaan_id) FROM bridge_pemeriksaan_skor_operasional;
-- 63851
```

Selisih 8.876 kasus, pecahannya: 7.693 varian vaksin, 1.183 gap murni, dan 395 memang kosong.

### Jadi bagaimana menjawab Q1–Q7

Kondisi setelah perbaikan:

```
"Tren temuan pada aspek pengadaan seluruh sarana"
   │
   ├─  63.845 kasus (24,6%)  bisa dijawab — punya label aspek resmi
   │                          (clusterC_skor lewat dim_pemeriksaan_aspek)
   │
   ├─   7.697 kasus ( 3,0%)  data sudah ada di bridge_pemeriksaan_vaksin,
   │                          tapi section_key belum punya label aspek
   ├─   1.182 kasus ( 0,5%)  bentuknya narasi bebas per section,
   │                          tidak ada struktur aspek berkode
   ├─     398 kasus          clusterC_skor yang masih kosong
   │
   └─ 186.226 kasus (71,8%)  tidak bisa — formulir produksi/kosmetik/pangan
                             memakai checklist CPOB, bukan aspek distribusi
```

Perubahan dari sebelum perbaikan: 8.879 kasus (vaksin + naratif) yang tadinya nol baris sekarang **sudah punya data**. Hanya saja label aspeknya belum dibuat, jadi belum bisa dikelompokkan per aspek seperti `clusterC_skor`.

Artinya: pertanyaan "tren aspek pengadaan **seluruh** sarana" tetap tidak bisa dijawab sepenuhnya. Yang bisa langsung dijawab 63.845 kasus, khusus sarana pelayanan (Apotek, PKM, Klinik, RS, Toko Obat).

Cakupan per aspek:

```sql
SELECT COALESCE(a.aspek_ktl_nama, a.aspek_label) AS aspek,
       a.status_kamus,
       count(*) item,
       count(DISTINCT s.pemeriksaan_id) kasus
FROM bridge_pemeriksaan_skor_operasional s
JOIN dim_pemeriksaan_aspek a ON a.area_key = s.area_key
GROUP BY 1, 2 ORDER BY 3 DESC;
```

| Aspek | status kamus | item | kasus |
|---|---|---:|---:|
| Penyerahan | resmi | 503.583 | 63.851 |
| Penyimpanan | resmi | 360.882 | 63.851 |
| Pengadaan | resmi | 230.955 | 63.851 |
| Pengembalian | belum_ada_di_kamus | 146.958 | 63.851 |
| Penerimaan | belum_ada_di_kamus | 127.702 | 63.851 |
| Pemusnahan | resmi | 103.253 | 63.851 |
| Pencatatan dan Pelaporan | resmi | 28.665 | 25.808 |
| Penyaluran | resmi | 13.547 | 5.811 |
| Efek Samping (SAS) | belum_ada_di_kamus | 2.885 | 2.885 |
| Pencantuman Kode (SAS) | belum_ada_di_kamus | 2.885 | 2.885 |

Query tren lengkapnya:

```sql
SELECT COALESCE(a.aspek_ktl_nama, a.aspek_label) AS aspek,
       date_trunc('year', f.tgl_start) AS tahun,
       count(DISTINCT f.id) AS jumlah_kasus,
       count(*)             AS jumlah_item
FROM bridge_pemeriksaan_skor_operasional s
JOIN fact_pemeriksaan      f ON f.id = s.pemeriksaan_id
JOIN dim_pemeriksaan_aspek a ON a.area_key = s.area_key
WHERE f.is_data_uji IS NOT TRUE
GROUP BY 1, 2 ORDER BY 1, 2;
```

---

## Q8 — Jumlah pemeriksaan per inspektur per jenis fasilitas

**Bisa dijawab penuh.** Tidak ada kendala data.

```sql
SELECT u.fullname                        AS inspektur,
       js.name                           AS jenis_sarana,
       js.parent_name                    AS rantai,
       count(DISTINCT p.pemeriksaan_id)  AS jumlah_kasus
FROM bridge_pemeriksaan_petugas p
JOIN fact_pemeriksaan f  ON f.id = p.pemeriksaan_id
JOIN dim_user u          ON u.user_id = p.user_id
JOIN dim_master_data js  ON js.master_data_id = f.jenis_id
                        AND js.type = 'JENIS_SARANA'
WHERE f.is_data_uji IS NOT TRUE
GROUP BY 1, 2, 3 ORDER BY 4 DESC;
```

Contoh hasil:

| Inspektur | Jenis | Rantai | Kasus |
|---|---|---|---:|
| Agatha Riona Octavianus, S.Farm., Apt | Pangan | Distribusi | 505 |
| Endang Listri Mulyaningsih, STP | Kosmetik | Distribusi | 501 |
| Afrida Yusni | Pangan | Distribusi | 463 |
| Supendy | Pangan | Distribusi | 463 |
| Delima R. Hutabarat | Pangan | Distribusi | 461 |

**Catatan:** tidak perlu tabel baru untuk memisahkan Sardis dan Saryan. Kamus jenis sarana sudah menyimpan golongannya di kolom `parent_name`:

```sql
SELECT master_data_id, name, parent_id, parent_name
FROM dim_master_data WHERE type='JENIS_SARANA' ORDER BY master_data_id;
```

Jadi Pangan dan Kosmetik golongannya Distribusi (Sardis), sedangkan Pangan MD dan Kosmetik CPKB golongannya Produksi (Saryan). Tinggal pakai kolomnya.

Satu catatan: nama inspektur datang dari `dim_user`, dan ada 169 baris petugas yang user-nya tidak terdaftar. Jumlahnya kecil, tidak mengganggu hasil agregat.

---

## Q9 — Temuan, kekritisan, regional

Pertanyaan ini punya tiga bagian, dan statusnya berbeda-beda.

### a. Jenis dan jumlah temuan — bisa, tapi angkanya perlu dibersihkan

```sql
SELECT m.name                            AS kategori,
       count(DISTINCT t.pemeriksaan_id)  AS jumlah_kasus,
       sum(t.jumlah_temuan)              AS jumlah_temuan
FROM bridge_pemeriksaan_temuan t
CROSS JOIN LATERAL jsonb_array_elements_text(t.kategori_kode) k(kode)
JOIN dim_master_data m ON m.master_data_id::text = k.kode
                      AND m.type = 'KATEGORI_TEMUAN_PRODUK'
WHERE t.is_kasus_draft = false
GROUP BY 1 ORDER BY 3 DESC;
```

| Kategori | Kasus | Jumlah temuan |
|---|---:|---:|
| TIE (Tanpa Izin Edar) | 18.292 | 22.071.610 |
| Lain - Lain | 1.496 | 1.536.436 |
| ED (Expire Date/Kedaluwarsa) | 11.589 | 1.243.209 |
| Substandard/Rusak | 2.316 | 1.024.285 |
| Temuan Obat Keras | 585 | 898.225 |

**Tapi angka "jumlah temuan" itu tidak bisa dipercaya apa adanya.** Kolom `jumlah_temuan` berisi nilai yang tidak wajar:

```sql
SELECT count(*)                                                  baris,
       min(jumlah_temuan)                                        min,
       max(jumlah_temuan)                                        max,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY jumlah_temuan) median,
       count(*) FILTER (WHERE jumlah_temuan < 0)                 negatif,
       count(*) FILTER (WHERE jumlah_temuan > 100000)            sangat_besar,
       sum(jumlah_temuan)                                        total
FROM bridge_pemeriksaan_temuan;
```

```
baris        : 304.687
min          : -196
max          : 20.221.092.024
median       : 5
negatif      : 137
sangat_besar : 32
total        : 20.250.383.345
```

Satu baris bernilai 20,2 miliar. Nilai itu **99,86% dari seluruh total**. Artinya seluruh angka "22 juta temuan TIE" sebenarnya berasal dari satu baris yang salah input.

```sql
SELECT pemeriksaan_id, tp_product_id, jumlah_temuan, harga_total
FROM bridge_pemeriksaan_temuan
ORDER BY jumlah_temuan DESC NULLS LAST LIMIT 5;
-- 109595 | 1813415 | 20221092024 | 7077382208400
```

Nilai 20.221.092.024 dan harga 7 triliun jelas bukan angka yang mungkin. Jumlah temuan normal berkisar 1 sampai puluhan, dengan median 5.

**Sudah dibersihkan (21 Sep 2026).** Tim data menangani ini dengan pendekatan yang tidak agresif:

- 1 baris outlier ekstrem (20,2 miliar) di-NULL-kan
- 137 baris negatif di-NULL-kan (`jumlah_temuan` dan `harga_total` sekaligus)
- Nilai besar lain (kisaran 100 ribu sampai 7,7 juta) **sengaja dibiarkan** — semuanya konsisten secara aritmatika (`harga_total = harga × jumlah_temuan` persis) dan sebagian punya justifikasi di kolom `keterangan`

Kondisi sekarang:

```sql
SELECT count(*)                                       baris,
       min(jumlah_temuan)                             min,
       max(jumlah_temuan)                             max,
       count(*) FILTER (WHERE jumlah_temuan < 0)      negatif,
       count(*) FILTER (WHERE jumlah_temuan IS NULL)  null_jumlah
FROM bridge_pemeriksaan_temuan;
-- 303521 | 1 | 7700000 | 0 | 927
```

Angka total masih perlu hati-hati karena nilai besar yang sah tetap ikut terjumlah. Untuk cacah temuan yang wajar, pakai median atau batasi nilainya.

### b. Per regional — bisa

```sql
SELECT b.regional_name               AS regional,
       count(DISTINCT f.id)          AS kasus,
       count(t.id)                   AS baris_temuan
FROM fact_pemeriksaan f
JOIN dim_balai b ON b.balai_id = f.balai_id
LEFT JOIN bridge_pemeriksaan_temuan t ON t.pemeriksaan_id = f.id
GROUP BY 1 ORDER BY 2 DESC;
```

| Regional | Kasus | Baris temuan |
|---|---:|---:|
| Semarang | 60.504 | 54.953 |
| Medan | 40.315 | 39.097 |
| Surabaya | 36.953 | 44.546 |
| Pekanbaru | 35.999 | 54.162 |
| Makassar | 27.533 | 31.987 |
| Samarinda | 24.483 | 42.614 |

Pakai `regional_name`, jangan `regional`. Kolom `regional` berisi kode angka yang tidak konsisten:

```sql
SELECT regional, regional_name, count(*)
FROM dim_balai GROUP BY 1, 2 ORDER BY 1;
-- kode 3 dipakai untuk dua nama sekaligus:
-- 3 | Jakarta  | 2 balai
-- 3 | Semarang | 14 balai
```

### c. Kekritisan — belum bisa

```sql
-- sumber: berapa kasus punya data kekritisan
SELECT count(*) FILTER (WHERE j ? 'hp_level') AS hp_level
FROM (SELECT (result::jsonb #>> '{}')::jsonb j FROM trx_pemeriksaan
      WHERE deleted_at IS NULL AND result IS NOT NULL) r;
-- 9100

-- staging: berapa kasus yang counternya terisi
SELECT count(*) FILTER (WHERE kritis_count IS NOT NULL
                           OR major_count IS NOT NULL
                           OR minor_count IS NOT NULL) AS counter
FROM fact_pemeriksaan;
-- 609
```

Sumber punya 9.100 kasus, staging hanya 609. **93% belum tersinkron.** Ini bukan karena datanya jarang — datanya ada di sumber, hanya belum diekstrak.

Ada juga hal yang perlu diketahui soal tingkat pemenuhan CPOB:

```sql
SELECT f.kesimpulan_balai_id, k.kode, k.keterangan, count(*)
FROM fact_pemeriksaan f
LEFT JOIN dim_pemeriksaan_kesimpulan k ON k.id = f.kesimpulan_balai_id
WHERE f.jenis_id = 8
GROUP BY 1, 2, 3 ORDER BY 4 DESC;
```

```
792 Baik      345      1 MK  140      793 Cukup 118
794 Kurang    107      2 TMK  84      791 Memuaskan 76
null           43      3 TTP   2
```

Perhatikan: kolom `kesimpulan_balai_id` untuk jenis sarana produksi obat berisi **dua hal berbeda sekaligus** — vonis kasus (MK, TMK, TTP) **dan** tingkat pemenuhan CPOB (Baik, Cukup, Kurang, Memuaskan). Kalau membuat rekap "per kesimpulan" untuk jenis sarana ini tanpa memisahkan, hasilnya mencampur dua taksonomi.

---

## Pertanyaan lanjutan

### Berapa pemeriksaan selesai dan berapa macet

```sql
SELECT sc.status_code, count(*) kasus
FROM fact_pemeriksaan f
JOIN dim_status_code sc ON sc.id = f.status_id AND sc.domain = 'pemeriksaan'
GROUP BY 1 ORDER BY 2 DESC;
-- VERIFY4 167116, yaitu 64,4% macet di Operator Pusat
```

### Tindakan paling sering atas temuan

```sql
SELECT m.name, count(*)
FROM bridge_pemeriksaan_temuan t
CROSS JOIN LATERAL jsonb_array_elements_text(t.tindakan_kode) k(kode)
JOIN dim_master_data m ON m.master_data_id::text = k.kode
                      AND m.type = 'TL_PRODUK_TEMUAN'
GROUP BY 1 ORDER BY 2 DESC;
```

### Produk paling sering jadi temuan

```sql
SELECT d.nama_produk, count(*) jumlah
FROM bridge_pemeriksaan_temuan t
JOIN dim_produk d ON d.produk_id = t.tp_product_id
WHERE t.is_kasus_draft = false
GROUP BY 1 ORDER BY 2 DESC LIMIT 10;
```

### Grade sarana produksi

```sql
SELECT grade, count(*) FROM fact_pemeriksaan
WHERE grade IS NOT NULL GROUP BY 1 ORDER BY 2 DESC;
-- A 24777 | B 9819 | C 9739 | N/A 65
```

Sumber 44.401, staging 44.400. Selisih satu baris.

### Kasus yang sampai CAPA

```sql
SELECT count(*) FROM fact_pemeriksaan WHERE tl_capa IS NOT NULL;
-- 19299
```

Catatan: `tl_capa` bertipe teks bebas, bukan relasi ke kamus. Jadi tidak bisa dikelompokkan per jenis tindakan.

### Kapan surat tindak lanjut di-TTE

Tidak bisa dijawab. Status TTE tidak pernah disimpan sebagai data oleh aplikasi, hanya muncul sebagai label di daftar berkas.

### Berapa klausul tidak sesuai per aspek

Bisa dihitung jumlah totalnya, tapi tidak bisa dikelompokkan per aspek resmi:

```sql
SELECT count(*) FROM bridge_pemeriksaan_checklist WHERE nilai_aspek = 'Tidak';
```

Penyebabnya dijelaskan di temuan E1.

---

## Temuan

### E1. `checklist.path` tidak punya kamus aspek

Setiap baris checklist punya kolom `path`, jejak posisi pertanyaan di JSON, misalnya `tx_pointB1`. Kamus aspek menyimpan nama section seperti `tx_pengadaan_obat`. Keduanya tidak pernah bertemu.

```sql
SELECT count(*) dari_checklist, count(a.area_key) ketemu
FROM bridge_pemeriksaan_checklist c
LEFT JOIN dim_pemeriksaan_aspek a ON a.area_key = c.path;
-- 7388165 | 0
```

Akibatnya 7,4 juta baris checklist tidak bisa dikelompokkan per aspek. Ini yang membuat Q1–Q7 tidak bisa dijawab untuk varian produksi.

### E2. `kategori_kode` dan `tindakan_kode` kadang tertukar

```sql
-- kode di kategori_kode yang bukan milik KATEGORI_TEMUAN_PRODUK
SELECT k.kode, count(*)
FROM bridge_pemeriksaan_temuan t, LATERAL jsonb_array_elements_text(t.kategori_kode) k(kode)
WHERE k.kode IS NOT NULL AND btrim(k.kode) <> ''
  AND NOT EXISTS (SELECT 1 FROM dim_master_data m
                  WHERE m.master_data_id::text = k.kode
                    AND m.type = 'KATEGORI_TEMUAN_PRODUK')
GROUP BY 1 ORDER BY 2 DESC;
-- 410 elemen; contoh 21214, 449, 762, 669
```

Ini berasal dari sumber, bukan kesalahan ekstraksi:

```sql
SELECT pemeriksaan_id, tp_product_id, tp_kategori_id, tp_tindakan_id
FROM trx_pemeriksaan_temuan WHERE pemeriksaan_id = 265622 LIMIT 6;
-- tp_kategori_id = ["762"], tp_tindakan_id = ["762"]
-- 762 = "Dimusnahkan", itu kode tindakan, tapi tersimpan di kolom kategori
```

### E3. Ada `[null]` di dalam array

```sql
SELECT count(*) FROM bridge_pemeriksaan_temuan
WHERE kategori_kode::text LIKE '%null%';
-- 81

SELECT pemeriksaan_id, tp_kategori_id, tp_tindakan_id
FROM trx_pemeriksaan_temuan WHERE pemeriksaan_id = 1213 LIMIT 3;
-- tp_kategori_id = [null], tp_tindakan_id = [null]
```

Parser perlu menangani `null` sebagai elemen array, bukan hanya string kosong.

### E4. Dua cara join kolom status

```sql
-- di fact, join ke id
JOIN dim_status_code c ON c.id = f.status_id    AND c.domain = 'pemeriksaan'

-- di approval, join ke status_code (teks)
JOIN dim_status_code c ON c.status_code = a.status AND c.domain = 'pemeriksaan'
```

Uji keduanya:

```sql
SELECT count(*) FILTER (WHERE f.status_id IS NULL)        status_null,
       count(*) FILTER (WHERE c.id IS NULL
                          AND f.status_id IS NOT NULL)   orphan_nyata
FROM fact_pemeriksaan f
LEFT JOIN dim_status_code c ON c.id = f.status_id AND c.domain='pemeriksaan';
-- 1 | 0   (yang 1 itu status_id NULL, bukan orphan)

SELECT count(*) FILTER (WHERE c.status_code IS NULL) orphan_approval
FROM fact_pemeriksaan_approval a
LEFT JOIN dim_status_code c ON c.status_code = a.status AND c.domain='pemeriksaan';
-- 0
```

### E5. `legal_id` merujuk dua kamus

```sql
SELECT m.type, count(*) FROM dim_sarana s
JOIN dim_master_data m ON m.master_data_id = s.legal_id
WHERE s.legal_id IS NOT NULL GROUP BY 1 ORDER BY 2 DESC;
-- BENTUK_PERUSAHAAN 241769 | JENIS_SARANA 169067

SELECT count(*) FROM dim_sarana s
WHERE s.legal_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM dim_master_data m WHERE m.master_data_id = s.legal_id);
-- 29356 tanpa match
```

### E6. `tl_saran` merujuk tujuh kamus

```sql
SELECT m.type, count(*) FROM fact_pemeriksaan f,
  LATERAL jsonb_array_elements_text(f.tl_saran) k(x)
  JOIN dim_master_data m ON m.master_data_id::text = k.x
GROUP BY 1 ORDER BY 2 DESC;
```

Bandingkan dengan kolom sebelahnya:

```sql
SELECT count(*) elemen, count(m.master_data_id) match
FROM fact_pemeriksaan f, LATERAL jsonb_array_elements_text(f.tl_saran_pusat) k(x)
LEFT JOIN dim_master_data m ON m.master_data_id::text = k.x
                           AND m.type = 'SARAN_TINDAK_LANJUT';
-- 56502 | 56362   (99,8% satu kamus)
```

Jadi `tl_saran` bercampur tujuh kamus, sementara `tl_saran_pusat` di sebelahnya hampir murni satu kamus.

### E7. `jenis_pangan_kode` merujuk dua kamus

```sql
SELECT 'PRODUK_PANGAN' t, count(*) FROM fact_pemeriksaan f,
  LATERAL jsonb_array_elements_text(f.jenis_pangan_kode) k(x)
  JOIN dim_master_data m ON m.master_data_id::text=k.x AND m.type='PRODUK_PANGAN'
UNION ALL
SELECT 'JENIS_PANGAN_68', count(*) FROM fact_pemeriksaan f,
  LATERAL jsonb_array_elements_text(f.jenis_pangan_kode) k(x)
  JOIN dim_master_data m ON m.master_data_id::text=k.x AND m.type='JENIS_PANGAN_68'
UNION ALL
SELECT 'JENIS_PANGAN', count(*) FROM fact_pemeriksaan f,
  LATERAL jsonb_array_elements_text(f.jenis_pangan_kode) k(x)
  JOIN dim_master_data m ON m.master_data_id::text=k.x AND m.type='JENIS_PANGAN';
-- 46521 | 20915 | 0
```

Nilai yang muncul misalnya 211629 (Dry Food), 211630 (Chill), 211631 (Frozen) dari `PRODUK_PANGAN`, dan 211538, 211427 dari `JENIS_PANGAN_68`. Kalau hanya pakai `PRODUK_PANGAN`, 31% baris hilang.

### E8. `regional` tidak konsisten

```sql
SELECT regional, regional_name, count(*)
FROM dim_balai GROUP BY 1, 2 ORDER BY 1;
```

### E9. `balai_id = 0` di dim_user adalah penanda

```sql
SELECT count(*) FROM dim_user WHERE balai_id = 0;
-- 4570

SELECT count(*) FILTER (WHERE u.user_id IS NULL) orphan
FROM dim_user d LEFT JOIN dim_balai u ON u.balai_id = d.balai_id
WHERE d.balai_id IS NOT NULL;
-- 4575, hampir semuanya nilai 0
```

Nilai 0 menandai user yang tidak terikat balai (misalnya user pusat), bukan join yang rusak.

### E10. `checklist.conformity` belum dibersihkan dari HTML

```sql
SELECT left(conformity, 120) FROM bridge_pemeriksaan_checklist
WHERE conformity IS NOT NULL LIMIT 3;
-- <p class="MsoNoSpacing" style="margin-left: 68.2pt; ...">Belum memiliki kebijakan mutu
```

Kolom `conformity` justru satu-satunya tempat tingkat keparahan per klausul tercatat, jadi sayang kalau isinya masih bercampur tag HTML.

### E11. `jumlah_temuan` punya outlier

Dijelaskan di Q9a. Satu baris berisi 20,2 miliar, dan 137 baris bernilai negatif.

### E12. 91.697 baris temuan punya pasangan kasus-produk duplikat

```sql
SELECT count(*) baris,
       count(DISTINCT (pemeriksaan_id, tp_product_id)) pasangan_unik,
       count(*) - count(DISTINCT (pemeriksaan_id, tp_product_id)) duplikat
FROM bridge_pemeriksaan_temuan;
-- 304687 | 212990 | 91697
```

Perlu keputusan: apakah temuan produk yang sama di kasus yang sama memang bisa muncul lebih dari sekali (temuan berulang), atau ini duplikasi yang perlu dihilangkan.

### E13. Kekritisan 93% belum tersinkron

Dijelaskan di Q9c. Sumber 9.100, staging 609.

### E14. Varian vaksin tidak dipetakan

Dijelaskan di bagian gap aspek pelayanan. 7.697 kasus, semuanya nol baris.

### E15. Section aspek tidak dipetakan

Dijelaskan di bagian kamus dan aspek. 42 nama di luar kamus, termasuk `tx_personalia` yang seharusnya ada.

### E16. Entri kamus hilang

```sql
SELECT count(*) FROM ms_master_data;    -- 1999
SELECT count(*) FROM dim_master_data;   -- 1994
```

### E17. Sarana belum tersinkron

```sql
SELECT count(*) FROM trx_sarana;    -- 441821
SELECT count(*) FROM dim_sarana;    -- 440192
```

### E18. Tingkat pemenuhan CPOB belum tersinkron

Sumber 876, staging 646. Selisih 230.

---

## Ringkasan perbaikan

Urutan pengerjaan sudah ada di bagian **"Data yang belum sinkron"** di awal dokumen (P1 sampai P8). Untuk referensi cepat, perbaikan mana membantu pertanyaan yang mana:

| Perbaikan | Pertanyaan yang terbantu |
|---|---|
| P1, P4 | Q1–Q7 tren temuan per aspek |
| P2 | Q9c tingkat kekritisan |
| P3 | pengelompokan checklist per aspek resmi |
| P5, P6 | kelengkapan nama dan alamat sarana |
| P7 | Q9 tingkat pemenuhan CPOB |
| P8 | perlu keputusan dulu sebelum dikerjakan |

## Yang tidak bisa diperbaiki

| Apa | Alasan |
|---|---|
| Aspek distribusi untuk sekitar 186.226 kasus produksi/kosmetik/pangan | Formulir SIPT memakai checklist CPOB, bukan aspek distribusi |
| Penerimaan dan Pengembalian di kamus resmi | Tidak ada di `ASPEK_KTL` BPOM (10 entri) |
| Status TTE | Tidak pernah direkam aplikasi |
| Kekritisan per klausul | Tidak pernah dicatat aplikasi |

## Di luar pembahasan

| Apa | Alasan |
|---|---|
| `JENIS_PANGAN` ID 211236 hilang | `JENIS_PANGAN` tidak dirujuk pemeriksaan |
| `TUJUAN_SAMPLING` ID 223492 hilang | Milik domain pengujian |
| `fact_pengawasan*`, `bridge_pengawasan_*`, `dim_pengawasan_*` | Milik domain pengawasan |

---

## Aturan praktis menulis query

Bagian ini merangkum hal-hal yang paling sering bikin salah.

**1. Tentukan dulu tingkat hitungannya.** Pertanyaan "berapa pemeriksaan" dan "berapa penugasan petugas" menghasilkan angka berbeda dari data yang sama.

```sql
SELECT (SELECT count(*) FROM fact_pemeriksaan) kasus,
       (SELECT count(*) FROM bridge_pemeriksaan_petugas) penugasan;
-- 259348 | 553380
```

Selisihnya sekitar dua kali karena satu kasus dikerjakan sekitar dua petugas.

**2. Cek flag sebelum menyentuh checklist.** Salah tabel berarti hasil kosong tanpa error.

```sql
SELECT flag_varian_datas FROM fact_pemeriksaan WHERE id = :id;
```

**3. Selalu sebutkan type di join dim_master_data**, kecuali untuk tiga kolom multi-kamus (E5, E6, E7).

**4. Cast ke teks** untuk `observasi_kode`, `komoditi_kode`, `fokus_kode`, dan semua kolom array.

**5. Filter data uji dan draft** kalau ingin angka final.

```sql
SELECT count(*) FILTER (WHERE is_data_uji IS TRUE) uji,
       count(*) FILTER (WHERE is_data_uji IS NULL) flag_kosong
FROM fact_pemeriksaan;
-- 72 | 29

SELECT count(*) FROM bridge_pemeriksaan_temuan WHERE is_kasus_draft = true;
-- 6474, yaitu 2,12%
```

**6. Pakai COALESCE untuk label aspek**, karena Penerimaan dan Pengembalian ada di `aspek_label`.

**7. Jangan pakai sum(jumlah_temuan) mentah.** Ada outlier 20 miliar.

**8. Pakai regional_name, jangan regional.** Kode regional tidak konsisten.

**9. Batasi jumlah baris checklist** kalau menampilkan per kasus, karena bisa ratusan baris.

```sql
SELECT pemeriksaan_id, count(*) FROM bridge_pemeriksaan_checklist
GROUP BY 1 ORDER BY 2 DESC LIMIT 5;
```

---

## Checklist konfirmasi untuk tim DE

| # | Klaim | Yang perlu dikonfirmasi |
|---|---|---|
| C1 | `jenis_pangan_kode` merujuk 2 kamus (PRODUK_PANGAN + JENIS_PANGAN_68) | Apakah memang desainnya begitu? |
| C2 | `tl_saran` merujuk 7 kamus | Apakah memang begitu? Kalau ya, perlu didokumentasikan |
| C3 | `dim_sarana.legal_id` merujuk 2 kamus | Apakah memang begitu? |
| C4 | 5 entri kamus hilang, 3 di antaranya dipakai pemeriksaan | Apa penyebabnya dan kapan diperbaiki? |
| C5 | 1.629 sarana tidak tersinkron | Filter apa yang membuangnya? |
| C6 | 7.693 kasus varian vaksin tidak punya baris skor | Apakah varian vaksin memang belum ditangani pipeline? |
| C7 | 42 nama section di luar kamus aspek, termasuk `tx_personalia` | Apakah sengaja dikecualikan atau terlewat? |
| C8 | `hp_level` dari 9.100 menjadi 609 | Apakah field ini memang tidak diekstrak? |
| C9 | `hp_pemenuhan` dari 876 menjadi 646 | Filter apa yang membuangnya? |
| C10 | `checklist.path` tidak punya kamus aspek | Apakah mapping-nya memang belum dibuat? |
| C11 | `klasifikasi_produk_kode` hanya 28 baris terisi | Apakah memang hampir kosong di sumber? |
| C12 | `jumlah_temuan` ada nilai 20,2 miliar dan 137 negatif | Perlu aturan validasi? |
| C13 | 91.697 baris temuan punya pasangan (kasus, produk) duplikat | Duplikat sah atau perlu dedup? |
| C14 | `checklist.conformity` belum dibersihkan dari HTML | Perlu dibersihkan? |
| C15 | `dim_balai.regional` kode 3 untuk dua nama berbeda | Mana yang benar? |

---

*Verifikasi 21 September 2026; crosscheck ke `sipt_sync` 22 September 2026. Cakupan hanya domain Pemeriksaan. Dokumen lama `pemetaan-entry-per-flow-ke-staging.md` sudah dihapus 22 Sep 2026 (rencana pra-ekstraksi, tidak lagi relevan, dan memuat kredensial internal).*
