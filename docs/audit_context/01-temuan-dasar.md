# 01 — Temuan Dasar

> Dasar mengapa penulisan ulang ini dilakukan, beserta bukti terukurnya.

---

## 1. Temuan 1: referensi pemeriksaan basi **dan** tidak terhubung ke agent

Pengukuran dengan pencarian teks di seluruh project:

| Yang dicari | Hasil |
|---|---|
| Skema lama (`mv_pemeriksaan`, `tanggal_mulai`, `nama_upt`) | **159 kemunculan tersebar di 30 file** |
| Skema sekarang (`fact_pemeriksaan`, `flag_varian_datas`) | **16 file** |

Sebaran 159 kemunculan itu:

| Lokasi | Artinya |
|---|---|
| `context/*.md` (15 halaman) | aturan yang dibaca agent → salah sasaran |
| `SEEKNAL_ASK.md` | orchestranya sendiri menyebut skema lama |
| `seeknal/skills/bpom-analyst/SKILL.md` | penegakan ikut salah |
| `seeknal/skills/bpom-forecaster/SKILL.md` (**19**) dan `detect-anomaly` (**7**) | dua skill ini paling banyak memuat skema lama |

Sedangkan 16 file yang memuat skema sekarang **semuanya dokumen manusia**: `docs/ERD/`, `docs/blueprint_kebutuhan_user/`, `docs/user_flow/`, `docs/testcase/README.md` (sebagian).

**Kesimpulan:** masalahnya bukan hanya "isi basi", tetapi **tidak adanya jembatan** antara dokumen kondisi (ERD/blueprint) dan dokumentasi pengajaran agent (context/skill). Jembatan itulah inti pekerjaan ini — bukan sekadar find-and-replace nama tabel.

Bukti pendukung: `docs/context_recap/after-insight-v1`, `-v2`, `-v3` semuanya masih memuat skema lama; v3 hanya menambah `context/15-tujuan-pemeriksaan.md` dan mengefisienkan Gate 1.

---

## 2. Temuan 2: katalog filter panel user tidak punya padanan kolom di `staging`

Label yang dilihat user di panel versus kenyataan `staging` (verifikasi 22 Sep 2026):

| Label panel | Padanan di `staging` | Status |
|---|---|---|
| Jenis sarana | `fact_pemeriksaan.jenis_id` → `JENIS_SARANA` | ✅ ada |
| Komoditi | `klasifikasi_id` → `JENIS_KLASIFIKASI` | ✅ ada |
| Tanggal | `tgl_start` · `tgl_end` · `created_at` · `updated_at` | ✅ 4 label → 4 kolom |
| Kesimpulan | `kesimpulan_balai_id` / `kesimpulan_pusat_id` | ✅ ada |
| Grade | `grade` | ✅ ada (subset produksi) |
| Tujuan pemeriksaan | `tujuan_id` | ✅ ada |
| Petugas | `bridge_pemeriksaan_petugas` | ✅ ada |
| Legal | `dim_sarana.legal_id` | ⚠️ ada, tapi **merujuk 2 kamus** |
| Status label | `dim_status_code.status_label` | ⚠️ kolom ada, **terisi 0 dari 35 baris** |
| Tingkat pemenuhan CPOB | kelompok kode pada `kesimpulan_balai_id` | ⚠️ ada sebagai kode, bukan kolom sendiri |
| Target / capaian | `dim_balai.target_sampling` + `target_sarana` | ✅ terisi 108/108 balai |
| **Klasifikasi distribusi** | — | ❌ **tidak ada kolom** |
| **Klasifikasi sarana** | `klasifikasi_sarana_kode` | ⚠️ ada, cakupan khusus Pangan |

Catatan: kolom `distribusi_provinsi_kode` yang terlihat di pencarian ada di `fact_pemeriksaan_profil_pangan_md` (tujuan distribusi pabrik Pangan MD) — **bukan** klasifikasi distribusi sarana. Salah menyambung ke sini akan menghasilkan query yang jalan dengan makna berbeda.

**Konsekuensi untuk context:** kalau agent menebak kolom dari nama label panel, ia akan menghasilkan query yang jalan tetapi salah. Karena itu `05-filter-katalog.md` wajib menyatakan honest gap secara eksplisit.

---

## 3. Temuan 3: `opsi` bercampur makna **dan** punya duplikat ejaan

Verifikasi per `area_key` (22 Sep 2026):

| area_key | Isi `opsi` | Kesimpulan |
|---|---|---|
| `tx_pemusnahan_obat` | N/A 47.026 · yes 15.521 · null 1.304 | **tidak ada nilai `no`** → tidak bisa dipakai sebagai indikator temuan |
| `tx_penerimaan_obat` | "Apoteker atau TTK" 31.203 · "Ya" 12.813 · "Tenaga Kesehatan Non-farmasi" 4.500 · "Lainnya" 4.121 · **"lainnya" 3.868** · "Asisten Apoteker" 3.300 · "ttk" 1.605 · "tenagakesehatan" 941 · **"asisten" 161** · "Tidak" 154 | campuran **jabatan + jawaban**, dan ada **duplikat kapitalisasi** |
| `tx_pengembalian_mutasi` | `{"mutasi":"yes"}` 46.610 · `{"mutasi":"mostly"}` 7.115 · null 6.110 · `{"mutasi":"rarely"}` 4.016 | bentuknya **JSON object**, bukan string |
| `tx_penyimpanan_obat` | null 63.756 (seluruh baris `opsi` kosong) | sinyalnya ada di `score`/key item, **bukan** di `opsi` |

