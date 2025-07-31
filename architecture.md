
# Diagram Arsitektur Aplikasi

Dokumen ini menguraikan arsitektur teknis dari aplikasi chatbot, menyoroti komponen utama, layanan eksternal yang digunakan, dan alur interaksi di antara mereka.

---

## Diagram

```
+--------------------------------------------------------------------+
|                            Pengguna / Klien                        |
|                            (Frontend Web)                          |
+--------------------------------------------------------------------+
                   |                                      ^
                   | (1. Permintaan HTTP/S - API Call)    | (6. Respons JSON)
                   v                                      |
+--------------------------------------------------------------------+
|                  Aplikasi Backend (FastAPI Server)                 |
|--------------------------------------------------------------------|
| +------------------+   +---------------------+   +-----------------+ |
| |   API Endpoints  |-->|    Service Layer    |-->|   Core / Config |
| | (schemas, router)|   | (Logika Bisnis)     |   |  (Koneksi Klien)|
| +------------------+   +----------+----------+   +-----------------+ |
|                                   |                                  |
+--------------------------------------------------------------------+
       |           | (3. Simpan/Ambil Riwayat)         |           |
       |           +-----------------------------------+           |
       | (2. Proses RAG)                               |           | (4. Panggil Model AI)
       v                                               v           v
+-------------------------+   +----------------------------+   +-------------------+
|     Azure AI Search     |   |          Supabase          |   |   Azure OpenAI    |
|-------------------------|   |----------------------------|   |-------------------|
| - Vector Store          |   | - Database PostgreSQL      |   | - GPT (LLM)       |
| - Indexing & Retrieval  |   | - Penyimpanan Chat History |   | - Embeddings      |
+-------------------------+   +----------------------------+   +-------------------+
```

---

## Deskripsi Komponen

### 1. Pengguna / Klien (Frontend)
- **Teknologi**: Diasumsikan sebagai aplikasi web (React, Vue, Angular, dll.).
- **Tanggung Jawab**: 
    - Menyediakan antarmuka pengguna (UI) untuk berinteraksi dengan chatbot.
    - Mengelola status sesi (menyimpan `session_id` di `localStorage` atau `sessionStorage`).
    - Mengirim permintaan HTTP ke Backend API.
    - Menampilkan respons dari chatbot kepada pengguna.

### 2. Aplikasi Backend (FastAPI Server)
Merupakan inti dari sistem yang menangani semua logika dan komunikasi.

- **API Endpoints** (`app/api/`):
    - **Teknologi**: FastAPI `APIRouter`.
    - **Tanggung Jawab**: Menerima permintaan HTTP dari klien, memvalidasi data masuk menggunakan skema Pydantic (`app/schemas/`), dan meneruskan permintaan ke *Service Layer* yang sesuai.

- **Service Layer** (`app/services/`):
    - **Teknologi**: Class Python.
    - **Tanggung Jawab**: Berisi logika bisnis inti.
        - `RAGService`: Mengorkestrasi alur *Retrieval-Augmented Generation*. Ini melibatkan pengambilan dokumen relevan dari Azure AI Search, memformat prompt dengan konteks dan riwayat, serta memanggil model bahasa di Azure OpenAI.
        - `ChatHistoryService`: Mengelola interaksi dengan Supabase untuk menyimpan dan mengambil riwayat percakapan.

- **Core / Config** (`app/core/`):
    - **Teknologi**: Pydantic `BaseSettings`, Klien SDK (Supabase, Azure).
    - **Tanggung Jawab**: Mengelola konfigurasi aplikasi (kunci API, endpoint URL) dari *environment variables* dan menginisialisasi klien koneksi ke layanan eksternal.

### 3. Layanan Eksternal (PaaS - Platform as a Service)

- **Azure OpenAI**:
    - **Peran**: Penyedia Model AI.
    - **Layanan yang Digunakan**:
        - **Model Bahasa (LLM)**: Menghasilkan jawaban berdasarkan prompt yang diberikan oleh `RAGService`.
        - **Model Embeddings**: Mengubah potongan teks (dari dokumen yang di-*ingest*) menjadi representasi vektor numerik untuk disimpan dan dicari.

- **Azure AI Search**:
    - **Peran**: Vector Store & Search Engine.
    - **Tanggung Jawab**: Menyimpan vektor dari dokumen yang telah di-*embed*. Saat ada query, layanan ini melakukan pencarian kesamaan (similarity search) untuk menemukan dan mengembalikan potongan teks yang paling relevan dengan query pengguna.

- **Supabase**:
    - **Peran**: Penyimpanan Data Terstruktur.
    - **Tanggung Jawab**: Berfungsi sebagai database PostgreSQL untuk menyimpan riwayat percakapan (`chat_messages`). Menyediakan persistensi data sehingga sesi obrolan dapat dilanjutkan dan digunakan sebagai konteks tambahan.

## Alur Data Utama (Chat)

1.  **Permintaan**: Klien mengirimkan `query` dan `session_id` ke API Endpoint di server FastAPI.
2.  **Proses RAG**: `RAGService` dipanggil. Ia pertama-tama mengambil riwayat obrolan dari Supabase (melalui `ChatHistoryService`) dan kemudian mengambil dokumen relevan dari Azure AI Search.
3.  **Konteks**: Riwayat dan dokumen yang relevan digabungkan menjadi sebuah prompt yang kaya konteks.
4.  **Panggilan LLM**: Prompt dikirim ke model bahasa di Azure OpenAI.
5.  **Simpan & Respons**: Jawaban dari LLM diterima. Pertanyaan pengguna dan jawaban AI disimpan di Supabase. Jawaban akhir dikirim kembali ke klien.
6.  **Tampilan**: Klien menerima respons JSON dan menampilkannya di UI.
