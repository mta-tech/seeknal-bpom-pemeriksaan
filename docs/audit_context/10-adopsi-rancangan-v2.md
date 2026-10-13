# 10 — Adopsi dari `rancangan-v2.md`

> Di folder ini sudah ada `rancangan-v2.md` (disusun 14 Agu 2026, "rancangan, belum dieksekusi"). Dokumen itu dibuat untuk **warehouse lama (`mv_*`)**, jadi seluruh rujukan kolomnya sudah basi — tetapi **metodenya lebih tajam** daripada spesifikasi awal saya di empat hal.
>
> Keputusan: **adopsi metodenya, tinggalkan rujukan kolomnya.**

---

## 1. Status `rancangan-v2.md`

| Aspek | Kondisi |
|---|---|
| Skema yang dirujuk | **basi**: `mv_pemeriksaan`, `mv_pemeriksaan_temuan`, `target_balai`, `product_name`, `tp_negara`, `tp_expire`, `urutan_step`, `tanggal_kirim_kabalai` — semuanya tidak ada di `staging` |
| Metode & diagnosis | **masih berlaku** dan dipakai di spesifikasi ini |
| Diagnosis 4 pola kegagalan | berlaku umum, tidak bergantung skema |
| Bukti spesifik (mis. `trim()` → 0 baris) | perlu diuji ulang di `staging` sebelum dikutip |

Cara memakainya: ambil **polanya**, cari padanannya di `staging`, dan buktikan ulang di sana. Jangan salin nama kolomnya.

---

## 2. Empat pola kegagalan (dari dokumen itu, berlaku sekarang)

| Pola | Isi | Bukti di konteks kita |
|---|---|---|
| **P1 — aturan menempel pada KOLOM, padahal kesalahan terjadi pada OPERASI** | satu kolom berperilaku berbeda saat disaring vs dikelompokkan vs di-join vs diperingkat | `opsi` berbeda-beda **per `area_key`**; `nilai_aspek` berbeda makna per kelompok nilai |
| **P2 — halaman yang memiliki topik justru memberi arahan salah** | lebih berbahaya daripada tidak ada halaman | 15 halaman sekarang mengarahkan ke kolom yang tidak ada |
| **P3 — pengetahuan berhenti di dokumen, tidak pernah menyeberang** | temuan sudah terdokumentasi, tapi tidak ada mekanisme yang memberi tahu ia belum punya pasangan di context | 159 kemunculan skema lama vs 16 file dokumen kondisi yang benar, tanpa jembatan |
| **P4 — prosa yang tidak pernah dieksekusi** | klaim berbasis ingatan struktur, bukan query | seluruh halaman lama |

---

## 3. Yang diadopsi (4 perubahan pada spesifikasi)

### 3.1 Matriks operasi per kolom berkod (menjawab P1)

Ditambahkan ke **template halaman** ([02](02-spec-context-halaman.md) §3). Setiap kolom berkod mendapat tabel kecil:

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| *(kolom)* | *(aturan)* | *(aturan)* | *(aturan)* | *(aturan)* |

Sel yang tidak berjebakan ditulis **"biasa"** — supaya terlihat sudah dipertimbangkan, bukan terlewat.

Padanan di `staging` yang wajib punya matriks ini: `opsi` · `nilai_aspek` · `kategori_kode` · `legal_id` · `tl_saran` · `jenis_pangan_kode` · `status_label` · `flag_varian_datas` · `dihapus_di_sumber`.

### 3.2 Kebersihan teks naik ke Gerbang (menjawab P1)

Cacat spasi/kapitalisasi membelah hasil **tanpa pesan kesalahan**, dan terjadi di operasi apa pun. Karena itu ia menjadi **butir Gate 5**, bukan catatan di satu halaman.

Bukti yang sudah kita punya: `opsi` memuat `Lainnya` **dan** `lainnya`, serta `Asisten Apoteker` **dan** `asisten` — pengelompokan tanpa normalisasi akan memecah satu makna menjadi dua baris.

Aturan yang masuk Gate 5: rapatkan spasi tepi & ganda, samakan kapitalisasi **sebelum** mengelompokkan atau memeringkat; untuk filter kesamaan persis, pakai nilai hasil probe apa adanya.

### 3.3 Daftar karantina eksplisit (menjawab P2 & P3)

Ditambahkan sebagai bagian baku. Isinya: kolom/tabel yang **tidak boleh dikutip** + alasan satu kalimat + **apa penggantinya**. Larangan tanpa pengganti akan dilanggar.

Karantina awal untuk `staging`:

