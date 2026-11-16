-- One row per course. Courses without enrollments are retained.
SELECT
  c.course_name,
  c.category,
  COUNT(e.enrollment_id) AS enrollments,
  SUM(CASE WHEN e.status = 'completed' THEN 1 ELSE 0 END) AS completed,
  COALESCE(ROUND(100.0 *
    SUM(CASE WHEN e.status = 'completed' THEN 1 ELSE 0 END)
    / NULLIF(COUNT(e.enrollment_id), 0), 1), 0) AS completion_pct
FROM courses c
LEFT JOIN enrollments e ON e.course_id = c.course_id
GROUP BY c.course_id, c.course_name, c.category
ORDER BY completion_pct DESC, c.course_name;
