# Telegram Manager

Aplikasi desktop untuk mengelola akun Telegram menggunakan Python dan Flet.

## Fitur

- Membuat dan mengelola multiple sesi Telegram
- Melihat riwayat chat
- Mengubah username dan nama profil
- Mengelola channel dan grup
- Keluar dari semua channel sekaligus
- Menghapus sesi

## Persyaratan

### Menggunakan Docker (Direkomendasikan)
- Docker
- Docker Compose

### Tanpa Docker
- Python 3.8+
- Telegram API credentials (API ID dan API Hash)

## Instalasi

### Menggunakan Docker (Direkomendasikan)

1. Clone repository:
```bash
git clone https://github.com/[username]/telegram-manager.git
cd telegram-manager
```

2. Buat file `.env` dan isi dengan API credentials:
```
API_ID=your_api_id
API_HASH=your_api_hash
```

3. Build dan jalankan dengan Docker Compose:
```bash
docker-compose up --build
```

### Tanpa Docker

1. Clone repository:
```bash
git clone https://github.com/[username]/telegram-manager.git
cd telegram-manager
```

2. Buat virtual environment:
```bash
python -m venv myenv
source myenv/bin/activate  # Linux/Mac
myenv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements-frontend.txt
pip install -r requirements-backend.txt
```

4. Buat file `.env` dan isi dengan API credentials:
```
API_ID=your_api_id
API_HASH=your_api_hash
```

## Penggunaan

### Dengan Docker
Aplikasi akan berjalan di:
- Frontend: http://localhost:8550
- Backend: http://localhost:5000

### Tanpa Docker
1. Jalankan server backend:
```bash
python server.py
```

2. Di terminal lain, jalankan frontend:
```bash
python main.py
```

3. Dapatkan API credentials dari https://my.telegram.org

## Struktur Project

```
telegram-manager/
├── lib/
│   ├── models/
│   │   └── session.py
│   ├── screens/
│   │   └── home_screen.py
│   └── services/
│       └── telegram_manager.py
├── sessions/          # Folder untuk menyimpan sesi
├── chat/             # Folder untuk menyimpan riwayat chat
├── main.py           # Frontend entry point
├── server.py         # Backend server
├── Dockerfile        # Konfigurasi Docker
├── docker-compose.yml # Konfigurasi Docker Compose
└── requirements.txt  # Dependencies
```

## Kontribusi

1. Fork repository
2. Buat branch baru (`git checkout -b fitur-baru`)
3. Commit perubahan (`git commit -am 'Menambahkan fitur baru'`)
4. Push ke branch (`git push origin fitur-baru`)
5. Buat Pull Request

## Lisensi

MIT License - lihat file [LICENSE](LICENSE) untuk detail.
