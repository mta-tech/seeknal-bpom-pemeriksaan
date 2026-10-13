# 09 — Risiko dan Keputusan Terbuka

> Dua hal yang tidak boleh dicampur: **keputusan bisnis** (wewenang stakeholder) dan **pekerjaan teknis** (wewenang tim data/AI). Keputusan bisnis tidak boleh diselesaikan dengan asumsi teknis.

---

## 1. Keputusan bisnis yang harus disepakati

| # | Keputusan | Kenapa diperlukan | Dampak bila ditunda |
|---|---|---|---|
| D1 | Definisi "temuan" per bentuk data (aspek · klausul · observasi · produk) | belum ada definisi tunggal yang sah untuk semua varian | testcase kelas `decision` tidak bisa dinilai |
| D2 | Definisi "tren" (kasus · item · persentase kepatuhan · proporsi TMK) | satu kata, empat metrik | Q1–Q7 tidak bisa dibandingkan antar laporan |
| D3 | Apakah pelayanan dan produksi ditampilkan bersama | satuannya berbeda (skor vs cacat klausul) | angka gabungan menyesatkan |
| D4 | Indikator ketidaksesuaian untuk Penerimaan, Pengembalian, Pemusnahan | `opsi` tidak menyimpan penanda "tidak" | tiga aspek dari tujuh tidak bisa dijawab |
| D5 | Definisi resmi "wilayah kerja UPT" | beda dari regional dan beda dari lokasi sarana | laporan per wilayah bisa benar secara SQL tapi salah secara bisnis |
| D6 | Matriks severitas → tindak lanjut | menilai proporsionalitas keputusan | evaluasi Pusat hanya bisa menampilkan asosiasi |
| D7 | Apakah Penerimaan & Pengembalian masuk kamus resmi `ASPEK_KTL` | saat ini berstatus belum ada di kamus | label aspek bergantung `COALESCE` selamanya |
| D8 | Perlakuan **klasifikasi distribusi** yang tidak punya kolom | panel punya, data tidak | permintaan user akan berulang sebagai "tidak bisa dijawab" |
| D9 | Perlakuan **status label** yang kosong | kolom ada, isi kosong | pertanyaan label selalu jadi honest gap |
| D10 | Arti `kriteria` (kode angka) pada observasi | belum pernah dikonfirmasi | halaman `45` hanya bisa menyebut batasnya |
| D11 | Apakah insight AI perlu persetujuan manusia sebelum masuk laporan | menyangkut tata kelola | tidak bisa diputuskan tim teknis |

---

## 2. Risiko teknis dan mitigasinya

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Aturan RPO bocor ke context pemeriksaan | agent memakai kode/kolom domain lain | linter L2 + guard di `SEEKNAL_ASK` dan `bpom-analyst` |
| **Aturan menempel pada kolom, bukan pada operasi** (pola P1) | aturan benar ada, tapi tidak sampai ke operasi tempat kesalahan terjadi (menyaring vs mengelompokkan vs join vs peringkat) | **matriks operasi** wajib per kolom berkod ([10](10-adopsi-rancangan-v2.md) §3.1) |
| **Pengetahuan berhenti di dokumen, tidak menyeberang ke context** (pola P3) | konsep sudah terdokumentasi, tapi tetap tak terpakai karena tak ada yang memberi tahu | **manifes + skrip verifikasi** yang mendeteksi kolom/konsep tak-terdaftar ([10](10-adopsi-rancangan-v2.md) §3.4) |
| **Prosa yang tidak pernah dieksekusi** (pola P4) | klaim kolom/perilaku lahir dari ingatan struktur | manifes memverifikasi tiap kolom/literal ke database; kontrol negatif wajib lulus |
| Alat ukur yang salah melaporkan "semua tercakup" | cakupan palsu → regresi tak terdeteksi | skrip wajib memuat **kontrol negatif** (nama kolom karangan harus dilaporkan tidak ditemukan) |
| Halaman kepanjangan | melewati `read_max_lines` → aturan tak terbaca | batas ≤200 baris + linter L7 |
| Context jadi duplikat ERD | dua sumber kebenaran yang bisa berbeda | context = instruksi; ERD = referensi; linter L9 |
| Kode ditulis dari ingatan | kode salah yang tetap "jalan" | wajib berasal dari [07](07-verifikasi-live.md); linter tidak bisa menangkap semua → review manual |
| Menulis angka hasil ke context | menjadikannya jawaban hafalan | linter L8 + aturan eksplisit |
| Rewrite menimpa `context/` langsung | tidak ada titik kembali | wajib snapshot; promosi hanya setelah F8 |
| Testcase dibuat sebelum aturan stabil | menguji aturan yang belum final | testcase adalah F10 |
| Corpus lama dijadikan quality gate | mengunci perilaku lama yang salah | audit status + banner di `docs/testcase/README.md` |
| Snapshot lama ikut diubah | kehilangan pembanding | `after-insight-v1..v3` tidak disentuh |
| `assert_sql` dipakai tanpa patch harness | testcase lolos palsu (kunci tidak dibaca) | dokumentasikan 6 kunci yang berlaku ([06](06-plan-testcase.md) §1) |

