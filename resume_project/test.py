from model import preprocess, calculate_similarity, missing_skills, ats_score

# -------------------------------------
# 1. Test Text Cleaning
# -------------------------------------
def test_preprocess():
    raw_text = "Hello! Looking for a Python Developer @ 2024."
    clean_text = preprocess(raw_text)
    # Ensure it makes it lowercase and removes punctuation
    assert clean_text == "hello looking for a python developer  2024"

# -------------------------------------
# 2. Test Missing Skills Logic
# -------------------------------------
def test_missing_skills():
    resume = "i know python, git, and sql"
    job_desc = "we need a developer with python, sql, and pandas experience"
    
    missing = missing_skills(resume, job_desc)
    
    # "pandas" should be flagged as missing
    assert "pandas" in missing
    # "python" is in the resume, so it should NOT be flagged
    assert "python" not in missing

# -------------------------------------
# 3. Test Similarity Scoring
# -------------------------------------
def test_calculate_similarity():
    text1 = "machine learning developer"
    text2 = "machine learning developer"
    text3 = "completely unrelated retail worker"
    
    # Exact matches should be 100%
    perfect_score = calculate_similarity(text1, text2)
    assert perfect_score == 100.0
    
    # Unrelated texts should have a very low score
    bad_score = calculate_similarity(text1, text3)
    assert bad_score < 10.0

# -------------------------------------
# 4. Test ATS Rule-Based Scoring
# -------------------------------------
def test_ats_score():
    resume = "education experience python built designed"
    job = "python developer"
    
    score = ats_score(resume, job)
    
    # As long as it returns a positive float/int, the function works
    assert isinstance(score, (int, float))
    assert score > 0