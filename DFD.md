
# Data Flow Diagram (DFD)

Dokumen ini menjelaskan aliran data dalam aplikasi Chatbot AI, dengan fokus pada integrasi autentikasi pengguna.

---

## Level 0: Diagram Konteks

Diagram ini menunjukkan interaksi antara sistem secara keseluruhan dengan entitas eksternal.

```
<< Pengguna >>
      |
      | 1. Permintaan Chat (Query, Session ID, Auth Token)
      v
+-----------------------+
|                       |
|   Sistem Chatbot AI   |
|       (Backend)       |
|                       |
+-----------------------+
      |
      | 2. Jawaban Chat (Answer, Sources, Session ID)
      v
<< Pengguna >>


<< Admin >>
      |
      | 3. Data untuk Ingest (PDF, URL)
      v
+-----------------------+
|                       |
|   Sistem Chatbot AI   |
|       (Backend)       |
|                       |
+-----------------------+
      |
      | 4. Status Ingest
      v
<< Admin >>
```

### Penjelasan Alur Data (Level 0)

1.  **Permintaan Chat**: Pengguna mengirimkan pertanyaan (`Query`), `Session ID` (jika ada), dan `Auth Token` (jika login) ke sistem.
2.  **Jawaban Chat**: Sistem memberikan jawaban (`Answer`), sumber referensi (`Sources`), dan `Session ID` kembali ke pengguna.
3.  **Data untuk Ingest**: Administrator mengirimkan data baru dalam bentuk file PDF atau URL untuk dipelajari oleh sistem.
4.  **Status Ingest**: Sistem memberikan konfirmasi atau status dari proses penyerapan data kepada Admin.

---

## Level 1: Diagram Rinci

Diagram ini memecah "Sistem Chatbot AI" menjadi proses-proses utama, penyimpanan data, dan interaksinya dengan layanan eksternal.

```
<< Pengguna >>
     |  
     | 1. Chat Request (Query, Session ID, Auth Token)
     v
+--------------------+
|                    |
| 1.0 API Endpoint   |
|    (chat.py)       |
|                    |
+---------+----------+
          | 2. (Query, Session ID, User ID)
          v
+---------+----------+
|                    |    3. Get History (Session ID, User ID)    +--------------------+
| 2.0 RAG Service    +------------------------------------------->| 3.0 Chat History   |
| (rag_service.py)   |                                            |   Service          |
+--------------------+<-------------------------------------------+--------------------+
          |           4. Formatted History                               | 5. DB Query
          | 6. Get Relevant Docs (Query)                                 v
          v                                                      { A. Chat History DB }
+---------+----------+                                             {    (Supabase)    }
|                    |                                                     ^
| 4.0 Vector Store   |<----------------------------------------------------+ 12. Save Messages
| (Azure AI Search)  |
+--------------------+
          |
          | 7. Relevant Docs
          v
+---------+----------+
|                    |
| 2.0 RAG Service    |  8. Prompt (History, Context, Query)
| (Lanjutan)         +-------------------------------------------> << B. Azure OpenAI LLM >>
+--------------------+<-------------------------------------------
          |           9. Generated Answer
          | 10. Save to History (User Query, AI Answer, User ID)
          v
+---------+----------+
| 3.0 Chat History   |
|   Service          |
+--------------------+
          |
          | 11. (OK)
          v
+---------+----------+
| 2.0 RAG Service    |
| (Final)            |
+---------+----------+
          |
          | 13. Final Response (Answer, Sources)
          v
+---------+----------+
| 1.0 API Endpoint   |
+--------------------+
          |
          | 14. HTTP Response (Answer, Sources, Session ID)
          v
     << Pengguna >>
```

### Komponen

*   **Proses (Persegi Panjang)**: Komponen sistem yang mentransformasikan data.
    *   `1.0 API Endpoint`: Menerima permintaan HTTP dan mengirimkan respons.
    *   `2.0 RAG Service`: Otak dari aplikasi, mengorkestrasi pengambilan data, pembuatan prompt, dan pemanggilan AI.
    *   `3.0 Chat History Service`: Mengelola logika untuk menyimpan dan mengambil riwayat percakapan dari database.
    *   `4.0 Vector Store`: Komponen yang bertanggung jawab untuk mencari dokumen yang relevan (retriever).
*   **Penyimpanan Data (Kurung Kurawal)**:
    *   `{A. Chat History DB}`: Database Supabase yang menyimpan semua pesan dari setiap sesi, termasuk `user_id` jika pengguna terautentikasi.
*   **Entitas Eksternal (Kurung Siku Ganda)**:
    *   `<< Pengguna >>`: Pengguna akhir yang berinteraksi dengan chatbot, bisa anonim atau terautentikasi.
    *   `<< B. Azure OpenAI LLM >>`: Model bahasa dari Azure yang menghasilkan jawaban.

### Penjelasan Alur Data (Level 1)

1.  **Request**: Pengguna mengirim `Chat Request` ke `API Endpoint`. Permintaan ini sekarang dapat menyertakan `Auth Token` jika pengguna login.
2.  **Validasi & Panggilan Service**: Endpoint memvalidasi `Auth Token` (jika ada) untuk mendapatkan `User ID`. Kemudian memanggil `RAG Service` dengan `Query`, `Session ID`, dan `User ID`.
3.  **Ambil Riwayat**: `RAG Service` meminta `Chat History Service` untuk mengambil riwayat obrolan. `Chat History Service` akan memprioritaskan pencarian berdasarkan `User ID` jika tersedia, atau `Session ID` untuk pengguna anonim.
4.  **Kirim Riwayat**: `Chat History Service` mengembalikan riwayat yang sudah diformat.
5.  **Query DB**: `Chat History Service` menjalankan query ke `Chat History DB` (Supabase) untuk mendapatkan pesan dari 24 jam terakhir, difilter berdasarkan `User ID` atau `Session ID`.
6.  **Ambil Dokumen**: `RAG Service` mengirim `Query` ke `Vector Store` (Azure AI Search) untuk mencari dokumen relevan.
7.  **Kirim Dokumen**: `Vector Store` mengembalikan dokumen yang paling relevan.
8.  **Kirim Prompt**: `RAG Service` menggabungkan riwayat obrolan, dokumen relevan, dan query pengguna menjadi sebuah *prompt* dan mengirimkannya ke `Azure OpenAI LLM`.
9.  **Terima Jawaban**: LLM mengembalikan jawaban yang dihasilkan.
10. **Simpan Riwayat**: `RAG Service` memanggil `Chat History Service` untuk menyimpan pertanyaan pengguna dan jawaban AI, termasuk `User ID` jika tersedia.
11. **Konfirmasi Simpan**: `Chat History Service` memberikan konfirmasi setelah pesan disimpan.
12. **Tulis ke DB**: `Chat History Service` menulis data pesan baru ke `Chat History DB`.
13. **Kirim Respons Internal**: `RAG Service` mengemas jawaban akhir dan sumbernya, lalu mengirimkannya kembali ke `API Endpoint`.
14. **Respons HTTP**: `API Endpoint` mengirimkan `HTTP Response` yang berisi jawaban, sumber, dan `Session ID` kembali ke Pengguna.
