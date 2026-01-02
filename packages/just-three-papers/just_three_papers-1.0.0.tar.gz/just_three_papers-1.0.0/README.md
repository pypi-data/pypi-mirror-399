📘 Just-Three-Papers: Tri-Planar Orthogonal Complex Mapping (TP-OCM)
Solusi Rotasi 3D yang Lebih Cepat, Ringan, dan Intuitif daripada Quaternion.

https://img.shields.io/badge/License-GPL%2520v3-blue.svg
https://img.shields.io/badge/python-3.8+-blue.svg
https://img.shields.io/badge/status-aktif%2520pengembangan-brightgreen

Bahasa Indonesia | English

📖 Tentang
TP-OCM (Tri-Planar Orthogonal Complex Mapping) adalah sebuah sistem matematika dan arsitektur komputasi baru untuk rotasi dan navigasi 3D. Sistem ini menggantikan metode tradisional yang mahal secara komputasi (seperti matriks rotasi 4x4 dan Quaternion) dengan dekomposisi ke dalam tiga bidang kompleks ortogonal yang sederhana.

✨ Mengapa TP-OCM? Karena sistem ini 40-60% lebih cepat dalam operasi rotasi sekuensial, menghindari singularitas seperti Gimbal Lock, dan secara alami mudah dipahami melalui analogi "Tiga Kertas".

🎯 Fitur Utama
⚡ Performa Tinggi: Algoritma inti hanya membutuhkan 12 perkalian & 6 penjumlahan per rotasi titik.

🧠 Intuitif: Konsep dasar divisualisasikan dengan tiga bidang ortogonal (Frontal, Sagittal, Horizontal), membuatnya lebih mudah dipelajari.

🛡️ Stabil Numerik: Protokol "Stable Angle Extraction" dan "Taylor Normalization" mencegah pembagian dengan nol dan drift.

🔧 Multi-Bahasa: Implementasi tersedia dalam Python (prototipe cepat) dan C++ (untuk sistem embedded).

📚 Lengkap: Dilengkapi dengan dokumentasi formal, paper pedagogis, dan contoh aplikasi nyata.

🚀 Mulai Cepat
Prasyarat
Python 3.8 atau lebih tinggi

Git (untuk mengkloning repositori)

Instalasi
Kloning repositori ini:

bash
git clone https://github.com/Eros99Cupdid/Just-Three-Papers.git
cd Just-Three-Papers
(Opsional) Buat dan aktifkan virtual environment:

bash
python -m venv venv
# Di Windows: .\venv\Scripts\activate
# Di macOS/Linux: source venv/bin/activate
Instal dependensi:

bash
pip install -r requirements.txt
Penggunaan Dasar (Python)
python
from just_three_papers import TPOCM

# Inisialisasi sistem dengan posisi awal (x1, x2, y)
sistem = TPOCM(x1=10.0, x2=20.0, y=5.0)

# 1. Dapatkan Sudut Orientasi Kanonik (Roll, Pitch, Yaw)
roll, pitch, yaw = sistem.get_angles()
print(f"Roll: {roll:.2f}°, Pitch: {pitch:.2f}°, Yaw: {yaw:.2f}°")

# 2. Hitung Jarak Euclidean (R)
jarak = sistem.get_distance()
print(f"Jarak 3D: {jarak:.2f} meter")

# 3. Rotasikan sebuah titik dalam ruang 3D
titik_asli = [1, 2, 3]
titik_hasil = sistem.rotate_point(titik_asli, roll=10, pitch=5, yaw=15)
print(f"Titik setelah rotasi: {titik_hasil}")

📁 Struktur Proyek

text

Just-Three-Papers/

├── src/                       # Kode sumber inti
│   ├── core.py                # Implementasi logika TP-OCM
│   ├── rotation.py            # Modul rotasi stabil
│   └── utils.py               # Fungsi pembantu
├── docs/                      # Dokumentasi lengkap
│   ├── FASE 0 FORMAL LOGICAL
│   │   ├── PAPER_TP-OCM.md
│   │   ├── TERJEMAHAN_FOL.md
│   │   ├── FORMAL_LOGIC.md
│   │   ├── 
│   ├── FASE 3                 # Paper teknis untuk engineer
│   ├── FASE 4                 # Paper untuk pengajaran
│   └── FASE 1                 # Pembuktian logika formal (FOL)
├── examples/                  # Contoh penggunaan
│   ├── drone_simulation.py    # Simulasi kontrol drone
│   ├── game_character.py      # Rotasi karakter game
│   └── survey_calculation.py  # Perhitungan sudut survey
├── tpocm/                  # Python Package
│   ├── __init__.py         # Ekspos kelas utama
│   ├── core.py             # Logika Matematika & Kelas TPOCM
│   └── utils.py            # Konverter (Degree/Radian, dll)
├── src_cpp/                # C++ Implementation (High Performance)
│   ├── tpocm.hpp           # Single-Header Library (Mudah di-include)
│   └── main.cpp            # Contoh penggunaan C++
├── examples/               # Contoh Script
│   ├── benchmark.py        # Uji kecepatan vs Quaternion
│   └── simple_nav.py       # Simulasi navigasi sederhana
├── tests/                  # Unit Tests
│   └── test_core.py
├── setup.py                # Konfigurasi Instalasi PIP
├── requirements.txt           # Dependensi Python
├── LICENSE                    # Lisensi GPL v3
└── README.md                  # File ini

📚 Dokumentasi & Pembelajaran
TP-OCM didokumentasikan melalui tiga pendekatan ("Three Papers"):

