# Audit eksekusi testcase — domain PEMERIKSAAN SARANA · varian `after-insight-v2`

**Tanggal eksekusi:** 18 Agustus 2026 · **Tanggal audit:** 18 Agustus 2026
**Cakupan:** 59 run · 58 skenario unik dari 256 berkas testcase · 1 varian (`after-insight-v2`)
**Model:** `dens-plus` · **Harness:** `scripts/test_variant_compare.py` mode `variant-compare` (`v3`)
**Sumber:** `seeknal/tests/outputs/2026-08-18/v1-insight/`
**Verifikasi ulang:** angka di dokumen ini dijalankan ulang ke database `pemeriksaan` via tunnel `localhost:5533`, 18 Agustus 2026

| Berkas | Isi |
|---|---|
| `00-RINGKASAN.md` | dokumen ini |
| `01-kondisi-instrumen.md` | kondisi harness dan varian |
| `02-rincian-kegagalan.md` | tabel 15 kegagalan, dibangkitkan dari berkas hasil |
| `03-verifikasi-database.md` | pembuktian ke database |
| `04-kondisi-database.md` | profil lengkap database: 9 tabel, indeks, grain, tiap kolom, sebaran nilai |
| `05-anatomi-per-kasus.md` | **15 kasus dibedah satu per satu** — SQL GT dijalankan ulang, SQL agent, jawaban, sebab gagal |

---

## 1. Hasil

| | Nilai |
|---|---:|
| Run | 59 |
| PASS | 44 (74,6 %) |
| FAIL | 15 |
| Skenario unik dijalankan | 58 dari 256 testcase (**22,7 %**) |
| Run melewati klarifikasi `[AUTO]` | 4 (6,8 %) |
| Median durasi · tool call · SQL | 57,5 s · 8 · 2 |

Cakupan 22,7 % adalah angka terendah kedua setelah pengujian. Pass-rate 74,6 % berlaku untuk
subset itu saja, bukan untuk 256 testcase.

## 2. Domain ini secara struktural lebih mudah daripada pengawasan

```sql
SELECT count(*), count(DISTINCT id) FROM mv_pemeriksaan;  -- 257607 | 257607
```

`id` unik penuh, sehingga pilihan `COUNT(*)` versus `COUNT(DISTINCT id)` **tidak dapat**
menghasilkan angka berbeda. Seluruh kelas kegagalan terbesar di domain pengawasan tidak mungkin
terjadi di sini — dan `context/00-menghitung.md` §1 memang menyatakannya terang-terangan.

## 2b. Kondisi data yang perlu diketahui sebelum menilai jawaban

Diukur 18 Agustus 2026 (rincian penuh di `04-kondisi-database.md`):

| Temuan | Angka |
|---|---|
| `tanggal_mulai` paling awal | **0004-02-21** — tahun 4 Masehi |
| Tanggal rusak lain | tahun `0020`, `1922`–`1928`, empat baris `1970-01-01` |
| Baris `tanggal_mulai` kosong | 947 |
| `nama_sarana` dengan spasi menempel di ujung | **18.827** baris |
| `nama_upt` dengan spasi menempel di ujung | 1.428 baris |
| `klasifikasi_distribusi` kosong | 197.652 baris (**76,7 %**) |
| `klasifikasi_sarana` kosong | 196.197 baris (76,2 %) |
| `grade` kosong | 213.459 baris (82,9 %) |
| `tingkat_pemenuhan_cpob` kosong | 256.746 baris (**99,7 %**) |
| `tujuan_pemeriksaan` kosong | 947 baris |
| Indeks di database | **tidak ada satu pun** |

Empat hal ini menjelaskan sebagian besar bentuk kegagalan: tren tahunan bisa memunculkan bucket
palsu, filter kesamaan persis pada nama sarana gagal senyap, dan peringkat pada kolom yang 76–99 %
kosong sangat sensitif terhadap perlakuan baris kosong — yang tidak dinyatakan oleh testcase.

## 3. Akar 1 — empat kolom bernama mirip, satu yang benar

`mv_pemeriksaan` memuat `sarana`, `jenis_sarana`, `klasifikasi_sarana`, dan `nama_sarana`.

`TC-PMR-RANK-SARANA-01` ("sarana apa yang paling banyak pada pemeriksaan?") — agent meminta
klarifikasi, harness memilih otomatis opsi **"Jenis sarana"**, lalu agent memakai `jenis_sarana`
dan menjawab **PANGAN 61.576**. GT memakai kolom `sarana`:

```sql
SELECT sarana, count(*) FROM mv_pemeriksaan
 WHERE sarana IS NOT NULL AND btrim(sarana)<>'' GROUP BY 1 ORDER BY 2 DESC LIMIT 3;
-- DISTRIBUSI 141559 | PELAYANAN 72680 | PRODUKSI 43367
```

Jadi kegagalan lahir dari **pilihan otomatis harness**, bukan dari kekeliruan analitik agent.
Pertanyaannya memang ambigu; agent mengenali ambiguitas itu dengan benar.

## 4. Akar 2 — GT yang cacat

`TC-PMR-TREN-HASIL-PEMERIKSAAN-02` menuntut jawaban memuat kata **"tidak ada"** / **"tidak
ditemukan"**, padahal `note`-nya sendiri memuat SQL yang mengembalikan **8.062 baris**:

```sql
SELECT count(*) FROM mv_pemeriksaan
 WHERE lower(sarana)='produksi'
   AND tanggal_mulai>='2024-01-01' AND tanggal_mulai<'2025-01-01';   -- 8062
```

