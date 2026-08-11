#PREDIKAT — RULES FOR ACCURATE COUNTING, STATUS FILTERS, KESIMPULAN, AND DATA QUALITY ON PEMERIKSAAN WAREHOUSE#

> **Single source of truth.** Reference this file. DO NOT recall literals from memory.
> Each rule appears **exactly once** — here.

---

## 1. Counting Method

The pemeriksaan tables are NOT versioned (unlike neo's registration tables). Each pemeriksaan
has one row in `mv_pemeriksaan` with a unique `id`. `COUNT(*)` and `COUNT(DISTINCT id)` return
the same number on the fact table.

| Entity | Method | Why |
|---|---|---|
| Pemeriksaan | `COUNT(DISTINCT id)` | One inspeksi = one `id`. DISTINCT preferred for clarity. |
| Temuan | `COUNT(DISTINCT id_pemeriksaan)` on temuan table | Counts pemeriksaan with findings, not individual products. |
| Produk temuan | `COUNT(*)` on temuan table | Each row = one product finding. |
| Petugas | `COUNT(DISTINCT petugas_id)` on petugas table | Unique petugas across all pemeriksaan. |
| Langkah | `COUNT(DISTINCT id_steps)` on log table | Each step is unique (99.995%). |

**Default for "berapa pemeriksaan":** `COUNT(DISTINCT id)` on `mv_pemeriksaan`.

**For child tables:** always use `COUNT(DISTINCT id_pemeriksaan)` when the question is about
how many pemeriksaan, not how many records. "Berapa pemeriksaan yang punya temuan" =
`COUNT(DISTINCT id_pemeriksaan)` on `mv_pemeriksaan_temuan`, never `COUNT(*)`.

---

## 2. Date Column Choice

| Entity | Correct column | Wrong columns |
|---|---|---|
| Kapan inspeksi dilakukan | `tanggal_mulai` | `tanggal_input` (kapan data dimasukkan) |
| Kapan inspeksi selesai | `tanggal_selesai` | `day_mulai_selesai` (durasi, bisa outlier) |
| Kapan data dimasukkan | `tanggal_input` | `tanggal_mulai` (waktu inspeksi) |
| Durasi inspeksi | `day_mulai_selesai` | `day_input_mulai` (bukan durasi inspeksi) |

`day_input_mulai` dan `day_input_selesai` punya outlier ekstrem (max 736.685 hari). Jangan
gunakan untuk filtering. `day_mulai_selesai` lebih bersih tapi masih punya max 34.706.

**Default date column:** `tanggal_mulai` untuk pertanyaan tentang "kapan inspeksi".

---

## 3. Status Filter (Workflow Stage)

**Status tier follows the question's verb:**

| Verb | Filter |
|---|---|
| "Selesai" / "finished" | `status IN ('FINISHED', 'FINISHED_PUSAT')` |
| "Dalam proses" / "active" | `status NOT IN ('FINISHED', 'FINISHED_PUSAT')` |
| "Draft" | `status IN ('DRAFT', 'DRAFT_REVISE', 'DRAFT_PUSAT', 'DRAFT_PUSAT_REVISE')` |
| "Dalam verifikasi" | `status LIKE 'VERIFY%'` |
| "Dikembalikan" | `status IN ('DRAFT_REVISE', 'DRAFT_PUSAT_REVISE')` |
| Specific stage | `status = '<exact code>'` |

**Pipeline normal:** DRAFT -> VERIFY1 -> VERIFY3 -> VERIFY4 -> FINISHED
**Pipeline with revision:** DRAFT -> VERIFY1 -> DRAFT_REVISE -> VERIFY1 -> ...
**Pipeline pusat:** DRAFT_PUSAT -> VERIFY_P1 -> VERIFY_P2 -> VERIFY_P3 -> FINISHED_PUSAT

"Total pemeriksaan" = ALL statuses (no filter needed).

---

## 4. Kesimpulan Filter (Inspection Result)

| Verb | Filter |
|---|---|
| "Memenuhi" / "compliant" | `kesimpulan = 'MK'` |
| "Tidak memenuhi" / "non-compliant" | `kesimpulan = 'TMK'` |
| "Bermasalah" / "with issues" | `kesimpulan IN ('TMK', 'TTP', 'TDP', 'TMBB')` |
| "Tindak pidana" | `kesimpulan = 'TTP'` |
| "Total" / "semua" | No kesimpulan filter |
| "Belum ada kesimpulan" | `kesimpulan IS NULL` |

**Never stack** kesimpulan filter on top of a status filter that already implies a specific
kesimpulan. If the question is "pemeriksaan selesai yang TMK", use both: `status IN ('FINISHED','FINISHED_PUSAT') AND kesimpulan = 'TMK'`.

---

## 5. Grade Filter

| Verb | Filter |
|---|---|
| "Grade A" | `grade = 'A'` |
| "Grade B" | `grade = 'B'` |
| "Grade C" | `grade = 'C'` |
| "Ada grade" | `grade IS NOT NULL AND grade != 'N/A'` |
| "Tidak ada grade" | `grade IS NULL OR grade = 'N/A'` |

Grade HANYA diisi untuk ~20% pemeriksaan. Sertifikasi tidak punya grade.
83% pemeriksaan punya grade NULL. NULL ≠ grade terburuk.

---

## 6. Komoditi Filter

| Verb | Filter |
|---|---|
| "Obat" | `komoditi = 'OBAT'` |
| "Pangan" | `komoditi = 'PRODUK PANGAN'` |
| "Kosmetik" | `komoditi = 'KOSMETIK'` |
| "Obat tradisional" | `komoditi = 'OBAT TRADISIONAL'` |
| "Suplemen" | `komoditi = 'SUPLEMEN KESEHATAN'` |
| "Semua obat" | `komoditi IN ('OBAT','NARKOTIKA','PSIKOTROPIKA','OBAT OBAT TERTENTU','PREKURSOR','BAHAN BAKU OBAT','BAHAN OBAT')` |
| "Mapping ke target" | `mapping_komoditi_target_balai = '<target value>'` |

Gunakan `komoditi` di `mv_pemeriksaan` (UPPER CASE) untuk filter.
Gunakan `mapping_komoditi_target_balai` untuk join ke `target_balai`.

---

## 7. Default Scope (when user doesn't specify)

| Missing | Default |
|---|---|
| **Year** | ALL-TIME: `tanggal_mulai >= '2020-01-01'`. Present total + per-year breakdown. |
| **Kesimpulan** | NO DEFAULT — you must clarify or show all. |
| **Status** | NO DEFAULT — show all unless the verb implies a tier. |
| **Result limit** | Top 10. Always state the total when truncating. |

A year or range stated by the user always overrides the default.

---

## 8. Exclusions (mandatory on every count query)

| Filter | SQL |
|---|---|
| Outlier tanggal | `tanggal_mulai >= '2015-01-01'` |
| Future tanggal | `tanggal_mulai <= CURRENT_DATE` OR `tanggal_mulai IS NOT NULL` |
| DEMO data | `nama_upt NOT IN ('DEMO BALAI BESAR', 'DEMO TIPE A')` |
| NULL tanggal guard | `tanggal_mulai IS NOT NULL` when grouping without date range |
| Orphan timeline | `EXISTS (SELECT 1 FROM mv_pemeriksaan p WHERE p.id = t.id_pemeriksaan)` |

The 14 outlier dates (0004, 0020, 1922-1928, 1970) and 2 future dates (2027) are data errors.
The 3 DEMO rows are test data. Always exclude them.

---

## 9. Cast Rules

**All columns in `mv_pemeriksaan` are native types** — no cast needed.
- `id`: bigint
- `nama_upt`, `nama_sarana`, `provinsi`, `kabupaten_kota`: text
- `tanggal_input`, `tanggal_mulai`, `tanggal_selesai`: date
- `day_input_mulai`, `day_input_selesai`, `day_mulai_selesai`: bigint
- `tx_critical_issue`, `tx_major_issue`, `tx_minor_issue`: integer
- `tp_harga`, `tp_harga_total`: numeric(38,9)

**No ERBA-style TEXT columns requiring cast.** This is a clean PostgreSQL database.

---

## 10. JOIN Template

```sql
-- Basic pemeriksaan count
SELECT COUNT(DISTINCT id) FROM mv_pemeriksaan
WHERE tanggal_mulai >= '2020-01-01'
  AND nama_upt NOT IN ('DEMO BALAI BESAR', 'DEMO TIPE A');

-- Pemeriksaan with temuan
SELECT p.kesimpulan, COUNT(DISTINCT p.id) AS jml_pemeriksaan
FROM mv_pemeriksaan p
WHERE p.tanggal_mulai >= '2020-01-01'
  AND p.nama_upt NOT IN ('DEMO BALAI BESAR', 'DEMO TIPE A')
  AND EXISTS (SELECT 1 FROM mv_pemeriksaan_temuan t WHERE t.id_pemeriksaan = p.id)
GROUP BY 1;

-- Pemeriksaan with target (via mapping)
SELECT p.kesimpulan, COUNT(DISTINCT p.id)
FROM mv_pemeriksaan p
WHERE p.mapping_komoditi_target_balai = 'OBAT'
  AND lower(p.nama_upt) IN (SELECT lower(nama_balai) FROM target_balai)
GROUP BY 1;
```

---

## 11. execute_sql

- **One statement per call.** No `;` — multi-statement SQL is rejected.
- **No `EXTRACT(YEAR ...)` to filter** — use a bounded range on `tanggal_mulai`.
- Prefer filters that push down: code equality is cheap; `ILIKE '%...%'` scans the whole column.
- JOINs are allowed but must be justified — no blind JOINs to child tables unless the question
  requires data from them.

---

## 12. Answer Contract — canonical interpretation + number provenance

Every answer takes a POSITION and shows its EVIDENCE:

**A. Answer with the canonical interpretation.** A term means what this file and
`filter_code_reference.md` define — lead with ONE decisive number under that definition.

**B. Attach the number's provenance.** Every headline number is accompanied by:
- its source (which table, which filter);
- the counting entity (`id` / `id_pemeriksaan` / `petugas_id`);
- the date range applied;
- any exclusions applied.

**C. Time breakdown is part of the default answer shape.** An aggregate answer shows:
total -> per-code breakdown -> a period x category table (rows = year).

**D. Proportionality.** A narrow question gets a direct answer + provenance. Decompose when
the question spans a family.

**D2. Wording.** Use the canonical business term; a natural synonym is fine.

**D3. Zero is an answer.** When a correct query returns no rows, say "tidak ada / tidak ditemukan".

**E. Hygiene is applied, never spotlighted.** Exclusions, DEMO filters: always applied, never
called out as their own bolded line. If a methodology footnote is warranted, the exclusion
fact may ride along as ONE plain bullet inside that list.

**F. Consistency.** The same question MUST produce the same answer — in this session, in a
new session, and in follow-ups. Canonical resolution is deterministic: same wording -> same
interpretation -> same SQL shape -> same numbers. The only legitimate difference is data drift
— stamp the as-of date.
