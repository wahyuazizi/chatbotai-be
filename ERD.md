
# Entity-Relationship Diagram (ERD) - Chat History

Diagram ini menggambarkan struktur database untuk menyimpan riwayat percakapan chatbot, yang terintegrasi dengan sistem autentikasi pengguna Supabase.

## Diagram

```
+---------------------+       +---------------------+
|     auth.users      |       |  public.chat_messages |
| (Tabel Supabase)    |       +---------------------+
+---------------------+       | id (PK)             |
| id (PK)             |------>| user_id (FK)        |
| email               |       | session_id          |
| ...                 |       | role                |
+---------------------+       | content             |
                              | created_at          |
                              +---------------------+
```

---

## Deskripsi Detail

### Tabel: `public.chat_messages`

Tabel ini adalah inti dari sistem riwayat obrolan. Setiap baris mewakili satu pesan yang dikirim oleh pengguna atau oleh asisten AI.

| Nama Kolom   | Tipe Data                 | Deskripsi                                                                                             | Kendala (Constraints)      |
|--------------|---------------------------|-------------------------------------------------------------------------------------------------------|----------------------------|
| `id`         | `UUID`                    | Kunci utama (Primary Key) unik untuk setiap pesan. Dibuat secara otomatis.                            | `PRIMARY KEY`, `NOT NULL`  |
| `created_at` | `TIMESTAMP WITH TIME ZONE`| Waktu kapan pesan dibuat. Otomatis diisi dengan waktu saat ini.                                         | `DEFAULT now()`, `NOT NULL`|
| `session_id` | `UUID`                    | Pengidentifikasi unik untuk satu sesi browser. Membantu membedakan tab/perangkat yang berbeda dari pengguna yang sama. | `NOT NULL`                 |
| `role`       | `TEXT`                    | Menandakan pengirim pesan. Nilainya bisa 'user' atau 'assistant'.                                       | `NOT NULL`                 |
| `content`    | `TEXT`                    | Isi teks dari pesan yang dikirim.                                                                     | `NOT NULL`                 |
| `user_id`    | `UUID`                    | Kunci asing (Foreign Key) yang merujuk ke `auth.users.id`. Menautkan pesan ke pengguna yang terautentikasi. | `FOREIGN KEY (auth.users.id)`   |

### Tabel: `auth.users` (Disediakan oleh Supabase)

Ini adalah tabel bawaan dari Supabase Auth yang menyimpan data semua pengguna yang terdaftar.

| Nama Kolom | Tipe Data | Deskripsi                                       | Kendala (Constraints) |
|------------|-----------|-------------------------------------------------|-----------------------|
| `id`       | `UUID`    | Kunci utama (Primary Key) unik untuk setiap pengguna. | `PRIMARY KEY`         |
| `email`    | `TEXT`    | Alamat email pengguna.                          | `UNIQUE`, `NOT NULL`  |
| `...`      | `...`     | Kolom lain yang dikelola oleh Supabase (misalnya, `encrypted_password`, `role`, `user_metadata`). |                       |

### Hubungan

*   **`auth.users` ke `public.chat_messages` (Satu-ke-Banyak)**
    *   Satu pengguna (`user`) dapat memiliki banyak pesan (`chat_messages`).
    *   Hubungan ini diimplementasikan melalui kolom `chat_messages.user_id` yang merujuk ke `auth.users.id`.
    *   Untuk pengguna anonim, `user_id` akan bernilai `NULL`.
