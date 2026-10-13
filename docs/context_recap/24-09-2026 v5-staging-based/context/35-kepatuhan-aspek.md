pengadaan · penerimaan · penyimpanan · penyerahan · pengembalian · pencatatan dan pelaporan · pemusnahan · pendistribusian · skor · kepatuhan · aspek

# Kepatuhan per aspek (varian pelayanan)

## Apa yang halaman ini putuskan

Untuk varian pelayanan, jawaban per aspek tersimpan di `bridge_pemeriksaan_skor_operasional` dengan
`area_key` → `dim_pemeriksaan_aspek`. **Kolom `opsi` dan `score` tidak punya satu arti global** — artinya
diputuskan **per `area_key`**.

## Tabel keputusan

| Kata dalam pertanyaan | Filter |
|---|---|
| "pengadaan" · "penerimaan" · "penyimpanan" · "penyerahan" · "pengembalian" · "pencatatan dan pelaporan" · "pemusnahan" | label aspek |
| "pendistribusian" · "distribusi" | label kamus resminya **Penyaluran** |
| "efek samping (SAS)" · "pencantuman kode (SAS)" | label khusus |
| aspek tertentu + jenis sarana | filter **dua-duanya** |
| "kepatuhan" tanpa aspek | seluruh aspek, **jangan** dijumlahkan menjadi satu angka tunggal |

## Aturan pertama: label aspek wajib `COALESCE`

```sql
COALESCE(a.aspek_ktl_nama, a.aspek_label) AS aspek
```

Tanpa ini, sebagian aspek bervolume besar **hilang dari hasil** — `status_kamus` menandai aspek yang
belum punya padanan di kamus resmi.

## Matriks operasi — per area_key, bukan per kolom

| area_key (contoh) | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| aspek pengadaan | `opsi` bernilai jawaban baku | normalisasi ejaan dulu | `dim_pemeriksaan_aspek.area_key` | sebut satuan |
| aspek penyimpanan | `opsi` **kosong**; sinyalnya ada di `score`/key item | pakai `score` dengan hati-hati | idem | jangan rata-ratakan mentah |
| aspek penerimaan | `opsi` memuat **jabatan/orang**, bukan hanya jawaban | normalisasi kapitalisasi | idem | sebut bahwa isinya peran |
| aspek pengembalian | `opsi` berbentuk **JSON object** | jangan bandingkan string mentah | idem | perlu ekstraksi key |
| aspek pemusnahan | tidak ada nilai penanda "tidak" | laporkan apa adanya | idem | jangan klaim "nol temuan" sebagai fakta kuat |

**Jangan pernah** memakai `opsi = 'no'` sebagai definisi temuan untuk **semua** aspek. Buktinya: ada
aspek yang nilainya tidak pernah `no`, ada yang isinya jabatan, ada yang `opsi`-nya kosong seluruhnya.

## Cara mencari — kontrak per area (lakukan sekali per aspek yang ditanya)

```sql
-- 1. daftar area_key + status kamusnya
SELECT area_key, aspek_ktl_kode, aspek_ktl_nama, aspek_label, status_kamus
FROM public.dim_pemeriksaan_aspek ORDER BY area_key;

-- 2. vocab `opsi` nyata untuk aspek itu
SELECT COALESCE(s.opsi,'(null)') AS opsi, count(*)
FROM public.bridge_pemeriksaan_skor_operasional s
WHERE s.area_key = '<area_key>'
GROUP BY 1 ORDER BY 2 DESC;

-- 3. sebaran `score` (memisahkan skala item dari nilai akumulasi)
SELECT COALESCE(s.score,'(null)') AS score, count(*)
FROM public.bridge_pemeriksaan_skor_operasional s
WHERE s.area_key = '<area_key>'
GROUP BY 1 ORDER BY 2 DESC LIMIT 20;
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| aspek tertentu selalu "0 tidak sesuai" | aspek itu memang tidak menyimpan nilai `no` | jalankan query vocab `opsi` |
| satu makna terpecah dua baris | ejaan berbeda (`Lainnya` vs `lainnya`, `Asisten Apoteker` vs `asisten`) | normalisasi sebelum mengelompokkan |
| filter JSON tidak kena | `opsi` berisi JSON object, bukan string | ekstrak key, jangan bandingkan mentah |
| rata-rata skor terlihat aneh | `score` mencampur skala item (0–100) dan akumulasi (>100) | pisahkan/dokumentasikan |
| aspek hilang dari hasil | label tidak pakai `COALESCE` | perbaiki SELECT |

## Batas

- Hanya varian pelayanan (Apotek, PKM, Klinik, Toko Obat, RS, PBF/IFK/IFP) yang punya aspek berkamus.
- Varian produksi memakai klausul → `37`; keduanya **tidak boleh dijumlahkan** (satuan berbeda).
- Pertanyaan tentang aspek pada sarana produksi → jawab lewat `37`, bukan halaman ini.

## Rute

- Klausul & severitas (produksi) → **lihat** `37-klausul-dan-severity.md`
- Routing varian → **lihat** `01-peta-data-dan-routing.md`
- Label panel aspek → **lihat** `05-filter-katalog.md`
- Menyebut antibiotik → **lihat** `45` dan `95`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `bridge_pemeriksaan_skor_operasional` | `pemeriksaan_id`, `area_key`, `opsi`, `score`, `n`, `fp` | — |
| `dim_pemeriksaan_aspek` | `area_key`, `aspek_ktl_kode`, `aspek_ktl_nama`, `aspek_label`, `status_kamus` | `resmi`, `belum_ada_di_kamus` |
| `fact_pemeriksaan` | `id`, `is_data_uji` | — |
