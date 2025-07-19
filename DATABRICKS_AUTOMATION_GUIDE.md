# Panduan Konfigurasi Otomatisasi Ingesti di Databricks

**Tujuan:** Menjalankan notebook ingesti data secara otomatis dan terjadwal menggunakan Databricks Jobs.

**Prasyarat:**
*   Anda memiliki akses ke Databricks Workspace.
*   Anda memiliki hak untuk membuat *secrets*, *notebooks*, dan *jobs*.

---

### Langkah 1: Simpan Kredensial dengan Aman (Databricks Secrets)

Jangan pernah menulis kredensial langsung di dalam kode. Gunakan Databricks Secrets untuk keamanan maksimal.

1.  **Buka Terminal Lokal Anda** (bukan di Gemini) dan pastikan Anda telah menginstal dan mengkonfigurasi [Databricks CLI](https://docs.databricks.com/en/dev-tools/cli/index.html).

2.  **Buat Secret Scope**: Scope adalah wadah untuk menyimpan sekumpulan *secrets*. Jalankan perintah ini di terminal lokal Anda:
    ```bash
    databricks secrets create-scope --scope chatbot-secrets
    ```

3.  **Tambahkan Secrets**: Tambahkan semua kunci yang dibutuhkan oleh notebook. Ganti `"NILAI_..._ANDA"` dengan nilai yang sesuai dari file `.env` Anda.
    ```bash
    # Kunci API untuk Azure OpenAI
    databricks secrets put --scope chatbot-secrets --key azureOpenaiApiKey --string-value "NILAI_AZURE_OPENAI_API_KEY_ANDA"

    # Endpoint untuk Azure OpenAI
    databricks secrets put --scope chatbot-secrets --key azureOpenaiEndpoint --string-value "NILAI_AZURE_OPENAI_ENDPOINT_ANDA"

    # Host untuk Databricks Workspace Anda
    databricks secrets put --scope chatbot-secrets --key databricksHost --string-value "NILAI_DATABRICKS_HOST_ANDA"

    # Token untuk otentikasi ke Databricks API
    databricks secrets put --scope chatbot-secrets --key databricksToken --string-value "NILAI_DATABRICKS_TOKEN_ANDA"
    ```

---

### Langkah 2: Impor Notebook ke Databricks

1.  Buka Databricks Workspace Anda.
2.  Di panel navigasi kiri, klik **Workspace**.
3.  Pilih direktori tempat Anda ingin menyimpan notebook (misalnya, di bawah `Users/nama_anda@email.com/`).
4.  Klik ikon tiga titik di sebelah kanan nama direktori, lalu pilih **Import**.
5.  Pilih **File** dan unggah file `databricks_ingestion_notebook.py` yang ada di proyek ini.

---

### Langkah 3: (Opsional) Unggah File PDF ke DBFS

Jika Anda ingin memproses file PDF, Anda harus mengunggahnya ke Databricks File System (DBFS).

1.  Di panel navigasi kiri, klik **Data**.
2.  Pilih tab **DBFS**.
3.  Navigasikan ke direktori `FileStore` dan buat folder baru, misalnya `chatbot_data`.
4.  Unggah file-file PDF Anda ke dalam direktori `/FileStore/chatbot_data/`. Notebook sudah dikonfigurasi untuk membaca dari path ini.

---

### Langkah 4: Buat dan Jadwalkan Databricks Job

Ini adalah langkah terakhir untuk mengotomatiskan eksekusi notebook.

1.  Di panel navigasi kiri, klik **Workflows**.
2.  Klik tombol **Create Job**.
3.  **Beri nama Job Anda**: Misalnya, `Ingesti Data Chatbot Harian`.
4.  **Pilih Notebook**: Di bagian **Task**, klik **Select notebook**, lalu cari dan pilih notebook yang baru saja Anda impor.
5.  **Pilih Cluster**: Pilih cluster yang akan menjalankan job ini. Anda bisa menggunakan cluster yang sudah ada atau membuat yang baru sesuai kebutuhan.
6.  **Atur Jadwal (Schedule)**:
    *   Klik tombol **Edit schedule**.
    *   Atur frekuensi yang Anda inginkan (misalnya, `Every 1 Day` pada jam `02:00`).
    *   Pilih zona waktu yang sesuai.
    *   Klik **Confirm**.
7.  **Simpan Job**: Klik tombol **Create** di bagian bawah halaman.

**Selesai!** Databricks sekarang akan secara otomatis menjalankan notebook ingesti data Anda sesuai jadwal. Proses ini akan menjaga data di Vector Search Index Anda tetap segar dan siap digunakan oleh aplikasi FastAPI Anda.
