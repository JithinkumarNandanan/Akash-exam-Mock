from pypdf import PdfReader
import os

# Path to the PDF file
pdf_path = r"d:\Akash Exam\Previous question Paper\CSP Practice Questions (www.hsezip.com).pdf"

try:
    reader = PdfReader(pdf_path)
    # Print the text from the first 5 pages
    for i in range(min(5, len(reader.pages))):
        page = reader.pages[i]
        text = page.extract_text()
        print(f"--- Page {i+1} ---")
        print(text)
        print("\n")
except Exception as e:
    print(f"Error reading PDF: {e}")
