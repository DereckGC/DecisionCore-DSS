from pathlib import Path
from urllib.parse import urlencode

from flask import Flask, redirect, render_template, request, send_from_directory

from auth.users import validate_credentials


STREAMLIT_URL = "http://localhost:8501"
BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)


@app.route("/assets/<path:filename>")
def assets_file(filename):
    return send_from_directory(BASE_DIR / "assets", filename)


@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    email = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = validate_credentials(email, password)

        if user:
            query = urlencode({"access": "demo", "email": user["email"]})
            return redirect(f"{STREAMLIT_URL}?{query}")

        error = "Credenciales incorrectas. Verifica el correo y la contraseña."

    return render_template("login.html", email=email, error=error)


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
