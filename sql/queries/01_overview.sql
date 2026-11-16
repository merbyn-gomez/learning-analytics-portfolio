-- KPI: completion = completed enrollments / all enrollments (including withdrawn).
SELECT
  COUNT(*) AS total_enrollments,
  COUNT(DISTINCT student_id) AS unique_learners,
  SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_enrollments,
  ROUND(100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0), 1) AS completion_pct
FROM enrollments;
