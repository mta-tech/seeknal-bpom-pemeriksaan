belum · tanpa · kosong · tidak punya · tidak terisi · tidak melaporkan · sentinel · soft delete · cakupan

# Kualitas data, sentinel, dan karantina kolom

## Apa yang halaman ini putuskan

Apakah sebuah kekosongan berarti "belum diisi", "tidak berlaku", atau "tidak ada kolomnya" — dan kolom
mana yang **tidak boleh dikutip**.

## Tabel keputusan — membaca kekosongan sebelum menyaring

| Pertanyaan | Tindakan |
|---|---|
| "belum punya X" | hitung keterisian kolom X lebih dulu; bila kolomnya kosong seluruhnya, jawabannya **seluruh populasi** — bukan temuan data |
| "yang tidak melaporkan" | cek apakah ada kolomnya; bila tidak ada → P5 |
| "kosong" pada kolom berkode | kenali bentuk sentinelnya (bukan selalu NULL) |
| kolom dipakai sebagai penyaring | **cek keterisian dulu**; kolom kosong = filter yang membuang populasi |

## Kolom yang praktis kosong (jangan dipakai sebagai penyaring)

| Kolom | Gejala |
|---|---|
| `sediaan_kode` | hampir selalu kosong |
| `unit_id` · `penelusuran_id` · `kasus_id` · `metode_inspeksi` | terisi sangat tipis |
| `tl_ba_pusat` · `tl_attachment_pusat` | nyaris tidak terisi |
| `status_label` | kosong seluruhnya |
| `dim_produk.is_imported` | bernilai sama di semua baris |

## Daftar karantina (jangan dikutip — pakai penggantinya)

| Jangan dikutip | Alasan | Pakai ini |
|---|---|---|
| kolom provinsi-tujuan distribusi sebagai "klasifikasi distribusi" | itu tujuan distribusi pabrik Pangan MD | nyatakan honest gap |
| `status_label` | kosong | `status_code` + label dari luar |
| `legal_id` difilter satu `type` | merujuk lebih dari satu kamus | tampilkan `type` sebagai hasil |
| `opsi` sebagai penanda temuan global | maknanya per `area_key` | `35` |
| `nilai_aspek` sebagai satu konsep | memuat empat makna | `37` |
| tabel domain pengawasan | akses ditolak | `95` |

## Matriks operasi

| Kolom | Menyaring | Mengelompokkan | Men-join | Memeringkat |
|---|---|---|---|---|
| `dihapus_di_sumber` | **flag, bukan eksklusi otomatis** — default: baris ikut | boleh untuk audit | — | — |
| `is_data_uji` | eksklusi saat membahas kegiatan nyata | — | — | — |
| `is_kasus_draft` | eksklusi saat angka diklaim final | — | — | — |
| nilai teks bebas | probe dulu, saring dengan nilai temuan | **normalisasi sebelum mengelompokkan** | — | peringkat tanpa normalisasi tidak sahih |

## Cara mencari

```sql
-- keterisian kolom yang dicurigai
SELECT count(*) AS total, count(<kolom>) AS terisi FROM public.<tabel>;

-- kolom mana yang benar-benar kosong? (pola: satu kali per pertanyaan, bukan borongan)
SELECT count(*) FILTER (WHERE <kolom> IS NULL) AS kosong FROM public.<tabel>;

-- kategori temuan: kode mana yang tidak ada di kamus
SELECT e.kode, COALESCE(d.name,'(tidak di kamus)') AS nama, count(*) AS baris
FROM public.bridge_pemeriksaan_temuan t
CROSS JOIN LATERAL jsonb_array_elements_text(t.kategori_kode) e(kode)
LEFT JOIN public.dim_master_data d
       ON d.master_data_id::text = e.kode AND d.type = 'KATEGORI_TEMUAN_PRODUK'
GROUP BY 1, 2 ORDER BY 3 DESC;
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| "belum punya X" = seluruh populasi | kolomnya memang kosong | hitung keterisian |
| peringkat memuat "tidak diketahui" di puncak | sentinel berbentuk kata dianggap entitas | periksa nilai teratas sebelum menyajikan |
| satu entitas terpecah beberapa baris | spasi/kapitalisasi | normalisasi |
| filter mengembalikan nol baris | nilai diketik dari ingatan | probe dulu |
| sebagian hasil hilang tanpa error | memfilter kolom multi-kamus dengan satu `type` | tampilkan `type` sebagai hasil |

## Batas

- Kekosongan **tidak selalu** cacat: pada sebagian kolom ia berarti "tidak berlaku untuk kelompok itu".
- Bila kolom yang dipakai punya keterisian rendah, **sebutkan cakupannya sebelum** menyajikan
  peringkat atau persentase.

## Rute

- Entity & eksklusi → **lihat** `00-menghitung.md`
- Label panel tanpa kolom → **lihat** `05-filter-katalog.md`
- Batas domain → **lihat** `95-batas-domain.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `dim_sarana` | `dihapus_di_sumber` | — |
| `dim_master_data` | `dihapus_di_sumber`, `type` | `KATEGORI_TEMUAN_PRODUK` |
| `fact_pemeriksaan` | `is_data_uji`, `sediaan_kode`, `unit_id`, `penelusuran_id`, `kasus_id`, `metode_inspeksi`, `tl_ba_pusat`, `tl_attachment_pusat` | — |
| `dim_status_code` | `status_label` | — |
| `dim_produk` | `is_imported` | — |
