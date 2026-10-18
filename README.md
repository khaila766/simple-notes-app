# simple-notes-app

Aplikasi Flask + MySQL sederhana untuk praktikum Komputasi Awan (Jenkins + Docker).

- `GET /` : pesan sambutan
- `GET /health` : cek koneksi database
- `GET /notes` : daftar catatan
- `POST /notes` : tambah catatan, body JSON `{"content": "teks"}`

Jalankan lokal: `docker compose up -d --build` lalu buka http://localhost:5000
