# 08 — Contoh Isian Form Asli & Artinya

> Berguna ketika ragu "angka ini di tabel bridge berasal dari isian yang mana". Folder [`contoh-datas/`](contoh-datas/) menyimpan 5 contoh isian form asli.
>
> **Catatan penting**: `staging` **tidak menyimpan** JSON mentah isian form. Yang tersedia hanya hasil pecahannya di tabel bridge. Contoh-contoh di folder ini adalah lampiran pembanding — supaya terlihat asal-usul tiap kolom bridge.

---

## 1. Kenapa isian form berbentuk khusus

Wizard pemeriksaan punya **banyak bentuk isian** tergantung jenis sarana, dan bentuk itu yang menentukan kasus tersebut masuk ke tabel bridge mana. Penunjuknya satu kolom: `fact_pemeriksaan.flag_varian_datas` ([04-routing-bridge.md](04-routing-bridge.md)).

| Bentuk isian | Wujudnya | Jenis sarana | Tabel bridge tujuan |
|---|---|---|---|
| **A — skor per aspek** | section per aspek dengan `opsi`/`n`/`fp`/`score` | pelayanan (Apotek, PKM, Klinik, RS, Toko Obat, PBF/IFK/IFP) | `bridge_pemeriksaan_skor_operasional` |
| **B — klausul Ya/Tidak** | klausul bernomor `a1..aN` + catatan, bisa bersarang | produksi/pangan/kosmetik/OT | `bridge_pemeriksaan_checklist` (+ `_temuan_observasi`) |
| **C — paste dokumen** | HTML MS Word mentah, bisa ratusan ribu karakter | semua | hanya jadi teks naratif — tidak bisa dihitung |

---

## 2. Lima contoh yang tersedia

| File | Bentuk | Menggambarkan |
|---|---|---|
| `case_291156_apotek.json` | A | Apotek lengkap: skor per aspek + daftar fast-moving antibiotika |
| `case_286187_spare8.json` | B | klausul bersih, semua jawaban "Ya" (kasus tanpa temuan) |
| `case_289850_tidak18.json` | B | 18 jawaban "Tidak" + sub-form importir & DIP |
| `case_289656_34klausul.json` | B | 34 klausul + sub-klausul bersarang + narasi panjang |
| `case_pbf_full.json` | C | paste dokumen Word utuh (termasuk XML gambar) |

---

### 2.1 `case_291156_apotek.json` — bentuk A (skor)

```json
"tx_pengadaan_obat":  { "n":"300", "fp":"3", "opsi":"yes",   "score":"100" },
"tx_penyerahan_dowa": { "n":"0",   "fp":"2", "opsi":"no",    "score":"0"   },
"tx_penyerahan_obat": { "n":"300", "fp":"3", "opsi":"apoteker", "score":"100" },
"tx_penyimpanan_obat":{ "n":"262.50", "fp":"3", "score":"262.5",
                        "wadah":"on","bentuk":"on","sentuh":"on","sistem":"on",
                        "jaminan":"on","kondisi":"on","kontaminasi":"on" },
"tx_pengembalian_mutasi": { "n":"196.89", "x":"0.75", "fp":"3",
                            "opsi":{"mutasi":"mostly"}, "score":"65.63" },
"tx_fast_moving_antibiotika": {
  "2": { "nama_zat_aktif":"Amoxicillin", "jumlah_penjualan":"360",
         "satuan_penjualan":"Kaplet", "jumlah_penjualan_tanpa_resep":"360" } }
```

Nilai layar: `yes` = Sesuai/Ya · `mostly` = Sebagian Besar · `rarely` = Sebagian Kecil · `no` = Tidak · `illegal` = Dugaan ilegal → `score` 100 / 50 / 25 / 0.

Yang menjelaskan kolom `staging`:

| Wujud nyata di contoh | Artinya untuk kolom `staging` |
|---|---|
| `opsi` kadang berisi jabatan (`apoteker`) atau JSON-string (`{"mutasi":"mostly"}`) | `bridge_pemeriksaan_skor_operasional.opsi` **bukan kolom penilaian tunggal** — memakai `opsi='no'` sebagai penanda temuan membuat sebagian aspek bernilai 0 |
| `score` ada yang `100` dan ada yang `262.5` | kolom `score` mencampur skala item (0–100) dengan nilai akumulasi (>100) |
| `n` / `fp` | skor mentah & faktor pembobot |
| `tx_fast_moving_antibiotika` berisi list zat aktif (key `1`,`2`,`3`) | bagian terstruktur yang **belum punya label aspek** di kamus (25.780 kasus) |
| `tx_total_n` / `tx_total_fp` | rekap skor kasus |

Key bernilai `"on"` menandai item yang diperiksa/dijawab.

### 2.2 `case_286187_spare8.json` — bentuk B tanpa temuan

