import math
from dataclasses import dataclass
from typing import Tuple, Dict

@dataclass
class TPOCMConfig:
    epsilon: float = 1e-9  # Toleransi floating point

class TPOCM:
    """
    Tri-Planar Orthogonal Complex Mapping (TP-OCM) System.
    Representasi titik 3D menggunakan 3 bidang kompleks ortogonal.
    """

    def __init__(self, x1: float, x2: float, y: float):
        self.x1 = float(x1)
        self.x2 = float(x2)
        self.y = float(y)

    # --- REPRESENTASI KOMPLEKS (THE THREE PAPERS) ---

    @property
    def z1(self) -> complex:
        """Bidang Frontal (Roll): Timur-Barat + i(Atas-Bawah)"""
        return complex(self.x1, self.y)

    @property
    def z2(self) -> complex:
        """Bidang Sagital (Pitch): Utara-Selatan + i(Atas-Bawah)"""
        return complex(self.x2, self.y)

    @property
    def z3(self) -> complex:
        """Bidang Horizontal (Yaw): Timur-Barat + i(Utara-Selatan)"""
        return complex(self.x1, self.x2)

    # --- SUDUT KANONIK (THE THREE ANGLES) ---

    @property
    def yaw(self) -> float:
        """Theta 3 (Heading): Rotasi pada Z3"""
        return math.atan2(self.x2, self.x1)

    @property
    def pitch(self) -> float:
        """Theta 2 (Elevation): Rotasi pada Z2"""
        return math.atan2(self.y, self.x2)

    @property
    def roll(self) -> float:
        """Theta 1 (Bank): Rotasi pada Z1"""
        return math.atan2(self.y, self.x1)

    @property
    def r(self) -> float:
        """Jarak Euclidean Global"""
        return math.sqrt(self.x1**2 + self.x2**2 + self.y**2)

    # --- OPERASI INTI (DEEP THINKING IMPLEMENTATION) ---

    def rotate(self, d_yaw: float = 0, d_pitch: float = 0, d_roll: float = 0) -> 'TPOCM':
        """
        Melakukan rotasi 3D sekuensial (Intrinsic Z-Y-X).
        Input dalam Radian.
        Mengembalikan instance baru (Immutable pattern).
        """
        # 1. Rotasi YAW (Sumbu Vertikal y) - Memutar bidang Horizontal
        # Matriks Rotasi Z (dalam konteks standar) atau Y (dalam TPOCM)
        # x1' = x1 cos - x2 sin
        # x2' = x1 sin + x2 cos
        cy, sy = math.cos(d_yaw), math.sin(d_yaw)
        x1_a = self.x1 * cy - self.x2 * sy
        x2_a = self.x1 * sy + self.x2 * cy
        y_a  = self.y

        # 2. Rotasi PITCH (Sumbu Lateral x1)
        # y' = y cos - x2 sin
        # x2'' = y sin + x2 cos
        cp, sp = math.cos(d_pitch), math.sin(d_pitch)
        x2_b  = x2_a * cp - y_a * sp
        y_b = x2_a * sp + y_a * cp
        x1_b = x1_a

        # 3. Rotasi ROLL (Sumbu Longitudinal x2)
        # x1'' = x1 cos - y sin
        # y'' = x1 sin + y cos
        cr, sr = math.cos(d_roll), math.sin(d_roll)
        x1_c = x1_b * cr - y_b * sr
        y_c  = x1_b * sr + y_b * cr
        x2_c = x2_b

        return TPOCM(x1_c, x2_c, y_c)

    def validate_theorem(self) -> bool:
        """Mengecek konsistensi Teorema Rantai Tangen"""
        t1 = math.tan(self.roll)
        t2 = math.tan(self.pitch)
        t3 = math.tan(self.yaw)
        
        # Hindari div by zero dengan pengecekan epsilon
        if abs(self.x1) < 1e-9 or abs(self.x2) < 1e-9:
            return True # Singularitas, skip validasi
            
        lhs = t1
        rhs = t2 * t3
        return abs(lhs - rhs) < 1e-6

    def __repr__(self):
        return f"TPOCM(x1={self.x1:.2f}, x2={self.x2:.2f}, y={self.y:.2f})"