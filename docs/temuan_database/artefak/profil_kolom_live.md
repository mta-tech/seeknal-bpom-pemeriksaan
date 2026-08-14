# Profil Kolom Live — database `pemeriksaan` (2026-08-13)

Per kolom: jumlah NULL (SQL NULL, bukan sentinel string), persentase, dan cacah nilai distinct.
Diikuti katalog nilai untuk kolom berkardinalitas rendah.

---


### coverage_balai  —  668 rows
  - id_balai                             bigint       null=        0 (  0.0%)  distinct=88
  - nama_balai                           text         null=        0 (  0.0%)  distinct=88
  - id_kabupaten                         integer      null=        0 (  0.0%)  distinct=514
  - kabupaten_kota                       text         null=        0 (  0.0%)  distinct=514
  - sync                                 timestamp without time zone null=        0 (  0.0%)  distinct=1

### mv_kriteria_pemeriksaan  —  5,892 rows
  - pemeriksaan_id                       bigint       null=        0 (  0.0%)  distinct=902
  - nama_sarana                          text         null=        0 (  0.0%)  distinct=273
  - klasifikasi                          text         null=        0 (  0.0%)  distinct=4
  - tujuan                               text         null=        0 (  0.0%)  distinct=8
  - kabupaten                            text         null=        0 (  0.0%)  distinct=57
  - nama_balai                           text         null=        0 (  0.0%)  distinct=18
  - tgl_start                            date         null=        0 (  0.0%)  distinct=565
  - tgl_end                              date         null=        0 (  0.0%)  distinct=582
  - criteria_index                       bigint       null=        0 (  0.0%)  distinct=48
  - tx_criteria                          text         null=      294 (  5.0%)  distinct=4
  - tx_criteria_desc                     text         null=      317 (  5.4%)  distinct=5274
  - sync                                 timestamp without time zone null=        0 (  0.0%)  distinct=1
    VALUES[klasifikasi] (4): Obat=5,420 | Produk Biologi dan Sarana Khusus=380 | Bahan Baku Obat=80 | Suplemen Kesehatan=12
    VALUES[tujuan] (8): Pemeriksaan Rutin=5,095 | Sertifikasi CPOB=369 | Pemusnahan=190 | Komprehensif=107 | Resertifikasi=65 | Asistensi=43 | Verifikasi CAPA=19 | Observasi Inspeksi otoritas Lain=4
    VALUES[kabupaten] (57): Kota Jakarta Timur=775 | Kabupaten Bekasi=478 | Kota Bandung=429 | Kota Semarang=402 | Kabupaten Pasuruan=354 | Kabupaten Sidoarjo=259 | Kabupaten Bandung Barat=249 | Kota Tangerang=240 | Kabupaten Bogor=212 | Kabupaten Serang=210 | Kabupaten Tangerang=184 | Kota Palembang=177 | Kabupaten Gresik=173 | Kabupaten Karanganyar=156 | Kota Jakarta Selatan=129 | Kota Surabaya=112 | Kabupaten Bandung=105 | Kota Cimahi=91 | Kabupaten Sukabumi=79 | Kabupaten Deli Serdang=68 | Kota Jakarta Utara=68 | Kabupaten Malang=61 | Kota Medan=58 | Kabupaten Cianjur=57 | Kota Bekasi=57 | Kabupaten Sumedang=56 | Kabupaten Sleman=52 | Kota Depok=47 | Kota Kediri=47 | Kabupaten Semarang=46 | Kabupaten Sukoharjo=41 | Kabupaten Brebes=41 | Kabupaten Padang Pariaman=39 | Kota Jakarta Barat=38 | Kabupaten Demak=38 | Kabupaten Karawang=36 | Kota Jakarta Pusat=34 | Kota Sukabumi=31 | Kabupaten Mojokerto=29 | Kabupaten Majalengka=27 | Kabupaten Klaten=26 | Kota Malang=16 | Kabupaten Jombang=14 | Kota Tangerang Selatan=13 | Kabupaten Subang=10 | Kabupaten Banyumas=8 | Kota Surakarta=8 | Kota Kendari=2 | Kota Bogor=2 | Kabupaten Pemalang=1 | Kota Pekalongan=1 | Kabupaten Purbalingga=1 | Kabupaten Lampung Tengah=1 | Kabupaten Pekalongan=1 | Kabupaten Kebumen=1 | Kota Palangka Raya=1 | Kabupaten Cilacap=1
    VALUES[nama_balai] (18): Direktorat Pengawasan Produksi ONPP=1,410 | BALAI BESAR POM DI BANDUNG=1,052 | BALAI BESAR POM DI JAKARTA=897 | BALAI BESAR POM DI SURABAYA=860 | BALAI BESAR POM DI SEMARANG=605 | BALAI BESAR POM DI SERANG=395 | BALAI BESAR POM DI PALEMBANG=177 | BALAI POM DI BOGOR=144 | BALAI POM DI TANGERANG=106 | BALAI BESAR POM DI MEDAN=102 | BALAI BESAR POM DI YOGYAKARTA=52 | BALAI POM DI SURAKARTA=47 | BALAI BESAR POM DI PADANG=39 | BALAI BESAR POM DI KENDARI=2 | BALAI BESAR POM DI PALANGKARAYA=1 | DEMO TIPE A=1 | BALAI BESAR POM DI BANDAR LAMPUNG=1 | BALAI POM DI KEDIRI=1
    VALUES[criteria_index] (48): 1=902 | 2=569 | 3=549 | 4=543 | 5=528 | 6=498 | 7=465 | 8=395 | 9=335 | 10=258 | 11=201 | 12=142 | 13=104 | 14=86 | 15=68 | 16=55 | 17=36 | 18=28 | 19=21 | 20=15 | 21=12 | 23=8 | 22=8 | 24=6 | 25=5 | 26=4 | 27=3 | 28=3 | 39=3 | 40=3 | 34=3 | 38=3 | 32=3 | 29=3 | 37=3 | 33=3 | 30=3 | 35=3 | 36=3 | 31=3 | 41=2 | 45=1 | 47=1 | 48=1 | 42=1 | 44=1 | 46=1 | 43=1
    VALUES[tx_criteria] (4): 3=2,635 | 2=2,620 | <NULL>=294 | 1=294 | 4=49

