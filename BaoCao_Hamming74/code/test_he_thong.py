# ==========================================
# KIEM THU TICH HOP: text_codec.py, channel.py, main.py
# (test_hamming.py kiem thu rieng hamming.py, test_hamming84.py kiem thu
#  rieng hamming84.py; TH14-TH16 o day kiem thu ma (8,4) trong ca quy trinh)
# Cach chay: python test_he_thong.py   hoac   python -m pytest test_he_thong.py
# Moi ham test_* dung assert, nen pytest bao dung khi co ca khong dat;
# chay truc tiep thi in bao cao va tra ma thoat 1 neu co ca khong dat.
# ==========================================

import contextlib
import io
import itertools
import math
import random
import sys

from hamming import hamming_encode, hamming_decode
from hamming84 import hamming84_encode, hamming84_decode
from text_codec import (
    text_to_bits, bits_to_text, split_blocks, encode_text, decode_text
)
from channel import simulate_noise_hamming
from main import simulate, print_report

TEXTS = ["", "A", "Hamming (7,4)", "Đại số tuyến tính", "Xin chào thế giới",
         "é", "😀 中 €"]


def bits(s):
    return [int(ch) for ch in s]


def raises(func, error_type):
    try:
        func()
    except error_type:
        return True
    return False


# TH01: Doi chuoi ky tu <-> day bit theo UTF-8, hai chieu
def test_th01_utf8_hai_chieu():
    assert text_to_bits("A") == bits("01000001")
    assert len(text_to_bits("é")) == 16          # 2 byte UTF-8
    assert len(text_to_bits("ế")) == 24          # 3 byte UTF-8
    for text in TEXTS:
        assert bits_to_text(text_to_bits(text)) == text


# TH02: Ma hoa chuoi: 'A' -> 01001010001111 (Bang 3.3), 14 bit moi byte
def test_th02_ma_hoa_chuoi():
    assert encode_text("A") == bits("01001010001111")
    for text in TEXTS:
        assert len(encode_text(text)) == 14 * len(text.encode("utf-8"))


# TH03: Khong co loi: giai ma lai dung chuoi, khong khoi nao bi sua
def test_th03_khong_loi():
    for text in TEXTS:
        result = decode_text(encode_text(text))
        n_blocks = 2 * len(text.encode("utf-8"))
        assert result["text"] == text
        assert result["error_positions"] == [None] * n_blocks
        assert len(result["blocks"]) == n_blocks


# TH04: Moi khoi toi da 1 bit loi: khoi phuc dung chuoi, sua dung vi tri
def test_th04_moi_khoi_mot_loi():
    rng = random.Random(4)
    for text in TEXTS:
        sent = encode_text(text)
        received = sent.copy()
        flipped = []
        for start in range(0, len(sent), 7):
            if rng.random() < 0.7:
                position = rng.randrange(7) + 1
                received[start + position - 1] ^= 1
                flipped.append(position)
            else:
                flipped.append(None)
        result = decode_text(received)
        assert result["text"] == text
        assert result["error_positions"] == flipped


# TH05: Kiem tra dau vao cua text_codec.py
def test_th05_dau_vao_text_codec():
    assert raises(lambda: text_to_bits(65), TypeError)
    assert raises(lambda: decode_text([0] * 7), ValueError)    # khong boi 14
    assert raises(lambda: split_blocks([0, 1, 0], 4), ValueError)
    assert raises(lambda: bits_to_text([0, 1, 2, 0, 0, 0, 0, 0]), ValueError)
    assert raises(lambda: decode_text("0" * 14), TypeError)


# TH06: Byte khong hop le sau giai ma sai -> U+FFFD, khong dung
def test_th06_byte_hong():
    assert bits_to_text(bits("11111111")) == "�"
    assert bits_to_text(bits("01000001") + bits("10111110")) == "A�"


# TH07: Kenh BSC voi p = 0 va p = 1
def test_th07_kenh_bien():
    sent = encode_text("Hamming")
    assert simulate_noise_hamming(sent, 0.0, random.Random(1)) == sent
    assert simulate_noise_hamming(sent, 1.0, random.Random(1)) == \
        [1 - b for b in sent]


# TH08: Kenh BSC: cung seed cho cung ket qua, khong sua danh sach dau vao
def test_th08_kenh_seed():
    sent = encode_text("Ma Hamming (7,4)")
    original = sent.copy()
    first = simulate_noise_hamming(sent, 0.2, random.Random(8))
    second = simulate_noise_hamming(sent, 0.2, random.Random(8))
    other = simulate_noise_hamming(sent, 0.2, random.Random(9))
    assert first == second
    assert first != other
    assert sent == original


