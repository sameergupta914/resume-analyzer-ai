# Main Application - AI Resume Analyzer v2
# Significantly modified by Jules.

import streamlit as st
import base64
import os
import tempfile
from PIL import Image
import plotly.express as px # Added for Plotly charts

# Utility Modules
from utils.resume_parser import parse_resume
from utils.job_matcher import match_resume_to_jd, extract_skills_from_text, compare_skills, load_spacy_model_for_job_matcher
from utils import job_matcher # To access job_matcher.nlp_jm

# --- Helper Functions ---
def show_pdf_from_bytes(file_bytes, width=700, height=1000):
    base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="{width}" height="{height}" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- Page Configuration ---
st.set_page_config(
   page_title="AI Resume Analyzer v2",
   page_icon='Logo/RESUM.png', # Adjusted path for consistency
   layout="wide" # Use wide layout for better column display
)

# --- Global NLP Model Management ---
def ensure_job_matcher_nlp_loaded():
    """Ensures the spaCy model in job_matcher is loaded."""
    if job_matcher.nlp_jm is None:
        load_spacy_model_for_job_matcher() # This function is from job_matcher.py

# --- Main Application Logic ---
def run():
    ensure_job_matcher_nlp_loaded()

    # Logo
    try:
        logo_path = 'Logo/RESUM.png' # Path relative to project root
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            st.image(img, width=200) # Control logo width
        else:
            st.warning(f"Logo image not found at {logo_path}")
    except Exception as e:
        st.error(f"Error loading logo: {e}")

    # Sidebar Navigation
    st.sidebar.markdown("# Choose Mode")
    activities = ["Resume Analysis", "Feedback", "About"]
    choice = st.sidebar.selectbox("Choose an option:", activities)

    # --- Resume Analysis Mode ---
    if choice == 'Resume Analysis':
        st.header("Resume and Job Description Analyzer")

        # Input Columns
        input_col1, input_col2 = st.columns([0.6, 0.4]) # Adjust column ratios as needed

        with input_col1:
            st.markdown("#### 1. Upload Your Resume")
            uploaded_resume_file = st.file_uploader("Supported formats: PDF, DOCX", type=["pdf", "docx"], key="resume_uploader")

        with input_col2:
            st.markdown("#### 2. Paste Job Description")
            job_description_text = st.text_area("Paste the full job description here...", height=270, key="jd_input")

        analyze_button = st.button("Analyze", key="analyze_button", use_container_width=True)

        if analyze_button and uploaded_resume_file is not None and job_description_text.strip():
            with st.spinner('Processing... Please wait.'):
                temp_file_path = None # Initialize to None
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_resume_file.name)[1]) as tmp_file:
                        tmp_file.write(uploaded_resume_file.getvalue())
                        temp_file_path = tmp_file.name

                    resume_data = parse_resume(temp_file_path)

                    if not resume_data or "error" in resume_data:
                        st.error(f"Failed to parse resume: {resume_data.get('error', 'Unknown parsing error')}")
                        return

                    resume_text_content = resume_data.get("text", "")
                    overall_match_score = match_resume_to_jd(resume_text_content, job_description_text)

                    jd_extracted_skills = []
                    if job_matcher.nlp_jm:
                         jd_extracted_skills = extract_skills_from_text(job_description_text, job_matcher.nlp_jm)
                    else:
                        st.warning("Could not extract JD skills: spaCy model for Job Matcher not available.")

                    skills_comparison_results = compare_skills(resume_data.get("skills", []), jd_extracted_skills)

                    st.success("Analysis Complete!")
                    st.markdown("<hr/>", unsafe_allow_html=True)
                    st.subheader("📊 Analysis Dashboard")

                    # Output Columns
                    score_col, skills_col = st.columns([0.4, 0.6])

                    with score_col:
                        st.markdown("##### Scorecard")
                        st.metric(label="Overall JD Match Score", value=f"{overall_match_score}%")
                        st.progress(int(overall_match_score) / 100)

                        st.markdown("**📄 Extracted Resume Info:**")
                        st.text(f"Name: {resume_data.get('name', 'N/A')}")
                        st.text(f"Email: {resume_data.get('email', 'N/A')}")
                        st.text(f"Phone: {resume_data.get('phone', 'N/A')}")
                        with st.expander("View Extracted Education Info"):
                            st.text(resume_data.get('education', 'N/A'))

                    with skills_col:
                        st.markdown("##### Skills Analysis")
                        num_matched_skills = len(skills_comparison_results.get('matched_skills', []))
                        num_missing_skills = len(skills_comparison_results.get('missing_skills', []))
                        num_jd_skills = len(jd_extracted_skills)

                        if num_jd_skills > 0:
                            # Data for chart
                            skills_chart_data = {
                                'Category': ['Matched Skills', 'Missing Skills (from JD)'],
                                'Count': [num_matched_skills, num_missing_skills]
                            }
                            try:
                                fig = px.bar(skills_chart_data, x='Category', y='Count', title='Resume vs. JD Skills Match', color='Category', color_discrete_map={'Matched Skills':'green', 'Missing Skills (from JD)':'red'})
                                fig.update_layout(showlegend=False)
                                st.plotly_chart(fig, use_container_width=True)
                            except Exception as e_chart:
                                st.warning(f"Could not generate skills chart: {e_chart}")
                        else:
                            st.info("No skills parsed from Job Description to generate a chart.")

                        st.markdown("**🛠️ Skills from Resume:**")
                        st.info(", ".join(resume_data.get("skills", ["N/A"])))

                        st.markdown("**🎯 Skills Parsed from JD:**")
                        st.text(", ".join(jd_extracted_skills if jd_extracted_skills else ["N/A"]))

                        st.markdown("**✅ Matched Skills:**")
                        st.success(", ".join(skills_comparison_results.get('matched_skills', ["N/A"])) )

                        st.markdown("**⚠️ Missing Skills (for JD):**")
                        st.warning(", ".join(skills_comparison_results.get('missing_skills', ["N/A"])) )

                except Exception as e:
                    st.error(f"An unexpected error occurred during analysis: {e}")
                finally:
                    if temp_file_path and os.path.exists(temp_file_path):
                        try:
                            os.remove(temp_file_path)
                        except Exception as e_remove:
                            st.error(f"Error removing temporary file: {e_remove}")

        elif analyze_button:
            if uploaded_resume_file is None: st.warning("Please upload your resume.")
            if not job_description_text.strip(): st.warning("Please paste the job description.")

    # --- Feedback Mode ---
    elif choice == 'Feedback':
        st.subheader("🗣️ Provide Feedback")
        # ... (Feedback form as before) ...
        st.info("This form is for demonstration. Submissions are not currently stored.")
        with st.form("feedback_form"):
            feed_name = st.text_input('Your Name (Optional)')
            feed_email = st.text_input('Your Email (Optional)')
            feed_score = st.slider('Overall Satisfaction (1=Low, 5=High)', 1, 5, 3)
            comments = st.text_area('Specific comments or suggestions:')
            submitted = st.form_submit_button("Submit Feedback")
            if submitted:
                st.success("Thank you for your feedback!")
                st.balloons()

    # --- About Mode ---
    elif choice == 'About':
        st.subheader("ℹ️ About AI Resume Analyzer v2")
        # ... (About text as before) ...
        st.markdown("""
        <p align='justify'>
            This tool leverages Natural Language Processing to parse resumes and match them against job descriptions.
            It extracts key candidate information, identifies relevant skills, and provides a similarity score to help assess fit.
            This version has been re-engineered by Jules for improved stability and accuracy using spaCy and scikit-learn.
        </p>
        <p align="justify">
            <b>How to use:</b> <br/>
            1. Go to the 'Resume Analysis' section from the sidebar.<br/>
            2. Upload a resume (PDF or DOCX format).<br/>
            3. Paste the complete job description into the provided text area.<br/>
            4. Click the 'Analyze' button.<br/>
            5. Review the extracted details, skill analysis, and match score.
        </p><br/>
        <p><i>Original application concept by Deepak Padhi. Current version enhanced by Jules.</i></p>
        """, unsafe_allow_html=True)

if __name__ == '__main__':
    run()