### mv_pemeriksaan  —  257,482 rows
  - id                                   bigint       null=        0 (  0.0%)  distinct=257482
  - nama_upt                             text         null=        0 (  0.0%)  distinct=91
  - nama_sarana                          text         null=        0 (  0.0%)  distinct=130508
  - alamat                               text         null=        0 (  0.0%)  distinct=158944
  - provinsi                             text         null=       18 (  0.0%)  distinct=34
  - kabupaten_kota                       text         null=       18 (  0.0%)  distinct=514
  - tanggal_input                        date         null=        0 (  0.0%)  distinct=2332
  - tanggal_mulai                        date         null=      946 (  0.4%)  distinct=2201
  - tanggal_selesai                      date         null=      946 (  0.4%)  distinct=2400
  - day_input_mulai                      bigint       null=      946 (  0.4%)  distinct=762
  - day_input_selesai                    bigint       null=      946 (  0.4%)  distinct=854
  - day_mulai_selesai                    bigint       null=      946 (  0.4%)  distinct=401
  - sarana                               text         null=        1 (  0.0%)  distinct=3
  - jenis_sarana                         text         null=        0 (  0.0%)  distinct=24
  - legal                                text         null=       23 (  0.0%)  distinct=51
  - tujuan_pemeriksaan                   text         null=      946 (  0.4%)  distinct=36
  - komoditi                             text         null=        0 (  0.0%)  distinct=13
  - mapping_komoditi_target_balai        text         null=        0 (  0.0%)  distinct=6
  - klasifikasi_distribusi               text         null=  197,568 ( 76.7%)  distinct=22
  - klasifikasi_sarana                   text         null=  196,102 ( 76.2%)  distinct=4
  - kesimpulan                           text         null=        0 (  0.0%)  distinct=6
  - status                               text         null=        0 (  0.0%)  distinct=17
  - status_label                         text         null=      114 (  0.0%)  distinct=15
  - tx_critical_issue                    integer      null=  202,297 ( 78.6%)  distinct=16
  - tx_major_issue                       integer      null=  190,898 ( 74.1%)  distinct=45
  - tx_minor_issue                       integer      null=  190,315 ( 73.9%)  distinct=42
  - grade                                text         null=  213,363 ( 82.9%)  distinct=4
  - tl_saran_names                       ARRAY        null=   44,035 ( 17.1%)  distinct=-
  - hp_followup_name                     text         null=  256,696 ( 99.7%)  distinct=20
  - tingkat_pemenuhan_cpob               text         null=  256,621 ( 99.7%)  distinct=4
  - sync                                 timestamp without time zone null=        0 (  0.0%)  distinct=1
    VALUES[provinsi] (34): JAWA BARAT=18,474 | JAWA TENGAH=13,861 | DKI JAKARTA=13,254 | JAWA TIMUR=12,860 | NUSA TENGGARA TIMUR=10,474 | SULAWESI SELATAN=10,444 | SUMATERA BARAT=10,424 | ACEH=10,045 | PAPUA=9,767 | LAMPUNG=8,983 | MALUKU=8,789 | SUMATERA UTARA=8,674 | RIAU=8,385 | BANTEN=8,311 | SUMATERA SELATAN=7,511 | BALI=7,152 | DI YOGYAKARTA=7,014 | SULAWESI TENGGARA=6,844 | JAMBI=6,742 | KALIMANTAN TIMUR=6,614 | KEPULAUAN RIAU=6,584 | NUSA TENGGARA BARAT=6,292 | KALIMANTAN SELATAN=6,161 | KALIMANTAN BARAT=5,529 | SULAWESI TENGAH=5,389 | PAPUA BARAT=5,373 | SULAWESI UTARA=4,918 | GORONTALO=4,486 | KALIMANTAN TENGAH=4,410 | BENGKULU=4,315 | KEPULAUAN BANGKA BELITUNG=4,159 | MALUKU UTARA=2,342 | KALIMANTAN UTARA=1,617 | SULAWESI BARAT=1,267 | <NULL>=18
    VALUES[sarana] (3): DISTRIBUSI=141,491 | PELAYANAN=72,641 | PRODUKSI=43,349 | <NULL>=1
    VALUES[jenis_sarana] (24): PANGAN=61,548 | KOSMETIK=36,720 | APOTEK=27,504 | PANGAN MD=26,308 | PUSAT KESEHATAN MASYARAKAT (PKM)=19,755 | OBAT TRADISIONAL=16,923 | PANGAN IRT (CPPB - IRT)=10,283 | BALAI PENGOBATAN / KLINIK=10,167 | INTENSIFIKASI PENGAWASAN KHUSUS=9,061 | SUPLEMEN KESEHATAN=7,092 | TOKO OBAT=6,891 | PBF=6,867 | INSTALLASI FARMASI RUMAH SAKIT SWASTA=4,526 | INSTALLASI FARMASI RUMAH SAKIT PEMERINTAH=3,787 | INSTALASI FARMASI PEMERINTAH KOTA/KABUPATEN (IFK)=3,117 | OBAT TRADISIONAL (CPOTB)=2,917 | KOSMETIK (CPKB)=2,596 | SARANA PRODUKSI OBAT=907 | INSTALASI FARMASI PEMERINTAH PROVINSI (IFP)=339 | BAHAN BERBAHAYA=108 | PANGAN UMKM MENUJU MD=52 | KANTOR KESEHATAN PELABUHAN (KKP)=11 | PANGAN MD (OLD)=2 | DARING=1
    VALUES[legal] (51): TOKO=48,271 | APOTEK=35,885 | PT=31,240 | SWALAYAN / MINI MARKET / SUPER MARKET=26,402 | PKM=19,588 | CV=10,833 | KIOS / WARUNG=10,543 | TOKO OBAT=8,903 | KLINIK=7,708 | PIRT=7,366 | UMKM MILIK PERORANGAN=6,779 | DEPOT JAMU / TOKO JAMU / DEPOT OBAT=4,522 | UD=4,380 | RUMAH SAKIT=4,308 | RUMAH SAKIT UMUM=3,937 | KLINIK KECANTIKAN=3,448 | -=3,284 | GFK=3,264 | DISTRIBUTOR / AGEN=3,093 | BALAI PENGOBATAN=2,134 | ALFAMART/ALFAMIDI=2,063 | SALON=2,044 | INDOMARET=2,036 | TOKO KELONTONG=1,140 | STAND / LOS / GEROBAK / COUNTER=985 | STOKIST / MLM=952 | BADAN USAHA/PERORANGAN SEBAGAI PEMOHON NOTIFIKASI KOSMETIK=686 | PD=449 | LEMBAGA / INSTITUSI=195 | IMPORTIR KOSMETIKA=173 | KLINIK HERBAL=147 | SARANA PERMANEN (TOKO/WARUNG/KIOS)=138 | FITNES COUNTER=122 | SARANA SEMI/NON PERMANEN (LAPAK)=103 | RUMAH BERSALIN=53 | SPA=52 | SUPLEMEN KESEHATAN=42 | UTD=39 | PELAYANAN=32 | PRODUKSI=26 | IMPORTIR OBAT TRADISIONAL DAN/ATAU SUPLEMEN MAKANAN=23 | <NULL>=23 | PBF=22 | MARKETPLACE=12 | SARANA BERGERAK (MOBIL/MOTOR/KANVAS/GEROBAK)=11 | INSTALASI FARMASI PEMERINTAH PROVINSI (IFP)=7 | BADAN USAHA DI BIDANG PEMASARAN=6 | DISTRIBUSI=4 | SARANA PRODUKSI OBAT=4 | MEDIA SOSIAL=3 | OBAT TRADISIONAL=1 | PANGAN IRT (CPPB - IRT)=1
    VALUES[tujuan_pemeriksaan] (36): PEMERIKSAAN RUTIN=200,625 | INTENSIFIKASI PENGAWASAN PANGAN=16,231 | INTENSIFIKASI VAKSIN=7,696 | RENCANA AKSI / INTENSIFIKASI PENGAWASAN=7,005 | SERTIFIKASI=5,328 | NATAL DAN TAHUN BARU=4,847 | IDUL FITRI=3,925 | SURVEILANS SMKPO=3,338 | KASUS=2,474 | PERMINTAAN REGISTRASI=1,173 | SERTIFIKASI CDOB=1,113 | <NULL>=946 | FORTIFIKASI=591 | KASUS/ TINDAK LANJUT=575 | KHUSUS=372 | VERIFIKASI CAPA SERTIFIKASI DAN PERIZINAN=295 | HARI BESAR AGAMA LAINNYA=234 | PEMUSNAHAN=183 | TINDAK LANJUT=113 | PRA SERTIFIKASI=88 | RESERTIFIKASI=60 | SERTIFIKASI CPOB=57 | VERIFIKASI CAPA PEMERIKSAAN RUTIN=41 | AUDIT PENERAPAN CPKB=32 | KOMPREHENSIF=31 | SERTIFIKASI UMKM MENJADI MD=26 | ASISTENSI=16 | VERIFIKASI CAPA=15 | VERIFIKASI CAPA KASUS=13 | IMLEK=11 | OPGABNAS=6 | IDUL ADHA=6 | PENELUSURAN JARINGAN=5 | TINDAKLANJUT PRAMUKA SAPA=4 | TINDAK LANJUT SURAT EDARAN=3 | OBSERVASI INSPEKSI OTORITAS LAIN=2 | OPGABDA=2
    VALUES[komoditi] (13): PRODUK PANGAN=107,254 | OBAT=82,850 | KOSMETIK=39,317 | OBAT TRADISIONAL=19,925 | SUPLEMEN KESEHATAN=7,126 | NARKOTIKA=273 | PSIKOTROPIKA=252 | OBAT OBAT TERTENTU=176 | PREKURSOR=118 | BAHAN BERBAHAYA=108 | PRODUK BIOLOGI DAN SARANA KHUSUS=55 | BAHAN BAKU OBAT=17 | BAHAN OBAT=11
    VALUES[mapping_komoditi_target_balai] (6): PRODUK PANGAN=107,254 | OBAT=83,752 | KOSMETIKA=39,317 | OBAT TRADISIONAL (OT)=19,925 | SUPLEMEN KESEHATAN=7,126 | OBAT KUASI=108
    VALUES[klasifikasi_distribusi] (22): <NULL>=197,568 | TOKO KOSMETIK / SWALAYAN / PENGECER=18,031 | DEPOT JAMU / PENGECER=12,176 | PENGECER=6,691 | LAIN-LAIN=4,574 | TOKO OBAT / SWALAYAN=4,508 | KLINIK KECANTIKAN / SALON / SPA=4,045 | DISTRIBUTOR=2,906 | BADAN USAHA/USAHA PERORANGAN PEMILIK NOTIFIKASI KOSMETIK=1,704 | IMPORTIR KOSMETIKA=1,597 | AGEN=1,197 | STOKIST MLM=863 | KLINIK KECANTIKAN=696 | SALON/SPA=317 | IMPORTIR OBAT TRADISIONAL DAN / ATAU SUPLEMEN MAKANAN=276 | PENGOBATAN TRADISIONAL ATAU ALTERNATIF=150 | GROSIR=39 | SUB DISTRIBUTOR ATAU SUB AGEN=38 | APOTEK/INSTALASI FARMASI=35 | PENJUALAN LANGSUNG SATU/MULTI TINGKAT (MLM)=26 | PENJUALAN OBAT TRADISIONAL DAN / ATAU SUPLEMEN MAKANAN MELALUI MEDIA ELEKTRONIK=22 | PENJUALAN KOSMETIK MELALUI MEDIA ELEKTRONIK=15 | BADAN USAHA=8
    VALUES[klasifikasi_sarana] (4): <NULL>=196,102 | SARANA RITEL MODERN=30,083 | SARANA RITEL TRADISIONAL=24,305 | SARANA GUDANG IMPORTIR/DISTRIBUTOR=6,940 | SARANA GUDANG E-COMMERCE=52
    VALUES[kesimpulan] (6): MK=176,791 | TMK=75,395 | NULL=2,948 | TTP=1,540 | TDP=790 | TMBB=18
    VALUES[status] (17): VERIFY4=165,898 | VERIFY5=46,324 | FINISHED=28,863 | DRAFT_REVISE=5,109 | VERIFY7=4,744 | DRAFT=3,245 | VERIFY6=1,008 | VERIFY2=619 | VERIFY1=596 | DRAFT_PUSAT=458 | VERIFY_P1=346 | FINISHED_PUSAT=113 | VERIFY_P3=85 | VERIFY3=53 | DRAFT_PUSAT_REVISE=13 | VERIFY_P2=7 | NULL=1
    VALUES[status_label] (15): OPERATOR PUSAT - VERIFIKASI=165,898 | SUPERVISOR PUSAT - VERIFIKASI=46,324 | SELESAI=28,863 | OPERATOR - PERBAIKAN=5,109 | DIREKTUR - VERIFIKASI=4,744 | OPERATOR - DRAFT=3,245 | SUPERVISOR 2 PUSAT - VERIFIKASI=1,008 | SUPERVISOR 2 - VERIFIKASI=619 | SUPERVISOR - VERIFIKASI=596 | PEMERIKSAAN PUSAT - OPERATOR PUSAT - DRAFT=458 | PEMERIKSAAN PUSAT - SUPERVISOR PUSAT - VERIFIKASI=346 | <NULL>=114 | PEMERIKSAAN PUSAT - DIREKTUR - VERIFIKASI=85 | KEPALA BALAI / LOKA - VERIFIKASI=53 | PEMERIKSAAN PUSAT - OPERATOR PUSAT - PERBAIKAN=13 | PEMERIKSAAN PUSAT - SUPERVISOR 2 PUSAT - VERIFIKASI=7
    VALUES[tx_critical_issue] (16): <NULL>=202,297 | 0=44,419 | 1=6,807 | 2=2,210 | 3=926 | 4=407 | 5=201 | 6=104 | 7=53 | 8=21 | 9=12 | 13=9 | 10=7 | 11=5 | 12=2 | 17=1 | 14=1
    VALUES[tx_major_issue] (45): <NULL>=190,898 | 0=19,667 | 1=12,770 | 2=10,714 | 3=5,124 | 4=3,875 | 5=3,088 | 6=2,379 | 7=1,784 | 8=1,444 | 9=1,077 | 10=837 | 11=623 | 12=550 | 13=446 | 14=351 | 15=349 | 16=268 | 17=227 | 18=202 | 19=175 | 20=122 | 21=105 | 24=73 | 22=69 | 23=65 | 25=38 | 26=28 | 27=27 | 29=23 | 28=20 | 30=14 | 32=11 | 34=8 | 31=7 | 33=7 | 36=3 | 40=2 | 58=2 | 41=2 | 37=2 | 35=2 | 38=1 | 43=1 | 39=1 | 61=1
    VALUES[tx_minor_issue] (42): <NULL>=190,315 | 0=12,273 | 1=10,307 | 2=7,482 | 3=6,433 | 4=5,503 | 5=4,683 | 6=3,804 | 7=3,051 | 8=2,519 | 9=2,015 | 10=1,871 | 11=1,364 | 12=1,191 | 13=883 | 14=794 | 15=668 | 16=517 | 17=425 | 18=330 | 19=245 | 20=188 | 21=155 | 22=130 | 23=93 | 24=56 | 25=41 | 26=34 | 27=30 | 28=21 | 30=14 | 29=14 | 31=11 | 32=9 | 39=2 | 36=2 | 35=2 | 34=2 | 61=1 | 46=1 | 48=1 | 38=1 | 44=1
    VALUES[grade] (4): <NULL>=213,363 | A=24,624 | B=9,747 | C=9,683 | N/A=65
    VALUES[hp_followup_name] (20): <NULL>=256,696 | Pembinaan=242 | Peringatan Keras=119 | Peringatan=112 | Perintah Perbaikan=99 | N/A=60 | Perbaikan Hasil Inspeksi=49 | Produk Dimusnahkan=35 | Permintaan CAPA=20 | Penghentian Sementara Kegiatan=16 | Rekomendasi Peringatan Keras=16 | Rekomendasi Penghentian Sementara Kegiatan=5 | Rekomendasi Perbaikan=4 | Rekomendasi Peringatan=2 | Rekomendasi Penarikan dan/atau Perintah Pemusnahan atau Pengiriman Kembali / Re-Ekspor=1 | Rekomendasi Pencabutan Izin/Perizinan Berusaha=1 | Rekomendasi Pencabutan Sertifikat Cara Pembuatan Obat yang Baik=1 | Produk Diamankan=1 | Pencabutan Sertifikat CDOB=1 | Pencabutan Izin/Perizinan Berusaha=1 | Rekomendasi larangan produksi dan/atau mengedarkan untuk sementara waktu=1
    VALUES[tingkat_pemenuhan_cpob] (4): <NULL>=256,621 | Baik=425 | Cukup=176 | Kurang=175 | Memuaskan=85