```json
"penyusunan":  { "a1":{"aspect":"Ya","note":null}, "...": "a6" },
"penyimpanan": { "gudang":  { "aspect":"Ya" },
                 "display": { "aspect":"Ya" } }
```

Menjelaskan: jawaban berbentuk **Ya/Tidak** (bukan skor), dan grup juga menyimpan `aspect` di levelnya — karena itu satu kasus menghasilkan baris checklist baik di level grup (`tx_pemeriksaan.penyimpanan.gudang`) maupun di level klausul (`tx_pemeriksaan.penyusunan.a1`).

### 2.3 `case_289850_tidak18.json` — bentuk B dengan 18 "Tidak"

Menambahkan dua hal:

- `"dip": { "a1": "<p>Tidak terdapat DIP produk</p>", … }` → jawaban berupa **HTML**, tetap dipecah per klausul
- `"administrasi": { "importir": { "a1": {…,"note":"memiliki LOA"}, … "a10" } }` → klausul sampai `a10` dengan catatan naratif

Menjelaskan kolom `catatan` (dari `note`) dan `nilai_aspek = 'Tidak'`.

### 2.4 `case_289656_34klausul.json` — bentuk B dengan sub-klausul

```json
"penyimpanan": { "gudang": { "a3": { "p1":{"aspect":"Tidak","note":"Ditemukan hama (kecoa)…"},
                                    "p2":{…}, "p3":{…}, "p4":{…}, "p5":{…},
                                    "aspect":"Ya", "note":"-" },
                             "aspect":"Ya" } }
```

Menjelaskan: `path` di checklist bisa bertingkat sampai klausul ke-2 (`…gudang.a3.p1`), dan `catatan` bisa panjang. Ada juga `other` berisi HTML ±1.500 karakter yang tidak bisa dipecah jadi klausul.

### 2.5 `case_pbf_full.json` — bentuk C (paste dokumen)

```json
"khusus": [ "<p class=\"MsoNormal\" style=\"margin-left:14.2pt;…\"> … </p>" ]
```

Isinya dokumen Word utuh: tag `MsoNormal`, daftar bernomor, bahkan XML gambar dengan path `C:/Users/…/clip_image001.png`. Satu section pernah mencapai **264.736 karakter**.

Menjelaskan: ada kasus yang **tidak bisa dihitung** sebagai item — hanya bisa dibaca sebagai teks.

---

## 3. Colokkan contoh ke tabel `staging`

| Yang terlihat di contoh | Kolom `staging` yang terisi |
|---|---|
| section per aspek + `opsi`/`n`/`fp`/`score` | `bridge_pemeriksaan_skor_operasional` (`area_key`, `opsi`, `n`, `fp`, `score`) |
| klausul `a1..aN` + `aspect` | `bridge_pemeriksaan_checklist` (`path`, `nilai_aspek`, `catatan`) |
| `level` | `bridge_pemeriksaan_checklist.nilai_aspek` (nilai Major/Minor/Kritikal/Lanjut) |
| `criteria` | `bridge_pemeriksaan_checklist.nilai_aspek` (nilai OK/Lanjut/Tidak Berlaku) |
| section form vaksin | `bridge_pemeriksaan_vaksin` (19 varian section) |
| 8 section naratif faskes | `bridge_pemeriksaan_narasi_faskes` (profil/pengadaan/penyimpanan/distribusi/personalia/dokumentasi/gudang/lain) |
| ID file / lampiran | `fact_pemeriksaan.tl_attachment`, `tl_ba`, `tl_attachment_pusat`, `tl_ba_pusat` |
| kesimpulan, grade, counter kekritisan, tindak lanjut | kolom `fact_pemeriksaan` |

Contoh: kasus `291156` di contoh-datas berpasangan dengan 22 baris `bridge_pemeriksaan_skor_operasional` di `staging`; kasus `286187` dengan 8 baris `bridge_pemeriksaan_checklist`.

---

## 4. Cara memeriksa satu kasus di `staging`

```sql
-- 1. tentukan dulu variannya
SELECT id, flag_varian_datas, jenis_id, tgl_start
FROM public.fact_pemeriksaan WHERE id = 291156;

-- 2. lihat bridge yang relevan (contoh untuk bentuk A)
SELECT a.area_key, COALESCE(a.aspek_ktl_nama, a.aspek_label) AS aspek,
       s.opsi, s.n, s.fp, s.score
FROM public.bridge_pemeriksaan_skor_operasional s
LEFT JOIN public.dim_pemeriksaan_aspek a ON a.area_key = s.area_key
WHERE s.pemeriksaan_id = 291156
ORDER BY a.area_key;
```

Query "cek semua bridge sekaligus" ada di [04-routing-bridge.md](04-routing-bridge.md) §5.