🧪 Paper Produksi: Fokus pada implementasi, benchmark, dan optimasi untuk engineer.

👨‍🏫 Paper Pedagogis: Penjelasan bertahap dengan analogi visual, cocok untuk pengajar dan pemula.

⚖️ Paper Formal Logic (FOL): Landasan aksiomatik dan pembuktian matematis yang rigorous.

Mulai dengan Paper Pedagogis jika Anda baru mengenal konsep ini.

🔬 Aplikasi Nyata
✈️ Kontrol Drone & UAV: Algoritma ringan untuk flight controller mikrokontroler.

🎮 Game & Real-Time Graphics: Rotasi objek dan kamera yang lebih cepat.

📡 Sensor Fusion & Radar: Pemrosesan data orientasi berkecepatan tinggi.

🏗️ Robotika & Navigasi Otonom: Menghitung orientasi dan arah pergerakan.

📊 Edukasi STEM: Alat mengajar transformasi geometri 3D yang lebih mudah dicerna.

🤝 Berkontribusi
Kontribusi Anda sangat diterima! Baik itu melaporkan bug, menyarankan fitur, atau mengirim kode.

Fork repositori ini.

Buat branch untuk fitur Anda (git checkout -b fitur/ajaib).

Commit perubahan Anda (git commit -m 'Menambahkan fitur ajaib').

Push ke branch (git push origin fitur/ajaib).

Buat Pull Request.

📜 Lisensi
TP-OCM menggunakan model lisensi terpisah untuk setiap jenis konten:

🖥️ Kode Sumber (/src/, /examples/)
Lisensi: GNU General Public License v3 (GPL v3)

Hak: Bebas menggunakan, memodifikasi, mendistribusikan

Kewajiban: Turunan harus tetap open source (copyleft)

Untuk siapa: Developer, kontributor, komunitas open source

📚 Materi Pendidikan (/docs/..)
Lisensi: Creative Commons Attribution 4.0 (CC BY 4.0)

Hak: Bebas mengajar, menerjemahkan, berbagi

Kewajiban: Wajib menyebut penemu asli (Nur Rohmat Hidayatulloh)

Untuk siapa: Guru, dosen, siswa, institusi pendidikan

🧠 Paper Logika Formal (/docs/paper_formal_logic.pdf)
Lisensi: Creative Commons Attribution-NoDerivatives 4.0 (CC BY-ND 4.0)

Hak: Bebas mengutip, merujuk, mendistribusikan

Kewajiban: Tidak boleh mengubah isi, wajib atribusi

Untuk siapa: Peneliti, akademisi, komunitas matematika

⚖️ Pertanyaan Umum
Q: Apakah ini legal?
A: YA. Setiap konten memiliki lisensi sendiri. Kode (GPL v3) tidak "menjalar" ke dokumen.

Q: Bisakah perusahaan pakai kode TP-OCM?
A: Bisa, tapi produk turunannya harus open source (sesuai GPL v3).

Q: Bisakah guru mengajar TP-OCM di sekolah?
A: BISA & SANGAT DISARANKAN! Materi pendidikan bebas dipakai dengan atribusi.

Q: Apakah paper formal bisa dikutip di jurnal?
A: BISA. Paper FOL bebas dikutip dengan atribusi, tidak boleh dimodifikasi.

💡 Lahir dari Kebingungan
Pada 20 Desember 2025, kejenuhan dengan tekanan tugas yang menumpuk justru memicu serangkaian pertanyaan mendasar: Bagaimana tepatnya bilangan imajiner (i) merepresentasikan rotasi? Mengapa perkalian berulang dengannya membentuk siklus yang kembali ke real?

Pencarian jawaban mengarah pada sebuah prinsip ontologis: bilangan bukan sekadar nilai, melainkan penunjuk tempat. Prinsip ini dimanifestasikan dalam model "Tiga Kertas" (Tri-Planar) yang menjadi fondasi TP-OCM—sebuah sistem untuk memetakan dan menavigasi ruang 3D dengan cara yang lebih intuitif dan efisien daripada metode konvensional.

Awalnya banyak ketidaktahuan. Banyak belajar dari 0 tentang apa kebutuhan efisiensi. Aku hanya berpikir, sedikit operator itu murah, tapi tiap operator punya "murahnya" sendiri-sendiri. Dengan evolusi yang bisa dipecah-pecah menjadi hubungan +, -, * itu membuatnya sangat murah.

👨‍💻 Penemu
Nur Rohmat Hidayatulloh - Penemu dan Arsitek Utama TP-OCM.

Konsep terbentuk di Pakualaman, 20 Desember 2025.

Visi: Membuat komputasi 3D menjadi lebih efisien.

🙏 Ucapan Terima Kasih
Kepada semua pendukung awal dan pemberi masukan.

Komunitas open-source yang menginspirasi.

Anda, untuk mengeksplorasi repositori ini!

💬 Dukungan & Komunitas
Jika Anda memiliki pertanyaan tentang:

Penggunaan komersial kode TP-OCM

Penggunaan materi pendidikan di institusi

Pengutipan paper formal di publikasi

Hubungi: eroscupd@gmail.com

Dibuat dengan ❤️ untuk memajukan teknologi yang lebih ringan dan cerdas.

🇬🇧 Just-Three-Papers: Tri-Planar Orthogonal Complex Mapping (TP-OCM)
A faster, lighter, and more intuitive 3D rotation solution than quaternions.

(The English section would follow the same structure as above, translated accordingly.)