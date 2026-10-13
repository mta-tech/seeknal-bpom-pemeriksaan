# Blueprint Kebutuhan User — Domain Pemeriksaan

> **Tujuan**: mendokumentasikan cara user Wasdis bekerja, informasi yang dibutuhkan, kondisi data `staging`, aturan pemaknaan, bentuk output, serta dasar membangun context/skill/testcase yang relevan.
>
> **Audiens**: stakeholder BPOM, tim Wasdis, tim data, product owner, developer, analis, dan pengembang AI/Seeknal Ask.
>
> **Scope data**: domain Pemeriksaan pada database `staging`. Alur pipeline atau database sumber tidak dibahas di blueprint ini.

Blueprint ini menjawab satu pertanyaan besar:

> **Bagaimana data pemeriksaan yang beragam diterjemahkan menjadi informasi, laporan, dan jawaban AI yang sesuai dengan cara user bekerja dan mengambil keputusan?**

---

## 1. Mengapa blueprint ini dibutuhkan

User tidak hanya membutuhkan dashboard atau SQL. Mereka perlu menelusuri seluruh siklus pemeriksaan:

```text
Objek yang diperiksa
→ standar/SOP yang seharusnya
→ kondisi nyata di lapangan
→ observasi atau ketidaksesuaian
→ tingkat keparahan
→ kesimpulan kasus
→ rekomendasi dan tindak lanjut
→ verifikasi UPT
→ evaluasi Pusat
→ laporan dan keputusan
```

Kondisi datanya kaya, tetapi tidak homogen:

- satu pemeriksaan dapat memiliki banyak petugas, checklist, temuan produk, narasi, dan event approval;
- form pelayanan berbeda dengan form produksi;
- satu kolom dapat memuat beberapa makna bisnis;
- istilah user tidak selalu sama dengan nama tabel atau kode database;
- kebutuhan report berubah menurut stakeholder, periode, komoditi, wilayah, dan isu.

Karena itu, pertanyaan user tidak boleh langsung diterjemahkan menjadi SQL tanpa menentukan konteks, grain, varian form, metrik, dan batas datanya.

---

## 2. Sumber kebenaran

Urutan otoritas yang digunakan:

1. **Kebutuhan dan bahasa user** — diskusi/transkrip, sembilan pertanyaan analitik awal, serta koreksi eksplisit stakeholder.
2. **Kondisi live `staging`** — fakta tabel, grain, bridge, join, coverage, dan kualitas data.
3. **Dokumentasi proses bisnis** — `docs/user_flow/` dan `docs/ERD/`.
4. **Context/skill Seeknal Ask** — artefak implementasi yang harus mengikuti kebutuhan.
5. **Testcase generated lama** — bukti historis/regresi, bukan sumber kebutuhan bisnis.

Setiap klaim harus dikenali sebagai salah satu dari:

| Jenis klaim | Arti |
|---|---|
| **Fakta user** | dinyatakan atau ditunjukkan dalam diskusi/user flow |
| **Interpretasi kebutuhan** | kesimpulan yang ditarik dari beberapa fakta user |
| **Fakta data** | terbukti pada kondisi `staging` |
| **Keputusan terbuka** | definisi bisnis yang belum boleh diputuskan teknis sepihak |

---

## 3. Peta dokumen

| File | Isi | Baca ketika… |
|---|---|---|
| [01-perspektif-user-dan-persona.md](01-perspektif-user-dan-persona.md) | persona, pekerjaan, keputusan, pertanyaan, dan output per user | ingin memahami **siapa yang membutuhkan apa** |
| [02-proses-bisnis-dan-entry-user.md](02-proses-bisnis-dan-entry-user.md) | apa yang di-entry user dan makna bisnisnya | ingin tahu **kegiatan lapangan menjadi data apa** |
| [03-kebutuhan-informasi-dan-pertanyaan-user.md](03-kebutuhan-informasi-dan-pertanyaan-user.md) | tujuh kelas kebutuhan + sembilan pertanyaan fondasi | ingin tahu **user biasanya bertanya apa** |
| [04-kondisi-data-dan-kesiapan.md](04-kondisi-data-dan-kesiapan.md) | variasi data serta status kesiapan jawaban | ingin tahu **apa yang bisa dijawab sekarang** |
| [05-kamus-bahasa-user-dan-semantik.md](05-kamus-bahasa-user-dan-semantik.md) | bahasa user → arti bisnis → grain → data → klarifikasi | ingin mencegah salah tafsir istilah |
| [06-kontrak-metrik-dan-aturan-jawaban.md](06-kontrak-metrik-dan-aturan-jawaban.md) | aturan hitung, routing, validasi, dan auditability | ingin membuat SQL/jawaban yang benar |
| [07-use-case-dan-bentuk-output.md](07-use-case-dan-bentuk-output.md) | skenario stakeholder end-to-end | ingin melihat contoh konkret report/insight |
| [08-blueprint-testcase.md](08-blueprint-testcase.md) | dasar membuat atau memperbarui testcase | ingin membangun testcase yang relevan |
| [09-gap-keputusan-dan-roadmap.md](09-gap-keputusan-dan-roadmap.md) | keputusan bisnis, gap data, gap agent, urutan kerja | ingin menentukan prioritas berikutnya |
| [10-blueprint-nppza-ekspor-impor-keamanan-mutu.md](10-blueprint-nppza-ekspor-impor-keamanan-mutu.md) | kebutuhan & kondisi data NPPZA (narkotika/psikotropika/prekursor), ekspor-impor, keamanan mutu — diverifikasi live 13 Okt 2026 | pertanyaan menyentuh **obat berkontrol / impor / keamanan mutu** |

