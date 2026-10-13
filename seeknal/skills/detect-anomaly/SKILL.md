---
name: detect-anomaly
description: "Anomaly detection skill for identifying unusual patterns in pemeriksaan time series. Detects outliers and explains data irregularities."
tags: [bpom, pemeriksaan, anomaly]
version: "2.0.0"
---

# Detect Anomaly (Trigger)

Routes BPOM anomaly/outlier questions to `detect_anomaly`. Sibling to `bpom-forecaster` — same series
registry, same SQL contract, but explains unusual periods instead of projecting future ones.

Load `context/00-menghitung.md` and `context/01-peta-data-dan-routing.md` first.

## CAPTURE

Lock `{sql}`.

- Default **table** = `fact_pemeriksaan`. Default series = total pemeriksaan.
- Build the SQL from the template with the series filter resolved from
  `context/` (dictionary `type`, status `domain`, kesimpulan FK).
- Use the same exclusions as forecast: `tgl_start >= '2020-01-01'` and `is_data_uji IS NOT TRUE`.
- If the **series** is ambiguous → `ask_clarification` first.

## SQL Template

```sql
SELECT date_trunc('month', tgl_start) AS x,
       COUNT(DISTINCT id)             AS y
FROM   public.fact_pemeriksaan
WHERE  tgl_start >= DATE '2020-01-01'
  AND  tgl_start < date_trunc('month', CURRENT_DATE)
  AND  is_data_uji IS NOT TRUE
  AND  <series filter, if any>
GROUP BY 1 ORDER BY 1
```

## RUN

Call `detect_anomaly(sql)`. Do NOT compute or guess anomalies yourself.

- `## Kesalahan` → SQL issue (forbidden pattern or runtime error); recheck and retry corrected.
- No anomalies found → say so plainly; never invent one.

## PRESENT

Read the tool's markdown and compose prose around it. State explicitly that flagged periods were
**not removed** — this tool explains, it does not clean. Never show raw `sigma`/internal field names.

**Two panels rule:** if the question spans pelayanan and produksi, run two series and present two
labelled sections — never one merged series, since the units differ.

**CSV (one store per question):** `detect_anomaly` does **not** self-upload. If the answer carries data,
call `upload_to_s3` exactly **once** with the same `sql`, as the turn's FINAL act.
**Self-check first:** does `upload_to_s3` already appear this turn? If yes, skip to the answer.
A "no anomalies found" narrative with no data → skip the export.

## Hard rules

- **Never use `execute_python`** for anomaly scoring — the engine is the deterministic source.
- **Follow-up consistency:** reuse the exact SQL for the same series.
- **Consistency contract:** same question re-asked (any session) → same SQL → same flags and numbers;
  only data drift may differ — stamp the as-of date. Each flagged period is its own labelled row
  (period, value, why it stands out).
- If the user also wants a projection, note that `run_forecast` covers it separately.
- **Custom series:** build from the template with the user's filter.