Agent menjawab 471 pemeriksaan sarana produksi **kosmetik** MK+TMK 2024 — diverifikasi ke database
dan **benar** untuk pertanyaan yang diajukan. Assert-nya yang tidak sinkron dengan `note`-nya
sendiri. Pola assert `'tidak ada'` yang sama muncul juga di domain pengujian; ini cacat generator
testcase, bukan cacat context.

## 5. Akar 3 — nama entitas diringkas (4 kegagalan)

`TC-PMR-TREN-HASIL-PEMERIKSAAN-06/07`, `TC-PMR-VONIS-MK-TMK-04`, `TC-PMR-SARANA-DISTRIBUSI-11`
gagal **hanya** pada `assert_contains` sementara asersi angkanya lolos. Yang hilang: label periode
(`2024-05`, `2025-06`) dan nama balai lengkap (`BALAI BESAR POM DI BANDUNG`,
`BALAI BESAR POM DI JAKARTA`). Datanya benar, penyajiannya yang tidak sesuai kontrak.

## 6. Akar 4 — entity "sarana" versus "pemeriksaan"

`TC-PMR-VONIS-MK-TMK-01` menanyakan **"jumlah sarana yang tidak memenuhi ketentuan"**. Agent
menghitung sarana unik; GT menghitung pemeriksaan:

```sql
-- filter: nama_upt ILIKE '%surabaya%', kesimpulan='TMK', tanggal_mulai 2025
count(*)                    = 455   -- GT
count(DISTINCT nama_sarana) = 443   -- jawaban agent
```

Selisih 2,6 % — di bawah toleransi 5 %, dan memang skenario ini FAIL di satu run lalu PASS di run
ulang. Bukan kegagalan stabil, melainkan **kasus batas** yang hasilnya ditentukan variasi
penulisan angka di jawaban.

## 7. Akar 5 — GT menuntut "baris pertama dari daftar saya" (11 dari 15 kegagalan)

Ini sebab tunggal terbesar di repo ini. Token yang dituntut ternyata **baris pertama keluaran SQL
GT**, sementara agent menjawab dalam bentuk ringkasan/agregat:

| Skenario | Token dituntut | SQL GT menghasilkan | Yang dijawab agent |
|---|---|---|---|
| `TC-PMR-RIWAYAT-SARANA-11` | `ABAD DUA SATU MAKMUR` | daftar 1.247 sarana importir | ringkasan 1.247 sarana / 1.877 pemeriksaan |
| `TC-PMR-TEMUAN-PRODUK-03` | `BUSANA INDAH` | daftar temuan impor per sarana | peringkat negara (China 51 %) |
| `TC-PMR-SARANA-TUTUP-06` | `KOTA JAKARTA UTARA` | 3 baris sarana TTP | 15 sarana unik, tanpa menyebut kabupaten |
| `TC-PMR-VONIS-MK-TMK-05` | `ED (Expire Date / Kedaluwarsa)` | nilai per `tp_kategori` apa adanya | kategori dinormalkan jadi `ED (Kedaluwarsa)` |
| `TC-PMR-VONIS-MK-TMK-04` | `BALAI BESAR POM DI BANDUNG` | peringkat UPT (3.324 hari ini) | peringkat benar, nama diringkas |

Perhatikan `VONIS-MK-TMK-05`: agent **menormalkan** label kategori (`ED (Kedaluwarsa)`), sedangkan
GT menuntut label mentah `ED (Expire Date / Kedaluwarsa)`. Normalisasi yang secara analitik rapi
justru menjatuhkan skenario.

## 8. Akar 6 — assert dengan spasi ujung dan nilai sentinel

Empat testcase pemeriksaan memuat `assert_contains` yang **mengandung spasi di ujung**, karena
nilainya disalin apa adanya dari database:

`'APOTEK EKA FARMA  '` · `'INDAH FARMA  '` · `'MITRA EKA SUKSES '` · `'    '`

Matcher harness (`_contains_expected`) memakai pencocokan substring **verbatim**, jadi jawaban
harus memuat nama itu **beserta dua spasi di belakangnya** — praktis mustahil bila nama ditulis
dalam tabel atau kalimat. Ini terukur di data: `nama_sarana` memiliki **18.827 baris berspasi
ujung** dan `nama_upt` **1.428 baris** (lihat `04-kondisi-database.md` §4).

Lima testcase lain menuntut nilai sentinel (`NULL`, `N/A`) sebagai jawaban, sementara context
mengajarkan membuangnya.

## 9. Kesimpulan

1. Dari 15 kegagalan, **hanya sebagian kecil yang merupakan kekeliruan analitik**. Empat murni
   penyajian nama/label, satu berasal dari GT yang bertentangan dengan `note`-nya sendiri, satu
   dari pilihan klarifikasi otomatis, satu kasus batas toleransi.
2. Domain ini tidak memiliki jebakan grain: `id` unik penuh. Sisa risikonya ada pada **kolom
   bernama mirip** (`sarana` / `jenis_sarana` / `klasifikasi_sarana`) — dan itu masalah pemetaan
   istilah, bukan masalah cara menghitung.
3. Cakupan 22,7 % terlalu sempit untuk menyimpulkan mutu domain. Menjalankan sisa 198 testcase
   lebih bernilai daripada menyetel ulang context berdasarkan 58 skenario.

### Neraca sebab kegagalan (15 kasus, satu kasus bisa punya lebih dari satu sebab)

| Sebab | Kasus |
|---|---:|
| GT menuntut baris pertama daftar / label mentah | 11 |
| Nama entitas diringkas walau angka benar | 4 |
| Kolom bernama mirip (`sarana` vs `jenis_sarana`) | 1 |
| Assert bertentangan dengan `note`-nya sendiri | 1 |
| Tidak menjalankan SQL sama sekali | 1 |
| Melewati klarifikasi otomatis `[AUTO]` | 1 |