### mv_pemeriksaan_agg  —  366,840 rows
  - periode_type                         text         null=        0 (  0.0%)  distinct=2
  - tanggal_periode                      date         null=        0 (  0.0%)  distinct=2426
  - nama_upt                             text         null=        0 (  0.0%)  distinct=91
  - provinsi                             text         null=       35 (  0.0%)  distinct=34
  - kabupaten_kota                       text         null=       35 (  0.0%)  distinct=514
  - sarana                               text         null=        0 (  0.0%)  distinct=3
  - jenis_sarana                         text         null=        0 (  0.0%)  distinct=23
  - legal                                text         null=        2 (  0.0%)  distinct=45
  - tujuan_pemeriksaan                   text         null=        0 (  0.0%)  distinct=36
  - komoditi                             text         null=        0 (  0.0%)  distinct=13
  - kesimpulan                           text         null=        0 (  0.0%)  distinct=6
  - status                               text         null=        0 (  0.0%)  distinct=17
  - jumlah_pemeriksaan                   bigint       null=        0 (  0.0%)  distinct=43
  - jumlah_sarana_unik                   bigint       null=        0 (  0.0%)  distinct=42
  - total_critical_issue                 bigint       null=        0 (  0.0%)  distinct=31
  - total_major_issue                    bigint       null=        0 (  0.0%)  distinct=82
  - total_minor_issue                    bigint       null=        0 (  0.0%)  distinct=139
  - avg_critical_issue                   double precision null=        0 (  0.0%)  distinct=111
  - avg_major_issue                      double precision null=        0 (  0.0%)  distinct=332
  - avg_minor_issue                      double precision null=        0 (  0.0%)  distinct=487
  - avg_day_input_mulai                  double precision null=        0 (  0.0%)  distinct=3456
  - avg_day_input_selesai                double precision null=        0 (  0.0%)  distinct=3585
  - avg_day_mulai_selesai                double precision null=        0 (  0.0%)  distinct=873
  - min_day_mulai_selesai                bigint       null=        0 (  0.0%)  distinct=399
  - max_day_mulai_selesai                bigint       null=        0 (  0.0%)  distinct=401
  - last_updated                         timestamp without time zone null=        0 (  0.0%)  distinct=1
    VALUES[periode_type] (2): day=202,124 | month=164,716
    VALUES[provinsi] (34): JAWA BARAT=29,615 | JAWA TENGAH=22,518 | JAWA TIMUR=20,979 | DKI JAKARTA=18,974 | SULAWESI SELATAN=15,453 | SUMATERA BARAT=15,221 | NUSA TENGGARA TIMUR=14,147 | SUMATERA UTARA=12,444 | ACEH=12,144 | BANTEN=11,958 | LAMPUNG=11,867 | RIAU=11,488 | BALI=11,192 | PAPUA=10,899 | SUMATERA SELATAN=10,630 | SULAWESI TENGGARA=10,583 | JAMBI=10,062 | MALUKU=10,037 | DI YOGYAKARTA=9,562 | KALIMANTAN SELATAN=9,425 | KEPULAUAN RIAU=9,193 | KALIMANTAN TIMUR=8,673 | NUSA TENGGARA BARAT=8,499 | KALIMANTAN BARAT=7,805 | SULAWESI TENGAH=7,674 | PAPUA BARAT=7,360 | SULAWESI UTARA=6,999 | BENGKULU=6,510 | KEPULAUAN BANGKA BELITUNG=5,874 | GORONTALO=5,780 | KALIMANTAN TENGAH=5,545 | MALUKU UTARA=3,331 | KALIMANTAN UTARA=2,559 | SULAWESI BARAT=1,805 | <NULL>=35
    VALUES[sarana] (3): DISTRIBUSI=188,847 | PELAYANAN=107,258 | PRODUKSI=70,735
    VALUES[jenis_sarana] (23): PANGAN=74,735 | KOSMETIK=51,367 | PANGAN MD=44,416 | APOTEK=36,566 | PUSAT KESEHATAN MASYARAKAT (PKM)=27,246 | OBAT TRADISIONAL=25,345 | BALAI PENGOBATAN / KLINIK=17,043 | PANGAN IRT (CPPB - IRT)=13,795 | SUPLEMEN KESEHATAN=11,282 | TOKO OBAT=11,173 | PBF=11,148 | INTENSIFIKASI PENGAWASAN KHUSUS=8,525 | INSTALLASI FARMASI RUMAH SAKIT SWASTA=7,950 | INSTALLASI FARMASI RUMAH SAKIT PEMERINTAH=7,258 | INSTALASI FARMASI PEMERINTAH KOTA/KABUPATEN (IFK)=6,134 | OBAT TRADISIONAL (CPOTB)=5,431 | KOSMETIK (CPKB)=4,819 | SARANA PRODUKSI OBAT=1,638 | INSTALASI FARMASI PEMERINTAH PROVINSI (IFP)=662 | BAHAN BERBAHAYA=191 | PANGAN UMKM MENUJU MD=90 | KANTOR KESEHATAN PELABUHAN (KKP)=22 | PANGAN MD (OLD)=4
    VALUES[legal] (45): TOKO=58,113 | PT=50,158 | APOTEK=48,815 | SWALAYAN / MINI MARKET / SUPER MARKET=32,569 | PKM=26,951 | CV=19,180 | TOKO OBAT=14,473 | KLINIK=12,732 | UMKM MILIK PERORANGAN=11,087 | KIOS / WARUNG=10,007 | PIRT=9,036 | RUMAH SAKIT=7,610 | RUMAH SAKIT UMUM=7,479 | UD=7,426 | GFK=6,411 | DEPOT JAMU / TOKO JAMU / DEPOT OBAT=6,041 | -=5,940 | DISTRIBUTOR / AGEN=5,292 | KLINIK KECANTIKAN=5,091 | BALAI PENGOBATAN=3,807 | ALFAMART/ALFAMIDI=3,506 | INDOMARET=3,389 | SALON=3,161 | TOKO KELONTONG=1,702 | STOKIST / MLM=1,701 | BADAN USAHA/PERORANGAN SEBAGAI PEMOHON NOTIFIKASI KOSMETIK=1,238 | STAND / LOS / GEROBAK / COUNTER=1,205 | PD=852 | LEMBAGA / INSTITUSI=379 | IMPORTIR KOSMETIKA=318 | KLINIK HERBAL=268 | SARANA PERMANEN (TOKO/WARUNG/KIOS)=212 | FITNES COUNTER=198 | SARANA SEMI/NON PERMANEN (LAPAK)=105 | RUMAH BERSALIN=104 | SPA=99 | UTD=70 | IMPORTIR OBAT TRADISIONAL DAN/ATAU SUPLEMEN MAKANAN=44 | MARKETPLACE=19 | SARANA BERGERAK (MOBIL/MOTOR/KANVAS/GEROBAK)=16 | BADAN USAHA DI BIDANG PEMASARAN=12 | SUPLEMEN KESEHATAN=8 | MEDIA SOSIAL=6 | PBF=4 | PELAYANAN=4 | <NULL>=2
    VALUES[tujuan_pemeriksaan] (36): PEMERIKSAAN RUTIN=295,281 | INTENSIFIKASI PENGAWASAN PANGAN=18,199 | INTENSIFIKASI VAKSIN=9,810 | SERTIFIKASI=9,217 | RENCANA AKSI / INTENSIFIKASI PENGAWASAN=8,573 | SURVEILANS SMKPO=5,831 | NATAL DAN TAHUN BARU=4,231 | IDUL FITRI=4,000 | KASUS=3,791 | SERTIFIKASI CDOB=1,791 | PERMINTAAN REGISTRASI=1,678 | FORTIFIKASI=978 | KASUS/ TINDAK LANJUT=708 | KHUSUS=649 | VERIFIKASI CAPA SERTIFIKASI DAN PERIZINAN=553 | PEMUSNAHAN=279 | HARI BESAR AGAMA LAINNYA=252 | TINDAK LANJUT=221 | PRA SERTIFIKASI=174 | RESERTIFIKASI=117 | SERTIFIKASI CPOB=114 | VERIFIKASI CAPA PEMERIKSAAN RUTIN=79 | AUDIT PENERAPAN CPKB=60 | KOMPREHENSIF=58 | SERTIFIKASI UMKM MENJADI MD=47 | ASISTENSI=32 | VERIFIKASI CAPA=30 | VERIFIKASI CAPA KASUS=25 | IDUL ADHA=12 | IMLEK=11 | PENELUSURAN JARINGAN=9 | TINDAKLANJUT PRAMUKA SAPA=8 | OPGABNAS=8 | TINDAK LANJUT SURAT EDARAN=6 | OPGABDA=4 | OBSERVASI INSPEKSI OTORITAS LAIN=4
    VALUES[komoditi] (13): PRODUK PANGAN=141,565 | OBAT=125,064 | KOSMETIK=56,186 | OBAT TRADISIONAL=30,893 | SUPLEMEN KESEHATAN=11,338 | NARKOTIKA=510 | PSIKOTROPIKA=454 | OBAT OBAT TERTENTU=259 | PREKURSOR=218 | BAHAN BERBAHAYA=191 | PRODUK BIOLOGI DAN SARANA KHUSUS=106 | BAHAN BAKU OBAT=34 | BAHAN OBAT=22
    VALUES[kesimpulan] (6): MK=241,726 | TMK=117,258 | NULL=3,611 | TTP=2,722 | TDP=1,497 | TMBB=26
    VALUES[status] (17): VERIFY4=228,206 | VERIFY5=68,918 | FINISHED=44,348 | DRAFT_REVISE=8,526 | VERIFY7=7,635 | DRAFT=3,887 | VERIFY6=1,582 | VERIFY1=1,006 | VERIFY2=998 | VERIFY_P1=628 | DRAFT_PUSAT=595 | FINISHED_PUSAT=208 | VERIFY_P3=168 | VERIFY3=97 | DRAFT_PUSAT_REVISE=22 | VERIFY_P2=14 | NULL=2
    VALUES[jumlah_pemeriksaan] (43): 1=285,238 | 2=52,591 | 3=15,496 | 4=6,281 | 5=2,901 | 6=1,587 | 7=900 | 8=552 | 9=350 | 10=237 | 11=165 | 12=135 | 13=81 | 14=71 | 15=48 | 16=35 | 17=33 | 19=17 | 22=15 | 21=15 | 18=14 | 24=12 | 20=11 | 23=8 | 25=7 | 28=6 | 30=5 | 29=4 | 26=4 | 39=4 | 35=2 | 52=2 | 31=2 | 27=2 | 49=1 | 36=1 | 50=1 | 53=1 | 33=1 | 38=1 | 37=1 | 40=1 | 47=1
    VALUES[jumlah_sarana_unik] (42): 1=287,260 | 2=51,374 | 3=15,181 | 4=6,086 | 5=2,781 | 6=1,528 | 7=870 | 8=522 | 9=339 | 10=218 | 11=162 | 12=131 | 13=89 | 14=73 | 15=35 | 16=31 | 17=27 | 19=16 | 18=16 | 21=15 | 22=12 | 23=12 | 20=10 | 25=9 | 24=7 | 30=4 | 26=4 | 29=3 | 36=3 | 38=3 | 28=3 | 27=3 | 52=2 | 32=2 | 31=2 | 53=1 | 34=1 | 39=1 | 45=1 | 37=1 | 46=1 | 49=1
    VALUES[total_critical_issue] (31): 0=349,479 | 1=9,597 | 2=3,656 | 3=1,728 | 4=942 | 5=501 | 6=318 | 7=202 | 8=132 | 9=69 | 10=42 | 11=33 | 12=32 | 13=26 | 14=18 | 18=11 | 17=10 | 16=9 | 15=7 | 19=6 | 26=5 | 23=3 | 24=2 | 32=2 | 22=2 | 21=2 | 25=2 | 31=1 | 34=1 | 27=1 | 20=1

