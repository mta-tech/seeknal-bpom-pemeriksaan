# 12 — Belum Ditemukan & Pertanyaan Eksternal

> Apa yang TIDAK bisa dijawab dari 19 tabel ini, dan pertanyaan apa yang perlu dikirim ke tim sumber data.

## 12.1 Tiga Lapis Ketidaklengkapan

Warehouse `pemeriksaan` belum lengkap dalam **3 lapis berbeda**:

| Lapis | Jenis ketidaklengkapan | Contoh | Solusi |
|---|---|---|---|
| **1: Nilai** | Kolom kondisional & NULL | grade 83% kosong, 943 tanggal hilang | Query validasi (dapat diatasi) |
| **2: Makna** | Kode tanpa kamus | jenis_id (25 kode), TTP/TDP label | Konfirmasi tim sumber |
| **3: Cakupan** | Data absen total | Inspeksi rokok, target pra-2024 | Cari sistem/sumber lain |

**Lapis 1 bisa diselesaikan dengan query.** Lapis 2 & 3 TIDAK BISA — informasinya memang tidak ada di DB ini,
harus didatangkan dari luar (tim aplikasi, dokumentasi regulasi BPOM, atau sistem sumber lain).

## 12.2 Pertanyaan untuk Tim Sumber Data (10 item)

### P1 — Kamus `jenis_id` petugas (25 kode)
**Pertanyaan**: "Apa label resmi tiap kode peran petugas? Apa arti 3 kode 6-digit (211265, 211337, 223447)?"
**Dampak jika tak terjawab**: Analisis komposisi tim (siapa memimpin, siapa lab) tidak bisa dipertanggungjawabkan.
**Bukti butuh**: 2.997 petugas diklasifikasi 25 kode tanpa kamus. 3 kode 6-digit = 30 baris tak dikenal.

### P2 — Kamus `tp_unit_id` (92 nilai)
**Pertanyaan**: "Apa satuan untuk tiap tp_unit_id? Apakah 281=pcs, 241=box, 282=botol?"
**Dampak**: Akurasi kuantitas & nilai sitaan. 11 kode 6-digit (211214-220008) tak dikenal.
**Bukti**: 92 nilai, top 281 (70k baris). Kode 263 menyebabkan INFALGIN error.

### P3 — Data inspeksi Rokok
**Pertanyaan**: "Di mana data inspeksi rokok tercatat? Target 21.504 tapi realisasi 0 di warehouse ini."
**Dampak**: Pencapaian target rokok selalu 0% — menyesatkan pimpinan.
**Bukti**: Tidak ada komoditi 'ROKOK' di fact. Target rokok ada di target_balai.

### P4 — Kenapa `target_pengawasan` Obat = 0
**Pertanyaan**: "Semua 76 balai punya target_pengawasan=0 untuk Obat. Apakah obat diukur via mekanisme lain?"
**Dampak**: 14.225 inspeksi Obat tanpa pembanding target. Evaluasi kinerja obat tidak lengkap.
**Bukti**: `sum(target_pengawasan) WHERE komoditi='Obat'` = 0 (bukan NULL).

### P5 — Penyebab TMK naik 2025 (38%→24%→32%)
**Pertanyaan**: "Apa yang berubah di 2025? Apakah ada perubahan standar pemeriksaan, kebijakan, atau memang kepatuhan menurun?"
**Dampak**: Tren positif 4 tahun (2020-2024) terhenti. PANGAN IRT kontributor utama lompatan.
**Bukti**: TMK 24,1% (2024) → 32,1% (2025). PANGAN IRT: 38% (2024) → 71% (2025).

### P6 — Definisi grade final
**Pertanyaan**: "Kapan grade final ditetapkan? Apakah grade bisa berubah antara VERIFY4 dan FINISHED? Grade mana yang boleh dipakai untuk pelaporan resmi?"
**Dampak**: Grade muncul di status IN_PROGRESS → mungkin sementara, bukan final.
**Bukti**: Grade terisi di status non-FINISHED. 83% NULL (struktural untuk non-rutin).

### P7 — Aturan cascade delete draft
**Pertanyaan**: "Apa yang seharusnya terjadi ketika draft dibatalkan? Haruskah timeline/petugas/log ikut terhapus?"
**Dampak**: 30.699 orphan timeline, termasuk 3 FINISHED + 3 VERIFY5/7 yang fact-nya hilang.
**Bukti**: 30.699 id di timeline tidak ada di fact. 6 di antaranya status lanjut (mencurigakan).

### P8 — Sumber otoritatif: public vs dimension
**Pertanyaan**: "Mana yang otoritatif untuk pelaporan — public (257k) atau dimension (150k)? Kenapa keduanya ada?"
**Dampak**: Risiko dua sumber kebenaran — dua tim bisa melapor angka berbeda.
**Bukti**: public.mv_pemeriksaan = 257.456 vs dimension.mv_pemeriksaan = 150.603. Struktur kolom berbeda.

### P9 — Apakah `agg` dipakai dashboard?
**Pertanyaan**: "Apakah mv_pemeriksaan_agg dipakai oleh dashboard? Apakah bug fan-out 2× diketahui?"
**Dampak**: Dashboard mungkin menampilkan total 2× lipat (513k vs 257k).
**Bukti**: `sum(jumlah_pemeriksaan)` agg = 513.026 ≈ 2× fact.

### P10 — Definisi resmi TTP/TDP/TMBB
**Pertanyaan**: "Apa kepanjangan & definisi resmi TTP, TDP, TMBB? Kapan masing-masing dipakai?"
**Dampak**: TTP hanya 0,3% punya temuan produk — BUKAN "temuan tindak pidana" seperti dugaan.
**Bukti**: TTP (1.540) tersebar di 7 komoditi, avg issue 0,7, hampir tanpa temuan. Kode administratif.

