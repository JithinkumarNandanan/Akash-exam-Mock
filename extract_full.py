import pdfplumber
import re
import json
import os

files = [
    r"d:\Akash Exam\Previous question Paper\CSP Questions and Solutions (www.hsezip.com).pdf",
    r"d:\Akash Exam\Previous question Paper\CSP Questions and Solutions 2017 (www.hsezip.com).pdf"
]

def clean_text(text):
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        if "Get All HSE Resources at One Place" in line: continue
        if "Manager@BowenEHS.com" in line: continue
        if "Copyright" in line: continue
        if "Solution on next page" in line: continue
        cleaned.append(line)
    return '\n'.join(cleaned).strip()

def extract_from_file(file_path, start_id):
    questions = []
    current_q_id = start_id
    
    print(f"Reading {os.path.basename(file_path)}...")
    full_text = ""
    with pdfplumber.open(file_path) as pdf:
        num_pages = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            t = page.extract_text()
            if t:
                # remove --- Page X --- if added by some readers, but pdfplumber doesn't add it natively
                full_text += t + "\n"
            if (i+1) % 200 == 0:
                print(f"Read {i+1}/{num_pages} pages...")
                
    # Split by Question blocks
    blocks = re.split(r'(?:ASP-)?CSP Question \d{2}/\d{2}/\d{4}.*?\n', full_text)
    
    for i, block in enumerate(blocks[1:]): # Skip preamble
        block = clean_text(block)
        
        # Split block into Question and Solution 
        # Sometimes it's simply "Solution:\n" or "Solution\n" or "Solution :"
        parts = re.split(r'\nSolution:?\s*\n', block, maxsplit=1)
        
        if len(parts) < 2:
            # Maybe solution header has no newline before it in the extracted text?
            parts = re.split(r'Solution:?\s*\n', block, maxsplit=1)
            if len(parts) < 2:
                # Just skip or append as-is with no solution
                q_part = block
                sol_part = "Explanation not found."
            else:
                q_part = parts[0].strip()
                sol_part = parts[1].strip()
        else:
            q_part = parts[0].strip()
            sol_part = parts[1].strip()
            
        # Parse out options
        lines = q_part.split('\n')
        q_text_lines = []
        options = {}
        current_opt = None
        opt_pattern = re.compile(r'^([A-E])\.\s+(.*)$')
        
        for line in lines:
            m = opt_pattern.match(line.strip())
            if m:
                current_opt = m.group(1).lower()
                options[current_opt] = m.group(2).strip()
            elif current_opt:
                options[current_opt] += " " + line.strip()
            else:
                q_text_lines.append(line)
                
        q_text = "\n".join(q_text_lines).strip()
        
        # Extract correct answer
        ans = None
        # Common format: The correct solution is B.
        ans_pattern = re.search(r'The correct (?:solution|answer) is ([A-E])\.', sol_part, re.IGNORECASE)
        if ans_pattern:
            ans = ans_pattern.group(1).lower()
        else:
            # Fallback format: The correct solution is: B
            ans_pattern2 = re.search(r'The correct (?:solution|answer) is:\s*([A-E])', sol_part, re.IGNORECASE)
            if ans_pattern2:
                ans = ans_pattern2.group(1).lower()
                
        questions.append({
            "id": current_q_id,
            "question": q_text,
            "options": options,
            "answer": ans,
            "explanation": sol_part
        })
        current_q_id += 1
        
    return questions, current_q_id

all_data = []
current_id = 1
for f in files:
    q_data, current_id = extract_from_file(f, current_id)
    all_data.extend(q_data)

out = r"d:\Akash Exam\questions.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2)

print(f"\nSaved {len(all_data)} complete items to {out}")

# Print the first few questions just to ensure data sanity
for i in range(min(2, len(all_data))):
    print(f"\nQ: {all_data[i]['question']}")
    print(f"A: {all_data[i]['answer']}")
    print(f"Opts: {all_data[i]['options']}")
