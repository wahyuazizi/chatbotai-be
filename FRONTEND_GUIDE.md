# Panduan Frontend: Mengimplementasikan Chat dengan Sesi dan Autentikasi Pengguna

Dokumen ini menjelaskan bagaimana frontend harus berinteraksi dengan API chat backend untuk mendukung percakapan yang berkelanjutan menggunakan `session_id` dan mengintegrasikan autentikasi pengguna.

---

## Konsep Utama: `session_id` dan `Auth Token`

- **`session_id`**: Pengidentifikasi unik untuk satu sesi percakapan. Frontend bertanggung jawab untuk menyimpan ID ini dan mengirimkannya kembali pada setiap permintaan. Ini penting untuk pengguna anonim atau untuk membedakan sesi dari perangkat/tab yang berbeda.
- **`Auth Token` (JWT)**: Jika pengguna sudah login, frontend harus menyertakan token JWT yang diperoleh dari proses autentikasi Supabase. Token ini memungkinkan backend untuk mengidentifikasi pengguna dan menautkan riwayat obrolan ke `user_id` mereka.

Backend sekarang dapat menangani **keduanya**: pengguna anonim (hanya dengan `session_id`) dan pengguna terautentikasi (dengan `Auth Token` dan `session_id`).

## Alur Kerja Frontend

Untuk mengelola sesi dan autentikasi, frontend harus mengikuti alur kerja berikut:

1.  **Simpan `session_id`**: Gunakan `localStorage` atau `sessionStorage` di browser untuk menyimpan `session_id`.
2.  **Dapatkan `Auth Token`**: Jika pengguna login, dapatkan token JWT dari Supabase Auth (misalnya, `supabase.auth.getSession().access_token`).
3.  **Kirim `session_id` dan `Auth Token`**: Saat pengguna mengirim pesan, baca `session_id` dari penyimpanan dan sertakan dalam *body* permintaan API. Jika ada `Auth Token`, sertakan juga dalam header `Authorization`.
4.  **Terima dan Simpan Ulang `session_id`**: Respons dari API akan *selalu* berisi `session_id`. Simpan kembali nilai ini ke `localStorage`, menimpa yang lama. Ini penting untuk menangani pembuatan sesi baru.

## Kontrak API

Berikut adalah detail dari request dan response JSON.

### 1. Request Body

Kirim permintaan `POST` ke endpoint `/api/v1/chat`.

```json
{
  "query": "Pertanyaan dari pengguna...",
  "session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" 
}
```

- **`query`** (string, wajib): Pertanyaan yang diketik oleh pengguna.
- **`session_id`** (string, opsional): Kirim `session_id` yang tersimpan. Jika ini adalah pesan pertama atau sesi telah dihapus, biarkan nilainya `null` atau jangan sertakan *key*-nya.

### 2. Request Headers

Jika pengguna login, sertakan header `Authorization`:

```
Authorization: Bearer <YOUR_SUPABASE_JWT_TOKEN>
```

### 3. Response Body

Anda akan menerima respons dengan struktur berikut:

```json
{
  "answer": "Jawaban yang dihasilkan oleh AI...",
  "sources": [
    {
      "source": "nama_file.pdf",
      "content": "Potongan teks dari sumber..."
    }
  ],
  "session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "debug_info": null
}
```

- **`answer`** (string): Jawaban dari chatbot untuk ditampilkan di UI.
- **`sources`** (array): Daftar sumber yang digunakan untuk menghasilkan jawaban.
- **`session_id`** (string): **Selalu ambil nilai ini dan simpan di `localStorage` setelah setiap panggilan berhasil.**

---

## Contoh Implementasi (JavaScript)

Berikut adalah contoh fungsi JavaScript yang menunjukkan cara menangani logika sesi dan autentikasi.

```javascript
// Nama key untuk menyimpan session_id di localStorage
const SESSION_ID_KEY = 'chatSessionId';

/**
 * Mengirim pesan ke backend dan mengelola sesi.
 * @param {string} userMessage - Pesan dari input pengguna.
 * @returns {Promise<object>} - Objek respons dari API.
 */
async function sendMessage(userMessage) {
  // 1. Baca session_id yang ada dari localStorage
  const currentSessionId = localStorage.getItem(SESSION_ID_KEY);

  // 2. Dapatkan Auth Token dari Supabase (jika pengguna login)
  let authToken = null;
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (session) {
      authToken = session.access_token;
    }
  } catch (error) {
    console.error("Error getting Supabase session:", error);
  }

  const apiEndpoint = '/api/v1/chat'; // Ganti dengan URL API Anda jika perlu

  const headers = {
    'Content-Type': 'application/json',
  };

  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  try {
    const response = await fetch(apiEndpoint, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({
        query: userMessage,
        session_id: currentSessionId, // Kirim ID yang ada, atau null jika tidak ada
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // 3. Ambil session_id dari respons dan simpan kembali
    // Ini akan menangani sesi baru dan sesi yang sudah ada secara otomatis
    if (data.session_id) {
      localStorage.setItem(SESSION_ID_KEY, data.session_id);
    }

    // 4. Kembalikan data untuk ditampilkan di UI
    return data;

  } catch (error) {
    console.error("Error sending message:", error);
    // Handle error di UI (misalnya, tampilkan pesan kesalahan)
    throw error;
  }
}

// Contoh cara memanggil fungsi ini
document.getElementById('sendButton').addEventListener('click', async () => {
  const input = document.getElementById('chatInput');
  const message = input.value;
  if (!message) return;

  // Tampilkan pesan pengguna di UI
  // ...

  try {
    const result = await sendMessage(message);
    
    // Tampilkan jawaban AI di UI
    // console.log("AI Answer:", result.answer);
    // ...

  } finally {
    input.value = ''; // Kosongkan input
  }
});

// Opsional: Tambahkan tombol untuk mereset percakapan
document.getElementById('resetButton').addEventListener('click', () => {
  localStorage.removeItem(SESSION_ID_KEY);
  // Hapus riwayat chat dari tampilan UI
  // ...
  console.log('Chat session has been reset.');
});
```