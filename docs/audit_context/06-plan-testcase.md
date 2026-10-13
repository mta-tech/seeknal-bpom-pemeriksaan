# 06 — Plan Testcase Baru

> Testcase baru **tidak** diturunkan dari 256 corpus, tetapi dari kebutuhan user di `docs/blueprint_kebutuhan_user/` — lalu diikatkan ke halaman context yang memuat aturannya, supaya kegagalan bisa dilokalisasi.

---

## 1. Lokasi, penemuan, hasil

| Hal | Nilai |
|---|---|
| Lokasi batch baru | `docs/testcase/blueprint-batch-<X>/` |
| Ditemukan oleh harness | `scripts/test_variant_compare.py --test-path <folder>` |
| Hasil run | `seeknal/tests/outputs/<tanggal>/<variant>/variant_compare_results_*.json` |
| Kunci yang benar-benar dibaca parser | `assert_contains`, `assert_any_of`, `tolerance_pct`, `assert_asked`, `clarif_response`, `note` |
| Metadata tambahan | ditulis di `description` dan `note` |
| Konsekuensi | `assert_sql`/`assert_absent`/`assert_no_sql` **tidak** berfungsi di harness ini (perlu patch bila ingin dipakai) |

Bila nanti `assert_sql` diperlukan, patch harus ditambahkan di **dua** fungsi worker (`_scenario_to_dict` dan `_scenario_from_dict`) agar tidak hilang saat `--workers > 1`.

---

## 2. Bentuk testcase

```yaml
name: BPOM-PMR-USR-PENYIMPANAN-PELAYANAN-2025
scenario_id: BPOM-PMR-USR-PENYIMPANAN-PELAYANAN-2025
verification_date: '2026-09-22'
description: >
  persona=kepala_balai | intent=compliance | entity=item aspek | grain=item per varian
  context_page=35-kepatuhan-aspek | answerability=rule
  anti_trap=jangan pakai opsi=no global; jangan campur produksi
turns:
- prompt: 'bagaimana tren ketidaksesuaian penyimpanan pada sarana pelayanan tahun 2025?'
  assert_contains: ['penyimpanan', 'pelayanan']
  assert_any_of: [['198'], ['47.666'], ['8.344']]
  tolerance_pct: 5
  note: >
    canonical_sql=<sql kanonis>
    coverage=sarana pelayanan (Apotek/PKM/Klinik/Toko Obat/RS) — produksi tidak termasuk
    bentuk jawaban=sebut entity + periode + satuan
    hasil 22 Sep 2026: 8.344 kasus · 47.666 item · 198 item ber-opsi 'no'
    anti-trap=menggabungkan pelayanan dan produksi tanpa memisahkan satuan = FAIL
```

**Arti metadata:**

| Field | Fungsi |
|---|---|
| `persona` | siapa yang bertanya (menentukan bentuk output) |
| `intent` | monitoring / compliance / risk / tindak lanjut / evaluasi / pola / report |
| `entity` + `grain` | apa yang dihitung |
| `context_page` | halaman yang bertanggung jawab bila gagal |
| `answerability` | `ready` · `rule` · `decision` · `unavailable` |
| `anti_trap` | apa yang **harus** gagal |
| `coverage` | sub-populasi yang wajib disebut di jawaban |

**Aturan angka:** angka **tidak pernah** ditaruh di `assert_contains` (tidak ada toleransi di sana) — selalu di `assert_any_of` bersama `tolerance_pct`.

---

## 3. Empat kelas

| Kelas | Contoh prompt | Yang diuji | FAIL berarti |
|---|---|---|---|
| `ready` | "berapa pemeriksaan BBPOM Bandung 2025?" | entity, Balai, periode, `COUNT DISTINCT` | entity/periode salah |
| `rule` | "kategori temuan dominan per regional 2025" | expand array, draft, `regional_name`, grain | bridge/kolom salah atau satuan dicampur |
| `decision` | "berapa temuan penerimaan tahun ini?" | apakah menjawab tanpa definisi | menebak `opsi='no'` atau mengarang definisi |
| `unavailable` | "kapan surat TL ini di-TTE?" | protokol honest gap | mengarang angka / memakai kolom mirip |

---

## 4. Batch A–I

| Batch | Tema | Halaman yang diuji | Contoh prompt | Kelas | Jumlah |
|---|---|---|---|---|---|
| A | monitoring | `00`,`01`,`10`,`15`,`20` | "berapa pemeriksaan BBPOM Bandung 2025?" | ready | 8–10 |
| B | kepatuhan | `35`,`37` | "tren ketidaksesuaian penyimpanan 2024–2025" | rule | 10 |
| C | risiko | `37`,`60` | "berapa temuan Major dan Kritis 2025?" | rule | 10 |
| D | tindak lanjut | `60` | "apa tindak lanjut dominan untuk kasus TMK?" | rule | 8 |
| E | evaluasi UPT vs Pusat | `31`,`30` | "berapa kasus beda kesimpulan Balai vs Pusat?" | rule | 8 |
| F | pola & wilayah | `10`,`40`,`50` | "kategori temuan dominan per regional 2025" | rule | 8 |
| G | antibiotik | `45`,`95` | "antibiotik apa paling banyak tanpa resep?" | decision/unavailable | 6 |
| H | free text | `60`,`97`,`90` | "ringkas alasan TMK 2025" | rule + evidence | 8 |
| I | klarifikasi | `97` | "berapa temuan tahun ini?" (objek temuan tidak disebut) | decision | 6 |

