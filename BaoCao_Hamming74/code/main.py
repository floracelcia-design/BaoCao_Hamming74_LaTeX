# ==========================================
# CHUONG TRINH MO PHONG MA HAMMING CHO CHUOI KY TU
# Chuoi ky tu -> ma hoa -> kenh BSC -> giai ma -> so sanh
# Ma (7,4) (mac dinh) hoac ma mo rong (8,4) (--ma 84)
# Cach chay: python main.py "chuoi ky tu" --p 0.05 --seed 1 [--ma 84]
# ==========================================

import argparse
import random
import sys

from text_codec import (
    DATA_BITS, block_length, encode_text, decode_text, split_blocks,
    text_to_bits
)
from channel import simulate_noise_hamming

MAX_ROWS = 16   # chuoi dai: chi in cac khoi bi kenh dao bit


def bits_str(bits):
    return "".join(str(b) for b in bits)


# ------------------------------------------
# 1. MO PHONG MOT LAN TRUYEN
# ------------------------------------------

def simulate(text, p, seed=None, extended=False):
    """Mo phong mot lan truyen chuoi text qua kenh BSC voi xac suat p.
    extended=False: ma (7,4); extended=True: ma mo rong (8,4)."""
    rng = random.Random(seed)

    data_bits = text_to_bits(text)
    sent = encode_text(text, extended)
    received = simulate_noise_hamming(sent, p, rng)
    result = decode_text(received, extended)

    # Bo giai ma chi biet vecto nhan duoc r. Phia mo phong biet ca du lieu
    # gui u va tu ma gui c, nen dem duoc so bit bi dao that va so khoi sai.
    # Chi tiet giai ma tung khoi lay tu decode_text, khong giai ma lai.
    rows = []
    data_blocks = split_blocks(data_bits, DATA_BITS)
    sent_blocks = split_blocks(sent, block_length(extended))
    for i, (u, c, dec) in enumerate(zip(data_blocks, sent_blocks,
                                        result["blocks"])):
        r = dec["received"]
        rows.append({
            "block": i + 1,
            "data": u,
            "sent": c,
            "received": r,
            "flips": sum(a ^ b for a, b in zip(c, r)),
            "syndrome": dec["syndrome"],
            "parity": dec.get("parity"),            # q, chi co o ma (8,4)
            "error_position": dec["error_position"],
            "decoded": dec["decoded"],
            "detected": dec.get("double_error", False),
            "ok": dec["decoded"] == u,
        })

    return {
        "text": text,
        "extended": extended,
        "received_text": result["text"],
        "n_bytes": len(text.encode("utf-8")),
        "n_bits": len(sent),
        "rows": rows,
    }


# ------------------------------------------
# 2. IN KET QUA
# ------------------------------------------

def result_label(row):
    if row["detected"]:
        return "PHAT HIEN"           # (8,4): phat hien hai loi, khong sua
    return "dung" if row["ok"] else "SAI"


def print_report(sim, p, seed):
    rows = sim["rows"]
    extended = sim["extended"]
    print(f"Chuoi gui        : {sim['text']!r}")
    print(f"Ma Hamming       : {'(8,4) mo rong' if extended else '(7,4)'}")
    print(f"Kich thuoc       : {sim['n_bytes']} byte UTF-8 -> "
          f"{len(rows)} khoi 4 bit -> {sim['n_bits']} bit sau ma hoa")
    print(f"Kenh BSC         : p = {p}, seed = {seed}")
    print()

    shown = rows
    if len(rows) > MAX_ROWS:
        shown = [row for row in rows if row["flips"] > 0]
        print("(Chuoi dai: chi in cac khoi bi kenh dao bit)")

    if extended:
        print("Khoi | Du lieu | Tu ma gui | Nhan duoc | Bit dao |  s  | q | "
              "Sua bit | Giai ma | Ket qua")
    else:
        print("Khoi | Du lieu | Tu ma gui | Nhan duoc | Bit dao | "
              "Hoi chung | Sua bit | Giai ma | Ket qua")
    for row in shown:
        pos = row["error_position"]
        if extended:
            words = (f" {bits_str(row['sent'])}  | "
                     f"{bits_str(row['received'])}  |")
            checks = f" {bits_str(row['syndrome'])} | {row['parity']} |"
        else:
            words = (f"  {bits_str(row['sent'])}  |  "
                     f"{bits_str(row['received'])}  |")
            checks = f"    {bits_str(row['syndrome'])}    |"
        print(f"{row['block']:4} |  {bits_str(row['data'])}   |{words}"
              f" {row['flips']:7} |{checks}"
              f" {('-' if pos is None else pos):>7} |  "
              f"{bits_str(row['decoded'])}   | {result_label(row)}")

    detected = sum(1 for row in rows if row["detected"])
    wrong = sum(1 for row in rows if not row["ok"] and not row["detected"])
    match = sim["received_text"] == sim["text"]
    print()
    print(f"Chuoi nhan       : {sim['received_text']!r}")
    if extended:
        print(f"Phat hien 2 loi  : {detected}/{len(rows)} khoi "
              f"(khong sua, can gui lai)")
        print(f"Khoi giai ma sai : {wrong}/{len(rows)} "
              f"(sai ma khong bi phat hien)")
    else:
        print(f"Khoi giai ma sai : {wrong}/{len(rows)}")
    print(f"Ket luan         : chuoi nhan "
          f"{'KHOP' if match else 'KHONG KHOP'} chuoi gui")


# ------------------------------------------
# 3. DIEM BAT DAU
# ------------------------------------------

def main():
    # Ky tu ma cua so dong lenh hoac tep nhan ket qua khong bieu dien duoc
    # (vi du khi chuyen huong ket qua ra tep tren Windows) duoc in duoi
    # dang ma thoat (\u1ebf, \ufffd) thay vi lam chuong trinh dung lai
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")

    parser = argparse.ArgumentParser(
        description="Mo phong ma Hamming (7,4) hoac (8,4) cho chuoi ky tu "
                    "qua kenh BSC")
    parser.add_argument("text", nargs="?",
                        help="chuoi ky tu can truyen (bo trong thi nhap tu ban phim)")
    parser.add_argument("--p", type=float, default=0.05,
                        help="xac suat dao bit cua kenh, 0 <= p <= 1 (mac dinh 0.05)")
    parser.add_argument("--seed", type=int, default=None,
                        help="so nguyen co dinh bo sinh ngau nhien de lap lai ket qua")
    parser.add_argument("--ma", choices=["74", "84"], default="74",
                        help="74: ma Hamming (7,4) (mac dinh); "
                             "84: ma mo rong (8,4), sua 1 loi va phat hien 2 loi")
    args = parser.parse_args()

    if args.text is not None:
        text = args.text
    else:
        try:
            text = input("Nhap chuoi ky tu: ")
        except EOFError:
            parser.error("khong co chuoi ky tu dau vao")

    try:
        sim = simulate(text, args.p, args.seed, extended=(args.ma == "84"))
    except ValueError as error:
        parser.error(str(error))

    print_report(sim, args.p, args.seed)


if __name__ == "__main__":
    main()