### mv_pemeriksaan_jenis_pangan  —  67,206 rows
  - id_pemeriksaan                       bigint       null=        0 (  0.0%)  distinct=48519
  - jenis_pangan_name                    text         null=        0 (  0.0%)  distinct=200
  - posisi_dalam_array                   bigint       null=        0 (  0.0%)  distinct=20
  - sync                                 timestamp without time zone null=        0 (  0.0%)  distinct=1
    VALUES[posisi_dalam_array] (20): 1=48,519 | 2=11,809 | 3=6,354 | 4=208 | 5=114 | 6=69 | 7=47 | 8=27 | 9=19 | 10=13 | 11=8 | 12=5 | 13=4 | 14=4 | 16=1 | 17=1 | 15=1 | 19=1 | 20=1 | 18=1

### mv_pemeriksaan_kategori_temuan  —  241,609 rows
  - id_pemeriksaan                       bigint       null=        0 (  0.0%)  distinct=29699
  - tp_kategori                          text         null=        0 (  0.0%)  distinct=49
  - posisi_dalam_array                   bigint       null=        0 (  0.0%)  distinct=3
  - sync                                 timestamp without time zone null=        0 (  0.0%)  distinct=1
    VALUES[tp_kategori] (49): TIE (Tanpa Izin Edar)=128,666 | ED (Expire Date / Kedaluwarsa)=46,479 | Temuan Obat Keras=15,891 | BKO=14,330 | Rusak=8,480 | Substandard/Rusak=7,901 | Illegal/TIE=5,445 | Lain - Lain=5,241 | TMK Label=3,073 | Kedaluwarsa=2,914 | Diversi/Penyalahgunaan=1,207 | Mengandung bahan berbahaya/bahan dilarang (berdasarkan SE)=689 | Farmasetik=476 | Mengandung bahan berbahaya/bahan dilarang (daftar PW)=229 | Mengandung bahan berbahaya/dilarang.=205 | Palsu=59 | Padat=52 | Pemusnahan=37 | Penandaan=31 | TIE=30 | Aspek CPOB / CPOTB / CPMB=28 | TMS Persyaratan Keamanan, Mutu, Dan Gizi Pangan=20 | Kedaluwarsa / Rusak=19 | Dimusnahkan=18 | Administrasi=7 | Bahan Obat=5 | Memproduksi MGB Berbahaya=4 | NPP dan OOT=4 | Obat=4 | Memproduksi Kosmetik TIE=4 | Lain-lain=4 | Agen=4 | Stokist MLM=4 | Distributor=4 | Dikembalikan kepada produsen / importir=4 | CCP=4 | Badan Usaha/Usaha Perorangan Pemilik Notifikasi Kosmetik=4 | Memproduksi Produk TMK Penandaan=4 | Klinik Kecantikan / Salon / Spa=4 | Importir Kosmetika=4 | Penarikan=4 | Penjualan kosmetik melalui media elektronik=4 | Dokumen Informasi Produk (DIP)=4 | Produksi=2 | Obat Tradisional (OT)=2 | Pengamanan=2 | Pemeriksaan Sarana=1 | Peringatan Tertulis=1 | Sale Pisang=1
    VALUES[posisi_dalam_array] (3): 1=234,180 | 2=7,346 | 3=83

