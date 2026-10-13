# Pemetaan Form Entri → Kolom Database, Kondisinya, dan Contoh Data Konkret

> **Tujuan**: setiap field yang diketik/dipilih user di form Pemeriksaan Sarana dipetakan ke **nama tabel & kolom** di `sipt_sync`, lengkap dengan **kondisi isian nyata** (persentase terisi, variasi format, jebakan) dan **contoh nilai dari database** (bukan karangan).
>
> Semua angka hasil query langsung ke `sipt_sync` (10.59.2.29:5432) per **16 September 2026**. Kasus contoh utama: **`trx_pemeriksaan` id 291155** (kasus nyata ber-status DRAFT dengan 9 temuan produk) — bisa direproduksi dengan SQL di akhir dokumen.
>
> Legenda: ✅ sehat · ⚠️ bermasalah/sebagian · ❌ tidak pernah terisi.

---

## 1. Header kasus — `trx_pemeriksaan` (290.203 baris; **259.348 aktif** `deleted_at IS NULL`)

| Kolom | Diisi dari | Kondisi | Contoh nilai nyata |
|---|---|---|---|
| `id` | sistem | ✅ PK | `291155` |
| `status` | workflow | ✅ 12 nilai — **VERIFY4 167.116 (64%)** · VERIFY5 46.619 · FINISHED 29.042 · DRAFT_REVISE 5.108 · VERIFY7 4.784 · DRAFT 3.297 · VERIFY6 1.008 · VERIFY1 640 · VERIFY2 619 · DRAFT_PUSAT 464 · VERIFY_P1 351 · FINISHED_PUSAT 113 | `DRAFT` (kasus 291155) |
| `jenis_id` | Jenis Sarana* | ✅ **100% terisi** — top: Pangan 61.831 · Kosmetik 36.999 · **Apotek 27.696** · Pangan MD 26.521 · PKM 19.860 · OT 17.260 · Pangan IRT 10.313 · Klinik 10.258 · Intensifikasi 9.061 · Suplemen 7.184 · Toko Obat 6.943 · PBF 6.934 → inilah dimensi **Sardis/Saryan** (golongan Produksi/Distribusi/Pelayanan via `parent_id` master) | `15` (kasus 291155) |
| `klasifikasi_id` | Jenis Komoditi* | ✅ ~100% — Pangan 107.780 · Obat 83.444 · Kosmetik 39.609 · OT 20.282 · Suplemen 7.220 · Narkotika 273 · dst. | `464` |
| `tujuan_id` | Tujuan Pemeriksaan | ✅ — kamus `TUJUAN_PEMERIKSAAN` (Rutin/Kasus) | `723` |
| `sarana_id` | Nama Sarana* (search master) | ✅ **100% terisi** | `3358722` |
| `tgl_start`, `tgl_end` | Tanggal Pemeriksaan (range) | ✅ — ⚠️ ada **±15 baris tanggal kotor 1922–2028**, validasi saat ekstraksi | `2026-08-20` |
| `form_version_id` | Versi Formulir | ⚠️ **terisi hanya 76.273/259.348 (29%)** — 71% kosong. Terpakai: v9 30.342 · v10 13.407 · v4 12.043 · v3 6.788 · v5 5.152 · v6 2.796 · v1 2.261 · v2 1.917 · v8 1.424 | (kosong di 291155) |
| `metode_inspeksi` | Metode Inspeksi | ⚠️ terisi **4.101 (1,6%)** — On-site inspection 4.009 · Remote 54 · Hybrid 38 | `220364` |
| `entri_balai_id` | Unit/Balai (pilihan pertama form) | ✅ **100% terisi**, join ke `ms_balai.regional_name` terverifikasi: Semarang 60.504 · Medan 40.315 · Surabaya 36.953 · Pekanbaru 35.999 · Makassar 27.533 · Samarinda 24.483 · Manado 17.264 · Jayapura 15.240 · (tanpa regional) 1.057 → **dasar breakdown per regional Q9** | `29` (BB POM Bandung) |
| `datas` | wizard pemeriksaan+inspeksi | ✅ terisi **247.244 (95,3%)** — ⚠️ **JSON dobel-encode + format bervariasi** (§4) | 2.119 char (kasus 291155); bisa >400 ribu char |
| `result` | hasil inspeksi/kesimpulan/TL | ✅ terisi **257.393 (99,2%)** — struktur lebih stabil dari `datas` (§5) | 1.042 char (kasus 291155) |
| `jenis_pangan` | (khusus komoditi pangan) | ⚠️ 48.729 terisi (18,8% kasus) | — |
| `kasus_id` | referensi kasus luar | ⚠️ hanya 1.946 | — |
| `attachment`, `penelusuran_file` | upload di entri | ❌ **0 semua** — file nyatanya hidup di `result.tl_attachment` (165.066) & `datas.*.file` |
| `unit_id`, `gudang_id`, `sediaan_id`, `status_bb/sp/ss`, `penelusuran_id`, `information` | variasi lama | marginal — cek dulu sebelum dipakai |

