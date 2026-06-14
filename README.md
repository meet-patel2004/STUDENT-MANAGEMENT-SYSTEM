# 📚 Student Management System

A full-stack Student Management System built with **Flask** (REST API backend) and a **single-page HTML/CSS/JS frontend**. It supports role-based access control (admin, teacher, student), JWT authentication, attendance tracking, marks management, academic reports, and data exports.

---

## 🗂️ Project Structure

```
sms/
├── app.py              # App entry point, config, shared utilities
├── auth.py             # Authentication routes (register, login, profile)
├── student.py          # Student CRUD operations
├── attendance.py       # Attendance tracking and analytics
├── marks.py            # Marks/grades management
├── reports.py          # Reports, transcripts, rankings, dashboard
├── exports.py          # CSV/Excel data export
├── helper.py           # Shared utilities (grading, GPA, role guards)
├── sms.sql             # Database schema
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (create this)
└── frontend/
    └── index.html      # ← Full frontend (single HTML file)
```

---

## ⚙️ Requirements

- Python 3.8+
- MySQL 5.7+ or MariaDB
- A modern web browser (Chrome, Firefox, Edge)
- pip packages (see `requirements.txt`):

```
Flask==3.0.3
Flask-MySQLdb==2.0.0
Flask-Bcrypt==1.0.1
Flask-JWT-Extended==4.6.0
openpyxl==3.1.0
reportlab==4.1.0
python-dotenv==1.0.0
```

---

## 🚀 Setup & Installation (Step-by-Step)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/meet-patel2004/STUDENT-MANAGEMENT-SYSTEM.git
cd STUDENT-MANAGEMENT-SYSTEM
```

---

### Step 2 — Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

---

### Step 3 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 4 — Set Up the MySQL Database

Make sure MySQL is running, then import the schema:

```bash
mysql -u root -p < sms.sql
```

This creates the `SMS` database with all required tables:
- `users` — system users (admin, teacher, student)
- `students` — student profiles
- `attendance` — daily attendance records
- `marks` — assessment scores and grades

---

### Step 5 — Configure Environment Variables

Create a `.env` file in the project root:

```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=SMS
JWT_SECRET_KEY=your-very-secret-key-change-this
```

> ⚠️ **Important:** Always use a strong, random `JWT_SECRET_KEY` in production. Never commit `.env` to version control.

**Alternative — set via terminal:**

**Linux/macOS:**
```bash
export MYSQL_HOST=localhost
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_DB=SMS
export JWT_SECRET_KEY=your-secret-key
```

**Windows (Command Prompt):**
```cmd
set MYSQL_HOST=localhost
set MYSQL_USER=root
set MYSQL_PASSWORD=your_password
set MYSQL_DB=SMS
set JWT_SECRET_KEY=your-secret-key
```

---

### Step 6 — Enable CORS (Required for Frontend)

The frontend runs from a browser and makes requests to `http://localhost:5000`. You must enable CORS in the Flask backend.

**Install Flask-CORS:**
```bash
pip install flask-cors
```

**Add to `app.py`** (after `app = Flask(__name__)`):
```python
from flask_cors import CORS
CORS(app, supports_credentials=True)
```

---

### Step 7 — Run the Flask Backend

```bash
python app.py
```

The API will be available at: **`http://localhost:5000`**

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

---

### Step 8 — Open the Frontend

Simply open the `frontend/index.html` file in your browser:

**Option A — Double-click the file**
Navigate to `frontend/index.html` and open it directly in Chrome or Firefox.

**Option B — Use VS Code Live Server**
If you have the Live Server extension:
1. Right-click `index.html` → "Open with Live Server"

**Option C — Use Python's built-in server**
```bash
cd frontend
python -m http.server 8080
```
Then open **`http://localhost:8080`** in your browser.

> **Note:** Make sure the Flask backend is running on port 5000 before using the frontend.

---

### Step 9 — Create Your First Admin Account

On the frontend login page, click **Register** and create an account with role `admin`.

> ⚠️ Only **one admin** account can be created. Subsequent admin registrations will be blocked by the API.

---

## 🖥️ Frontend Overview

The frontend is a **single-page application** (`index.html`) with no external dependencies — pure HTML, CSS, and JavaScript.

### Pages / Sections

| Section | Description |
|---|---|
| **Dashboard** | System-wide stats: average grade, attendance rate, pass/fail counts, top 5 students, and today's daily attendance |
| **Students** | Paginated list with search/filter by name, course, and department. View, edit, or delete any student |
| **Add Student** | Full form to register a new student with all fields |
| **Attendance** | Mark attendance for a student; view records with date range filter; analytics with visual progress bars |
| **Marks & Grades** | Add marks for any student; view marks history with subject breakdown |
| **Reports** | Summary report, performance & GPA, full semester transcript, department ranking, and PDF report card download |
| **Export Data** | Download Students, Marks, or Attendance data as CSV or Excel (.xlsx) |

### Design Highlights

- 🌑 **Dark theme** with a clean, professional sidebar layout
- 🔐 **JWT authentication** — token stored in localStorage, auto-attached to every request
- 📱 **Responsive** — adapts to smaller screens
- ✅ **Toast notifications** for success/error feedback
- 🔍 **Live search** on the Students page
- 📄 **Paginated** student table with navigation controls

