import pdfplumber
import re
import json
import os

# Configuration
PDF_PATH = r"d:\Akash Exam\Previous question Paper\CSP Practice Questions (www.hsezip.com).pdf"
OUTPUT_JSON = r"d:\Akash Exam\questions.json"

def extract_text_from_pdf(pdf_path):
    """Extracts all text from the PDF."""
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Extracting text from {len(pdf.pages)} pages...")
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
    return full_text

def parse_questions_and_answers(full_text):
    """Parses questions, options, and answers from the text."""
    
    # 1. Split text into Question Section and Answer Key Section
    # Based on analysis, answer key starts around "153. B:" or similar late in the doc
    # But a safer way is to look for the transition. 
    # Let's try to detect where the "Question 1" vs "Answer 1" pattern changes, 
    # or just parse everything and associate later.
    
    # Actually, looking at the dump, questions are 1...152 (approx) and Answers are 153...200?
    # Wait, the dump showed "153. B:" in the answer key section? 
    # Let's re-examine the dump. 
    # Page 67 has "153. B: ..." 
    # Page 3 has "1. ...". 
    # It seems the questions go up to some number, and then the answer key might strictly follow?
    # OR, does the answer key start at 1?
    # Let's look at the dump again.
    # Page 3: "1. Within the realm..." -> Question 1
    # Page 67: "153. B: Heat is transferred..." -> This looks like an Answer explanation for Q153?
    # Wait, where is the answer for Question 1?
    # Maybe the PDF contains BOTH questions AND answers?
    # Let's assume the Answer Key is at the end.
    
    # Strategy:
    # 1. Extract all "Question Blocks".
    #    Regex: `^\d+\.` start a question.
    #    Options: `^[a-d]\.` start an option.
    # 2. Extract "Answer Blocks".
    #    Regex: `^\d+\.\s+[A-D]:` starts an answer with explanation.
    
    questions = {}
    answers = {}
    
    lines = full_text.split('\n')
    
    current_q_id = None
    buffer_text = []
    
    # Regex patterns
    q_start_pattern = re.compile(r'^(\d+)\.\s+(.*)')
    option_pattern = re.compile(r'^([a-d])\.\s+(.*)')
    answer_pattern = re.compile(r'^(\d+)\.\s+([A-D]):\s*(.*)')
    
    mode = "scan" # scan, question, answer_section
    
    # We'll just iterate and classify.
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Check for Answer Key Format first (matches "153. B: ...")
        ans_match = answer_pattern.match(line)
        if ans_match:
            # If we match an answer pattern, we are definitely in the answer/explanation part
            # (assuming questions don't look like "1. A: Text")
            q_id = int(ans_match.group(1))
            correct_opt = ans_match.group(2)
            explanation = ans_match.group(3)
            
            answers[q_id] = {
                "correct_option": correct_opt.lower(), # Store as 'a', 'b', 'c', 'd'
                "explanation": explanation
            }
            current_q_id = q_id # Track for multi-line explanations
            mode = "answer"
            continue
            
        # Check for Question Start
        q_match = q_start_pattern.match(line)
        if q_match:
            # If we find a new number, it could be a question OR a continuation of answers if regex failed?
            # But the answer regex is specific ("153. B:"). The question regex is "1. Text".
            # So this is likely a question.
            
            # Save previous question if exists
            if current_q_id is not None and mode == "question":
                # Save logic handled below
                pass
                
            q_id = int(q_match.group(1))
            q_text = q_match.group(2)
            
            # Initialize new question
            questions[q_id] = {
                "id": q_id,
                "question": q_text,
                "options": {},
                "img_ref": None # Placeholder
            }
            current_q_id = q_id
            mode = "question"
            continue
            
        # Check for Option (only valid if we are in 'question' mode)
        opt_match = option_pattern.match(line)
        if opt_match and mode == "question" and current_q_id:
            opt_label = opt_match.group(1).lower()
            opt_text = opt_match.group(2)
            questions[current_q_id]["options"][opt_label] = opt_text
            continue

        # Append continuation text
        if mode == "question" and current_q_id:
            # Is it an option continuation?
            last_opt = list(questions[current_q_id]["options"].keys())
            if last_opt:
                questions[current_q_id]["options"][last_opt[-1]] += " " + line
            else:
                questions[current_q_id]["question"] += " " + line
        
        elif mode == "answer" and current_q_id:
            if current_q_id in answers:
                answers[current_q_id]["explanation"] += " " + line

    return questions, answers

def merge_and_save(questions, answers, filename):
    """Merges Questions and Answers and saves to JSON."""
    final_data = []
    
    print(f"Found {len(questions)} questions and {len(answers)} answers.")
    
    for q_id in sorted(questions.keys()):
        q_data = questions[q_id]
        
        # Attach answer if available
        if q_id in answers:
            q_data["answer"] = answers[q_id]["correct_option"]
            q_data["explanation"] = answers[q_id]["explanation"]
            final_data.append(q_data)
        else:
            # If no answer found, should we include it? 
            # Maybe mark as "unknown"? Or just skip?
            # For a mock test, questions without answers are useless.
            print(f"Warning: No answer found for Question {q_id}. Skipping.")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2)
    
    print(f"Saved {len(final_data)} complete items to {filename}")

if __name__ == "__main__":
    text = extract_text_from_pdf(PDF_PATH)
    if text:
        # Save raw text for debugging
        with open(r"d:\Akash Exam\raw_text_dump.txt", "w", encoding="utf-8") as f:
            f.write(text)
            
        q, a = parse_questions_and_answers(text)
        merge_and_save(q, a, OUTPUT_JSON)
