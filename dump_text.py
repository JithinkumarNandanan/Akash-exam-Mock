import pdfplumber

pdf_path = r"d:\Akash Exam\Previous question Paper\CSP Practice Questions (www.hsezip.com).pdf"
output_path = r"d:\Akash Exam\sample_text.txt"

with pdfplumber.open(pdf_path) as pdf:
    with open(output_path, "w", encoding="utf-8") as f:
        for i in range(2, 10): # pages 3-10 (0-indexed)
            page = pdf.pages[i]
            text = page.extract_text()
            f.write(f"--- Page {i+1} ---\n")
            f.write(text if text else "[No text found]")
            f.write("\n\n")

print("Dump complete.")
