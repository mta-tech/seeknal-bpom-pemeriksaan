# Audit Context — Spesifikasi Penulisan Ulang Context, Skill, dan Testcase

> **Folder ini adalah spesifikasi kerja**, bukan artefak yang dibaca agent. Isinya merinci *apa yang akan dibuat*, dari sumber mana, dengan aturan apa, dan bagaimana diverifikasi.
>
> Status: **detail plan (siap dieksekusi)** · Disusun 22 Sep 2026 · Domain: Pemeriksaan (`staging`)

---

## 1. Untuk apa folder ini

**Mulai dari sini:** [00-story.md](00-story.md) — cerita pekerjaan: apa yang sudah dikerjakan per
dokumen, insight yang didapat, dan status tiap fase.

| Pertanyaan | Dijawab di |
|---|---|
| **Apa yang sudah dikerjakan dan insight-nya apa?** | **[00-story.md](00-story.md)** |
| Kenapa context/skill sekarang harus diganti? | [01-temuan-dasar.md](01-temuan-dasar.md) |
| Halaman context apa saja yang akan dibuat, masing-masing isinya apa? | [02-spec-context-halaman.md](02-spec-context-halaman.md) |
| Bagaimana bentuk `SEEKNAL_ASK.md` v5 dan blok Canonical Rules? | [03-spec-seeknal-ask-v5.md](03-spec-seeknal-ask-v5.md) |
| Skill mana yang diubah dan apa persisnya? | [04-spec-skill.md](04-spec-skill.md) |
| Bagaimana memetakan label panel user ke kolom? | [05-spec-filter-katalog.md](05-spec-filter-katalog.md) |
| Bagaimana testcase baru dibentuk dan diuji? | [06-plan-testcase.md](06-plan-testcase.md) |
| Fakta apa yang sudah diverifikasi live? | [07-verifikasi-live.md](07-verifikasi-live.md) |
| Urutan kerja dan definisi selesai? | [08-urutan-kerja-dan-dod.md](08-urutan-kerja-dan-dod.md) |
| Risiko dan keputusan bisnis yang masih terbuka? | [09-risiko-dan-keputusan-terbuka.md](09-risiko-dan-keputusan-terbuka.md) |
| Metode mana dari rancangan lama yang dipakai? | [10-adopsi-rancangan-v2.md](10-adopsi-rancangan-v2.md) |

**Sudah ada sebelumnya di folder ini:** [`rancangan-v2.md`](rancangan-v2.md) — rancangan 14 Agu 2026 untuk warehouse **lama** (`mv_*`). Skemanya basi, tetapi **metodenya dipakai** (lihat file 10): matriks operasi per kolom, daftar karantina, penjaga waktu sebagai perilaku, dan **manifes + skrip verifikasi** dengan kontrol negatif.

Rencana induk (yang sudah disetujui): `~/.commandcode/plans/blueprint-context-skill-seeknal-ask-v2.md`.

---

## 2. Sumber isi (semua path relatif dari root project)

Root: `/home/mta/projects/seeknal_audit/seeknal-bpom-pemeriksaan/`

| Kategori | Path | Dipakai untuk |
|---|---|---|
| Kebutuhan user | `docs/blueprint_kebutuhan_user/01..09` + `README.md` | persona, entry flow, kebutuhan informasi, kesiapan data, glossary, kontrak metrik, use-case, blueprint testcase, gap |
| Kondisi data | `docs/ERD/README.md`, `01-aliran-data.md` … `08-contoh-datas.md` | katalog tabel, aturan join, routing bridge, aturan wajib, kamus, kualitas |
| Proses bisnis | `docs/user_flow/alur-entry-dari-capture.md`, `pemetaan-form-ke-database.md`, `pemetaan-entry-per-flow-ke-staging-NEW.md`, `pertanyaan-analitik.md` | flow entry, pemetaan form, sembilan pertanyaan fondasi |
| Corpus testcase lama | `docs/testcase/README.md` + 18 folder | status generated/historis; objek audit |
| Artefak agent sekarang | `SEEKNAL_ASK.md`, `context/*.md` (15 halaman), `seeknal/skills/*/SKILL.md` (4 skill), `seeknal_agent.yml` | objek yang diganti |
| Gaya acuan | `../seeknal-bpom-rpo-erba/docs/context_recap/september/v4-sep-w1/` | pola penulisan: Canonical Rules, filter-katalog, tabel keputusan, anti-tuning |
| Harness & output | `scripts/test_variant_compare.py`, `seeknal/tests/outputs/<tanggal>/<variant>/` | menjalankan dan mengaudit testcase |

