import pytest
from datetime import datetime

# Import app và LOWER_BOUND từ file app.py trong cùng repository
from app import app as flask_app, LOWER_BOUND

current_year = datetime.now().year

@pytest.fixture
def client():
    flask_app.testing = True
    with flask_app.test_client() as client:
        yield client

@pytest.mark.parametrize("input_value, expect_type, expect", [
    # Hợp lệ
    ("1990", "age", current_year - 1990),            # TC01
    (str(1950), "age", current_year - 1950),         # TC02 lower bound
    (str(current_year), "age", 0),                   # TC03 upper bound (năm hiện tại)

    # Ngoài phạm vi
    ("1949", "error_range", f"Vui lòng chọn năm sinh từ {LOWER_BOUND} đến {current_year}."),  # TC04
    (str(current_year + 1), "error_range", f"Vui lòng chọn năm sinh từ {LOWER_BOUND} đến {current_year}."),  # TC05

    # Dữ liệu không hợp lệ (non-numeric / empty / float / alphanumeric / malicious)
    ("", "error_invalid", "Dữ liệu không hợp lệ."),        # TC06 empty
    ("abcd", "error_invalid", "Dữ liệu không hợp lệ."),    # TC07 non-numeric
    ("1990.5", "error_invalid", "Dữ liệu không hợp lệ."),  # TC08 float string
    (" 1990 ", "age", current_year - 1990),               # TC09 whitespace (hợp lệ)
    ("01990", "age", current_year - 1990),                # TC10 leading zeros (hợp lệ)
    ("-1980", "error_range", f"Vui lòng chọn năm sinh từ {LOWER_BOUND} đến {current_year}."),  # TC11 negative -> out of range
    ("100000", "error_range", f"Vui lòng chọn năm sinh từ {LOWER_BOUND} đến {current_year}."), # TC12 too large
    ("199a", "error_invalid", "Dữ liệu không hợp lệ."),    # TC13 alphanumeric
    ("01/01/1990", "error_invalid", "Dữ liệu không hợp lệ."), # TC14 date format
    ("2020; DROP TABLE users;", "error_invalid", "Dữ liệu không hợp lệ."), # TC15 injection-like
])
def test_birth_year_post(client, input_value, expect_type, expect):
    resp = client.post("/", data={"birth_year": input_value})
    text = resp.get_data(as_text=True)

    # Với trường hợp trả về age: kiểm tra số tuổi xuất hiện trong HTML
    if expect_type == "age":
        assert str(expect) in text, f"Expected age {expect} to appear in response for input {input_value}. Response:\n{text}"

    # Trường hợp lỗi do vượt ngoài phạm vi (range error)
    elif expect_type == "error_range":
        assert expect in text, f"Expected range error message for input {input_value}. Response:\n{text}"

    # Trường hợp dữ liệu không hợp lệ (parse error / empty / non-numeric)
    elif expect_type == "error_invalid":
        assert expect in text, f"Expected invalid-data error message for input {input_value}. Response:\n{text}"

    else:
        pytest.fail("Unknown expect_type")
