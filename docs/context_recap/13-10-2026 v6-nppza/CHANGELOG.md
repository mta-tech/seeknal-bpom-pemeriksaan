# CHANGELOG — `13-10-2026 v6-nppza` (context & skill nasional pemeriksaan)

**Tanggal:** 13 Oktober 2026 · **Turunan:** `24-09-2026 v5-staging-based` · **Sumber:** blueprint 10 NPPZA (revisi 13 Okt) + blueprint 03–09 · **Verifikasi:** live `staging` via `pemeriksaan_reader`

## Prinsip perubahan

Snapshot immutable: folder ini dibuat dengan menyalin v5 lalu diubah di dalam salinan — snapshot lama
tidak disentuh. Angka hasil query tidak masuk context (aturan linter); semua aturan baru diajarkan
sebagai jalur penemuan.

## Perubahan per artefak

| Artefak | Perubahan |
|---|---|
| `context/22-komoditi-pbf-dan-fokus.md` | BARU — bridge `komoditi_pbf`/`fokus_pbf`, dua grain NPP, join `master_data_id::text` + `type`, cakupan PBF/IFK/IFP |
| `context/25-profil-sarana-faskes.md` | BARU — `prekursor` text t/f + cakupan form, `jenis_obat` JSON-string → parse, personel faskes |
| `context/20-komoditi.md` | +rute grain kedua (`22`), +baris keputusan "NPP di distribusi" |
| `context/40-temuan-produk.md` | +jebakan alias/varian kode & kode tertukar tempat (bucket eksplisit), +batas "keamanan mutu" = kelompok kode TMS KMG/bahan berbahaya |
| `context/41-nilai-dan-negara.md` | +kontrak tiga bucket negara (+query), +proxy prefix ML/MD dengan disclaimer & query keterisian |
| `context/60-mutu-dan-tindak-lanjut.md` | +pencarian narasi wajib prefiks, +CAPA "ekspor" tak terpakai → 95 |
| `context/80-waktu-dan-durasi.md` | +guard rentang operasional (nilai < 2020 dan masa depan jauh ada) |
| `context/95-batas-domain.md` | +4 baris konsep tak terekam: zat adiktif, permit/awal impor, re-ekspor, atribut importir |
| `context/97-glossary-istilah-user.md` | +6 istilah ambigu: PKM, NPP/NPPZA, keamanan mutu, obat keras, ekspor impor (+pemicu) |
| `SEEKNAL_ASK.md` | PAGE MAP: +baris `22`/`25`, pemicu diperluas (prekursor, obat keras, bahan berbahaya, zat adiktif, PKM, keamanan mutu); R2 +2 baris (grain NPP; obat keras/keamanan mutu/PKM) |
| `skills/bpom-analyst` (dua lokasi) | Gate 5 +2 check: dua grain NPP; kanonik kode temuan + bucket |

## Yang sengaja TIDAK berubah

- `skills/bpom-forecaster`, `skills/detect-anomaly`, `skills/visualize-chart` — kontrak tool tidak berubah.
- `seeknal_agent.yml` — salinan v5 verbatim.
- Seluruh halaman context lainnya — aturan lama tetap; halaman lama hanya menerima rute/guard kecil.

## Verifikasi yang mendasari (ringkas)

Semua aturan baru dicek langsung ke `staging` (13 Okt 2026): cakupan bridge distribusi (hanya
PBF/IFK/IFP), nilai `prekursor` (text, cakupan form Toko Obat), format `jenis_obat` (string JSON),
kunci `profil_sarana_json` (`ms_prekursor`, `ms_jenis_obat` — dasar aturan regional), keberadaan nilai
tanggal di luar rentang operasional, join kamus kategori via `master_data_id` beserta residu
varian/tertukar-tempat, dan kontrak negara (ejaan ganda + sentinel + kosong).

## Belum dikerjakan (sesi lanjutan)

- Linter L1–L12 + skrip manifes + uji "menemukan" atas snapshot ini.
- Batch pembanding testcase lama; batch testcase NPPZA (positif + anti-trap).

## Promosi (13 Okt 2026)

- **SELESAI** — dipromosikan ke folder hidup: `context/` (23 halaman), `SEEKNAL_ASK.md`, dan
  `seeknal/skills/bpom-analyst/SKILL.md`; hasil diverifikasi identik ke snapshot ini (`diff`/`cmp` kosong).
- Catatan lokasi skill: folder hidup memakai **satu lokasi** `seeknal/skills/` (tanpa `skills/` root);
  salinan `skills/` di snapshot identik isinya, jadi tidak ada yang hilang.
- Derivasi regional `13-10-2026 v2-regional` untuk `sipt-pemeriksaan-makasar` & `sipt-pemeriksaan-pekanbaru` — **SELESAI** (lihat CHANGELOG kedua snapshot regional, juga sudah dipromosikan).

## Perbaikan audit pasca-promosi (13 Okt 2026)

- `SEEKNAL_ASK.md` (live): label judul (v5) → **(v6)** — konten sudah memuat PAGE MAP 22/25 + R2 grain NPP sejak promosi; tidak ada perubahan aturan. Gate 5 skill live **tidak** mengalami duplikasi bullet (temuan itu hanya di varian regional).
- `context/80-waktu-dan-durasi.md` (live): blok "durasi perpindahan tahap" diperbaiki — `percentile_cont(0.5)` tanpa cast `double precision` (error PostgreSQL, cacat turunan v5), dan label "durasi" sebelumnya menghitung median timestamp, bukan durasi. Kini: `lag(created_at)` per kasus → median **hari** antar tahap; teruji jalan di `pemeriksaan_reader`.
- `context/97` · `SEEKNAL_ASK` · `skills/bpom-analyst|bpom-forecaster|detect-anomaly` (live): nama tool klarifikasi `request_clarification` → **`ask_clarification`** (nama tool runtime Seeknal); kunci config `agent.request_clarification` di agent.yml tidak diubah (namespace config ≠ nama tool).
