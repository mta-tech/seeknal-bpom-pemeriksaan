# 04 — Spesifikasi Perubahan Skill

> Skill adalah lapisan **penegakan**: ia tidak memuat aturan data (itu tugas `context/`), tetapi memaksa urutan, anggaran, dan pemeriksaan sebelum menjawab.

---

## 1. Skill yang ada dan nasibnya

| Skill | Path sekarang | Nasib |
|---|---|---|
| `bpom-analyst` | `seeknal/skills/bpom-analyst/SKILL.md` | **ditulis ulang** |
| `visualize-chart` | `seeknal/skills/visualize-chart/SKILL.md` | **disesuaikan** |
| `bpom-forecaster` | `seeknal/skills/bpom-forecaster/SKILL.md` | **ditulis ulang** (19 kemunculan skema lama) |
| `detect-anomaly` | `seeknal/skills/detect-anomaly/SKILL.md` | **ditulis ulang** (7 kemunculan skema lama) |
| `seeknal_agent.yml` | `seeknal_agent.yml` | **tidak berubah** |

Catatan struktur: di project ini skill hidup di `seeknal/skills/`. Di snapshot v5 disalin ke **dua tempat** (`skills/` dan `seeknal/skills/`) mengikuti kebiasaan snapshot RPO, supaya pembandingan dan pemuatan tetap konsisten.

---

## 2. `bpom-analyst` — yang ditambah

Tambahan pada checklist Gate 5:

| # | Check baru | Alasan |
|---|---|---|
| 1 | Menghitung dari bridge yang **sesuai varian** (`flag_varian_datas`) | salah tabel = kosong tanpa error |
| 2 | `COUNT(DISTINCT)` untuk kasus saat menjawab pertanyaan pemeriksaan/temuan | join bridge melipatgandakan baris |
| 3 | Panel pelayanan dan produksi **tidak dijumlahkan**; bila keduanya diminta → dua panel | satuan berbeda (skor vs cacat klausul) |
| 4 | `COALESCE(aspek_ktl_nama, aspek_label)` saat menampilkan aspek | tanpa ini dua aspek bervolume besar hilang |
| 5 | Coverage severitas disebut sebelum menyajikan peringkat/persentase | severitas tidak merata antar jenis sarana |
| 6 | Regional ≠ lokasi sarana | dua makna wilayah berbeda |
| 7 | Korelasi ditulis sebagai asosiasi, bukan sebab-akibat | bukti tidak mendukung kausalitas |
| 8 | Nilai teks dinormalkan sebelum dikelompokkan | ada duplikat ejaan nyata (`Lainnya`/`lainnya`) |

Tambahan pada stop rules:

- larangan menuning filter demi mendekati angka yang "terasa benar";
- bila pertanyaan memuat istilah ambigu (`temuan`, `wilayah`, `tren`, `kritis`, `tindak lanjut`), klarifikasi dulu — bukan menebak jalur;
- bila memilih bridge untuk satu kasus, periksa flag-nya lebih dulu (satu query kecil lebih murah daripada jawaban kosong).

## 3. `bpom-analyst` — yang dihapus

Seluruh rujukan ke skema lama:

`mv_pemeriksaan`, `mv_pemeriksaan_temuan`, `mv_pemeriksaan_petugas`, `mv_pemeriksaan_kategori_temuan`, `mv_pemeriksaan_jenis_pangan`, `mv_pemeriksaan_agg`, `mv_pemeriksaan_log`, `mv_pemeriksaan_timeline`, `mv_kriteria_pemeriksaan`, `target_balai`, `coverage_balai`, `tanggal_mulai`, `tanggal_selesai`, `tanggal_input`, `nama_upt`, `sarana = 'PRODUKSI'`.

---

## 4. `visualize-chart` — yang disesuaikan

- tambah pola **dua panel** untuk satuan berbeda (kepatuhan pelayanan vs cacat klausul produksi);
- larangan menaruh dua satuan berbeda dalam satu sumbu;
- larangan menyajikan chart sebelum angka utama final;
- hapus contoh yang menyebut kolom lama (bila ada).

---

## 5. `bpom-forecaster` dan `detect-anomaly` — wajib disentuh

Keduanya paling banyak memuat skema lama (19 dan 7 kemunculan). Yang berubah:

| Bagian | Sebelum | Sesudah |
|---|---|---|
| Entity seri | `mv_pemeriksaan` | `fact_pemeriksaan` |
| Kolom tanggal seri | `tanggal_mulai` | `tgl_start` |
| Filter eksklusi | tidak ada / versi lama | `is_data_uji IS NOT TRUE` |
| Dimensi pemecahan | `nama_upt`, `jenis_sarana` versi rantai | `balai_id`, `jenis_id` (+ golongan) |
| Metode | ETS fit, window, capture gate, MAPE label | **tidak berubah** |

Yang **tidak** diubah pada keduanya: metode statistiknya, ambang, dan kontrak keluaran. Hanya entity dan kolomnya.

---

## 6. Guard lintas domain di skill

`bpom-analyst` memuat daftar istilah terlarang (sama dengan [01](01-temuan-dasar.md) §6) dan aturan: bila pertanyaan jatuh ke domain lain, jalurnya honest gap — bukan kolom terdekat.

---

## 7. Yang tidak berubah di semua skill

- kerangka gerbang dan sifat blocking;
- query ledger dan anggaran langkah;
- kontrak jawaban (interpretasi kanonik → angka → rincian);
- closing pair: satu chart + satu CSV per jawaban data;
- aturan follow-up.

---

## 8. Kriteria lulus skill

- [ ] tidak ada satu pun nama skema lama tersisa;
- [ ] checklist Gate 5 memuat 8 check baru di §2;
- [ ] stop rule "larangan menuning filter" ada;
- [ ] forecaster & anomaly memakai entity/kolom `staging`;
- [ ] inventaris skill di `SEEKNAL_ASK.md` sama dengan isi folder `skills/` (tidak ada skill yatim);
- [ ] `seeknal/skills` dan `skills` identik (bila snapshot memakai dua lokasi).
