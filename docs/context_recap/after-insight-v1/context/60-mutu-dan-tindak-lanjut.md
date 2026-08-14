Grade, kriteria temuan, pemenuhan CPOB, dan tindak lanjut — empat konsep berbeda.

## Peta cepat

| Konsep pengguna | Kolom / tabel | Cakupan |
|---|---|---|
| grade / grading | `mv_pemeriksaan.grade` | **hanya sebagian jenis sarana** |
| temuan kritis / mayor / minor (cacah) | `tx_critical_issue`, `tx_major_issue`, `tx_minor_issue` | sebagian populasi |
| kriteria / jenis temuan (uraian) | `mv_kriteria_pemeriksaan` | **populasi sangat sempit** |
| tingkat pemenuhan CPOB | `tingkat_pemenuhan_cpob` | **populasi sangat sempit** |
| tindak lanjut sarana | `tl_saran_names` (array) | populasi luas |
| tindak lanjut hasil inspeksi | `hp_followup_name` | **populasi sangat sempit** |

"Populasi sempit" berarti kolomnya hanya terisi untuk irisan kecil pemeriksaan. Menjawab
dengannya tanpa menyebut cakupan membuat pembaca mengira seluruh pemeriksaan tercakup.

## `grade` — dikunci jenis sarana

Kolom `grade` **hanya terisi untuk satu jenis sarana** (keluarga pangan), dan nol untuk seluruh
jenis sarana lain. Karena itu:

> Pertanyaan "ketepatan grading di UPT X" adalah **pertanyaan khusus sarana pangan**, bukan
> tentang seluruh pemeriksaan UPT itu. Sebutkan batas ini.

Nilai `grade` berupa huruf tunggal, ditambah satu nilai yang berarti tidak berlaku.

⚠️ **"Nilai sarana" bukan `grade`.** Aturan penilaian unit menyebut "nilai sarana A/B/C/D" sebagai
masukan dan grade sebagai keluarannya. **Kolom nilai sarana tidak ada di database ini.**
Pertanyaan ketepatan grading yang menuntut perbandingan grade terhadap nilai sarana →
**P5 NOT COVERED**. Yang bisa dijawab hanyalah hubungan antara `grade` dan `kesimpulan`, dan itu
**bukan hal yang sama** — sebutkan perbedaannya.

## `tx_*_issue` — cacah, bukan jenis

Ketiga kolom berisi **berapa banyak** isu kritis/mayor/minor ditemukan, bukan **isu apa**.

> Pertanyaan *"tiga temuan kritis paling sering"* menanyakan **jenis**. Menjawabnya dengan
> `GROUP BY tx_critical_issue` menghasilkan "berapa pemeriksaan yang punya N isu kritis" — bukan
> jawaban pertanyaannya.

Jenis dan uraian temuan ada di `mv_kriteria_pemeriksaan` (`tx_criteria` untuk tingkat kekritisan,
`tx_criteria_desc` untuk uraiannya). Tabel itu mencakup **populasi yang sangat sempit** —
terkonsentrasi pada klasifikasi dan tujuan tertentu. Sebutkan cakupannya, atau jawab NOT COVERED
bila pertanyaannya menuntut cakupan nasional.

## Tingkat pemenuhan CPOB

`tingkat_pemenuhan_cpob` berisi tingkat kepatuhan cara pembuatan obat yang baik, dengan beberapa
tingkat bernama. Terisi hanya untuk pemeriksaan sarana produksi obat — **populasinya sangat
sempit** relatif seluruh pemeriksaan.

Pertanyaan "riwayat kepatuhan CPOB PT X" dijawab dari kolom ini plus `nama_sarana` (jalur **P3**:
`ILIKE` untuk menemukan, lalu nilai persis). Sebutkan bahwa datanya hanya ada untuk sarana yang
memang diperiksa dengan skema CPOB.

## Dua kolom tindak lanjut yang berbeda

| Kolom | Bentuk | Cakupan |
|---|---|---|
| `tl_saran_names` | **array** teks | luas — mayoritas pemeriksaan |
| `hp_followup_name` | teks tunggal | sangat sempit |

Isinya berbeda jenis: yang pertama berisi saran tindak lanjut untuk sarana (pembinaan, peringatan,
peringatan keras, dan seterusnya); yang kedua berisi tindak lanjut hasil inspeksi bergaya
sertifikasi (rekomendasi pencabutan, penghentian sementara, permintaan CAPA).

> Pertanyaan umum *"tindak lanjut apa yang diberikan"* dijawab dari **`tl_saran_names`**.
> `hp_followup_name` hanya untuk konteks sertifikasi/CPOB, dan cakupannya harus disebut.

Karena `tl_saran_names` bertipe array, mengelompokkannya perlu `unnest`. Satu pemeriksaan bisa
punya lebih dari satu saran — cacah per saran akan melebihi cacah pemeriksaan; itu benar dan
harus dinyatakan.

## Rute

- Menyebut vonis MK/TMK → **seberang** `30-kesimpulan.md`.
- Menyebut temuan produk → **seberang** `40-temuan-produk.md`.
- Mempertanyakan keterisian kolom → **seberang** `90-kualitas-data.md`.
