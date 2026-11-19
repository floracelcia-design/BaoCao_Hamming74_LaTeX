# ==========================================
# HAMMING MO RONG (8,4) - SUA 1 LOI, PHAT HIEN 2 LOI (SEC-DED)
# Quy uoc (muc 2.7): c' = [c1, ..., c7, c8]
#   c1..c7 la tu ma (7,4) cua hamming.py: [d1, d2, d3, d4, p1, p2, p3]
#   c8 = c1 ^ c2 ^ ... ^ c7 (bit chan le tong the, quy uoc chan)
# H' = [H | 0 ; 1 1 1 1 1 1 1 1], hoi chung mo rong s' = r.H'^T = (s, q)
#   s: hoi chung 3 bit tinh tren 7 bit dau (nhu ma (7,4))
#   q = r1 ^ r2 ^ ... ^ r8
# ==========================================

from hamming import validate_bits, hamming_encode, calculate_syndrome, syndrome_map

# Trang thai giai ma theo Bang 2.3 (gia thiet khong qua 2 bit loi)
NO_ERROR = "khong loi"           # s = 0,  q = 0
SINGLE_ERROR = "sua 1 loi"       # s != 0, q = 1: dao bit j co h_j = s
PARITY_ERROR = "loi bit 8"       # s = 0,  q = 1: dao bit 8, du lieu khong doi
DOUBLE_ERROR = "phat hien 2 loi" # s != 0, q = 0: khong sua, bao loi


# ------------------------------------------
# 1. MA HOA 4 BIT THANH 8 BIT
# ------------------------------------------

def hamming84_encode(data):
    """Ma hoa 4 bit du lieu u thanh tu ma mo rong 8 bit c' = (c, c8)."""
    codeword = hamming_encode(data)      # kiem tra du lieu va tinh c = u.G

    c8 = 0
    for bit in codeword:
        c8 ^= bit

    return codeword + [c8]


# ------------------------------------------
# 2. TINH HOI CHUNG MO RONG
# ------------------------------------------

def calculate_syndrome84(received):
    """Tinh s' = r.H'^T cua vecto nhan duoc r (8 bit).
    Tra ve (s, q): s gom 3 bit, q la bit kiem tra chan le tong the."""
    validate_bits(received, 8)

    # Ba hang dau cua H' co phan tu cuoi bang 0, nen s chi phu thuoc 7 bit dau
    syndrome = calculate_syndrome(received[:7])

    q = 0
    for bit in received:
        q ^= bit

    return syndrome, q


# ------------------------------------------
# 3. GIAI MA: SUA 1 LOI, PHAT HIEN 2 LOI
# ------------------------------------------

def hamming84_decode(received):
    """Giai ma mot khoi 8 bit theo Bang 2.3.
    Tra ve tu dien: syndrome (s), parity (q), status, error_position
    (1..8, None neu khong sua), corrected, decoded (4 bit dau cua corrected),
    double_error (True neu phat hien hai loi; khi do khoi khong duoc sua va
    decoded la 4 bit dau cua vecto nhan duoc)."""
    syndrome, q = calculate_syndrome84(received)

    corrected = received.copy()
    error_position = None
    has_syndrome = syndrome != [0, 0, 0]

    if not has_syndrome and q == 0:
        status = NO_ERROR
    elif has_syndrome and q == 1:
        # So bit loi le, hoi chung khac 0: coi la mot loi trong 7 bit dau
        status = SINGLE_ERROR
        error_position = syndrome_map[tuple(syndrome)]
        corrected[error_position - 1] ^= 1
    elif not has_syndrome and q == 1:
        # Bay bit dau thoa ma (7,4), chi sai chan le tong the: loi o bit 8
        status = PARITY_ERROR
        error_position = 8
        corrected[7] ^= 1
    else:
        # So bit loi chan khac 0: phat hien hai loi, khong sua
        status = DOUBLE_ERROR

    return {
        "syndrome": syndrome,
        "parity": q,
        "status": status,
        "error_position": error_position,
        "corrected": corrected,
        "decoded": corrected[:4],
        "double_error": status == DOUBLE_ERROR
    }
