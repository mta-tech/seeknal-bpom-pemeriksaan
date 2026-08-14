Kesimpulan pemeriksaan — vonis kepatuhan sarana.

## Kolom `kesimpulan`

Satu kolom, memuat hasil akhir pemeriksaan sarana. Nilainya berupa singkatan huruf besar.

| Kode | Arti | Sifat |
|---|---|---|
| `MK` | Memenuhi Ketentuan | vonis kepatuhan |
| `TMK` | Tidak Memenuhi Ketentuan | vonis kepatuhan |
| `TDP` | Tidak Dapat Diperiksa | **bukan vonis** — pemeriksaan tidak terjadi |
| `TTP` | Tutup | **bukan vonis** — sarana tutup saat didatangi |
| `TMBB` | Tidak Memenuhi ketentuan Bahan Berbahaya | vonis khusus, sangat jarang |
| `NULL` | **string empat huruf**, bukan SQL NULL | belum berkesimpulan |

## Dua jebakan wajib

**1. Sentinel berupa string.** Nilai `'NULL'` adalah teks, bukan SQL NULL. `WHERE kesimpulan IS NULL`
mengembalikan nol baris. Yang benar `kesimpulan = 'NULL'` atau `kesimpulan <> 'NULL'`.

**2. `TDP` dan `TTP` bukan kegagalan kepatuhan.** Keduanya berarti pemeriksaan **tidak jadi
dilakukan** — sarananya tutup, atau tidak dapat diperiksa. Menghitung "tingkat kepatuhan" dengan
denominator seluruh baris memasukkan keduanya dan menurunkan angka MK secara semu.

> Tingkat kepatuhan dihitung pada populasi yang **benar-benar berkesimpulan**:
> `kesimpulan IN ('MK','TMK')`. Sebutkan berapa bagian populasi yang dikeluarkan.

Sebaliknya, pertanyaan **"berapa sarana yang tutup"** justru menargetkan `TTP` — dan
**"tidak dapat diperiksa"** menargetkan `TDP`. Keduanya pertanyaan yang sah dan berbeda.

## Terjemahan istilah pengguna

| Istilah pengguna | Kode |
|---|---|
| memenuhi ketentuan · patuh · lolos | `MK` |
| tidak memenuhi ketentuan · TMK · tidak patuh · bermasalah | `TMK` |
| tutup · sedang tutup · tidak beroperasi | `TTP` |
| tidak dapat diperiksa · TDP | `TDP` |
| "tutup dan/atau tidak berproduksi" | `TTP` dan `TDP` — dua kode, sebutkan keduanya |

## Istilah dari domain lain

**`MS` / `TMS`** (Memenuhi Syarat / Tidak Memenuhi Syarat) adalah istilah **hasil laboratorium**
milik domain pengujian. **Tidak ada** di domain ini. Bila pengguna menulis "hasil uji TMS",
pertanyaannya salah rute — lihat `95-batas-domain.md`.

Bila pengguna menulis "TMK" untuk hasil uji, kemungkinan yang dimaksud memang kepatuhan sarana;
klarifikasi bila konteksnya bercampur.

## Hubungan dengan temuan produk

Vonis `TMK` **tidak berarti selalu ada temuan produk**, dan adanya temuan tidak selalu berujung
`TMK`. Keduanya kolom/tabel yang berbeda dan tidak boleh dipakai bergantian. Bila pertanyaannya
tentang produk yang ditemukan, itu `40-temuan-produk.md`; bila tentang vonis sarana, kolom ini.

## Rute

- Menyebut temuan produk: buka `40-temuan-produk.md`.
- Menyebut grade / kriteria / tingkat kekritisan: buka `60-mutu-dan-tindak-lanjut.md`.
- Menyebut status alur (draft/verifikasi/selesai): buka `31-status-dan-alur.md`.

---

<!-- MANIFES
tabel: -
kolom: kesimpulan
nilai: NULL, TDP, TMBB, TMK, TTP
-->
