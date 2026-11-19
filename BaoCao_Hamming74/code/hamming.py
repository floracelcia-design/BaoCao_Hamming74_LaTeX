# ==========================================
# HAMMING (7,4)
# Quy uoc: [d1, d2, d3, d4, p1, p2, p3]
# ==========================================


# Bang anh xa syndrome -> vi tri loi
# Moi khoa la mot cot cua H = [P^T | I3]; vi tri bit tinh tu 1 den 7
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
    """Kiem tra bits la list gom dung expected_length so nguyen 0/1.
    Sai kieu: TypeError; sai do dai hoac gia tri: ValueError."""
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
    """Ma hoa 4 bit du lieu u thanh tu ma 7 bit c = u.G."""
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
    """Tinh hoi chung s = r.H^T cua vecto nhan duoc r (7 bit)."""
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
    """Giai ma mot khoi 7 bit, gia thiet co toi da 1 bit loi.
    Tra ve tu dien: syndrome, error_position (None neu khong sua),
    corrected, decoded (4 bit dau cua corrected)."""
    # calculate_syndrome da kiem tra du lieu dau vao
    syndrome = calculate_syndrome(received)

    corrected = received.copy()
    error_position = None

    # Gia thiet toi da 1 bit loi: syndrome khac 0 thi dao bit tuong ung.
    # Neu thuc te co tu 2 bit loi, buoc nay se sua nham.
    if syndrome != [0, 0, 0]:
        error_position = syndrome_map[tuple(syndrome)]

        # Python dem chi so tu 0, vi tri bit dem tu 1
        index = error_position - 1

        # Dao bit bi loi: 0 thanh 1, 1 thanh 0
        corrected[index] ^= 1

    # Lay 4 bit dau lam du lieu giai ma
    decoded = corrected[:4]

    return {
        "syndrome": syndrome,
        "error_position": error_position,
        "corrected": corrected,
        "decoded": decoded
    }
