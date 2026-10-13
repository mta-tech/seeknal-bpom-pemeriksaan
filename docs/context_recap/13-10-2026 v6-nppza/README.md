# Varian `13-10-2026 v6-nppza` — context & skill nasional (+ kebutuhan NPPZA)

**Dibuat:** 13 Oktober 2026
**Turunan dari:** `24-09-2026 v5-staging-based` (disalin utuh, `.seeknal/` & `target/` sandbox tidak dibawa)
**Sumber kebutuhan:** `docs/blueprint_kebutuhan_user/10-blueprint-nppza-ekspor-impor-keamanan-mutu.md` (revisi 13 Okt 2026) + blueprint 03–09
**Status:** snapshot siap linter/UAT — **belum dipromosikan** ke `context/` + `seeknal/skills/` hidup.

---

## 1. Mengapa varian ini ada

Blueprint NPPZA (narkotika, psikotropika, prekursor, ekspor-impor, keamanan mutu) memetakan kebutuhan
user yang **belum diajarkan ke context hidup**: dua bridge distribusi, kolom profil faskes, variasi kode
temuan, kontrak negara, dan batas domain obat-berkontrol. Varian ini menutupnya dengan prinsip yang
sama dengan v5: **context mengajarkan cara menemukan, bukan melafalkan jawaban** — tanpa angka hasil
query, tanpa istilah domain RPO.

## 2. Apa yang berubah dari v5

| Artefak | Perubahan |
|---|---|
| `context/22-komoditi-pbf-dan-fokus.md` | **baru** — dua bridge distribusi (`komoditi_pbf`, `fokus_pbf`), grain "kasus yang mengelola" vs kasus klasifikasi, join `master_data_id::text` + `type`, cakupan PBF/IFK/IFP dibuktikan lewat query |
| `context/25-profil-sarana-faskes.md` | **baru** — `profil_faskes.prekursor` (text `'t'/'f'`, cakupan form) & `jenis_obat` (TEXT ber-JSON → parse, kamus `JENIS_OBAT_KELOLA`), personel faskes |
| `context/20-komoditi.md` | rute grain kedua ke `22`; baris keputusan "NPP di distribusi" |
| `context/40-temuan-produk.md` | variasi kode: alias/varian ketik, kode tindakan tertukar tempat, bucket eksplisit; "keamanan mutu" = kelompok kode TMS KMG + bahan berbahaya |
| `context/41-nilai-dan-negara.md` | kontrak **tiga bucket** negara (lokal / tidak tercatat / impor); proxy prefix `ML`/`MD` dengan disclaimer |
| `context/60-mutu-dan-tindak-lanjut.md` | pencarian narasi wajib **prefiks** (`narkotik%`, `psikotrop%`, …); CAPA "ekspor" praktis tak terpakai |
| `context/80-waktu-dan-durasi.md` | guard rentang operasional (nilai sebelum 2020 & jauh di masa depan ada) |
| `context/95-batas-domain.md` | +zat adiktif, permit/awal impor, re-ekspor, atribut importir (semuanya honest gap) |
| `context/97-glossary-istilah-user.md` | +PKM (Puskesmas vs keamanan mutu), NPP/NPPZA, keamanan mutu, obat keras, ekspor impor |
| `SEEKNAL_ASK.md` | PAGE MAP +baris `22`/`25`, pemicu diperluas; R2 +grain NPP & istilah ambigu |
| `skills/bpom-analyst` | +2 bullet Gate 5 (dua grain NPP; kanonik kode temuan) |
| `audit_context/02-spec-context-halaman.md` | matriks halaman 21 → 23 + kepemilikan (di folder spesifikasi, bukan di snapshot) |

## 3. Prinsip yang dipegang (sama dengan v5)

1. Context mengajarkan **cara menemukan** — tanpa angka hasil query; kode domain boleh ditulis asal
   disertai jalur pencariannya.
2. Satu aturan satu pemilik: bridge distribusi = `22`, profil faskes = `25`, sisanya tetap di halaman
   lama yang hanya menerima rute/guard.
3. Manifes tiap halaman → skrip verifikasi bisa membuktikan ke database.
4. Karantina eksplisit (`90`) tetap berlaku; tidak ada larangan tanpa pengganti.

## 4. Verifikasi yang mendasari (live `staging`, 13 Okt 2026, akun `pemeriksaan_reader`)

Bridge komoditi/fokus hanya milik kasus PBF/IFK/IFP; `prekursor` hanya terisi pada form Toko Obat
(text `'t'/'f'`); `jenis_obat` = string JSON; `profil_sarana_json` memuat kunci `ms_prekursor` &
`ms_jenis_obat` (jadi aturan regional view tetap mungkin); `tgl_start` punya nilai di luar rentang
operasional (2018–2019, 2027); kamus kategori temuan terjoin via `master_data_id` dengan residu
varian/tertukar-tempat yang wajib di-bucket; label CAPA "Re-Ekspor" ada tapi nyaris tak terpakai.

Rincian angka: blueprint 10 §2 & §4.1 (angka **tidak** disalin ke context, sesuai aturan linter).

## 5. Item tertunda

| Item | Status |
|---|---|
| Linter L1–L12 + skrip manifes atas snapshot ini | sebelum promosi |
| Uji "menemukan" (pertanyaan NPPZA harus membuka `22`/`25`) | sebelum promosi |
| Batch pembanding testcase lama + batch NPPZA baru | setelah linter |
| Promosi ke `context/` + `seeknal/skills/` hidup | menunggu persetujuan |
| Derivasi regional `v2-regional` (makassar, pekanbaru) | dari snapshot ini |

## 6. Cara memakai

- Bandingkan dengan baseline: `--variants-path docs/context_recap --variants "13-10-2026 v6-nppza"`.
- Snapshot lama (`v5-staging-based`, `after-insight-*`) **tidak disentuh** — arsip perbandingan.
