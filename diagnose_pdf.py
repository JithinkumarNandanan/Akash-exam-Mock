import pdfplumber
import sys

pdf_paths = [
    r"d:\Akash Exam\Previous question Paper\CSP Practice Questions (www.hsezip.com).pdf",
    r"d:\Akash Exam\Previous question Paper\CSP Questions and Solutions 2017 (www.hsezip.com).pdf"
]

log_file = r"d:\Akash Exam\pdf_analysis.txt"

with open(log_file, "w", encoding="utf-8") as f:
    for pdf_path in pdf_paths:
        f.write(f"Analyzing: {pdf_path}\n")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                f.write(f"Total Pages: {len(pdf.pages)}\n")
                for i in range(min(5, len(pdf.pages))):
                    page = pdf.pages[i]
                    text = page.extract_text()
                    images = page.images
                    f.write(f"  Page {i+1}: Text Length = {len(text) if text else 0}, Image Count = {len(images)}\n")
                    if text:
                        f.write(f"    Sample Text: {text[:100].replace(chr(10), ' ')}...\n")
        except Exception as e:
            f.write(f"Error: {e}\n")
        f.write("-" * 40 + "\n")

print("Analysis complete.")
