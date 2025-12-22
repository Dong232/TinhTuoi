import pytest
from datetime import datetime
from app import app  # import Flask app từ app.py

# Test client setup
@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

# Thông điệp lỗi mong đợi (nếu app dùng thông điệp khác -> cập nhật ở đây)
# Các giá trị này chỉ là gợi ý / phép kiểm tra "contains" — điều chỉnh cho khớp ứng dụng thực tế.
EXPECTED_ERROR_MISSING = ["Chưa nhập", "Vui lòng nhập", "không có dữ liệu"]
EXPECTED_ERROR_NON_NUMERIC = ["Dữ liệu không hợp lệ", "không hợp lệ"]
# Biên dưới tar = 1900 theo Decision Table
LOWER_BOUND = 1900

def contains_any(text, needles):
    return any(n in text for n in needles)

def post_birth_year(client, value):
    # Simulate form submit to "/"
    return client.post("/", data={"birth_year": value}, follow_redirects=True)

def test_valid_birth_year_returns_age(client):
    current_year = datetime.now().year
    birth_year = 1990
    expected_age = current_year - birth_year

    resp = post_birth_year(client, str(birth_year))
    html = resp.get_data(as_text=True)

    assert resp.status_code == 200
    # Kiểm tra tuổi (số) xuất hiện trên trang
    assert str(expected_age) in html, f"Expected age {expected_age} to appear in response HTML."

@pytest.mark.parametrize("input_value", ["", None])
def test_missing_birth_year_shows_error(client, input_value):
    # Gửi chuỗi rỗng hoặc không có giá trị
    post_value = "" if input_value is None else input_value
    resp = post_birth_year(client, post_value)
    html = resp.get_data(as_text=True)

    assert resp.status_code == 200
    assert contains_any(html, EXPECTED_ERROR_MISSING + EXPECTED_ERROR_NON_NUMERIC), (
        "Expected a missing-data or invalid-data error message to appear in response HTML."
    )

@pytest.mark.parametrize("input_value", ["abcd", "1990.5", "12.34"])
def test_non_numeric_birth_year_shows_error(client, input_value):
    resp = post_birth_year(client, input_value)
    html = resp.get_data(as_text=True)

    assert resp.status_code == 200
    assert contains_any(html, EXPECTED_ERROR_NON_NUMERIC), (
        "Expected a non-numeric / invalid-data error message to appear in response HTML."
    )

def test_birth_year_too_small_shows_error(client):
    # Biên dưới (LOWER_BOUND - 1)
    too_small = LOWER_BOUND - 1
    resp = post_birth_year(client, str(too_small))
    html = resp.get_data(as_text=True)

    assert resp.status_code == 200
    # Chúng ta mong thấy tham chiếu tới LOWER_BOUND hoặc thông báo lỗi
    assert (str(LOWER_BOUND) in html) or contains_any(html, EXPECTED_ERROR_NON_NUMERIC), (
        f"Expected an error message referencing lower bound {LOWER_BOUND} or 'invalid' message."
    )

def test_birth_year_too_large_shows_error(client):
    current_year = datetime.now().year
    too_large = current_year + 1
    resp = post_birth_year(client, str(too_large))
    html = resp.get_data(as_text=True)

    assert resp.status_code == 200
    # Mong thấy tham chiếu tới năm hiện tại (current_year) hoặc một thông báo lỗi chung
    assert (str(current_year) in html) or contains_any(html, EXPECTED_ERROR_NON_NUMERIC + EXPECTED_ERROR_MISSING), (
        "Expected an error message referencing current year or an invalid-data message."
    )
