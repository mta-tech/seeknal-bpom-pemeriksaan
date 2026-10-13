# 05 — Kamus Bahasa User dan Semantik

> Tujuan semantic layer: mengubah **kata user → definisi bisnis → grain → data → rule → bentuk jawaban**, bukan sekadar mencocokkan kata dengan nama kolom.

---

## 1. Kamus inti

| Istilah user | Arti bisnis | Grain | Data tujuan | Rule/filter | Ambiguitas |
|---|---|---|---|---|---|
| Wasdis | tim pemeriksa/pengawasan distribusi | persona/tim | petugas, Balai, kasus | konteks organisasi | bukan kolom database |
| pemeriksaan | satu kasus/kunjungan | kasus | `fact_pemeriksaan.id` | `COUNT(DISTINCT id)` | jangan dihitung dari bridge |
| sarana | objek usaha/fasilitas | sarana unik | `dim_sarana` | join lewat `sarana_id` | satu sarana bisa diperiksa berulang |
| jenis sarana | kategori objek (Apotek, PBF, dll.) | kode/kasus | `JENIS_SARANA` | filter `type` | berbeda dari komoditi |
| komoditi | kelompok produk/domain | kode/kasus | `JENIS_KLASIFIKASI` | filter `type` | istilah historis bisa berbeda |
| aspek | bagian pemeriksaan | item/aspek | dim aspek atau path/narasi | tergantung varian | tidak semua varian punya aspek resmi |
| observasi | catatan/kode kondisi lapangan | item/narasi | checklist/observasi/narasi | route varian | bisa bukan ketidaksesuaian |
| temuan | kondisi bermasalah | beragam | skor/checklist/observasi/produk/narasi | wajib klarifikasi | istilah paling ambigu |
| ketidaksesuaian | kondisi tidak memenuhi standar | item/kasus | opsi/score/nilai_aspek | rule per field | tidak ada definisi global |
| Minor/Major/Kritikal | tingkat keparahan | kasus atau item | counter/level/nilai_aspek | bedakan grain | coverage tidak universal |
| MK/TMK | kesimpulan kasus | kasus | dim kesimpulan | join FK | bukan severity |
| grade A/B/C | klasifikasi kualitas produksi | kasus | `grade` | subset produksi | bukan MK/TMK |
| rekomendasi | saran tindak lanjut | kasus/narasi | `tl_saran`, narasi rekomendasi | multi-kamus/teks | berbeda dari tindakan produk |
| tindak lanjut | respons setelah temuan | kasus/produk/event | TL, CAPA, tindakan produk, approval | tentukan jenis | istilah luas |
| CAPA | corrective/preventive action | kasus | `tl_capa` | teks bebas | tidak terkamus |
| final Balai | hasil awal yang disahkan UPT | kasus | kesimpulan/narasi Balai + approval | konteks workflow | versi historis tidak lengkap |
| evaluasi Pusat | penilaian Pusat | kasus | kesimpulan/narasi/TL Pusat | review parsial | NULL bukan otomatis belum diproses |
| UPT/Balai | pelaksana pemeriksaan | organisasi | `dim_balai` | join `balai_id` | bukan lokasi objek |
| regional | kelompok operasional Balai | regional | `regional_name` | jangan pakai kode `regional` | bukan provinsi sarana |
| wilayah kerja | cakupan administratif UPT | wilayah | belum satu kolom langsung | perlu definisi | bisa berbeda dari lokasi sarana |
| lokasi sarana | lokasi fisik objek | provinsi/kabupaten | `dim_sarana` | join wilayah | bukan Balai pelaksana |
| pendistribusian | aspek penyaluran | item aspek | label resmi `Penyaluran` | semantic synonym | nama form ≠ nama kamus |
| selesai | kasus selesai | status | FINISHED/FINISHED_PUSAT | tentukan jalur | dua kode |
| temuan produk | produk bermasalah | kasus/baris/kuantitas | bridge temuan | bedakan grain | bukan checklist |
| antibiotik | isu tematik penyerahan/pencatatan | item/kasus/zat aktif | skor + data belum terstruktur | route tematik | detail volume belum siap |
| free text/narasi | catatan petugas/verifikator | potongan teks | tabel narasi/catatan | NLP + evidence | tidak boleh langsung dihitung |
| tren | perubahan sepanjang waktu | metrik × waktu | tergantung intent | wajib definisi metrik | bukan satu konsep |
| produktivitas inspektur | volume penugasan | kasus/penugasan | bridge petugas | `COUNT DISTINCT` kasus | bukan kompetensi/performa |
| NPP / NPPZA / obat berkontrol | komoditi obat berkontrol | kasus atau kasus distribusi | `JENIS_KLASIFIKASI` (klasifikasi) vs bridge `komoditi_pbf`/`fokus_pbf` (pengelolaan) | pilih grain dari kalimat; join `master_data_id` + `type` | bisa termasuk OOT; dua grain berbeda |
| PKM | Puskesmas (jenis sarana) | kasus/sarana | `JENIS_SARANA` | filter jenis | vs "Pengawasan Keamanan Mutu" — bukan modul |
| keamanan mutu | kategori temuan TMS KMG / profil mutu pabrik pangan / bukan modul | temuan atau profil | kategori `220001`/`220131–133` (`40`) · profil pangan MD (`50`) | pilih dari kalimat | bisa berarti tiga hal |
| obat keras | kategori temuan produk | baris/kasus | `KATEGORI_TEMUAN_PRODUK` (kode raw) | kamus via `master_data_id` | bukan golongan produk |
| zat adiktif | tidak direkam terstruktur | — | narasi (prefiks) | NOT COVERED | hanya bukti teks |
| ekspor impor | bukan modul; negara asal & proxy nama sarana | temuan/sarana | `negara` bridge temuan · `nama_sarana` | tiga bucket; proxy+disclaimer | permit/awal impor tidak ada |

