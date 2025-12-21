from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    age = None
    birth_year = None
    error = None

    if request.method == "POST":
        try:
            birth_year = int(request.form.get("birth_year"))
            current_year = datetime.now().year

            if birth_year < 1950 or birth_year > current_year:
                error = "Vui lòng chọn năm sinh từ 1950 đến hiện tại."
            else:
                age = current_year - birth_year
        except:
            error = "Dữ liệu không hợp lệ."

    return render_template(
        "index.html",
        age=age,
        birth_year=birth_year,
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)
