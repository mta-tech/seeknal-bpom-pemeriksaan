# 04 — Kondisi Data dan Kesiapan Jawaban

> File ini menjelaskan kondisi `staging` dengan bahasa stakeholder: **data apa yang ada, variasinya bagaimana, apa yang bisa dijawab, dan apa batasnya**. Detail tabel/kolom berada di [ERD](../ERD/README.md).

---

## 1. Kondisi umum

| Fakta | Kondisi |
|---|---|
| Kasus pemeriksaan | 259.348 |
| Tabel dapat dibaca | 27 (19 domain Pemeriksaan + 8 dim general) |
| Petugas | 553.380 penugasan, 2.975 inspektur unik |
| Checklist produksi | 7.388.165 item |
| Item berskor pelayanan | 1.521.315 item |
| Temuan produk | 303.521 baris |
| Narasi pemeriksaan | 525.894 potongan |
| Event approval | 1.320.680 |
| Kasus tanpa bridge detail | 15.412 (5,9%) |

Kesimpulan umum:

> Header kasus sangat lengkap. Kedalaman detail pemeriksaan berbeda menurut jenis form, jenis sarana, dan tahap entry.

---

## 2. Enam bentuk data pemeriksaan

### A. Pelayanan berskor

Tabel: `bridge_pemeriksaan_skor_operasional`.

- punya label aspek (`area_key` → `dim_pemeriksaan_aspek`);
- mencakup Apotek, PKM, Klinik, Toko Obat, dan Rumah Sakit;
- cocok untuk kepatuhan per aspek;
- `opsi` dan `score` tidak homogen.

**Kesiapan**: siap dengan rule per `area_key`.

### B. Produksi berklausul

Tabel: `bridge_pemeriksaan_checklist`.

- punya path, nilai, catatan, dan sebagian severity;
- mencakup Pangan/Pangan MD/Pangan IRT, Kosmetik, OT, Suplemen, PBF/IFK/IFP;
- cocok untuk cacah klausul tidak sesuai;
- hanya sebagian path dapat dipetakan ke aspek.

**Kesiapan**: siap dengan rule/routing; aspek tertentu parsial.

### C. Observasi GMP

Tabel: `bridge_pemeriksaan_temuan_observasi`.

- kode observasi dapat diterjemahkan;
- `kriteria` 1–4 belum punya arti bisnis yang terkonfirmasi.

**Kesiapan**: siap sebagian; butuh keputusan kamus severity/kriteria.

### D. Vaksin

Tabel: `bridge_pemeriksaan_vaksin`.

- 19 section;
- mempunyai opsi, jumlah, observasi, perbaikan, intervensi;
- belum mempunyai dim label aspek formal.

**Kesiapan**: siap untuk daftar/profil; butuh semantic mapping untuk agregasi aspek.

### E. Narasi bebas

Tabel: `bridge_pemeriksaan_narasi_faskes`, `fact_pemeriksaan_narasi`, catatan checklist/approval.

- kaya konteks;
- dapat dibersihkan, diringkas, dan dikelompokkan;
- tidak boleh langsung dihitung sebagai klausul.

**Kesiapan**: siap untuk NLP dengan evidence trace.

### F. Temuan produk

Tabel: `bridge_pemeriksaan_temuan`.

- produk, kategori, tindakan, kuantitas, harga, negara, draft flag;
- kategori berupa jsonb array;
- jumlah kasus, baris produk, kuantitas, dan nilai ekonomi berbeda grain.

**Kesiapan**: siap dengan rule join, draft filter, dan quality guard.

---

## 3. Status kesiapan per kebutuhan

### Siap langsung

