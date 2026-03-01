import os
import json
from pdf_parser import extract_text_from_pdf, parse_questions_and_answers

files = [
    r"d:\Akash Exam\Previous question Paper\CSP Questions and Solutions (www.hsezip.com).pdf",
    r"d:\Akash Exam\Previous question Paper\CSP Questions and Solutions 2017 (www.hsezip.com).pdf"
]

total_questions = 0
all_extracted = []

for file_path in files:
    print(f"Processing: {os.path.basename(file_path)}")
    text = extract_text_from_pdf(file_path)
    if text:
        q, a = parse_questions_and_answers(text)
        num_q = len(q)
        print(f"Found {num_q} questions in this file.")
        total_questions += num_q
        
        # We merge questions and answers to create a list of items
        # Just like merge_and_save in pdf_parser
        final_data = []
        for q_id in sorted(q.keys()):
            q_data = q[q_id]
            if q_id in a:
                q_data["answer"] = a[q_id]["correct_option"]
                q_data["explanation"] = a[q_id]["explanation"]
            final_data.append(q_data)
            
        all_extracted.extend(final_data)

print(f"Total questions combined: {total_questions}")

output_file = r"d:\Akash Exam\combined_questions.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_extracted, f, indent=2)
print(f"Saved total {len(all_extracted)} questions to {output_file}")