---

## 3. Ketergantungan luar

| Ketergantungan | Dampak bila tidak tersedia |
|---|---|
| Tunnel `srv29-staging` (→ `localhost:5432`) | verifikasi live dan penulisan SQL kanonis testcase tidak bisa dijalankan |
| Grant `pemeriksaan_reader` (27 tabel) | seluruh aturan tabel terverifikasi, tidak berubah |
| Konfirmasi tim data untuk D8/D9/D10 | tiga halaman tetap menyebut honest gap (bukan salah, tapi belum tuntas) |
| Keputusan stakeholder untuk D1–D6 | testcase kelas `decision` berhenti di tahap klarifikasi |

---

## 4. Yang secara sengaja TIDAK dikerjakan sekarang

| Hal | Alasan |
|---|---|
| Mengubah `context/` dan `seeknal/skills/` secara langsung | menunggu snapshot lulus uji |
| Menyunting 256 testcase lama | hanya diaudit statusnya; penyuntingan menyusul per batch |
| Membangun bridge antibiotik | keputusan data terpisah; halaman `45`/`95` cukup menyatakan batasnya |
| Menambah `assert_sql` ke harness | keputusan terpisah; testcase batch awal cukup dengan 6 kunci |
| Menyentuh snapshot `after-insight-v1..v3` | berfungsi sebagai pembanding historis |
| Menulis ulang `docs/ERD` dan `docs/blueprint_kebutuhan_user` | keduanya sudah jadi sumber; folder ini hanya menjembatani ke artefak agent |

---

## 5. Urutan keputusan yang disarankan

```text
D3 (satuan pelayanan vs produksi)
  → D2 (definisi tren)
    → D1 (definisi temuan per bentuk)
      → D4 (indikator tiga aspek)
        → D6 (severitas → tindak lanjut)
          → D5 (wilayah)
            → D8, D9, D10 (gap panel & kode)
              → D7, D11 (kebijakan kamus & tata kelola)
```

Alasan urutannya: D3 dan D2 menentukan **bentuk** semua laporan; D1 dan D4 menentukan **isi angka**; D6 dan D5 menentukan **tafsir**; sisanya melengkapi cakupan.

---

## 6. Cara memakai dokumen ini

- **Tim data/AI**: pakai §2 sebagai daftar periksa sebelum promosi.
- **Stakeholder**: pakai §1 sebagai agenda keputusan — setiap baris punya "kenapa diperlukan" dan "dampak bila ditunda", tanpa menuntut pembaca memahami struktur database.
- **Audit**: setiap keputusan yang akhirnya diambil sebaiknya dicatat tanggalnya di dokumen ini, supaya asumsi lama tidak hidup kembali.