---

## 2. Istilah yang wajib memicu klarifikasi

### “Temuan”

Tanyakan:

> Temuan yang dimaksud adalah ketidaksesuaian checklist, observasi GMP, kategori produk bermasalah, atau alasan kesimpulan TMK?

### “Wilayah”

Tanyakan:

> Apakah wilayah yang dimaksud adalah Balai/UPT pelaksana, regional Balai, atau lokasi fisik sarana?

### “Jumlah”

Tanyakan/nyatakan:

> Apakah yang dihitung jumlah pemeriksaan, sarana unik, item checklist, produk bermasalah, kuantitas produk, atau penugasan petugas?

### “Tren”

Tanyakan:

> Tren berdasarkan jumlah kasus, jumlah item tidak sesuai, persentase kepatuhan, atau proporsi TMK?

### “Kritis”

Tanyakan:

> Apakah yang dimaksud jumlah kasus dengan level kritis atau jumlah klausul ber-severity Kritis/Kritikal?

### “Tindak lanjut”

Tanyakan:

> Apakah tindak lanjut yang dimaksud adalah saran Balai/Pusat, CAPA, tindakan terhadap produk, atau status approval?

---

## 3. Mapping bahasa natural ke intent

| Pola bahasa user | Intent |
|---|---|
| “berapa pemeriksaan…” | monitoring volume kasus |
| “sarana apa saja…” | list/detail sarana |
| “aspek apa paling bermasalah…” | kepatuhan/ketidaksesuaian |
| “Minor/Major/Kritis…” | risk/severity |
| “MK/TMK…” | kesimpulan kasus |
| “apa tindak lanjutnya…” | response/CAPA/rekomendasi |
| “Balai vs Pusat…” | decision consistency |
| “di wilayah/regional…” | spatial/organizational breakdown |
| “siapa inspektur…” | assignment/exposure |
| “mengapa/apa alasannya…” | narrative evidence/NLP |
| “antibiotik tanpa resep…” | thematic antibiotic analysis |
| “buat laporan/ringkas…” | reporting/communication |

---

## 4. Bahasa user yang terlihat sama tetapi berbeda data

### “Penyimpanan”

- pelayanan: `area_key` → skor kepatuhan;
- produksi: `path` checklist → Ya/Tidak/severity;
- narasi: section penyimpanan → teks bebas.

Default aman: tampilkan tiga sumber terpisah, tidak dijumlahkan.

### “Temuan kritis”

- per kasus: `kritis_count`/`level_kesimpulan`;
- per klausul: `nilai_aspek` Kritis/Kritikal;
- observasi: `kriteria` angka 1–4 (belum terkonfirmasi).

### “Rekomendasi”

- saran TL berkode;
- CAPA teks bebas;
- narasi rekomendasi;
- tindakan produk (pemusnahan/penarikan/dll.);
- keputusan approval.

### “Regional Bandung/Jakarta”

- bisa Balai pelaksana;
- bisa `regional_name`;
- bisa provinsi/kabupaten sarana;
- bisa wilayah kerja administratif.

---

## 5. Kontrak semantic entry

Setiap istilah baru ditambahkan dengan format:

```yaml
term: "..."
synonyms: ["..."]
business_definition: "..."
intent: "..."
entity: "..."
grain: "..."
data_route: ["fact...", "bridge...", "dim..."]
required_filters: ["..."]
ambiguities: ["..."]
clarification: "..."
answer_shape: "..."
coverage_note: "..."
```

Tujuannya bukan membuat YAML sekarang, tetapi memastikan setiap istilah punya kontrak yang lengkap sebelum masuk ke context/skill.

---

## 6. Aturan bahasa jawaban

Jawaban harus:

- menyebut entitas yang dihitung;
- menyebut scope periode/wilayah/jenis sarana;
- menyebut coverage bila parsial;
- membedakan fakta data vs interpretasi;
- memakai “berasosiasi/sering muncul bersama” untuk korelasi;
- menyertakan evidence untuk insight narasi.

Hindari:

- “semua sarana” bila data hanya subset;
- “menyebabkan” tanpa bukti kausal;
- “regional” tanpa menjelaskan maknanya;
- “jumlah temuan” tanpa grain;
- “kompetensi inspektur” bila hanya menghitung volume penugasan.

---

## 7. Semantic layer sebagai jembatan

```text
Bahasa user
→ istilah bisnis
→ intent
→ entity/grain
→ varian form
→ metric contract
→ data route
→ query
→ validated answer
```

LLM tidak cukup hanya mengetahui nama tabel. Ia harus mengetahui makna bisnis dan batas penggunaannya.