### mv_pemeriksaan_log  —  1,311,847 rows
  - id_pemeriksaan                       bigint       null=        0 (  0.0%)  distinct=257482
  - id_steps                             bigint       null=       64 (  0.0%)  distinct=1311783
  - status                               text         null=       64 (  0.0%)  distinct=16
  - status_label                         text         null=      177 (  0.0%)  distinct=15
  - fullname                             text         null=      777 (  0.1%)  distinct=2063
  - nama_balai                           text         null=      809 (  0.1%)  distinct=92
  - catatan                              text         null=  232,167 ( 17.7%)  distinct=207863
  - created_at                           timestamp without time zone null=       64 (  0.0%)  distinct=887853
  - updated_at                           timestamp without time zone null=       92 (  0.0%)  distinct=887852
  - urutan_step                          bigint       null=        0 (  0.0%)  distinct=75
  - sync                                 timestamp without time zone null=        0 (  0.0%)  distinct=1
    VALUES[status] (16): VERIFY1=290,557 | VERIFY3=256,870 | DRAFT=256,493 | VERIFY4=253,902 | VERIFY5=82,407 | VERIFY2=40,444 | DRAFT_REVISE=38,712 | VERIFY7=34,587 | FINISHED=29,414 | VERIFY6=26,595 | DRAFT_PUSAT=953 | VERIFY_P1=526 | VERIFY_P3=137 | FINISHED_PUSAT=113 | <NULL>=64 | DRAFT_PUSAT_REVISE=41 | VERIFY_P2=32
    VALUES[status_label] (15): Supervisor - Verifikasi=290,557 | Kepala Balai / Loka - Verifikasi=256,870 | Operator - Draft=256,493 | Operator Pusat - Verifikasi=253,902 | Supervisor Pusat - Verifikasi=82,407 | Supervisor 2 - Verifikasi=40,444 | Operator - Perbaikan=38,712 | Direktur - Verifikasi=34,587 | Selesai=29,414 | Supervisor 2 Pusat - Verifikasi=26,595 | Pemeriksaan Pusat - Operator Pusat - Draft=953 | Pemeriksaan Pusat - Supervisor Pusat - Verifikasi=526 | <NULL>=177 | Pemeriksaan Pusat - Direktur - Verifikasi=137 | Pemeriksaan Pusat - Operator Pusat - Perbaikan=41 | Pemeriksaan Pusat - Supervisor 2 Pusat - Verifikasi=32
    VALUES[urutan_step] (75): 1=257,482 | 2=253,788 | 3=252,874 | 4=249,991 | 5=125,719 | 6=65,817 | 7=47,432 | 8=32,492 | 9=13,052 | 10=5,729 | 11=3,532 | 12=1,564 | 13=876 | 14=522 | 15=312 | 16=222 | 17=89 | 18=55 | 19=42 | 20=29 | 21=24 | 22=16 | 23=12 | 24=10 | 25=9 | 26=7 | 32=6 | 27=6 | 28=6 | 29=6 | 30=6 | 31=6 | 33=6 | 34=6 | 35=6 | 41=5 | 40=5 | 39=5 | 38=5 | 37=5 | 36=5 | 43=4 | 42=4 | 47=3 | 48=3 | 44=3 | 45=3 | 46=3 | 54=2 | 55=2 | 56=2 | 57=2 | 58=2 | 59=2 | 60=2 | 61=2 | 62=2 | 49=2 | 64=2 | 63=2 | 50=2 | 51=2 | 52=2 | 53=2 | 68=1 | 69=1 | 67=1 | 70=1 | 71=1 | 72=1 | 73=1 | 74=1 | 75=1 | 66=1 | 65=1

