# 📚 Student Management System

A RESTful API built with **Flask** for managing students, attendance, marks, and academic reports. It supports role-based access control (admin, teacher, student), JWT authentication, and export capabilities.

---

## 🗂️ Project Structure

```
sms/
├── app.py            # App entry point, config, shared utilities
├── auth.py           # Authentication routes (register, login, profile)
├── student.py        # Student CRUD operations
├── attendance.py     # Attendance tracking and analytics
├── marks.py          # Marks/grades management
├── reports.py        # Reports, transcripts, rankings, dashboard
├── exports.py        # CSV/Excel data export
├── helper.py         # Shared utilities (grading, GPA, role guards)
├── sms.sql           # Database schema
└── requirements.txt  # Python dependencies
```

---

## ⚙️ Requirements

- Python 3.8+
- MySQL 5.7+ or MariaDB
- pip packages (see `requirements.txt`):

```
Flask==3.0.3
Flask-MySQLdb==2.0.0
Flask-Bcrypt==1.0.1
Flask-JWT-Extended==4.6.0
openpyxl==3.1.0
reportlab==4.1.0
```

---

## 🚀 Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/student-management-system.git
cd student-management-system
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up the database

```bash
mysql -u root -p < sms.sql
```

### 4. Configure environment variables

Set the following environment variables (or update defaults in `app.py`):

| Variable | Default | Description |
|---|---|---|
| `MYSQL_HOST` | `************` | MySQL host |
| `MYSQL_USER` | `*******` | MySQL username |
| `MYSQL_PASSWORD` | `*******` | MySQL password |
| `MYSQL_DB` | `**********` | Database name |
| `JWT_SECRET_KEY` | `*********` | JWT signing secret |

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
set MYSQL_PASSWORD=your_password
set JWT_SECRET_KEY=your-secret-key
```

> ⚠️ **Important:** Always set a strong `JWT_SECRET_KEY` in production.

### 5. Run the server

```bash
python app.py
```

The API will be available at `http://localhost:5000`.

---

## 🔐 Authentication

All protected routes require a **Bearer JWT token** in the `Authorization` header:

```
Authorization: Bearer <your_token>
```

### Roles

| Role | Permissions |
|---|---|
| `admin` | Full access — manage students, teachers, all data |
| `teacher` | Add/update students, record marks and attendance |
| `student` | Read-only access to own data |

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
exam_types     — lookup table for exam types
semesters      — lookup table for semester names/dates
```

---

## 📄 License

This project is open-source. Feel free to use and modify it for educational or personal projects.
