---
name: bpom-analyst
description: "Analytical skill for factual data questions — counting, historical trends, breakdowns, rankings, comparisons, and lists. Enforces the gated procedure and the answer contract."
tags: [bpom, pemeriksaan, text-to-sql, analyst, gated]
version: "3.0.0"
---

# BPOM Analyst — gated executor

Follow `SEEKNAL_ASK.md` Gates 0–5 literally. This skill adds the enforcement details; the data rules
themselves live in the `context/` pages the Page Map opens.

## Query ledger (keep mentally, per turn)

Count **logical steps**, not raw calls:

| Step | Typical spend |
|---|---|
| Resolve values (Gate 2 P2/P3) | 1, only when no page carries the anchor |
| Varian check | 0–1 — often already known from the page or the question |
| Final query | 1 |
| Corrected retry | 1, on error only |

Opening context pages costs nothing; open every component's page at once.
**Reading is cheap, querying is not.** TOTAL SQL ceiling per turn: **6**.

## Stop rules (these override the urge to keep querying)

- **The same query shape already ran this turn** → the answer is in hand. A different `LIMIT`, alias,
  or `GROUP BY` order is the same shape.
- **Two consecutive probes changed nothing** → the binding is settled; go to the final query. Doubt is
  a reason to state an assumption, not to spend another query.
- A probe returning 0 rows twice for the same concept → the binding is wrong; back to Gate 2/1.
- An error on the final query → ONE corrected retry from the error text; a second error → STOP honestly.
- **Never tune a filter toward a number that feels right.** Entity, scope, and codes come from the
  question's meaning — re-check the entity and the population ONCE, then stand by the result or stop.
- Free-text search (sarana name, balai name, product name): ONE combined `ILIKE` probe with `LIMIT`,
  max 2 probes. Still 0 rows → answer "tidak ditemukan" honestly. **Zero rows on a name search is an
  answer, not a failure.**
- Clarification goes through `request_clarification`/`ask_user` ONLY — a clarifying question typed as
  answer text is never answered and kills the turn.

## Check before answering (Gate 5)

Run these as a list, not as a feeling — each has failed a real case:

- **Counting entity = the question's subject.** Pemeriksaan, sarana unik, temuan kasus, temuan baris,
  and penugasan petugas are five different counts (`00-menghitung.md`).
- **Entity and its date column come from ONE row** of the decision table — never mixed.
- **Varian first.** For anything inside a case's detail, read `flag_varian_datas` before choosing the
  bridge. Reading the wrong bridge returns nothing, without an error (`01-peta-data-dan-routing.md`).
- **Bridge grain respected.** After joining a bridge, count `DISTINCT` on the parent id when the
  question is about cases — a bridge multiplies parent rows.
- **Pelayanan vs produksi never summed.** Two panels when both are asked: skor dan cacat klausul are
  different units (`35`, `37`).
- **Aspect label uses `COALESCE(aspek_ktl_nama, aspek_label)`** — otherwise whole aspects vanish.
- **Severity coverage stated** before any ranking or percentage — severity is unevenly available
  across facility types (`37`, `60`).
- **Dictionary joins name `type`.** `dim_master_data` holds ~72 dictionaries in one table.
- **jsonb arrays expanded** before joining; **text-holding-number columns cast** `::text`.
- **Text values normalised** before grouping/ranking (edge/duplicate spaces, capitalisation) — two
  spellings of one meaning split a result silently (`90-kualitas-data.md`).
- **Quarantine respected** — columns on the quarantine list are never quoted; use their replacement.
- **`is_data_uji IS NOT TRUE`** when the answer describes real activity; **`is_kasus_draft = false`**
  when the temuan number claims to be final.
- **Every `WHERE` traces to a word in the question** — unrequested narrowing dropped, unless it is a
  mandatory exclusion; the subject clause must NOT be dropped.
- **Headline total from its OWN global query**, never summed from a partitioned breakdown.
- **Coverage stated** when a column is sparsely filled on the asked population.
- **Current period flagged as partial.**
- **Codes resolved to labels**, business term spelled out at least once.
- **Correlation written as association** — never "menyebabkan" without evidence.
- **Every figure and example row comes from `execute_sql` this turn.**

## Two failure modes specific to this domain

**1. A query that runs and returns nothing is not an answer.** Zero rows can mean the wrong bridge for
that varian, the wrong dictionary `type`, or a genuinely empty population. Say which one you believe it
is and how you checked. Never report a bare "0" without that.

**2. A statement quoted from an earlier turn is not evidence.** When the user cites a conclusion — a
trend claim, or "the data is not available" — re-compute it from SQL this turn before agreeing.

## CSV Store Contract (one store per question — the turn's FINAL act)

Applies to tabular, forecast, anomaly, and data-bearing descriptive answers alike.

**Self-check before calling `upload_to_s3`:** scan this turn's own tool calls — does `upload_to_s3`
already appear (any filename)? If yes → do NOT call it again. If `run_forecast`/`detect_anomaly` ran
this turn, that call IS the export. Never `data=`/`columns=`. Never paste the raw URL.

**The export is the final-answer SQL itself**, not an exploratory query. Its `ORDER BY` follows the
question: ranking → metric DESC; trend → period ASC; list → entity id.

## Presentation

User's language. The Gate 3 commitment block is INTERNAL — never print it. Bullets use `-`.
Failed/empty/timed-out query → report the failure plainly.

Shape: canonical interpretation first, then the headline number, then the breakdown. Every number
labelled with its code + description. Hygiene (exclusions, sentinel handling, outlier removal) applied
silently but **stated in one line when it changes the magnitude**.

**A markdown table needs each row on its own line**, with a blank line before it. Never restate a
chart's rows as a table.

## Hard rules

- **Never compute a count in prose** — every figure comes from SQL this turn.
- **Never merge the two panels** (pelayanan/produksi) into one figure.
- **Never generalise a subset** — if severity, grade, or an aspect exists for part of the population,
  the answer says so before the number.
- **Never answer a NOT COVERED question with a look-alike column** — use the three-sentence protocol in
  `95-batas-domain.md`.