### mv_pemeriksaan_petugas  —  581,923 rows
  - id_pemeriksaan                       bigint       null=        0 (  0.0%)  distinct=257482
  - petugas_id                           bigint       null=      216 (  0.0%)  distinct=2998
  - petugas                              text         null=      216 (  0.0%)  distinct=2970
  - jenis_id                             bigint       null=        0 (  0.0%)  distinct=25
  - komoditi                             text         null=        0 (  0.0%)  distinct=24
  - tujuan                               text         null=    1,732 (  0.3%)  distinct=36
  - klasifikasi                          text         null=        0 (  0.0%)  distinct=13
  - nomorsurat                           text         null=       29 (  0.0%)  distinct=110605
  - tgl_surat                            date         null=       29 (  0.0%)  distinct=2306
  - daftar_balai_pemeriksa               text         null=       29 (  0.0%)  distinct=98
  - sync                                 timestamp without time zone null=        0 (  0.0%)  distinct=1
    VALUES[jenis_id] (25): 16=140,635 | 13=81,765 | 109=60,106 | 5=59,760 | 107=43,476 | 15=39,044 | 108=22,450 | 18=22,448 | 10=22,136 | 14=15,757 | 105=14,847 | 17=14,410 | 106=10,349 | 748=8,737 | 747=7,127 | 4=7,018 | 7=6,032 | 8=3,570 | 9=1,073 | 12=804 | 11=215 | 6=134 | 211265=26 | 223447=2 | 211337=2
    VALUES[komoditi] (24): PANGAN=140,635 | KOSMETIK=81,765 | APOTEK=60,106 | PANGAN MD=59,760 | PUSAT KESEHATAN MASYARAKAT (PKM)=43,476 | OBAT TRADISIONAL=39,044 | BALAI PENGOBATAN / KLINIK=22,450 | INTENSIFIKASI PENGAWASAN KHUSUS=22,448 | PANGAN IRT (CPPB - IRT)=22,136 | PBF=15,757 | SUPLEMEN KESEHATAN=15,483 | TOKO OBAT=14,847 | INSTALLASI FARMASI RUMAH SAKIT SWASTA=10,349 | INSTALLASI FARMASI RUMAH SAKIT PEMERINTAH=8,737 | INSTALASI FARMASI PEMERINTAH KOTA/KABUPATEN (IFK)=7,127 | OBAT TRADISIONAL (CPOTB)=7,018 | KOSMETIK (CPKB)=6,032 | SARANA PRODUKSI OBAT=3,570 | INSTALASI FARMASI PEMERINTAH PROVINSI (IFP)=804 | BAHAN BERBAHAYA=215 | PANGAN UMKM MENUJU MD=134 | KANTOR KESEHATAN PELABUHAN (KKP)=26 | PANGAN MD (OLD)=2 | DARING=2
    VALUES[tujuan] (36): PEMERIKSAAN RUTIN=443,563 | INTENSIFIKASI PENGAWASAN PANGAN=41,041 | RENCANA AKSI / INTENSIFIKASI PENGAWASAN=19,988 | INTENSIFIKASI VAKSIN=16,736 | SERTIFIKASI=12,268 | NATAL DAN TAHUN BARU=12,008 | IDUL FITRI=9,487 | SURVEILANS SMKPO=7,342 | KASUS=6,012 | SERTIFIKASI CDOB=2,485 | PERMINTAAN REGISTRASI=2,363 | <NULL>=1,732 | FORTIFIKASI=1,529 | KASUS/ TINDAK LANJUT=1,323 | KHUSUS=863 | HARI BESAR AGAMA LAINNYA=782 | VERIFIKASI CAPA SERTIFIKASI DAN PERIZINAN=720 | PEMUSNAHAN=345 | TINDAK LANJUT=253 | SERTIFIKASI CPOB=205 | PRA SERTIFIKASI=202 | RESERTIFIKASI=150 | VERIFIKASI CAPA PEMERIKSAAN RUTIN=106 | KOMPREHENSIF=72 | AUDIT PENERAPAN CPKB=71 | SERTIFIKASI UMKM MENJADI MD=66 | IMLEK=44 | VERIFIKASI CAPA=40 | ASISTENSI=38 | VERIFIKASI CAPA KASUS=23 | OPGABNAS=17 | IDUL ADHA=14 | TINDAK LANJUT SURAT EDARAN=12 | PENELUSURAN JARINGAN=10 | TINDAKLANJUT PRAMUKA SAPA=8 | OBSERVASI INSPEKSI OTORITAS LAIN=3 | OPGABDA=2
    VALUES[klasifikasi] (13): PRODUK PANGAN=245,115 | OBAT=184,787 | KOSMETIK=87,799 | OBAT TRADISIONAL=46,240 | SUPLEMEN KESEHATAN=15,549 | PSIKOTROPIKA=587 | NARKOTIKA=571 | OBAT OBAT TERTENTU=445 | PRODUK BIOLOGI DAN SARANA KHUSUS=268 | PREKURSOR=257 | BAHAN BERBAHAYA=215 | BAHAN BAKU OBAT=69 | BAHAN OBAT=21

