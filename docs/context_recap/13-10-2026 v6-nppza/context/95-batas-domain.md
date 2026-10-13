TTE · tanda tangan elektronik · lampiran · berkas · dokumen · kompetensi · sertifikasi petugas · riwayat perubahan · antibiotik · domain lain · iklan · hasil uji · label · zat adiktif · permit impor · re-ekspor

# Batas domain — apa yang tidak ada di sini

## Apa yang halaman ini putuskan

Bagaimana menjawab pertanyaan yang **tidak bisa dijawab** dari database ini — tanpa memakai kolom
terdekat yang namanya mirip.

## Domain lain (tidak tersambung)

| Istilah dalam pertanyaan | Domain sebenarnya | Kenapa mudah tertukar |
|---|---|---|
| iklan · media · promosi | pengawasan | — |
| label · penandaan produk | penandaan | domain ini juga punya "kesimpulan" |
| hasil uji · laboratorium · sampel · parameter uji · LHU · MS/TMS | pengujian | domain ini memakai MK/TMK, bukan MS/TMS |
| NIE · izin edar · registrasi produk · permohonan | registrasi produk | domain lain punya kode permohonan; di sini tidak ada |

## Konsep yang tidak direkam di database ini

| Diminta | Status | Alternatif yang benar-benar bisa dijawab |
|---|---|---|
| kapan surat di-**TTE** | tidak ada kolomnya | status kasus + tanggal approval |
| **isi** lampiran/berkas | hanya ID dokumen, tanpa isi | keberadaan/ketiadaan ID |
| **kompetensi / sertifikasi** inspektur | tidak ada | eksposur penugasan per jenis sarana |
| **riwayat perubahan** isi kasus | edit menimpa, tidak ada versioning | `updated_at` (kapan terakhir berubah) |
| siapa yang **menyetujui** | semantik pelaku tidak dapat dipastikan | waktu & volume tahap, bukan keputusan orang |
| **detail checklist Kosmetik CPKB** | tidak ada bridge | header + narasi kasus |
| **volume/zat aktif antibiotik** | ada di isian form, belum jadi tabel terstruktur | kepatuhan aspek penyerahan/pencatatan |
| **klasifikasi distribusi** | tidak ada kolomnya | nyatakan batas |
| **zat adiktif** (kategori terstruktur) | tidak ada kolom/kamusnya | terdekat: teks narasi dengan pencarian prefiks (`60`) atau kategori temuan Diversi/Penyalahgunaan (`40`) — sebut bedanya |
| **permit/awal impor obat** | tidak ada sumbernya di database ini (ada di sistem registrasi terpisah; yang tersambung hanya cakupan pangan) | nyatakan NOT COVERED — jangan diproxykan |
| **re-ekspor sebagai metrik tindak lanjut** | label ada di kamus CAPA/TL tapi praktis tidak dipakai | nyatakan; tawarkan tindak lanjut yang benar-benar terisi (`40`) |
| **atribut importir/eksportir sarana** | tidak ada kolom klasifikasinya | terdekat: teks nama sarana (proxy, `10`) — wajib disclaimer |

## Protokol menjawab NOT COVERED — tepat tiga kalimat

1. sebut **apa yang ditanyakan** dan bahwa konsepnya tidak direkam di database ini;
2. sebut **di mana kemungkinan besar** konsep itu berada (domain/sistem lain), bila diketahui;
3. tawarkan **hal terdekat yang benar-benar bisa dijawab**, dan sebutkan bedanya.

Yang **tidak boleh**: menjawab dengan kolom yang namanya mirip lalu berharap pembaca memahami bedanya.
Query semacam itu jalan, hasilnya rapi, dan pembaca tidak punya cara tahu bahwa yang ditampilkan bukan
yang ditanyakan.

## Matriks operasi

| Situasi | Menyaring | Menjawab |
|---|---|---|
| istilah domain lain muncul | **jangan** memetakan ke kolom terdekat | protokol 3 kalimat |
| "belum ada datanya" | cek dulu apakah kolomnya ada | kalau tidak ada → P5, bukan "nol" |
| permintaan granularitas yang tidak ada | jangan membagi rata | nyatakan batas grain |

## Cara memastikan sebuah konsep benar-benar tidak ada

```sql
-- cari kolomnya di seluruh schema sebelum menyimpulkan
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND (column_name ILIKE '%<kata>%' OR column_name ILIKE '%<sinonim>%')
ORDER BY 1, 2;

-- bila kosong: konsepnya tidak ada di sini -> protokol 3 kalimat
```

## Jebakan

| Gejala | Penyebab | Cara memastikan |
|---|---|---|
| jawaban rapi untuk konsep yang tidak ada | memakai kolom terdekat yang namanya mirip | jalankan pencarian kolom di atas; bila kosong → protokol 3 kalimat |
| "belum ada datanya" padahal tidak ada kolomnya | kekosongan disamakan dengan "nol" | bedakan: kolom tidak ada = P5; kolom kosong = sebutkan cakupannya |
| granularitas dipaksa | menuntut pecahan yang tidak didukung data | nyatakan batas grain, jangan membagi rata |
| kesimpulan tentang orang | menafsirkan kolom pelaku sebagai keputusan | jawab lewat waktu & volume tahap |

## Rute

- Label panel yang tidak punya kolom → **lihat** `05-filter-katalog.md`
- Kekosongan & sentinel → **lihat** `90-kualitas-data.md`
- Ambiguitas istilah user → **lihat** `97-glossary-istilah-user.md`

## Manifes

| Tabel | Kolom | Literal |
|---|---|---|
| `information_schema.columns` | `table_name`, `column_name` | — |
| `fact_pemeriksaan` | `updated_at`, `status_id` | — |
| `fact_pemeriksaan_approval` | `created_at`, `act_steps` | — |
