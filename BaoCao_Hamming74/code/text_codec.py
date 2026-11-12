# ==========================================
# TEXT CODEC - XU LY CHUOI KY TU
# Quy uoc: ky tu -> byte UTF-8 -> 8 bit (bit cao truoc)
#          moi byte tach thanh 2 khoi 4 bit (4 bit cao truoc)
#          moi khoi 4 bit ma hoa thanh 7 bit bang hamming.py
# ==========================================

from hamming import hamming_encode, hamming_decode

DATA_BITS = 4                    # so bit du lieu cua mot khoi
CODE_BITS = 7                    # so bit cua mot tu ma
BITS_PER_BYTE = 8
CODE_BITS_PER_BYTE = 2 * CODE_BITS   # mot byte cho hai tu ma


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

    # Byte khong hop le (do sua sai) duoc thay bang ky tu U+FFFD,
    # chuong trinh khong dung lai
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

def encode_text(text):
    codeword = []

    for block in split_blocks(text_to_bits(text), DATA_BITS):
        codeword += hamming_encode(block)

    return codeword


def decode_text(received):
    # Moi byte tuong ung 14 bit nhan duoc (hai khoi 7 bit)
    _check_bit_list(received, CODE_BITS_PER_BYTE)

    data_bits = []
    error_positions = []

    for block in split_blocks(received, CODE_BITS):
        result = hamming_decode(block)
        data_bits += result["decoded"]
        error_positions.append(result["error_position"])

    return {
        "text": bits_to_text(data_bits),
        "decoded_bits": data_bits,
        "error_positions": error_positions
    }
