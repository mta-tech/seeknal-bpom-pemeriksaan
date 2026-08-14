---
name: bpom-analyst
description: "Analytical skill for factual data questions — counting, historical trends, breakdowns, rankings, comparisons, and lists. Uses structured gates with SQL budget control."
tags: [bpom, pemeriksaan, text-to-sql, analyst, gated]
version: "1.0.0"
---

# BPOM Analyst — gated executor

Follow `SEEKNAL_ASK.md` Gates 1-5 literally. This skill adds the enforcement details.

## Budget ledger (keep mentally, per turn)
- Dictionary lookups: max 2 — a P2 category listing or a P3 scoped-label ILIKE (Gate 2 paths)
  each count as one.
- Discovery/verification SQL: max 2.
- Final SQL: 1. Corrected retry: 1.
- TOTAL SQL ceiling per turn: **6**. Reaching the ceiling without a defensible number = STOP and
  report honestly (what resolved, what failed, which single decision is missing).

## Stop rules (these override the urge to keep querying)
- A probe returning 0 rows twice for the same concept -> the binding is wrong; go back to
  Gate 2/Gate 1, do not brute-force variations.
- An error on the final query -> ONE corrected retry, informed by the error text. A second error
  -> STOP honestly.
- If the expected magnitude and the result differ wildly, do not "search" for a number that
  feels right — re-check the counting entity and population filter once, then either stand by
  the result or stop honestly. Never tune filters toward an expected number.
- Free-text search (nama_balai, nama_sarana): try a coded column first; only then ONE combined query
  with ILIKE and a LIMIT, max 2 probes total. Still 0 rows -> answer "tidak ditemukan" honestly.
- Clarification goes through `request_clarification`/`ask_user` ONLY — a clarifying question
  typed as plain answer text is never answered and kills the turn.
- A count question on a populated concept expects at least one counting query — if the plan ends
  with none, re-check the entity and population once before answering rather than stopping short.
- On a follow-up, read the earlier turns first: carry over the settled subject, scope, time
  range, and resolved codes, and change only what this turn names.

## CHECK before answering (Gate 5)
Run these as a list, not as a feeling — each one has failed a real case:

- **Counting entity = question subject**, and the same rule holds for every code family.
- **The code set is closed.** Compound concepts take every member from the reference or from
  a full category read. Never the first single-keyword ILIKE hit.
- **Headline total came from its OWN global DISTINCT query**, never summed from a partitioned
  breakdown.
- **Status filter = the asked population.** Never stack filters that erase what was asked about.
- **Exclusions applied** — DEMO data, outlier dates, NULL-date guard.
- **The final SQL touches exactly the tables the settled scope implies.**
- **Codes resolved to labels**, with the business term spelled out at least once.

## CSV Store Contract (one store per question — the turn's FINAL act)
Applies to tabular, forecast, anomaly, and data-bearing descriptive answers alike.

The export is the LAST tool call of the turn: after the final evidence query and after Gate 5
passes, immediately before the answer.

**Self-check before calling `upload_to_s3`:** scan this turn's own tool calls so far — does
`upload_to_s3` already appear (any filename)? If yes -> do NOT call it again, the export already
happened, go straight to the answer. If `run_forecast`/`detect_anomaly` ran this turn, that
call IS the export — count it before adding another. Never an exploratory query, never
`data=`/`columns=`, never more than one per turn. Never paste the raw URL.

## Presentation
User's language. The Gate 3 commitment block is INTERNAL — never print it. Bullets use `-`.
Failed/empty/timed-out query -> report the failure plainly.
Shape the answer per the Answer Contract (`predikat.md` 12): canonical interpretation first,
every number labelled with its code + description, per-code split, and a period x category table
from ONE closing `GROUP BY` — hygiene applied silently.
