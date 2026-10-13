# ERD & Data Dictionary — Domain Pemeriksaan (`staging`)

> **Untuk siapa**: siapa pun yang mau menulis query atau memahami data pemeriksaan sarana BPOM — analis, data engineer, atau AI agent.
>
> **Cara pakai**: mulai dari tabel "Peta cepat" di bawah, lalu buka file yang dituju. Setiap file ditulis supaya bisa dibaca sendiri tanpa harus membaca yang lain.

Semua isi folder ini dibaca langsung dari database `staging` per **22 Sep 2026** — bukan asumsi. Dokumen di sini **hanya** menjelaskan kondisi `staging` sekarang; alur sistem di luar `staging` tidak dibahas di sini.

---

## Peta file

| File | Isi | Buka kalau… |
|---|---|---|
| [01-aliran-data.md](01-aliran-data.md) | 7 flow entri user: apa yang diisi → mendarat di tabel/kolom mana → isi apa → insight apa | mau tahu **isian user berakhir di kolom mana** |
| [02-katalog-tabel.md](02-katalog-tabel.md) | 27 tabel: grain, jumlah baris, ukuran, asal, isi, insight | mau tahu **tabel mana yang harus dipakai** |
| [03-aturan-join.md](03-aturan-join.md) | 6 pola join + kolom mana merujuk kamus mana | mau **menulis query** dan tidak mau salah join |
| [04-routing-bridge.md](04-routing-bridge.md) | `flag_varian_datas` → bridge mana, matriks cakupan | tabel bridge **kosong tanpa error** padahal datanya ada |
| [05-aturan-wajib.md](05-aturan-wajib.md) | 22 aturan wajib sebelum menulis query | baca dulu sebelum query serius |
| [06-kamus-dan-dimensi.md](06-kamus-dan-dimensi.md) | Isi kamus: jenis sarana, aspek, kesimpulan, status, balai, wilayah | butuh **arti kode**, bukan cuma id |
| [07-kualitas-data.md](07-kualitas-data.md) | Kolom lengkap · kosong permanen · bisa dilengkapi · cacat yang diketahui | meragukan angka, atau mau tahu batas data |
| [08-contoh-datas.md](08-contoh-datas.md) | 5 contoh isian form asli + artinya | mau melihat **wujud asli** isian form |
| [contoh-datas/](contoh-datas/) | File JSON mentah sebagai lampiran | butuh data uji nyata |

Untuk perspektif kebutuhan user, bentuk pertanyaan/report, semantic layer, kontrak metrik, dan dasar testcase, buka [Blueprint Kebutuhan User](../blueprint_kebutuhan_user/README.md). ERD tetap fokus pada kondisi data dan cara memakainya.

---

## Ringkasan domain dalam satu layar

**Pemeriksaan** = kunjungan fisik BPOM ke sarana (pabrik, apotek, toko obat, klinik, gudang, PBF) untuk mengaudit CPOB/CPOTB/CPKB, memeriksa kelengkapan izin edar, sampai vonis sarana **MK** (Memenuhi Ketentuan) atau **TMK** (Tidak Memenuhi Ketentuan). Berbeda dari domain **Pengawasan** (iklan/promosi) — dua domain terpisah tapi berbagi 8 dim umum.

| Fakta | Nilai |
|---|---|
| Database / schema | `staging` / `public` (PostgreSQL 16.15) |
| Tabel bisa dibaca | **27** (19 tabel pemeriksaan + 8 dim general) |
| Tabel di luar domain | 26 tabel pengawasan (namanya terlihat, datanya ditolak) |
| Ukuran | 2.497 MB total database; 775 MB di antaranya `bridge_pemeriksaan_checklist` |
| Grain utama | 1 baris `fact_pemeriksaan` = 1 kasus pemeriksaan |
| Jumlah kasus | **259.348** (2020: 29.761 · 2021: 40.308 · 2022: 46.293 · 2023: 45.831 · 2024: 48.005 · 2025: 33.360 · 2026: 14.759 · 963 tanpa tanggal) |
| Rentang tanggal periksa | 2018-01-11 → 2027-07-27 (1 kasus terjadwal ke depan) |
| Perubahan terakhir (`updated_at`) | 2026-09-14 12:25 |

**Satu hal yang paling menentukan**: bentuk isian form berbeda per jenis sarana, jadi satu kasus **tidak** selalu bisa dijawab dari tabel bridge yang sama. Kolom `fact_pemeriksaan.flag_varian_datas` adalah penunjuk tabel mana yang harus dibaca — lihat [04-routing-bridge.md](04-routing-bridge.md).

---

## Konvensi penulisan

- Semua angka diverifikasi langsung ke database. Tanggal verifikasi ditulis di bagian *Verifikasi* tiap file.
- ✅ data lengkap & sehat · ⚠️ bisa dipakai dengan catatan · ❌ tidak ada / tidak bisa dipakai.
- Referensi antar dokumen memakai penomoran **Aturan #N** yang stabil — nomor tidak berubah walau file-nya dipindah, supaya dokumen lain (mis. `docs/user_flow/pemetaan-entry-per-flow-ke-staging-NEW.md`) tetap valid.
- Nama tabel ditulis `snake_case` tanpa schema; default schema `public`.

---

## Indeks 22 aturan wajib

Semuanya ada di [05-aturan-wajib.md](05-aturan-wajib.md), dikelompokkan per tema:

| Kelompok | Aturan |
|---|---|
| Kesimpulan & status | #1, #3, #20 |
| Join wajib | #2, #14, #19 |
| Draft & data uji | #4, #13 |
| Grain & routing bridge | #5, #6, #15, #16 |
| Kamus & aspek | #7, #8, #17 |
| Kolom jsonb & cadangan | #11, #22 |
| Kebersihan teks & tanggal | #9, #12 |
| Petugas & detail terbaru | #18 |
| Kebersihan isi temuan | #21 |

---

## Riwayat dokumen

| Tanggal | Perubahan |
|---|---|
| 2026-09-21 | ERD v3: 22 aturan, tambahan `bridge_pemeriksaan_vaksin`, `bridge_pemeriksaan_narasi_faskes`, kolom vaksin & `status_ss`/`tp_asset`/`updated_at`. Sebelumnya sempat ada tiga file terpisah (`erd-pemeriksaan.md`, `erd-pemeriksaan-terbaru.md`, `erd-pemeriksaan-v3.md`). |
| 2026-09-22 | Dipecah jadi 9 file bertema (folder ini). Isi tidak dikurangi, hanya ditata ulang; angka diperbarui ke kondisi 22 Sep 2026 dan fokus diarahkan ke kondisi `staging` saja. Menyerap materi alur entri dari `docs/user_flow/`. |

*Dokumen ini mencerminkan skema per migrasi terakhir ke database `staging`. Kalau ada perubahan skema, update file terkait dan catat tanggalnya di sini.*