---

## 3. Target yang akan dibuat

| Artefak | Path target | Isi | Status |
|---|---|---|---|
| Snapshot context/skill v5 | `docs/context_recap/24-09-2026 v5-staging-based/` | `SEEKNAL_ASK.md`, `context/` (21 halaman), `skills/` + `seeknal/skills/`, `README.md` | ✅ **sudah dibuat** |
| Linter context | `scripts/lint_context.py` | 12 pemeriksaan L1–L12 | ✅ **sudah dibuat, lulus** |
| Skrip manifes | `scripts/verify_context_manifest.py` | verifikasi tabel/kolom/literal + kontrol negatif | ⏳ belum |
| Batch testcase | `docs/testcase/blueprint-batch-<X>/` | 6–10 YAML per batch, kelas `ready`/`rule`/`decision`/`unavailable` | ⏳ belum |

Promosi ke `context/` + `seeknal/skills/` mengikuti kriteria di [08-urutan-kerja-dan-dod.md](08-urutan-kerja-dan-dod.md).

> ⚠️ Snapshot sudah dibuat **mendahului** F3 (verifikasi lanjutan), F6b (manifes), dan F7 (uji menemukan).
> Konsekuensinya: isinya **belum pernah diuji ke database maupun ke agent**. Linter hanya membuktikan
> konsistensi internal teks — bukan kebenaran klaimnya ke data.

---

## 4. Peta lama → baru

| Artefak lama | Nasib |
|---|---|
| `SEEKNAL_ASK.md` | diganti v5 (gerbang + Page Map + Canonical Rules) |
| `context/00-menghitung.md` | ditulis ulang |
| `context/10-sarana-dan-fasilitas.md` | ditulis ulang |
| `context/11-klasifikasi-distribusi.md` | **dilebur** ke `05-filter-katalog.md` (temuan: kolomnya tidak ada di `staging`) |
| `context/20-komoditi.md` | ditulis ulang |
| `context/30-kesimpulan.md` | ditulis ulang |
| `context/31-status-dan-alur.md` | ditulis ulang |
| `context/40-temuan-produk.md` | ditulis ulang |
| `context/41-nilai-dan-negara.md` | ditulis ulang |
| `context/50-jenis-pangan.md` | disesuaikan |
| `context/60-mutu-dan-tindak-lanjut.md` | ditulis ulang |
| `context/70-petugas.md` | ditulis ulang |
| `context/80-waktu-dan-durasi.md` | ditulis ulang |
| `context/85-target-capaian.md` | disesuaikan (kolom target ada, terisi penuh) |
| `context/90-kualitas-data.md` | ditulis ulang |
| `context/95-batas-domain.md` | disesuaikan |
| `context/15-tujuan-pemeriksaan.md` | disesuaikan |
| — | **baru**: `01`, `05`, `35`, `37`, `45`, `97` |
| `docs/context_recap/after-insight-v1..v3` | **tidak disentuh**; hanya pembanding historis |
| `docs/testcase/*` (256) | tidak diubah; diaudit statusnya |

---

## 5. Prinsip yang mengikat semua file

1. Context **mengajarkan cara menemukan**, bukan melamarikan jawaban: tanpa angka hasil query, tanpa daftar kode tanpa jalur pencarian.
2. Satu aturan satu pemilik (matriks di [02](02-spec-context-halaman.md) §4).
3. Setiap halaman: pemicu → keputusan → jebakan → batas → Rute; ≤200 baris.
4. Setiap kode yang ditulis harus berasal dari [07-verifikasi-live.md](07-verifikasi-live.md), bukan ingatan, dan bukan dari domain lain.
5. Aturan domain lain (RPO/ERBA/ERLA) **dilarang bocor** ke context pemeriksaan.

---

*Verifikasi live: 22 Sep 2026 · tunnel `srv29-staging` → `localhost:5432` · database `staging` schema `public`*
