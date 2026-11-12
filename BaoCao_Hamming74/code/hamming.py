# ==========================================
# HAMMING (7,4)
# Quy uoc: [d1, d2, d3, d4, p1, p2, p3]
# ==========================================


# Bang anh xa syndrome -> vi tri loi
# Vi tri bit tinh tu 1 den 7
syndrome_map = {
    (1, 1, 0): 1,
    (1, 0, 1): 2,
    (0, 1, 1): 3,
    (1, 1, 1): 4,
    (1, 0, 0): 5,
    (0, 1, 0): 6,
    (0, 0, 1): 7
}


# ------------------------------------------
# 1. KIEM TRA DU LIEU DAU VAO
# ------------------------------------------

def validate_bits(bits, expected_length):
    if not isinstance(bits, list):
        raise TypeError("Du lieu phai la list[int]")

    if len(bits) != expected_length:
        raise ValueError(
            f"Du lieu phai co dung {expected_length} bit"
        )

    for bit in bits:
        if type(bit) is not int or bit not in (0, 1):
            raise ValueError("Moi bit chi duoc la 0 hoac 1")


# ------------------------------------------
# 2. MA HOA 4 BIT THANH 7 BIT
# ------------------------------------------

def hamming_encode(data):
    validate_bits(data, 4)

    d1, d2, d3, d4 = data

    # Tinh 3 bit parity theo quy uoc cua nhom
    p1 = d1 ^ d2 ^ d4
    p2 = d1 ^ d3 ^ d4
    p3 = d2 ^ d3 ^ d4

    parity_bits = [p1, p2, p3]

    # Noi 4 bit du lieu voi 3 bit parity
    codeword = data.copy() + parity_bits

    return codeword


# ------------------------------------------
# 3. TINH SYNDROME
# ------------------------------------------

def calculate_syndrome(received):
    validate_bits(received, 7)

    r1, r2, r3, r4, r5, r6, r7 = received

    s1 = r1 ^ r2 ^ r4 ^ r5
    s2 = r1 ^ r3 ^ r4 ^ r6
    s3 = r2 ^ r3 ^ r4 ^ r7

    syndrome = [s1, s2, s3]

    return syndrome


# ------------------------------------------
# 4. GIAI MA VA SUA LOI 1 BIT
# ------------------------------------------

def hamming_decode(received):
    # calculate_syndrome da kiem tra du lieu dau vao
    syndrome = calculate_syndrome(received)

    corrected = received.copy()
    error_position = None

    # Neu syndrome khac [0, 0, 0] thi co loi 1 bit
    if syndrome != [0, 0, 0]:
        error_position = syndrome_map[tuple(syndrome)]

        # Python dem chi so tu 0, vi tri bit dem tu 1
        index = error_position - 1

        # Dao bit bi loi: 0 thanh 1, 1 thanh 0
        corrected[index] ^= 1

    # Lay lai 4 bit du lieu ban dau
    decoded = corrected[:4]

    return {
        "syndrome": syndrome,
        "error_position": error_position,
        "corrected": corrected,
        "decoded": decoded
    }
