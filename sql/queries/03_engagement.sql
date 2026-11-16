-- Activity in the inclusive 30-day window ending 2026-10-31.
-- Active enrollment: at least one activity event during the window.
SELECT
  c.course_name,
  COUNT(DISTINCT CASE WHEN a.activity_date BETWEEN '2026-10-02'
      AND '2026-10-31' THEN a.enrollment_id END) AS active_enrollments_30d,
  COALESCE(ROUND(SUM(CASE WHEN a.activity_date BETWEEN '2026-10-02'
      AND '2026-10-31' THEN a.minutes_spent ELSE 0 END) / 60.0, 1), 0)
      AS engagement_hours_30d
FROM courses c
LEFT JOIN enrollments e ON e.course_id = c.course_id
LEFT JOIN activities a ON a.enrollment_id = e.enrollment_id
GROUP BY c.course_id, c.course_name
ORDER BY active_enrollments_30d DESC, c.course_name;
