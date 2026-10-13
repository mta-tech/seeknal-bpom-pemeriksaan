# Pertanyaan Asli User → Jalur Data → Bisakah Dijawab?

> **Posisi dokumen (22 Sep 2026):** sembilan pertanyaan di file ini adalah **fondasi kebutuhan awal**, bukan satu-satunya definisi requirement. Perspektif user yang lebih lengkap—persona, entry flow, kebutuhan report, semantic glossary, kontrak metrik, use-case, dan dasar testcase—ada di [Blueprint Kebutuhan User](../blueprint_kebutuhan_user/README.md).
>
> Angka/status lama di dokumen ini tidak otomatis mencerminkan kondisi current. Untuk kondisi `staging`, gunakan [ERD current](../ERD/README.md) dan [Kondisi Data & Kesiapan](../blueprint_kebutuhan_user/04-kondisi-data-dan-kesiapan.md).
>
> **Tujuan**: memasangkan **pertanyaan analitik asli tim** (verbatim) dengan jalur data, status kesiapan jawaban, dan **bentuk jawaban yang akan muncul** — supaya jelas "kalau pertanyaan ini dijawab, datanya seperti apa".
>
> Kategori status: **[SIAP]** datanya ada & sehat, tinggal query · **[SEBAGIAN]** bisa dengan catatan keras · **[BELUM]** butuh kerja ekstraksi/keputusan dulu.
>
> Baseline data: 259.348 kasus aktif (2020: 29.761 · 2021: 40.308 · 2022: 46.293 · 2023: 45.831 · 2024: 48.005 · 2025: 33.360 · 2026 ytd: 14.759) — `sipt_sync`, 16 Sep 2026. Semua jalur di bawah bisa dieksekusi sekarang ke `sipt_sync`; setelah pipeline tahap-2 selesai, jalur yang sama berpindah ke `staging` (fact/bridge/dim — lihat [../ERD/02-katalog-tabel.md](../ERD/02-katalog-tabel.md)).

---

## Q1–Q7 — "Tampilkan tren temuan hasil pemeriksaan pada aspek pengadaan / penerimaan / penyimpanan / penyerahan / pengembalian / pencatatan dan pelaporan / pemusnahan selama periode x"

**Status: [SEBAGIAN → SIAP setelah parser `datas`] — jalur per aspek di bawah, fokus di sini: VARIAN ISI-NYA APA SAJA.**

Pertanyaan aspek tidak bisa dijawab dengan satu query sederhana karena isi `datas` punya **3 varian bentuk isian yang berbeda**, dan tiap aspek punya **item pertanyaan yang berbeda**:

### Varian A — Sarana Pelayanan: pertanyaan terukur dengan skor (mayoritas data)

Setiap aspek = section `tx_<aspek>_*` berisi item pertanyaan dengan **5 kemungkinan jawaban berkode + skor**:

| Nilai `opsi` di database | Padanan di layar | Skor |
|---|---|---|
| `yes` | Sesuai / Ya | 100 |
| `mostly` | Sebagian Besar | 50 |
| `rarely` | Sebagian Kecil | 25 |
| `no` | Tidak | 0 |
| `illegal` | Dugaan ilegal | 0 (+ flag `other`) |

Contoh nyata section `tx_pengadaan_obat` (Apotek): `opsi:"yes", n:"300", fp:"3", score:"100"`; ada juga sub-pertanyaan kondisional yang di layar berbunyi *"sebutkan sumber pengadaan / pihak yang melakukan pengadaan"* (wajib bila jawab bukan `yes`).

Item per aspek berbeda-beda, contoh nyata yang terbaca dari key section:

- **Pengadaan**: `tx_pengadaan_obat`, `tx_pengadaan_drugs`, `tx_pengadaan_apj`, `tx_pengadaan_arsip` — sumber pengadaan, legalitas pemasok.
- **Penerimaan**: `tx_penerimaan_obat`, `tx_penerimaan_param` — faktur, cek label/ED saat terima.
- **Penyimpanan**: `tx_penyimpanan_obat/_drugs/_ccp/_psiko/_rusak/_investigasi/_opname_obat/_opname_drugs` — contoh item nyata: `wadah, bentuk, sentuh, sistem, jaminan, kondisi, kontaminasi` (semuanya `"on"` = terjawab) + skor akumulasi `n:"262.50", score:"262.5"`.
- **Pendistribusian**: `tx_distribusi`.
- **Penyerahan**: ±14 section — `tx_penyerahan_obat/_drugs/_izin/_info/_sarana/_jaminan/_arsip`, khusus antibiotik: `tx_penyerahan_antibiotika_oleh/_tanpa_resep_kepada/_tanpa_resep_kepada_terbanyak/_tanpa_resep_kie/_tanpa_resep_oleh`, plus `tx_total_fp/tx_total_n` (skor total).
- **Pengembalian + Pencatatan/Pelaporan**: `tx_pengembalian_mutasi/_retur/_sipnap`, `tx_pencatatan_mutasi_antibiotika`.
- **Pemusnahan**: `tx_pemusnahan_obat/_drugs`.

