from app.services.categorization import (
    infer_category,
    infer_employment_type,
    is_entry_level_friendly,
    is_senior_role,
)


def test_infer_category_software_engineering():
    assert infer_category("Software Engineer Intern") == "Software Engineering"


def test_infer_category_data_engineering():
    assert infer_category("Data Engineer, New Grad") == "Data Engineering"


def test_infer_category_ml():
    assert infer_category("Machine Learning Research Intern") == "Machine Learning / AI"


def test_infer_category_data_analytics():
    assert infer_category("Data Analyst") == "Data Analytics"


def test_infer_category_cloud_platform():
    assert infer_category("Site Reliability Engineer") == "Cloud / Platform Engineering"


def test_infer_category_none_when_no_match():
    assert infer_category("Executive Assistant") is None


def test_infer_category_uses_description_as_fallback():
    result = infer_category("Summer Intern", description="Build ETL pipelines with dbt.")
    assert result == "Data Engineering"


def test_infer_employment_type_internship():
    assert infer_employment_type("Software Engineering Intern") == "Internship"


def test_infer_employment_type_new_grad():
    assert infer_employment_type("Software Engineer, New Grad") == "New Grad"


def test_infer_employment_type_none_when_unclear():
    assert infer_employment_type("Senior Software Engineer") is None


def test_is_senior_role_detects_senior():
    assert is_senior_role("Senior Software Engineer") is True


def test_is_senior_role_detects_staff():
    assert is_senior_role("Staff Data Engineer") is True


def test_is_senior_role_detects_manager():
    assert is_senior_role("Engineering Manager") is True


def test_is_senior_role_detects_director():
    assert is_senior_role("Director of Platform Engineering") is True


def test_is_senior_role_false_for_plain_title():
    assert is_senior_role("Software Engineer") is False


def test_is_senior_role_avoids_false_positive_on_leadership():
    assert is_senior_role("Leadership Development Program Engineer") is False


def test_is_entry_level_friendly_true_for_intern():
    assert is_entry_level_friendly("Software Engineering Intern") is True


def test_is_entry_level_friendly_true_for_plain_title():
    assert is_entry_level_friendly("Software Engineer") is True


def test_is_entry_level_friendly_false_for_senior_title():
    assert is_entry_level_friendly("Senior Software Engineer") is False


def test_is_entry_level_friendly_false_for_director():
    assert is_entry_level_friendly("Director of Engineering") is False
