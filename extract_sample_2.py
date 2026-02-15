from pypdf import PdfReader
import os

# Path to the PDF file
pdf_path = r"d:\Akash Exam\Previous question Paper\CSP Questions and Solutions (www.hsezip.com).pdf"

try:
    reader = PdfReader(pdf_path)
    # Print the text from pages 5 to 10
    start_page = 5
    end_page = min(10, len(reader.pages))
    
    for i in range(start_page, end_page):
        page = reader.pages[i]
        text = page.extract_text()
        print(f"--- Page {i+1} ---")
        print(text)
        print("\n")
except Exception as e:
    print(f"Error reading PDF: {e}")
