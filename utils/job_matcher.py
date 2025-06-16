from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy # Needed for potential skill parsing from JD

# nlp object will be loaded if/when needed for skill parsing
nlp_jm = None # Using a different variable name to avoid confusion if App.py also uses 'nlp'

def load_spacy_model_for_job_matcher():
    """Loads the spaCy model if not already loaded."""
    global nlp_jm
    if nlp_jm is None:
        try:
            nlp_jm = spacy.load('en_core_web_sm')
            print("spaCy model 'en_core_web_sm' loaded successfully for job_matcher.")
        except OSError:
            print("CRITICAL: Failed to load spaCy model 'en_core_web_sm' in job_matcher.")
            print("Ensure 'en_core_web_sm' is installed (e.g., via requirements.txt).")
            # Depending on strictness, could raise an exception or allow fallback
            # For now, functions relying on it will have to handle nlp_jm being None.
        except Exception as e:
            print(f"An unexpected error occurred while loading spaCy model in job_matcher: {e}")

def match_resume_to_jd(resume_text, jd_text):
    """
    Calculates the cosine similarity between resume text and job description text
    using TF-IDF vectors.
    Returns the similarity score as a percentage.
    """
    if not resume_text or not jd_text:
        return 0.0

    vectorizer = TfidfVectorizer(stop_words='english')

    try:
        # Fit and transform the texts
        vectors = vectorizer.fit_transform([resume_text, jd_text])

        # Calculate cosine similarity
        # vectors[0] is the resume_text vector, vectors[1] is the jd_text vector
        similarity_matrix = cosine_similarity(vectors[0:1], vectors[1:2]) # Ensure 2D arrays for cosine_similarity

        # The result is a 2D array (matrix), get the single similarity value
        similarity_score = similarity_matrix[0][0]

        return round(similarity_score * 100, 2)

    except Exception as e:
        print(f"Error calculating TF-IDF similarity: {e}")
        return 0.0

def extract_skills_from_text(text, skills_matcher_nlp_instance, predefined_skills_list=None):
    """
    Extracts skills from a given text using spaCy's Matcher.
    This is a helper that might be used by both resume parser and JD matcher.
    Requires an initialized spaCy nlp instance.
    """
    if not text or not skills_matcher_nlp_instance:
        return []

    doc = skills_matcher_nlp_instance(text)
    matcher = spacy.matcher.Matcher(skills_matcher_nlp_instance.vocab)

    if predefined_skills_list is None:
        # Using a similar default list as in resume_parser for consistency
        predefined_skills_list = [
            "python", "java", "c++", "javascript", "react", "angular", "vue", "node.js",
            "sql", "nosql", "mongodb", "postgresql", "mysql",
            "aws", "azure", "gcp", "docker", "kubernetes",
            "machine learning", "deep learning", "tensorflow", "pytorch", "keras", "scikit-learn",
            "data analysis", "data science", "pandas", "numpy", "matplotlib", "seaborn",
            "natural language processing", "nlp", "spacy", "nltk",
            "agile", "scrum", "jira", "git", "communication", "problem solving", "teamwork"
        ]

    for skill in predefined_skills_list:
        pattern = [{"LOWER": token} for token in skill.split()]
        matcher.add(skill.upper(), [pattern])

    matches = matcher(doc)
    found_skills = set(skills_matcher_nlp_instance.vocab.strings[match_id].lower() for match_id, _, _ in matches)
    return list(found_skills)

def compare_skills(resume_skills, jd_skills):
    """
    Compares skills extracted from the resume and job description.
    Returns a dictionary with matched_skills and missing_skills (from JD).
    """

    # Ensure inputs are sets for efficient comparison
    set_resume_skills = set(skill.lower() for skill in resume_skills)
    set_jd_skills = set(skill.lower() for skill in jd_skills)

    matched_skills = list(set_resume_skills.intersection(set_jd_skills))
    missing_skills = list(set_jd_skills.difference(set_resume_skills))

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "jd_skills_parsed": list(set_jd_skills) # Return all unique skills parsed from JD
    }

if __name__ == '__main__':
    print("Job Matcher Module - Running Test")

    # Ensure spaCy model is loaded for tests that need it
    load_spacy_model_for_job_matcher()

    sample_resume_text = "Experienced Python developer with skills in Django, Flask, and data analysis. Proficient in SQL and Git."
    sample_jd_text = "Seeking a Python developer with Django experience. Key skills include REST API development, SQL, and Agile methodologies. Knowledge of data analysis is a plus."

    # Test TF-IDF similarity
    similarity = match_resume_to_jd(sample_resume_text, sample_jd_text)
    print(f"\nTF-IDF Similarity: {similarity}%")

    if nlp_jm: # Proceed only if spaCy model loaded
        # Test skill extraction (can use the helper function)
        resume_skills_list = extract_skills_from_text(sample_resume_text, nlp_jm)
        jd_skills_list = extract_skills_from_text(sample_jd_text, nlp_jm)

        print(f"\nResume Skills Extracted: {resume_skills_list}")
        print(f"JD Skills Extracted: {jd_skills_list}")

        # Test skill comparison
        comparison_results = compare_skills(resume_skills_list, jd_skills_list)
        print(f"\nSkill Comparison Results:")
        print(f"  Matched Skills: {comparison_results['matched_skills']}")
        print(f"  Missing Skills (from JD): {comparison_results['missing_skills']}")
        print(f"  All JD Skills Parsed: {comparison_results['jd_skills_parsed']}")
    else:
        print("\nSkipping skill extraction/comparison tests as spaCy model failed to load.")
