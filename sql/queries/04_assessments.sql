-- Final assessments: scores from completed enrollments only.
-- Pass threshold: 70 out of 100 (illustrative, not institution policy).
SELECT
  c.course_name,
  COUNT(a.assessment_id) AS final_assessments,
  ROUND(AVG(a.score), 1) AS average_score,
  COALESCE(ROUND(100.0 *
    SUM(CASE WHEN a.score >= 70 THEN 1 ELSE 0 END)
    / NULLIF(COUNT(a.assessment_id), 0), 1), 0) AS pass_pct
FROM courses c
LEFT JOIN enrollments e ON e.course_id = c.course_id
  AND e.status = 'completed'
LEFT JOIN assessments a ON a.enrollment_id = e.enrollment_id
GROUP BY c.course_id, c.course_name
ORDER BY pass_pct DESC, c.course_name;
