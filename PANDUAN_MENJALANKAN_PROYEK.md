# Bab 4: Panduan Menjalankan Proyek

Proyek ini merupakan sebuah aplikasi chatbot cerdas yang dibangun dengan serangkaian teknologi modern untuk menyediakan fungsionalitas Retrieval-Augmented Generation (RAG). Bagian ini akan menjelaskan tumpukan teknologi yang digunakan serta panduan lengkap untuk menjalankan aplikasi.

## 4.1 Tumpukan Teknologi (Tech Stack)

Aplikasi ini dibangun menggunakan beberapa teknologi utama, yaitu:

*   **Python:** Sebagai bahasa pemrograman utama.
*   **FastAPI:** Kerangka kerja (framework) web modern berkinerja tinggi untuk membangun API dengan Python.
*   **Uvicorn:** Server ASGI (Asynchronous Server Gateway Interface) yang sangat cepat, digunakan untuk menjalankan aplikasi FastAPI.
*   **LangChain:** Kerangka kerja untuk mengembangkan aplikasi yang didukung oleh model bahasa (LLM), memfasilitasi integrasi antara berbagai komponen.
*   **Azure OpenAI:** Layanan dari Microsoft Azure yang menyediakan akses ke model bahasa canggih dari OpenAI untuk pemrosesan bahasa alami.
*   **Azure AI Search:** Layanan pencarian cloud dengan kemampuan AI bawaan yang digunakan untuk pengindeksan dan pencarian data dalam implementasi RAG.
*   **Supabase:** Platform open-source yang menyediakan basis data Postgres, otentikasi, dan penyimpanan, digunakan untuk mengelola data pengguna dan riwayat percakapan.
*   **Docker:** Platform untuk mengembangkan, mengirim, dan menjalankan aplikasi dalam kontainer, memastikan lingkungan yang konsisten di seluruh tahap pengembangan dan produksi.

## 4.2 Lingkungan Pengembangan

Proyek ini dikembangkan menggunakan bahasa pemrograman Python dengan framework FastAPI untuk membangun RESTful API. Untuk menjalankan proyek ini, diperlukan beberapa perangkat lunak dan konfigurasi lingkungan.

### 4.2.1 Perangkat Lunak yang Dibutuhkan

Pastikan perangkat lunak berikut telah terpasang di sistem Anda:

*   **Python 3.10+:** Bahasa pemrograman utama yang digunakan.
*   **Docker:** Untuk menjalankan aplikasi dalam kontainer.
*   **Pip:** Manajer paket untuk Python.

### 4.2.2 Konfigurasi Variabel Lingkungan

Aplikasi ini memerlukan beberapa kunci API dan konfigurasi yang disimpan dalam *environment variables*.

1.  Salin file `.env.example` menjadi file baru bernama `.env`:
    ```bash
    cp .env.example .env
    ```
2.  Buka file `.env` dan isi nilainya sesuai dengan kredensial yang Anda miliki dari layanan Azure, Supabase, dan lainnya.

    ```dotenv
    AZURE_OPENAI_API_KEY=<KUNCI_API_AZURE_OPENAI_ANDA>
    AZURE_OPENAI_ENDPOINT=<ENDPOINT_AZURE_OPENAI_ANDA>
    AZURE_OPENAI_API_VERSION=<VERSI_API_AZURE_OPENAI_ANDA>
    AZURE_OPENAI_DEPLOYMENT_NAME=<NAMA_DEPLOYMENT_ANDA>
    AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=<NAMA_DEPLOYMENT_CHAT_ANDA>

    # Supabase
    SUPABASE_URL=<URL_SUPABASE_ANDA>
    SUPABASE_KEY=<KUNCI_API_SUPABASE_ANDA>
    SUPABASE_JWT_SECRET=<RAHASIA_JWT_SUPABASE_ANDA>

    # Azure AI Search
    AZURE_AI_SEARCH_ENDPOINT=<ENDPOINT_AZURE_AI_SEARCH_ANDA>
    AZURE_AI_SEARCH_KEY=<KUNCI_AZURE_AI_SEARCH_ANDA>
    AZURE_AI_SEARCH_INDEX_NAME=<NAMA_INDEKS_ANDA>

    # App
    USER_AGENT=chatbot-ai/1.0
    ```

## 4.3 Instalasi Dependensi

