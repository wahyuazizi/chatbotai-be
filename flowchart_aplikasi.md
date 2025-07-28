# Flowchart Aplikasi Chatbot AI

Ini adalah flowchart yang menggambarkan alur kerja keseluruhan dari aplikasi, dengan menyertakan teknologi yang digunakan dan menunjukkan bahwa Admin harus login untuk mengakses fitur ingesti data.

```mermaid
graph TD
    subgraph Authentication [Wajib untuk Admin]
        A[Pengguna/Admin] --> H{Login};
        H --> I[Isi Form Login];
        I --> J["Verifikasi kredensial (Supabase, passlib)"];
        J -- Gagal --> I;
        J -- Berhasil --> K["Buat JWT Token (python-jose)"];
        K --> L{Cek Role Admin};
    end

    subgraph Chat_RAG [Alur Chat Publik]
        U0[Pengguna Mengakses Aplikasi] --> N[Masuk ke Halaman Chat];
        N --> O[User Mengajukan Pertanyaan];
        O --> Q["Terima di Endpoint (FastAPI)"];
        Q --> R["Buat Embedding (Azure OpenAI)"];
        R --> S["Cari Dokumen (Azure AI Search)"];
        S --> T["Gabungkan Konteks (LangChain)"];
        T --> U["Kirim ke LLM (Azure OpenAI)"];
        U --> V[Terima Jawaban dari LLM];
        V --> W[Tampilkan Jawaban ke User];
        W --> O;
    end

    subgraph Proses_Ingesti_Data [Alur Ingesti Data - Admin]
        Z1[Buka Halaman Ingest];
        Z1 --> Z2[Upload Dokumen];
        Z2 --> Z3["Panggil Endpoint Ingest (FastAPI)"];
        Z3 --> Z4["Muat & Pecah Dokumen (LangChain)"];
        Z4 --> Z5["Buat Embeddings (Azure OpenAI)"];
        Z5 --> Z6["Simpan di Vector Store (Azure AI Search)"];
        Z6 --> Z7[Proses Ingesti Selesai];
    end

    %% Koneksi Antar Alur
    L -- Ya --> Z1;
    L -- Tidak --> N; %% Pengguna non-admin diarahkan ke chat

    %% Koneksi Dependensi Teknis
    Z6-.->|Menyediakan Knowledge Base|S;

    style Authentication fill:#f9f,stroke:#333,stroke-width:2px
    style Chat_RAG fill:#ccf,stroke:#333,stroke-width:2px
    style Proses_Ingesti_Data fill:#cfc,stroke:#333,stroke-width:2px
```

### Cara Menggunakan

1.  **PENTING:** Salin **hanya kode Mermaid** di dalam blok di atas. Jangan sertakan baris ` ```mermaid ` atau ` ``` `.
2.  Tempelkan kode yang telah disalin ke editor yang mendukung Mermaid (seperti [Mermaid Live Editor](https://mermaid.live)).
3.  Flowchart akan secara otomatis digambar.

---

### Deskripsi Alur

1.  **Alur Chat Publik (Chat RAG)**
    *   Alur ini dapat diakses oleh siapa saja tanpa perlu login. Pengguna langsung masuk ke halaman chat dan dapat mulai bertanya.

2.  **Alur Autentikasi (Authentication)**
    *   Alur ini menjadi **wajib** bagi pengguna yang ingin mengakses fungsionalitas admin.
    *   Setelah login berhasil, sistem akan melakukan pengecekan peran (role).

3.  **Alur Ingesti Data (Admin)**
    *   Alur ini **hanya dapat diakses** setelah pengguna berhasil login dan terverifikasi sebagai **Admin**.
    *   Jika pengguna yang login bukan admin, mereka akan diarahkan ke halaman chat biasa.