## 12.2B — Gap Baru Terverifikasi dari Pertanyaan User KAI (7 item)

> Dari analisis **963 pertanyaan natural-language** user di sistem KAI text2sql (lihat [14_pola_pertanyaan_user.md](14_pola_pertanyaan_user.md)),
> ditemukan gap yang user AKTIF tanyakan tapi data-nya TIDAK ada di warehouse. Jumlah = bukti permintaan riil.

### G1 — BUPN (18 pertanyaan user) 🔴
**Pertanyaan**: "Sarana BUPN apa saja yang pernah diperiksa BPOM?" / "temuan produk berdasarkan kategori sarana distribusi BUPN..."
**Dampak**: 18 pertanyaan user tidak bisa dijawab. Tidak ada kolom `bupn` di warehouse.
**Investigasi**: Cek apakah BUPN tersimpan di `klasifikasi_sarana`, `legal`, atau `klasifikasi_distribusi`. BUPN = Badan Usaha Pangan Berizin? Perlu konfirmasi definisi.

### G2 — SIPT / ketepatan waktu pelaporan (13 pertanyaan) 🟡
**Pertanyaan**: "ketepatan waktu pelaporan SIPT... tanggal pemeriksaan vs tanggal kirim SIPT ke pusat (kurang/lebih dari 30 hari kerja)"
**Dampak**: User mau audit SLA pelaporan. Tidak ada kolom `tanggal_kirim_sipt`.
**Proxy**: `day_input_mulai` (tanggal_mulai − tanggal_input) = proxy keterlambatan entri. BUKAN SIPT sebenarnya.
**Investigasi**: Data SIPT ada di sistem SIPT terpisah, tidak di warehouse pemeriksaan.

### G3 — Nomor notifikasi produk (7 pertanyaan) 🔴
**Pertanyaan**: "jumlah sarana distribusi yang TIDAK memiliki nomor notifikasi"
**Dampak**: Tidak ada kolom nomor notifikasi/NIE di `mv_pemeriksaan` atau `mv_pemeriksaan_temuan`.
**Investigasi**: Nomor notifikasi ada di DB `penandaan` atau `rpo_v2`, bukan pemeriksaan.

### G4 — Sampling (3 pertanyaan) 🔴
**Pertanyaan**: "profil sampling dan pengujian obat dan makanan" / "jumlah sampel kosmetik yang disampling"
**Dampak**: Sampling ada di DB `pengujian`, bukan pemeriksaan. Cross-database query dibutuhkan.

### G5 — Forecast/proyeksi (2 pertanyaan) 🟡
**Pertanyaan**: "proyeksikan pertumbuhan populasi sarana peredaran... 5 tahun terakhir... simulasi proyeksi tahun berikutnya"
**Dampak**: Bukan fungsi SQL analyst — perlu skill forecast (mirip `bpom-forecaster` di project pemeriksaan).

### G6 — "Nilai sarana" mentah (2 pertanyaan) 🟡
**Pertanyaan**: "grading A MK jika nilai sarana A dan B; grading B TMK jika nilai sarana C..."
**Dampak**: User definisikan grading logic custom dengan "nilai sarana" sebagai input. Warehouse hanya punya `grade` (A/B/C) final, tidak ada "nilai" mentah per sarana.
**Investigasi**: Apakah "nilai sarana" tersimpan di sistem sumber (sebelum jadi grade)?

### G7 — CPOTB (1 pertanyaan) 🟡
**Pertanyaan**: "tren... kategori temuan TIE/CPOTB/CPOTB habis/tidak memiliki CPOTB"
**Dampak**: Warehouse punya CPOB/CPKB (`mv_kriteria_pemeriksaan`), bukan CPOTB (Cara Pembuatan Obat Tradisional yang Baik).
**Investigasi**: CPOTB mungkin sub-kategori kriteria untuk Obat Tradisional yang belum dipetakan.

## 12.3 Limitasi Analisis Ini

Beberapa hal yang TIDAK bisa dianalisis dari warehouse `pemeriksaan` saja:

1. **Tren pencapaian target multi-tahun** — target hanya 2024, tidak ada 2020-2023.
2. **Coverage rate (cakupan pengawasan)** — tidak ada data jumlah sarana terdaftar riil sebagai denominator.
3. **Efektivitas tindak lanjut** — tidak ada data apa yang terjadi SETELAH Pembinaan/Peringatan.
4. **Recidivism rate akurat** — entity resolution sarana masih kabur (130k nama → 126k normalized).
5. **Cost-benefit pengawasan** — tidak ada data biaya inspeksi vs nilai sitaan.
6. **Perubahan record dari waktu ke waktu** — sync full-reload, tidak ada CDC.
7. **Korelasi severity CPOB vs grade** — zero overlap antara kriteria dan grade.

## 12.4 Investigasi Lanjutan yang Masih Bisa Dilakukan dari DB Ini

Hal-hal yang BISA digali lebih dalam tetapi belum tuntas dalam analisis ini:

- **NLP catatan log** (207.850 distinct) — alasan revisi/penolakan, pola teks.
- **Normalisasi `tp_negara`** (1.299 varian) — build mapping table China/CINA/TIONGKOK/PRC.
- **Entity resolution sarana** — fuzzy matching untuk dedup 130k nama → sarana riil.
- **Analisis petugas individul** — siapa paling produktif, konsistensi kesimpulan antar petugas.
- **Pola kriteria CPOB berulang** — "temuan berulang dari inspeksi sebelumnya" di tx_criteria_desc.
- **Kohort inspeksi lintas tahun** — lacak sarana yang sama diinspeksi 2020, 2022, 2024 — apakah membaik?
