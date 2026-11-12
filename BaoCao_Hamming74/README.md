# Mã Hamming (7,4): mô phỏng mã hóa, gây nhiễu, phát hiện và sửa lỗi cho chuỗi ký tự

Bài tập lớn Đại số tuyến tính MT1007, nhóm 10, lớp L06, Trường Đại học Bách khoa – ĐHQG TP.HCM.

## Cấu trúc

```
BaoCao_Hamming74/
├── main.tex, latexmkrc   Báo cáo LaTeX (XeLaTeX + minted, cần -shell-escape)
├── config/               settings.tex, macros.tex
├── frontmatter/          Bìa, lời cảm ơn, tóm tắt…
├── chapters/             chuong1.tex … chuong6.tex
├── backmatter/           phuluc.tex (Phụ lục A đọc thẳng các file trong code/), tailieu.tex
├── images/
└── code/                 Mã nguồn Python
    ├── hamming.py        Mã hóa, hội chứng, giải mã một khối
    ├── text_codec.py     Chuỗi ký tự <-> khối 4 bit
    ├── channel.py        Mô phỏng kênh nhiễu BSC
    └── test_hamming.py   10 ca kiểm thử cho hamming.py
```

## Quy ước (dạng hệ thống, đã chốt 06/11/2026)

- Từ mã c = (d1, d2, d3, d4, p1, p2, p3), bit dữ liệu đứng trước.
- p1 = d1 ⊕ d2 ⊕ d4, p2 = d1 ⊕ d3 ⊕ d4, p3 = d2 ⊕ d3 ⊕ d4.
- G = [I4 | P], H = [Pᵀ | I3]; hội chứng s = r·Hᵀ.
- Bit được lưu dưới dạng `list[int]`, mỗi phần tử là 0 hoặc 1.
- Chuỗi ký tự: UTF-8, mỗi byte 8 bit (bit cao trước), tách thành hai khối 4 bit (4 bit cao trước).

## Chạy kiểm thử

Yêu cầu Python 3.8 trở lên, không cần thư viện ngoài.

```
cd code
python test_hamming.py
```

## Quy tắc commit

- Fetch/Pull trước khi sửa; mỗi commit một thay đổi.
- Tiền tố trong Summary: `[code]`, `[ch1]` … `[ch6]`, `[phuluc]`, `[repo]`.
- Không commit file sinh ra khi biên dịch LaTeX (đã chặn trong `.gitignore`).
