from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

# Đồng bộ với test: lower bound = 1900
LOWER_BOUND = 1900

@app.route("/", methods=["GET", "POST"])
def index():
    age = None
    birth_year = None
    error = None
    current_year = datetime.now().year

    if request.method == "POST":
        try:
            raw = request.form.get("birth_year")
            # Nếu rỗng/None, sẽ gây ValueError và vào except -> "Dữ liệu không hợp lệ."
            birth_year = int(raw)
            if birth_year < LOWER_BOUND or birth_year > current_year:
                error = f"Vui lòng chọn năm sinh từ {LOWER_BOUND} đến {current_year}."
            else:
                age = current_year - birth_year
        except:
            error = "Dữ liệu không hợp lệ."

    return render_template(
        "index.html",
        age=age,
        birth_year=birth_year,
        error=error,
        lower_bound=LOWER_BOUND,
        current_year=current_year
    )

if __name__ == "__main__":
    app.run(debug=True)
