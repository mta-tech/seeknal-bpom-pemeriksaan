---
name: bpom-forecaster
description: "Forecasting skill for predicting future trends from any pemeriksaan time series. Computes projections deterministically from historical data with quality labels."
tags: [bpom, pemeriksaan, forecast]
version: "2.0.0"
---

# BPOM Forecaster (Trigger)

Routes BPOM forecast requests to `run_forecast`. This skill owns only the BPOM CAPTURE parameters —
all compute is deterministic (ETS seasonal fit inside the IBA forecast engine). The LLM does **no**
forecast arithmetic.

Load `context/00-menghitung.md` and `context/01-peta-data-dan-routing.md` first. This file covers only
the tool workflow.

## CAPTURE

Lock `{sql, periods}`.

- Default **table** = `fact_pemeriksaan`. Default series = total pemeriksaan.
- **Horizon translation:** `periods` is a step count on the SQL's own grain — monthly:
  6 bulan → 6, 1 tahun → 12, 3 tahun → 36, 5 tahun → 60 → capped at 36. When the request exceeds it,
  SAY in the answer that 36 months is the maximum supported horizon.
- **"hingga/sampai {X}"** = every step through the end of X, intermediate periods included.
  **Always pass `periods` explicitly.**
- **"bulan depan"** = the next **COMPLETE** month (the month after the running one), not the first
  forecast step.
- If the **series** is ambiguous → `request_clarification` first.

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

Default Y = `COUNT(DISTINCT id)`; default grain = monthly. No JOINs, no `generate_series`, no recursive
CTE (the tool rejects these). Univariate only.

**Date column:** `tgl_start` for the standard series. `created_at` for data-entry lag.
Never use `tgl_end` as the primary series date.

**Exclusions are mandatory:** `tgl_start >= '2020-01-01'` (drops early/edge dates) and
`is_data_uji IS NOT TRUE` (drops test data). Both come from `context/00-menghitung.md`.

## Series Registry

| Series | Filter |
|---|---|
| Total Pemeriksaan | none |
| Pemeriksaan Selesai | status = finished group (both finish codes) |
| Pemeriksaan TMK | `kesimpulan_balai_id` → kode TMK |
| Pemeriksaan MK | `kesimpulan_balai_id` → kode MK |
| Pemeriksaan KOSMETIK | `klasifikasi_id` → kamus komoditi (dengan `type`) |
| Pemeriksaan PANGAN | idem |
| Pemeriksaan OBAT | idem |
| Pemeriksaan DISTRIBUSI | golongan `parent_name` = Distribusi |
| Pemeriksaan PELAYANAN | golongan `parent_name` = Pelayanan |
| Pemeriksaan PRODUKSI | golongan `parent_name` = Produksi |
| Temuan produk per bulan | dari `bridge_pemeriksaan_temuan`, `COUNT(DISTINCT pemeriksaan_id)`, `is_kasus_draft = false` |

Resolve every code from `context/` — never from memory. A code that lives in the dictionary needs its
`type`; a status needs `domain='pemeriksaan'`; a kesimpulan needs the FK join.

## RUN

Call `run_forecast(sql, periods)`. Do NOT compute forecast numbers yourself.

- **After a clarification is answered**, call `run_forecast` FRESH this turn. Numbers in the answer
  MUST come from a `run_forecast` result produced **this turn**.
- `## Kesalahan` with "policy check" → the SQL has a forbidden pattern; rebuild flat per the template.
- `## Kesalahan` with "EXECUTE" → runtime error; recheck the template and retry corrected.
- `## Ditolak` → present the engine's reason and offer the historical trend instead.

## PRESENT

Read the tool's markdown and compose prose around it. Lead with the quality label. Never show raw
`sigma`/`sub_type`/field names/CV numbers.

**Present the full computed horizon.** Every predicted period the tool returned appears in the answer.

**Two panels rule:** if the request covers both pelayanan and produksi, run **two** series and present
them as two labelled sections — never one merged projection, because the units differ.

**Anomaly:** if the markdown has an `## Anomali` block, include it and state the points were **not
removed**. If the user asks about anomalies directly, call `detect_anomaly(sql)` yourself.

**CSV:** on a SUCCESSFUL forecast, `run_forecast` self-uploads ONE combined CSV (history + projection).
**Do NOT call `upload_to_s3` yourself.** Only on a refused/failed forecast, when you fall back to a
historical trend, may you export the history.

## Stock vs flow

| Question pattern | Kind | Y expression |
|---|---|---|
| "pemeriksaan baru/selesai per bulan" | flow | `COUNT(DISTINCT id)` |
| "total pemeriksaan aktif/akumulasi" | stock | `SUM(COUNT(DISTINCT id)) OVER (ORDER BY date_trunc(...))` |

For stock series the fit may drift — say so.

## Hard rules

- **Never use `execute_python` for forecast arithmetic.** `run_forecast` is the single deterministic source.
- **Follow-up consistency:** reuse the exact SQL from the prior turn for the same series.
- **If the projection ran but its chart did not render**, the numbers still stand: present them in
  words and note the chart could not be shown — never re-run to force the visual.
- **Same question → same SQL:** resolve the series from the registry exactly.
- **Consistency contract:** same question (same series, grain, horizon) → same numbers in any session.
  Any difference means a different SQL or `periods`.
- **Custom series:** build from the template, and document the filter in the answer.
