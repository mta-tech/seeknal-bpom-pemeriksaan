Jenis pangan — dan di kolom mana penanda MD / IRT sebenarnya berada.

## Dua tempat berbeda

| Konsep | Di mana | Bentuk |
|---|---|---|
| **Penanda MD / IRT / UMKM** | `mv_pemeriksaan.jenis_sarana` | bagian dari nama jenis fasilitas |
| **Jenis pangan** (produk apa yang diproduksi) | `mv_pemeriksaan_jenis_pangan.jenis_pangan_name` | tabel terpisah |

Ini pemisahan yang paling sering keliru. Skema lama menggabungkan komoditi dan penanda MD dalam
satu kolom; sekarang terpisah.

> **"Sarana produksi MD" bukan filter komoditi.** Yang benar:
> `sarana = 'PRODUKSI'` **AND** `jenis_sarana LIKE '%MD%'`.
> Memfilter `komoditi LIKE '%MD%'` mengembalikan **nol baris tanpa error**.

Penanda di `jenis_sarana` mencakup varian MD, varian IRT/PIRT, dan varian UMKM menuju MD. Ambil
daftarnya lebih dulu (jalur **P2**) supaya polanya tepat; jangan mengetik dari ingatan.

## Tabel jenis pangan

`mv_pemeriksaan_jenis_pangan` menempel ke fakta lewat `id_pemeriksaan`. Satu pemeriksaan bisa
punya **beberapa** jenis pangan (ada kolom posisi dalam array) — jadi join ini **melipatgandakan**
baris induk. Hitung dengan `COUNT(DISTINCT mp.id)` bila entity-nya pemeriksaan.

Tidak semua pemeriksaan punya baris di tabel ini; join harus LEFT dari fakta bila pertanyaannya
tentang populasi.

## Istilah pengguna

| Istilah | Cara mengikat |
|---|---|
| **AMDK** / air minum dalam kemasan | nilai `jenis_pangan_name` yang memuat *air minum* |
| **garam**, **tepung**, **minyak nabati**, **lemak** | nilai yang memuat kata itu |
| **MD** | `jenis_sarana`, bukan jenis pangan |
| **PIRT / IRT** | `jenis_sarana`, bukan jenis pangan |

⚠️ Nilai `jenis_pangan_name` bercampur antara **kategori produk pangan** dan **kategori
penyimpanan** (istilah seperti kering, beku, dingin). Bila pertanyaannya tentang jenis produk,
sebutkan bahwa sebagian nilai adalah kategori penyimpanan, bukan produk.

## Pola pertanyaan yang lazim

| Pertanyaan | Bentuk filter |
|---|---|
| tren pemeriksaan sarana produksi MD jenis pangan X | `sarana='PRODUKSI'` + `jenis_sarana LIKE '%MD%'` + join jenis pangan + pola nama |
| berapa sarana produksi AMDK yang TMK di balai X tahun Y | idem + `kesimpulan='TMK'` + `nama_upt ILIKE` + rentang tanggal |
| jenis pangan apa yang paling banyak TMK | join jenis pangan, `GROUP BY jenis_pangan_name`, `COUNT(DISTINCT mp.id)` |

Populasi hasil kombinasi filter ini bisa **sangat kecil**. Bila hasilnya tinggal sedikit baris,
katakan apa adanya — jangan melonggarkan filter diam-diam supaya angkanya terlihat lebih besar.

## Rute

- Kembali ke konsep sarana → **naik** ke `10-sarana-dan-fasilitas.md`.
- Menyebut komoditi → **seberang** `20-komoditi.md`.
- Menyebut vonis → **seberang** `30-kesimpulan.md`.
