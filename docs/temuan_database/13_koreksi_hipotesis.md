# 13 — Koreksi Hipotesis (Meta-Learning)

> Dokumen ini mencatat hipotesis yang muncul selama analisis, lalu diverifikasi oleh query nyata.
> Tujuan: mencegah pengularan kesalahan yang sama di analisis mendatang.

## 13.1 Hipotesis yang TERBANTAHKAN (❌)

### ❌ "943 record NULL tanggal = satu batch migrasi lama"
**Sumber**: Polymorfit NULL (tanggal_mulai + selesai + day_* + tujuan semua NULL serempak).
**Bukti yang membantahkan**: id tersebar 284-289.133 (span nyaris penuh), tanggal_input 2020-2026, 84 balai.
**Vonis**: NULL operasional tersebar (inspeksi dibuat tapi tak dimulai), BUKAN kohort migrasi.

### ❌ "Grade (kepatuhan sarana) dan temuan (produk ilegal) adalah dua sistem independen"
**Sumber**: Dua jalur penilaian terpisah (checklist vs produk sitaan).
**Bukti yang membantahkan**: Grade A 6,2% punya temuan, Grade C 49,6% — korelasi monoton 8× lipat.
**Vonis**: Berkorelasi KUAT. Sarana dengan manajemen buruk cenderung menyimpan produk ilegal.
**Pelajaran**: "Terpisah secara prosedural" ≠ "tidak berkorelasi secara empiris."

### ❌ "TTP = Temuan Tindak Pidana (pelanggaran produk pidana)"
**Sumber**: Akronim TTP mirip "tindak pidana."
**Bukti yang membantahkan**: TTP hanya 0,3% punya temuan produk (lebih rendah dari MK 2,3%!).
**Vonis**: TTP/TDP = kode administratif/perizinan, bukan pelanggaran produk.
**Pelajaran**: Jangan menebak akronim tanpa verifikasi profil data.

### ❌ "Bottleneck di kabalai→direktur = 91 hari (dari timeline)"
**Sumber**: `mv_pemeriksaan_timeline.kabalai_direktur` median dilaporkan ~91 hari.
**Bukti yang membantahkan**: Timeline tercemar outlier tanggal. Hitung dari log: V4→V7 total ~67 hari.
**Vonis**: "91 hari" adalah artefak outlier. Bottleneck nyata = seluruh pipeline pusat (V4-V7), bukan satu tahap.
**Pelajaran**: Data turunan (timeline) < reliable dari data mentah (log) saat ada outlier.

### ❌ "Hotspot #1 adalah Jamu/Obat Tradisional (Jatim 50%)"
**Sumber**: Query tanpa kontrol tujuan pemeriksaan.
**Bukti yang membantahkan**: Setelah kontrol RUTIN (kepatuhan riil, bukan efek penargetan),
**PANGAN IRT** muncul sebagai #1 (59-79% TMK konsisten nasional).
**Vonis**: Tanpa kontrol tujuan, TMK tinggi bisa hanya efek penargetan (KASUS/INTENSIFIKASI), bukan kepatuhan riil.
**Pelajaran**: Selalu kontrol `tujuan_pemeriksaan` saat membandingkan kepatuhan antar dimensi.

### ❌ "agg konsisten dengan fact (selisih hanya 943 = NULL tanggal)"
**Sumber**: Grand total per periode_type cocok (256.513 vs 257.456).
**Bukti yang membantahkan**: `sum(jumlah_pemeriksaan)` semua baris agg = 513.026 ≈ 2× fact.
**Vonis**: Grand total per periode_type cocok, tetapi SUM semua baris menggandakan karena fan-out dimensional.
**Pelajaran**: Konsistensi pada satu level granularitas ≠ konsistensi pada semua level.

### ❌ "dimension adalah snapshot lama dari public"
**Sumber**: Row count lebih sedikit (150k vs 257k).
**Bukti yang membantahkan**: Struktur kolom berbeda total (18 vs 31, tanpa id/tanggal/measures).
dimension.mv_pemeriksaan_timeline = 18 baris 1 kolom = tabel referensi status, bukan timeline.
**Vonis**: Dimension = proyeksi dimensi murni (untuk BI), bukan snapshot.
**Pelajaran**: Row count saja tidak cukup untuk karakterisasi — bandingkan struktur kolom juga.

## 13.2 Hipotesis yang TERKONFIRMASI (✅)

### ✅ "30.699 orphan timeline = draft yang dibatalkan tanpa cascade delete"
Mayoritas (29.874) berstatus DRAFT dengan tgl_end NULL. Absennya FK = penyebab.
Catatan: 6 record (FINISHED + VERIFY5/7) mencurigakan, perlu investigasi.

### ✅ "mv_* adalah tabel fisik, bukan materialized view"
`relkind='r'` untuk semua. Tidak ada `REFRESH MATERIALIZED VIEW`.

### ✅ "Kolom dengan NULL tinggi mayoritas adalah structural (kondisional)"
grade 83% (RUTIN only), klasifikasi 77% (DISTRIBUSI only), cpob 99,7% (CPOB only).
~70% NULL adalah structural, bukan missing.

### ✅ "tp_pelanggaran & tp_netto adalah kolom mati sejati"
99,996-99,998% NULL. Kolom sejenis (tp_kategori, tp_tindakan) terisi penuh di tabel yang sama.

## 13.3 Pelajaran Metodologi

### Pelajaran 1: Always control for confounders
TMK rate tanpa kontrol `tujuan_pemeriksaan` menyesatkan. RUTIN (29%) vs RENCANA AKSI (53%) —
perbedaan 24 poin BISA hanya efek penargetan, bukan kepatuhan riil.

### Pelajaran 2: Verify derived data against source data
Timeline (derived) < reliable dari log (source) saat ada outlier tanggal.
Selalu cross-check angka turunan dengan sumber asli.

### Pelajaran 3: Fan-out trap is real
JOIN multi-tabel tanpa agregasi awal = COUNT/SUM salah berlipat.
 agg = 2× fact karena dimensional fan-out.
Target × fact JOIN = target jutaan karena fan-out.

### Pelajaran 4: Structural NULL ≠ Missing NULL
83% grade NULL bukan data hilang — memang tidak berlaku untuk sertifikasi.
Menghitung sebagai "missing" = salah tafsir kualitas data.

### Pelajaran 5: Outlier tanggal merambat ke seluruh hilir
1 record tanggal 0004 → day_input_mulai = 736.685 → agg avg_day tercemar → dashboard salah.
Bersihkan di HULU (fact), bukan di tiap dashboard.

### Pelajaran 6: Don't guess acronyms
TTP ditebak "tindak pidana" → salah. Profil data (0,3% punya temuan) membantah.
Verifikasi makna kode dengan profil data, bukan asumsi akronim.

### Pelajaran 7: Grand total consistency ≠ dimensional consistency
agg grand total cocok (selisih 943 NULL), tetapi per-UPT/day mismatch (8.530 hari) dan SUM semua baris = 2×.
Uji konsistensi pada MULTIPLE level granularitas.

### Pelajaran 8: Row count ≠ structural identity
dimension vs public: row count beda, tapi struktur kolom juga beda → bukan mirror/snapshot.
Karakterisasi butuh struktur + row count + konten, bukan satu metrik saja.