| Jangan dikutip | Alasan | Pakai ini |
|---|---|---|
| `distribusi_provinsi_kode` sebagai "klasifikasi distribusi" | itu tujuan distribusi pabrik Pangan MD | nyatakan honest gap |
| `dim_status_code.status_label` | terisi 0/35 | `status_code` + label dari luar |
| `legal_id` dengan filter satu `type` | merujuk 2 kamus | tampilkan `type` sebagai kolom hasil |
| `opsi` sebagai penanda temuan global | maknanya per `area_key` | kontrak `35` |
| `nilai_aspek` sebagai satu konsep | memuat 4 makna | pisahkan konformasi/grade/severity |
| `sediaan_kode`, `unit_id`, `penelusuran_id`, `kasus_id`, `metode_inspeksi`, `tl_ba_pusat`, `tl_attachment_pusat` | praktis kosong | jangan dipakai sebagai penyaring |
| `dim_produk.is_imported` | bernilai sama di seluruh baris | gunakan kolom lain |
| tabel domain pengawasan | `SELECT` ditolak | `95-batas-domain` |

### 3.4 Manifes verifikasi (menjawab P3 & P4) — **tambahan terpenting**

Setiap halaman diakhiri blok **manifes** yang mendaftar: nama tabel, nama kolom, dan literal nilai yang diajarkannya. Lalu satu skrip di `scripts/` memverifikasi tiga hal terhadap database:

1. setiap **tabel & kolom** di manifes benar-benar ada;
2. setiap **literal nilai** ada persis di data (termasuk spasi & kapitalisasi);
3. setiap **kolom berkode** di database muncul di manifes salah satu halaman, atau terdaftar sebagai **sengaja diabaikan**.

Pemeriksaan ketiga menutup P3: kolom/konsep yang belum menyeberang ke context muncul sebagai kolom tak-terdaftar.

**Syarat wajib:** skrip memuat **kontrol negatif** — nama kolom karangan harus dilaporkan tidak ditemukan. Tanpa itu, angka cakupan tidak bisa dipercaya (di dokumen asal, versi pertama alat ukur sempat melaporkan seluruh kolom tercakup karena bug pemisah kolom, dan hasil mustahil itu nyaris lolos).

Skrip ini juga otomatis menutup L8 (larangan angka) dan L1/L2 (larangan skema lama) di [linter](08-urutan-kerja-dan-dod.md) §2 — karena keduanya bisa diperiksa dari manifes.

---

## 4. Yang TIDAK diadopsi

| Dari dokumen itu | Alasan tidak diadopsi |
|---|---|
| nama kolom & tabel `mv_*` | tidak ada di `staging` |
| klaim cakupan tabel kategori temuan "beku sejak Nov 2025" | perlu diuji ulang di `staging`; kondisi kita berbeda (49 kode dipakai, 27 tak terpetakan) |
| bukti `trim()` pada nama balai (0 baris vs 1.428) | bentuknya valid sebagai pola; angkanya wajib diverifikasi ulang di `staging` sebelum dikutip |
| klaim "15 halaman, sebagian besar benar" | tidak berlaku lagi: seluruh 15 halaman memakai skema lama |

---

## 5. Perubahan pada urutan kerja

Fase baru **F6b — manifes & skrip verifikasi** disisipkan antara linter dan uji menemukan, dan skrip manifes ikut menjadi **gerbang pilot**:

| Metrik gerbang | Ambang |
|---|---|
| suite testcase lama | PASS **tidak turun** |
| jawaban pada skenario yang sudah benar | **nol** yang bergerak |
| SQL per turn | **tidak naik** |
| skrip manifes | **nol pelanggaran**, kontrol negatif lulus |
| pertanyaan pada kolom berjebakan | memakai normalisasi yang benar sesuai operasinya |
| pertanyaan "sejak kapan / paling awal" | membatasi tahun, tidak mengembalikan tahun mustahil |

Satu hal yang tidak tertangkap suite mana pun (tetap dari dokumen itu, dan tetap benar): **apakah agent benar-benar membuka halaman yang relevan**. Manifes memverifikasi isi halaman, bukan bahwa halamannya dibaca → perlu pembacaan manual jejak beberapa jawaban. Ini masuk uji menemukan ([08](08-urutan-kerja-dan-dod.md) §3).

---

## 6. Ringkasan perubahan spesifikasi

| File | Perubahan |
|---|---|
| [02](02-spec-context-halaman.md) | template halaman + **matriks operasi** + **blok manifes** + daftar karantina |
| [03](03-spec-seeknal-ask-v5.md) | Gate 5 + kebersihan teks (sudah ada, dinaikkan prioritasnya) + penjaga waktu sebagai perilaku |
| [08](08-urutan-kerja-dan-dod.md) | + fase F6b (manifes & skrip) dan gerbang pilot |
| [09](09-risiko-dan-keputusan-terbuka.md) | + risiko "aturan menempel pada kolom" dan "pengetahuan tak menyeberang" |