**Bentuk "temuan" di varian ini** = item dengan `opsi ≠ yes` (skor <100) dan/atau `illegal`. Tren per aspek = agregasi skor/jawaban section itu per periode.

### Varian B — Sarana Produksi: klausul Ya/Tidak dengan catatan naratif

Struktur bersarang per aspek → sub-aspek → klausul `a1..aN`:

```json
"administrasi":{"distribusi":{
  "a1":{"aspect":"Ya","note":"izin usaha"},
  "a2":{"aspect":"Ya","note":"memiliki faktur"},
  "a4":{"aspect":"Tidak","note":"tidak ada pencatatan"}}},
"penyimpanan":{"gudang":{"a1":{"aspect":"Ya","note":null},
  "a3":{"aspect":"Ya","note":null,"p1":{...sub-klausul}}}}
```

Yang menjadi "temuan" = klausul dengan `"aspect":"Tidak"` (plus catatan petugas di `note`). Counter temuan kasus (gross/major/minor) masuk `result.hp_level` — terpisah dari JSON ini. 77.862 datas memuat pola `aspect` ini; volume per aspek: penyimpanan 187.457 · pengadaan 88.594 · penerimaan 88.335 · pemusnahan 82.842 · pengembalian 69.846 · penyerahan 68.865 · pencatatan 65.991.

### Varian C — Paste dokumen (6.731 datas)

Isian berupa dokumen Word mentah (HTML `MsoNormal`, sampai 264 ribu karakter/section). Untuk tren: tidak bisa dinilai otomatis → dihitung sebagai "naratif", bisa diproses layer teks/NLP.

### Konsekuensi untuk menjawab Q1–Q7

1. Parser wajib **routable 3 varian** (routing per `jenis_id`; `form_version_id` hanya membantu 29% kasus) dan **unescape 2×**.
2. Definisi "temuan aspek" harus disepakati dulu: Apotek-style (skor <100 atau `illegal`) vs Produksi-style (`aspect:"Tidak"`) — kedua varian menghasilkan satuan berbeda (persen pemenuhan vs jumlah klausul tidak sesuai).
3. Nama aspek di form ≠ master `ASPEK_KTL` (tidak ada Penerimaan/Pengembalian di master; ada Penyaluran yang di layar bernama Pendistribusian) → mapping label untuk dashboard.
4. Setelah itu bentuk jawaban: `tahun | aspek | kasus_diperiksa | item_dijawab | item_tidak_sesuai | skor_rata2 | persen_pemenuhan` (+ breakdown `ms_balai.regional_name` untuk versi per daerah).

---

## Q8 — "Analisis jumlah pemeriksaan oleh masing-masing inspektur … dalam penugasan ke masing-masing jenis fasilitas Sardis dan Saryan"

**Status: [SIAP — data 100% ada]**

- Jalur: `trx_pemeriksaan_detail.petugas_id` (array JSON, terisi 100%) → `dim_user` (staging) untuk nama · dibelah per `trx_pemeriksaan.jenis_id` → `ms_master_data` (JENIS_SARANA; golongan Sardis/Saryan via `parent_id` 1=Produksi, 2=Distribusi, 3=Pelayanan).
- Bentuk jawaban: `inspektur | jenis_sarana | golongan | jumlah_kasus | rentang_tanggal`. Angka nyata sekarang: inspektur terbanyak user_id `1925` (1.113 kasus), `2469` (1.096), `2069` (1.031); sebaran tim per kasus 2 orang (236.777 kasus), 3 orang (31.091), 1 (26.124), 4 (11.389), 5 (1.578).
- Catatan: nama inspektur tidak ada di `sipt_sync` (hanya ID) — nama datang dari `dim_user` staging.

---

## Q9 — "Tren hasil pengawasan sarana distribusi dan pelayanan berdasarkan kolom ketidaksesuaian … (jenis dan jumlah temuan terbanyak) … kategori temuan dan tingkat kekritisannya, tren per regional"