| Kebutuhan | Data |
|---|---|
| Jumlah pemeriksaan per periode/Balai/jenis sarana/komoditi | `fact_pemeriksaan` + dim |
| Status workflow dan backlog | `status_id` + `dim_status_code` |
| Kesimpulan MK/TMK | `kesimpulan_balai_id` + dim kesimpulan |
| Grade produksi | `grade` |
| Daftar petugas per kasus | bridge petugas + dim user |
| Regional Balai | `dim_balai.regional_name` |
| Narasi/catatan per kasus | fact/bridge narasi |

### Siap dengan rule

| Kebutuhan | Rule wajib |
|---|---|
| Inspektur × jenis sarana | `COUNT(DISTINCT pemeriksaan_id)` |
| Aspek pelayanan | rule per `area_key`, jangan global `opsi='no'` |
| Klausul produksi | route berdasarkan `flag_varian_datas`, pilih nilai sesuai intent |
| Kategori temuan produk | expand jsonb array, cast text, filter draft |
| Regional + temuan | bedakan regional Balai vs lokasi sarana |
| Kekritisan | bedakan level kasus vs klausul |
| Tindak lanjut | bedakan `tl_saran`, CAPA, tindakan produk, narasi, approval |
| Tren | definisikan kasus/item/persentase/TMK terlebih dahulu |

### Butuh keputusan bisnis

| Kebutuhan | Keputusan yang dibutuhkan |
|---|---|
| Penerimaan sebagai “temuan” | apa indikator ketidaksesuaiannya? `opsi` berisi peran/proses |
| Pengembalian sebagai “temuan” | bagaimana membaca JSON/prosedur mutasi/retur? |
| Pemusnahan sebagai “temuan” | apakah N/A/yes cukup; di mana indikator tidak sesuai? |
| Gabungan pelayanan + produksi | satuan apa yang boleh dibandingkan? |
| Definisi tren | kasus, item, persentase kepatuhan, atau TMK? |
| Definisi wilayah | Balai, regional, lokasi sarana, atau wilayah kerja administratif? |
| Severity → rekomendasi | aturan proporsionalitas resminya apa? |
| Arti kriteria observasi 1–4 | kamus bisnis belum terkonfirmasi |

### Tidak tersedia

| Kebutuhan | Kondisi |
|---|---|
| Status TTE | tidak ada field |
| Isi lampiran | hanya ID file |
| Version history edit | nilai lama tertimpa |
| Detail checklist Kosmetik CPKB | 2.610 kasus tanpa bridge |
| Metode inspeksi seluruh kasus | hanya ±1,6% terisi |
| Severity per klausul untuk Kosmetik/OT/Suplemen | tidak tersedia |
| Kompetensi/sertifikasi formal inspektur | tidak ada atributnya |

---

## 4. Variasi data yang sering menyesatkan

### `opsi`

Bisa berarti:

```text
jawaban kepatuhan
+ jabatan/orang
+ pilihan prosedur
+ JSON object
```

Contoh nyata:

```text
yes, no, mostly, rarely, N/A
apoteker, ttk, Apoteker atau TTK
{"mutasi":"yes"}
```

Konsekuensi: `WHERE opsi='no'` tidak valid secara global.

### `score`

Bisa berarti:

- skor item 0–100;
- skor akumulasi >100;
- N/A/kosong.

Konsekuensi: `AVG(score)` mentah tidak valid tanpa klasifikasi area/field.

### `nilai_aspek`

Bisa berarti:

- konformitas: Ya/Tidak/OK/Tidak Berlaku;
- grade: B/T/C/K;
- severity: Minor/Major/Kritis/Serius/Kritikal;
- status: Lanjut.

Konsekuensi: filter harus berdasarkan intent dan sumber pola.

### “Temuan”

Bisa berarti:

1. item aspek tidak sesuai;
2. klausul Tidak/severity;
3. observasi GMP;
4. produk bermasalah;
5. alasan TMK dalam narasi.

Konsekuensi: wajib klarifikasi atau routing intent.

---

## 5. Grain: angka yang terlihat mirip tetapi berbeda

