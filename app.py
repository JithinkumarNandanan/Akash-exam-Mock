import streamlit as st
import json
import time
import random
import os

# Configuration
QUESTIONS_FILE = "questions.json"

def load_questions():
    if not os.path.exists(QUESTIONS_FILE):
        return []
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def initialize_session_state():
    if 'test_started' not in st.session_state:
        st.session_state.test_started = False
    
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
        
    if 'selected_questions' not in st.session_state:
        st.session_state.selected_questions = []

    if 'test_duration' not in st.session_state:
        st.session_state.test_duration = 3600
        
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {} # {q_id: option_key}
        
    if 'flagged_questions' not in st.session_state:
        st.session_state.flagged_questions = set()

    if 'visited_questions' not in st.session_state:
        st.session_state.visited_questions = set()
        
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

    if 'current_q_index' not in st.session_state:
        st.session_state.current_q_index = 0

def format_time(seconds):
    mins, secs = divmod(int(seconds), 60)
    return f"{mins:02d}:{secs:02d}"

def get_timer_script(start_time, duration):
    """
    Returns a Javascript script to display a ticking timer.
    It calculates remaining time on the client side.
    """
    remaining_time = duration - (time.time() - start_time)
    if remaining_time < 0:
        remaining_time = 0
        
    return f"""
    <div id="countdown-timer" style="
        font-size: 20px; 
        font-weight: bold; 
        color: #FF4B4B; 
        padding: 10px; 
        border: 2px solid #FF4B4B; 
        border-radius: 5px; 
        text-align: center;
        margin-bottom: 20px;">
        Loading Timer...
    </div>
    <script>
    var timeleft = {remaining_time};
    var timerElement = document.getElementById("countdown-timer");
    
    var downloadTimer = setInterval(function() {{
      if(timeleft <= 0){{
        clearInterval(downloadTimer);
        timerElement.innerHTML = "Time Finished";
      }} else {{
        var minutes = Math.floor(timeleft / 60);
        var seconds = Math.floor(timeleft % 60);
        timerElement.innerHTML = "Time Remaining: " + 
            minutes.toString().padStart(2, '0') + ":" + 
            seconds.toString().padStart(2, '0');
      }}
      timeleft -= 1;
    }}, 1000);
    </script>
    """

def main():
    st.set_page_config(page_title="CSP Mock Exam", layout="wide")
    
    # Load Data
    all_questions = load_questions()
    if not all_questions:
        st.error(f"Questions file not found at {QUESTIONS_FILE}. Please run the parser first.")
        return

    initialize_session_state()

    # Sidebar: Exam Status & Navigation
    with st.sidebar:
        st.title("Exam Controls")
        
        if st.session_state.test_started and not st.session_state.submitted:
            # Determine elapsed time for backend check
            elapsed = time.time() - st.session_state.start_time
            remaining = st.session_state.test_duration - elapsed
            
            if remaining <= 0:
                st.warning("Time is up!")
                st.session_state.submitted = True
                remaining = 0
            
            # Navigation Board
            st.markdown("---")
            st.markdown("### Question Palette")
            st.caption("✅ Answered | 🚩 Flagged | 👁️ Visited")
            
            questions = st.session_state.selected_questions
            
            # CSS for grid of buttons
            st.markdown("""
            <style>
            div[data-testid="stHorizontalBlock"] button {
                width: 100%;
                margin: 0px;
                padding: 0px;
                line-height: 1.2;
            }
            </style>
            """, unsafe_allow_html=True)

            # Create grid
            cols = st.columns(5)
            for i, q in enumerate(questions):
                q_id = q['id']
                label = f"{i+1}"
                
                # Dynamic Labeling
                status_icon = ""
                if q_id in st.session_state.user_answers:
                    status_icon = "✅"
                elif q_id in st.session_state.flagged_questions:
                    status_icon = "🚩"
                elif q_id in st.session_state.visited_questions:
                    status_icon = "👁️"
                
                # Check for Current Question Highlight
                if i == st.session_state.current_q_index:
                    label = f"[{label}]" 
                
                full_label = f"{label} {status_icon}"
                
                if cols[i % 5].button(full_label, key=f"nav_{i}"):
                    st.session_state.current_q_index = i
                    st.rerun()

            st.markdown("---")
            if st.button("Submit Exam", type="primary"):
                st.session_state.submitted = True
                st.rerun()
                
        elif not st.session_state.test_started and not st.session_state.submitted:
            st.markdown("### Select a Practice Test")
            test_options = [f"Test {i}" for i in range(1, 15)] + ["Random 100 Questions"]
            
            # Using radio buttons to show all options at once
            selected_test = st.radio("Available Tests:", test_options)
            
            if selected_test == "Test 14":
                st.caption("Contains exactly 80 questions. Time limit: 45 minutes.")
            elif selected_test.startswith("Test"):
                st.caption("Contains 100 questions. Time limit: 60 minutes.")
            else:
                st.caption("Contains 100 questions sampled randomly. Time limit: 60 minutes.")
                
            if st.button("Start Exam", type="primary"):
                if selected_test.startswith("Test"):
                    test_num = int(selected_test.split(" ")[1])
                    start_idx = (test_num - 1) * 100
                    
                    if test_num == 14:
                        end_idx = start_idx + 80
                        duration = 45 * 60
                    else:
                        end_idx = start_idx + 100
                        duration = 60 * 60
                        
                    selected_q = all_questions[start_idx:end_idx]
                else:
                    num_q = min(len(all_questions), 100)
                    selected_q = random.sample(all_questions, num_q)
                    duration = 60 * 60
                    
                st.session_state.selected_questions = selected_q
                st.session_state.test_duration = duration
                st.session_state.test_started = True
                st.session_state.start_time = time.time()
                st.rerun()

    # Main Area
    st.title("CSP Mock MCQ Exams")
    
    if not st.session_state.test_started:
        st.info("Welcome to the CSP Mock Exam.")
        st.write(f"Total Questions Available in Pool: {len(all_questions)}")
        st.write("👈 **Please select a test from the sidebar on the left to begin.**")
            
    elif st.session_state.submitted:
        show_results()
    
    else:
        # Display the timer at the top of the main area
        st.components.v1.html(get_timer_script(st.session_state.start_time, st.session_state.test_duration), height=80)
        show_question()

