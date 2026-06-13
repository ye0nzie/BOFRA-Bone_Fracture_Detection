# 🦴 BOFRA - Bone Fracture Detection Web App

BOFRA (Bone Fracture Detection) adalah aplikasi berbasis web yang dibangun menggunakan **Flask (Python)** untuk mendeteksi patah tulang (fracture) pada hasil gambar sinar-X (X-Ray). Proyek ini menggabungkan model arsitektur Deep Learning untuk klasifikasi dan deteksi objek secara cepat dan akurat.



 Fitur Utama
* **Deteksi Otomatis:** Mengunggah gambar X-Ray dan mendapatkan hasil prediksi patah tulang secara instan.
* **Dual-Model Support:** Menggunakan arsitektur CNN khusus (`.h5`) dan model YOLO/PyTorch (`.pt`) untuk akurasi optimal.
* **User-Friendly Interface:** Tampilan web sederhana dan responsif yang mudah digunakan oleh tenaga medis maupun pengguna umum.


 Download Trained Model
Karena ukuran file bobot model (weights) terlalu besar untuk di-upload langsung ke GitHub, Anda harus mengunduhnya secara manual melalui tautan Google Drive di bawah ini:

👉 **[Download Model Files (best.pt & cnn_best.h5) di Sini](https://drive.google.com/drive/folders/1aF51zKhaiQ_gJwBarofuJEVYzdFlEdA-?usp=sharing)**

> ⚠️ **PENTING:** Setelah diunduh, buat folder baru bernama `model` di direktori utama proyek ini, lalu masukkan file `best.pt` dan `cnn_best.h5` ke dalam folder tersebut sebelum menjalankan aplikasi.
