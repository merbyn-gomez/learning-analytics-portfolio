PRAGMA foreign_keys = ON;

CREATE TABLE students (
    student_id INTEGER PRIMARY KEY,
    region TEXT NOT NULL,
    age_group TEXT NOT NULL
);

CREATE TABLE courses (
    course_id INTEGER PRIMARY KEY,
    course_name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    duration_hours INTEGER NOT NULL CHECK (duration_hours > 0)
);

CREATE TABLE enrollments (
    enrollment_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id),
    course_id INTEGER NOT NULL REFERENCES courses(course_id),
    enrolled_on TEXT NOT NULL,
    completed_on TEXT,
    status TEXT NOT NULL CHECK (status IN ('completed','in_progress','withdrawn')),
    UNIQUE(student_id, course_id)
);

CREATE TABLE activities (
    activity_id INTEGER PRIMARY KEY,
    enrollment_id INTEGER NOT NULL REFERENCES enrollments(enrollment_id),
    activity_date TEXT NOT NULL,
    minutes_spent INTEGER NOT NULL CHECK (minutes_spent > 0)
);

CREATE TABLE assessments (
    assessment_id INTEGER PRIMARY KEY,
    enrollment_id INTEGER NOT NULL UNIQUE REFERENCES enrollments(enrollment_id),
    score INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100)
);

CREATE INDEX idx_activities_enrollment_date ON activities(enrollment_id, activity_date);
CREATE INDEX idx_enrollments_course_status ON enrollments(course_id, status);
