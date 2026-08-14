Cara menghitung — entity, grain, tanggal kanonik, eksklusi. Berlaku untuk SETIAP pertanyaan data.

Domain ini merekam **pemeriksaan sarana** (inspeksi ke fasilitas), bukan pengujian laboratorium,
bukan iklan, bukan penandaan. Batasnya di `95-batas-domain.md`.

## 1. Entity — dari SUBJEK pertanyaan, bukan dari kata bendanya

| Subjek | Hitung dengan | Tabel | Tanggal kanoniknya |
|---|---|---|---|
| Pemeriksaan / inspeksi | `COUNT(*)` atau `COUNT(DISTINCT id)` | `mv_pemeriksaan` | `tanggal_mulai` |
| Sarana (fasilitas) unik | `COUNT(DISTINCT nama_sarana)` | `mv_pemeriksaan` | idem |
| Temuan produk | `COUNT(*)` pada tabel temuan | `mv_pemeriksaan_temuan` | tanggal induknya |
| Pemeriksaan yang punya temuan | `COUNT(DISTINCT id_pemeriksaan)` | `mv_pemeriksaan_temuan` | idem |
| Penugasan petugas | `COUNT(*)` pada tabel petugas | `mv_pemeriksaan_petugas` | `tgl_surat` |

`id` di `mv_pemeriksaan` **unik penuh** — satu baris satu pemeriksaan. Karena itu `COUNT(*)` dan
`COUNT(DISTINCT id)` memberi hasil sama di tabel fakta, dan keduanya sah.

**Yang tidak sama:** pemeriksaan ≠ sarana. Satu sarana bisa diperiksa berkali-kali lintas tahun.
Pertanyaan "berapa sarana yang diperiksa" menuntut `COUNT(DISTINCT nama_sarana)`; menjawabnya
dengan cacah pemeriksaan melebihkan angkanya. Kalau pertanyaannya tidak jelas, **tanya di Gate 1**.

**Tabel pendamping mengubah grain.** Menjoin `mv_pemeriksaan` ke tabel temuan, petugas, jenis
pangan, atau kategori temuan **melipatgandakan baris induk**. Bila entity-nya pemeriksaan, hitung
dengan `COUNT(DISTINCT mp.id)` setelah join, atau saring dengan sub-query `EXISTS` alih-alih join.

## 2. Tanggal kanonik — tiga kolom, tiga arti

| Kolom | Arti | Pakai untuk |
|---|---|---|
| `tanggal_mulai` | pemeriksaan dimulai | **default** untuk "kapan diperiksa", tren, periode |
| `tanggal_selesai` | pemeriksaan selesai | pertanyaan tentang penyelesaian |
| `tanggal_input` | entri ke sistem | pertanyaan tentang pelaporan/administrasi, bukan kegiatan |

**Entity dan kolom tanggal adalah SATU keputusan.** Menghitung pemeriksaan lalu menyaringnya
dengan `tanggal_input` mencampur dua peristiwa: yang dihitung kegiatannya, yang disaring
administrasinya.

`tanggal_input` adalah satu-satunya yang selalu terisi. Dua lainnya punya baris kosong — lihat
`90-kualitas-data.md`.

## 3. Eksklusi WAJIB

| Apa | Aturan | Alasan |
|---|---|---|
| Akun uji | buang `nama_upt` yang berupa akun demo/uji | bukan balai sungguhan |
| Unit pusat pada hitungan per-balai | `nama_upt` yang berupa direktorat bukan balai | tidak punya wilayah kerja maupun target |

Kedua nilai itu dikenali dari daftar di `10-sarana-dan-fasilitas.md` §UPT. Terapkan pada hitungan
per-balai dan pada capaian; sebutkan bila angkanya dibandingkan sumber lain.

### Uji satu kalimat sebelum menambah klausa `WHERE` apa pun

> **Apakah baris yang dibuang klausa ini bisa menjadi jawaban yang benar?**
> **Bisa itu PENYEMPITAN, dan penyempitan hanya ada bila pertanyaan memintanya.**
> **Tidak bisa itu eksklusi, dan boleh selalu.**

Akun uji lolos uji itu. **Kolom yang kosong tidak lolos** — baris berkolom kosong tetap pemeriksaan
sungguhan yang ikut dihitung, kecuali pertanyaannya memang tentang kolom itu.

## 4. Bentuk angka & eksekusi

- **Angka utama dari query global sendiri**, bukan penjumlahan partisi. Setelah join ke tabel
  pendamping, penjumlahan per kelompok bisa melebihi total karena satu pemeriksaan muncul di
  beberapa kelompok.
