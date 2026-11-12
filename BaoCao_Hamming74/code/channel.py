import random

def simulate_noise_hamming(codeword, error_probability):
    """
    Mô hình nhiễu cho mã Hamming (hoặc bất kỳ dãy bit nào).
    Mỗi bit trong codeword có xác suất error_probability bị lật.

    Tham số:
    - codeword: chuỗi bit (ví dụ '1010101')
    - error_probability: xác suất lật bit (float từ 0 đến 1)

    Trả về:
    - Chuỗi bit sau khi qua kênh nhiễu (một số bit bị đổi)
    """
    noisy_codeword = []
    for bit in codeword:
        rnd = random.random()
        if rnd < error_probability:
            # Lật bit nếu random < error_probability
            flipped_bit = '1' if bit == '0' else '0'
            noisy_codeword.append(flipped_bit)
        else:
            # Giữ bit nguyên
            noisy_codeword.append(bit)
    return ''.join(noisy_codeword)
