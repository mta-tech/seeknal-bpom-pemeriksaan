# CHANGELOG — `after-insight-v2` → `after-insight-v3` (domain pemeriksaan)

**Tanggal:** 19 Agustus 2026 · **Domain:** PEMERIKSAAN SARANA

**Dasar perubahan:** 13 kegagalan nyata pada gelombang uji 18 Agustus 2026. Sebelum dipakai,
seluruh testcase repo ini diverifikasi ulang ke database live dan terbukti terjawab — sehingga
testcase diperlakukan sebagai acuan, dan context yang menyesuaikan.

---

## Khas domain ini — tidak ada jebakan satuan hitung

Kunci tabel fakta di domain ini unik penuh, sehingga cacah baris dan cacah kunci selalu sama.
Persoalan satuan yang menjadi akar terbesar di domain pengawasan **tidak mungkin muncul di sini**,
dan karena itu tidak ada aturan satuan yang perlu diubah.

Yang tetap perlu kehati-hatian di sini adalah beberapa kolom yang namanya mirip dan sama-sama
memuat kata "sarana" — pemilihan kolom dilakukan dari makna pertanyaan, bukan dari kemiripan nama.
Aturan itu sudah ada sejak versi sebelumnya dan tidak diubah.
---

## Berlaku di keempat repo — 1. Mengikat nilai berkode (`00-menghitung.md` §1b, bagian baru)

Draf pertama v3 menulis aturan ini khusus untuk satu kolom vonis. Itu terlalu sempit. Pemeriksaan
ke database menunjukkan pola yang sama hidup di banyak kolom berkode **di semua repo** — termasuk
kolom komoditi, tujuan, dan klasifikasi, bukan hanya kolom vonis. Justru kata yang paling sering
ditanya adalah yang paling berisiko, karena ia sekaligus menjadi awalan beberapa nilai turunan.

Yang ditulis sekarang adalah **prosedur berpikir**, bukan daftar jawaban:

1. **Lihat dulu daftar nilainya** lewat satu probe — jangan menebak.
2. **Baca daftar itu dengan dua pertanyaan:** apakah nilai saya juga awalan nilai lain, dan apakah
   ada dua baris yang menjadi sama setelah spasi serta kapitalisasi disamakan. Keduanya ditangani
   ke arah berlawanan, dan itulah yang paling mudah tertukar.
3. **Kalau kolomnya bertingkat, tentukan bacaan dari bentuk pertanyaannya** — menyebut nama kolom
   beserta nilainya berarti nilai itu apa adanya; menggambarkan keadaan atau putusan berarti nilai
   dasar beserta turunannya. Bila petunjuknya lemah, ambil bacaan yang paling sempit.
4. **Sebutkan nilai mana saja yang ikut dihitung**, apa pun pilihannya. Bila pertanyaannya memang
   bisa dibaca dua arah, berikan keduanya — angka utama dan satu kalimat pembanding.

## Berlaku di keempat repo — 2. Nama entitas ditulis apa adanya (`SEEKNAL_ASK.md` Gate 5)

Nama balai, sarana, perusahaan, dan produk disalin persis dari hasil query; singkatan boleh
menyusul, tidak menggantikan. Untuk pertanyaan peringkat, nama baris teratas wajib muncul utuh —
itu isi jawabannya, bukan hiasan.

Pada gelombang uji sebelumnya ada kelompok kegagalan yang seluruh angkanya benar dan urutannya
benar, dan gagal semata karena nama diringkas. Aturan ini menutup kelompok itu tanpa mengubah satu
pun SQL.

## Berlaku di keempat repo — 3. Gate 1 dihemat (`SEEKNAL_ASK.md`)

Klarifikasi hanya untuk hal yang benar-benar tidak punya bacaan default. Bila context sudah
menetapkan default, pakai default itu, jawab, lalu sebutkan asumsinya dalam satu kalimat.
Disertai tabel hal-hal yang tidak boleh ditanyakan: cakupan wilayah, periode, tingkat nilai
berkode, bentuk keluaran, dan satuan hitung.

Sebelumnya sebagian kegagalan terjadi justru pada giliran **setelah** klarifikasi — pertanyaan yang
sebenarnya bisa langsung dijawab berbelok lebih dulu, lalu opsi yang terpilih tidak sejalan dengan
maksud penanya.

---

## Tidak ada nilai eksak yang ditanam di context

Draf pertama v3 sempat memuat tabel angka hasil query. Semuanya dihapus. Nilai eksak berubah
setiap kali data disinkron, sehingga context yang menghafalnya akan menyesatkan dalam hitungan
hari — dan lebih buruk lagi, ia mengajari agent menjawab dari ingatan alih-alih dari query.

Yang ditinggalkan sebagai gantinya adalah **cara memperolehnya**: query probe yang bisa dijalankan
sendiri, ditambah hubungan yang memang tidak berubah (misalnya cacah baris tidak mungkin lebih
kecil dari cacah kunci uniknya).

## Pemeriksaan regresi

Seluruh testcase yang **lulus** pada gelombang 18 Agustus diperiksa satu per satu terhadap aturan
yang diubah, lalu SQL-nya dijalankan ulang ke database:

| Kelompok | Hasil di bawah v3 |
|---|---|
| Lulus dengan satuan cacah event padahal acuannya cacah baris | tetap lulus, dan mayoritas kini cocok **persis** — sebelumnya hanya lolos karena ambang toleransi |
| Lulus dengan pola awalan padahal acuannya nilai dasar | tetap lulus, kini cocok persis |
| Acuannya memang menuntut nilai dasar **beserta turunannya** | tetap lulus — tercakup bacaan "keadaan/putusan" di Langkah 3 |
| Lulus setelah klarifikasi otomatis | opsi yang dulu terpilih **sama dengan** default v3, sehingga hasilnya tidak berubah |
| Testcase yang mewajibkan agent bertanya | tidak ada satu pun di seluruh suite |

**Tidak ditemukan regresi.**

## Yang sengaja TIDAK diubah

- Aturan sentinel, kualitas data, dan batas domain — tidak ada kegagalan yang berakar di sana.
- Anggaran query Gate 4 — tidak ada bukti anggarannya terlalu ketat.
- Testcase yang assert-nya bercacat (lihat `docs/contextaudit/.../06-crosscheck-semua-testcase.md`)
  tidak dipakai menurunkan aturan apa pun. Memperbaiki context agar lulus tes yang salah tulis
  akan merusak akurasi yang sebenarnya.

## Cara memverifikasi

```bash
uv run python scripts/test_variant_compare.py \
    --variants after-insight-v2,after-insight-v3 \
    --test-path docs/testcase --workers 1
```

Jalankan **kedua** varian berdampingan — itu satu-satunya cara membaca selisihnya. Gelombang
18 Agustus hanya menjalankan satu varian, sehingga perbandingan antar versi belum pernah terukur.
Pastikan `.seeknal/` ada di setiap varian yang diuji.
