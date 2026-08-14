# 16. Cakupan context terhadap kondisi database `pemeriksaan`

Dokumen ini menjawab satu pertanyaan: **apakah yang diajarkan ke agent sudah menutup**
**kondisi database yang sebenarnya.** Sumbernya profiling langsung ke warehouse, bukan
pembacaan skema. Seluruh isi dokumen ini khusus domain `pemeriksaan`; istilah, kode, dan
perilaku kolom di sini **tidak berlaku untuk domain lain** dan tidak boleh dipinjam.

## Cara membacanya

Tiap kolom data ditempatkan di salah satu dari empat kuadran, dari dua pertanyaan:
apakah **context/skill menyebutnya**, dan apakah **SQL sistem lama pernah memakainya**.

| Kuadran | Arti | Tindakan |
|---|---|---|
| **A — aman** | diajarkan, dan pernah dipakai | tidak ada |
| **B — berlebih** | diajarkan, tapi tak pernah dipakai | biarkan; menyiapkan pertanyaan yang belum muncul |
| **C — regresi** | **tidak** diajarkan, padahal SQL lama memakainya | tutup; kemampuan yang hilang saat migrasi |
| **D — titik buta** | tidak diajarkan, dan tak pernah dipakai siapa pun | nilai satu per satu; sebagian memang tak perlu |

Dari **132 kolom data** di **11 tabel** (kolom pembukuan ETL `sync`/`last_updated` tidak dihitung):

| Kuadran | Jumlah | Porsi |
|---|--:|--:|
| A | 63 | 47% |
| B | 23 | 17% |
| C | 14 | 10% |
| D | 32 | 24% |

> Angka di tabel ini menggambarkan **cakupan dokumen**, bukan isi data. Angka isi data
> tidak dibawa ke halaman `context/` — halaman itu mengajarkan pemetaan, bukan nilai.

## Batas alat ukur ini — wajib dibaca sebelum menindak kuadran C dan D

Penempatan kuadran dihitung dengan mencocokkan **nama kolom** ke teks context. Cara itu punya dua
kelemahan yang sudah terbukti, dan keduanya membuat kuadran C dan D **melebih-lebihkan** lubang.

**Pertama, aturan tingkat tabel tidak terdeteksi.** Kalau context mengajarkan sebuah aturan tentang
satu tabel tanpa menyebut kolomnya satu per satu, semua kolom tabel itu jatuh ke kuadran D seolah
tak dikenal. Kasus nyatanya di domain ini: aturan kubus `mv_pemeriksaan_agg` — bahwa `periode_type`
bernilai dua dan wajib disaring salah satu, dan bahwa kubus beragregasi berdasarkan tanggal selesai
sehingga trennya tidak sebanding dengan tabel fakta — **sudah tertulis dengan benar** di
`00-menghitung.md`. Namun 14 kolom kubus itu tetap muncul di kuadran D. Itu artefak pengukuran,
**bukan lubang**.

**Kedua, alat ukur bisa gagal diam-diam.** Versi pertama pengukuran ini melaporkan seluruh kolom
tercakup — hasil yang mustahil. Sebabnya pemisah kolom tertulis sebagai teks literal, bukan tab,
sehingga nama kolom menjadi string kosong dan pola pencarian cocok ke apa saja. Setiap pengukuran
ulang wajib menyertakan **kontrol negatif**: nama kolom yang sengaja dikarang harus dilaporkan
tidak ditemukan. Tanpa itu, angka cakupan tidak boleh dipercaya.

**Karena itu:** perlakukan kuadran C dan D sebagai **daftar kandidat**, bukan vonis. Yang sudah
diverifikasi satu per satu terhadap warehouse ada di bagian *Lubang yang terbukti* di bawah —
hanya itu yang layak ditindak.

## C — Regresi: dipakai sistem lama, tidak diajarkan sekarang

Ini kelompok paling mendesak. SQL sistem lama membuktikan kolomnya **memang dipakai untuk**
**menjawab pertanyaan nyata**; kalau context sekarang tidak menyebutnya, kemampuan itu hilang
tanpa ada yang sadar.

| Tabel | Kolom | Kondisi data |
|---|---|---|
| `mv_kriteria_pemeriksaan` | `tgl_end` | ±582 nilai |
| `mv_kriteria_pemeriksaan` | `tgl_start` | ±565 nilai |
| `mv_pemeriksaan` | `day_mulai_selesai` | ±191 nilai |
| `mv_pemeriksaan` | `tujuan_pemeriksaan` | berkode, ±34 nilai |
| `mv_pemeriksaan_agg` | `jumlah_pemeriksaan` | berkode, ±28 nilai |
| `mv_pemeriksaan_agg` | `tujuan_pemeriksaan` | berkode, ±30 nilai |
| `mv_pemeriksaan_log` | `created_at` | kardinalitas 16% dari baris |
| `mv_pemeriksaan_log` | `urutan_step` | berkode, ±23 nilai |
| `mv_pemeriksaan_timeline` | `kabalai_direktur` | ±511 nilai · kosong 89% |
| `mv_pemeriksaan_timeline` | `mulai_kabalai` | ±407 nilai · kosong 14% |
| `mv_pemeriksaan_timeline` | `tanggal_kirim_direktur` | ±286 nilai · kosong 89% |
| `mv_pemeriksaan_timeline` | `tgl_end` | ±1993 nilai · kosong 5% |
| `mv_pemeriksaan_timeline` | `tgl_start` | ±1796 nilai · kosong 5% |
| `target_balai` | `target_sarana_distribusi` | kardinalitas 33% dari baris |

## D — Titik buta: tak dikenal context maupun sistem lama

Sebagian memang tidak perlu diajarkan (id internal, indeks posisi array, stempel waktu baris).
Sisanya adalah kemampuan yang belum pernah dipakai siapa pun.

