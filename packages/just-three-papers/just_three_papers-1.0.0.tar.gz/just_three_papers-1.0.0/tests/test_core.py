import unittest
import math
from tpocm.core import TPOCM

class TestTPOCMCore(unittest.TestCase):
    """
    Unit Test Suite untuk TP-OCM (Tri-Planar Orthogonal Complex Mapping).
    Fokus: Validasi Matematis, Konsistensi Logika, dan Stabilitas Numerik.
    """

    def setUp(self):
        # Titik standar untuk pengujian umum (x1, x2, y)
        self.p_std = TPOCM(10.0, 20.0, 5.0)
        # Titik Singular (Origin)
        self.p_zero = TPOCM(0.0, 0.0, 0.0)
        # Toleransi Floating Point (Standar IEEE 754 presisi ganda)
        self.epsilon = 1e-9

    def test_01_complex_projection_mapping(self):
        """Memastikan pemetaan ke 3 bidang kompleks (Aksioma 2) akurat."""
        # Z1 (Frontal): x1 + iy
        self.assertEqual(self.p_std.z1, complex(10.0, 5.0))
        # Z2 (Sagital): x2 + iy
        self.assertEqual(self.p_std.z2, complex(20.0, 5.0))
        # Z3 (Horizontal): x1 + ix2
        self.assertEqual(self.p_std.z3, complex(10.0, 20.0))

    def test_02_tangent_chain_theorem(self):
        """
        Validasi Teorema 1 (OBS): tan(roll) = tan(pitch) * tan(yaw).
        Ini adalah tanda tangan matematika unik TP-OCM.
        """
        # Hitung manual tan dari sudut properti
        tan_roll = math.tan(self.p_std.roll)
        tan_pitch = math.tan(self.p_std.pitch)
        tan_yaw = math.tan(self.p_std.yaw)
        
        # Rumus: LHS = tan(roll), RHS = tan(pitch) * tan(yaw)
        lhs = tan_roll
        rhs = tan_pitch * tan_yaw
        
        # Assert dengan toleransi kecil
        self.assertAlmostEqual(lhs, rhs, places=7, 
            msg="Teorema Rantai Tangen gagal divalidasi!")

    def test_03_geometric_energy_conservation(self):
        """
        Validasi Teorema 2: 2r^2 = r1^2 + r2^2 + r3^2.
        Memastikan total energi geometris tidak hilang/bertambah.
        """
        r_global_sq = self.p_std.r ** 2
        
        r1_sq = abs(self.p_std.z1) ** 2
        r2_sq = abs(self.p_std.z2) ** 2
        r3_sq = abs(self.p_std.z3) ** 2
        
        lhs = 2 * r_global_sq
        rhs = r1_sq + r2_sq + r3_sq
        
        self.assertAlmostEqual(lhs, rhs, places=7,
            msg="Teorema Konservasi Energi Geometris gagal!")

    def test_04_pure_rotation_yaw(self):
        """Uji Rotasi Murni pada sumbu Y (Yaw/Heading)."""
        # Titik awal: (10, 0, 0) -> Arah Timur murni
        p = TPOCM(10.0, 0.0, 0.0)
        
        # Rotasi +90 derajat (pi/2) -> Harus jadi Utara (0, 10, 0)
        p_rotated = p.rotate(d_yaw=math.pi/2)
        
        self.assertAlmostEqual(p_rotated.x1, 0.0, places=7)
        self.assertAlmostEqual(p_rotated.x2, 10.0, places=7)
        self.assertAlmostEqual(p_rotated.y, 0.0, places=7)

    def test_05_sequential_rotation_integrity(self):
        """
        Uji Rotasi Bertahap (Non-Komutatif).
        Rotasi 3D harus konsisten dan tidak merobek koordinat (Spatial Tear).
        """
        p = TPOCM(10.0, 0.0, 0.0) # Timur
        
        # 1. Yaw 90 -> Utara (0, 10, 0)
        p = p.rotate(d_yaw=math.pi/2)
        # 2. Pitch 90 -> Atas (0, 0, 10)
        # Catatan: Pitch berputar pada sumbu x1 (Lateral). 
        # Saat di Utara, x1 adalah Timur-Barat. Sumbu x2 (Utara) naik ke y (Atas).
        p = p.rotate(d_pitch=math.pi/2)
        
        self.assertAlmostEqual(p.x1, 0.0, places=7)
        self.assertAlmostEqual(p.x2, 0.0, places=7)
        self.assertAlmostEqual(p.y, 10.0, places=7)

    def test_06_singularity_handling(self):
        """
        Uji ketahanan terhadap titik singular (0,0,0).
        Sistem tidak boleh crash (ZeroDivisionError).
        """
        try:
            _ = self.p_zero.yaw
            _ = self.p_zero.pitch
            _ = self.p_zero.roll
            valid = self.p_zero.validate_theorem() # Harusnya return True (skip check)
            self.assertTrue(valid)
        except Exception as e:
            self.fail(f"TP-OCM crash pada titik singular: {e}")

    def test_07_immutability(self):
        """Memastikan metode rotate() mengembalikan objek baru (Functional Pattern)."""
        p_awal = TPOCM(1, 1, 1)
        p_baru = p_awal.rotate(d_yaw=0.5)
        
        self.assertIsNot(p_awal, p_baru, "Objek harus immutable!")
        self.assertEqual(p_awal.x1, 1.0, "Objek awal tidak boleh berubah!")

    def test_08_reversibility(self):
        """
        Uji sifat dapat balik (Reversible).
        Rotasi maju +X lalu mundur -X harus kembali ke posisi awal.
        """
        angle = 1.234 # radian acak
        p_rotated = self.p_std.rotate(d_yaw=angle, d_pitch=angle, d_roll=angle)
        p_back = p_rotated.rotate(d_yaw=-angle, d_pitch=-angle, d_roll=-angle) # Urutan terbalik (simple check)
        
        # Note: Untuk rotasi 3D matrix penuh, inversi urutan rotasi (roll->pitch->yaw vs yaw->pitch->roll) 
        # sangat penting. Di fungsi rotate() implementasi sederhana, kita membalik input negatif.
        # Jika matriks benar, posisi harus kembali (dengan sedikit error floating point).
        
        # Karena implementasi core `rotate` melakukan 3 step sekuensial (Yaw->Pitch->Roll),
        # untuk mengembalikan sempurna kita harus melakukan Roll(-a) -> Pitch(-a) -> Yaw(-a).
        # Namun untuk tes sederhana ini, kita cek apakah selisihnya kecil.
        
        # Mari kita lakukan cara benar untuk inversi:
        p_inv = p_rotated.rotate(d_roll=-angle) # Inverse step 3
        p_inv = p_inv.rotate(d_pitch=-angle)    # Inverse step 2
        p_inv = p_inv.rotate(d_yaw=-angle)      # Inverse step 1
        
        self.assertAlmostEqual(p_inv.x1, self.p_std.x1, places=7)
        self.assertAlmostEqual(p_inv.x2, self.p_std.x2, places=7)
        self.assertAlmostEqual(p_inv.y, self.p_std.y, places=7)

if __name__ == '__main__':
    unittest.main()