| Grain | Makna |
|---|---|
| Kasus pemeriksaan | satu kunjungan/kasus |
| Sarana unik | objek usaha unik |
| Penugasan petugas | satu petugas dalam satu kasus |
| Item skor/checklist | satu pertanyaan/klausul |
| Baris temuan produk | satu produk bermasalah dalam kasus |
| Kuantitas temuan | jumlah fisik produk |
| Nilai ekonomi | harga × kuantitas |
| Event approval | satu perpindahan/aksi workflow |

Contoh kesalahan:

- menghitung petugas dengan `COUNT(*)` lalu menyebutnya jumlah pemeriksaan;
- menghitung baris produk lalu menyebutnya jumlah fisik produk;
- menjumlah item checklist pelayanan dan produksi tanpa menyamakan satuan.

---

## 6. Wilayah: tiga konsep berbeda

| Konsep | Data | Menjawab |
|---|---|---|
| Balai/UPT pelaksana | `fact_pemeriksaan.balai_id` | siapa yang melakukan pemeriksaan? |
| Regional Balai | `dim_balai.regional_name` | kelompok operasional mana? |
| Lokasi sarana | `dim_sarana.provinsi_id/kabupaten_id` | objek berada di mana? |

“Wilayah kerja UPT” belum otomatis sama dengan lokasi sarana; bila diminta, perlu definisi/cakupan administratif yang jelas.

---

## 7. Kekritisan dan coverage

Kekritisan tersedia pada dua grain:

### Per kasus

- `kritis_count`, `major_count`, `minor_count`;
- `level_kesimpulan`;
- tersedia pada subset kasus.

### Per klausul

- `bridge_pemeriksaan_checklist.nilai_aspek`;
- tersedia kuat pada Pangan/Pangan MD/Pangan IRT/PBF/IFK/IFP;
- tidak tersedia pada Kosmetik/OT/Suplemen.

Jawaban harus menyebut coverage. Tidak boleh menggeneralisasi subset sebagai kondisi seluruh domain.

---

## 8. Free text dan auditability

Lokasi free text:

- `fact_pemeriksaan_narasi`;
- `fact_pemeriksaan_approval.notes/notes_tl`;
- `bridge_pemeriksaan_checklist.catatan/conformity`;
- `bridge_pemeriksaan_temuan.keterangan`;
- `bridge_pemeriksaan_narasi_faskes.teks`;
- `tl_capa`.

Pipeline insight yang diharapkan:

```text
teks mentah
→ pembersihan
→ ringkasan
→ klasifikasi topik
→ hubungan dengan severity/kesimpulan/TL
→ agregasi pola
→ evidence kasus
```

Setiap insight wajib membawa:

- `pemeriksaan_id`;
- sumber teks/jenis narasi;
- potongan bukti;
- tanggal;
- sarana/UPT;
- severity/kesimpulan terkait;
- status/confidence klasifikasi.

---

## 9. Antibiotik

Kebutuhan user mencakup:

- nama zat aktif;
- jumlah penjualan;
- penjualan tanpa resep;
- satuan;
- pihak yang menyerahkan;
- penerima/KIE;
- pencatatan dan pelaporan;
- ketidaksesuaian dan tindak lanjut.

Kondisi:

- sekitar 25.780 kasus memiliki section `tx_fast_moving_antibiotika`;
- sebagian aturan antibiotik sudah muncul dalam Penyerahan/Pencatatan;
- detail zat aktif/volume belum tersedia sebagai bridge terstruktur di `staging`.

Status: kebutuhan valid dan prioritas data konkret, tetapi belum siap dijawab penuh.

---

## 10. Referensi teknis

- routing bridge: [ERD 04](../ERD/04-routing-bridge.md)
- aturan wajib: [ERD 05](../ERD/05-aturan-wajib.md)
- kamus/dimensi: [ERD 06](../ERD/06-kamus-dan-dimensi.md)
- kualitas/gap: [ERD 07](../ERD/07-kualitas-data.md)
