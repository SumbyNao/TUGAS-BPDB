# PPDB SMK Karya Bangsa

Sistem Penerimaan Peserta Didik Baru (PPDB) Online untuk SMK Karya Bangsa. Aplikasi web ini dibangun menggunakan Flask framework dan Bootstrap untuk memudahkan proses pendaftaran siswa baru.

## Fitur

### Calon Siswa
- Registrasi akun dan verifikasi email
- Pengisian formulir pendaftaran online
- Upload berkas persyaratan:
  - Kartu Keluarga
  - Akta Kelahiran  
  - Rapor
  - Surat Keterangan Lulus/SKHUN
- Pembayaran biaya pendaftaran
- Tracking status pendaftaran
- Pengumuman hasil seleksi

### Admin
- Manajemen data pendaftar
- Verifikasi berkas dan pembayaran
- Pengelolaan pengumuman
- Generate hasil seleksi
- Export data pendaftar
- Statistik dan laporan

## Teknologi

### Backend
- Python 3.12
- Flask Web Framework
- SQLAlchemy ORM 
- Flask-Login untuk autentikasi
- Flask-Mail untuk notifikasi email

### Frontend
- Bootstrap 5
- jQuery 
- DataTables
- Font Awesome icons

### Database
- MySQL/PostgreSQL database

## Prerequisites

Make sure you have installed:
- Python 3.12 or higher
- pip (Python package manager)
- MySQL/PostgreSQL server

## Dependencies

Main Python packages:
```bash
Flask==2.0.1
Flask-SQLAlchemy==2.5.1
Flask-Login==0.5.0
Flask-Mail==0.9.1
Flask-WTF==0.15.1
SQLAlchemy==1.4.23
PyMySQL==1.0.2
python-dotenv==0.19.0
```

Frontend libraries (included via CDN):
```html
<!-- Bootstrap 5 -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">

<!-- jQuery -->
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>

<!-- DataTables -->
<link href="https://cdn.datatables.net/1.11.3/css/dataTables.bootstrap5.min.css" rel="stylesheet">
<script src="https://cdn.datatables.net/1.11.3/js/jquery.dataTables.min.js"></script>

<!-- Font Awesome -->
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
```

## Screenshots

### Halaman Login
![Login Page](docs/images/login.png)
Halaman login untuk siswa dan admin sistem PPDB.

### Dashboard Siswa
![Student Dashboard](docs/images/dashboard-siswa.png)
Dashboard siswa menampilkan progress pendaftaran dan pengumuman terbaru.

### Form Pendaftaran 
![Registration Form](docs/images/form-daftar.png)
Form pengisian data diri dan upload berkas persyaratan.

### Upload Berkas
![Document Upload](docs/images/upload-berkas.png)
Halaman upload berkas persyaratan seperti ijazah, SKHUN, dan dokumen lainnya.

### Informasi Pembayaran
![Payment Information](docs/images/pembayaran.png)
Informasi biaya pendaftaran dan panduan pembayaran.

### Status Pendaftaran
![Registration Status](docs/images/status-pendaftaran.png)
Tracking status proses pendaftaran siswa.

### Dashboard Admin
![Admin Dashboard](docs/images/dashboard-admin.png)
Dashboard admin untuk monitoring dan manajemen sistem PPDB.

### Manajemen Pendaftar
![Applicant Management](docs/images/management-pendaftar.png)
Halaman admin untuk verifikasi berkas dan data pendaftar.

### Verifikasi Pembayaran
![Payment Verification](docs/images/verifikasi-pembayaran.png)
Panel admin untuk verifikasi bukti pembayaran pendaftar.

### Pengumuman
![Announcements](docs/images/pengumuman.png)
Manajemen pengumuman dan informasi penting PPDB.

### Laporan dan Statistik
![Reports](docs/images/laporan.png)
Statistik dan laporan pendaftaran dalam bentuk grafik dan tabel.

### Pengaturan Sistem
![System Settings](docs/images/pengaturan.png)
Konfigurasi sistem seperti jadwal, kuota, dan parameter lainnya.
