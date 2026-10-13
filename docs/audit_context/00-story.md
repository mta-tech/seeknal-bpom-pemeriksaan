# 00 — Cerita: apa yang dikerjakan, dan insight yang didapat

> Dokumen ini adalah **pintu masuk** folder `audit_context`. Ia menelusuri setiap dokumen rencana:
> apa isinya, apa yang sudah dikerjakan, dan pelajaran yang muncul dari pekerjaan itu.
>
> Terakhir diperbarui: 24 Sep 2026

---

## 1. Status pekerjaan

| # | Fase | Keluaran | Status | Bukti |
|---|---|---|---|---|
| F1 | Verifikasi live kode & nilai | hasil V1–V7 | ✅ selesai | [07-verifikasi-live.md](07-verifikasi-live.md) |
| F2 | Tulis spesifikasi | 11 dokumen di folder ini | ✅ selesai | file 01–10 + README |
| F3 | Verifikasi lanjutan (10 item) | daftar kode/tipe lengkap | ⏳ belum | daftar di [07](07-verifikasi-live.md) §3 |
| F4 | Tulis snapshot context + orchestrator | `24-09-2026 v5-staging-based` | ✅ **selesai (mendahului urutan)** | 1 `SEEKNAL_ASK.md` + 21 halaman |
| F5 | Patch skill | 4 skill | ✅ selesai | `skills/` + `seeknal/skills/` |
| F6 | Linter context | `scripts/lint_context.py` | ✅ selesai — lulus | 12 pemeriksaan |
| F6b | Skrip manifes + kontrol negatif | `scripts/verify_context_manifest.py` | ⏳ belum | butuh query DB |
| F7 | Uji "menemukan" (6 pertanyaan) | bukti agent mencari | ⏳ belum | daftar di [08](08-urutan-kerja-dan-dod.md) §3 |
| F8 | Batch A testcase | folder batch | ⏳ belum | [06](06-plan-testcase.md) |
| F9 | Promosi ke `context/` + `seeknal/skills/` | artefak live | ⏳ belum | syarat di [08](08-urutan-kerja-dan-dod.md) §4 |
| F10 | Batch testcase A–I | 9 batch | ⏳ belum | [06](06-plan-testcase.md) §4 |

Catatan jujur: F4 dan F5 **berjalan lebih dulu** daripada F3, F6b, dan F7. Itu disengaja pada akhirnya —
snapshot dipakai sebagai objek yang diuji, bukan hasil akhir. Tetapi konsekuensinya harus disebut:
**halaman-halaman itu belum pernah diuji ke database maupun ke agent.** Linter hanya membuktikan
konsistensi internal teks, bukan kebenaran klaim ke data.

---

## 2. Cerita per dokumen

### [README.md](README.md) — peta folder
**Isi:** untuk apa folder ini, daftar sumber isi (dengan path), target yang akan dibuat, peta
lama→baru, prinsip yang mengikat.
**Sudah dikerjakan:** semua path sumber dan target diverifikasi ada.
**Insight:** folder ini bukan artefak yang dibaca agent — ia spesifikasi kerja. Memisahkan keduanya
mencegah aturan kerja ikut terbaca agent dan mengotori context.

### [01-temuan-dasar.md](01-temuan-dasar.md) — mengapa penulisan ulang perlu
**Isi:** bukti terukur, empat temuan, gaya yang diadopsi, guard lintas domain.
**Sudah dikerjakan:** pengukuran selesai (159 kemunculan skema lama di 30 file vs 16 file dokumen
kondisi yang benar).
**Insight paling penting:** masalahnya **bukan sekadar isi basi**, melainkan **tidak adanya jembatan**
antara dokumen kondisi (ERD/blueprint) dan dokumentasi pengajaran agent. Kalau hanya find-and-replace
nama tabel, masalahnya akan terulang.

### [02-spec-context-halaman.md](02-spec-context-halaman.md) — rancangan 21 halaman
**Isi:** daftar halaman + template baku + matriks operasi + daftar karantina + kepemilikan aturan.
**Sudah dikerjakan:** 21 halaman sudah ditulis di snapshot, mengikuti template.
**Insight:** aturan yang menempel pada **nama kolom** tidak cukup — kesalahan terjadi pada **operasi**
(menyaring / mengelompokkan / join / memeringkat). Matriks operasi memaksa keempatnya dipikirkan;
prosa membiarkan tiga di antaranya terlupa. Ini diadopsi dari `rancangan-v2.md`.

