# 02 — Spesifikasi 23 Halaman Context

> **Revisi 13 Okt 2026 (v6-nppza)**: +2 halaman baru (`22`, `25`) dari blueprint NPPZA; matriks §1 dan kepemilikan §4 diperbarui.
>
> Setiap halaman baru wajib mengikuti urutan baku: **(1) baris pemicu · (2) apa yang diputuskan · (3) tabel keputusan · (4) cara mencari · (5) jebakan (gejala + cara memastikan) · (6) batas/honest gap · (7) Rute**.
>
> Batas: ≤200 baris · tanpa angka hasil query · satu aturan satu pemilik.

---

## 1. Daftar halaman dan pemilik aturannya

| # | Halaman | Pemicu (trigger words) | Yang diputuskan | Sumber | Status |
|---|---|---|---|---|---|
| 1 | `00-menghitung` | semua pertanyaan data | entity · grain · tanggal kanonik · eksklusi · uji penyempitan vs eksklusi | ERD 05 §A–C · blueprint 06 §1–2 | ditulis ulang |
| 2 | `01-peta-data-dan-routing` | semua; "kenapa kosong" | 27 tabel; `flag_varian_datas` → bridge; salah tabel = kosong tanpa error | ERD 02 · ERD 04 | **baru** |
| 3 | `05-filter-katalog` | label panel | label panel → kolom/kode, atau honest gap | blueprint 05 · ERD 03/06 · verifikasi 07 | **baru** |
| 4 | `10-sarana-dan-fasilitas` | apotek · PBF · pangan MD · toko obat · PKM · klinik · RS · produksi/distribusi/pelayanan | jenis sarana vs golongan; `dim_sarana`; wilayah; soft-delete | ERD 06 §1/§6 | ditulis ulang |
| 5 | `15-tujuan-pemeriksaan` | rutin · kasus · intensifikasi · sertifikasi · hari besar | `tujuan_id` → kamus; eksklusi unit pusat | ERD 06 | disesuaikan |
| 6 | `20-komoditi` | obat · kosmetik · pangan · OT · suplemen · narkotika | `klasifikasi_id` → `JENIS_KLASIFIKASI`; wajib `type` | ERD 03/06 | ditulis ulang |
| 7 | `30-kesimpulan` | MK · TMK · TTP · TDP · TMBB · memenuhi/tidak memenuhi | FK kesimpulan; kelompok CPOB; kode vaksin; review Pusat parsial | ERD 06 §3 | ditulis ulang |
| 8 | `31-status-dan-alur` | draft · verifikasi · selesai · macet · bottleneck | 16 status + `domain`; label dari luar; "siapa menyetujui" = P5 | ERD 06 §4 · ERD 01 §7 | ditulis ulang |
| 9 | `35-kepatuhan-aspek` | pengadaan · penerimaan · penyimpanan · penyerahan · pengembalian · pencatatan · pemusnahan · pendistribusian | **kontrak `opsi`/`score` per `area_key`**; `COALESCE` label | ERD 04 §6 · blueprint 06 §3 · verifikasi 07 | **baru** |
| 10 | `37-klausul-dan-severity` | klausul · tidak sesuai · minor/major/kritis · severity | `path`/`nilai_aspek`; severitas per jenis; satuan beda dari pelayanan | ERD 04 §6 · ERD 07 §4 | **baru** |
| 11 | `40-temuan-produk` | TIE · kedaluwarsa · rusak · BKO · sitaan · dimusnahkan | array jsonb; join `master_data_id::text`; draft; bucket tak terpetakan; 4 grain | ERD 03/05 §E · verifikasi 07 | ditulis ulang |
| 12 | `41-nilai-dan-negara` | nilai · harga · rupiah · kerugian · negara · impor | `jumlah_temuan`/`harga_total`; guard kualitas; grain kuantitas vs nilai | ERD 05 §I | ditulis ulang |
| 13 | `45-observasi-dan-vaksin` | observasi · GMP · kriteria · vaksin · imunisasi · narasi | observasi + `kriteria` (belum terkonfirmasi); 19 section vaksin; 8 section narasi | ERD 02 §4/§6 | **baru** |
| 14 | `50-jenis-pangan` | MD · IRT · UMKM · AMDK · jenis pangan | `jenis_pangan_kode` multi-kamus; `CLASS_SARANA` | ERD 03 Pola 4 | disesuaikan |
| 15 | `60-mutu-dan-tindak-lanjut` | grade · CAPA · tindak lanjut · sanksi · pembinaan · rekomendasi | `grade`; counter/level; `tl_saran` multi-kamus; CAPA teks; narasi | ERD 05 §E · ERD 06 §3 | ditulis ulang |
| 16 | `70-petugas` | inspektur · petugas · beban kerja · jam terbang | `COUNT(DISTINCT)`; eksposur ≠ kompetensi; user tak terdaftar | ERD 05 §H · ERD 06 §6 | ditulis ulang |
| 17 | `80-waktu-dan-durasi` | tahun · bulan · triwulan · tren · durasi · lama | `tgl_start`/`tgl_end`; durasi dari approval; frontier data | ERD 05 §G | ditulis ulang |
| 18 | `85-target-capaian` | target · capaian · realisasi · persentase | `dim_balai.target_sampling`/`target_sarana` (terisi penuh) | ERD 02 §6 | disesuaikan |
| 19 | `90-kualitas-data` | belum · tanpa · kosong · tidak terisi · tidak melaporkan | sentinel · soft-delete · kolom mati · coverage · kategori tak terpetakan | ERD 05 §F/§I · ERD 07 | ditulis ulang |
| 20 | `95-batas-domain` | TTE · lampiran · kompetensi · riwayat edit · antibiotik detail | honest gap + protokol 3 kalimat | blueprint 04 §3/§9 | disesuaikan |
| 21 | `97-glossary-istilah-user` | temuan · wilayah · jumlah · tren · kritis · tindak lanjut · selesai · inspektur terbaik | istilah user → konsep → grain → ambiguitas → klarifikasi | blueprint 05 | **baru** |
| 22 | `22-komoditi-pbf-dan-fokus` | NPP · obat berkontrol · komoditi PBF · fokus pemeriksaan · NPP dan OOT | dua bridge distribusi; dua grain NPP; join `master_data_id::text` + `type`; cakupan PBF/IFK/IFP | blueprint 10 §2/§3 (A1/A5) · verifikasi live 13 Okt | **baru (v6)** |
| 23 | `25-profil-sarana-faskes` | prekursor · jenis obat kelola · profil faskes · personel faskes | `prekursor` text t/f + cakupan form; `jenis_obat` JSON-string → parse; personel | blueprint 10 §3 (A4) · verifikasi live 13 Okt | **baru (v6)** |

