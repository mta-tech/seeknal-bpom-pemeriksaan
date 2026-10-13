# 04 — Routing Bridge: tabel mana untuk kasus mana

> **Ini jebakan nomor satu di domain ini.** Kalau `flag_varian_datas`-nya `clusterC_skor` tapi yang dibaca `bridge_pemeriksaan_checklist`, hasilnya **kosong — tanpa pesan error**. Orang akan menyimpulkan "tidak ada data" padahal cuma salah tabel.
>
> Verifikasi: 22 Sep 2026.

---

## 1. Tabel routing

| `flag_varian_datas` | Kasus | Porsi | Baca bridge ini | Karakteristik |
|---|---:|---:|---|---|
| `pola1_direct` | 107.778 | 41,6% | `bridge_pemeriksaan_checklist` | klausul `a1..aN`, jawaban OK/Tidak Berlaku/B/T/C/K/severity |
| `clusterC_skor` | 64.243 | 24,8% | `bridge_pemeriksaan_skor_operasional` | **satu-satunya yang punya kamus aspek** (`area_key`) |
| `pola1_nested` | 61.266 | 23,6% | `bridge_pemeriksaan_checklist` | klausul bersarang, jawaban Ya/Tidak + catatan |
| `pola1_observation` | 10.421 | 4,0% | `bridge_pemeriksaan_checklist` | Lanjut/Major/Minor/Kritikal |
| `clusterC_vaksin` | 7.697 | 3,0% | `bridge_pemeriksaan_vaksin` | 19 `section_key` form vaksin — **baru 21 Sep 2026** |
| `pola2_klasifikasi` | 4.137 | 1,6% | `bridge_pemeriksaan_temuan_observasi` | kode observasi GMP baku + `kriteria` |
| `clusterF_cpkb` | 2.610 | 1,0% | **tidak ada bridge** | Aturan #15 — hanya header + narasi |
| `clusterC_naratif` | 1.182 | 0,5% | `bridge_pemeriksaan_narasi_faskes` | 8 section narasi bebas |
| `lainnya` | 14 | 0,0% | **tidak ada bridge** | sangat jarang |

Cara memastikan untuk satu kasus:

```sql
SELECT flag_varian_datas FROM public.fact_pemeriksaan WHERE id = :pemeriksaan_id;
```

## 2. Tabel routing terpisah: `bridge_pemeriksaan_temuan`

Bridge temuan produk **tidak** ditentukan flag — dia lahir dari FLOW 4 (daftar temuan) dan bisa ada di flag apa pun. Karena itu saat menghitung temuan, jangan pakai routing di atas.

| Flag | Kasus | Punya baris temuan |
|---|---:|---:|
| pola1_direct | 107.778 | 14.905 |
| pola1_nested | 61.266 | 15.346 |
| clusterC_skor | 64.243 | 2.341 |
| clusterC_naratif | 1.182 | 70 |
| clusterF_cpkb | 2.610 | 57 |
| pola2_klasifikasi | 4.137 | 52 |
| pola1_observation | 10.421 | 45 |
| clusterC_vaksin | 7.697 | 19 |
| lainnya | 14 | 0 |

---

## 3. Matriks cakupan: kasus vs bridge yang terisi

Angka di bawah hasil silang `fact_pemeriksaan` dengan semua bridge — memperlihatkan tabel mana yang benar-benar terisi per flag (segregasinya bersih: tidak ada silang antar-bridge).

| flag | Kasus | checklist | observasi | skor | vaksin | narasi_faskes | temuan |
|---|---:|---:|---:|---:|---:|---:|---:|
| pola1_direct | 107.778 | 97.567 | – | – | – | – | 14.905 |
| clusterC_skor | 64.243 | – | – | 63.845 | – | – | 2.341 |
| pola1_nested | 61.266 | 61.012 | – | – | – | – | 15.346 |
| pola1_observation | 10.421 | 8.756 | – | – | – | – | 45 |
| clusterC_vaksin | 7.697 | – | – | 4 | 7.660 | 33 | 19 |
| pola2_klasifikasi | 4.137 | – | 4.022 | – | – | – | 52 |
| clusterF_cpkb | 2.610 | – | – | – | – | – | 57 |
| clusterC_naratif | 1.182 | – | – | 2 | – | 1.035 | 70 |
| lainnya | 14 | – | – | – | – | – | 0 |

**Ringkasan cakupan detail per kasus:**

| flag | Punya bridge | Kosong | % gap |
|---|---:|---:|---:|
| pola1_direct | 97.567 | 10.211 | 9,5% |
| clusterF_cpkb | 0 | 2.610 | 100% (memang belum ada bridge) |
| pola1_observation | 8.756 | 1.665 | 16,0% |
| clusterC_skor | 63.845 | 398 | 0,6% |
| pola1_nested | 61.012 | 254 | 0,4% |
| clusterC_naratif | 1.037 | 145 | 12,3% |
| pola2_klasifikasi | 4.022 | 115 | 2,8% |
| lainnya | 0 | 14 | 100% |
| clusterC_vaksin | 7.697 | 0 | 0% |
| **Total** | — | **15.412** | 5,9% |

Query-nya:

