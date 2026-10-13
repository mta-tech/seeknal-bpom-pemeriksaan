# CHANGELOG — `14-10-2026 v7-nasional`

**Tanggal:** 14 Oktober 2026
**Turunan:** `13-10-2026 v6-nppza`
**Verifikasi:** live `staging` via `pemeriksaan_reader` · diff live≡snapshot kosong

## Dasar perubahan

Potongan dari folder aktif **setelah audit pasca-promosi** (PR #2 ter-merge ke `main`). Tidak ada aturan baru — isi snapshot = live per 14 Okt 2026.

## Perbaikan pasca-promosi yang termuat (vs v6-nppza)

1. `context/80` — blok "durasi perpindahan tahap" diperbaiki:
   - `percentile_cont(0.5)` tanpa cast → **error**; kini `0.5::double precision`;
   - label "durasi" sebelumnya menghitung median timestamp; kini `lag(created_at)` per kasus → median **hari** antar tahap.
2. `context/97` · `SEEKNAL_ASK.md` · `skills/bpom-analyst` · `bpom-forecaster` · `detect-anomaly` — nama tool klarifikasi `request_clarification` → **`ask_clarification`** (nama tool runtime).
3. `SEEKNAL_ASK.md` — label versi `(v5)` → `(v6)`.
4. `seeknal_agent.yml` — harness ERBA-aligned: `tool_call_limit: 40`, `temperature: 0.5`, `read_max_lines: 200`.
5. `scripts/lint_context.py` — expected set 23 halaman (v6: +22/+25) + skip inline-code pada L8.

## Yang sengaja TIDAK berubah

- 21 halaman lama + halaman 22/25 — aturan tetap; hanya menerima perbaikan di atas.
- `skills/visualize-chart`, kontrak tool forecast/anomaly/S3 — tidak berubah.
- Arsitektur varian routing (`flag_varian_datas`) — tidak berubah.

## Belum dikerjakan (sesi lanjutan)

- UAT smoke lewat agent hidup (end-to-end, bukan lagi uji manual).
- Batch testcase NPPZA (positif + anti-trap).
