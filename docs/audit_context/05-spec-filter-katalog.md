# 05 — Spesifikasi Halaman `05-filter-katalog.md`

> Halaman ini menjawab satu pola kegagalan yang paling mahal: **agent menebak kolom dari nama label panel**. Label panel adalah bahasa user; kolom adalah bahasa database. Keduanya tidak selalu sepadan.
>
> Semua status di bawah = hasil verifikasi live 22 Sep 2026 (lihat [07](07-verifikasi-live.md)).

---

## 1. Dimensi panel → kolom → status

| Label panel | Padanan di `staging` | Catatan teknis | Status |
|---|---|---|---|
| Jenis sarana | `fact_pemeriksaan.jenis_id` → kamus `JENIS_SARANA` | golongan lewat `parent_name` | ✅ ada |
| Jenis komoditi | `klasifikasi_id` → `JENIS_KLASIFIKASI` | wajib sebut `type` | ✅ ada |
| Tanggal | `tgl_start` · `tgl_end` · `created_at` · `updated_at` | 4 label → 4 kolom, makna berbeda | ✅ ada |
| Kesimpulan | `kesimpulan_balai_id` / `kesimpulan_pusat_id` → `dim_pemeriksaan_kesimpulan` | review Pusat parsial | ✅ ada |
| Tingkat pemenuhan CPOB | kelompok kode pada `kesimpulan_balai_id` (kelompok CPOB) | bukan kolom sendiri | ⚠️ ada sebagai kode |
| Grade | `fact_pemeriksaan.grade` | hanya sebagian jenis sarana | ⚠️ subset |
| Tujuan pemeriksaan | `tujuan_id` → kamus | — | ✅ ada |
| Petugas / inspektur | `bridge_pemeriksaan_petugas` → `dim_user` | `COUNT(DISTINCT)` untuk kasus | ✅ ada |
| Unit / Balai | `balai_id` → `dim_balai` | pelaksana, bukan lokasi objek | ✅ ada |
| Regional | `dim_balai.regional_name` | jangan kolom `regional` | ⚠️ ada dengan catatan |
| Provinsi / Kabupaten sarana | `dim_sarana.provinsi_id` / `kabupaten_id` | lokasi objek | ✅ ada |
| Legal | `dim_sarana.legal_id` | **merujuk 2 kamus** | ⚠️ ada dengan catatan |
| Klasifikasi sarana | `fact_pemeriksaan.klasifikasi_sarana_kode` → `CLASS_SARANA` | khusus jenis sarana Pangan | ⚠️ subset |
| Status label | `dim_status_code.status_label` | **terisi 0 dari 35 baris** | ❌ tidak dapat dipakai sebagai label |
| Target / capaian | `dim_balai.target_sampling` · `target_sarana` | terisi 108/108 balai | ✅ ada |
| **Klasifikasi distribusi** | — | tidak ada kolom; `distribusi_provinsi_kode` milik profil Pangan MD | ❌ **honest gap** |
| Aspek / skor | `bridge_pemeriksaan_skor_operasional.area_key` → `dim_pemeriksaan_aspek` | hanya varian pelayanan | ⚠️ subset |
| Klausul / severity | `bridge_pemeriksaan_checklist.path` + `nilai_aspek` | parsial | ⚠️ subset |
| Observasi / GMP | `bridge_pemeriksaan_temuan_observasi` | `kriteria` belum terkonfirmasi | ⚠️ sebagian |
| Vaksin | `bridge_pemeriksaan_vaksin.section_key` | belum punya kamus label aspek | ⚠️ sebagian |

---

## 2. Tiga honest gap yang wajib dinyatakan di halaman

### Gap 1 — Klasifikasi distribusi

Tidak ada kolomnya di `staging`. Perangkapnya: `distribusi_provinsi_kode` (jsonb, di `fact_pemeriksaan_profil_pangan_md`) **bukan** klasifikasi distribusi sarana — itu daftar provinsi tujuan distribusi pabrik Pangan MD. Menyambung ke sana menghasilkan angka yang rapi tetapi menjawab hal lain.

Jawaban yang benar: sebutkan konsepnya tidak direkam di database ini, sebutkan di mana kemungkinan berada (data master sarana / sistem lain), lalu tawarkan hal terdekat yang benar-benar bisa dijawab.

### Gap 2 — Status label

Kolomnya ada tetapi isinya kosong seluruhnya (0/35). Konsekuensi:
- pertanyaan "berapa yang belum punya status label" jawabannya **seluruh populasi** — bukan temuan data;
- pertanyaan "tampilkan status label X" tidak bisa dijawab dari label; yang tersedia hanya kode status (`status_code`) pada `dim_status_code` dan nilai `status` per kasus.

### Gap 3 — Legal

`dim_sarana.legal_id` merujuk **dua kamus** (`BENTUK_PERUSAHAAN` + `JENIS_SARANA`) dengan distribusi tidak merata. Filter satu `type` akan menghilangkan sebagian besar baris tanpa peringatan. Aturan: jangan filter `type`; tampilkan `type` sebagai kolom hasil.

---

## 3. Perangkap panel-vs-kanon

| Label panel | Bedanya dengan bacaan kanonik | Default |
|---|---|---|
| Tingkat pemenuhan CPOB | panel menampilkan sebagai dimensi sendiri; di data ia berbagi kolom dengan kesimpulan umum | bacaan kanon: kelompok kode pada kolom kesimpulan |
| Status label | panel menampilkan label; data hanya punya kode | bacaan kanon: kode status |
| Klasifikasi sarana | panel umum; data hanya untuk Pangan | bacaan kanon: sebutkan cakupannya |

Aturan umum: **panel tidak menang atas kanon**; bila berbeda, pakai kanon dan sebutkan bedanya.

---

## 4. Cara mencari bila label tidak ada di tabel

```sql
-- 1. cari kolomnya lebih dulu
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND (column_name ILIKE '%<kata>%' OR column_name ILIKE '%<sinonim>%')
ORDER BY 1, 2;

-- 2. bila kolom ada, cek keterisian sebelum dipakai sebagai penyaring
SELECT count(*) AS total, count(<kolom>) AS terisi FROM public.<tabel>;

-- 3. bila kolom tidak ada -> honest gap, jangan pakai kolom "mirip"
```

Metode inilah yang dipakai untuk membuktikan Gap 1–3 di atas, dan wajib dicantumkan di halaman sebagai **cara memastikan** — supaya agent dapat mengulang pembuktiannya sendiri, bukan menerima kesimpulan jadi.

---

## 5. Rute

- dimensi tentang sarana → `10-sarana-dan-fasilitas.md`
- dimensi tentang komoditi → `20-komoditi.md`
- kesimpulan & CPOB → `30-kesimpulan.md`
- status → `31-status-dan-alur.md`
- aspek/skor → `35-kepatuhan-aspek.md`
- klausul/severity → `37-klausul-dan-severity.md`
- target → `85-target-capaian.md`
- label tanpa kolom → `95-batas-domain.md` (protokol honest gap)

---

## 6. Kriteria lulus halaman ini

- [ ] memuat seluruh dimensi panel yang terverifikasi (tabel §1);
- [ ] memuat tiga honest gap dengan **cara memastikannya**, bukan hanya kesimpulan;
- [ ] memuat peringatan `distribusi_provinsi_kode` bukan klasifikasi distribusi;
- [ ] memuat aturan "panel tidak menang atas kanon";
- [ ] tanpa angka hasil query;
- [ ] ≤200 baris.