## 2. Surat tugas — `trx_pemeriksaan_detail` (307.482 baris; 1:1 dengan kasus)

| Kolom | Diisi dari | Kondisi | Contoh nyata (kasus 291155) |
|---|---|---|---|
| `nomorsurat` | Nomor Surat Tugas* | ✅ **100%** | `PW.02.02.31B.08.26.1402` |
| `tgl_surat` | Tanggal Surat Tugas* | ✅ **100%** | `2026-08-14` |
| `balai_id` | Unit/Balai multi | ✅ 100% — **array JSON string** `["29"]` (bisa >1) | `["29"]` |
| `petugas_id` | Petugas* (chip multi) | ✅ **100%** — array JSON string `["2018","7732","493"]` → **dasar Q8**. Sebaran jumlah petugas per kasus: 2 orang **236.777** · 3 orang 31.091 · 1 orang 26.124 · 4 orang 11.389 · 5 orang 1.578. Inspektur terbanyak: user_id `1925` (1.113 kasus), `2469` (1.096), `2069` (1.031) | 3 petugas |

> ⚠️ **Jebakan join**: `balai_id`/`petugas_id` adalah **string JSON array**, bukan angka. Join ke master wajib parse array dulu (`petugas_id::jsonb->>0`, `jsonb_array_elements_text`).

## 3. Temuan produk — `trx_pemeriksaan_temuan` (308.295 baris; 33.501 kasus/12,9% punya temuan)

Satu baris = satu produk bermasalah dalam satu kasus.

| Kolom | Diisi dari | Kondisi | Contoh nyata |
|---|---|---|---|
| `tp_product_id` | pilih produk | ✅ **308.295 (100%)** → `ms_product.product_name` | kasus 291155: **Montalin**, **Wantong kapsul**, **Wantong serbuk**, **Yaostein BS (TR 061738555)**, **Jamu Asli Madura Keputihan**, **Urat Madu Gold**, dst. (9 baris) |
| `tp_kategori_id` | Kategori Temuan (dropdown) | ✅ kosong hanya **36** — ⚠️ **format array JSON string**: `["506"]`, bisa multi `["499","506"]`. Kamus `KATEGORI_TEMUAN_PRODUK` (28 kode): TIE `["506"]` **160.213** · ED/Kedaluwarsa `["840"]` 60.264 · Obat Keras `["211214"]` 22.263 · BKO `["499"]` 10.473 · Rusak 10.472 · Substandard/Rusak 9.328 · Illegal/TIE 6.364 · dst. — **dasar jenis temuan terbanyak Q9** | (kosong pada kasus DRAFT — lihat §3.1) |
| `tp_tindakan_id` | Tindakan (dropdown) | ✅ kosong hanya **116** — array juga. Kamus 15 kode: **Pemusnahan 186.818** · Dikembalikan ke produsen 33.776 · Pengamanan 29.970 · Dimusnahkan 17.421 · Diamankan 12.171 · Pendataan 9.377 · Penarikan 4.553 | — |
| `tp_jml_temuan` | jumlah | ✅ 307.497 (99,7%) | Montalin `34`, Wantong kapsul `31`, Urat Madu Gold `43` |
| `tp_harga`, `tp_harga_total` | nilai barang | ✅ 307.286 (99,7%) | — |
| `tp_negara` | asal | ✅ 301.771 (98%) | — |
| `tp_keterangan` | **free text** | ⚠️ 143.345 (46%) — contoh: *"Dimusnahkan ditempat oleh pelaku usaha dengan disaksikan petugas BBPOM di Surabaya"*; *"Pabrik PJ sumber makmur; TR05367796 Produk PW"* | kosong di 291155 |
| `tp_expire` | ED produk | ⚠️ 117.550 (38%) | — |
| `tp_bets`, `tp_asset`, `tp_unit_id`, `komoditi_id`, `jenis_pangan` | kontekstual | marginal | — |
| `tahap_pelaporan`, `jenis_tie` | (varian form tertentu) | ❌ **0 semua** — jangan dipakai |
| `tp_pelanggaran` | teks pelanggaran | ❌ praktis mati (**16** terisi) |
| `tp_klasifikasi_id` | klasifikasi lama | ❌ praktis mati (**34**) — pengklasifikasi sebenarnya `tp_kategori_id` |

