# Varian `24-09-2026 v5-staging-based` — context & skill berbasis `staging`

**Dibuat:** 24 September 2026
**Menggantikan:** `context/` + `SEEKNAL_ASK.md` + `seeknal/skills/` yang masih memakai skema `mv_*`
**Acuan gaya:** `../../seeknal-bpom-rpo-erba/docs/context_recap/september/v4-sep-w1/` (metode saja)
**Spesifikasi kerja:** `../../../audit_context/` (11 dokumen, termasuk verifikasi live)

---

## 1. Mengapa varian ini ada

Artefak yang dibaca agent sebelumnya mengajarkan skema yang sudah tidak dipakai:

| Pencarian | Hasil |
|---|---|
| `mv_pemeriksaan`, `tanggal_mulai`, `nama_upt` | **159 kemunculan di 30 file** — semuanya di `context/`, `SEEKNAL_ASK.md`, `skills/` |
| `fact_pemeriksaan`, `flag_varian_datas` | 16 file — semuanya dokumen manusia (`docs/ERD`, `docs/blueprint_kebutuhan_user`) |

Artinya: aturan yang dipakai agent **salah sasaran**, dan dokumen yang benar **belum terhubung** ke agent. Varian ini menjadi jembatannya.

---

## 2. Apa yang berubah

| Artefak | Perubahan |
|---|---|
| `SEEKNAL_ASK.md` | v5: blok **Canonical Rules** (5 blok, menang atas halaman), Page Map konsep `staging`, Gate 0 sub-routing "temuan", Gate 2 wajib `type` + P5 diperluas, Gate 3 dua field baru, Gate 5 14 check |
| `context/` | 21 halaman: **6 baru** (`01`, `05`, `35`, `37`, `45`, `97`), **10 ditulis ulang**, **5 disesuaikan** |
| `context/11-klasifikasi-distribusi.md` | **dilebur** ke `05-filter-katalog.md` — kolomnya tidak ada di `staging` |
| `skills/bpom-analyst` | checklist Gate 5 versi `staging`; larangan salah varian; kewajiban coverage & dua panel |
| `skills/bpom-forecaster` · `skills/detect-anomaly` | entity & kolom `staging` (sebelumnya paling banyak memuat skema lama) |
| `skills/visualize-chart` | pola dua panel untuk satuan berbeda |

---

## 3. Empat prinsip yang mengikat

1. **Context mengajarkan cara menemukan, bukan melamarikan jawaban.** Tanpa angka hasil query; kode domain boleh ditulis, tapi selalu disertai jalur pencariannya.
2. **Setiap halaman punya matriks operasi.** Satu kolom berperilaku berbeda saat **menyaring**, **mengelompokkan**, **men-join**, dan **memeringkat** — keempatnya ditulis, termasuk yang "biasa".
3. **Setiap halaman punya manifes** (tabel · kolom · literal) sehingga skrip verifikasi dapat membuktikan keabsahannya ke database dan mendeteksi konsep yang belum menyeberang ke context.
4. **Karantina eksplisit.** Kolom yang tidak boleh dikutip selalu disertai penggantinya.

---

## 4. Yang diadopsi dari gaya `v4-sep-w1`

Canonical Rules di orchestrator · halaman katalog filter panel · tabel keputusan "kata → filter/kode" · trigger words di kepala halaman · aturan anti-tuning (*decide from the subject, never from the size of the result*) · jebakan format + cara memastikan · panel-vs-kanon · scope tabel eksplisit · Gate 5 sebagai tabel check.

Yang **tidak** diadopsi: aturan domain RPO (`produk_id`, `jenis_permohonan`, `kategori_dokumen`, `status_produk`, `daerah_pabrik`/`daerah_trader`, `ERBA`/`ERLA`, `NIE`). Domain berbeda; hanya cara berpikirnya yang dipinjam.

---

## 5. Hasil verifikasi yang mendasari

| # | Temuan |
|---|---|
| V1 | `distribusi_provinsi_kode` **bukan** klasifikasi distribusi; kolom klasifikasi distribusi **tidak ada** |
| V2 | `dim_balai.target_sampling` & `target_sarana` terisi penuh |
| V3 | `dim_status_code.status_label` terisi **0 dari 35** |
| V4 | 9 nilai `flag_varian_datas` → 9 jalur bridge |
| V5 | `opsi` bercampur makna **dan** punya duplikat ejaan; per `area_key` berbeda |
| V6 | `nilai_aspek` memuat 15 nilai = 4 makna berbeda |
| V7 | kamus kategori 28 kode, data memakai 49, **27 tak terpetakan** |

Rincian: `../../../audit_context/07-verifikasi-live.md`.

---

## 6. Item tertunda

| Item | Status |
|---|---|
| Skrip manifes (`scripts/verify_context_manifest.py`) + kontrol negatif | belum dibuat (fase F6b) |
| Linter context L1–L12 | belum dijalankan |
| Uji "menemukan" 6 pertanyaan di luar corpus | belum dijalankan |
| Keputusan bisnis D1–D11 (`audit_context/09`) | menunggu stakeholder |
| Bridge antibiotik & pemetaan section | pekerjaan data terpisah |

---

## 7. Cara memakai varian ini

- Uji pembanding: `--variants-path docs/context_recap --variants "24-09-2026 v5-staging-based"`.
- Promosi ke `context/` + `seeknal/skills/` hanya setelah linter, manifes, dan uji menemukan lulus.
- Varian `after-insight-v1..v3` **tidak disentuh**; hanya dipakai sebagai pembanding historis.
