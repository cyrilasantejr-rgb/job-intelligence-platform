from app.services.ingestion_service import strip_html, transform_greenhouse_job

SAMPLE_GREENHOUSE_JOB = {
    "id": 123456,
    "title": "Software Engineering Intern - Summer 2027",
    "location": {"name": "New York, NY"},
    "absolute_url": "https://boards.greenhouse.io/acme/jobs/123456",
    "updated_at": "2026-08-15T10:30:00-04:00",
    "content": "<p>Work on <strong>backend systems</strong> this summer.</p>",
}


def test_strip_html_removes_tags():
    assert strip_html("<p>Hello <b>world</b></p>") == "Hello world"


def test_strip_html_handles_none():
    assert strip_html(None) is None


def test_strip_html_handles_empty_string():
    assert strip_html("") is None


def test_strip_html_handles_double_escaped_entities():
    double_escaped = "&lt;div&gt;&lt;p&gt;Join our team&amp;nbsp;today.&lt;/p&gt;&lt;/div&gt;"
    assert strip_html(double_escaped) == "Join our team today."


def test_transform_greenhouse_job_maps_fields():
    job_in = transform_greenhouse_job(SAMPLE_GREENHOUSE_JOB, company_name="Acme Corp")

    assert job_in.company_name == "Acme Corp"
    assert job_in.title == "Software Engineering Intern - Summer 2027"
    assert job_in.location == "New York, NY"
    assert job_in.application_url == "https://boards.greenhouse.io/acme/jobs/123456"
    assert job_in.description == "Work on backend systems this summer."
    assert job_in.date_posted is not None
    assert job_in.date_posted.isoformat() == "2026-08-15"


def test_transform_greenhouse_job_infers_category_and_employment_type():
    job_in = transform_greenhouse_job(SAMPLE_GREENHOUSE_JOB, company_name="Acme Corp")

    assert job_in.category == "Software Engineering"
    assert job_in.employment_type == "Internship"


def test_transform_greenhouse_job_handles_missing_location():
    payload = {**SAMPLE_GREENHOUSE_JOB, "location": None}
    job_in = transform_greenhouse_job(payload, company_name="Acme Corp")
    assert job_in.location is None


def test_transform_greenhouse_job_handles_missing_content():
    payload = {**SAMPLE_GREENHOUSE_JOB, "content": None}
    job_in = transform_greenhouse_job(payload, company_name="Acme Corp")
    assert job_in.description is None