### 3.1 Temuan penting (baru, 16 Sep 2026): DRAFT boleh punya temuan "setengah jadi"

Kasus **291155** ber-status `DRAFT` dengan **9 temuan produk lengkap** (nama produk + jumlah terisi) tetapi `tp_kategori_id`/`tp_tindakan_id` **masih kosong** — keduanya baru terisi ketika operator menekan **Proses** di wizard Daftar Temuan. Implikasi: query agregasi kategori/tindakan otomatis aman (kosongnya sedikit), tapi **jumlah baris temuan ≠ jumlah temuan final** kalau draft ikut dihitung — filter status dulu untuk angka resmi.

## 4. Isi wizard inspeksi — kolom JSON `datas` (TIGA format nyata, wajib routable)

Format **dobel-encode**: `datas` adalah string-JSON-di-dalam-string. Parser wajib unescape 2×:
`(datas::jsonb #>> '{}')::jsonb`. Tanpa itu semua query key gagal diam-diam.

Sebaran gaya (dari 247.244 datas terisi): gaya `tx_*` **247.244 (semua)** · mengandung item `aspect` 77.862 · **paste HTML Word (`MsoNormal`) 6.731** · literal `cpob` 7.

### Format 1 — Sarana Pelayanan: section `tx_<aspek>_*` + checklist `"on"` + skor

Terkonfirmasi dari datas Apotek (27.528 aktif; **27.387 atau 99,5% terstruktur rapi**, 141 HTML):

```json
"tx_penyimpanan_obat": { "wadah": "on", "bentuk": "on", "sentuh": "on",
  "sistem": "on", "jaminan": "on", "kondisi": "on", "kontaminasi": "on",
  "n": "262.50", "fp": "3", "score": "262.5" }
```
Section yang pernah teramati (satu kasus bisa memuat puluhan): `tx_pengadaan_obat/_drugs/_apj/_arsip`, `tx_penerimaan_obat/_param`, `tx_penyimpanan_obat/_drugs/_ccp/_psiko/_rusak/_investigasi/_opname_*`, `tx_penyerahan_*` (±14 varian, termasuk antibiotik), `tx_pengembalian_mutasi/_retur/_sipnap`, `tx_pencatatan_mutasi_antibiotika`, `tx_pemusnahan_obat/_drugs`, `tx_total_fp`, `tx_total_n`. Nama section = **nama aspek** → inilah bahan Q1–Q7.

### Format 2 — Sarana Produksi: item klausul `a1..aN` + `{"aspect": "Ya/Tidak", "note": ...}`

77.862 datas memuat pola `aspect`. Section mengikuti aspek form per jenis (cluster: `administrasi`+`penyimpanan`, `gudang`+`sanitasi`+`perlengkapan`+`bangunan`+`infestasi`+`pimpinan`+…, item langsung `a1..j1`, `l1..l4`). Volume observasi per aspek: **penyimpanan 187.457 · pengadaan 88.594 · penerimaan 88.335 · pemusnahan 82.842 · pengembalian 69.846 · penyerahan 68.865 · pencatatan 65.991**.

### Format 3 — Paste dokumen Word mentah (free text ekstrem)

**6.731 datas** berisi HTML MS Word (`<p class="MsoNormal">…`) — contoh nyata: satu section `tx_pengadaan` sepanjang **264.736 karakter** (petugas paste dokumen berisi XML `o:DocumentProperties`, gambar base64, dll). Kasus ini tetap sah, hanya tidak bisa diparse sebagai checklist → parser harus punya fallback "simpan sebagai teks naratif".

## 5. Hasil inspeksi & tindak lanjut — kolom JSON `result` (struktur stabil)