- Satu statement per panggilan, tanpa `;`.
- **Jangan `EXTRACT(YEAR ...)` untuk menyaring** — pakai rentang berbatas (`>= awal AND < akhir`).
  `EXTRACT` hanya untuk melabeli hasil yang sudah dikelompokkan. Tidak ada indeks di database ini,
  jadi setiap query memindai penuh; bentuk filter yang salah membuatnya jauh lebih lambat.
- `ILIKE '%…%'` memindai seluruh kolom — pakai **sekali** untuk menemukan nilai, lalu hitung
  dengan `=` pada nilai itu.
- Semua kolom bertipe asli (date, bigint, numeric). **Tidak perlu cast.**

## 5. Tabel pendamping — arah join

Semua join bersifat **logis**; tidak ada foreign key di schema.

| Tabel | Kunci | Arah aman |
|---|---|---|
| `mv_pemeriksaan_temuan` | `id_pemeriksaan` = `mv_pemeriksaan.id` | dari fakta, LEFT JOIN |
| `mv_pemeriksaan_kategori_temuan` | idem | dari fakta, LEFT JOIN |
| `mv_pemeriksaan_jenis_pangan` | idem | dari fakta, LEFT JOIN |
| `mv_pemeriksaan_petugas` | idem | dari fakta, LEFT JOIN |
| `mv_pemeriksaan_log` | idem | dari fakta |
| `mv_kriteria_pemeriksaan` | `pemeriksaan_id` = `mv_pemeriksaan.id` | dari fakta |
| `mv_pemeriksaan_timeline` | idem | **dari fakta (INNER)** — timeline memuat id yang tidak ada di fakta |
| `mv_pemeriksaan_agg` | tanpa id | jangan dijoin; pakai langsung, lihat §6 |
| `target_balai` | `nama_balai` | lihat `85-target-capaian.md` |
| `coverage_balai` | `nama_balai` | many-to-many; jangan dijoin bila hanya butuh daftar balai |

**INNER JOIN ke tabel temuan menjatuhkan sebagian besar pemeriksaan** — hanya sebagian kecil
pemeriksaan yang menghasilkan temuan. Untuk pertanyaan populasi, LEFT JOIN dari fakta.

## 6. Tabel `agg` — satu syarat

`mv_pemeriksaan_agg` menyimpan kubus pra-agregasi dengan kolom `periode_type` yang punya dua nilai
(harian dan bulanan). **Selalu saring satu `periode_type`**; tanpa itu angkanya tergandakan karena
periode harian dan bulanan dijumlahkan bersamaan.

Kubus ini juga **tidak memuat baris yang tanggalnya kosong**, sehingga totalnya selalu sedikit di
bawah total fakta. Untuk angka populasi, hitung dari fakta; kubus dipakai bila pertanyaannya
memang berbentuk deret waktu per dimensi yang tersedia di sana.

## Kolom di dalam kubus

Kubus `mv_pemeriksaan_agg` memakai `tanggal_periode` sebagai kolom periodenya dan
`jumlah_pemeriksaan` sebagai cacah yang sudah diagregasi. Kolom cacah lain mengikuti pola nama yang
sama (`jumlah_`, `total_`, `avg_`, `min_`, `max_`).

Aturan pemakaiannya tetap seperti di atas: saring satu `periode_type`, dan ingat kubus beragregasi
pada tanggal selesai sehingga trennya tidak sebanding dengan tren dari tabel fakta.

## Rute

- Konsep berkode belum teresolusi buka peta halaman di `SEEKNAL_ASK.md`.
- Menyebut periode / tren / durasi: buka `80-waktu-dan-durasi.md`.
- Berkata "belum / tanpa / kosong / tidak melaporkan": buka `90-kualitas-data.md`.
- Menyentuh kolom yang belum pernah dipakai `describe_table` dulu sebelum menulis filter.

---

<!-- MANIFES
tabel: coverage_balai, mv_kriteria_pemeriksaan, mv_pemeriksaan, mv_pemeriksaan_agg, mv_pemeriksaan_jenis_pangan, mv_pemeriksaan_kategori_temuan, mv_pemeriksaan_log, mv_pemeriksaan_petugas, mv_pemeriksaan_temuan, mv_pemeriksaan_timeline, target_balai
kolom: id, id_pemeriksaan, jumlah_pemeriksaan, nama_balai, nama_upt, pemeriksaan_id, periode_type, tanggal_input, tanggal_mulai, tanggal_periode, tanggal_selesai, tgl_surat
nilai: -
-->
