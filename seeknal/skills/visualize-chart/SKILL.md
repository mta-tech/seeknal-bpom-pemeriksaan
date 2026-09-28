---
name: visualize-chart
description: "Chart skill. Decides when a chart helps, picks the type from the data shape, and renders exactly one chart per question."
tags: [chart, visualization, pemeriksaan]
version: "2.0.0"
---

# Visualize Chart (Trigger)

Routes chart requests to `visualize_chart`. Same SQL discipline, same filter and entity contract as the
analyst skill — it renders the answer's data instead of only tabulating it.

Load the project's context pages before building chart SQL, exactly as the analyst skill requires. A
chart built on the wrong bridge or the wrong code is not a chart problem — it is a wrong answer with a
picture attached.

## CAPTURE

Lock `{widget_type, widget_title, source of rows}`.

- The chart's rows are the **answer's own rows**. Never write a second, differently-filtered query.
- Column order is the axis contract: X first, Y second, optional series third.
- **A chart reads exactly three columns.** More than three is refused, not truncated.
- Title in the answer's language, describing the data rather than the request.

Pick the source by what the data *is*:

1. **The SQL you already ran** — the default; `sql=` reuses that exact cached result.
2. **The CSV this turn exported** — for values a query cannot return (e.g. a projection).
3. **`data=`+`columns=`** — last resort only.

**An export failure never cancels the chart.**

## Two-panel rule (domain-specific)

When the answer covers **pelayanan (skor per aspek)** and **produksi (cacat klausul)** together, they
are different units. Render **two separate charts** — one per panel — and never plot them on one axis
or sum them into a single series. The same applies to any answer that intentionally splits into panels
(`35-kepatuhan-aspek.md`, `37-klausul-dan-severity.md`).

## RUN

Call `visualize_chart(widget_type, widget_title, sql=...)` **once**, after the headline number is
settled — the chart draws the answer; it never comes before the counting query or stands in for it.

Trigger rules — **a chart is part of a data answer, not an extra**:

- **Any answer that carries data** gets exactly one chart, whether or not the user said "grafik".
- **Explicit request** → always chart; never answer with a table alone.
- **Skip only when there is nothing to draw**: definitional/explanatory answers, a single figure with
  nothing to compare, a record lookup or identifier listing, zero rows, or a shape no type fits.

Type selection:

| What the answer is about | Type |
|---|---|
| a trend over periods | `line_chart` |
| several trends over periods | `grouped_line_chart` |
| cumulative or volume over time | `area_chart` |
| comparison across categories | `bar_chart` |
| same categories split by a second dimension | `grouped_bar_chart` |
| categories with long labels | `horizontal_bar_chart` |
| share of one whole, few slices | `pie_chart` |
| a value across two dimensions | `heatmap` |
| two quantitative columns compared | `scatter_plot` |
| spread within categories | `box_plot` |
| nested part-of-whole | `treemap` |
| a single scalar | `big_number` |

**Each type fixes its X axis.** `line_chart`, `area_chart`, `grouped_line_chart` need a date on X →
periods must be ISO (`2024-01-01`, or `2024-01`). A month name or `Q1` belongs on `bar_chart`.

### Charting more than one series

When the answer covers several codes/aspects, the chart shows **all of them**, not just the total. Use
**long** form — each code as rows tagged in one series column:

```sql
SELECT periode, 'aspek A' AS seri, nilai_a AS jumlah FROM t
UNION ALL
SELECT periode, 'aspek B' AS seri, nilai_b AS jumlah FROM t
ORDER BY 1, 2
```

Then chart `[periode, jumlah, seri]` as `grouped_line_chart` over periods, or `grouped_bar_chart`
across categories. Never chart a total beside its own parts.

If the tool returns `## Kesalahan` → act on the reason, do not retry the same call.
If it returns `No rows to chart.` → answer in text; do not force a chart.

**If the call succeeded but no chart appears, the answer still stands** — write the full answer, say
once that the chart could not be displayed, never retry, never trim the answer to compensate.

## PRESENT

- Lead with the finding in words. The chart supports the sentence; it does not replace it.
- Do **not** repeat the chart's table as markdown.
- Mention any limit the tool reported (top-N bucketing, downsampling) when it changes interpretation.

## Hard rules

- **One chart per question — but one chart carries many series.** The two-panel rule is the only
  exception, and it produces two charts by design.
- **Never re-type tool output into `data=`/`columns=`.**
- **Chart follows the answer's filters** — same bridge/varian, same codes, same date range.
- **The chart is not the export.** A chart never replaces `upload_to_s3`.
