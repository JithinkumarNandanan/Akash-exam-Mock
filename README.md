# CSP Mock MCQ Exam App

This is a Streamlit-based web application that simulates a timed Multiple Choice Question (MCQ) exam using questions extracted from your PDF documents.

## Features
-   **Timed Exam**: 60-minute countdown timer.
-   **Randomized Questions**: Selects 40 random questions from the pool for each session.
-   **Review System**: Instant feedback after submission with correct answers and explanations.
-   **Question Palette**: easy navigation between questions.

## Setup & Running

1.  **Install Dependencies**:
    ```bash
    pip install streamlit pdfplumber
    ```

2.  **Extract Data (if needed)**:
    If `questions.json` is missing or you want to re-parse the PDF:
    ```bash
    python pdf_parser.py
    ```

3.  **Run the App**:
    ```bash
    streamlit run app.py
    ```
    The app will open in your default web browser (usually at `http://localhost:8501`).

## Files
-   `app.py`: The main Streamlit application.
-   `pdf_parser.py`: Script to extract questions/answers from the PDF.
-   `questions.json`: The extracted data store.
