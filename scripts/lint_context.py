#!/usr/bin/env python3
"""Linter context/skill variant Pemeriksaan (L1-L12).

Pakai:
    python3 scripts/lint_context.py "docs/context_recap/24-09-2026 v5-staging-based"

Read-only. Tidak menyentuh database. Keluar dengan kode 1 bila ada pelanggaran.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

FORBIDDEN_SCHEMA = [
    "mv_pemeriksaan", "tanggal_mulai", "tanggal_input", "tanggal_selesai", "nama_upt",
    "mv_pemeriksaan_agg", "mv_pemeriksaan_log", "mv_pemeriksaan_timeline",
    "target_balai", "coverage_balai", "mv_kriteria_pemeriksaan",
]

FORBIDDEN_RPO = [
    "jenis_permohonan", "kategori_dokumen", "status_produk",
    "daerah_pabrik", "daerah_trader", "ERBA", "ERLA",
]
# Catatan: 'produk_id' TIDAK dilarang — itu kolom sah di dim_produk domain ini.
# 'NIE' juga tidak dilarang: halaman 95-batas-domain memang mengarahkannya ke domain lain.

SKILLS_IN_PAGE = ["bpom-analyst", "visualize-chart", "bpom-forecaster", "detect-anomaly"]

MAX_LINES = 200


def strip_fences(text: str) -> str:
    """Buang blok kode berpagar (SQL boleh memuat angka)."""
    return re.sub(r"```.*?```", "", text, flags=re.S)


def body_without_manifest(text: str) -> str:
    """Buang tabel Manifes (literal nilai memang boleh ada di sana)."""
    return re.split(r"^##\s+Manifes", text, flags=re.M)[0]


def is_result_number(tok: str) -> bool:
    """Angka hasil: >=3 digit, bukan tahun (19xx/20xx), bukan bagian kode/desimal/ribuan berkonteks."""
    if len(tok) < 3:
        return False
    if re.fullmatch(r"(19|20)\d\d", tok):
        return False
    return True


def lint(target: Path) -> int:
    problems: list[str] = []
    ctx_dir = target / "context"
    ask = target / "SEEKNAL_ASK.md"
    skills_dir = target / "skills"

    pages = sorted(ctx_dir.glob("*.md")) if ctx_dir.is_dir() else []
    all_docs = pages + ([ask] if ask.exists() else [])
    all_docs += sorted(skills_dir.rglob("SKILL.md")) if skills_dir.is_dir() else []

    if not pages:
        problems.append(f"L0 tidak ada halaman di {ctx_dir}")

    # L1 / L2 — istilah terlarang
    for f in all_docs:
        txt = f.read_text()
        for term in FORBIDDEN_SCHEMA:
            if term in txt:
                problems.append(f"L1 {f.name}: memuat skema lama '{term}'")
        for term in FORBIDDEN_RPO:
            if re.search(rf"\b{re.escape(term)}\b", txt):
                problems.append(f"L2 {f.name}: memuat istilah domain lain '{term}'")

    # GLOBAL — daftar 21 halaman wajib
    expected = {
        "00-menghitung", "01-peta-data-dan-routing", "05-filter-katalog", "10-sarana-dan-fasilitas",
        "15-tujuan-pemeriksaan", "20-komoditi", "30-kesimpulan", "31-status-dan-alur",
        "35-kepatuhan-aspek", "37-klausul-dan-severity", "40-temuan-produk", "41-nilai-dan-negara",
        "45-observasi-dan-vaksin", "50-jenis-pangan", "60-mutu-dan-tindak-lanjut", "70-petugas",
        "80-waktu-dan-durasi", "85-target-capaian", "90-kualitas-data", "95-batas-domain",
        "97-glossary-istilah-user",
    }
    found = {p.stem for p in pages}
    for miss in sorted(expected - found):
        problems.append(f"L10 halaman wajib hilang: {miss}")
    for extra in sorted(found - expected):
        problems.append(f"L10 halaman tak terdaftar: {extra}")

    # per-halaman
    for p in pages:
        raw = p.read_text()
        lines = raw.splitlines()
        if len(lines) > MAX_LINES:
            problems.append(f"L7 {p.name}: {len(lines)} baris (> {MAX_LINES})")

        first_content = next((l.strip() for l in lines if l.strip()), "")
        is_trigger = "·" in first_content
        has_h1 = any(l.startswith("# ") for l in lines)
        if not has_h1:
            problems.append(f"L3 {p.name}: tanpa judul H1")
        if not is_trigger:
            problems.append(f"L3 {p.name}: tanpa baris pemicu (trigger words dipisah '·')")

        for need, code in (("## Rute", "L4"), ("## Jebakan", "L5")):
            if need not in raw:
                problems.append(f"{code} {p.name}: bagian '{need[3:]}' tidak ada")

        has_probe = "```sql" in raw and (
            "SELECT DISTINCT" in raw or "information_schema" in raw or "GROUP BY" in raw
        )
        if not has_probe:
            problems.append(f"L6 {p.name}: tanpa jalur penemuan (probe SQL: DISTINCT / GROUP BY / information_schema)")

        scan = body_without_manifest(strip_fences(raw))
        for ln, line in enumerate(scan.splitlines(), 1):
            for tok in re.findall(r"\b\d{3,}\b", line):
                if not is_result_number(tok):
                    continue
                # lewati angka yang jelas bersifat penjelasan, bukan hasil hitung:
                # rentang ("0–100"), persentase ("> 100%"), dan angka berkoma-ribuan dari kode
                if re.search(rf"[–-]\s*{tok}\b", line) or re.search(rf"\b{tok}\s*[–-]", line):
                    continue
                if re.search(rf"\b{tok}\s*%", line):
                    continue
                problems.append(f"L8 {p.name}:{ln}: angka hasil '{tok}' -> {line.strip()[:70]}")

    # L9 — tabel keputusan identik di 2 halaman
    seen: dict[str, str] = {}
    for p in pages:
        for m in re.finditer(r"^\|.+\|\s*$\n^\|[-|: ]+\|\s*$\n((?:^\|.+\|\s*$\n)+)", p.read_text(), re.M):
            key = m.group(1)[:200]
            if key in seen and seen[key] != p.name:
                problems.append(f"L9 tabel identik di {seen[key]} dan {p.name}")
            seen.setdefault(key, p.name)

    # L11 — inventaris skill vs isi folder
    if ask.exists():
        txt = ask.read_text()
        for s in SKILLS_IN_PAGE:
            if s not in txt:
                problems.append(f"L11 {s}: tidak disebut di SEEKNAL_ASK.md")
    if skills_dir.is_dir():
        on_disk = {d.name for d in skills_dir.iterdir() if d.is_dir()}
        for miss in sorted(set(SKILLS_IN_PAGE) - on_disk):
            problems.append(f"L11 folder skills/ tidak punya: {miss}")
        for extra in sorted(on_disk - set(SKILLS_IN_PAGE)):
            problems.append(f"L11 skill yatim di folder: {extra}")
    else:
        problems.append("L11 folder skills/ tidak ada")

    # L12 — traceability (dokumen spesifikasi)
    spec = Path(__file__).resolve().parent.parent / "docs" / "audit_context" / "02-spec-context-halaman.md"
    if spec.exists():
        spec_txt = spec.read_text()
        for p in pages:
            if p.stem not in spec_txt:
                problems.append(f"L12 {p.name}: tidak muncul di matriks traceability")

    print(f"== linter context: {target} ==")
    print(f"halaman: {len(pages)} · dokumen diperiksa: {len(all_docs)}")
    if problems:
        print(f"\nPELANGGARAN ({len(problems)}):")
        for pr in problems:
            print(f"  - {pr}")
        return 1
    print("\nSEMUA PEMERIKSAAN LULUS ✅")
    return 0


if __name__ == "__main__":
    tgt = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "docs/context_recap/24-09-2026 v5-staging-based")
    sys.exit(lint(tgt))