### mv_pemeriksaan_temuan  —  296,987 rows
  - id_pemeriksaan                       bigint       null=        0 (  0.0%)  distinct=32504
  - product_register                     text         null=       65 (  0.0%)  distinct=25554
  - product_name                         text         null=       17 (  0.0%)  distinct=89063
  - product_brands                       text         null=  207,502 ( 69.9%)  distinct=5945
  - registrar                            text         null=   86,810 ( 29.2%)  distinct=15333
  - tp_bets                              text         null=  140,007 ( 47.1%)  distinct=50822
  - tp_negara                            text         null=    6,039 (  2.0%)  distinct=1299
  - tp_pelanggaran                       text         null=  296,975 (100.0%)  distinct=7
  - tp_netto                             text         null=  296,982 (100.0%)  distinct=4
  - tp_expire                            date         null=  182,943 ( 61.6%)  distinct=4186
  - tp_jml_temuan                        bigint       null=      790 (  0.3%)  distinct=1224
  - tp_unit_id                           bigint       null=        0 (  0.0%)  distinct=92
  - tp_harga                             numeric      null=      983 (  0.3%)  distinct=4146
  - tp_harga_total                       numeric      null=      986 (  0.3%)  distinct=8527
  - tp_tindakan                          text         null=      335 (  0.1%)  distinct=126
  - tp_kategori                          text         null=      252 (  0.1%)  distinct=106
  - tp_keterangan                        text         null=  158,660 ( 53.4%)  distinct=17855
  - sync                                 timestamp without time zone null=        0 (  0.0%)  distinct=1
    VALUES[tp_pelanggaran] (7): <NULL>=296,975 | Kadaluarsa=3 | TIE (volume tidak sesuai data notifikasi)=3 | TIE=2 | Menjual kosmetik yang TIE=1 | Expired=1 | menjual kosmetik yang TIE=1 | ED=1
    VALUES[tp_netto] (4): <NULL>=296,982 | 1,7 gr (ternotifikasi untuk 3,5gr)=2 | 1,7 gr=1 | 25 g=1 | kemasan 1,7gr (ternotifikasi untuk 3,5gr)=1

### mv_pemeriksaan_timeline  —  288,186 rows
  - id_pemeriksaan                       bigint       null=        0 (  0.0%)  distinct=288186
  - tgl_start                            date         null=   14,690 (  5.1%)  distinct=2268
  - tgl_end                              date         null=   14,690 (  5.1%)  distinct=2430
  - tanggal_kirim_kabalai                date         null=   39,050 ( 13.6%)  distinct=2111
  - tanggal_kirim_direktur               date         null=  254,414 ( 88.3%)  distinct=378
  - status                               text         null=        0 (  0.0%)  distinct=18
  - mulai_kabalai                        integer      null=   39,062 ( 13.6%)  distinct=656
  - kabalai_direktur                     integer      null=  254,415 ( 88.3%)  distinct=797
  - sync                                 timestamp without time zone null=        0 (  0.0%)  distinct=1
    VALUES[status] (18): VERIFY4=165,916 | VERIFY5=46,326 | DRAFT=33,122 | FINISHED=28,866 | DRAFT_REVISE=5,428 | VERIFY7=4,745 | VERIFY6=1,008 | DRAFT_PUSAT=908 | VERIFY1=624 | VERIFY2=619 | VERIFY_P1=346 | FINISHED_PUSAT=113 | VERIFY_P3=85 | VERIFY3=58 | DRAFT_PUSAT_REVISE=13 | VERIFY_P2=7 | NULL=1 | 0=1