| Tabel | Kolom | Kondisi data | Perlu? |
|---|---|---|---|
| `coverage_balai` | `id_balai` | kardinalitas 13% dari baris | tidak — teknis |
| `coverage_balai` | `id_kabupaten` | kardinalitas 77% dari baris | tidak — teknis |
| `mv_kriteria_pemeriksaan` | `criteria_index` | berkode, ±48 nilai | tidak — teknis |
| `mv_pemeriksaan` | `day_input_mulai` | ±459 nilai | nilai manual |
| `mv_pemeriksaan` | `day_input_selesai` | ±492 nilai | nilai manual |
| `mv_pemeriksaan_agg` | `avg_critical_issue` | berkode, ±47 nilai | nilai manual |
| `mv_pemeriksaan_agg` | `avg_day_input_mulai` | ±1197 nilai | nilai manual |
| `mv_pemeriksaan_agg` | `avg_day_input_selesai` | ±1260 nilai | nilai manual |
| `mv_pemeriksaan_agg` | `avg_day_mulai_selesai` | ±297 nilai | nilai manual |
| `mv_pemeriksaan_agg` | `avg_major_issue` | ±140 nilai | nilai manual |
| `mv_pemeriksaan_agg` | `avg_minor_issue` | ±168 nilai | nilai manual |
| `mv_pemeriksaan_agg` | `jumlah_sarana_unik` | berkode, ±27 nilai | nilai manual |
| `mv_pemeriksaan_agg` | `max_day_mulai_selesai` | ±210 nilai | nilai manual |
| `mv_pemeriksaan_agg` | `min_day_mulai_selesai` | ±202 nilai | nilai manual |
| `mv_pemeriksaan_agg` | `tanggal_periode` | ±1862 nilai | nilai manual |
| `mv_pemeriksaan_agg` | `total_critical_issue` | berkode, ±18 nilai | nilai manual |
| `mv_pemeriksaan_agg` | `total_major_issue` | berkode, ±54 nilai | nilai manual |
| `mv_pemeriksaan_agg` | `total_minor_issue` | ±68 nilai | nilai manual |
| `mv_pemeriksaan_jenis_pangan` | `posisi_dalam_array` | berkode, ±17 nilai | tidak — teknis |
| `mv_pemeriksaan_kategori_temuan` | `posisi_dalam_array` | berkode, ±3 nilai | tidak — teknis |
| `mv_pemeriksaan_log` | `id_steps` | nyaris unik per baris | tidak — teknis |
| `mv_pemeriksaan_log` | `updated_at` | kardinalitas 16% dari baris | tidak — teknis |
| `mv_pemeriksaan_temuan` | `tp_bets` | ±12069 nilai · kosong 47% | nilai manual |
| `mv_pemeriksaan_temuan` | `tp_keterangan` | ±5236 nilai · kosong 54% | nilai manual |
| `mv_pemeriksaan_temuan` | `tp_unit_id` | ±69 nilai | nilai manual |
| `mv_pemeriksaan_timeline` | `tanggal_kirim_kabalai` | ±1945 nilai · kosong 14% | nilai manual |
| `target_balai` | `target_penandaan` | kardinalitas 48% dari baris | nilai manual |
| `target_balai` | `target_pengawasan` | berkode, ±53 nilai | nilai manual |
| `target_balai` | `target_pengujian` | kardinalitas 48% dari baris | nilai manual |
| `target_balai` | `target_pengujian_pangan` | kardinalitas 13% dari baris · kosong 3% | nilai manual |
| `target_balai` | `target_pengujian_pangan_fortifikasi` | berkode, ±19 nilai · kosong 3% | nilai manual |
| `target_balai` | `target_sarana_produksi` | kardinalitas 14% dari baris | nilai manual |

## Katalog nilai kolom berkode

Kolom yang nilainya terbatas dikatalogkan penuh di bawah — inilah "kode filter" yang boleh
diajarkan. Yang tidak boleh dibawa ke `context/` adalah **cacah barisnya**, karena itu
bergeser tiap ETL; karena itu di sini hanya nilainya yang didaftar, tanpa jumlah.

### `mv_kriteria_pemeriksaan` . `kabupaten`  ·  kuadran A

`Kota Jakarta Timur`, `Kabupaten Bekasi`, `Kota Bandung`, `Kota Semarang`, `Kabupaten Pasuruan`, `Kabupaten Sidoarjo`, `Kabupaten Bandung Barat`, `Kota Tangerang`, `Kabupaten Bogor`, `Kabupaten Serang`, `Kabupaten Tangerang`, `Kota Palembang`, `Kabupaten Gresik`, `Kabupaten Karanganyar`, `Kota Jakarta Selatan`, `Kota Surabaya`, `Kabupaten Bandung`, `Kota Cimahi`, `Kabupaten Sukabumi`, `Kabupaten Deli Serdang`, `Kota Jakarta Utara`, `Kabupaten Malang`, `Kota Medan`, `Kabupaten Cianjur`, `Kota Bekasi`, `Kabupaten Sumedang`, `Kabupaten Sleman`, `Kota Depok`, `Kota Kediri`, `Kabupaten Semarang`, `Kabupaten Sukoharjo`, `Kabupaten Brebes`, `Kabupaten Padang Pariaman`, `Kota Jakarta Barat`, `Kabupaten Demak`, `Kabupaten Karawang`, `Kota Jakarta Pusat`, `Kota Sukabumi`, `Kabupaten Mojokerto`, `Kabupaten Majalengka`, `Kabupaten Klaten`, `Kota Malang`, `Kabupaten Jombang`, `Kota Tangerang Selatan`, `Kabupaten Subang`, `Kabupaten Banyumas`, `Kota Surakarta`, `Kota Kendari`, `Kota Bogor`, `Kabupaten Pemalang`, `Kota Pekalongan`, `Kabupaten Purbalingga`, `Kabupaten Lampung Tengah`, `Kabupaten Pekalongan`, `Kabupaten Kebumen`, `Kota Palangka Raya`, `Kabupaten Cilacap`

### `mv_kriteria_pemeriksaan` . `klasifikasi`  ·  kuadran A

`Obat`, `Produk Biologi dan Sarana Khusus`, `Bahan Baku Obat`, `Suplemen Kesehatan`

### `mv_kriteria_pemeriksaan` . `nama_balai`  ·  kuadran A

`Direktorat Pengawasan Produksi ONPP`, `BALAI BESAR POM DI BANDUNG`, `BALAI BESAR POM DI JAKARTA`, `BALAI BESAR POM DI SURABAYA`, `BALAI BESAR POM DI SEMARANG`, `BALAI BESAR POM DI SERANG`, `BALAI BESAR POM DI PALEMBANG`, `BALAI POM DI BOGOR`, `BALAI POM DI TANGERANG`, `BALAI BESAR POM DI MEDAN`, `BALAI BESAR POM DI YOGYAKARTA`, `BALAI POM DI SURAKARTA`, `BALAI BESAR POM DI PADANG`, `BALAI BESAR POM DI KENDARI`, `BALAI BESAR POM DI PALANGKARAYA`, `DEMO TIPE A`, `BALAI BESAR POM DI BANDAR LAMPUNG`, `BALAI POM DI KEDIRI`

### `mv_kriteria_pemeriksaan` . `tujuan`  ·  kuadran A

`Pemeriksaan Rutin`, `Sertifikasi CPOB`, `Pemusnahan`, `Komprehensif`, `Resertifikasi`, `Asistensi`, `Verifikasi CAPA`, `Observasi Inspeksi otoritas Lain`

### `mv_kriteria_pemeriksaan` . `tx_criteria`  ·  kuadran A

`3`, `2`, _(SQL NULL)_, `1`, `4`

⚠️ Penanda kosong di kolom ini: SQL NULL — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan` . `grade`  ·  kuadran A

_(SQL NULL)_, `A`, `B`, `C`, `N/A`

⚠️ Penanda kosong di kolom ini: SQL NULL, `N/A` — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan` . `hp_followup_name`  ·  kuadran B

