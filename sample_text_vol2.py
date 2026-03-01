import pdfplumber

pdf_path = r"d:\Akash Exam\Previous question Paper\CSP Exam Vol 2_Ebook rev 004 (www.hsezip.com).pdf"
with pdfplumber.open(pdf_path) as pdf:
    # Let's extract from page 5, assuming some early pages are contents or headers
    text = ""
    for i in range(5, 15): # Pages 5-15
        if i < len(pdf.pages):
            text += f"\n--- Page {i} ---\n"
            text += pdf.pages[i].extract_text() or ""
        
with open(r"d:\Akash Exam\sample_text_vol2.txt", "w", encoding="utf-8") as f:
    f.write(text)