### target_balai  —  532 rows
  - id                                   bigint       null=        0 (  0.0%)  distinct=532
  - nama_balai                           text         null=        0 (  0.0%)  distinct=76
  - komoditi                             text         null=        0 (  0.0%)  distinct=7
  - tahun                                bigint       null=        0 (  0.0%)  distinct=1
  - target_penandaan                     bigint       null=        0 (  0.0%)  distinct=253
  - target_pengawasan                    bigint       null=        0 (  0.0%)  distinct=53
  - target_pengujian                     bigint       null=        0 (  0.0%)  distinct=254
  - target_pengujian_pangan              bigint       null=       17 (  3.2%)  distinct=68
  - target_pengujian_pangan_fortifikasi  bigint       null=       17 (  3.2%)  distinct=19
  - target_sarana_distribusi             bigint       null=        0 (  0.0%)  distinct=177
  - target_sarana_produksi               bigint       null=        0 (  0.0%)  distinct=74
  - sync                                 timestamp without time zone null=        0 (  0.0%)  distinct=1
    VALUES[nama_balai] (76): BALAI BESAR POM DI PALEMBANG=7 | BALAI BESAR POM DI BANJARBARU=7 | BALAI BESAR POM DI GORONTALO=7 | BALAI POM DI TASIKMALAYA=7 | BALAI BESAR POM DI PEKANBARU=7 | BALAI BESAR POM DI SURABAYA=7 | Loka POM di Kabupaten Sijunjung=7 | Loka POM di Kabupaten Belitung=7 | BALAI BESAR POM DI PONTIANAK=7 | Loka POM di Kota Lubuklinggau=7 | BALAI BESAR POM DI KENDARI=7 | BALAI POM DI DUMAI =7 | BALAI POM DI AMBON=7 | BALAI BESAR POM DI PALU=7 | BALAI POM DI BALIKPAPAN=7 | BALAI BESAR POM DI BANDAR LAMPUNG=7 | BALAI BESAR POM DI SEMARANG=7 | Loka POM di Kabupaten Kepulauan Sangihe=7 | Loka POM di Kab. Sumba Timur=7 | BALAI BESAR POM DI SERANG=7 | BALAI BESAR POM DI MANADO=7 | Loka POM di Kab. Sambas=7 | BALAI BESAR POM DI BANDUNG=7 | Loka POM di Kab. Belu=7 | BALAI POM DI TARAKAN=7 | BALAI POM DI TANJUNGBALAI=7 | Loka POM di Kabupaten Buleleng=7 | Loka POM di Kabupaten Aceh Selatan=7 | BALAI POM DI PAYAKUMBUH=7 | BALAI POM DI JAMBI=7 | BALAI POM DI BENGKULU=7 | BALAI POM DI JEMBER=7 | BALAI BESAR POM DI BANDA ACEH=7 | BALAI POM DI BATAM=7 | BALAI POM DI TANGERANG=7 | BALAI BESAR POM DI MEDAN=7 | BALAI POM DI PALOPO=7 | BALAI POM DI TULANGBAWANG=7 | BALAI POM DI ENDE=7 | BALAI POM DI TABALONG=7 | Loka POM di Kabupaten Merauke=7 | Loka POM di Kabupaten Manggarai Barat=7 | BALAI POM DI SANGGAU=7 | BALAI POM DI MANOKWARI=7 | BALAI POM DI INDRAGIRI HULU=7 | BALAI POM DI BOGOR=7 | BALAI POM DI BAU-BAU=7 | BALAI BESAR POM DI PALANGKARAYA=7 | BALAI POM DI PANGKALPINANG=7 | BALAI POM DI SOFIFI=7 | BALAI BESAR POM DI YOGYAKARTA=7 | BALAI BESAR POM DI JAKARTA=7 | BALAI BESAR POM DI KUPANG=7 | Loka POM di Kabupaten Tanah Bumbu=7 | BALAI BESAR POM DI MATARAM=7 | BALAI BESAR POM DI SAMARINDA=7 | Loka POM di Kabupaten Banggai=7 | BALAI POM DI SURAKARTA=7 | BALAI POM DI TOBA=7 | BALAI BESAR POM DI DENPASAR=7 | Loka POM di Kabupaten Aceh Tengah=7 | BALAI BESAR POM DI PADANG=7 | Loka POM di Kabupaten Rejang Lebong=7 | BALAI POM DI KEDIRI=7 | Loka POM di Kabupaten Mimika=7 | BALAI BESAR POM DI MAKASSAR=7 | BALAI POM DI BANYUMAS=7 | BALAI BESAR POM DI JAYAPURA=7 | Loka POM di Kabupaten Kotawaringin Barat=7 | Loka POM di Kabupaten Bungo=7 | Loka POM di Kabupaten Pulau Morotai=7 | BALAI POM DI BIMA=7 | Loka POM di Kabupaten Tanimbar=7 | BALAI POM DI MAMUJU=7 | Loka POM di Kabupaten Sorong=7 | Loka POM di Kota Tanjung Pinang=7
    VALUES[komoditi] (7): Obat Kuasi=76 | Produk Pangan=76 | Obat Tradisional (OT)=76 | Obat=76 | Kosmetika=76 | Suplemen Kesehatan=76 | Rokok=76
    VALUES[tahun] (1): 2024=532
    VALUES[target_pengawasan] (53): 0=76 | 10=55 | 110=42 | 15=42 | 120=38 | 35=26 | 75=22 | 235=21 | 40=19 | 300=17 | 5=16 | 360=14 | 432=10 | 576=10 | 85=9 | 30=8 | 288=8 | 25=8 | 100=7 | 70=7 | 270=6 | 60=6 | 80=6 | 20=6 | 65=5 | 305=5 | 130=5 | 250=3 | 50=3 | 160=3 | 175=2 | 90=2 | 210=2 | 170=2 | 620=2 | 320=2 | 215=1 | 150=1 | 95=1 | 79=1 | 200=1 | 115=1 | 381=1 | 105=1 | 420=1 | 356=1 | 440=1 | 180=1 | 133=1 | 600=1 | 125=1 | 530=1 | 260=1
    VALUES[target_pengujian_pangan] (68): 0=439 | <NULL>=17 | 65=3 | 160=3 | 64=2 | 80=2 | 50=2 | 60=2 | 110=2 | 760=1 | 215=1 | 575=1 | 875=1 | 540=1 | 95=1 | 643=1 | 555=1 | 627=1 | 481=1 | 76=1 | 100=1 | 387=1 | 942=1 | 919=1 | 132=1 | 66=1 | 894=1 | 199=1 | 114=1 | 163=1 | 82=1 | 450=1 | 69=1 | 105=1 | 141=1 | 150=1 | 670=1 | 122=1 | 553=1 | 177=1 | 212=1 | 566=1 | 241=1 | 435=1 | 538=1 | 171=1 | 620=1 | 254=1 | 116=1 | 607=1 | 41=1 | 448=1 | 185=1 | 120=1 | 90=1 | 957=1 | 560=1 | 71=1 | 210=1 | 70=1 | 198=1 | 75=1 | 573=1 | 155=1 | 347=1 | 173=1 | 909=1 | 397=1 | 196=1
    VALUES[target_pengujian_pangan_fortifikasi] (19): 0=462 | <NULL>=17 | 15=10 | 75=9 | 20=6 | 60=4 | 125=4 | 70=4 | 80=3 | 50=2 | 85=2 | 31=1 | 30=1 | 65=1 | 105=1 | 110=1 | 10=1 | 100=1 | 39=1 | 40=1
    VALUES[target_sarana_produksi] (74): 0=327 | 1=38 | 2=12 | 3=11 | 4=10 | 5=7 | 12=6 | 25=6 | 6=5 | 13=5 | 21=5 | 7=4 | 11=4 | 10=4 | 33=3 | 38=3 | 40=3 | 18=3 | 31=3 | 8=3 | 28=2 | 60=2 | 23=2 | 62=2 | 9=2 | 15=2 | 30=2 | 14=2 | 65=2 | 44=2 | 36=2 | 24=2 | 17=2 | 48=2 | 22=2 | 50=2 | 16=1 | 71=1 | 26=1 | 72=1 | 70=1 | 75=1 | 96=1 | 207=1 | 144=1 | 109=1 | 19=1 | 20=1 | 34=1 | 32=1 | 261=1 | 66=1 | 175=1 | 51=1 | 153=1 | 27=1 | 190=1 | 235=1 | 43=1 | 42=1 | 309=1 | 69=1 | 54=1 | 139=1 | 55=1 | 52=1 | 85=1 | 73=1 | 164=1 | 87=1 | 124=1 | 56=1 | 35=1 | 162=1
