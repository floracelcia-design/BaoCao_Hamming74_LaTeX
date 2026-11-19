# ==========================================
# TEXT CODEC - XU LY CHUOI KY TU
# Quy uoc: ky tu -> byte UTF-8 -> 8 bit (bit cao truoc)
#          moi byte tach thanh 2 khoi 4 bit (4 bit cao truoc)
#          moi khoi 4 bit ma hoa thanh 7 bit bang hamming.py (mac dinh)
#          hoac 8 bit bang hamming84.py (extended=True, ma mo rong (8,4))
# ==========================================

from hamming import hamming_encode, hamming_decode
from hamming84 import hamming84_encode, hamming84_decode

DATA_BITS = 4                    # so bit du lieu cua mot khoi
CODE_BITS = 7                    # so bit cua mot tu ma (7,4)
CODE_BITS_84 = 8                 # so bit cua mot tu ma mo rong (8,4)
BITS_PER_BYTE = 8
CODE_BITS_PER_BYTE = 2 * CODE_BITS   # mot byte cho hai tu ma (7,4)


def block_length(extended=False):
    """Do dai mot tu ma: 7 voi ma (7,4), 8 voi ma mo rong (8,4)."""
    return CODE_BITS_84 if extended else CODE_BITS


# ------------------------------------------
# 1. KIEM TRA DANH SACH BIT
# ------------------------------------------

def _check_bit_list(bits, multiple):
    if not isinstance(bits, list):
        raise TypeError("Du lieu phai la list[int]")

    if len(bits) % multiple != 0:
        raise ValueError(f"Do dai phai la boi so cua {multiple}")

    for bit in bits:
        if type(bit) is not int or bit not in (0, 1):
            raise ValueError("Moi bit chi duoc la 0 hoac 1")


# ------------------------------------------
# 2. KY TU <-> BIT
# ------------------------------------------

def text_to_bits(text):
    if not isinstance(text, str):
        raise TypeError("Du lieu phai la str")

    bits = []
    for byte in text.encode("utf-8"):
        # Lay 8 bit cua byte, bit cao truoc
        for shift in range(7, -1, -1):
            bits.append((byte >> shift) & 1)

    return bits


def bits_to_text(bits):
    _check_bit_list(bits, BITS_PER_BYTE)

    data = bytearray()
    for i in range(0, len(bits), BITS_PER_BYTE):
        byte = 0
        for bit in bits[i:i + BITS_PER_BYTE]:
            byte = (byte << 1) | bit
        data.append(byte)

    # Byte khong hop le (do mot khoi bi giai ma sai) duoc thay bang
    # ky tu U+FFFD, chuong trinh khong dung lai
    return data.decode("utf-8", errors="replace")


# ------------------------------------------
# 3. TACH KHOI
# ------------------------------------------

def split_blocks(bits, size):
    _check_bit_list(bits, size)

    return [bits[i:i + size] for i in range(0, len(bits), size)]


# ------------------------------------------
# 4. MA HOA VA GIAI MA CHUOI KY TU
# ------------------------------------------

def encode_text(text, extended=False):
    """Ma hoa chuoi ky tu: moi byte thanh 14 bit (ma (7,4)) hoac
    16 bit (ma mo rong (8,4), extended=True)."""
    encode = hamming84_encode if extended else hamming_encode
    codeword = []

    for block in split_blocks(text_to_bits(text), DATA_BITS):
        codeword += encode(block)

    return codeword


def decode_text(received, extended=False):
    """Giai ma day bit nhan duoc thanh chuoi ky tu. Do dai phai la boi cua
    14 (ma (7,4)) hoac 16 (ma mo rong (8,4), extended=True).
    Tra ve tu dien:
    - text: chuoi ky tu sau giai ma
    - decoded_bits: day bit du lieu (4 bit dau cua moi khoi sau sua)
    - error_positions: vi tri bit da sua cua tung khoi (None neu khong sua)
    - blocks: chi tiet tung khoi, gom received va cac khoa do ham giai ma
      mot khoi tra ve (hamming_decode hoac hamming84_decode)
    - double_errors: so khoi phat hien hai loi (luon bang 0 voi ma (7,4))
    """
    n = block_length(extended)
    decode = hamming84_decode if extended else hamming_decode

    # Moi byte tuong ung hai khoi nhan duoc (14 hoac 16 bit)
    _check_bit_list(received, 2 * n)

    data_bits = []
    error_positions = []
    blocks = []

    for block in split_blocks(received, n):
        result = decode(block)
        data_bits += result["decoded"]
        error_positions.append(result["error_position"])
        blocks.append({"received": block, **result})

    return {
        "text": bits_to_text(data_bits),
        "decoded_bits": data_bits,
        "error_positions": error_positions,
        "blocks": blocks,
        "double_errors": sum(1 for b in blocks if b.get("double_error"))
    }
