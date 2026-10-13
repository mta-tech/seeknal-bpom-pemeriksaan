# 08 — Blueprint Testcase

> Testcase harus menguji kemampuan sistem memahami kebutuhan user dan kondisi data—bukan sekadar mencocokkan angka lama.

---

## 1. Posisi 256 testcase lama

`docs/testcase/` berisi 256 prompt generated/historis.

Corpus itu **berguna untuk**:

- regresi teknis;
- variasi istilah;
- menemukan pola salah-query;
- membandingkan behavior context/skill.

Corpus itu **bukan**:

- representasi frekuensi pertanyaan user nyata;
- source of truth requirement;
- prioritas bisnis;
- definisi metrik;
- bukti bahwa seluruh prompt masih relevan.

Testcase lama harus diaudit relevansinya sebelum dijadikan quality gate.

---

## 2. Hierarki sumber testcase baru

1. kebutuhan user yang terdokumentasi di blueprint;
2. kontrak semantic dan metrik;
3. kondisi live `staging`;
4. skenario positif/ambigu/partial/honest-gap;
5. regression behavior context/skill;
6. corpus lama sebagai bukti historis tambahan.

---

## 3. Metadata minimum testcase

| Field | Isi |
|---|---|
| `persona` | operator/supervisor/pusat/pimpinan/analis |
| `intent` | monitoring/compliance/risk/TL/evaluation/pattern/report |
| `prompt` | bahasa natural/verbatim, tidak dipoles untuk PASS |
| `decision_goal` | keputusan apa yang ingin dibuat |
| `entity` | pemeriksaan/sarana/petugas/item/produk/event |
| `grain` | apa yang dihitung |
| `scope` | periode/UPT/lokasi/jenis sarana/komoditi |
| `metric_contract` | definisi metrik |
| `expected_route` | fact/bridge/dim |
| `expected_clarification` | jika ambigu |
| `answerability` | ready/rule/decision/unavailable |
| `expected_shape` | angka/tabel/chart/narasi/evidence |
| `required_evidence` | evidence yang wajib |
| `anti_trap` | klaim/filter yang dilarang |
| `verification_date` | kapan data diverifikasi |
| `canonical_sql` | hanya jika SQL-answerable |

---

## 4. Empat kelas testcase

### A. Ready — jawaban langsung

Contoh:

> Berapa pemeriksaan yang dilakukan BBPOM Bandung pada 2025?

Menguji:

- entity kasus;
- Balai pelaksana;
- periode;
- count distinct.

### B. Rule — butuh routing/normalisasi

Contoh:

> Kategori temuan produk apa yang dominan per regional?

Menguji:

- expand jsonb category;
- draft filter;
- `regional_name`;
- kasus vs baris.

### C. Decision — butuh klarifikasi/keputusan bisnis

Contoh:

> Berapa temuan Penerimaan tahun ini?

Ekspektasi:

- tidak langsung menghitung `opsi='no'`;
- menjelaskan bahwa opsi bercampur;
- meminta definisi ketidaksesuaian atau memakai kontrak yang disepakati.

### D. Unavailable / honest gap

Contoh:

> Kapan surat TL kasus ini selesai TTE?

Ekspektasi:

- menyatakan status TTE tidak tersedia;
- tidak mengarang dari status workflow;
- menjelaskan data terdekat yang tersedia.

---

## 5. Testcase ambigu wajib menguji klarifikasi

| Prompt ambigu | Klarifikasi yang diharapkan |
|---|---|
| “temuan paling banyak” | checklist, observasi, atau produk? |
| “di Bandung” | Balai pelaksana atau lokasi sarana? |
| “tren penyimpanan” | pelayanan/produksi/keduanya dan metric apa? |
| “inspektur terbaik” | volume/eksposur atau kompetensi? |
| “kasus kritis” | level kasus atau klausul? |
| “tindak lanjut” | saran, CAPA, tindakan produk, atau approval? |

Klarifikasi bukan kegagalan; ia adalah behavior yang benar bila definisi belum cukup.

---

## 6. Positive + anti-trap per rule

Setiap rule minimal punya dua testcase:

### Rule: jumlah pemeriksaan

- positif: `COUNT(DISTINCT fact.id)`;
- anti-trap: join petugas tidak boleh menggandakan kasus.

### Rule: aspek pelayanan

