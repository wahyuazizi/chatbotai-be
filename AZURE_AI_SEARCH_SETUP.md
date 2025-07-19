# Panduan Setup Azure AI Search untuk Chatbot

Dokumen ini memberikan panduan langkah demi langkah untuk membuat layanan Azure AI Search, mendapatkan kredensial yang diperlukan, dan mengkonfigurasi file `.env` proyek ini.

## Prasyarat

- Akun Azure dengan subscription yang aktif. Jika Anda belum punya, Anda bisa membuat akun gratis [di sini](https://azure.microsoft.com/free/).

---

## Langkah 1: Membuat Layanan Azure AI Search

1.  **Masuk ke Portal Azure:** Buka [portal.azure.com](https://portal.azure.com) dan masuk dengan akun Anda.

2.  **Buat Resource Baru:**
    - Di bar pencarian di bagian atas, ketik `Azure AI Search` dan pilih layanan tersebut dari daftar.
    - Klik tombol **"+ Create"** atau **"+ Add"**.

3.  **Konfigurasi Layanan:**
    - **Subscription:** Pilih subscription Azure Anda.
    - **Resource group:** Pilih resource group yang sudah ada atau buat yang baru (misalnya, `rg-chatbot-ai`).
    - **Service name:** Berikan nama yang unik secara global untuk layanan pencarian Anda (misalnya, `my-chatbot-search-service`). Nama ini akan menjadi bagian dari URL endpoint Anda.
    - **Location:** Pilih region Azure yang paling dekat dengan Anda atau pengguna Anda (misalnya, `East US 2` atau `Southeast Asia`).
    - **Pricing tier:** Untuk development atau proyek skala kecil, tier **Basic** atau **Free** (jika tersedia) sudah cukup. Tier `Free` hanya memperbolehkan 1 layanan per subscription.
    - Klik **"Review + create"**, lalu setelah validasi berhasil, klik **"Create"**.

Tunggu beberapa menit hingga proses deployment selesai.

---

## Langkah 2: Mendapatkan Kredensial (Endpoint & API Key)

Setelah layanan Anda berhasil di-deploy, ikuti langkah berikut untuk mendapatkan kredensial yang dibutuhkan oleh aplikasi.

1.  **Buka Layanan Search Anda:**
    - Navigasi ke resource group Anda dan klik pada layanan Azure AI Search yang baru saja Anda buat.
    - Atau, cari namanya di bar pencarian utama.

2.  **Dapatkan Endpoint URL:**
    - Di halaman **Overview** layanan, Anda akan menemukan **Url**.
    - Salin URL ini. Ini adalah nilai untuk `AZURE_AI_SEARCH_ENDPOINT`.
    - Contoh: `https://my-chatbot-search-service.search.windows.net`

3.  **Dapatkan API Key:**
    - Di menu navigasi sebelah kiri, di bawah bagian **"Settings"**, klik **"Keys"**.
    - Anda akan melihat dua jenis kunci: **Admin keys** dan **Query keys**. Untuk development dan ingesti data, kita memerlukan **Admin key**.
    - Salin salah satu dari **Primary admin key**. Ini adalah nilai untuk `AZURE_AI_SEARCH_KEY`.

---

## Langkah 3: Konfigurasi File `.env`

Sekarang, buka file `.env` di root direktori proyek Anda dan isi variabel-variabel berikut dengan nilai yang baru saja Anda dapatkan.

1.  **Buka file `.env`**.

2.  **Isi nilai-nilainya:**

    ```dotenv
    # ... (variabel lain)

    # Azure AI Search
    AZURE_AI_SEARCH_ENDPOINT="https_URL_DARI_LANGKAH_2"
    AZURE_AI_SEARCH_KEY="API_KEY_DARI_LANGKAH_2"
    AZURE_AI_SEARCH_INDEX_NAME="chatbot-index"
    ```

    - Ganti `https_URL_DARI_LANGKAH_2` dengan URL yang Anda salin.
    - Ganti `API_KEY_DARI_LANGKAH_2` dengan primary admin key yang Anda salin.
    - `AZURE_AI_SEARCH_INDEX_NAME` adalah nama untuk indeks vektor di dalam layanan search Anda. Anda bisa membiarkannya sebagai `chatbot-index`. LangChain akan secara otomatis membuat indeks dengan nama ini saat pertama kali Anda melakukan ingesti data.

3.  **Simpan file `.env`**.

---

Selesai! Aplikasi Anda sekarang siap untuk terhubung ke Azure AI Search. Anda bisa melanjutkan untuk menjalankan server FastAPI dan mulai melakukan ingesti data.
