// Layer 2 — Financial report data access.
// P-06 (fixes AP-07): the legacy report issued one query per course, then per
// enrollment, then per user and per payment (an N+1+1 explosion). This replaces
// all of it with a single batched LEFT JOIN. Ordering by course id then
// enrollment id preserves the legacy row/student order deterministically.

class ReportModel {
  constructor(db) {
    this.db = db;
  }

  getFinancialRows() {
    return this.db.all(
      `SELECT c.id           AS course_id,
              c.title        AS course_title,
              e.id           AS enrollment_id,
              u.name         AS student_name,
              p.amount       AS payment_amount,
              p.status       AS payment_status
         FROM courses c
         LEFT JOIN enrollments e ON e.course_id = c.id
         LEFT JOIN users u       ON u.id = e.user_id
         LEFT JOIN payments p    ON p.enrollment_id = e.id
        ORDER BY c.id, e.id`,
      []
    );
  }
}

module.exports = ReportModel;