**Status: [SIAP untuk jenis & jumlah + regional] · [SEBAGIAN untuk kekritisan]**

- **Jenis & jumlah temuan terbanyak** → `trx_pemeriksaan_temuan.tp_kategori_id[]` → kamus `KATEGORI_TEMUAN_PRODUK`. Bentuk jawaban: `kategori | jumlah_temuan | jumlah_kasus | tren_tahunan`. Angka nyata: **TIE 160.213 · ED/Kedaluwarsa 60.264 · Obat Keras 22.263 · BKO 10.473 · Rusak 10.472** — dengan syarat **mapping kanonik kamus duplikat** (TIE 3 kode, Kedaluwarsa 3 kode) atau angka akan pecah.
- **Regional** → `trx_pemeriksaan.entri_balai_id → ms_balai.regional_name`: Semarang 60.504 · Medan 40.315 · Surabaya 36.953 · Pekanbaru 35.999 · Makassar 27.533 · Samarinda 24.483 · Manado 17.264 · Jayapura 15.240 · tanpa regional 1.057 (0,4%). Bentuk jawaban: `regional | kategori | tahun | jumlah`.
- **Tingkat kekritisan** ⚠️ → hanya per **kasus** (bukan per temuan): `result.hp_level = {major, minor, critical, conclusion}`, terisi ±9 rb+ (subset form produksi); scaffold staging punya `jumlah_temuan_kritis/mayor/minor`. Angka kekritisan global TIDAK AKAN penuh 259 rb kasus — sampaikan ke user bahwa kekritisan hanya tersedia untuk subset form tertentu.
- **Distribusi vs pelayanan** → filter `jenis_id` golongan 2 (Distribusi: PBF, Toko Obat, dst.) dan 3 (Pelayanan: Apotek, Klinik, PKM, dst.) via parent kamus JENIS_SARANA.

---

## Pertanyaan lanjutan yang juga sudah bisa dijawab dari data yang sama

| Pertanyaan user (mungkin) | Jalur | Status |
|---|---|---|
| "Berapa pemeriksaan yang selesai vs macet di verifikasi?" | `status` + `trx_pemeriksaan_approval` | **[SIAP]** — VERIFY4 backlog 167.116 kasus (64%) di Operator Pusat |
| "Apa tindakan yang paling sering diambil atas temuan?" | `tp_tindakan_id[]` → kamus 15 kode | **[SIAP]** — Pemusnahan 186.818, Dikembalikan 33.776, Pengamanan 29.970… |
| "Produk apa yang paling sering jadi temuan?" | `tp_product_id → ms_product.product_name` | **[SIAP]** — 100% ter-link |
| "Bagaimana grade/kualitas sarana produksi?" | `result.hp_grade` (A/B/C), `hp_hasil` | **[SEBAGIAN]** — ±44 rb kasus produksi saja |
| "Berapa kasus yang sampai CAPA?" | `result.tl_capa` | **[SIAP]** — 62.097 |
| "Kapan surat TL sudah ditandatangani elektronik?" | — | **[BELUM]** — TTE tidak terekam di DB (status dokumen saja) |
| "Berapa klausul yang tidak sesuai per aspek (bukan per kasus)?" | perlu parse `datas` klausul | **[BELUM → SIAP setelah P3]** — kekritisan klausul tidak pernah dicatat; yang ada jawaban Ya/Tidak + catatan |

---

## Ringkasan kesiapan

| Kelompok | Status | Penghalang utama |
|---|---|---|
| Q8 inspektur × fasilitas | SIAP | — (nama user dari `dim_user`) |
| Q9 jenis/jumlah temuan + regional | SIAP | mapping kanonik kamus duplikat |
| Q9 kekritisan | SEBAGIAN | hanya per kasus, subset form |
| Q1–Q7 tren per aspek | SEBAGIAN → SIAP | parser 3-format `datas` (P3) |
| CAPA/naratif/NLP | SEBAGIAN | ekstraksi teks `result` (P6) |
| TTE, kekritisan klausul | TIDAK BISA | data tidak pernah ada di aplikasi |

*Verifikasi 16 Sep 2026; SQL contoh di [pemetaan-form-ke-database.md](pemetaan-form-ke-database.md); prioritas kerja ekstraksi (P1–P8) di [pemetaan-entry-per-flow-ke-staging-NEW.md](pemetaan-entry-per-flow-ke-staging-NEW.md) dan [../ERD/07-kualitas-data.md](../ERD/07-kualitas-data.md) §5.*