_(SQL NULL)_, `Pembinaan`, `Peringatan Keras`, `Peringatan`, `Perintah Perbaikan`, `N/A`, `Perbaikan Hasil Inspeksi`, `Produk Dimusnahkan`, `Permintaan CAPA`, `Penghentian Sementara Kegiatan`, `Rekomendasi Peringatan Keras`, `Rekomendasi Penghentian Sementara Kegiatan`, `Rekomendasi Perbaikan`, `Rekomendasi Peringatan`, `Pencabutan Izin/Perizinan Berusaha`, `Pencabutan Sertifikat CDOB`, `Produk Diamankan`, `Rekomendasi larangan produksi dan/atau mengedarkan untuk sementara waktu`, `Rekomendasi Penarikan dan/atau Perintah Pemusnahan atau Pengiriman Kembali / Re-Ekspor`, `Rekomendasi Pencabutan Izin/Perizinan Berusaha`, `Rekomendasi Pencabutan Sertifikat Cara Pembuatan Obat yang Baik`

⚠️ Penanda kosong di kolom ini: SQL NULL, `N/A` — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan` . `jenis_sarana`  ·  kuadran A

`PANGAN`, `KOSMETIK`, `APOTEK`, `PANGAN MD`, `PUSAT KESEHATAN MASYARAKAT (PKM)`, `OBAT TRADISIONAL`, `PANGAN IRT (CPPB - IRT)`, `BALAI PENGOBATAN / KLINIK`, `INTENSIFIKASI PENGAWASAN KHUSUS`, `SUPLEMEN KESEHATAN`, `TOKO OBAT`, `PBF`, `INSTALLASI FARMASI RUMAH SAKIT SWASTA`, `INSTALLASI FARMASI RUMAH SAKIT PEMERINTAH`, `INSTALASI FARMASI PEMERINTAH KOTA/KABUPATEN (IFK)`, `OBAT TRADISIONAL (CPOTB)`, `KOSMETIK (CPKB)`, `SARANA PRODUKSI OBAT`, `INSTALASI FARMASI PEMERINTAH PROVINSI (IFP)`, `BAHAN BERBAHAYA`, `PANGAN UMKM MENUJU MD`, `KANTOR KESEHATAN PELABUHAN (KKP)`, `PANGAN MD (OLD)`, `DARING`

### `mv_pemeriksaan` . `kesimpulan`  ·  kuadran A

`MK`, `TMK`, `NULL`, `TTP`, `TDP`, `TMBB`

⚠️ Penanda kosong di kolom ini: `NULL` — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan` . `klasifikasi_distribusi`  ·  kuadran A

_(SQL NULL)_, `TOKO KOSMETIK / SWALAYAN / PENGECER`, `DEPOT JAMU / PENGECER`, `PENGECER`, `LAIN-LAIN`, `TOKO OBAT / SWALAYAN`, `KLINIK KECANTIKAN / SALON / SPA`, `DISTRIBUTOR`, `BADAN USAHA/USAHA PERORANGAN PEMILIK NOTIFIKASI KOSMETIK`, `IMPORTIR KOSMETIKA`, `AGEN`, `STOKIST MLM`, `KLINIK KECANTIKAN`, `SALON/SPA`, `IMPORTIR OBAT TRADISIONAL DAN / ATAU SUPLEMEN MAKANAN`, `PENGOBATAN TRADISIONAL ATAU ALTERNATIF`, `GROSIR`, `SUB DISTRIBUTOR ATAU SUB AGEN`, `APOTEK/INSTALASI FARMASI`, `PENJUALAN LANGSUNG SATU/MULTI TINGKAT (MLM)`, `PENJUALAN OBAT TRADISIONAL DAN / ATAU SUPLEMEN MAKANAN MELALUI MEDIA ELEKTRONIK`, `PENJUALAN KOSMETIK MELALUI MEDIA ELEKTRONIK`, `BADAN USAHA`

⚠️ Penanda kosong di kolom ini: SQL NULL — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan` . `klasifikasi_sarana`  ·  kuadran A

_(SQL NULL)_, `SARANA RITEL MODERN`, `SARANA RITEL TRADISIONAL`, `SARANA GUDANG IMPORTIR/DISTRIBUTOR`, `SARANA GUDANG E-COMMERCE`

⚠️ Penanda kosong di kolom ini: SQL NULL — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan` . `komoditi`  ·  kuadran A

`PRODUK PANGAN`, `OBAT`, `KOSMETIK`, `OBAT TRADISIONAL`, `SUPLEMEN KESEHATAN`, `NARKOTIKA`, `PSIKOTROPIKA`, `OBAT OBAT TERTENTU`, `PREKURSOR`, `BAHAN BERBAHAYA`, `PRODUK BIOLOGI DAN SARANA KHUSUS`, `BAHAN BAKU OBAT`, `BAHAN OBAT`

### `mv_pemeriksaan` . `legal`  ·  kuadran B

`TOKO`, `APOTEK`, `PT`, `SWALAYAN / MINI MARKET / SUPER MARKET`, `PKM`, `CV`, `KIOS / WARUNG`, `TOKO OBAT`, `KLINIK`, `PIRT`, `UMKM MILIK PERORANGAN`, `DEPOT JAMU / TOKO JAMU / DEPOT OBAT`, `UD`, `RUMAH SAKIT`, `RUMAH SAKIT UMUM`, `KLINIK KECANTIKAN`, `-`, `GFK`, `DISTRIBUTOR / AGEN`, `BALAI PENGOBATAN`, `ALFAMART/ALFAMIDI`, `SALON`, `INDOMARET`, `TOKO KELONTONG`, `STAND / LOS / GEROBAK / COUNTER`, `STOKIST / MLM`, `BADAN USAHA/PERORANGAN SEBAGAI PEMOHON NOTIFIKASI KOSMETIK`, `PD`, `LEMBAGA / INSTITUSI`, `IMPORTIR KOSMETIKA`, `KLINIK HERBAL`, `SARANA PERMANEN (TOKO/WARUNG/KIOS)`, `FITNES COUNTER`, `SARANA SEMI/NON PERMANEN (LAPAK)`, `RUMAH BERSALIN`, `SPA`, `SUPLEMEN KESEHATAN`, `UTD`, `PELAYANAN`, `PRODUKSI`, _(SQL NULL)_, `IMPORTIR OBAT TRADISIONAL DAN/ATAU SUPLEMEN MAKANAN`, `PBF`, `MARKETPLACE`, `SARANA BERGERAK (MOBIL/MOTOR/KANVAS/GEROBAK)`, `INSTALASI FARMASI PEMERINTAH PROVINSI (IFP)`, `BADAN USAHA DI BIDANG PEMASARAN`, `DISTRIBUSI`, `SARANA PRODUKSI OBAT`, `MEDIA SOSIAL`, `OBAT TRADISIONAL`, `PANGAN IRT (CPPB - IRT)`

