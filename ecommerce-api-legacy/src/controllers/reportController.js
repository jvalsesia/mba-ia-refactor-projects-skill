// Layer 4 — Financial report orchestration (P-04).
// Consumes the single batched query from ReportModel (P-06) and aggregates the
// flat rows into the same per-course shape the legacy endpoint returned:
//   [{ course, revenue, students: [{ student, paid }] }]

class ReportController {
  constructor({ reportModel }) {
    this.reportModel = reportModel;
  }

  async generate() {
    const rows = await this.reportModel.getFinancialRows();

    const byCourse = new Map();
    for (const row of rows) {
      if (!byCourse.has(row.course_id)) {
        byCourse.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
      }
      const entry = byCourse.get(row.course_id);

      // A course with no enrollments yields a single row with a null
      // enrollment_id — keep the course but add no student (legacy behavior).
      if (row.enrollment_id == null) {
        continue;
      }

      if (row.payment_status === 'PAID') {
        entry.revenue += row.payment_amount;
      }
      entry.students.push({
        student: row.student_name || 'Unknown',
        paid: row.payment_amount != null ? row.payment_amount : 0,
      });
    }

    return Array.from(byCourse.values());
  }
}

module.exports = ReportController;
