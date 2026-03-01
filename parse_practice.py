import pdfplumber
import re
import json
import os

pdf_path = r"d:\Akash Exam\Previous question Paper\CSP Practice Questions (www.hsezip.com).pdf"
existing_file = r"d:\Akash Exam\questions.json"

def clean_text(text):
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line: continue
        if "Get All HSE Resources" in line: continue
        if "Copyright" in line: continue
        if re.match(r'^-\s*\d+\s*-$', line): continue
        # Page numbers might just be digits on a line based on sample
        if re.match(r'^\d+$', line): continue 
        cleaned.append(line)
    return '\n'.join(cleaned)

def parse_practice_file(file_path, start_global_id):
    print(f"Reading {file_path}...")
    full_text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"
                
    full_text = clean_text(full_text)
    lines = full_text.split('\n')
    
    questions = {}
    answers = {}
    
    mode = "scan" # scan, question, option, answer
    current_num = None
    current_opt = None
    
    max_q_num = 0
    seen_q_nums = set()
    
    # regex patterns based on sample
    q_start_pattern = re.compile(r'^(\d+)\.\s+(.*)')
    opt_pattern = re.compile(r'^([a-d])\.\s+(.*)')
    ans_pattern = re.compile(r'^(\d+)\.\s+([A-D]):\s*(.*)')
    
    for line in lines:
        m_ans = ans_pattern.match(line)
        if m_ans:
            num = int(m_ans.group(1))
            correct_opt = m_ans.group(2).lower()
            explanation = m_ans.group(3)
            current_num = num
            mode = "answer"
            answers[num] = {
                "correct": correct_opt,
                "explanation": explanation + "\n"
            }
            continue
            
        if mode == "answer" and current_num is not None:
            # might be a continuation of the explanation unless it matches a new answer or question
            m_num = q_start_pattern.match(line)
            if not m_num:
                answers[current_num]["explanation"] += line + "\n"
                continue
                
        # Not an answer, let's check for question start
        m_num = q_start_pattern.match(line)
        if m_num:
            num = int(m_num.group(1))
            text = m_num.group(2)
            # If we've seen this before, and it didn't match the ans_pattern...
            # The sample showed answers like "153. B: Heat is transferred...". 
            # If an answer was misformatted it might fall here, but we will assume it's just a question start.
            if num not in seen_q_nums:
                current_num = num
                seen_q_nums.add(num)
                mode = "question"
                questions[num] = {
                    "question_text": text + "\n",
                    "options": {}
                }
                current_opt = None
                if num > max_q_num: max_q_num = num
                continue
            else:
                # If we've seen the question, and it's not an answer match, maybe we append to previous answer?
                if current_num in answers and mode == "answer":
                    answers[current_num]["explanation"] += line + "\n"
                continue
                
        # Check for options
        if mode == "question" or mode == "option":
            m_opt = opt_pattern.match(line)
            if m_opt:
                mode = "option"
                current_opt = m_opt.group(1).lower()
                questions[current_num]["options"][current_opt] = m_opt.group(2) + "\n"
            else:
                if mode == "question":
                    questions[current_num]["question_text"] += line + "\n"
                elif mode == "option" and current_opt:
                    questions[current_num]["options"][current_opt] += line + "\n"
                    
    # Compile
    parsed_items = []
    
    # We will only append items that appear to be complete or at least valid
    for q_num, q_data in sorted(questions.items()):
        q_text = q_data["question_text"].strip()
        opts = {k: v.strip() for k, v in q_data["options"].items()}
        
        # If no options found, maybe it wasn't a real question
        if not opts:
            continue
            
        ans_data = answers.get(q_num, {})
        correct_ans = ans_data.get("correct", None)
        explanation = ans_data.get("explanation", "").strip()
        
        parsed_items.append({
            "id": start_global_id,
            "question": q_text,
            "options": opts,
            "answer": correct_ans,
            "explanation": explanation
        })
        start_global_id += 1
        
    print(f"Extracted {len(parsed_items)} questions from this file.")
    return parsed_items

if __name__ == "__main__":
    if os.path.exists(existing_file):
        with open(existing_file, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
    else:
        all_data = []
        
    start_id = 1
    if all_data:
        start_id = max([q["id"] for q in all_data]) + 1
        print(f"Loaded {len(all_data)} existing questions. Starting new IDs at {start_id}")
        
    new_data = parse_practice_file(pdf_path, start_id)
    
    all_data.extend(new_data)
    with open(existing_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)
        
    print(f"Saved total of {len(all_data)} questions to {existing_file}")