⚠️ Penanda kosong di kolom ini: `-`, SQL NULL — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan` . `mapping_komoditi_target_balai`  ·  kuadran B

`PRODUK PANGAN`, `OBAT`, `KOSMETIKA`, `OBAT TRADISIONAL (OT)`, `SUPLEMEN KESEHATAN`, `OBAT KUASI`

### `mv_pemeriksaan` . `provinsi`  ·  kuadran A

`JAWA BARAT`, `JAWA TENGAH`, `DKI JAKARTA`, `JAWA TIMUR`, `NUSA TENGGARA TIMUR`, `SULAWESI SELATAN`, `SUMATERA BARAT`, `ACEH`, `PAPUA`, `LAMPUNG`, `MALUKU`, `SUMATERA UTARA`, `RIAU`, `BANTEN`, `SUMATERA SELATAN`, `BALI`, `DI YOGYAKARTA`, `SULAWESI TENGGARA`, `JAMBI`, `KALIMANTAN TIMUR`, `KEPULAUAN RIAU`, `NUSA TENGGARA BARAT`, `KALIMANTAN SELATAN`, `KALIMANTAN BARAT`, `SULAWESI TENGAH`, `PAPUA BARAT`, `SULAWESI UTARA`, `GORONTALO`, `KALIMANTAN TENGAH`, `BENGKULU`, `KEPULAUAN BANGKA BELITUNG`, `MALUKU UTARA`, `KALIMANTAN UTARA`, `SULAWESI BARAT`, _(SQL NULL)_

⚠️ Penanda kosong di kolom ini: SQL NULL — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan` . `sarana`  ·  kuadran A

`DISTRIBUSI`, `PELAYANAN`, `PRODUKSI`, _(SQL NULL)_

⚠️ Penanda kosong di kolom ini: SQL NULL — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan` . `status`  ·  kuadran A

`VERIFY4`, `VERIFY5`, `FINISHED`, `DRAFT_REVISE`, `VERIFY7`, `DRAFT`, `VERIFY6`, `VERIFY1`, `VERIFY2`, `DRAFT_PUSAT`, `VERIFY_P1`, `FINISHED_PUSAT`, `VERIFY_P3`, `VERIFY3`, `DRAFT_PUSAT_REVISE`, `VERIFY_P2`, `NULL`

⚠️ Penanda kosong di kolom ini: `NULL` — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan` . `status_label`  ·  kuadran B

`OPERATOR PUSAT - VERIFIKASI`, `SUPERVISOR PUSAT - VERIFIKASI`, `SELESAI`, `OPERATOR - PERBAIKAN`, `DIREKTUR - VERIFIKASI`, `OPERATOR - DRAFT`, `SUPERVISOR 2 PUSAT - VERIFIKASI`, `SUPERVISOR - VERIFIKASI`, `SUPERVISOR 2 - VERIFIKASI`, `PEMERIKSAAN PUSAT - OPERATOR PUSAT - DRAFT`, `PEMERIKSAAN PUSAT - SUPERVISOR PUSAT - VERIFIKASI`, _(SQL NULL)_, `PEMERIKSAAN PUSAT - DIREKTUR - VERIFIKASI`, `KEPALA BALAI / LOKA - VERIFIKASI`, `PEMERIKSAAN PUSAT - OPERATOR PUSAT - PERBAIKAN`, `PEMERIKSAAN PUSAT - SUPERVISOR 2 PUSAT - VERIFIKASI`

⚠️ Penanda kosong di kolom ini: SQL NULL — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan` . `tingkat_pemenuhan_cpob`  ·  kuadran A

_(SQL NULL)_, `Baik`, `Cukup`, `Kurang`, `Memuaskan`

⚠️ Penanda kosong di kolom ini: SQL NULL — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan` . `tujuan_pemeriksaan`  ·  kuadran C

`PEMERIKSAAN RUTIN`, `INTENSIFIKASI PENGAWASAN PANGAN`, `INTENSIFIKASI VAKSIN`, `RENCANA AKSI / INTENSIFIKASI PENGAWASAN`, `SERTIFIKASI`, `NATAL DAN TAHUN BARU`, `IDUL FITRI`, `SURVEILANS SMKPO`, `KASUS`, `PERMINTAAN REGISTRASI`, `SERTIFIKASI CDOB`, _(SQL NULL)_, `FORTIFIKASI`, `KASUS/ TINDAK LANJUT`, `KHUSUS`, `VERIFIKASI CAPA SERTIFIKASI DAN PERIZINAN`, `HARI BESAR AGAMA LAINNYA`, `PEMUSNAHAN`, `TINDAK LANJUT`, `PRA SERTIFIKASI`, `RESERTIFIKASI`, `SERTIFIKASI CPOB`, `VERIFIKASI CAPA PEMERIKSAAN RUTIN`, `AUDIT PENERAPAN CPKB`, `KOMPREHENSIF`, `SERTIFIKASI UMKM MENJADI MD`, `ASISTENSI`, `VERIFIKASI CAPA`, `VERIFIKASI CAPA KASUS`, `IMLEK`, `OPGABNAS`, `IDUL ADHA`, `PENELUSURAN JARINGAN`, `TINDAKLANJUT PRAMUKA SAPA`, `TINDAK LANJUT SURAT EDARAN`, `OBSERVASI INSPEKSI OTORITAS LAIN`, `OPGABDA`

⚠️ Penanda kosong di kolom ini: SQL NULL — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan_agg` . `jenis_sarana`  ·  kuadran A

`PANGAN`, `KOSMETIK`, `PANGAN MD`, `APOTEK`, `PUSAT KESEHATAN MASYARAKAT (PKM)`, `OBAT TRADISIONAL`, `BALAI PENGOBATAN / KLINIK`, `PANGAN IRT (CPPB - IRT)`, `SUPLEMEN KESEHATAN`, `TOKO OBAT`, `PBF`, `INTENSIFIKASI PENGAWASAN KHUSUS`, `INSTALLASI FARMASI RUMAH SAKIT SWASTA`, `INSTALLASI FARMASI RUMAH SAKIT PEMERINTAH`, `INSTALASI FARMASI PEMERINTAH KOTA/KABUPATEN (IFK)`, `OBAT TRADISIONAL (CPOTB)`, `KOSMETIK (CPKB)`, `SARANA PRODUKSI OBAT`, `INSTALASI FARMASI PEMERINTAH PROVINSI (IFP)`, `BAHAN BERBAHAYA`, `PANGAN UMKM MENUJU MD`, `KANTOR KESEHATAN PELABUHAN (KKP)`, `PANGAN MD (OLD)`

### `mv_pemeriksaan_agg` . `kesimpulan`  ·  kuadran A

`MK`, `TMK`, `NULL`, `TTP`, `TDP`, `TMBB`

⚠️ Penanda kosong di kolom ini: `NULL` — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan_agg` . `komoditi`  ·  kuadran A

`PRODUK PANGAN`, `OBAT`, `KOSMETIK`, `OBAT TRADISIONAL`, `SUPLEMEN KESEHATAN`, `NARKOTIKA`, `PSIKOTROPIKA`, `OBAT OBAT TERTENTU`, `PREKURSOR`, `BAHAN BERBAHAYA`, `PRODUK BIOLOGI DAN SARANA KHUSUS`, `BAHAN BAKU OBAT`, `BAHAN OBAT`

### `mv_pemeriksaan_agg` . `legal`  ·  kuadran B