| Key | Isi (form mana) | Terisi |
|---|---|---:|
| `hp_kesimpulan` | Hasil Kesimpulan (Langkah 3 Hasil Inspeksi / verifikasi Supervisor) | **262.182 (89%)** — contoh nyata: `TMK` |
| `hp_catatan` | Catatan Hasil Pemeriksaan (balai) | 246.734 — contoh: *"Tidak ditemukan pada pajangan kosmetik Tanpa Izin Edar (TIE), rusak dan Kedaluarsa"* |
| `hp_catatan_pusat` | versi pusat (Justifikasi Pusat) | 68.774 — contoh: *"Pengadaan obat tradisional dari distributor dan PBF; Faktur pengadaan telah diarsipkan…"* |
| `hp_grade` | Grade sarana A/B/C (produksi; C = hanya TMK) | A 24.777 · B 9.819 · C 9.739 |
| `hp_hasil` | BAIK/CUKUP/KURANG | ±16 rb |
| `hp_level` | **Kekritisan per kasus** `{major, minor, critical, conclusion}` (counter Langkah 3 Daftar Temuan varian produksi) | ±9 rb+ (subset form) — ⚠️ di sinilah "temuan major/minor" tercatat, bukan di `trx_pemeriksaan_temuan` |
| `tl_detil` | Detil Tindak Lanjut | 196.361 — contoh: `Pembinaan`, `Pembinaan Teknis` |
| `tl_saran` | Saran TL | 171.549 |
| `tl_attachment` | file (ID server) | 165.066 |
| `tl_ba` / `tl_ba_pusat` | Berita Acara | 163.244 / 68.774 |
| `tl_capa` | **CAPA** (Corrective And Preventive Action) | 62.097 |
| `tl_sarana` | tautan TL-sarana | 57.618 |
| `tl_attachment_pusat`, `tl_detil_pusat` | versi pusat | 66.074 / 68.774 |

## 6. Log verifikasi — `trx_pemeriksaan_approval` (1.352.827 event)

Setiap aksi user (entri, kirim, verifikasi, revisi) = 1 baris: `pemeriksaan_id`, `act_steps`, `to_steps`, `status`, `notes`, `notes_tl`, `created_by`, `created_at`.

Distribusi `to_steps` (arah disposisi): `step_verify2` 333.448 · `step_verify1` 288.774 · `step_verify3` 259.070 · `step_verify4` 255.730 · `step_verify5` 82.927 · `draft_revise` 39.529 · `step_verify7` 34.818 · `finished` 29.598 · `step_verify6` 26.614 · varian pusat kecil (`step_verify_p1` 1.420 · p2 571 · p3 142 · `finished_pusat` 113 · `draft_pusat_revise` 44).

Contoh nyata (kasus 291155): `DRAFT → step_verify1`, notes = *"Entri Draft Pemeriksaan Sarana Obat Trad…"* (2026-09-14).

⚠️ **Belum ada pemetaan resmi** `VERIFY1..7` → role manual (Operator→Supervisor Balai→Kepala Balai/Loka→Operator Pusat→Supervisor Pusat→Direktur = 6 tingkat; pola `to_steps`+`created_by` bisa dipakai untuk konfirmasi). **TTE tidak terekam** sebagai data (hanya status dokumen).

---

## 7. Isi konkret & variasi nilai per kolom (bukan sekadar persentase)

### 7.1 `trx_pemeriksaan.status` — 12 nilai unik (aktif)
`VERIFY4` 167.116 · `VERIFY5` 46.619 · `FINISHED` 29.042 · `DRAFT_REVISE` 5.108 · `VERIFY7` 4.784 · `DRAFT` 3.297 · `VERIFY6` 1.008 · `VERIFY1` 640 · `VERIFY2` 619 · `DRAFT_PUSAT` 464 · `VERIFY_P1` 351 · `FINISHED_PUSAT` 113. Artinya: 3 dari 4 kasus berhenti/menunggu di verifikasi Operator Pusat.

### 7.2 `datas` — variasi jawaban aspek (yang benar-benar tersimpan di dalam JSON)

**Pelayanan (Apotek, section `tx_pengadaan_obat`, sampel 500 kasus terbaru)** — pertanyaan berkode Inggris:

