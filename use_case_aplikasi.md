# Dokumen Use Case Aplikasi Chatbot AI

Dokumen ini menjelaskan fungsionalitas sistem dari perspektif pengguna (aktor). Setiap use case mendefinisikan interaksi spesifik antara aktor dan sistem untuk mencapai tujuan tertentu.

**Aktor:**
*   **Pengguna Baru:** Seseorang yang belum memiliki akun.
*   **Pengguna Terdaftar:** Seseorang yang sudah memiliki akun dan telah login.
*   **Administrator:** Pengguna dengan hak akses khusus untuk mengelola sistem, termasuk basis pengetahuan (knowledge base).
*   **Sistem:** Aplikasi chatbot itu sendiri.

---

### UC-01: Registrasi Pengguna Baru

| Field | Deskripsi |
| :--- | :--- |
| **Use Case** | Registrasi Pengguna Baru |
| **Aktor** | Pengguna Baru |
| **Deskripsi** | Aktor membuat akun baru untuk dapat mengakses fitur aplikasi. |
| **Pre-kondisi** | Aktor berada di halaman registrasi. |
| **Post-kondisi** | Akun baru untuk aktor tersimpan di database Sistem. Aktor diarahkan ke halaman login. |
| **Alur Utama** | 1. Aktor mengisi form registrasi (username, email, password).
| | 2. Aktor menekan tombol "Daftar".
| | 3. Sistem memvalidasi data yang dimasukkan.
| | 4. Sistem membuat akun baru dan menyimpannya ke database.
| | 5. Sistem menampilkan pesan sukses dan mengarahkan aktor ke halaman login. |
| **Alur Alternatif** | **3a. Data tidak valid:** Sistem menampilkan pesan error (misal: "Email tidak valid"). Aktor tetap di halaman registrasi.
| | **4a. Username atau email sudah ada:** Sistem menampilkan pesan error. Aktor tetap di halaman registrasi untuk memperbaiki isian. |

---

### UC-02: Login Pengguna

| Field | Deskripsi |
| :--- | :--- |
| **Use Case** | Login Pengguna |
| **Aktor** | Pengguna Baru, Pengguna Terdaftar |
| **Deskripsi** | Aktor masuk ke dalam aplikasi menggunakan kredensial yang sudah terdaftar. |
| **Pre-kondisi** | Aktor memiliki akun dan berada di halaman login. |
| **Post-kondisi** | Aktor berhasil diautentikasi, sesi dibuat, dan diarahkan ke halaman chat utama. |
| **Alur Utama** | 1. Aktor memasukkan username dan password.
| | 2. Aktor menekan tombol "Login".
| | 3. Sistem memverifikasi kredensial dengan data di database.
| | 4. Sistem membuat token sesi (JWT) untuk aktor.
| | 5. Sistem mengarahkan aktor ke halaman chat. |
| **Alur Alternatif** | **3a. Kredensial salah:** Sistem menampilkan pesan error ("Username atau password salah"). Aktor tetap di halaman login. |

---

### UC-03: Mengajukan Pertanyaan ke Chatbot (RAG)

| Field | Deskripsi |
| :--- | :--- |
| **Use Case** | Mengajukan Pertanyaan ke Chatbot |
| **Aktor** | Pengguna Terdaftar |
| **Deskripsi** | Aktor berinteraksi dengan chatbot untuk mendapatkan jawaban berdasarkan basis pengetahuan yang ada. |
| **Pre-kondisi** | Aktor sudah login dan berada di halaman chat. |
| **Post-kondisi** | Aktor menerima jawaban dari Sistem dan dapat melanjutkan percakapan. |
| **Alur Utama** | 1. Aktor mengetik pertanyaan di kolom input chat.
| | 2. Aktor mengirim pertanyaan.
| | 3. Sistem menerima pertanyaan dan memprosesnya melalui alur RAG:
| |    a. Membuat embedding dari pertanyaan.
| |    b. Mencari dokumen relevan di Vector Store.
| |    c. Menggabungkan pertanyaan dengan konteks dari dokumen.
| |    d. Mengirim prompt yang diperkaya ke LLM.
| | 4. Sistem menerima jawaban dari LLM.
| | 5. Sistem menampilkan jawaban di antarmuka chat. |
| **Alur Alternatif** | **3b. Tidak ditemukan dokumen relevan:** Sistem memberikan jawaban standar (misal: "Maaf, saya tidak memiliki informasi mengenai hal tersebut."). |

---

### UC-04: Ingesti Dokumen ke Basis Pengetahuan

| Field | Deskripsi |
| :--- | :--- |
| **Use Case** | Ingesti Dokumen ke Basis Pengetahuan |
| **Aktor** | Administrator |
| **Deskripsi** | Aktor menambahkan dokumen baru ke dalam basis pengetahuan agar dapat digunakan oleh RAG. |
| **Pre-kondisi** | Administrator sudah login dan memiliki akses ke panel ingesti. |
| **Post-kondisi** | Dokumen baru telah diproses dan disimpan di Vector Store, siap untuk digunakan dalam pencarian. |
| **Alur Utama** | 1. Administrator mengakses halaman/endpoint ingesti.
| | 2. Administrator mengunggah file dokumen (misal: PDF, TXT).
| | 3. Administrator memulai proses ingesti.
| | 4. Sistem memuat dokumen, memecahnya menjadi beberapa bagian (chunks), membuat embeddings, dan menyimpannya ke Vector Store.
| | 5. Sistem memberikan notifikasi bahwa proses ingesti berhasil. |
| **Alur Alternatif** | **2a. Format file tidak didukung:** Sistem menolak file dan menampilkan pesan error.
| | **4a. Proses ingesti gagal:** Sistem mencatat error dan memberikan notifikasi kegagalan kepada Administrator. |