`TOKO`, `PT`, `APOTEK`, `SWALAYAN / MINI MARKET / SUPER MARKET`, `PKM`, `CV`, `TOKO OBAT`, `KLINIK`, `UMKM MILIK PERORANGAN`, `KIOS / WARUNG`, `PIRT`, `RUMAH SAKIT`, `RUMAH SAKIT UMUM`, `UD`, `GFK`, `DEPOT JAMU / TOKO JAMU / DEPOT OBAT`, `-`, `DISTRIBUTOR / AGEN`, `KLINIK KECANTIKAN`, `BALAI PENGOBATAN`, `ALFAMART/ALFAMIDI`, `INDOMARET`, `SALON`, `TOKO KELONTONG`, `STOKIST / MLM`, `BADAN USAHA/PERORANGAN SEBAGAI PEMOHON NOTIFIKASI KOSMETIK`, `STAND / LOS / GEROBAK / COUNTER`, `PD`, `LEMBAGA / INSTITUSI`, `IMPORTIR KOSMETIKA`, `KLINIK HERBAL`, `SARANA PERMANEN (TOKO/WARUNG/KIOS)`, `FITNES COUNTER`, `RUMAH BERSALIN`, `SARANA SEMI/NON PERMANEN (LAPAK)`, `SPA`, `UTD`, `IMPORTIR OBAT TRADISIONAL DAN/ATAU SUPLEMEN MAKANAN`, `MARKETPLACE`, `SARANA BERGERAK (MOBIL/MOTOR/KANVAS/GEROBAK)`, `BADAN USAHA DI BIDANG PEMASARAN`, `SUPLEMEN KESEHATAN`, `MEDIA SOSIAL`, `PBF`, `PELAYANAN`, _(SQL NULL)_

⚠️ Penanda kosong di kolom ini: `-`, SQL NULL — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan_agg` . `periode_type`  ·  kuadran B

`day`, `month`

### `mv_pemeriksaan_agg` . `provinsi`  ·  kuadran A

`JAWA BARAT`, `JAWA TENGAH`, `JAWA TIMUR`, `DKI JAKARTA`, `SULAWESI SELATAN`, `SUMATERA BARAT`, `NUSA TENGGARA TIMUR`, `SUMATERA UTARA`, `ACEH`, `BANTEN`, `LAMPUNG`, `RIAU`, `BALI`, `PAPUA`, `SUMATERA SELATAN`, `SULAWESI TENGGARA`, `JAMBI`, `MALUKU`, `DI YOGYAKARTA`, `KALIMANTAN SELATAN`, `KEPULAUAN RIAU`, `KALIMANTAN TIMUR`, `NUSA TENGGARA BARAT`, `KALIMANTAN BARAT`, `SULAWESI TENGAH`, `PAPUA BARAT`, `SULAWESI UTARA`, `BENGKULU`, `KEPULAUAN BANGKA BELITUNG`, `GORONTALO`, `KALIMANTAN TENGAH`, `MALUKU UTARA`, `KALIMANTAN UTARA`, `SULAWESI BARAT`, _(SQL NULL)_

⚠️ Penanda kosong di kolom ini: SQL NULL — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan_agg` . `sarana`  ·  kuadran A

`DISTRIBUSI`, `PELAYANAN`, `PRODUKSI`

### `mv_pemeriksaan_agg` . `status`  ·  kuadran A

`VERIFY4`, `VERIFY5`, `FINISHED`, `DRAFT_REVISE`, `VERIFY7`, `DRAFT`, `VERIFY6`, `VERIFY1`, `VERIFY2`, `VERIFY_P1`, `DRAFT_PUSAT`, `FINISHED_PUSAT`, `VERIFY_P3`, `VERIFY3`, `DRAFT_PUSAT_REVISE`, `VERIFY_P2`, `NULL`

⚠️ Penanda kosong di kolom ini: `NULL` — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan_agg` . `tujuan_pemeriksaan`  ·  kuadran C

`PEMERIKSAAN RUTIN`, `INTENSIFIKASI PENGAWASAN PANGAN`, `INTENSIFIKASI VAKSIN`, `SERTIFIKASI`, `RENCANA AKSI / INTENSIFIKASI PENGAWASAN`, `SURVEILANS SMKPO`, `NATAL DAN TAHUN BARU`, `IDUL FITRI`, `KASUS`, `SERTIFIKASI CDOB`, `PERMINTAAN REGISTRASI`, `FORTIFIKASI`, `KASUS/ TINDAK LANJUT`, `KHUSUS`, `VERIFIKASI CAPA SERTIFIKASI DAN PERIZINAN`, `PEMUSNAHAN`, `HARI BESAR AGAMA LAINNYA`, `TINDAK LANJUT`, `PRA SERTIFIKASI`, `RESERTIFIKASI`, `SERTIFIKASI CPOB`, `VERIFIKASI CAPA PEMERIKSAAN RUTIN`, `AUDIT PENERAPAN CPKB`, `KOMPREHENSIF`, `SERTIFIKASI UMKM MENJADI MD`, `ASISTENSI`, `VERIFIKASI CAPA`, `VERIFIKASI CAPA KASUS`, `IDUL ADHA`, `IMLEK`, `PENELUSURAN JARINGAN`, `TINDAKLANJUT PRAMUKA SAPA`, `OPGABNAS`, `TINDAK LANJUT SURAT EDARAN`, `OPGABDA`, `OBSERVASI INSPEKSI OTORITAS LAIN`

### `mv_pemeriksaan_kategori_temuan` . `tp_kategori`  ·  kuadran A

`TIE (Tanpa Izin Edar)`, `ED (Expire Date / Kedaluwarsa)`, `Temuan Obat Keras`, `BKO`, `Rusak`, `Substandard/Rusak`, `Illegal/TIE`, `Lain - Lain`, `TMK Label`, `Kedaluwarsa`, `Diversi/Penyalahgunaan`, `Mengandung bahan berbahaya/bahan dilarang (berdasarkan SE)`, `Farmasetik`, `Mengandung bahan berbahaya/bahan dilarang (daftar PW)`, `Mengandung bahan berbahaya/dilarang.`, `Palsu`, `Padat`, `Pemusnahan`, `Penandaan`, `TIE`, `Aspek CPOB / CPOTB / CPMB`, `TMS Persyaratan Keamanan, Mutu, Dan Gizi Pangan`, `Kedaluwarsa / Rusak`, `Dimusnahkan`, `Administrasi`, `Bahan Obat`, `Memproduksi MGB Berbahaya`, `NPP dan OOT`, `Obat`, `Memproduksi Kosmetik TIE`, `Lain-lain`, `Agen`, `Stokist MLM`, `Distributor`, `Dikembalikan kepada produsen / importir`, `CCP`, `Badan Usaha/Usaha Perorangan Pemilik Notifikasi Kosmetik`, `Memproduksi Produk TMK Penandaan`, `Klinik Kecantikan / Salon / Spa`, `Importir Kosmetika`, `Penarikan`, `Penjualan kosmetik melalui media elektronik`, `Dokumen Informasi Produk (DIP)`, `Produksi`, `Obat Tradisional (OT)`, `Pengamanan`, `Pemeriksaan Sarana`, `Peringatan Tertulis`, `Sale Pisang`

### `mv_pemeriksaan_log` . `status`  ·  kuadran A

`VERIFY1`, `VERIFY3`, `DRAFT`, `VERIFY4`, `VERIFY5`, `VERIFY2`, `DRAFT_REVISE`, `VERIFY7`, `FINISHED`, `VERIFY6`, `DRAFT_PUSAT`, `VERIFY_P1`, `VERIFY_P3`, `FINISHED_PUSAT`, _(SQL NULL)_, `DRAFT_PUSAT_REVISE`, `VERIFY_P2`

⚠️ Penanda kosong di kolom ini: SQL NULL — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan_log` . `status_label`  ·  kuadran B