- positif: route ke bridge skor + dim aspek;
- anti-trap: `opsi='no'` tidak dipakai global.

### Rule: temuan produk

- positif: kategori array diexpand;
- anti-trap: baris temuan tidak disebut kuantitas produk.

### Rule: wilayah

- positif: `regional_name` untuk regional;
- anti-trap: regional tidak disebut provinsi sarana.

### Rule: severity

- positif: bedakan kasus vs klausul;
- anti-trap: subset tidak digeneralisasi.

### Rule: free text

- positif: summary + evidence;
- anti-trap: insight tanpa sumber harus fail.

---

## 7. Acceptance criteria jawaban

Jawaban PASS bila:

- intent dan grain tepat;
- route data tepat;
- filter wajib digunakan;
- definisi metrik sesuai kontrak;
- scope disebut;
- coverage/batas data disebut jika parsial;
- bentuk output sesuai kebutuhan persona;
- evidence tersedia bila dibutuhkan;
- tidak ada klaim kausal tanpa bukti;
- tidak ada fabrikasi.

Jawaban FAIL bila:

- angka benar tetapi grain salah;
- memakai bridge salah;
- mencampur pelayanan dan produksi;
- menganggap `no` global;
- menyebut regional sebagai lokasi;
- menyimpulkan kompetensi dari volume;
- menjawab honest-gap dengan angka buatan;
- summary free text tanpa evidence.

---

## 8. Question-space awal untuk batch testcase

Buat batch kecil berdasarkan tujuh kebutuhan:

| Batch | Tema | Skenario awal |
|---|---|---|
| A | monitoring | kasus/Balai/periode/status |
| B | kepatuhan | Penyimpanan pelayanan vs produksi |
| C | risiko | severity kasus vs klausul |
| D | tindak lanjut | severity × CAPA/rekomendasi |
| E | evaluasi | Balai vs Pusat/workflow |
| F | pola | regional/temuan berulang |
| G | antibiotik | available/partial/gap |
| H | free text | summary/evidence/anti-hallucination |

Bangun 8–16 testcase per batch, review dulu, baru perluas. Jangan generate ratusan sekaligus.

---

## 9. Contoh skenario lengkap

```yaml
scenario_id: BPOM-PMR-USR-PENYIMPANAN-01
persona: kepala_balai
intent: compliance_trend
prompt: "Bagaimana tren ketidaksesuaian penyimpanan selama 2024 sampai 2025?"
decision_goal: "menentukan fokus pembinaan"
entity: pemeriksaan_item
grain: "item per varian, tidak digabung"
scope:
  period: [2024, 2025]
metric_contract:
  pelayanan: "rule per area_key penyimpanan"
  produksi: "nilai_aspek Tidak/severity pada path penyimpanan"
expected_route:
  - bridge_pemeriksaan_skor_operasional
  - bridge_pemeriksaan_checklist
expected_clarification: "jenis sarana atau tampilkan dua panel"
answerability: rule
expected_shape: "dua tabel/chart terpisah + coverage"
required_evidence:
  - pemeriksaan_id
anti_trap:
  - "jangan jumlahkan score pelayanan dengan klausul produksi"
  - "jangan pakai opsi=no global"
verification_date: "YYYY-MM-DD"
```

---

## 10. Workflow update testcase lama

1. Kelompokkan 256 testcase menurut intent.
2. Tandai sumber prompt: generated / real / unknown.
3. Cocokkan dengan blueprint kebutuhan.
4. Tandai status: relevant / needs rewrite / duplicate / obsolete / out-of-domain.
5. Periksa metric contract.
6. Periksa data route ke skema current.
7. Refresh canonical SQL/verification date bila tetap relevan.
8. Tambahkan anti-trap/evidence assert.
9. Jangan menghapus atau mengubah prompt natural untuk memaksa PASS.
10. Jalankan per batch kecil dan audit jawaban, bukan hanya verdict.

---

## 11. Definition of done testcase baru

- [ ] ada persona dan decision goal;
- [ ] prompt natural;
- [ ] grain eksplisit;
- [ ] metric contract eksplisit;
- [ ] route sesuai current staging;
- [ ] status answerability;
- [ ] expected shape;
- [ ] evidence/coverage requirement;
- [ ] anti-trap;
- [ ] canonical SQL bila relevan;
- [ ] positive + anti-trap coverage;
- [ ] tidak bergantung angka generated lama sebagai requirement.
