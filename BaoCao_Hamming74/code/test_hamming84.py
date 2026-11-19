# ==========================================
# KIEM THU MA HAMMING MO RONG (8,4): hamming84.py
# Doi chieu voi muc 2.7 (Bang 2.3) va vi du o muc 3.6
# Cach chay: python test_hamming84.py   hoac   python -m pytest test_hamming84.py
# ==========================================

import itertools
import sys

from hamming import hamming_encode
from hamming84 import (
    hamming84_encode, calculate_syndrome84, hamming84_decode,
    NO_ERROR, SINGLE_ERROR, PARITY_ERROR, DOUBLE_ERROR
)

# H' = [H | 0 ; 1 1 1 1 1 1 1 1] (muc 2.7.2)
H_EXT = [
    [1, 1, 0, 1, 1, 0, 0, 0],
    [1, 0, 1, 1, 0, 1, 0, 0],
    [0, 1, 1, 1, 0, 0, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1],
]
DATA = [list(u) for u in itertools.product([0, 1], repeat=4)]
CODEWORDS = [hamming84_encode(u) for u in DATA]


def bits(s):
    return [int(ch) for ch in s]


def flip(word, positions):
    """Dao cac bit o vi tri (dem tu 1)."""
    out = word.copy()
    for i in positions:
        out[i - 1] ^= 1
    return out


def raises(func, error_type):
    try:
        func()
    except error_type:
        return True
    return False


# TM01: Ma hoa: 1011 -> 10110100 (muc 3.6); c' = (c, c8) voi c la tu ma (7,4)
def test_tm01_ma_hoa():
    assert hamming84_encode([1, 0, 1, 1]) == bits("10110100")
    for u, c_ext in zip(DATA, CODEWORDS):
        assert c_ext[:7] == hamming_encode(u)
        assert sum(c_ext) % 2 == 0                  # chan le chan


# TM02: 16 tu ma thoa c'.H'^T = 0; trong so 0, 4, 8 nen d_min = 4
def test_tm02_tu_ma_va_dmin():
    for c_ext in CODEWORDS:
        assert all(sum(a * b for a, b in zip(c_ext, row)) % 2 == 0
                   for row in H_EXT)
    weights = sorted(sum(c) for c in CODEWORDS)
    assert weights == [0] + [4] * 14 + [8]
    assert len({tuple(c) for c in CODEWORDS}) == 16


# TM03: (s, q) trung r.H'^T voi ca 256 vecto r
def test_tm03_hoi_chung():
    for r in itertools.product([0, 1], repeat=8):
        r = list(r)
        s_ext = [sum(a * b for a, b in zip(r, row)) % 2 for row in H_EXT]
        s, q = calculate_syndrome84(r)
        assert s + [q] == s_ext


# TM04: Khong loi -> s = 0, q = 0, giu nguyen (Bang 2.3, dong 1)
def test_tm04_khong_loi():
    for u, c_ext in zip(DATA, CODEWORDS):
        result = hamming84_decode(c_ext)
        assert result["status"] == NO_ERROR
        assert result["error_position"] is None
        assert result["corrected"] == c_ext and result["decoded"] == u


# TM05: Mot loi o 7 bit dau -> s != 0, q = 1, sua dung (dong 2)
def test_tm05_mot_loi_bay_bit_dau():
    for u, c_ext in zip(DATA, CODEWORDS):
        for i in range(1, 8):
            result = hamming84_decode(flip(c_ext, [i]))
            assert result["status"] == SINGLE_ERROR
            assert result["parity"] == 1 and result["error_position"] == i
            assert result["corrected"] == c_ext and result["decoded"] == u


# TM06: Mot loi o bit 8 -> s = 0, q = 1, dao bit 8, du lieu khong doi (dong 3)
def test_tm06_loi_bit_8():
    for u, c_ext in zip(DATA, CODEWORDS):
        result = hamming84_decode(flip(c_ext, [8]))
        assert result["status"] == PARITY_ERROR
        assert result["syndrome"] == [0, 0, 0] and result["error_position"] == 8
        assert result["corrected"] == c_ext and result["decoded"] == u