### [03-spec-seeknal-ask-v5.md](03-spec-seeknal-ask-v5.md) — orchestrator
**Isi:** kerangka v5, isi konkret Canonical Rules, perubahan per gerbang.
**Sudah dikerjakan:** `SEEKNAL_ASK.md` v5 tertulis dengan 5 blok Canonical Rules dan Gate 5 16 check.
**Insight:** koreksi paling menentukan sebaiknya **tidak bersembunyi di halaman** yang mungkin tak
dibuka. Menaruhnya di orchestrator sebagai tabel keputusan — dan menyatakan ia menang atas halaman —
membuatnya selalu terbaca.

### [04-spec-skill.md](04-spec-skill.md) — penegakan
**Isi:** perubahan per skill, 8 check baru, daftar yang dihapus.
**Sudah dikerjakan:** 4 skill ditulis ulang ke versi `staging`.
**Insight:** `bpom-forecaster` (19 kemunculan) dan `detect-anomaly` (7) adalah **yang paling basi** —
dan keduanya justru yang paling senyap salahnya: mereka akan memproyeksikan deret dari tabel yang
tidak ada. Skill yang jarang dipakai tetap harus ikut diperiksa.

### [05-spec-filter-katalog.md](05-spec-filter-katalog.md) — label panel
**Isi:** label panel → kolom/kode, atau honest gap; peringatan kolom pengecoh.
**Sudah dikerjakan:** halaman `05-filter-katalog.md` tertulis.
**Insight:** tiga honest gap nyata — **klasifikasi distribusi tidak punya kolom** (dan ada pengecoh:
kolom provinsi-tujuan distribusi milik profil Pangan MD), **status label kosong seluruhnya**, dan
**legal merujuk dua kamus**. Semua ini jenis kesalahan yang query-nya jalan dengan hasil rapi.

### [06-plan-testcase.md](06-plan-testcase.md) — rencana testcase
**Isi:** skema, empat kelas, batch A–I, katalog anti-trap, siklus hidup, larangan.
**Sudah dikerjakan:** **belum** — ini rencana, bukan hasil.
**Insight yang mengubah pendekatan:** testcase diikat ke `context_page`, sehingga kegagalan bisa
**dilokalisasi ke halaman**, bukan hanya dinilai PASS/FAIL. Ditambah temuan penting: harness hanya
membaca 6 kunci, jadi `assert_sql` akan lolos palsu bila dipakai tanpa patch.

### [07-verifikasi-live.md](07-verifikasi-live.md) — fakta
**Isi:** hasil V1–V7 + halaman mana yang diberi makan + 10 verifikasi lanjutan.
**Sudah dikerjakan:** V1–V7 selesai (read-only).
**Insight:** `opsi` bukan hanya bercampur makna, tapi punya **duplikat ejaan** (`Lainnya` vs `lainnya`);
satu aspek tidak punya nilai `no` sama sekali; satu aspek `opsi`-nya kosong seluruhnya dan sinyalnya
ada di `score`. Kesimpulannya: **kontrak per `area_key` itu wajib, bukan pelengkap**.

### [08-urutan-kerja-dan-dod.md](08-urutan-kerja-dan-dod.md) — urutan & definisi selesai
**Isi:** fase F1–F10, linter L1–L12, uji menemukan, kriteria promosi, gerbang pilot.
**Sudah dikerjakan:** linter dibangun dan **lulus penuh**; F6b/F7/F8 belum.
**Insight:** linter pada berkas teks **tidak bisa** membuktikan klaim ke database. Karena itu F6b
(manifes per halaman + skrip + **kontrol negatif**) bukan pelengkap — ia satu-satunya yang menutup
pola "pengetahuan tidak pernah menyeberang".

