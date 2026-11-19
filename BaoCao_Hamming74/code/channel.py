# ==========================================
# KENH DOI XUNG NHI PHAN (BSC)
# Moi bit bi dao doc lap voi xac suat p: r = c XOR e
# Du lieu vao/ra: list[int] (cung kieu voi hamming.py, text_codec.py)
# ==========================================

import random


def simulate_noise_hamming(bits, error_probability, rng=None):
    """
    Cho danh sach bit di qua kenh BSC.

    Tham so:
    - bits: list[int], moi phan tu la 0 hoac 1 (thuong la luong bit
      do encode_text tao ra)
    - error_probability: xac suat dao bit p, 0 <= p <= 1
    - rng: bo sinh so ngau nhien, vi du random.Random(seed);
      bo trong thi dung module random

    Tra ve: danh sach bit moi cung do dai; danh sach dau vao khong doi.
    Loi: TypeError neu bits khong phai list; ValueError neu co bit khac
    0, 1 hoac p nam ngoai [0, 1].
    """
    if not isinstance(bits, list):
        raise TypeError("Du lieu phai la list[int]")
    for bit in bits:
        if type(bit) is not int or bit not in (0, 1):
            raise ValueError("Moi bit chi duoc la 0 hoac 1")
    if not 0 <= error_probability <= 1:
        raise ValueError("Xac suat phai nam trong [0, 1]")

    if rng is None:
        rng = random

    # Vecto loi e: e_i = 1 voi xac suat p
    error = [1 if rng.random() < error_probability else 0 for _ in bits]

    # r = c XOR e
    return [b ^ e for b, e in zip(bits, error)]