# TH09: Kenh BSC: du lieu dau vao sai
def test_th09_kenh_dau_vao():
    sent = encode_text("A")
    for p in [-0.1, 1.5, float("nan"), float("inf")]:
        assert raises(lambda: simulate_noise_hamming(sent, p), ValueError)
    assert raises(lambda: simulate_noise_hamming("01", 0.1), TypeError)
    assert raises(lambda: simulate_noise_hamming([0, 2], 0.1), ValueError)


# TH10: Toan bo quy trinh qua main.py: hai vi du o muc 4.5.4 (Ma 4.1, 4.2)
def test_th10_vi_du_main():
    sim = simulate("A", 0.1, 22)
    row1, row2 = sim["rows"]
    assert row1["received"] == bits("0110101") and row1["flips"] == 1
    assert row1["syndrome"] == [0, 1, 1] and row1["error_position"] == 3
    assert row1["ok"] and row2["ok"] and row2["flips"] == 0
    assert sim["received_text"] == "A"

    sim = simulate("A", 0.1, 15)
    row1 = sim["rows"][0]
    assert row1["received"] == bits("0000111") and row1["flips"] == 2
    assert row1["syndrome"] == [1, 1, 1] and row1["error_position"] == 4
    assert row1["decoded"] == bits("0001") and not row1["ok"]
    assert sim["received_text"] == "\x11"

    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        print_report(sim, 0.1, 15)
    assert "Khoi giai ma sai : 1/2" in output.getvalue()
    assert "KHONG KHOP" in output.getvalue()


# TH11: Toan bo quy trinh voi p = 0 va p = 1
def test_th11_quy_trinh_bien():
    text = "Đại số tuyến tính"
    sim = simulate(text, 0.0, 1)
    assert sim["received_text"] == text
    assert all(row["ok"] and row["flips"] == 0 for row in sim["rows"])

    # p = 1: e = 1111111 la tu ma, nen moi khoi co hoi chung 0
    # va bi giai ma thanh phan bu cua du lieu (muc 4.4.2)
    sim = simulate(text, 1.0, 1)
    for row in sim["rows"]:
        assert row["syndrome"] == [0, 0, 0] and row["error_position"] is None
        assert row["decoded"] == [1 - b for b in row["data"]]
        assert not row["ok"]


# TH12: Vet can 16 x 128 mau loi: giai ma dung khi va chi khi <= 1 bit loi
def test_th12_vet_can():
    for u in itertools.product([0, 1], repeat=4):
        u = list(u)
        c = hamming_encode(u)
        for e in itertools.product([0, 1], repeat=7):
            r = [a ^ b for a, b in zip(c, e)]
            assert (hamming_decode(r)["decoded"] == u) == (sum(e) <= 1)


# TH13: Thong ke: ti le khoi giai ma dung khop cong thuc (4.2)
def test_th13_thong_ke():
    rng = random.Random(2026)
    p, n_blocks = 0.1, 20000
    sent, data = [], []
    for _ in range(n_blocks):
        u = [rng.randrange(2) for _ in range(4)]
        data.append(u)
        sent += hamming_encode(u)
    received = simulate_noise_hamming(sent, p, rng)
    good = sum(hamming_decode(received[7 * i:7 * i + 7])["decoded"] == data[i]
               for i in range(n_blocks))
    theory = (1 - p) ** 7 + 7 * p * (1 - p) ** 6
    sigma = math.sqrt(theory * (1 - theory) / n_blocks)
    assert abs(good / n_blocks - theory) < 4 * sigma


# TH14: Ma mo rong (8,4) cho chuoi: 16 bit moi byte, khoi phuc dung khi moi
# khoi co toi da 1 bit loi (ke ca loi o bit 8)
def test_th14_chuoi_ma_84():
    assert encode_text("A", extended=True) == bits("0100101100011110")
    rng = random.Random(14)
    for text in TEXTS:
        sent = encode_text(text, extended=True)
        assert len(sent) == 16 * len(text.encode("utf-8"))
        assert decode_text(sent, extended=True)["text"] == text
        received = sent.copy()
        for start in range(0, len(sent), 8):
            if rng.random() < 0.7:
                received[start + rng.randrange(8)] ^= 1
        result = decode_text(received, extended=True)
        assert result["text"] == text and result["double_errors"] == 0
    assert raises(lambda: decode_text([0] * 14, extended=True), ValueError)


