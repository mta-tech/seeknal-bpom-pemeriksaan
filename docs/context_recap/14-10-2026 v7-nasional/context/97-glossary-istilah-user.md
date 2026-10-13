temuan · wilayah · jumlah · tren · kritis · tindak lanjut · selesai · inspektur terbaik · kapasitas · beban kerja · PKM · NPP · keamanan mutu · obat keras · ekspor impor

# Kamus istilah user — dan kapan harus bertanya

## Apa yang halaman ini putuskan

Beberapa kata dalam bahasa user punya **lebih dari satu bacaan** di data. Halaman ini memutuskan bacaan
mana yang dipakai — atau menyatakan bahwa pertanyaannya harus diklarifikasi.

## Tabel keputusan — istilah ambigu

| Istilah user | Bacaan yang mungkin | Yang dipakai / tindakan |
|---|---|---|
| **temuan** | aspek (pelayanan) · klausul (produksi) · observasi · produk bermasalah · alasan TMK | tentukan dari kalimat; bila dua bacaan bertahan → **tanya** |
| **wilayah** | balai pelaksana · regional · lokasi sarana · wilayah kerja UPT | tentukan dari kalimat; "wilayah kerja" saja → **tanya** |
| **jumlah** | kasus · sarana unik · item · baris produk · kuantitas fisik · penugasan petugas | pilih sesuai kata benda; ragu → **tanya** |
| **tren** | jumlah kasus · jumlah item tidak sesuai · persentase kepatuhan · proporsi TMK | **tanya** bila tidak disebut |
| **kritis / major / minor** | per kasus · per klausul | **tanya**; lalu sebutkan cakupannya |
| **tindak lanjut** | saran balai · saran pusat · CAPA · tindakan produk · status approval | **tanya** |
| **selesai** | jalur final balai · jalur final pusat | pakai **keduanya**, sebutkan |
| **inspektur terbaik** | volume penugasan · eksposur jenis sarana · kompetensi | **tanya**, dan sebutkan kompetensi tidak tersedia |
| **bermasalah / tidak sesuai** | nilai jawaban · skor rendah · klausul Tidak · severitas | **tanya** |
| **kapasitas / beban kerja** | jumlah kasus · jumlah jenis sarana ditangani | pilih, dan sebutkan dasarnya |
| **PKM** | Puskesmas (`JENIS_SARANA`) vs "Pengawasan Keamanan Mutu" (bukan modul di domain ini) | default: Puskesmas (`10`); bila konteks keamanan mutu → `95` |
| **NPP / NPPZA / obat berkontrol** | tiga komoditi (narkotika+psikotropika+prekursor) vs termasuk Obat-Obat Tertentu; kasus (`20`) vs pengelolaan di distribusi (`22`) | pilih dari kalimat; dua bacaan bertahan → **tanya** |
| **keamanan mutu** | kategori temuan TMS Keamanan-Mutu-Gizi Pangan (`40`) · profil manajemen mutu pabrik pangan (`50`) · bukan modul | pilih dari kalimat; bila maksudnya modul → `95` |
| **obat keras** | kategori temuan produk vs golongan produk | kategori temuan → `40`; golongan/registrasi → `20` |
| **ekspor impor** | bukan modul; jalur nyata: negara asal temuan, proxy nama sarana | `41` / `10`; konsep permit/awal impor → `95` |

## Pemetaan istilah user → konsep data

| Bahasa user | Konsep | Halaman |
|---|---|---|
| pendistribusian | label kamus resmi **Penyaluran** | `35` |
| tidak memenuhi ketentuan | TMK | `30` |
| memenuhi ketentuan | MK | `30` |
| tingkat pemenuhan CPOB | kelompok kode CPOB pada kesimpulan | `30` |
| laporan/berkas banyak belum selesai | status non-final | `31` |
| harus diperiksa lagi / berulang | sarana yang muncul di beberapa kasus | `10` + `80` |
| jam terbang / pengalaman | eksposur penugasan | `70` |
| nilai sitaan / kerugian | nilai pada temuan produk | `41` |
| regulasi/sertifikat sarana | sertifikat Pangan MD | `50` |

## Cara mencari padanan istilah yang tidak ada di tabel

```sql
-- 1. cek apakah konsepnya ada sebagai kolom
SELECT table_name, column_name FROM information_schema.columns
WHERE table_schema='public' AND column_name ILIKE '%<kata>%' ORDER BY 1,2;

-- 2. cek apakah konsepnya ada sebagai nilai kamus
SELECT type, count(*) FROM public.dim_master_data
WHERE name ILIKE '%<kata>%' GROUP BY 1 ORDER BY 2 DESC;
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| menjawab "temuan" padahal user bertanya klausul | istilah paling ambigu dipilih tanpa klarifikasi | tanya dulu |
| angka TMK dipakai sebagai proxy "temuan" | dua konsep berbeda | sebutkan konsep yang dipakai |
| jawaban benar tapi tidak menjawab maksud | bacaan ambigu dipilih diam-diam | sebutkan asumsi satu kalimat, atau tanya |

## Aturan klarifikasi

- Klarifikasi **hanya** untuk yang tidak punya bacaan default aman (lihat daftar di atas).
- Satu pertanyaan pada satu waktu, maksimal dua putaran.
- Klarifikasi **selalu** melalui tool `ask_clarification`/`ask_user` — pertanyaan klarifikasi yang
  ditulis sebagai teks jawaban tidak akan pernah dijawab dan mematikan giliran.
- Bila memakai default, **sebutkan asumsinya** dalam satu baris di jawaban.

## Rute

- Istilah kepatuhan → **lihat** `35` / `37`
- Istilah kesimpulan & mutu → **lihat** `30` / `60`
- Istilah wilayah → **lihat** `10` dan `05`
- Konsep yang tidak ada → **lihat** `95-batas-domain.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `dim_master_data` | `type`, `name` | — |
| `information_schema.columns` | `table_name`, `column_name` | — |
