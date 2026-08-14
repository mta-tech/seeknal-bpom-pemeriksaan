# Artefak Bukti — database `pemeriksaan`

Hasil eksekusi nyata terhadap database live lewat tunnel `postgresql://localhost:5533/pemeriksaan`,
**2026-08-13**. Folder induk memuat dokumen naratifnya; di sini **datanya**, supaya setiap klaim
bisa ditelusuri ulang tanpa menjalankan apa pun.

## Isi

| Berkas | Isi | Bentuk |
|---|---|---|
| `pair_ringkas.csv` | **213 pertanyaan**, satu baris fisik per pertanyaan. Kolom: tabel yang disentuh, pakai agregasi atau tidak, status sebelum/sesudah terjemahan, cacah baris hasil, **kode diagnosa**, dan penjelasan sebabnya | CSV rapi — aman dibuka di Excel / `pandas.read_csv` |
| `pair_detail_sql.csv` | SQL asli dan SQL yang dipakai, **diratakan jadi satu baris** supaya tidak merusak struktur CSV | CSV rapi |
| `pair_per_pertanyaan.md` | Uraian per pertanyaan: bentuk NER, tabel, status, lapis terjemahan, diagnosa, sebab, dan SQL-nya | Markdown, dikelompokkan per generasi koneksi |
| `csv_sql_training.csv` | **27 SQL** kolom *SQL Training* dari `BPOM User Relevant Query.xlsx` untuk modul ini + hasil eksekusinya | CSV rapi |
| `katalog_nilai_unik_live.md` | Katalog nilai unik penuh (`GROUP BY` seluruh baris) semua kolom kategorikal, dengan cacah, persen, dan tanda sentinel | Markdown |
| `profil_kolom_live.md` | Per kolom tiap tabel: cacah SQL NULL, persentase, cacah distinct | Markdown |
| `ringkasan_eksekusi.json` | Rekap angka untuk dibaca mesin | JSON |

## Hasil

| Set | Hasil |
|---|---|
| Pair `context_stores` | **208 dari 213 menghasilkan data (98%)** |
| `SQL Training` dari CSV | **27 dari 27** |

### Sebaran diagnosa

| Kode | Jumlah |
|---|--:|
| `OK_LANGSUNG` | 166 |
| `PULIH_RELASI_KOLOM` | 38 |
| `NOL_TIDAK_DITEMUKAN` | 3 |
| `OK_TAPI_RAKSASA` | 3 |
| `NOL_KOLOM_PECAH` | 2 |
| `PULIH_RELASI_KOLOM_NILAI` | 1 |

## Kamus kode diagnosa

| Kode | Arti | Tindakan |
|---|---|---|
| `OK_LANGSUNG` | SQL sudah cocok dengan skema live | pakai sebagai bukti pola pertanyaan |
| `PULIH_RELASI` | pulih setelah ganti nama relasi (`vw_*` → `mv_*`) | idem |
| `PULIH_RELASI_KOLOM` | + ganti nama kolom | idem |
| `PULIH_RELASI_NILAI` | + normalisasi nilai (`MEMENUHI KETENTUAN` → `MK`, dst) | idem |
| `OK_TAPI_RAKSASA` | jalan, tapi >100 ribu baris **tanpa agregasi** | **bukan jawaban** — perlu agregasi sesuai pertanyaan |
| `NOL_TIDAK_DITEMUKAN` | pencarian teks tidak ketemu | nol baris = jawaban sah ("tidak ditemukan") |
| `NOL_ANTIJOIN_KOSONG` | himpunan "yang tidak pernah" memang kosong | ubah bentuk jadi peringkat porsi |
| `NOL_CAKUPAN_TABEL` | tabel hanya memuat sebagian periode | cari sumber pengganti (mis. rekonstruksi dari log) |
| `NOL_KOLOM_PECAH` | satu kolom lama pecah jadi dua di skema live | tulis ulang semantik |
| `NOL_NILAI_TIDAK_ADA` | nilai yang difilter tidak ada di kolom itu | pindahkan ke kolom yang benar |
| `NOL_PLACEHOLDER` | literal masih `'NAMA_..._TERTENTU'` | pair tidak pernah disubstitusi — saring sebelum dipakai |
| `NOL_FILTER_SEMPIT` | kombinasi filter menyempit sampai kosong | periksa tiap klausa terhadap katalog nilai |
| `ERR_KOLOM_DIHAPUS` | kolom sudah dihapus dari skema | **NOT COVERED**, tidak bisa ditulis ulang |
| `ERR_SQL_RUSAK` | SQL rusak sejak asalnya | tulis ulang |

## Peringatan

1. **"OK" hanya berarti "tidak error"** — bukan "menjawab pertanyaannya". Lihat kode
   `OK_TAPI_RAKSASA`; contoh konkretnya ada di dokumen naratif folder induk.
2. **Angka absolut adalah snapshot 2026-08-13.** ETL menambah baris tiap hari.
3. **`sql_dipakai_1baris` bukan SQL siap pakai.** Ia hasil terjemahan mekanis untuk menguji apakah
   pola pertanyaannya masih punya data — bukan jawaban yang sudah divalidasi maknanya.
4. Satu jebakan yang terbukti saat menyusun ini: **literal di dalam `lower()`/`upper()` jangan ikut
   dinormalisasi** — baik pada `=`, `LIKE`, maupun `IN (...)`. Melanggarnya membuat pair tampak
   "nol baris" padahal datanya ada.