# TH15: Cung mau nhieu (seed 15): ma (7,4) sua nham, ma (8,4) phat hien
def test_th15_so_sanh_hai_ma():
    sim74 = simulate("A", 0.1, 15)
    sim84 = simulate("A", 0.1, 15, extended=True)
    row74, row84 = sim74["rows"][0], sim84["rows"][0]
    # Hai lan chay cung dao bit 2 va 6 cua khoi thu nhat
    assert row74["received"] == flip_bits(row74["sent"], [2, 6])
    assert row84["received"] == flip_bits(row84["sent"], [2, 6])
    assert not row74["ok"] and not row74["detected"]       # sua nham, khong biet
    assert row84["detected"] and row84["syndrome"] == [1, 1, 1]
    assert row84["parity"] == 0 and row84["error_position"] is None

    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        print_report(sim84, 0.1, 15)
    assert "PHAT HIEN" in output.getvalue()
    assert "Phat hien 2 loi  : 1/2" in output.getvalue()


# TH16: Thong ke ma (8,4): ti le khoi dung, phat hien, sai khong bi phat hien
def test_th16_thong_ke_84():
    rng = random.Random(2027)
    p, n_blocks = 0.1, 20000
    sent, data = [], []
    for _ in range(n_blocks):
        u = [rng.randrange(2) for _ in range(4)]
        data.append(u)
        sent += hamming84_encode(u)
    received = simulate_noise_hamming(sent, p, rng)
    good = detected = silent = 0
    for i in range(n_blocks):
        result = hamming84_decode(received[8 * i:8 * i + 8])
        if result["double_error"]:
            detected += 1
        elif result["decoded"] == data[i]:
            good += 1
        else:
            silent += 1
    q = 1 - p
    theory = {
        "good": q ** 8 + 8 * p * q ** 7,
        "detected": 28 * p**2 * q**6 + 56 * p**4 * q**4 + 28 * p**6 * q**2,
        "silent": (56 * p**3 * q**5 + 14 * p**4 * q**4 + 56 * p**5 * q**3
                   + 8 * p**7 * q + p**8),
    }
    assert abs(sum(theory.values()) - 1) < 1e-12
    for name, count in [("good", good), ("detected", detected),
                        ("silent", silent)]:
        t = theory[name]
        sigma = math.sqrt(t * (1 - t) / n_blocks)
        assert abs(count / n_blocks - t) < 4 * sigma, name


def flip_bits(word, positions):
    out = word.copy()
    for i in positions:
        out[i - 1] ^= 1
    return out


# ==========================================
# CHAY TOAN BO
# ==========================================

TESTS = [
    ("TH01 - UTF-8 hai chieu", test_th01_utf8_hai_chieu),
    ("TH02 - Ma hoa chuoi", test_th02_ma_hoa_chuoi),
    ("TH03 - Khong co loi", test_th03_khong_loi),
    ("TH04 - Moi khoi toi da 1 loi", test_th04_moi_khoi_mot_loi),
    ("TH05 - Dau vao text_codec", test_th05_dau_vao_text_codec),
    ("TH06 - Byte hong -> U+FFFD", test_th06_byte_hong),
    ("TH07 - Kenh voi p = 0, p = 1", test_th07_kenh_bien),
    ("TH08 - Kenh: seed", test_th08_kenh_seed),
    ("TH09 - Kenh: dau vao sai", test_th09_kenh_dau_vao),
    ("TH10 - Hai vi du cua main.py", test_th10_vi_du_main),
    ("TH11 - Quy trinh voi p = 0, p = 1", test_th11_quy_trinh_bien),
    ("TH12 - Vet can 16 x 128 mau loi", test_th12_vet_can),
    ("TH13 - Thong ke so voi (4.2)", test_th13_thong_ke),
    ("TH14 - Chuoi ky tu voi ma (8,4)", test_th14_chuoi_ma_84),
    ("TH15 - Cung nhieu: (7,4) sua nham, (8,4) phat hien",
     test_th15_so_sanh_hai_ma),
    ("TH16 - Thong ke ma (8,4)", test_th16_thong_ke_84),
]


def run_all_tests():
    passed = 0
    print("===== KIEM THU TICH HOP =====")
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