**Halaman lama `11-klasifikasi-distribusi.md` dilebur** ke `05-filter-katalog.md` karena kolomnya tidak ada di `staging` (temuan 2).

---

## 2. Rincian enam halaman baru

### 2.1 `01-peta-data-dan-routing.md`

**Tabel wajib — routing varian → bridge:**

| `flag_varian_datas` | Kasus | Baca bridge |
|---|---:|---|
| `pola1_direct` | 107.778 | `bridge_pemeriksaan_checklist` |
| `clusterC_skor` | 64.243 | `bridge_pemeriksaan_skor_operasional` |
| `pola1_nested` | 61.266 | `bridge_pemeriksaan_checklist` |
| `pola1_observation` | 10.421 | `bridge_pemeriksaan_checklist` |
| `clusterC_vaksin` | 7.697 | `bridge_pemeriksaan_vaksin` |
| `pola2_klasifikasi` | 4.137 | `bridge_pemeriksaan_temuan_observasi` |
| `clusterF_cpkb` | 2.610 | **tidak ada bridge** |
| `clusterC_naratif` | 1.182 | `bridge_pemeriksaan_narasi_faskes` |
| `lainnya` | 14 | **tidak ada bridge** |

**Jebakan wajib:** membaca bridge yang salah untuk satu kasus → hasil kosong **tanpa error**. Cara memastikan: periksa `flag_varian_datas` kasus itu lebih dulu.

**Rute:** tabel/kolom → `02` ERD; kontrak isi → `35`/`37`; gap → `90`.

### 2.2 `05-filter-katalog.md`

**Tabel wajib:** label panel → kolom/kode → halaman pemilik, dengan kolom **status** (ada / ada-dengan-catatan / **tidak ada**). Wajib memuat tiga honest gap yang sudah terverifikasi:

