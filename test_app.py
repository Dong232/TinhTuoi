# Unit tests cho app tính tuổi (sử dụng pytest và Flask test client)
# File này đặt tại tests/test_app.py
#
# Chú thích:
# - Các test dùng Flask test_client để gửi POST tới endpoint "/".
# - Kỳ vọng dựa trên thông báo và giá trị được tạo trong app.py:
#     * Out-of-range message: f"Vui lòng chọn năm sinh từ {LOWER_BOUND} đến {current_year}."
#     * Parse error: "Dữ liệu không hợp lệ."
# - Mỗi test có ghi chú test case ID và kỹ thuật áp dụng (BVA = Boundary Value Analysis,
#   EP = Equivalence Partitioning, BB = Black-box).

import pytest
from datetime import datetime
from app import app, LOWER_BOUND

# Lấy năm hiện tại tại thời điểm chạy test
CURRENT_YEAR = datetime.now().year

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# -------------------------
# Test nhóm: giá trị hợp lệ (phân vùng hợp lệ, kiểm thử hộp đen)
# Các test: TC-01, TC-03, TC-04, TC-06, TC-11, TC-14
# Kỹ thuật: Equivalence Partitioning (hợp lệ) + Boundary Value (1950, current_year)
# -------------------------
@pytest.mark.parametrize("input_year, test_id, technique", [
    ("1950", "TC-01", "BVA (lower bound)"),        # biên dưới
    ("1951", "TC-03", "BVA"),                      # biên dưới +1
    (str(CURRENT_YEAR), "TC-04", "BVA (upper bound)"), # biên trên
    ("1990", "TC-06", "EP (mid-range)"),           # mid-range valid
    (" 1990 ", "TC-11", "EP (whitespace handling)"),# whitespace should be accepted
    (str(CURRENT_YEAR - 1), "TC-14", "BVA"),       # ngay sát biên trên
])
def test_valid_years_show_age(client, input_year, test_id, technique):
    """
    Test case nhóm hợp lệ: gửi năm hợp lệ -> hiển thị tuổi = current_year - birth_year
    Chú thích: test_id, technique
    """
    resp = client.post("/", data={"birth_year": input_year})
    body = resp.get_data(as_text=True)

    # Tính tuổi mong đợi
    expected_age = str(CURRENT_YEAR - int(input_year.strip()))
    assert expected_age in body, (
        f"{test_id} ({technique}) thất bại: mong đợi tuổi '{expected_age}' trong response.\n"
        f"Response body: {body}"
    )

# -------------------------
# Test nhóm: numeric nhưng ngoài khoảng (out-of-range)
# Các test: TC-02 (1949), TC-05 (current_year+1), TC-10 (-10), TC-12 (very large)
# Kỹ thuật: BVA + EP (numeric but invalid)
# -------------------------
@pytest.mark.parametrize("input_year, test_id, technique", [
    ("1949", "TC-02", "BVA (below lower bound)"),
    (str(CURRENT_YEAR + 1), "TC-05", "BVA (above current year)"),
    ("-10", "TC-10", "EP (negative number)"),
    ("10000000000", "TC-12", "EP (excessively large)"),
])
def test_numeric_out_of_range_shows_out_of_range_error(client, input_year, test_id, technique):
    """
    Nếu năm là số nhưng ngoài khoảng [LOWER_BOUND, CURRENT_YEAR] -> hiển thị lỗi out-of-range
    """
    resp = client.post("/", data={"birth_year": input_year})
    body = resp.get_data(as_text=True)

    expected_msg = f"Vui lòng chọn năm sinh từ {LOWER_BOUND} đến {CURRENT_YEAR}."
    assert expected_msg in body, (
        f"{test_id} ({technique}) thất bại: mong đợi message out-of-range '{expected_msg}'.\n"
        f"Response body: {body}"
    )

# -------------------------
# Test nhóm: không phải số / parse error / missing
# Các test: TC-07 (empty), TC-08 ("abc"), TC-09 ("1990.5"), TC-13 (injection)
# Kỹ thuật: EP (non-numeric), BB (hộp đen)
# -------------------------
@pytest.mark.parametrize("input_value, test_id, technique", [
    ("", "TC-07", "EP (empty input)"),                  # empty string -> parse error
    (None, "TC-07b", "EP (missing field)"),             # omitted field -> parse error
    ("abc", "TC-08", "EP (non-numeric)"),               # non-numeric string
    ("1990.5", "TC-09", "EP (decimal string)"),         # decimal string -> int() fails
    ("1; DROP TABLE users", "TC-13", "EP (injection-like)"), # malicious-looking string
])
def test_non_numeric_or_missing_shows_parse_error(client, input_value, test_id, technique):
    """
    Nếu input không thể chuyển sang int (hoặc không có) -> hiển thị "Dữ liệu không hợp lệ."
    """
    # Khi input_value là None: không gửi trường birth_year (mô phỏng submit rỗng)
    data = {} if input_value is None else {"birth_year": input_value}
    resp = client.post("/", data=data)
    body = resp.get_data(as_text=True)

    expected_msg = "Dữ liệu không hợp lệ."
    assert expected_msg in body, (
        f"{test_id} ({technique}) thất bại: mong đợi parse error '{expected_msg}'.\n"
        f"Response body: {body}"
    )

# -------------------------
# Extra sanity test: kiểm tra rằng khi POST GET khác nhau vẫn trả page (smoke)
# -------------------------
def test_get_homepage_contains_form(client):
    """
    Smoke test: GET / trả về trang (kiểm tra có tồn tại form input 'birth_year' trong HTML).
    Đây là kiểm thử hộp đen, đảm bảo endpoint GET vẫn trả page.
    """
    resp = client.get("/")
    body = resp.get_data(as_text=True)

    # Chỉ kiểm tra tồn tại chuỗi 'birth_year' (field name), không phụ thuộc vào template chi tiết
    assert "birth_year" in body, "GET / không chứa trường 'birth_year' trong response."
