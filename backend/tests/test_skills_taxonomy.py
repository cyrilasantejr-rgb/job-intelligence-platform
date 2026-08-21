from app.services.skills_taxonomy import extract_skills


def test_extract_skills_basic():
    result = extract_skills("Experienced in Python, SQL, and AWS.")
    assert result == ["AWS", "Python", "SQL"]


def test_extract_skills_sentence_final_punctuation():
    result = extract_skills("Built ETL pipelines with Airflow and dbt.")
    assert "Airflow" in result
    assert "dbt" in result
    assert "ETL" in result


def test_extract_skills_avoids_false_positive_substring():
    result = extract_skills("React developer, worked closely with Google.")
    assert result == ["React"]
    assert "Go" not in result


def test_extract_skills_dotted_skill_names():
    result = extract_skills("Built with Node.js and Next.js.")
    assert "Node.js" in result
    assert "Next.js" in result


def test_extract_skills_symbol_skills():
    result = extract_skills("C++ and C# experience, plus CI/CD pipelines.")
    assert set(result) == {"C++", "C#", "CI/CD"}


def test_extract_skills_case_insensitive():
    result = extract_skills("proficient in python and sql")
    assert "Python" in result
    assert "SQL" in result


def test_extract_skills_deduplicates():
    result = extract_skills("Python Python Python developer")
    assert result.count("Python") == 1


def test_extract_skills_handles_none():
    assert extract_skills(None) == []


def test_extract_skills_handles_empty_string():
    assert extract_skills("") == []


def test_extract_skills_no_matches():
    assert extract_skills("Excellent communicator and team player.") == []
