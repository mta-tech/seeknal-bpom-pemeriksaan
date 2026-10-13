# 07 — Hasil Verifikasi Live

> Dijalankan 22 Sep 2026 · tunnel `srv29-staging` → `localhost:5432` · database `staging`, schema `public` · **read-only**.
>
> Setiap kode dan nilai yang akan ditulis ke context harus berasal dari sini — bukan dari ingatan, dan bukan dari domain lain.

---

## 1. Hasil pemeriksaan

### V1 — Kolom yang dipakai label panel

| table | column | tipe | Kesimpulan |
|---|---|---|---|
| `dim_sarana` | `legal_id` | bigint | ada (multi-kamus) |
| `fact_pemeriksaan` | `klasifikasi_id` | bigint | komoditi |
| `fact_pemeriksaan` | `klasifikasi_sarana_kode` | text | khusus Pangan |
| `dim_status_code` | `status_label` | text | ada, **kosong** |
| `dim_balai` | `target_sampling` · `target_sarana` | bigint | ada, terisi penuh |
| `bridge_pemeriksaan_temuan` | `klasifikasi_produk_kode` | bigint | lokal/impor produk |
| `fact_pemeriksaan_profil_pangan_md` | `distribusi_provinsi_kode` | jsonb | **bukan** klasifikasi distribusi |
| — | *(kolom klasifikasi distribusi)* | — | **tidak ada** |

### V2 — Target pada `dim_balai`

108 balai; `target_sampling` terisi **108/108**; `target_sarana` terisi **108/108** → halaman `85` boleh mengandalkan kolom ini.

### V3 — Label status

`dim_status_code`: 35 baris, label terisi **0** → label tahap tidak bisa diambil dari tabel ini.

### V4 — Routing varian (`flag_varian_datas`)

| Nilai | Kasus | Bridge |
|---|---:|---|
| `pola1_direct` | 107.778 | checklist |
| `clusterC_skor` | 64.243 | skor operasional |
| `pola1_nested` | 61.266 | checklist |
| `pola1_observation` | 10.421 | checklist |
| `clusterC_vaksin` | 7.697 | vaksin |
| `pola2_klasifikasi` | 4.137 | temuan observasi |
| `clusterF_cpkb` | 2.610 | **tidak ada** |
| `clusterC_naratif` | 1.182 | narasi faskes |
| `lainnya` | 14 | **tidak ada** |

### V5 — `opsi` per `area_key` (bukti kontrak per aspek)

| area_key | Isi `opsi` | Kesimpulan |
|---|---|---|
| `tx_pemusnahan_obat` | N/A 47.026 · yes 15.521 · null 1.304 | tidak ada `no` → bukan indikator temuan |
| `tx_penerimaan_obat` | jabatan + Ya/Tidak; `Lainnya` 4.121 vs `lainnya` 3.868; `Asisten Apoteker` 3.300 vs `asisten` 161 | campur makna **+ duplikat ejaan** |
| `tx_pengembalian_mutasi` | `{"mutasi":"yes"}` 46.610 · `{"mutasi":"mostly"}` 7.115 · null 6.110 · `{"mutasi":"rarely"}` 4.016 | JSON object |
| `tx_penyimpanan_obat` | null 63.756 | sinyal ada di `score`/key item, bukan `opsi` |

### V6 — Vocab `nilai_aspek` (15 nilai)

`OK` 3.845.010 · `Ya` 1.190.918 · `Tidak Berlaku` 556.000 · `Minor` 340.959 · `B` 295.644 · `Tidak` 279.310 · `Major` 229.710 · `T` 201.488 · `C` 147.259 · `Lanjut` 145.192 · *(kosong)* 79.019 · `Serius` 37.226 · `K` 20.084 · `Kritis` 18.544 · `Kritikal` 1.802

Empat makna dalam satu kolom: konformitas · grade · severitas · status.

### V7 — Kategori temuan: kamus vs data

| Ukuran | Nilai |
|---|---:|
| Kode di kamus `KATEGORI_TEMUAN_PRODUK` | 28 |
| Kode berbeda yang dipakai di data | **49** |
| Kode dipakai yang **tidak ada** di kamus | **27** (444 baris) |

---

## 2. Yang diberi makan oleh tiap verifikasi

| Verifikasi | Halaman yang memakai |
|---|---|
| V1 | `05-filter-katalog` (tabel dimensi + 3 honest gap) |
| V2 | `85-target-capaian` |
| V3 | `31-status-dan-alur`, `05` |
| V4 | `01-peta-data-dan-routing` |
| V5 | `35-kepatuhan-aspek` (kontrak per area) |
| V6 | `37-klausul-dan-severity` |
| V7 | `40-temuan-produk` (bucket tak terpetakan) |

---

## 3. Yang masih perlu diverifikasi saat menulis halaman

| # | Yang perlu dipastikan | Halaman |
|---|---|---|
| 1 | Daftar lengkap 47 `area_key` + `status_kamus` | `35` |
| 2 | Rentang dan keterisian `tgl_start`/`tgl_end` | `80` |
| 3 | Daftar lengkap tipe kamus (72) + jumlah kode per tipe | `20`,`10`,`05` |
| 4 | Pemakaian tiap baris `dim_pemeriksaan_kesimpulan` | `30` |
| 5 | Cakupan severitas per jenis sarana | `37` |
| 6 | Kolom yang praktis kosong (untuk daftar "jangan dipakai") | `90` |
| 7 | Distribusi status 16 nilai + jumlah kasus | `31` |
| 8 | Keterisian kolom `legal_id` per nilai kamus | `05` |
| 9 | Cakupan `klasifikasi_sarana_kode` per jenis sarana | `05`,`50` |
| 10 | Statistik kualitas `jumlah_temuan`/`harga_total` | `41` |

---

## 4. Cara mengulang verifikasi

```bash
# 1. pastikan tunnel hidup
ssh -f -N srv29-staging
ss -tlnp | grep ':5432'

# 2. ambil DSN dari env project (tanpa menampilkan password)
cd /home/mta/projects/seeknal_audit/seeknal-bpom-pemeriksaan
url=$(grep -m1 '^WAREHOUSE_URL=' .env | cut -d= -f2-)

# 3. contoh probe
psql "$url" -P pager=off -c "SELECT flag_varian_datas, count(*) FROM public.fact_pemeriksaan GROUP BY 1 ORDER BY 2 DESC;"
```

Aturan saat memverifikasi: read-only, satu statement per pemanggilan, dan **jangan** menyalin nilai hasil ke halaman context sebagai jawaban — halaman hanya boleh memuat **kode domain** dan **cara mencarinya**.

---

## 5. Catatan

- Semua angka di atas adalah kondisi pada tanggal verifikasi; angka yang bergerak wajar (mis. jumlah kasus) **tidak** boleh dijadikan patokan di halaman context.
- Yang boleh ditulis di context: **daftar kode/tipe** (kosakata domain, stabil) dan **cara mencarinya**; yang tidak boleh: angka hasil.
- Untuk pembanding domain lain (`../seeknal-bpom-rpo-erba/.../v4-sep-w1/`) nilai RPO **tidak** boleh dipakai di sini meski namanya mirip.
