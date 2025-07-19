
# Cara Mendapatkan Kredensial Azure Databricks

Dokumen ini menjelaskan cara mendapatkan nilai untuk variabel lingkungan yang diperlukan untuk menghubungkan aplikasi ke Azure Databricks.

### 1. `DATABRICKS_HOST`

Ini adalah URL unik untuk workspace Azure Databricks Anda.

1.  Buka **portal Azure** di [portal.azure.com](https://portal.azure.com/).
2.  Cari dan buka layanan **Azure Databricks** Anda.
3.  Di halaman **Overview**, salin nilai dari kolom **URL**.
4.  Formatnya akan terlihat seperti ini: `https://adb-xxxxxxxxxxxxxxxx.xx.azuredatabricks.net`

### 2. `DATABRICKS_TOKEN`

Ini adalah *Personal Access Token* (PAT) yang digunakan untuk autentikasi API. Token ini sangat rahasia.

1.  Masuk ke workspace Databricks Anda (menggunakan `DATABRICKS_HOST`).
2.  Klik nama pengguna Anda di pojok kanan atas, lalu pilih **User Settings**.
3.  Buka tab **Developer**.
4.  Di bagian **Access tokens**, klik tombol **Generate new token**.
5.  Berikan deskripsi singkat (komentar) untuk token tersebut (misalnya, "koneksi-chatbot-ai").
6.  Atur masa berlaku token sesuai kebutuhan.
7.  Klik **Generate**.
8.  **PENTING:** Salin token yang ditampilkan dan simpan di tempat yang aman. Anda tidak akan bisa melihatnya lagi setelah dialog ini ditutup.

**PERINGATAN:** Perlakukan token ini seperti kata sandi. Jangan pernah menyimpannya langsung di dalam kode atau membagikannya.

### 3. `DATABRICKS_INDEX_NAME`

Ini adalah nama lengkap dari *Vector Search Index* yang digunakan oleh aplikasi.

1.  Di workspace Databricks Anda, buka **Catalog Explorer** dari menu di sebelah kiri.
2.  Cari *Vector Search Index* yang relevan dengan proyek ini.
3.  Salin nama lengkap indeks, yang biasanya memiliki format tiga bagian: `<nama_katalog>.<nama_skema>.<nama_indeks>`.

Jika indeks belum ada, Anda mungkin perlu membuatnya terlebih dahulu. Lihat `databricks_ingestion_notebook.py` atau `DATABRICKS_AUTOMATION_GUIDE.md` untuk petunjuk lebih lanjut.

### Konfigurasi File `.env`

Setelah mendapatkan semua nilai di atas, buat file `.env` di direktori utama proyek dengan menyalin dari `.env.example`, lalu isi nilainya seperti contoh di bawah ini:

```bash
# /home/azizi/chatbotai-be/.env

DATABRICKS_HOST="<URL_WORKSPACE_ANDA>"
DATABRICKS_TOKEN="<TOKEN_ANDA>"
DATABRICKS_INDEX_NAME="<NAMA_LENGKAP_INDEKS_ANDA>"
```