| Label panel | Keputusan |
|---|---|
| Klasifikasi distribusi | **tidak ada kolom** → P5, sebutkan batas; jangan pakai `distribusi_provinsi_kode` (itu tujuan distribusi Pangan MD) |
| Status label | kolom ada, isi kosong (0/35) → label diambil dari luar; jangan mengarang |
| Legal | `dim_sarana.legal_id` merujuk **2 kamus** → jangan filter satu `type` |

**Jebakan wajib:** menebak kolom dari nama label panel → query jalan, makna beda.

### 2.3 `35-kepatuhan-aspek.md`

**Tabel wajib — kontrak per `area_key`** (contoh terverifikasi, halaman memuat seluruh 47):

| `area_key` | Pertanyaan form | Vocab `opsi` nyata | Sinyal temuan | Catatan |
|---|---|---|---|---|
| `tx_pemusnahan_obat` | prosedur pemusnahan | N/A · yes · null | **tidak ada** → laporkan apa adanya | jangan klaim 0 temuan sebagai fakta kuats |
| `tx_penerimaan_obat` | siapa yang menerima | jabatan + Ya/Tidak | campuran | ada duplikat ejaan |
| `tx_pengembalian_mutasi` | prosedur mutasi | JSON `{"mutasi":…}` | di dalam objek | jangan bandingkan string |
| `tx_penyimpanan_obat` | item penyimpanan | `opsi` kosong; sinyal di `score`+key item | dari `score` | bukti bahwa kontrak per area wajib |

**Aturan wajib:** label aspek selalu `COALESCE(aspek_ktl_nama, aspek_label)`; normalisasi ejaan sebelum mengelompokkan (`Lainnya` vs `lainnya`, `Asisten Apoteker` vs `asisten`).

### 2.4 `37-klausul-dan-severity.md`

**Tabel wajib — vocab `nilai_aspek` (15 nilai) dan maknanya:**

| Kelompok | Nilai | Dipakai untuk |
|---|---|---|
| konformitas | `OK` · `Ya` · `Tidak` · `Tidak Berlaku` | cacah sesuai/tidak |
| grade | `B` · `T` · `C` · `K` | kelompok penilaian huruf |
| severity | `Minor` · `Major` · `Kritis` · `Serius` · `Kritikal` | tingkat keparahan |
| status | `Lanjut` | status tindakan |
| kosong | — | perlu dilaporkan bila relevan |

**Batas wajib:** severitas per klausul tidak tersedia untuk semua jenis sarana; satuan berbeda dari panel pelayanan → tidak dijumlahkan.

### 2.5 `45-observasi-dan-vaksin.md`

Tiga sumber dalam satu halaman: observasi GMP (`observasi_kode` + `kriteria` **belum punya arti bisnis terkonfirmasi**), vaksin (19 `section_key`, belum punya kamus label aspek), narasi faskes (8 section, teks bebas → bukan cacah).

**Jebakan wajib:** memperlakukan narasi sebagai item yang bisa dihitung.

### 2.6 `97-glossary-istilah-user.md`

Inti: istilah user → konsep → grain → ambiguitas → pertanyaan klarifikasi. Wajib memuat minimal:

| Istilah user | Ambiguitas | Klarifikasi |
|---|---|---|
| temuan | aspek / klausul / observasi / produk / alasan TMK | "temuan yang dimaksud yang mana?" |
| wilayah | Balai pelaksana / regional / lokasi sarana / wilayah kerja | pilih salah satu |
| jumlah | kasus / sarana unik / item / produk / kuantitas / penugasan | sebutkan grain |
| tren | kasus / item / persentase kepatuhan / proporsi TMK | sebutkan metrik |
| kritis | level kasus / severitas klausul | bedakan |
| tindak lanjut | saran / CAPA / tindakan produk / approval | bedakan |
| selesai | `FINISHED` / `FINISHED_PUSAT` | sebutkan jalur |
| inspektur terbaik | volume / eksposur / kompetensi | hanya volume & eksposur yang tersedia |

---

## 3. Struktur baku isi setiap halaman (template)

```markdown
# <judul singkat>

<trigger words, dipisah · >

## Apa yang halaman ini putuskan
<1–2 baris>

## Tabel keputusan
| kata / label dalam pertanyaan | entity / kolom / filter |

## Matriks operasi per kolom berkod
| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |

## Cara mencari bila nilainya tidak stabil
<perintah SELECT DISTINCT pada kolom yang tepat, sebutkan type kamus bila perlu>

## Jebakan
| gejala | penyebab | cara memastikan |

## Batas & honest gap
<termasuk panel-vs-kanon bila ada>

## Rute
- <kondisi> → **lihat** `<halaman>`

## Manifes
| Tabel | Kolom | Literal nilai |
```

