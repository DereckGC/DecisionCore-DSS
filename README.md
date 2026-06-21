# DecisionCore DSS

DecisionCore DSS uses two small local servers:

- `portal.py`: Flask login portal rendered with HTML/CSS.
- `app.py`: Streamlit dashboard shown after login.
- `run_demo.py`: starts both servers together.
- `auth/users.py`: shared demo-user validation from `data/users_data.json`.
- `templates/login.html` and `static/login.css`: login page design.

## Run

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the demo:

```powershell
python run_demo.py
```

Open the login:

```text
http://localhost:5000
```

Demo credentials:

```text
admin@decisioncore.com
admin123
```

Do not open the dashboard first. The login portal redirects to Streamlit after successful access.