---

## 🔐 Authentication

All protected routes require a **Bearer JWT token** in the `Authorization` header (handled automatically by the frontend):

```
Authorization: Bearer <your_token>
```

### Roles

| Role | Permissions |
|---|---|
| `admin` | Full access — manage students, teachers, all data, delete records |
| `teacher` | Add/update students, record marks and attendance |
| `student` | Read-only access to data |

---

## 📡 API Reference

### Auth

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | Public | Register a new user |
| POST | `/auth/login` | Public | Login and receive JWT token |
| GET | `/auth/me` | JWT | Get current user profile |

**Register example:**
```json
POST /auth/register
{
  "username": "john_doe",
  "password": "secret123",
  "role": "teacher",
  "email": "john@example.com",
  "full_name": "John Doe"
}
```

> Note: Only one `admin` account can exist at a time.

---

### Students

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/students` | JWT | List students (paginated, filterable) |
| GET | `/students/<id>` | JWT | Get a student by ID |
| POST | `/students` | admin/teacher | Add a new student |
| PUT | `/students/<id>` | admin/teacher | Update student details |
| DELETE | `/students/<id>` | admin | Delete a student |

**Query params for `GET /students`:** `page`, `limit`, `name`, `course`, `department`

**Add student example:**
```json
POST /students
{
  "name": "Alice Smith",
  "email": "alice@example.com",
  "course": "B.Tech",
  "age": 20,
  "department": "Computer Science",
  "admission_date": "2023-08-01",
  "phone": "9876543210",
  "class_section": "A"
}
```

**Valid departments:**
- Information Technology
- Computer Science
- Mechanical Engineering
- Civil Engineering
- Electrical Engineering

---

### Attendance

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/students/<id>/attendance` | admin/teacher | Mark attendance |
| GET | `/students/<id>/attendance` | JWT | Get student attendance records |
| GET | `/attendance/class-report` | JWT | Attendance report by class/date |
| GET | `/attendance/daily-report` | JWT | Daily attendance summary |
| GET | `/attendance/analytics` | JWT | Overall attendance analytics & alerts |

**Mark attendance example:**
```json
POST /students/1/attendance
{
  "date": "2024-06-01",
  "status": "present",
  "note": "On time"
}
```

**Valid statuses:** `present`, `absent`, `late`, `excused`, `holiday`

---

### Marks

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/students/<id>/marks` | admin/teacher | Add marks for a student |
| GET | `/students/<id>/marks` | JWT | Get marks with stats and subject breakdown |

**Add marks example:**
```json
POST /students/1/marks
{
  "subject": "Data Structures",
  "marks": 85.5,
  "exam_date": "2024-05-20",
  "semester": "Semester 3",
  "assessment_type": "exam",
  "exam_type": "Mid-term",
  "credits": 4,
  "comments": "Good performance"
}
```

**Valid assessment types:** `exam`, `class_test`, `assignment`, `project`, `quiz`, `practical`

### Grading Scale

| Marks | Grade | Grade Points |
|---|---|---|
| 90 – 100 | A+ | 4.0 |
| 80 – 89 | A | 4.0 |
| 70 – 79 | B+ | 3.5 |
| 60 – 69 | B | 3.0 |
| 50 – 59 | C | 2.0 |
| 40 – 49 | D | 1.0 |
| Below 40 | F | 0.0 |

---

### Reports

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/students/<id>/report` | JWT | Summary report (attendance + marks) |
| GET | `/students/<id>/performance` | JWT | Detailed performance with GPA/CGPA |
| GET | `/students/<id>/transcript` | JWT | Full transcript by semester |
| GET | `/students/<id>/ranking` | JWT | Student rank within department |
| GET | `/students/<id>/report-card` | JWT | Downloadable PDF report card |
| GET | `/reports/dashboard` | JWT | System-wide dashboard stats |
| GET | `/exam-types` | JWT | List all distinct exam types |
| GET | `/semesters` | JWT | List all distinct semesters |

---

### Exports

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/export/students` | JWT | Export all students |
| GET | `/export/marks` | JWT | Export all marks |
| GET | `/export/attendance` | JWT | Export all attendance records |

Add `?format=xlsx` to any export endpoint to download as Excel. Defaults to CSV.

```
GET /export/students?format=xlsx
GET /export/marks?format=csv
```

---

## 🗄️ Database Schema

```
users          — system users (admin, teacher, student)
students       — student profiles and personal details
attendance     — daily attendance records per student
marks          — assessment scores, grades, and credits
```

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---|---|
| `CORS error` in browser | Add `Flask-CORS` to `app.py` (see Step 6) |
| `401 Unauthorized` | Log out and log in again — token may have expired |
| `Cannot connect to API` | Make sure `python app.py` is running on port 5000 |
| `MySQL connection error` | Check your `.env` credentials and that MySQL service is running |
| Frontend shows blank page | Open browser console (F12) and check for JS errors |
| `Admin already exists` error | Only one admin account is allowed per database |

---

## 📄 License

This project is open-source. Feel free to use and modify it for educational or personal projects.
