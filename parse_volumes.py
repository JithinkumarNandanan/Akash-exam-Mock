import pdfplumber
import re
import json
import os

files = [
    r"d:\Akash Exam\Previous question Paper\CSP Exam Vol 2_Ebook rev 004 (www.hsezip.com).pdf",
    r"d:\Akash Exam\Previous question Paper\CSP Exam Vol 3 Ebook rev 004 (www.hsezip.com).pdf",
    r"d:\Akash Exam\Previous question Paper\CSP Exam Vol 4 Ebook rev 005 (www.hsezip.com).pdf",
    r"d:\Akash Exam\Previous question Paper\CSP Exam Vol 5 Ebook rev 004 (www.hsezip.com).pdf",
    r"d:\Akash Exam\Previous question Paper\CSP Exam Vol 6 Ebook rev 001 (www.hsezip.com).pdf",
]

def clean_text(text):
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line: continue
        if line == "www.BowenEHS.com": continue
        if re.match(r'^-\s*\d+\s*-$', line): continue
        if "Get All HSE Resources" in line: continue
        cleaned.append(line)
    return '\n'.join(cleaned)

def parse_volume(file_path, start_id):
    print(f"Reading {file_path}...")
    full_text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"
                
    full_text = clean_text(full_text)
    
    # We will do a two pass: identify questions, then identify answers.
    # Because questions have "1. Subject" and answers have "1. Explanation"
    
    # Let's split by the start of a number block: "^(\d+)\.\s+"
    # But wait, options are "A. ", numbers might be in text.
    # The format usually has the number at the start of a line.
    
    lines = full_text.split('\n')
    
    questions = {}
    answers = {}
    
    mode = "scan" # scan, question, option, answer
    current_num = None
    current_opt = None
    
    max_q_num = 0
    
    # Regexes
    # Questions start with a number, a period, and a text (Subject or Solution)
    num_match = re.compile(r'^(\d+)\.\s+(.*)')
    opt_match = re.compile(r'^([A-E])\.\s+(.*)')
    
    ans_regex = re.compile(r'The (?:correct|best) (?:solution|choice|answer) is ([A-E])\.', re.IGNORECASE)
    ans_regex_fallback = re.compile(r'The (?:correct|best) (?:solution|choice|answer) is:\s*([A-E])', re.IGNORECASE)
    
    seen_q_nums = set()
    
    for line in lines:
        m_num = num_match.match(line)
        if m_num:
            num = int(m_num.group(1))
            text_part = m_num.group(2)
            
            # If we've seen this number before, we are probably in the Answer key section
            if num in seen_q_nums or (num == 1 and max_q_num > 10): 
                # It's an answer explanation start
                current_num = num
                mode = "answer"
                answers[current_num] = text_part + "\n"
                continue
            else:
                # It's a new question start
                current_num = num
                seen_q_nums.add(num)
                if num > max_q_num: max_q_num = num
                mode = "question"
                questions[current_num] = {
                    "question_text": text_part + "\n",
                    "options": {}
                }
                current_opt = None
                continue
                
        if mode == "question" or mode == "option":
            m_opt = opt_match.match(line)
            if m_opt:
                mode = "option"
                current_opt = m_opt.group(1).lower()
                questions[current_num]["options"][current_opt] = m_opt.group(2) + "\n"
            else:
                if mode == "question":
                    questions[current_num]["question_text"] += line + "\n"
                elif mode == "option" and current_opt:
                    questions[current_num]["options"][current_opt] += line + "\n"
                    
        elif mode == "answer":
            answers[current_num] += line + "\n"
            
    # Compile the final data
    parsed_items = []
    
    for q_num, q_data in questions.items():
        q_text = q_data["question_text"].strip()
        opts = {k: v.strip() for k, v in q_data["options"].items()}
        
        ans_text = answers.get(q_num, "")
        
        # Extract the correct option
        correct_ans = None
        m_ans = ans_regex.search(ans_text)
        if m_ans:
            correct_ans = m_ans.group(1).lower()
        else:
            m_ans2 = ans_regex_fallback.search(ans_text)
            if m_ans2:
                correct_ans = m_ans2.group(1).lower()
                
        parsed_items.append({
            "id": start_id,
            "question": q_text,
            "options": opts,
            "answer": correct_ans,
            "explanation": ans_text.strip()
        })
        start_id += 1
        
    print(f"Extracted {len(parsed_items)} questions from this volume.")
    return parsed_items, start_id

if __name__ == "__main__":
    existing_file = r"d:\Akash Exam\questions.json"
    if os.path.exists(existing_file):
        with open(existing_file, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
    else:
        all_data = []
        
    start_id = 1
    if all_data:
        start_id = max([q["id"] for q in all_data]) + 1
        print(f"Loaded {len(all_data)} existing questions. Starting new IDs at {start_id}")
        
    new_data = []
    for f in files:
        data, start_id = parse_volume(f, start_id)
        new_data.extend(data)
        
    print(f"Extracted a total of {len(new_data)} new questions.")
    
    # Save combined
    all_data.extend(new_data)
    with open(existing_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)
        
    print(f"Saved total of {len(all_data)} questions to {existing_file}")