Dokumen teknis rinci tetap berada di:

- [ERD & Data Dictionary](../ERD/README.md)
- [Alur entry dari capture](../user_flow/alur-entry-dari-capture.md)
- [Pemetaan form ke database](../user_flow/pemetaan-form-ke-database.md)
- [Kondisi staging per flow](../user_flow/pemetaan-entry-per-flow-ke-staging-NEW.md)
- [Sembilan pertanyaan analitik awal](../user_flow/pertanyaan-analitik.md)

---

## 4. Ringkasan kebutuhan dalam satu layar

### Tujuh kebutuhan utama user

```text
1. Monitoring kegiatan
   Apa, siapa, kapan, dan di mana diperiksa?

2. Penilaian kepatuhan
   Aspek/klausul apa yang sesuai atau tidak?

3. Penilaian risiko
   Minor, Major, Kritis, MK/TMK, dan grade.

4. Respons dan tindak lanjut
   Pembinaan, CAPA, penarikan, pemusnahan, rekomendasi.

5. Evaluasi keputusan
   Apakah keputusan UPT dan Pusat konsisten?

6. Analisis pola
   Tren, hotspot, temuan berulang, regional, antibiotik.

7. Komunikasi
   Ringkasan free text, tabel, chart, dan laporan sesuai audiens.
```

### Empat fondasi teknis

```text
Semantic/business glossary
+ kontrak metrik per field/area_key
+ routing fact/bridge berdasarkan varian
+ evidence trace ke kasus dan teks asli
```

---

## 5. Status kesiapan kebutuhan

| Status | Arti | Contoh |
|---|---|---|
| **Siap langsung** | struktur dan definisi metrik jelas | jumlah kasus per Balai/tahun, status workflow |
| **Siap dengan rule** | data ada, wajib routing/join/normalisasi | inspektur × jenis sarana, kategori temuan produk |
| **Butuh keputusan bisnis** | data ada, definisi jawaban belum disepakati | Penerimaan/Pengembalian sebagai “temuan”, arti tren |
| **Tidak tersedia** | atribut tidak direkam atau detail tidak ada | status TTE, isi attachment, history sebelum/sesudah edit |

---

## 6. Prinsip dasar jawaban AI

Sebelum menjawab, sistem harus menentukan:

```text
Pertanyaan user
→ intent
→ entitas dan grain
→ populasi/jenis sarana
→ varian form
→ definisi metrik
→ fact/bridge/dim yang relevan
→ coverage dan kualitas
→ bentuk jawaban
→ evidence dan batas jawaban
```

AI tidak boleh:

- memakai `opsi='no'` sebagai definisi global temuan;
- menggabungkan skor pelayanan dengan cacah klausul produksi;
- menyamakan kasus, item, produk, kuantitas, dan penugasan;
- menyebut hubungan sebagai sebab-akibat tanpa bukti;
- membuat insight free text tanpa tautan ke kasus dan teks sumber;
- memakai 256 prompt generated sebagai representasi kebutuhan user.

---

## 7. Posisi sembilan pertanyaan awal

Sembilan pertanyaan awal tetap penting sebagai fondasi:

- **Q1–Q7**: tren temuan per aspek;
- **Q8**: aktivitas inspektur;
- **Q9**: kategori temuan, kekritisan, dan regional.

Namun diskusi user memperluas kebutuhan ke:

- konsistensi rekomendasi terhadap severity;
- perbandingan keputusan Balai dan Pusat;
- backlog dan bottleneck;
- laporan tematik antibiotik;
- ringkasan free text;
- temuan berulang pada sarana yang sama;
- report berbeda untuk UPT, Pusat, dan pimpinan;
- pemetaan istilah dan singkatan.

---

## 8. Hubungan dengan testcase lama

Folder `docs/testcase/` berisi **256 prompt generated/historis**. Corpus itu berguna untuk regresi, tetapi:

- bukan daftar pertanyaan user nyata;
- bukan source of truth requirement;
- angka/assert lama dapat drift;
- beberapa prompt tidak lagi sesuai struktur `staging` sekarang;
- relevansinya harus diaudit sebelum dijadikan quality gate.

Testcase baru atau testcase yang diperbarui harus mengikuti [08-blueprint-testcase.md](08-blueprint-testcase.md).

---

## 9. Definisi selesai

Blueprint ini dianggap berhasil bila pembaca baru dapat menjawab tanpa membaca 256 testcase:

- siapa user dan keputusan apa yang mereka buat;
- apa yang mereka entry;
- apa arti observasi, temuan, severity, dan rekomendasi;
- informasi apa yang mereka butuhkan;
- bagaimana bahasa user dipetakan ke data;
- apa yang siap dijawab dan apa batasnya;
- seperti apa report yang berguna;
- bagaimana membuat testcase yang relevan dan dapat diaudit;
- keputusan dan gap apa yang masih terbuka.
