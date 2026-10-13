# Snapshot `14-10-2026 v7-nasional` — context & skill nasional pemeriksaan

**Tanggal potong:** 14 Oktober 2026
**Turunan:** `13-10-2026 v6-nppza` + perbaikan pasca-promosi (ter-merge ke `main` via PR #2)
**Sumber:** folder aktif (live) `seeknal-bpom-pemeriksaan`

## Status

Snapshot ini adalah **potongan langsung dari folder aktif** setelah seluruh perbaikan audit pasca-promosi selesai dan ter-merge ke `main`.

**Diverifikasi: live ≡ snapshot** — diff kosong untuk `context/`, `skills/`, `SEEKNAL_ASK.md`, dan `seeknal_agent.yml` (14 Okt 2026).

## Isi

```
14-10-2026 v7-nasional/
├── SEEKNAL_ASK.md        # orchestrator: scope akun + PAGE MAP (23 halaman)
├── seeknal_agent.yml     # harness: tool_call_limit 40, temperature 0.5, read_max_lines 200
├── context/              # 23 halaman
├── skills/               # 4 skill
└── seeknal/skills        # symlink -> ../skills
```

## Delta vs `v6-nppza`

| Artefak | Perubahan |
|---|---|
| `context/80-waktu-dan-durasi.md` | SQL durasi tahap diperbaiki: `percentile_cont(0.5::double precision)` + `lag(created_at)` → median **hari** (sebelumnya error PostgreSQL & salah makna) |
| `context/97` · `SEEKNAL_ASK.md` · `skills/bpom-analyst` · `bpom-forecaster` · `detect-anomaly` | nama tool klarifikasi `request_clarification` → `ask_clarification` |
| `SEEKNAL_ASK.md` | label versi `(v5)` → `(v6)` |
| `seeknal_agent.yml` | + harness: `tool_call_limit: 40`, `temperature: 0.5`, `read_max_lines: 200` |
| `scripts/lint_context.py` (repo, bukan snapshot) | expected set 23 halaman + skip inline-code pada L8 |

## Verifikasi

- Linter L1–L12: **LULUS** (23 halaman, 28 dokumen) — 14 Okt 2026.
- Identitas live ≡ snapshot: diverifikasi 14 Okt 2026.