# TM07: Moi mau hai loi (16 x 28) -> s != 0, q = 0, phat hien, khong sua (dong 4)
def test_tm07_hai_loi():
    for c_ext in CODEWORDS:
        for i, j in itertools.combinations(range(1, 9), 2):
            r = flip(c_ext, [i, j])
            result = hamming84_decode(r)
            assert result["status"] == DOUBLE_ERROR and result["double_error"]
            assert result["syndrome"] != [0, 0, 0] and result["parity"] == 0
            assert result["error_position"] is None
            assert result["corrected"] == r                # khong sua


# TM08: Hai vi du o muc 3.6 (Bang 3.5)
def test_tm08_vi_du_muc_3_6():
    result = hamming84_decode(bits("11111100"))            # loi bit 2 va 5
    assert result["syndrome"] == [0, 0, 1] and result["parity"] == 0
    assert result["status"] == DOUBLE_ERROR

    result = hamming84_decode(bits("10110110"))            # loi bit 7
    assert result["syndrome"] == [0, 0, 1] and result["parity"] == 1
    assert result["error_position"] == 7
    assert result["corrected"] == bits("10110100")


# TM09: Ngoai pham vi bao dam (cuoi muc 2.7.3): ba loi khong bao gio duoc bao
# la loi kep (7 mau hieu la loi bit 8, 49 mau hieu la loi don o 7 bit dau);
# bon loi trung mot tu ma trong so 4 (14 mau) khong bi phat hien
def test_tm09_ngoai_pham_vi():
    for c_ext in CODEWORDS:
        count = {PARITY_ERROR: 0, SINGLE_ERROR: 0, DOUBLE_ERROR: 0}
        for positions in itertools.combinations(range(1, 9), 3):
            result = hamming84_decode(flip(c_ext, positions))
            count[result["status"]] += 1
            assert result["corrected"] != c_ext            # luon sai
        assert count == {PARITY_ERROR: 7, SINGLE_ERROR: 49, DOUBLE_ERROR: 0}

        undetected = sum(
            hamming84_decode(flip(c_ext, positions))["status"] == NO_ERROR
            for positions in itertools.combinations(range(1, 9), 4))
        assert undetected == 14


# TM10: Kiem tra dau vao
def test_tm10_dau_vao():
    assert raises(lambda: hamming84_decode([1, 0, 1, 1, 0, 1, 0]), ValueError)
    assert raises(lambda: hamming84_decode((1, 0, 1, 1, 0, 1, 0, 0)), TypeError)
    assert raises(lambda: hamming84_decode([1, 0, 1, 1, 0, 1, 0, 2]), ValueError)
    assert raises(lambda: hamming84_encode([1, 0, 1]), ValueError)
    r = bits("10110110")
    original = r.copy()
    hamming84_decode(r)
    assert r == original                                   # khong sua dau vao


# ==========================================
# CHAY TOAN BO
# ==========================================

TESTS = [
    ("TM01 - Ma hoa c' = (c, c8)", test_tm01_ma_hoa),
    ("TM02 - 16 tu ma, d_min = 4", test_tm02_tu_ma_va_dmin),
    ("TM03 - (s, q) = r.H'^T", test_tm03_hoi_chung),
    ("TM04 - Khong loi", test_tm04_khong_loi),
    ("TM05 - Mot loi o 7 bit dau", test_tm05_mot_loi_bay_bit_dau),
    ("TM06 - Loi o bit 8", test_tm06_loi_bit_8),
    ("TM07 - Moi mau hai loi duoc phat hien", test_tm07_hai_loi),
    ("TM08 - Vi du muc 3.6", test_tm08_vi_du_muc_3_6),
    ("TM09 - Ba va bon loi (ngoai pham vi)", test_tm09_ngoai_pham_vi),
    ("TM10 - Dau vao", test_tm10_dau_vao),
]


def run_all_tests():
    passed = 0
    print("===== KIEM THU MA HAMMING MO RONG (8,4) =====")
    for name, test in TESTS:
        try:
            test()
            print(f"[DAT]       {name}")
            passed += 1
        except Exception as error:
            print(f"[KHONG DAT] {name}: {type(error).__name__} {error}")
    failed = len(TESTS) - passed
    print()
    print(f"Tong so: {len(TESTS)}   DAT: {passed}   KHONG DAT: {failed}")
    return failed


if __name__ == "__main__":
    sys.exit(1 if run_all_tests() else 0)
