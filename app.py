import os
import sys
import csv
import math
import MySQLdb.cursors


from functools import wraps
from datetime import datetime, timedelta
from io import BytesIO, StringIO
from flask import Flask, request, jsonify, send_file
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)

sys.modules.setdefault('app', sys.modules[__name__])

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=365)

mysql = MySQL(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

route = app.route
wraps = wraps
jsonify = jsonify
get_jwt_identity = get_jwt_identity
jwt_required = jwt_required

def cur():
    return mysql.connection.cursor(MySQLdb.cursors.DictCursor)

from helper import get_current_user as helper_get_current_user, requires_role as helper_requires_role, grade_for as helper_grade_for, gpa_for as helper_gpa_for
get_current_user = helper_get_current_user
requires_role = helper_requires_role
grade_for = helper_grade_for
gpa_for = helper_gpa_for

PAGE_SIZE = 10
VALID_ROLES = ('admin', 'teacher', 'student')
VALID_ASSESSMENT_TYPES = ('exam', 'class_test', 'assignment', 'project', 'quiz', 'practical')
VALID_ATTENDANCE_STATUSES = ('present', 'absent', 'late', 'excused', 'holiday')
GRADE_POINTS = {
    'A+': 4.0,
    'A': 4.0,
    'B+': 3.5,
    'B': 3.0,
    'C': 2.0,
    'D': 1.0,
    'F': 0.0,
}

import auth
import attendance
import exports
import marks
import reports
import student

def make_csv_response(filename, headers, rows):
    string_buffer = StringIO()
    writer = csv.writer(string_buffer)
    writer.writerow(headers)
    for row in rows:
        writer.writerow([row.get(k, '') for k in headers])
    
    csv_bytes = string_buffer.getvalue().encode('utf-8')
    bytes_buffer = BytesIO(csv_bytes)
    bytes_buffer.seek(0)
    
    return send_file(
        bytes_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename,
    )


def make_excel_response(filename, headers, rows):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(headers)
    for row in rows:
        sheet.append([row.get(k, '') for k in headers])
    buffer = app.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return app.send_file(
        buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename,
    )


def build_export_response(resource, headers, rows, export_format):
    export_format = export_format.lower()
    if export_format == 'xlsx':
        return make_excel_response(f'{resource}.xlsx', headers, rows)
    return make_csv_response(f'{resource}.csv', headers, rows)


def generate_report_card(student, marks, attendance_summary, gpa, cgpa):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(40, height - 40, f"Report Card: {student['name']}")
    pdf.setFont('Helvetica', 10)
    pdf.drawString(40, height - 65, f"Email: {student['email']}    Course: {student['course']}    Department: {student['department']}")
    pdf.drawString(40, height - 80, f"Admission Date: {student['admission_date']}    GPA: {gpa}    CGPA: {cgpa}")

    pdf.drawString(40, height - 105, 'Attendance Summary:')
    line_y = height - 120
    for status, count in attendance_summary.items():
        pdf.drawString(50, line_y, f'{status.capitalize()}: {count}')
        line_y -= 12

    pdf.drawString(40, line_y - 10, 'Marks & Assessments:')
    line_y -= 25

    headers = ['Subject', 'Type', 'Exam Type', 'Marks', 'Grade', 'Semester']
    x_positions = [40, 210, 260, 330, 370, 410]
    col_widths = [200, 45, 65, 35, 35, 160]

    pdf.setFont('Helvetica-Bold', 10)
    for idx, header in enumerate(headers):
        pdf.drawString(x_positions[idx], line_y, header)
    line_y -= 12
    pdf.line(40, line_y, 570, line_y)
    line_y -= 4

    pdf.setFont('Helvetica', 8)
    for record in marks:
        if line_y < 50:
            pdf.showPage()
            pdf.setFont('Helvetica', 8)
            line_y = height - 60
        
        subject = str(record.get('subject', ''))[:35]
        assessment_type = str(record.get('assessment_type', ''))[:10]
        exam_type = str(record.get('exam_type', ''))[:12]
        marks_str = str(record.get('marks', ''))[:8]
        grade = str(record.get('grade', ''))[:5]
        semester = str(record.get('semester', ''))[:15]
        
        pdf.drawString(x_positions[0], line_y, subject)
        pdf.drawString(x_positions[1], line_y, assessment_type)
        pdf.drawString(x_positions[2], line_y, exam_type)
        pdf.drawString(x_positions[3], line_y, marks_str)
        pdf.drawString(x_positions[4], line_y, grade)
        pdf.drawString(x_positions[5], line_y, semester)
        line_y -= 12

    pdf.save()
    buffer.seek(0)
    return buffer


if __name__ == '__main__':
    app.run(debug=True)
