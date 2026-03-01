import pdfplumber

pdf_path = r"d:\Akash Exam\Previous question Paper\CSP Exam Vol 2_Ebook rev 004 (www.hsezip.com).pdf"
with pdfplumber.open(pdf_path) as pdf:
    # Solutions are probably at the end. The book has some number of pages.
    num_pages = len(pdf.pages)
    start_page = max(0, num_pages - 15)
    text = ""
    for i in range(start_page, num_pages): 
        text += f"\n--- Page {i} ---\n"
        text += pdf.pages[i].extract_text() or ""
        
with open(r"d:\Akash Exam\sample_text_vol2_end.txt", "w", encoding="utf-8") as f:
    f.write(text)