Temuan tambahan: `nilai_aspek` memuat **15 nilai berbeda** yang mencampur konformitas (`OK`, `Ya`, `Tidak Berlaku`), grade (`B`, `T`, `C`, `K`), severity (`Minor`, `Major`, `Kritis`, `Serius`, `Kritikal`), dan status (`Lanjut`).

**Konsekuensi:** kontrak per `area_key` (halaman `35`) dan kontrak `nilai_aspek` (halaman `37`) bukan pelengkap — keduanya wajib. Pola duplikat kapitalisasi ini analog dengan jebakan `'5'` vs `'5.0'` di gaya v4, dan harus punya aturan normalisasi.

---

## 4. Temuan 4: kamus kategori temuan tidak menutup data

| Aspek | Nilai (22 Sep 2026) |
|---|---|
| Kode di kamus `KATEGORI_TEMUAN_PRODUK` | 28 |
| Kode berbeda yang dipakai di data | **49** |
| Kode dipakai yang **tidak ada** di kamus | **27** (444 baris) |
| Kode kamus yang **tidak dipakai** | 6 (termasuk 3 kode TIE duplikat & 2 kode Kedaluwarsa) |
| Tumpang tindih makna yang nyata di data | Rusak (`856` + `759`) · bahan berbahaya (3 kode) |

**Konsekuensi:** halaman `40` wajib memuat prosedur bucket "tidak terpetakan" dan aturan penggabungan makna yang benar-benar terjadi di data — bukan mengklaim kanonikalisasi sudah tuntas.

---

## 5. Gaya yang diadopsi dari `v4-sep-w1`

Acuan: `../seeknal-bpom-rpo-erba/docs/context_recap/september/v4-sep-w1/` (proyek sebelah).

| Elemen gaya | Wujud | Alasan dipakai |
|---|---|---|
| **Canonical Rules di orchestrator** | tabel keputusan diletakkan di `SEEKNAL_ASK.md` sebelum gerbang, dan **menang** atas halaman | koreksi paling menentukan terbaca tanpa membuka halaman |
| **Halaman katalog filter panel** | label panel → kolom → kode → halaman; plus daftar label tanpa kolom | user bertanya dengan bahasa panel |
| **Tabel keputusan per konsep** | "kata dalam pertanyaan → filter/kode" | mengajarkan menemukan, bukan menghafal |
| **Trigger words di kepala halaman** | baris pertama = kata pemicu | menyambung ke Page Map |
| **Anti-tuning** | *decide from the subject, never from the size of the result* | mencegah filter digeser agar angka terlihat wajar |
| **Jebakan format + cara memastikan** | padding kode, duplikat ejaan, sentinel | dipetakan ke jebakan `opsi`/`nilai_aspek`/soft-delete |
| **Panel vs kanon** | label panel berbeda dari bacaan kanonik | mis. "tingkat pemenuhan CPOB" vs kode kesimpulan |
| **Scope & tabel terlarang eksplisit** | daftar tabel yang boleh | 27 boleh · 26 pengawasan terlarang |
| **Gate 5 sebagai tabel check** | check + pass criterion | memudahkan audit |
| **README delta + koreksi terverifikasi** | ringkas dan bernomor | pola untuk README snapshot v5 |

---

## 6. Guard lintas domain (tidak boleh bocor)

Aturan RPO/ERBA/ERLA **bukan** aturan pemeriksaan. Istilah yang dilarang muncul di context pemeriksaan:

`produk_id` · `nomor_surat` (sebagai identitas produk) · `jenis_permohonan` · `kategori_dokumen` · `status_produk` · `daerah_pabrik` · `daerah_trader` · `ERBA` · `ERLA` · `NIE`

Yang **diadopsi** hanya cara berpikirnya: tabel keputusan kata→kode, kode gabungan, panel-vs-kanon, jebakan format, anti-tuning.

**Kewaspadaan yang relevan:** bahaya "kode angka berulang lintas kategori" juga nyata di pemeriksaan — `dim_master_data` memuat **72 tipe kamus dalam satu tabel**, sehingga `master_data_id` bisa berbenturan makna antar tipe. Karena itu aturan *"setiap join ke kamus wajib menyebut `type`"* naik menjadi aturan tingkat satu di blok Canonical Rules.

---

## 7. Daftar terlarang untuk linter

Linter wajib menolak file yang memuat:

- `mv_pemeriksaan`, `mv_pemeriksaan_temuan`, `mv_pemeriksaan_agg`, `mv_pemeriksaan_log`, `mv_pemeriksaan_timeline`, `mv_pemeriksaan_petugas`
- `tanggal_mulai`, `tanggal_input`, `nama_upt`, `sarana = 'PRODUKSI'` (versi kolom lama)
- istilah RPO pada §6
- angka hasil query (pola umum: bilangan ≥ 3 digit yang berdiri sendiri tanpa konteks kode)
