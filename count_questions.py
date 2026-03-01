import pdfplumber
import re

files = [
    r"d:\Akash Exam\Previous question Paper\CSP Questions and Solutions (www.hsezip.com).pdf",
    r"d:\Akash Exam\Previous question Paper\CSP Questions and Solutions 2017 (www.hsezip.com).pdf"
]

total_count = 0
all_questions_text = []

for file_path in files:
    print(f"\nProcessing: {file_path}")
    count_in_file = 0
    with pdfplumber.open(file_path) as pdf:
        num_pages = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                # Based on the sample, each question block starts with "CSP Question "
                matches = re.findall(r'CSP Question', text)
                if matches:
                    count_in_file += len(matches)
                    
                    # Store first few matches just to verify formatting
                    if count_in_file <= 2:
                        # Extract the first line containing the question
                        for line in text.split('\n'):
                            if 'CSP Question' in line:
                                all_questions_text.append(line.strip())
                                break
                                
            if (i+1) % 200 == 0:
                print(f"Processed {i+1}/{num_pages} pages...")
                
    print(f"Total questions found in {file_path}: {count_in_file}")
    total_count += count_in_file

print(f"\n============================")
print(f"GRAND TOTAL COMBINED QUESTIONS: {total_count}")
print(f"============================")
print(f"Sample questions extracted:")
for sq in all_questions_text:
    print(sq)
