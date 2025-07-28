# Dokumen Analisis Kebutuhan Aplikasi Chatbot AI

Dokumen ini bertujuan untuk mendefinisikan kebutuhan fungsional dan non-fungsional dari sistem chatbot AI. Tujuannya adalah untuk memastikan semua pemangku kepentingan memiliki pemahaman yang sama mengenai apa yang akan dibangun.

---

## 1. Kebutuhan Fungsional

Kebutuhan fungsional mendeskripsikan fitur-fitur atau fungsi spesifik yang harus dapat dilakukan oleh sistem.

### 1.1. Manajemen Pengguna
| ID | Kebutuhan | Deskripsi |
| :--- | :--- | :--- |
| KF-01 | Registrasi Pengguna | Sistem harus menyediakan antarmuka bagi pengguna baru untuk mendaftarkan akun dengan username, email, dan password. |
| KF-02 | Login Pengguna | Sistem harus memungkinkan pengguna yang sudah terdaftar untuk masuk menggunakan username dan password. |
| KF-03 | Otentikasi Berbasis Token | Setelah login berhasil, sistem harus menghasilkan token (JWT) yang digunakan untuk mengamankan sesi dan akses ke API. |
| KF-04 | Logout Pengguna | Sistem harus menyediakan fungsi bagi pengguna untuk keluar dari sesi mereka saat ini. |

### 1.2. Fungsionalitas Chat (RAG)
| ID | Kebutuhan | Deskripsi |
| :--- | :--- | :--- |
| KF-05 | Antarmuka Chat | Sistem harus menyediakan antarmuka percakapan di mana pengguna dapat mengirim dan menerima pesan. |
| KF-06 | Pengiriman Pertanyaan | Pengguna harus dapat mengetik dan mengirimkan pertanyaan kepada chatbot. |
| KF-07 | Pemrosesan RAG | Untuk setiap pertanyaan, sistem harus:
| | | 1. Mencari informasi relevan dari basis pengetahuan (Vector Store).
| | | 2. Menggabungkan informasi tersebut dengan pertanyaan asli.
| | | 3. Menghasilkan jawaban menggunakan Large Language Model (LLM). |
| KF-08 | Tampilan Jawaban | Sistem harus menampilkan jawaban yang dihasilkan oleh chatbot kepada pengguna di antarmuka chat. |
| KF-09 | Riwayat Percakapan | Sistem sebaiknya menampilkan riwayat percakapan antara pengguna dan chatbot selama sesi masih aktif. |

### 1.3. Manajemen Basis Pengetahuan (Admin)
| ID | Kebutuhan | Deskripsi |
| :--- | :--- | :--- |
| KF-10 | Ingesti Dokumen | Administrator harus dapat mengunggah file dokumen (misalnya PDF, TXT) ke dalam sistem. |
| KF-11 | Pemrosesan Dokumen | Sistem harus dapat memproses dokumen yang diunggah untuk diekstrak, dipecah (chunking), dan diubah menjadi embeddings. |
| KF-12 | Penyimpanan ke Vector Store | Sistem harus menyimpan hasil embeddings dari dokumen ke dalam database vektor (Vector Store) untuk pencarian di masa mendatang. |

---

## 2. Kebutuhan Non-Fungsional

Kebutuhan non-fungsional mendeskripsikan kriteria kualitas, batasan, dan atribut dari sistem.

| ID | Kategori | Kebutuhan |
| :--- | :--- | :--- |
| KNF-01 | **Kinerja** | Waktu respons chatbot untuk menjawab pertanyaan pengguna rata-rata harus di bawah 5 detik. |
| KNF-02 | **Keamanan** | - Password pengguna harus di-hash sebelum disimpan di database.
| | | - Komunikasi antara klien dan server harus dienkripsi menggunakan HTTPS.
| | | - API endpoint harus dilindungi dan hanya bisa diakses dengan token JWT yang valid. |
| KNF-03 | **Usabilitas** | Antarmuka pengguna harus intuitif, bersih, dan mudah digunakan bahkan oleh pengguna non-teknis. |
| KNF-04 | **Skalabilitas** | Arsitektur sistem harus dapat menangani peningkatan jumlah pengguna dan volume data di basis pengetahuan tanpa degradasi performa yang signifikan. |
| KNF-05 | **Ketersediaan** | Sistem harus tersedia untuk diakses oleh pengguna 99% dari waktu (high availability). |
| KNF-06 | **Kompatibilitas** | Aplikasi web harus berfungsi dengan baik di versi terbaru dari peramban web modern (Google Chrome, Mozilla Firefox, Safari). |
| KNF-07 | **Maintainability** | Kode sumber harus terstruktur dengan baik, terdokumentasi secukupnya, dan mudah untuk dimodifikasi atau dikembangkan di masa depan. |