### [09-risiko-dan-keputusan-terbuka.md](09-risiko-dan-keputusan-terbuka.md) — risiko & keputusan
**Isi:** 11 keputusan bisnis, risiko teknis, ketergantungan, urutan keputusan.
**Sudah dikerjakan:** daftar lengkap; keputusan **belum** diambil (wewenang stakeholder).
**Insight:** tiga dari tujuh pertanyaan aspek (Penerimaan, Pengembalian, Pemusnahan) tidak bisa dijawab
bukan karena datanya hilang, tetapi karena **kolomnya tidak menyimpan penilaian "tidak"**. Ini
keputusan definisi, bukan pekerjaan data.

### [10-adopsi-rancangan-v2.md](10-adopsi-rancangan-v2.md) — memanfaatkan rancangan lama
**Isi:** adopsi metode dari `rancangan-v2.md` (yang skemanya sudah basi), 4 perubahan spesifikasi.
**Sudah dikerjakan:** matriks operasi, daftar karantina, penjaga waktu sebagai perilaku, dan manifes
sudah masuk ke halaman; skrip manifesnya belum.
**Insight:** dokumen lama bisa tetap berharga karena **diagnosisnya**, meski rujukan kolomnya mati.

### [rancangan-v2.md](rancangan-v2.md) — dokumen yang sudah ada
**Isi:** rancangan 14 Agu 2026 untuk warehouse lama.
**Sudah dikerjakan:** dibaca, metodenya diadopsi (lihat file 10), rujukan kolomnya ditinggalkan.
**Insight:** empat pola kegagalannya masih berlaku: aturan menempel pada kolom · halaman yang punya
topik justru salah arah · pengetahuan berhenti di dokumen · prosa yang tidak pernah dieksekusi.

---

## 3. Insight lintas dokumen

1. **Yang sulit bukan jumlah tabel, tetapi makna kolom.** `opsi` dan `nilai_aspek` masing-masing memuat
   beberapa konsep sekaligus. Satu kolom, banyak arti → butuh kontrak.
2. **Satuan tidak boleh dicampur.** Skor pelayanan dan cacat klausul produksi adalah dua satuan →
   dua panel, selamanya.
3. **Coverage adalah bagian dari jawaban, bukan catatan kaki.** Severitas, grade, CPOB, dan ketersediaan
   aspek semuanya tidak merata.
4. **Honest gap adalah jenis jawaban yang sah.** Tiga label panel memang tidak punya kolom; menjawabnya
   dengan kolom mirip menghasilkan angka yang rapi dan salah.
5. **Aturan harus menempel pada operasi**, bukan pada nama kolom.
6. **Pencegahan harus otomatis.** Linter menutup konsistensi teks; manifes + kontrol negatif menutup
   kebenaran klaim ke database. Tanpa yang kedua, masalah yang sama akan kembali.
7. **Testcase harus bisa melokalisasi kegagalan** ke halaman yang bertanggung jawab — kalau tidak,
   perbaikan berikutnya hanya menambal angka.

---

## 4. Yang belum dikerjakan, dan urutannya

```text
F3  verifikasi lanjutan (10 item)
 → F6b skrip manifes + kontrol negatif      (menutup klaim ke database)
 → F7  uji menemukan 6 pertanyaan           (membuktikan agent mencari, bukan menghafal)
 → F8  batch A testcase                     (pembanding pertama)
 → F9  promosi ke context/ + seeknal/skills/
 → F10 batch B–I + audit corpus lama
```

Keputusan bisnis (D1–D11 di [09](09-risiko-dan-keputusan-terbuka.md)) berjalan **paralel** dan tidak
menghambat F3–F6b, tetapi menghambat batch testcase kelas `decision`.

---

## 5. Cara membaca folder ini sebagai cerita

```text
01  kenapa perlu berubah        (bukti)
02  apa yang akan dibuat        (rancangan 21 halaman)
03  bagaimana orchestrator      (gerbang + Canonical Rules)
04  bagaimana penegakannya      (skill)
05  satu halaman dibedah        (filter panel = sumber salah kolom)
06  bagaimana diuji             (testcase)
07  fakta pendukung             (verifikasi live)
08  urutan & definisi selesai   (fase + gerbang)
09  risiko & keputusan          (yang butuh wewenang stakeholder)
10  pemanfaatan dokumen lama    (metode, bukan kolomnya)
```

Bila hanya punya waktu singkat: baca **01 → 07 → 09**. Tiga dokumen itu memberi alasan, fakta, dan
keputusan yang belum diambil.
