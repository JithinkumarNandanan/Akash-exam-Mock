import pdfplumber

pdf_path = r"d:\Akash Exam\Previous question Paper\CSP Practice Questions (www.hsezip.com).pdf"

try:
    with pdfplumber.open(pdf_path) as pdf:
        # Check first 3 pages
        for i in range(min(3, len(pdf.pages))):
            page = pdf.pages[i]
            text = page.extract_text()
            print(f"--- Page {i+1} ---")
            print(text)
            print("-" * 20)
except Exception as e:
    print(f"Error: {e}")