| Key | Nilai unik (frekuensi) |
|---|---|
| `opsi` | `"yes"` 410 · `"mostly"` 46 · `"rarely"` 11 · `"no"` 10 · `"illegal"` 3 |
| `n` | `"300"` 410 · `"150"` 46 · `"0"` 13 · `"75"` 11 |
| `fp` | `"3"` 480 |
| `score` | `"100"` 410 · `"50"` 46 · `"0"` 13 · `"25"` 11 |
| `other` | `{"apotek":"on"}` 58 · `{"pm":"on"}` 2 · `{"to":"on"}` 2 |

Pemetaan ke layar: yes=**Ya/Sesuai**, mostly=**Sebagian Besar**, rarely=**Sebagian Kecil**, no=**Tidak**, illegal=**dugaan produk ilegal**; `score = n ÷ fp` (100/50/25/0 per item; section `tx_penyimpanan_*` mengakumulasi, contoh `n:"262.50", score:"262.5"`). Section `tx_penyerahan_*` punya varian key khusus (antibiotika tanpa resep, KIE, DOWA).

**Produksi (item klausul)** — potongan mentah nyata:
```json
"administrasi":{"distribusi":{
  "a1":{"aspect":"Ya","note":"izin usaha"},
  "a2":{"aspect":"Ya","note":"memiliki faktur"},
  "a3":{"aspect":"Ya","note":"tidak mengeluarkan bon penjualan"},
  "a4":{"aspect":"Tidak","note":"tidak ada pencatatan"}}},
"penyimpanan":{"gudang":{"aspect":"Ya","a1":{"aspect":"Ya","note":null},
  "a3":{"aspect":"Ya","note":null,"p1":{"aspec...
```
Perhatikan: `note` bisa berisi keterangan naratif ("tidak ada pencatatan") atau `null`; ada **sub-item bersarang** (`a3.p1`); jawaban `"Ya"/"Tidak"` (Indonesia) — beda dari pelayanan yang Inggris.

**Paste Word**: 6.731 datas berisi HTML `MsoNormal` — contoh ekstrem section `tx_pengadaan` = 264.736 karakter dokumen Word utuh (termasuk XML `o:DocumentProperties`).

### 7.3 `result` — nilai unik `hp_kesimpulan` (sampel 3.000 kasus terbaru)
`MK` 1.931 · `TMK` 1.038 · `TTP` 20 · `TDP` 9 · teks bebas: *"tidak ada temuan produk"* 19, *"Tidak ada temuan"* 9, *"Tidak ditemukan produk kosmetik TIE, rusak dan kadaluarsa"* 8, `-` 98, kosong 655. → Kode MK/TMK dominan, tapi kolom ini **tidak murni terkamusk** — campuran teks bebas harus dinormalisasi saat ekstraksi.

### 7.4 `trx_pemeriksaan_approval.notes` — nilai unik paling sering (membuka label role!)
*"Verifikasi Supervisor Pemdik Satu"* **102.708** · *"Verifikasi Supervisor Pemdik Dua"* 23.586 · *"Verifikasi Supervisor Pemdik Satu Tipe-A Tipe-B Loka"* 18.908 · *"Ditolak Supervisor Pemdik Satu"* 6.161 · *"Mohon koreksi, terima kasih"* 2.936 · *"Mohon diverifikasi sebagai laporan"* 2.381. → kandidat kunci pemetaan `VERIFY1..7` → role (Pemdik Satu/Dua), walau belum resmi.

### 7.5 `ms_product.product_register` (NIE pada temuan) — variasi prefix
`NA` 624.011 · `MD` 477.651 · `ML` 178.660 · `"-"` 163.751 · `NC` 118.143 · `NE` 47.479 · `TR` 41.749 · `DK` 32.357 · `LK` 14.527 · `NK` 12.706 — produk temuan bisa lintas jenis izin (kosmetik NA, pangan MD/ML, obat TR/DK/LK, dll).

### 7.6 `trx_pemeriksaan_temuan.tp_keterangan` — free text bukti tindak lanjut (46% terisi)
Contoh nyata: *"Dimusnahkan ditempat oleh pelaku usaha dengan disaksikan petugas BBPOM di Surabaya"* · *"Pabrik PJ sumber makmur; TR05367796 Produk PW"* — narasi singkat petugas, bukan terkamusk.

## 8. SQL verifikasi + output nyata (reproduksibel)

