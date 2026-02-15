import pdfplumber

pdf_path = r"d:\Akash Exam\Previous question Paper\CSP Practice Questions (www.hsezip.com).pdf"
output_path = r"d:\Akash Exam\last_pages_dump.txt"

with pdfplumber.open(pdf_path) as pdf:
    with open(output_path, "w", encoding="utf-8") as f:
        total = len(pdf.pages)
        for i in range(max(0, total - 5), total):
            page = pdf.pages[i]
            text = page.extract_text()
            f.write(f"--- Page {i+1} ---\n")
            f.write(text if text else "[No text found]")
            f.write("\n\n")

print("Dump complete.")
