from app.services.categorization import infer_category, infer_employment_type


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
    # Title alone doesn't hint at a category; description does.
    result = infer_category("Summer Intern", description="Build ETL pipelines with dbt.")
    assert result == "Data Engineering"


def test_infer_employment_type_internship():
    assert infer_employment_type("Software Engineering Intern") == "Internship"


def test_infer_employment_type_new_grad():
    assert infer_employment_type("Software Engineer, New Grad") == "New Grad"


def test_infer_employment_type_none_when_unclear():
    assert infer_employment_type("Senior Software Engineer") is None