Prompt sengaja memakai **bahasa panel user** agar katalog filter ikut teruji, termasuk saat jawaban yang benar adalah honest gap (mis. "klasifikasi distribusi", "status label").

---

## 5. Katalog anti-trap

| Anti-trap | Bentuk salah | Bentuk benar |
|---|---|---|
| grain petugas | `COUNT(*)` disebut jumlah pemeriksaan | `COUNT(DISTINCT pemeriksaan_id)` |
| `opsi` global | `WHERE opsi='no'` untuk semua aspek | kontrak per `area_key` |
| `score` mentah | `AVG(score)` lintas aspek | pisahkan item vs akumulasi |
| `nilai_aspek` campur | satu filter untuk semua makna | pisahkan konformitas / grade / severity |
| dua varian | pelayanan + produksi dijumlahkan | dua panel terpisah |
| wilayah | `regional` disebut provinsi sarana | tiga makna wilayah dibedakan |
| severitas | subset digeneralisasi | sebutkan coverage |
| produk | baris temuan disebut kuantitas | empat grain dipisahkan |
| kamus | join tanpa `type` | sebut `type` |
| array | bandingkan string array mentah | expand jsonb |
| ejaan | kelompokkan tanpa normalisasi | normalisasi (`Lainnya` vs `lainnya`) |
| filter | klausa tanpa kata di pertanyaan | uji penyempitan vs eksklusi |
| kausal | "menyebabkan" | "berasosiasi" |
| honest gap | jawab dengan kolom mirip | nyatakan tidak tersedia |

---

## 6. Siklus hidup dan policy drift

```text
prompt natural
→ tetapkan grain & metrik dari halaman context
→ jalankan SQL kanonis ke staging (localhost:5432 via tunnel srv29-staging)
→ catat angka + verification_date
→ jalankan harness satu batch
→ audit JAWABAN (bukan hanya verdict)
→ lokalisasi kegagalan ke context_page
→ perbaiki halaman context atau testcase
→ bekukan
```

| Jenis pergerakan angka | Perlakuan |
|---|---|
| drift wajar | diserap `tolerance_pct` |
| data tumbuh (transient) | tandai `transient` di `note`, jangan longgarkan testcase |
| salah permanen | perbaiki context, bukan testcase |

---

## 7. Lokalisasi kegagalan

| Gejala | Halaman yang diperiksa |
|---|---|
| jawaban kosong padahal data ada | `01` (routing varian) |
| kolom salah / tidak ada | `05` (label panel) |
| angka berlipat | `00` (grain) |
| aspek hilang dari hasil | `35` (`COALESCE`) |
| severity diklaim menyeluruh | `37` (coverage) |
| kode tidak terpetakan | `40` (bucket) |
| honest gap dijawab dengan angka | `95` |

---

## 8. Audit corpus lama (256)

Metode: klasifikasikan tiap testcase ke salah satu status, tanpa mengubah prompt.

| Status | Kriteria |
|---|---|
| `relevant` | prompt masih natural, aturan masih berlaku |
| `needs rewrite` | maksudnya benar, tapi route/kolom/metrik berubah |
| `duplicate` | menguji hal yang sama dengan testcase lain |
| `obsolete` | menyentuh konsep/kolom yang tidak ada lagi |
| `out-of-domain` | menyentuh domain lain |

Contoh yang sudah bisa diduga dari kondisi sekarang: testcase bertema `klasifikasi distribusi` → `needs rewrite`/`obsolete` (kolomnya tidak ada); bertema `status label` → `needs rewrite` (label kosong); bertema `tingkat pemenuhan CPOB` → `needs rewrite` (berbagi kolom kesimpulan).

---

## 9. Aturan yang dilarang

1. Menaruh angka di `assert_contains`.
2. Merinci prompt agar PASS.
3. Menghapus atau melonggarkan testcase untuk menghilangkan kegagalan.
4. Memakai angka lama sebagai requirement.
5. Memakai 256 corpus sebagai daftar kebutuhan.
6. Menambah testcase massal sebelum satu batch direview.

---

## 10. Kriteria lulus batch

- [ ] setiap testcase punya `context_page` dan `answerability`;
- [ ] setiap aturan penting punya pasangan positif + anti-trap;
- [ ] angka hanya di `assert_any_of`;
- [ ] prompt tetap natural (tidak dibocorkan petunjuk);
- [ ] ada minimal satu testcase `decision` dan satu `unavailable` per batch tematik;
- [ ] canonical SQL dijalankan pada tanggal verifikasi dan angkanya tercatat;
- [ ] hasil run diaudit per jawaban, bukan hanya verdict.