```sql
WITH b AS (
  SELECT pemeriksaan_id FROM public.bridge_pemeriksaan_checklist
  UNION SELECT pemeriksaan_id FROM public.bridge_pemeriksaan_skor_operasional
  UNION SELECT pemeriksaan_id FROM public.bridge_pemeriksaan_temuan_observasi
  UNION SELECT pemeriksaan_id FROM public.bridge_pemeriksaan_vaksin
  UNION SELECT pemeriksaan_id FROM public.bridge_pemeriksaan_narasi_faskes
)
SELECT f.flag_varian_datas, count(*) AS kasus,
       count(b.pemeriksaan_id) AS punya_bridge,
       count(*) - count(b.pemeriksaan_id) AS tanpa_bridge
FROM public.fact_pemeriksaan f LEFT JOIN b ON b.pemeriksaan_id = f.id
GROUP BY 1 ORDER BY 4 DESC;
```

---

## 4. Jenis sarana per flag (hasil verifikasi)

| flag | Jenis sarana yang memakai |
|---|---|
| `clusterC_skor` | Apotek 26.611 · PKM 13.122 · Klinik 9.991 · Toko Obat 6.765 · IFRS Swasta 4.040 · IFRS Pemerintah 3.322 |
| `pola1_nested` | Kosmetik 36.875 · Obat Tradisional 17.156 · Suplemen 6.880 · Bahan Berbahaya 101 |
| `clusterC_vaksin` | faskes klaster C, dominan PKM |
| `clusterC_naratif` | faskes klaster C, dominan Apotek |
| `pola1_direct` | Pangan · Pangan MD · Pangan IRT (volume terbesar: Pangan 2.921.028 item, Pangan MD 2.408.942 item) |
| `pola1_observation` | PBF 15.254 item · IFK 12.441 item (dari item ber-severity) |
| `pola2_klasifikasi` | `jenis_id` 4 (OT/CPOTB) · 8 (Sarana Produksi Obat) · 9 (Suplemen) |
| `clusterF_cpkb` | `jenis_id`=7 (Kosmetik CPKB) |

---

## 5. Query "cek semua bridge satu kasus" (untuk menyelidiki satu kasus)

```sql
SELECT f.id,
       (SELECT count(*) FROM public.bridge_pemeriksaan_checklist        WHERE pemeriksaan_id=f.id) checklist,
       (SELECT count(*) FROM public.bridge_pemeriksaan_skor_operasional WHERE pemeriksaan_id=f.id) skor,
       (SELECT count(*) FROM public.bridge_pemeriksaan_temuan           WHERE pemeriksaan_id=f.id) temuan,
       (SELECT count(*) FROM public.bridge_pemeriksaan_petugas          WHERE pemeriksaan_id=f.id) petugas,
       (SELECT count(*) FROM public.fact_pemeriksaan_approval           WHERE pemeriksaan_id=f.id) approval,
       (SELECT count(*) FROM public.fact_pemeriksaan_narasi             WHERE pemeriksaan_id=f.id) narasi,
       (SELECT count(*) FROM public.bridge_pemeriksaan_vaksin           WHERE pemeriksaan_id=f.id) vaksin
FROM public.fact_pemeriksaan f
WHERE f.id = :pemeriksaan_id;
```

Contoh hasil untuk kasus 287342 (Apotek): checklist 0 · skor 22 · temuan 0 · petugas 2 · approval 5 · narasi 6 · vaksin 0.

---

## 6. Vocab `nilai_aspek` berbeda per varian — jangan digabung mentah

| sumber_pola | Nilai yang muncul (jumlah item) |
|---|---|
| `pola1_direct` | OK 3.845.010 · Tidak Berlaku 556.000 · Minor 317.813 · **B** 295.644 · **T** 201.488 · Major 200.930 · **C** 147.259 · Serius 37.226 · **K** 20.084 · Kritis 18.544 · Lanjut 18.484 · kosong 55.089 |
| `pola1_nested` | **Ya** 1.190.894 · **Tidak** 279.310 · kosong 473 |
| `pola1_observation` | Lanjut 126.708 · Major 28.780 · kosong 23.457 · Minor 23.146 · Kritikal 1.802 · Ya 24 |

Kolom yang sama memuat **tiga sistem kode berbeda**: konformitas (OK/Tidak Berlaku), grade (B/T/C/K), dan severity (Minor/Major/Kritis/Serius/Kritikal). Sebaran severity per jenis sarana:

| Jenis sarana | Item ber-severity | Total item |
|---|---:|---:|
| Pangan MD | 319.196 | 2.408.942 |
| Pangan | 219.845 | 2.921.028 |
| Pangan IRT | 35.143 | 379.327 |
| PBF | 29.473 | 111.508 |
| IFK | 22.258 | 83.831 |
| IFP | 1.997 | 8.578 |
| UMKM / Intensifikasi | 313 / 16 | 3.060 / 1.214 |
| **Kosmetik · Obat Tradisional · Suplemen · Bahan Berbahaya** | **0** | 807.482 · 397.464 · 264.317 · 1.414 |

Untuk jenis yang nol itu, satu-satunya kekritisan yang tersedia adalah per kasus (`kritis_count`/`major_count`/`minor_count`/`level_kesimpulan`) — dan itu pun hanya untuk sebagian kasus.