**Matriks operasi wajib** ([10](10-adopsi-rancangan-v2.md) §3.1): satu kolom berperilaku berbeda saat disaring, dikelompokkan, di-join, dan diperingkat. Sel tanpa jebakan ditulis **"biasa"** supaya terlihat sudah dipertimbangkan.

**Manifes wajib** ([10](10-adopsi-rancangan-v2.md) §3.4): daftar tabel/kolom/literal yang diajarkan halaman itu, sehingga skrip verifikasi dapat membuktikan keabsahannya ke database — dan mendeteksi konsep yang belum menyeberang ke context.

Wajib punya matriks operasi: `opsi` · `nilai_aspek` · `kategori_kode` · `legal_id` · `tl_saran` · `jenis_pangan_kode` · `status_label` · `flag_varian_datas` · `dihapus_di_sumber`.

### 3b. Daftar karantina (bagian baku di `90-kualitas-data.md`)

Kolom/tabel yang **tidak boleh dikutip**, dengan alasan dan penggantinya:

| Jangan dikutip | Alasan | Pakai ini |
|---|---|---|
| `distribusi_provinsi_kode` sebagai "klasifikasi distribusi" | tujuan distribusi pabrik Pangan MD | honest gap |
| `dim_status_code.status_label` | terisi 0/35 | `status_code` |
| `legal_id` dengan filter satu `type` | merujuk 2 kamus | tampilkan `type` sebagai hasil |
| `opsi` sebagai penanda temuan global | maknanya per `area_key` | kontrak `35` |
| `nilai_aspek` sebagai satu konsep | memuat 4 makna | pisahkan konformasi/grade/severity |
| `sediaan_kode` · `unit_id` · `penelusuran_id` · `kasus_id` · `metode_inspeksi` · `tl_ba_pusat` · `tl_attachment_pusat` | praktis kosong | jangan dipakai sebagai penyaring |
| `dim_produk.is_imported` | bernilai sama di seluruh baris | kolom lain |
| tabel domain pengawasan | `SELECT` ditolak | `95-batas-domain` |

Aturan: larangan tanpa pengganti akan dilanggar.

---

## 4. Matriks kepemilikan aturan (anti-duplikasi)

| Aturan | Pemilik tunggal |
|---|---|
| entity · grain · tanggal kanonik · eksklusi · uji penyempitan | `00` |
| daftar tabel · routing flag → bridge | `01` |
| label panel → kolom/kode · honest gap panel | `05` |
| jenis sarana vs golongan · soft-delete sarana | `10` |
| tujuan pemeriksaan | `15` |
| jenis komoditi | `20` |
| makna kesimpulan · kode CPOB · kode vaksin | `30` |
| status & tahap alur | `31` |
| kontrak `opsi`/`score` per `area_key` | `35` |
| kontrak `nilai_aspek`/severity | `37` |
| kategori temuan · draft · bucket tak terpetakan · 4 grain | `40` |
| kualitas angka nilai/kuantitas | `41` |
| observasi · vaksin · narasi | `45` |
| jenis pangan | `50` |
| mutu & tindak lanjut | `60` |
| petugas | `70` |
| waktu & durasi | `80` |
| target | `85` |
| sentinel · soft-delete · coverage | `90` |
| batas domain | `95` |
| ambiguitas istilah user | `97` |
| bridge komoditi/fokus distribusi & dua grain NPP | `22` |
| kolom profil faskes (`prekursor`, `jenis_obat`) & personel faskes | `25` |

Aturan `COALESCE` label aspek hidup di `35`; `00` hanya menautkannya, tidak menuliskannya ulang.

---

## 5. Batas yang mengikat semua halaman

| Batas | Alasan |
|---|---|
| tanpa angka hasil query | mencegah jawaban hafalan dan basi |
| tanpa daftar kode tanpa jalur pencarian | menjaga kemampuan menemukan |
| ≤200 baris | `read_max_lines: 500`; satu halaman harus muat sekali baca |
| menautkan ERD, tidak menyalin | context = instruksi tindakan; ERD = referensi kondisi |
| dilarang memuat istilah RPO (§ [01](01-temuan-dasar.md) §6) | mencegah bocornya aturan domain lain |