`Supervisor - Verifikasi`, `Kepala Balai / Loka - Verifikasi`, `Operator - Draft`, `Operator Pusat - Verifikasi`, `Supervisor Pusat - Verifikasi`, `Supervisor 2 - Verifikasi`, `Operator - Perbaikan`, `Direktur - Verifikasi`, `Selesai`, `Supervisor 2 Pusat - Verifikasi`, `Pemeriksaan Pusat - Operator Pusat - Draft`, `Pemeriksaan Pusat - Supervisor Pusat - Verifikasi`, _(SQL NULL)_, `Pemeriksaan Pusat - Direktur - Verifikasi`, `Pemeriksaan Pusat - Operator Pusat - Perbaikan`, `Pemeriksaan Pusat - Supervisor 2 Pusat - Verifikasi`

⚠️ Penanda kosong di kolom ini: SQL NULL — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan_petugas` . `klasifikasi`  ·  kuadran A

`PRODUK PANGAN`, `OBAT`, `KOSMETIK`, `OBAT TRADISIONAL`, `SUPLEMEN KESEHATAN`, `PSIKOTROPIKA`, `NARKOTIKA`, `OBAT OBAT TERTENTU`, `PRODUK BIOLOGI DAN SARANA KHUSUS`, `PREKURSOR`, `BAHAN BERBAHAYA`, `BAHAN BAKU OBAT`, `BAHAN OBAT`

### `mv_pemeriksaan_petugas` . `komoditi`  ·  kuadran A

`PANGAN`, `KOSMETIK`, `APOTEK`, `PANGAN MD`, `PUSAT KESEHATAN MASYARAKAT (PKM)`, `OBAT TRADISIONAL`, `BALAI PENGOBATAN / KLINIK`, `INTENSIFIKASI PENGAWASAN KHUSUS`, `PANGAN IRT (CPPB - IRT)`, `PBF`, `SUPLEMEN KESEHATAN`, `TOKO OBAT`, `INSTALLASI FARMASI RUMAH SAKIT SWASTA`, `INSTALLASI FARMASI RUMAH SAKIT PEMERINTAH`, `INSTALASI FARMASI PEMERINTAH KOTA/KABUPATEN (IFK)`, `OBAT TRADISIONAL (CPOTB)`, `KOSMETIK (CPKB)`, `SARANA PRODUKSI OBAT`, `INSTALASI FARMASI PEMERINTAH PROVINSI (IFP)`, `BAHAN BERBAHAYA`, `PANGAN UMKM MENUJU MD`, `KANTOR KESEHATAN PELABUHAN (KKP)`, `PANGAN MD (OLD)`, `DARING`

### `mv_pemeriksaan_petugas` . `tujuan`  ·  kuadran A

`PEMERIKSAAN RUTIN`, `INTENSIFIKASI PENGAWASAN PANGAN`, `RENCANA AKSI / INTENSIFIKASI PENGAWASAN`, `INTENSIFIKASI VAKSIN`, `SERTIFIKASI`, `NATAL DAN TAHUN BARU`, `IDUL FITRI`, `SURVEILANS SMKPO`, `KASUS`, `SERTIFIKASI CDOB`, `PERMINTAAN REGISTRASI`, _(SQL NULL)_, `FORTIFIKASI`, `KASUS/ TINDAK LANJUT`, `KHUSUS`, `HARI BESAR AGAMA LAINNYA`, `VERIFIKASI CAPA SERTIFIKASI DAN PERIZINAN`, `PEMUSNAHAN`, `TINDAK LANJUT`, `SERTIFIKASI CPOB`, `PRA SERTIFIKASI`, `RESERTIFIKASI`, `VERIFIKASI CAPA PEMERIKSAAN RUTIN`, `KOMPREHENSIF`, `AUDIT PENERAPAN CPKB`, `SERTIFIKASI UMKM MENJADI MD`, `IMLEK`, `VERIFIKASI CAPA`, `ASISTENSI`, `VERIFIKASI CAPA KASUS`, `OPGABNAS`, `IDUL ADHA`, `TINDAK LANJUT SURAT EDARAN`, `PENELUSURAN JARINGAN`, `TINDAKLANJUT PRAMUKA SAPA`, `OBSERVASI INSPEKSI OTORITAS LAIN`, `OPGABDA`

⚠️ Penanda kosong di kolom ini: SQL NULL — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `mv_pemeriksaan_timeline` . `status`  ·  kuadran A

`VERIFY4`, `VERIFY5`, `DRAFT`, `FINISHED`, `DRAFT_REVISE`, `VERIFY7`, `VERIFY6`, `DRAFT_PUSAT`, `VERIFY1`, `VERIFY2`, `VERIFY_P1`, `FINISHED_PUSAT`, `VERIFY_P3`, `VERIFY3`, `DRAFT_PUSAT_REVISE`, `VERIFY_P2`, `NULL`, `0`

⚠️ Penanda kosong di kolom ini: `NULL`, `0` — perlakukan sebagai "belum diisi", bukan sebagai kategori.

### `target_balai` . `komoditi`  ·  kuadran A

`Obat Kuasi`, `Produk Pangan`, `Obat Tradisional (OT)`, `Obat`, `Kosmetika`, `Suplemen Kesehatan`, `Rokok`


---

## Apa yang diceritakan database ini

`pemeriksaan` merekam **kunjungan inspeksi ke sarana** — apotek, toko, gudang, pabrik — beserta apa
yang ditemukan di sana dan bagaimana berkasnya bergerak sampai disetujui.

Ceritanya bertumpuk dalam empat lapis, dan tiap lapis punya tabelnya sendiri:

| Lapis | Cerita | Tabel |
|---|---|---|
| Peristiwa | siapa memeriksa apa, kapan, untuk tujuan apa, kesimpulannya apa | `mv_pemeriksaan` |
| Isi temuan | produk apa yang bermasalah, berapa banyak, senilai berapa, dari negara mana | `mv_pemeriksaan_temuan` + `mv_pemeriksaan_kategori_temuan` + `mv_pemeriksaan_jenis_pangan` |
| Perjalanan berkas | tahap demi tahap dari draft sampai disetujui, siapa memegang di tiap tahap | `mv_pemeriksaan_log` + `mv_pemeriksaan_timeline` + `mv_pemeriksaan_petugas` |
| Rencana vs capaian | berapa yang ditargetkan, berapa wilayah yang tercakup | `target_balai` + `coverage_balai` + `mv_kriteria_pemeriksaan` |

Satu tabel lagi, `mv_pemeriksaan_agg`, bukan lapis baru — ia kubus pra-agregasi dari lapis peristiwa.

**Yang paling menentukan bentuk jawaban:** tabel peristiwa adalah satu baris per pemeriksaan, tetapi
tabel temuan adalah satu baris per produk temuan. Satu pemeriksaan bisa punya banyak temuan. Setiap
pertanyaan harus memilih dulu ia bicara tentang kunjungan atau tentang barang.

---

## Lubang yang terbukti — dan sifatnya: PENYALURAN, bukan penemuan

Satu hal yang harus dibaca sebelum daftar di bawah, karena ia mengubah ke mana perbaikan diarahkan.

Sebagian besar lubang di bawah **bukan** berarti temuannya belum pernah dibuat. Diperiksa ulang
14 Agustus 2026, mayoritasnya **sudah terdokumentasi dengan benar di direktori ini sejak awal** —
lengkap dengan katalog nilai, grain, dan jebakannya. Yang gagal adalah **penyalurannya ke
`context/`**: halaman context menyebut nama tabelnya lalu berhenti, sehingga pengetahuan yang sudah
dimiliki repositori ini tidak pernah sampai ke agent yang menjawab pertanyaan.

Karena itu tiap butir di bawah mencantumkan **berkas topik** tempat rinciannya tinggal. Dokumen ini
mencatat **pengukurannya**; rincian datanya tetap di berkas topiknya masing-masing, dan di sanalah
pembaruan berikutnya harus ditulis.

Implikasinya untuk cara kerja: menambah dokumen temuan **tidak dengan sendirinya** menutup lubang.
Setiap temuan yang mengubah cara menjawab harus punya pasangan di `context/` atau di skill.

### Daftar temuan

Empat hal di bawah ini diverifikasi lewat query langsung ke warehouse. Masing-masing mengubah angka
jawaban, bukan sekadar melengkapi dokumentasi.

### 1. `tujuan_pemeriksaan` — satu dimensi utuh yang tidak pernah diajarkan

> 📄 Rincian datanya tinggal di `04_kamus_unique_value.md` §4.6 — katalog nilai lengkap + tiga kolom lookalike

Kolom ini menyimpan **alasan** sebuah pemeriksaan dilakukan, dan isinya bercerita banyak: mayoritas
besar adalah pemeriksaan rutin, sisanya terbagi menjadi kampanye musiman yang menempel pada hari
besar keagamaan (Idul Fitri, Natal dan Tahun Baru, Idul Adha, Imlek), jalur sertifikasi (CPOB, CDOB,
CPKB, UMKM menjadi MD, pra/re-sertifikasi), penindakan berbasis kasus, intensifikasi tematik
(pangan, vaksin, fortifikasi), surveilans, sampai operasi gabungan.

**Bukti kondisi:** kolomnya berisi 37 nilai berbeda. **Nol** penyebutan di seluruh `context/`,
`skills/`, dan `SEEKNAL_ASK.md`. Sementara itu SQL sistem lama memakainya 12 kali — jadi ini
kemampuan yang **hilang saat migrasi**, bukan kemampuan yang belum pernah ada.

**Akibatnya:** pertanyaan seperti *"berapa pemeriksaan menjelang Idul Fitri"* atau *"pemeriksaan
rutin dibanding pemeriksaan kasus"* tidak punya rute sama sekali. Agent tidak tahu kolomnya ada.

#### 1b. Dan ada kolom mirip yang SUDAH diajarkan, di tabel dengan grain berbeda

Ini yang membuat butir 1 lebih berbahaya daripada lubang biasa. Database ini punya **empat kolom**
bernama mirip, di empat tabel berbeda:

| Tabel | Kolom | Grain tabelnya | Status di context |
|---|---|---|---|
| `mv_pemeriksaan` | `tujuan_pemeriksaan` | satu baris per pemeriksaan | **tidak diajarkan** |
| `mv_pemeriksaan_agg` | `tujuan_pemeriksaan` | kubus pra-agregasi | tidak diajarkan |
| `mv_pemeriksaan_petugas` | `tujuan` | satu baris per **penugasan petugas** | **diajarkan**, lengkap dengan contoh `GROUP BY tujuan` |
| `mv_kriteria_pemeriksaan` | `tujuan` | satu baris per kriteria | tidak diajarkan |

Jadi pertanyaan *"pemeriksaan per tujuan"* punya rute yang **salah tetapi terlihat benar** — halaman
petugas menawarkan pengelompokan yang namanya persis cocok.

**Bukti kondisi:** `mv_pemeriksaan_petugas` memuat 582.021 baris untuk 257.522 pemeriksaan unik —
sekitar **2,26 baris per pemeriksaan**, karena satu pemeriksaan dikerjakan beberapa petugas.
Jawaban yang lewat jalur itu akan **melebihkan sekitar dua kali lipat**, dan angkanya tidak akan
terlihat aneh.

**Akibatnya untuk perbaikan:** menambahkan `tujuan_pemeriksaan` saja tidak cukup. Halaman petugas
harus sekaligus ditandai bahwa `tujuan` di sana adalah tujuan **penugasan**, bukan tujuan
pemeriksaan, dan tidak boleh dipakai untuk menghitung pemeriksaan. Kalau tidak, kedua rute akan
bersaing dan yang salah tetap menang karena sudah lebih dulu ada.

### 2. Kolom kosong pada tanggal bukan cacat data — itu status DRAFT

> 📄 Rincian datanya tinggal di `11_kualitas_data_dan_anomali.md` — kaitan tanggal kosong dengan status DRAFT

Ada blok baris yang `tanggal_mulai` **dan** `tanggal_selesai`-nya kosong, dan `tujuan_pemeriksaan`-nya
juga kosong. Blok itu bukan acak: **98,4% di antaranya berstatus `DRAFT` atau `DRAFT_PUSAT`**,
sisanya tersebar tipis di tahap verifikasi awal. Semuanya punya `tanggal_input`.

**Artinya:** berkas yang belum diisi memang belum punya tanggal kegiatan. Ini keadaan alur kerja
yang wajar, bukan kerusakan.

**Akibatnya:** setiap filter periode berbasis `tanggal_mulai` **membuang seluruh draft secara
diam-diam**. Untuk pertanyaan "berapa pemeriksaan tahun X" itu benar. Untuk pertanyaan "berapa
berkas yang masuk" itu salah. Context sekarang menyebutkan bahwa kolom tanggal punya baris kosong,
tetapi tidak pernah menghubungkannya dengan status draft, sehingga pilihan itu tidak pernah sadar.

### 3. `mv_pemeriksaan_kategori_temuan` berhenti diperbarui sejak 12 November 2025

> 📄 Rincian datanya tinggal di `02_pemetaan_tabel_per_tabel.md` — tabel cakupan per bulan + aturan penggantinya

Semua tabel lain di database ini di-sync harian. Tabel ini **satu-satunya** yang stempel sync-nya
tertinggal di 2025-11-12.

**Bukti kondisi** — porsi pemeriksaan bertemuan yang punya baris kategori, per bulan:

| Periode | Cakupan kategori |
|---|---|
| sampai Oktober 2025 | hampir penuh |
| November 2025 | jatuh drastis |
| Desember 2025 dan sesudahnya | praktis nol |

**Akibatnya:** pertanyaan "kategori temuan terbanyak" untuk periode berjalan akan mengembalikan
nyaris tidak ada apa-apa, dan yang lebih berbahaya — perbandingan antar tahun akan menampilkan
"penurunan" yang sebenarnya adalah ETL yang berhenti. Tidak ada satu pun peringatan soal ini di
context.

### 4. `target_balai` — tabelnya disebut, kolom targetnya tidak

> 📄 Rincian datanya tinggal di `07_target_dan_capaian.md` — grain, batas tahun, dan pemilihan kolom target

Halaman `85-target-capaian.md` menyebut nama tabel dan kunci join, lalu berhenti di situ.

**Bukti kondisi:** tabel ini bergrain **balai × komoditi** (76 balai × 7 komoditi), bukan satu baris
per balai. `tahun` hanya berisi **2024** — tidak ada tahun lain. Dan ia memuat **tujuh kolom target
berbeda**, di antaranya `target_sarana_produksi` dan `target_sarana_distribusi` yang relevan untuk
domain ini; sisanya milik kegiatan lain dan **tidak boleh dipakai di sini**.

**Akibatnya:** pertanyaan capaian tidak bisa dijawab tanpa menebak kolom. Menjumlahkan tanpa sadar
grain-nya balai × komoditi akan melipatgandakan target tujuh kali. Dan setiap pertanyaan capaian
untuk tahun selain 2024 tidak punya pembanding sama sekali — itu harus dikatakan, bukan dijawab nol.

### 5. Kolom tahap di `mv_pemeriksaan_timeline` tidak diajarkan

> 📄 Rincian datanya tinggal di `05_workflow_dan_bottleneck.md` — kolom tahap dan kekosongan deterministiknya

`tanggal_kirim_kabalai`, `tanggal_kirim_direktur`, `mulai_kabalai`, `kabalai_direktur` — inilah
kolom yang menjawab "berapa lama berkas tertahan di tahap mana". SQL sistem lama memakainya;
context sekarang hanya menyebut nama tabelnya.

**Bukti kondisi:** kolom tahap direktur kosong pada sebagian besar baris, sedangkan tahap kepala
balai hampir selalu terisi. Kekosongan itu **deterministik** — berkas yang tidak pernah naik ke
direktur memang tidak punya tanggalnya, jadi rata-rata yang menyertakan baris kosong akan salah.

---

## Yang TIDAK ditutupi oleh daftar pertanyaan mana pun

Ini menjawab langsung pertanyaan "apakah pertanyaan yang ada sudah mencakup semua kondisi": **tidak.**

Sebagian besar kondisi database ini tidak pernah ditanyakan oleh siapa pun — tidak oleh 494 pasang
SQL sistem lama, tidak pula oleh daftar pertanyaan analitik pengguna. Contoh yang terbukti nol
penyebutan di kedua korpus: satuan pada temuan (`tp_unit_id`), nomor bets produk (`tp_bets`),
keterangan bebas pada temuan (`tp_keterangan`), dan seluruh kolom target selain yang dipakai
laporan rutin.

Konsekuensinya untuk cara kerja kita: **daftar pertanyaan tidak bisa dipakai sebagai ukuran
kelengkapan context.** Kalau context hanya menutupi yang pernah ditanyakan, ia akan gagal pada
pertanyaan pertama yang keluar dari kebiasaan — dan justru pertanyaan seperti itulah yang paling
sering muncul dari pengguna baru. Ukuran yang benar adalah kuadran C dan D di atas, bukan cakupan
terhadap daftar pertanyaan.

---

## Pencocokan temuan konsistensi terhadap `context/` yang hidup sekarang

Diverifikasi 14 Agustus 2026, dengan **kondisi database sebagai acuan mutlak**. Tiap temuan
konsistensi penulisan dan anomali tanggal — rinciannya di berkas kualitas data domain ini —
dicocokkan ke apa yang benar-benar tertulis di `context/` dan `skills/` saat ini.

Kolom **Status** memakai tiga nilai, dan bedanya penting:

| Status | Arti |
|---|---|
| **SUDAH** | aturannya ada dan benar — jangan diubah |
| **BELUM** | aturannya tidak ada di mana pun — perlu ditambahkan |
| **SALAH ARAH** | ada aturan, tetapi isinya menyesatkan terhadap kondisi database — **perbaiki lebih dulu daripada menambah apa pun** |


| Temuan | Status | Yang tertulis sekarang | Perubahan yang dibutuhkan |
|---|---|---|---|
| Spasi ekor pada nama balai membuat filter kesamaan persis nol baris | **BELUM** | `85-target-capaian.md` mengajarkan `lower(trim(...))` **hanya untuk join** ke tabel target; `10-sarana-dan-fasilitas.md` membahas beda kapitalisasi antar tabel, bukan spasi ekor | Tambahkan di `10-sarana-dan-fasilitas.md`: filter kesamaan persis pada `nama_upt` wajib lewat `trim()`, atau memakai nilai hasil probe apa adanya |
| `tp_negara` perlu normalisasi huruf dan spasi | **SUDAH** | `41-nilai-dan-negara.md` sudah mengajarkan `lower(trim(tp_negara))` sebagai langkah pertama | — |
| Keluarga "tidak diketahui" adalah sentinel yang menyamar sebagai negara | **BELUM** | tidak ada | Tambahkan ke `41-nilai-dan-negara.md`: keluarga tak-diketahui dikeluarkan sebelum peringkat negara, karena kalau tidak ia bisa menempati posisi teratas seolah sebuah negara |
| Nama petugas terpecah oleh cara menulis gelar | **SUDAH sebagian** | `70-petugas.md` menyebut adanya varian penulisan | Pertegas konsekuensinya: peringkat orang tidak sahih tanpa normalisasi, dan keterbatasan itu harus disebut di kalimat jawaban |
| Tanggal mustahil: salah ketik abad, epoch 1970, tahun terpotong | **BELUM** | tidak ada | Tambahkan ke `80-waktu-dan-durasi.md`: pertanyaan "paling awal / sejak kapan" wajib membatasi tahun ke rentang operasional; tren per tahun menyaring tahun di luar rentang |
| Tanggal kedaluwarsa produk memang jatuh di masa depan | **BELUM** | tidak ada | Tambahkan sebagai pengecualian di halaman yang sama, supaya tahun 2027+ pada kolom kedaluwarsa tidak ikut dibuang sebagai anomali |

### Urutan yang disarankan

**SALAH ARAH lebih dulu.** Aturan yang menyesatkan lebih berbahaya daripada aturan yang tidak ada:
kalau tidak ada aturan, agent akan memakai kuota probe dan sering menemukan sendiri; kalau ada
aturan yang salah, ia akan mengikutinya dengan yakin dan hasilnya terlihat masuk akal.

Sesudah itu baru **BELUM**, didahulukan yang paling sering mengubah angka jawaban.

Yang berstatus **SUDAH** tidak boleh disentuh — daftar ini juga berfungsi melindunginya dari
perubahan yang tidak perlu.

> Dokumen ini adalah **acuan perubahan** untuk `context/` dan `skills/`. Perubahan itu sendiri
> belum dikerjakan; tidak ada satu pun berkas context atau skill yang diubah saat dokumen ini
> ditulis.