Proyek ini memiliki beberapa dependensi pustaka Python yang tercantum dalam file `requirements.txt`.

1.  (Opsional, tapi direkomendasikan) Buat dan aktifkan *virtual environment* Python:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
2.  Instal semua dependensi yang dibutuhkan menggunakan pip:
    ```bash
    pip install -r requirements.txt
    ```

## 4.4 Menjalankan Aplikasi

Ada dua cara untuk menjalankan aplikasi ini: langsung menggunakan Uvicorn atau melalui Docker.

### 4.4.1 Menjalankan dengan Uvicorn (Lokal)

Uvicorn adalah server ASGI (Asynchronous Server Gateway Interface) yang ringan. Ini adalah cara standar untuk menjalankan aplikasi FastAPI selama pengembangan.

Jalankan perintah berikut dari direktori root proyek:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

*   `app.main:app`: Memberi tahu Uvicorn untuk menemukan objek `app` di dalam file `app/main.py`.
*   `--reload`: Server akan otomatis me-restart setiap kali ada perubahan pada kode.
*   `--host 0.0.0.0`: Membuat server dapat diakses dari luar container/mesin lokal.
*   `--port 8000`: Menjalankan server pada port 8000.

Aplikasi sekarang akan berjalan dan dapat diakses di `http://localhost:8000`.

### 4.4.2 Menjalankan dengan Docker

Docker memungkinkan aplikasi untuk dijalankan di dalam lingkungan yang terisolasi dan konsisten menggunakan `Dockerfile` yang telah disediakan.

#### 1. Membangun (Build) Docker Image

Langkah pertama adalah membangun *image* Docker dari `Dockerfile`. Beri nama *image* agar mudah dikenali, misalnya `chatbot-api`.

```bash
docker build -t chatbot-api .
```

*   `-t chatbot-api`: Memberi *tag* (nama) `chatbot-api` pada *image* yang dibangun.
*   `.`: Menunjukkan bahwa Docker harus mencari `Dockerfile` di direktori saat ini.

#### 2. Menjalankan Kontainer Docker

Setelah *image* berhasil dibangun, Anda dapat menjalankannya sebagai kontainer.

**Untuk Lingkungan Produksi:**

Jalankan kontainer di latar belakang (*detached mode*) dan terus berjalan meskipun terminal ditutup.

```bash
docker run -d --name chatbot-container --env-file .env -p 8000:8000 chatbot-api
```

*   `-d`: Menjalankan kontainer di *detached mode*.
*   `--name chatbot-container`: Memberi nama `chatbot-container` pada kontainer yang berjalan.
*   `--env-file .env`: Memuat *environment variables* dari file `.env`.
*   `-p 8000:8000`: Memetakan port 8000 di mesin Anda ke port 8000 di dalam kontainer.
*   `chatbot-api`: Nama *image* yang akan dijalankan.

**Untuk Lingkungan Pengembangan (dengan Hot-Reload):**

Jika Anda ingin menjalankan kontainer untuk pengembangan dengan *hot-reloading* (server otomatis restart saat ada perubahan kode), Anda perlu me-*mount* volume dari kode lokal Anda ke dalam kontainer.

```bash
docker run -d --name chatbot-dev-container --env-file .env -p 8000:8000 -v $(pwd):/app chatbot-api
```

*   `-v $(pwd):/app`: Me-*mount* direktori proyek saat ini (`$(pwd)`) ke direktori `/app` di dalam kontainer.

#### Mengelola Kontainer

*   **Melihat log kontainer:**
    ```bash
    docker logs -f chatbot-container
    ```
*   **Menghentikan kontainer:**
    ```bash
    docker stop chatbot-container
    ```
*   **Menghapus kontainer (setelah dihentikan):**
    ```bash
    docker rm chatbot-container
    ```

## 4.5 Mengakses Dokumentasi API

FastAPI secara otomatis menghasilkan dokumentasi interaktif untuk semua *endpoint* API. Setelah aplikasi berjalan (baik melalui Uvicorn maupun Docker), Anda dapat mengaksesnya melalui salah satu dari URL berikut:

*   **Swagger UI:** `http://localhost:8000/docs`
*   **ReDoc:** `http://localhost:8000/redoc`

Melalui antarmuka ini, Anda dapat melihat semua *endpoint* yang tersedia, parameter yang dibutuhkan, dan bahkan mencoba mengirim permintaan langsung dari browser.