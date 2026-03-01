import pdfplumber

pdf_path = r"d:\Akash Exam\Previous question Paper\CSP Practice Questions (www.hsezip.com).pdf"
with pdfplumber.open(pdf_path) as pdf:
    # Let's extract from page 3 (often where questions start) and page 67 (where answers might be)
    sample_text = ""
    for i in [2, 3, 4, 60, 66, 67, 68]: # pages 3,4,5 and 61, 67, 68, 69
        if i < len(pdf.pages):
            sample_text += f"\n--- Page {i+1} ---\n"
            sample_text += pdf.pages[i].extract_text() or ""

with open(r"d:\Akash Exam\sample_practice.txt", "w", encoding="utf-8") as f:
    f.write(sample_text)
