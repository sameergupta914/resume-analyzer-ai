# AI Resume Analyzer v2

## Overview

This application analyzes resumes and matches them against job descriptions using Natural Language Processing (NLP). It extracts key information from resumes, identifies relevant skills from both the resume and the job description, calculates an overall match score, and highlights skill gaps.

This project is an enhanced version, re-engineered by Jules for improved stability, accuracy, and a more streamlined user interface. It leverages Python, Streamlit, spaCy, and scikit-learn.

## Features

-   Parses resumes in PDF and DOCX formats.
-   Extracts candidate information: Name, Email, Phone, Education (basic).
-   Identifies skills from both resumes and job descriptions.
-   Calculates a TF-IDF based cosine similarity score between the resume and job description.
-   Provides a skills gap analysis: matched skills and skills missing from the resume based on the job description.
-   Visualizes skill comparison using Plotly charts.
-   User-friendly web interface built with Streamlit.

## Project Structure

```
AI-Resume-Analyzer/
├── App.py                # Main Streamlit application
├── utils/
│   ├── resume_parser.py  # Module for parsing resume files
│   └── job_matcher.py    # Module for matching resume to job description
├── requirements.txt      # Python dependencies
├── .gitignore            # Files and directories to be ignored by Git
├── Logo/                 # Contains application logo
│   └── RESUM.png
└── README.md             # This file
```

## Setup and Installation

1.  **Clone the repository (if applicable):**
    ```bash
    # git clone <repository_url>
    # cd AI-Resume-Analyzer
    ```

2.  **Create a Python virtual environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    -   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
    -   On Windows:
        ```bash
        .\\venv\\Scripts\\activate
        ```

4.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    This will install all necessary libraries, including Streamlit, spaCy, scikit-learn, and the specific English language model for spaCy.

## How to Run

1.  Ensure your virtual environment is activated and dependencies are installed.
2.  Navigate to the project's root directory (where `App.py` is located).
3.  Run the Streamlit application using the following command:
    ```bash
    streamlit run App.py
    ```
4.  The application should open in your default web browser.

## Usage

-   Select the "Resume Analysis" mode from the sidebar.
-   Upload a resume file (PDF or DOCX).
-   Paste the job description into the text area.
-   Click the "Analyze" button.
-   Review the analysis, including the match score, extracted information, and skills breakdown.

---
*Original application concept by Deepak Padhi. Current version enhanced by Jules.*
