from hamming import (
   validate_bits,
   hamming_encode,
   calculate_syndrome,
   hamming_decode
)

# ==========================================
# KIỂM THỬ ĐỘC LẬP HAMMING (7,4)
# ==========================================

# TC01: Kiểm tra dữ liệu đầu vào hợp lệ
def tc01_valid_input():
   validate_bits([1, 0, 1, 1], 4)
   return True

# TC02: kiểm tra bit không hợp lệ
def tc02_invalid_bit():
   try:
       validate_bits([1, 0, 2, 1], 4)
   except ValueError:
       return True
   return False

# TC03: Kiểm tra độ dài dữ liệu sai
def tc03_invalid_length():
   try:
       validate_bits([1, 0, 1], 4)
   except ValueError:
       return True
   return False

# TC04: Kiểm tra kết quả mã hóa
def tc04_encoding():
   data = [1, 0, 1, 1]

   expected = [1, 0, 1, 1, 0, 1, 0]
   actual = hamming_encode(data)

   return actual == expected

# TC05: Kiểm tra dữ liệu không có lỗi
def tc05_no_error():
   data = [1, 0, 1, 1]

   codeword = hamming_encode(data)
   result = hamming_decode(codeword)

   return (
       result["syndrome"] == [0, 0, 0]
       and result["error_position"] is None
       and result["corrected"] == codeword
       and result["decoded"] == data
   )

# TC06: Kiểm tra lỗi đơn bit tại 7 vị trí
def tc06_single_bit_errors():
   data = [1, 0, 1, 1]
   codeword = hamming_encode(data)

   for position in range(7):
       received = codeword.copy()
       received[position] ^= 1

       result = hamming_decode(received)

       if result["error_position"] != position + 1:
           return False

       if result["corrected"] != codeword:
           return False

       if result["decoded"] != data:
           return False

   return True

# TC07: Kiểm tra trường hợp 2 bit bị lỗi
def tc07_multiple_errors():
   data = [1, 0, 1, 1]
   codeword = hamming_encode(data)

   received = codeword.copy()

   received[0] ^= 1
   received[1] ^= 1

   result = hamming_decode(received)

   # 2 bit lỗi có thể khiến bộ giải mã sửa nhầm
   return (
       result["syndrome"] != [0, 0, 0]
       and result["corrected"] != codeword
       and result["decoded"] != data
   )

# TC08: Kiểm tra kết quả syndrome
def tc08_syndrome():
   data = [1, 0, 1, 1]
   codeword = hamming_encode(data)

   received = codeword.copy()
   received[2] ^= 1

   expected = [0, 1, 1]

   return calculate_syndrome(received) == expected

# TC09: Kiểm tra cấu trúc kết quả giải mã
def tc09_decode_structure():
   codeword = hamming_encode([1, 0, 1, 1])
   result = hamming_decode(codeword)

   return (
       set(result.keys()) == {
           "syndrome",
           "error_position",
           "corrected",
           "decoded"
       }
       and len(result["syndrome"]) == 3
       and len(result["corrected"]) == 7
       and len(result["decoded"]) == 4
   )

# TC10: Kiểm tra 16 bộ dữ liệu 4 bit
def tc10_all_data():
   for number in range(16):

       data = [
           (number >> 3) & 1,
           (number >> 2) & 1,
           (number >> 1) & 1,
           number & 1
       ]

       codeword = hamming_encode(data)
       result = hamming_decode(codeword)

       if result["decoded"] != data:
           return False

       if result["syndrome"] != [0, 0, 0]:
           return False

   return True

# ==========================================
# CÁC NHÓM KIỂM THỬ
# ==========================================

def test_no_error():
   return tc05_no_error() and tc10_all_data()


def test_single_bit_errors():
   return tc06_single_bit_errors()


def test_multiple_errors():
   return tc07_multiple_errors()


# ==========================================
# CHẠY TOÀN BỘ 10 TEST CASE
# ==========================================

def run_all_tests():

   tests = [
       ("TC01 - Dữ liệu đầu vào hợp lệ", tc01_valid_input),
       ("TC02 - Bit không hợp lệ", tc02_invalid_bit),
       ("TC03 - Độ dài không hợp lệ", tc03_invalid_length),
       ("TC04 - Mã hóa", tc04_encoding),
       ("TC05 - Không có lỗi", tc05_no_error),
       ("TC06 - Lỗi đơn bit", tc06_single_bit_errors),
       ("TC07 - Lỗi nhiều bit", tc07_multiple_errors),
       ("TC08 - Syndrome", tc08_syndrome),
       ("TC09 - Cấu trúc kết quả giải mã", tc09_decode_structure),
       ("TC10 - Đủ 16 tổ hợp dữ liệu", tc10_all_data)
   ]

   passed = 0
   failed = 0

   print("===== BÁO CÁO KIỂM THỬ HAMMING (7,4) =====")

   for name, test in tests:

       try:
           result = test()

           if result:
               print(f"[ĐẠT] {name}")
               passed += 1
           else:
               print(f"[KHÔNG ĐẠT] {name}")
               failed += 1

       except Exception as error:
           print(f"[KHÔNG ĐẠT] {name}: {error}")
           failed += 1

   print("\n===== TỔNG KẾT =====")
   print(f"Tổng số test: {len(tests)}")
   print(f"ĐẠT: {passed}")
   print(f"KHÔNG ĐẠT: {failed}")

   return passed, failed


if __name__ == "__main__":
   run_all_tests()
