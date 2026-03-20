# izone-hls — Hostel Lock System

## Project Structure

```
izone-hls/
├── backend/          # Django REST API
│   ├── hostel_project/   # Django project settings
│   ├── outpass/          # Main app (models, views, urls)
│   ├── manage.py
│   └── requirements.txt
└── frontend/         # Static HTML/CSS/JS UI
    ├── html/
    ├── css/
    ├── js/
    └── img/
```

## Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Frontend
Open `frontend/html/home.html` in a browser, or serve via a static server.