```sql
-- (1) Nilai unik jawaban aspek pelayanan + frekuensinya
WITH a AS (SELECT (datas::jsonb #>> '{}')::jsonb j FROM trx_pemeriksaan
  WHERE deleted_at IS NULL AND datas IS NOT NULL
    AND jenis_id = (SELECT id FROM ms_master_data WHERE type='JENIS_SARANA' AND name='Apotek' LIMIT 1)
  ORDER BY tgl_start DESC LIMIT 500),
s AS (SELECT p, k0, p->k0 v FROM a, LATERAL (SELECT j->'tx_pengadaan_obat' p) q,
  LATERAL (SELECT jsonb_object_keys(p) k0) x)
SELECT k0, v::text, count(*) FROM s GROUP BY 1,2 ORDER BY 1, 3 DESC;
-- → opsi "yes" 410 | "mostly" 46 | "rarely" 11 | "no" 10 | "illegal" 3 ; score 100/50/25/0

-- (2) Nilai unik hp_kesimpulan
WITH r AS (SELECT (result::jsonb #>> '{}')::jsonb j FROM trx_pemeriksaan
  WHERE deleted_at IS NULL AND result IS NOT NULL AND length(result) < 30000
  ORDER BY tgl_start DESC LIMIT 3000)
SELECT j->>'hp_kesimpulan', count(*) FROM r GROUP BY 1 ORDER BY 2 DESC;
-- → MK 1931 | TMK 1038 | TTP 20 | TDP 9 | (teks bebas…)

-- (3) Sebaran petugas per kasus (array JSON!)
SELECT jsonb_array_length(petugas_id::jsonb) n_petugas, count(*)
FROM trx_pemeriksaan_detail GROUP BY 1 ORDER BY 2 DESC;
-- → 2 → 236.777 | 3 → 31.091 | 1 → 26.124 | 4 → 11.389 | 5 → 1.578

-- (4) Kategori temuan (array JSON) — top 8
SELECT tp_kategori_id, count(*) FROM trx_pemeriksaan_temuan
GROUP BY 1 ORDER BY 2 DESC LIMIT 8;
-- → ["506"] 160.213 (TIE) | ["840"] 60.264 (ED) | ["211214"] 22.263 (Obat Keras)
--   ["499"] 10.473 (BKO) | ["856"] 10.472 (Rusak) | ["499","506"] 7.267 (kombinasi!)

-- (5) Regional via entri_balai_id → ms_balai
SELECT b.regional_name, count(*) FROM trx_pemeriksaan t
JOIN ms_balai b ON b.id = t.entri_balai_id::bigint
WHERE t.deleted_at IS NULL GROUP BY 1 ORDER BY 2 DESC;
-- → Semarang 60.504 | Medan 40.315 | Surabaya 36.953 | Pekanbaru 35.999 | … | (NULL) 1.057

-- (6) Jejak workflow kasus contoh
SELECT act_steps, to_steps, status, left(notes,60), created_at
FROM trx_pemeriksaan_approval WHERE pemeriksaan_id = 291155 ORDER BY id;
-- → DRAFT | step_verify1 | DRAFT | "Entri Draft Pemeriksaan Sarana Obat Trad…" | 2026-09-14 08:31
```

---

### SQL reproduksi contoh dasar di dokumen ini

```sql
-- koneksi: postgresql://<user>:<pass>@10.59.2.29:5432/sipt_sync
-- 1) kasus contoh + surat tugas + petugas
SELECT t.*, d.nomorsurat, d.tgl_surat, d.balai_id, d.petugas_id
FROM trx_pemeriksaan t JOIN trx_pemeriksaan_detail d ON d.pemeriksaan_id = t.id
WHERE t.id = 291155;
-- 2) temuan produk kasus contoh (join kamus WAJIB parse array + cast)
SELECT p.product_name, x.tp_jml_temuan, x.tp_kategori_id, x.tp_tindakan_id
FROM trx_pemeriksaan_temuan x
LEFT JOIN ms_product p ON p.id::text = x.tp_product_id::text
WHERE x.pemeriksaan_id = 291155;
-- 3) membuka JSON dobel-encode
SELECT (datas::jsonb #>> '{}')::jsonb -> 'tx_penyimpanan_obat'
FROM trx_pemeriksaan WHERE id = 291156;
```

---
*Angka per 16 Sep 2026. Dokumen pendamping: [alur-entry-dari-capture.md](alur-entry-dari-capture.md) · [../ERD/02-katalog-tabel.md](../ERD/02-katalog-tabel.md) · [pertanyaan-analitik.md](pertanyaan-analitik.md).*
