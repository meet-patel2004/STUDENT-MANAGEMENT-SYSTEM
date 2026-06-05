CREATE DATABASE IF NOT EXISTS SMS;
USE SMS;

CREATE TABLE IF NOT EXISTS users (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(150) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('admin', 'teacher', 'student') NOT NULL DEFAULT 'teacher',
  email VARCHAR(255) UNIQUE NOT NULL,
  full_name VARCHAR(255),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS students (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  course VARCHAR(150) NOT NULL,
  age INT NOT NULL,
  phone VARCHAR(50),
  address VARCHAR(500),
  guardian_name VARCHAR(255),
  guardian_contact VARCHAR(100),
  department ENUM('Information Technology','Computer Science','Mechanical Engineering','Civil Engineering','Electrical Engineering'),
  admission_date DATE NOT NULL,
  class_section VARCHAR(100),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attendance (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    date DATE NOT NULL,
    status ENUM('present','absent','late','excused','holiday') DEFAULT 'present',
    note VARCHAR(1000),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE KEY unique_attendance (student_id, date)
);

CREATE TABLE IF NOT EXISTS marks (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  subject VARCHAR(255) NOT NULL,
  marks DECIMAL(5,2) NOT NULL,
  grade VARCHAR(5) NOT NULL,
  exam_date DATE NOT NULL,
  semester VARCHAR(100),
  assessment_type VARCHAR(100) NOT NULL DEFAULT 'exam',
  exam_type VARCHAR(150),
  credits DECIMAL(5,2) NOT NULL DEFAULT 0.00,
  comments VARCHAR(1000),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS exam_types (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) UNIQUE NOT NULL,
  description VARCHAR(500),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS semesters (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL,
  start_date DATE,
  end_date DATE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
