# Kondisi instrumen — apa yang sebenarnya dijalankan

**Tanggal audit:** 18 Agustus 2026 · **Harness:** `scripts/test_variant_compare.py` mode `variant-compare` (`version: v3`)
**Sumber pemeriksaan:** berkas hasil JSON, berkas testcase YAML, direktori varian, `.env`, dan **database live via tunnel `localhost:5533`**.

## 1. Yang dijalankan hanya SATU varian, bukan perbandingan

Setiap berkas hasil hanya memuat kunci varian `after-insight-v2`. Tidak satu pun run memuat
`v1-base` atau `after-insight-v1`.

> **Konsekuensi:** angka pass-rate ini adalah **uji regresi satu titik**, bukan bukti bahwa
> `after-insight-v2` lebih baik dari `v1-base`. Klaim "context v2 memperbaiki v1" **belum diuji**
> pada gelombang 18 Agustus.

Penyebab teknisnya terlihat di direktori varian:

| Varian | `.env` | `.seeknal/` | `seeknal/skills` |
|---|---|---|---|
| `v1-base` | ada | **tidak ada** | ada |
| `after-insight-v1` | ada | **tidak ada** | ada |
| `after-insight-v2` | ada | ada | ada |

Docstring harness menyatakan `.seeknal/` **wajib** dimiliki setiap varian. Dua varian pembanding
tidak memilikinya, jadi keduanya tidak dapat dijalankan tanpa perbaikan symlink lebih dulu.

## 2. Logika harness seragam, hanya default path yang berbeda

Empat salinan `scripts/test_variant_compare.py` di repo domain **identik secara logika**. Terhadap
induknya di `seeknal-bpom-neo` bedanya hanya tiga baris (dua default path dan contoh teks bantuan):

```
- DEFAULT_VARIANTS_ROOT = .../docs/context_recap/testing_refactor
- DEFAULT_TEST_PATH     = .../seeknal/tests/v1
+ DEFAULT_VARIANTS_ROOT = .../docs/context_recap
+ DEFAULT_TEST_PATH     = .../docs/testcase
```

Jadi perbedaan hasil antar repo **bukan** berasal dari perbedaan harness.

## 3. Cacat penilaian yang dibawa harness

### 3.1 Toleransi 5 % memindai SELURUH teks jawaban

`_token_in_answer()` mencocokkan angka GT dengan **setiap angka** yang muncul di jawaban, lalu
menyatakan cocok bila ada satu saja yang selisihnya ≤ toleransi:

```python
for m in re.finditer(r"\d[\d\.]*", answer_lower):
    anum = _extract_num(m.group(0))
    if anum is not None and abs(anum - tnum) <= tol:
        return True
```

Jawaban yang memuat tabel rincian bisa memuat belasan angka. Satu di antaranya kebetulan dekat
dengan GT sudah cukup untuk PASS — **walau angka utamanya salah**. Bukti kuantitatifnya ada di
`03-verifikasi-database.md`.

### 3.2 Token angka kecil dinilai sebagai angka, bukan teks

Token seperti `'1970'` (penanda epoch) diperlakukan sebagai angka karena memuat ≥ 2 digit. Pada
`tolerance_pct: 0` ia jatuh ke pencocokan substring, tetapi pada testcase bertoleransi ia
dibandingkan secara numerik terhadap seluruh angka jawaban. Assert tekstual dan assert numerik
tidak dipisahkan di tingkat skema testcase.

### 3.3 Jawaban klarifikasi dipilih otomatis ke opsi pertama

Bila agent memanggil `request_clarification`, harness melanjutkan dengan giliran `[AUTO]` yang
memilih opsi. Yang dinilai adalah jawaban setelah AUTO. Bila urutan opsi yang disusun agent tidak
sejalan dengan definisi GT, kegagalan yang tercatat adalah **kegagalan pilihan otomatis**, bukan
kegagalan analitik.

## 4. Cakupan pengujian jauh di bawah populasi testcase

Hanya sebagian kecil testcase yang dijalankan pada gelombang ini. Rinciannya per repo ada di
`00-RINGKASAN.md` §1. Pass-rate karena itu **bukan** ukuran kualitas seluruh domain — ia ukuran
kualitas pada subset yang dipilih.