def show_question():
    q_idx = st.session_state.current_q_index
    questions = st.session_state.selected_questions
    current_q = questions[q_idx]
    q_id = current_q['id']
    
    # Mark as visited
    st.session_state.visited_questions.add(q_id)
    
    col_header, col_flag = st.columns([4, 1])
    with col_header:
        st.markdown(f"### Question {q_idx + 1} of {len(questions)}")
    with col_flag:
        is_flagged = q_id in st.session_state.flagged_questions
        if st.checkbox("🚩 Flag", value=is_flagged, key=f"flag_{q_id}"):
            st.session_state.flagged_questions.add(q_id)
        else:
            if q_id in st.session_state.flagged_questions:
                st.session_state.flagged_questions.remove(q_id)
                
    st.progress((q_idx + 1) / len(questions))
    
    st.markdown(f"**{current_q['question']}**")
    
    options = current_q['options']
    # Streamlit Radio requires a list. We need to map back the selected text to the key.
    opt_keys = sorted(options.keys())
    opt_labels = [f"{k}) {options[k]}" for k in opt_keys]
    
    # Handle current selection
    current_selection = st.session_state.user_answers.get(q_id, None)
    index = 0
    if current_selection:
        try:
            index = opt_keys.index(current_selection)
        except ValueError:
            index = 0 
            
    # Display Radio
    selected_label = st.radio(
        "Select your answer:",
        opt_labels,
        index=index if current_selection else None,
        key=f"radio_{q_id}"
    )
    
    # Update state immediately on selection
    if selected_label:
        selected_key = selected_label.split(')')[0]
        st.session_state.user_answers[q_id] = selected_key

    # Navigation Buttons (Next/Prev)
    col1, col2, col3 = st.columns([1, 4, 1])
    
    if q_idx > 0:
        if col1.button("⬅️ Previous"):
            st.session_state.current_q_index -= 1
            st.rerun()
            
    if q_idx < len(questions) - 1:
        if col3.button("Next ➡️"):
            st.session_state.current_q_index += 1
            st.rerun()

def show_results():
    st.markdown("## Exam Results")
    
    questions = st.session_state.selected_questions
    user_answers = st.session_state.user_answers
    
    score = 0
    total = len(questions)
    
    st.markdown("---")
    
    for i, q in enumerate(questions):
        q_id = q['id']
        # Fallback if answer wasn't extracted properly due to regex misses
        correct = (q.get('answer') or "").lower()
        selected = user_answers.get(q_id, None)
        
        is_correct = (selected == correct) if correct else False
        if is_correct:
            score += 1
            
        status = '✅ Correct' if is_correct else '❌ Incorrect'
        if not correct: status = "⚠️ Answer Key Missing"
        
        with st.expander(f"Q{i+1}: {q['question'][:80]}... - {status}"):
            st.markdown(f"**Question:** {q['question']}")
            
            st.markdown("**Options:**")
            for k, v in q['options'].items():
                prefix = ""
                if k == correct:
                    prefix = "✅ " 
                elif k == selected and not is_correct:
                    prefix = "❌ " 
                
                if k == correct or k == selected:
                     st.markdown(f"- {prefix}**{k}) {v}**")
                else:
                     st.markdown(f"- {prefix}{k}) {v}")
            
            st.markdown("---")
            st.markdown(f"**Your Answer:** {selected if selected else 'Not Answered'}")
            st.markdown(f"**Correct Answer:** {correct if correct else 'Unknown'}")
            st.info(f"**Explanation:** {q.get('explanation', 'No explanation provided.')}")
            
    percentage = (score / total) * 100 if total > 0 else 0
    
    st.metric(label="Final Score", value=f"{score}/{total}", delta=f"{percentage:.1f}%")
    
    if st.button("Restart Exam"):
        # Reset everything
        keys_to_delete = ['test_started', 'start_time', 'selected_questions', 'test_duration', 
                          'user_answers', 'submitted', 'current_q_index', 
                          'flagged_questions', 'visited_questions']
        for key in keys_to_delete:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

if __name__ == "__main__":
    main()
