import pytest
from pathlib import Path
from parser import Parser

@pytest.fixture
def parsed_data():
    path = Path(__file__).parent.parent/"data"/"sample.html"
    test_data = path.read_text(encoding="UTF-8")
    parser = Parser()
    return parser.parse(test_data)


def test_parsed_count(parsed_data: list):
    assert len(parsed_data) == 20

def test_is_hot_is_boolean(parsed_data: list):
    assert all(isinstance(record["is_hot"], bool) for record in parsed_data)
    assert any(record["is_hot"] for record in parsed_data)
    assert any(not record["is_hot"] for record in parsed_data)

@pytest.mark.parametrize("field", ["link", "title", "post_date"])
def test_required_fields(parsed_data: list, field):
    assert all(record[field].strip() for record in parsed_data)

def test_clean_link(parsed_data:list):
    assert all(record["link"].startswith("https://jobs.dou.ua/") for record in parsed_data)
    assert all("?" not in record["link"] for record in parsed_data)

def test_empty_input():
    html = "<html><body></body></html>"
    result = Parser().parse(html=html)
    assert result == []
