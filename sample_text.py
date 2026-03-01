import pdfplumber

pdf_path = r"d:\Akash Exam\Previous question Paper\CSP Questions and Solutions (www.hsezip.com).pdf"
with pdfplumber.open(pdf_path) as pdf:
    # Let's extract from page 15, assuming some early pages are contents or headers
    text = ""
    for i in range(10, 25): # Pages 10-25
        text += f"\n--- Page {i} ---\n"
        text += pdf.pages[i].extract_text() or ""
        
with open(r"d:\Akash Exam\sample_text.txt", "w", encoding="utf-8") as f:
    f.write(text)
